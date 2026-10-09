import base64
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from config import COLORS

_S_URL = base64.b64decode(b"aHR0cHM6Ly9sb2xrYS5nZy9nYzdhUER6eg==").decode("utf-8")
_D_URL = base64.b64decode(b"aHR0cHM6Ly9sb2xrYS5hcHAvZGV2ZWxvcGVycy9wb3J0YWw=").decode("utf-8")


class SettingsPage(QWidget):
    connect_requested = pyqtSignal(str)
    delete_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.token = QLineEdit()
        self.token.setEchoMode(QLineEdit.EchoMode.Password)
        self.token.setPlaceholderText("Вставьте токен бота")
        self.connect = QPushButton("Подключить")
        self.connect.setObjectName("success")
        self.delete = QPushButton("Удалить")
        self.delete.setObjectName("danger")
        self.connect.clicked.connect(lambda: self.connect_requested.emit(self.token.text().strip()))
        self.delete.clicked.connect(self.delete_requested.emit)

        token_card = self._card()
        token_lay = QVBoxLayout(token_card)
        token_lay.setContentsMargins(12, 12, 12, 12)
        token_lay.setSpacing(7)

        token_label = QLabel("Токен бота")
        token_label.setObjectName("settingsLabel")
        token_lay.addWidget(token_label)
        token_lay.addWidget(self.token)

        helper = QLabel()
        helper.setObjectName("settingsHint")
        helper.setWordWrap(True)
        helper.setText(
            f'Создайте бота на <a href="{_D_URL}">портале разработчиков</a>, '
            'скопируйте его токен и вставьте в это поле.'
        )
        helper.setOpenExternalLinks(True)
        token_lay.addWidget(helper)

        row = QHBoxLayout()
        row.setSpacing(7)
        row.addWidget(self.connect)
        row.addWidget(self.delete)
        row.addStretch(1)
        token_lay.addLayout(row)

        support_card = self._card()
        support_lay = QVBoxLayout(support_card)
        support_lay.setContentsMargins(12, 12, 12, 12)
        support_lay.setSpacing(7)

        support_label = QLabel("Сервер поддержки")
        support_label.setObjectName("settingsLabel")
        support_lay.addWidget(support_label)

        link = QLabel(f'<a href="{_S_URL}">{_S_URL}</a>')
        link.setObjectName("settingsLink")
        link.setOpenExternalLinks(True)
        support_lay.addWidget(link)

        text = QLabel(
            "\n"
            "Наш лис помогает упаковывать скучные тексты в сочные, функциональные Embed-карточки прямо через твоего бота.\n" 
            "Если у вас возникли трудности с настройкой, вы хотите предложить новую функцию или просто ищете вдохновение.\n"
            "Наш официальный сервер поддержки всегда открыт для вас."
        )
        text.setObjectName("settingsHint")
        text.setWordWrap(True)
        support_lay.addWidget(text)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 0, 8, 8)
        lay.setSpacing(10)
        lay.addWidget(token_card)
        lay.addWidget(support_card)
        lay.addStretch(1)

    def _card(self):
        card = QFrame()
        card.setObjectName("settingsCard")
        return card

    def set_token(self, token: str):
        self.token.setText(token)

    def clear_token(self):
        self.token.clear()

    def set_status(self, connected: bool):
        self.connect.setText("Подключено" if connected else "Подключить")
        self.connect.setEnabled(not connected)