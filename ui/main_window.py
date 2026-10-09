from PyQt6.QtCore import QEvent, QObject, QTimer, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from config import APP_NAME, WINDOW_HEIGHT, WINDOW_WIDTH
from core.embed_builder import build_embed, is_empty
from core.lolka_client import LolkaWorker
from core.models import DraftState
from core.storage import delete_token, load_draft, load_token, save_draft, save_token
from .create_page import CreatePage
from .settings_page import SettingsPage
from .styles import app_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(760, 600)
        self.setStyleSheet(app_stylesheet())

        self.draft = load_draft()
        self.worker = LolkaWorker()
        self.worker.ready.connect(self._on_ready)
        self.worker.connection_error.connect(self._on_connection_error)
        self.worker.publish_error.connect(self._on_publish_error)
        self.worker.published.connect(self._on_published)

        self.status = QLabel("")
        self.status.setMinimumWidth(250)
        self.status.setStyleSheet("color:#A7A9AE; padding:2px 5px;")

        header = QWidget()
        header.setObjectName("topBar")
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(10, 5, 8, 5)
        self.title = QLabel(APP_NAME)
        self.title.setObjectName("appTitle")
        header_lay.addWidget(self.title)
        header_lay.addStretch(1)
        self.create_nav = QPushButton("Создать")
        self.settings_nav = QPushButton("Настройки")
        self.create_nav.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.settings_nav.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        header_lay.addWidget(self.create_nav)
        header_lay.addWidget(self.settings_nav)

        self.create_page = CreatePage(self.draft)
        self.settings_page = SettingsPage()
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_page)
        self.pages.addWidget(self.settings_page)
        self.create_page.changed.connect(self._schedule_save)
        self.create_page.publish_requested.connect(self._publish)
        self.settings_page.connect_requested.connect(self._connect)
        self.settings_page.delete_requested.connect(self._delete_token)

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(9, 8, 9, 8)
        lay.setSpacing(8)
        lay.addWidget(header)
        lay.addWidget(self.pages, 1)
        lay.addWidget(self.status)
        self.setCentralWidget(central)

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self._save)

        token = load_token()
        if token:
            self.settings_page.set_token(token)
            self.status.setText("Подключение к Lolka...")
            self._pending_token = token
            QTimer.singleShot(250, lambda: self.worker.connect_token(token))
        else:
            self._pending_token = ""
            self.status.setText("Токен бота не подключён")

        self._install_shortcut_filter()

    def _install_shortcut_filter(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            key_event = event
            if isinstance(key_event, QKeyEvent) and key_event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                key = key_event.key()
                text = key_event.text().lower()
                mapping = {
                    Qt.Key.Key_C: "copy", Qt.Key.Key_V: "paste", Qt.Key.Key_X: "cut",
                    Qt.Key.Key_Z: "undo", Qt.Key.Key_Y: "redo", Qt.Key.Key_A: "selectAll",
                }
                if key in mapping or text in {"c", "с", "v", "м", "x", "ч", "z", "я", "y", "н", "a", "ф"}:
                    action = mapping.get(key)
                    if not action:
                        chars = {"c":"copy", "с":"copy", "v":"paste", "м":"paste", "x":"cut", "ч":"cut", "z":"undo", "я":"undo", "y":"redo", "н":"redo", "a":"selectAll", "ф":"selectAll"}
                        action = chars.get(text)
                    if action and hasattr(self, "_focused_text_action"):
                        return self._focused_text_action(action)
        return super().eventFilter(obj, event)

    def _focused_text_action(self, action):
        from PyQt6.QtWidgets import QApplication, QLineEdit, QTextEdit
        widget = QApplication.focusWidget()
        if isinstance(widget, QLineEdit):
            getattr(widget, action)()
            return True
        if isinstance(widget, QTextEdit):
            getattr(widget, action)()
            return True
        return False

    def _schedule_save(self):
        self.save_timer.start(250)

    def _save(self):
        save_draft(self.draft)

    def _connect(self, token: str):
        if not token:
            self.status.setText("Введите токен бота")
            return
        self._pending_token = token
        self.settings_page.set_status(False)
        self.status.setText("Подключение к Lolka...")
        self.worker.connect_token(token)

    def _on_ready(self, guilds):
        if self._pending_token:
            try:
                save_token(self._pending_token)
            except Exception as exc:
                self.status.setText(f"Не удалось сохранить токен: {exc}")
        self.settings_page.set_status(True)
        self.create_page.set_servers(guilds)
        self.status.setText(f"Подключено. Серверов: {len(guilds)}")
        self._schedule_save()

    def _on_connection_error(self, message: str):
        self.settings_page.set_status(False)
        self.status.setText(f"Ошибка подключения: {message}")

    def _delete_token(self):
        delete_token()
        self.settings_page.clear_token()
        self.settings_page.set_status(False)
        self._pending_token = ""
        self.worker.disconnect_client()
        self.status.setText("Токен удалён")

    def _publish(self, guild_id: str, channel_id: str):
        embeds = [build_embed(d) for d in self.create_page.get_publish_data() if not is_empty(d)]
        if not embeds:
            self.status.setText("Нет заполненных Embed для публикации")
            return
        if len(embeds) > 10:
            self.status.setText("Нельзя опубликовать больше 10 Embed")
            return
        self.status.setText("")
        self.worker.publish(guild_id, channel_id, embeds)

    def _on_publish_error(self, message: str):
        self.status.setText(f"Ошибка публикации: {message}")

    def _on_published(self):
        self.status.setText("")

    def closeEvent(self, event):
        self._save()
        self.worker.shutdown()
        event.accept()
