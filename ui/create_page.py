from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
)
from config import COLORS, MAX_EMBEDS, MAX_FIELDS
from core.models import DraftState, EmbedData, FieldData
from .widgets import CollapsibleSection, ColorPicker, IconButton, MarkdownTextEdit, SearchSelector


class FieldEditor(QFrame):
    changed = pyqtSignal()
    deleted = pyqtSignal(object)

    def __init__(self, data: FieldData, number: int, parent=None):
        super().__init__(parent)
        self.data = data
        self.number = number
        
        self.setObjectName("fieldCard")
        self.setStyleSheet(
            f"QFrame#fieldCard {{ background:{COLORS['input']}; border:1px solid {COLORS['border']}; border-radius:2px; }}"
        )

        self.header = QPushButton()
        self.header.setStyleSheet(
            f"QPushButton {{ background:transparent; border:none; font-size:14px; font-weight:700; text-align:left; padding:5px; }}"
        )
        self.header.clicked.connect(self.toggle)

        self.delete = QPushButton("Удалить")
        self.delete.setObjectName("danger")
        self.delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete.setStyleSheet(f"""
            QPushButton#danger {{
                background: {COLORS['danger']};
                border: 1px solid #D47B70;
                border-radius: 3px;
                padding: 3px 12px;
                font-weight: 600;
                font-size: 12px;
                min-height: 22px;
            }}
            QPushButton#danger:hover {{
                background: {COLORS['danger_hover']};
            }}
        """)
        self.delete.clicked.connect(lambda: self.deleted.emit(self))

        top = QHBoxLayout()
        top.setContentsMargins(8, 6, 8, 4)
        top.addWidget(self.header, 1)
        top.addWidget(self.delete)

        self.lbl_name = QLabel("Название")
        self.lbl_name.setStyleSheet("border: none; background: transparent;")

        self.name = QLineEdit(data.name)
        self.name.setPlaceholderText("Название")

        self.lbl_text = QLabel("Текст")
        self.lbl_text.setStyleSheet("border: none; background: transparent;")

        self.value = MarkdownTextEdit(95)
        self.value.setPlainText(data.value)

        self.inline = QCheckBox("Inline")
        self.inline.setChecked(data.inline)

        self.name.textChanged.connect(self._changed)
        self.value.textChanged.connect(self._changed)
        self.inline.stateChanged.connect(self._changed)

        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setContentsMargins(12, 8, 12, 12)
        lay.setSpacing(7)

        lay.addWidget(self.lbl_name)
        lay.addWidget(self.name)
        lay.addWidget(self.lbl_text)
        lay.addWidget(self.value)
        lay.addWidget(self.inline, 0, Qt.AlignmentFlag.AlignLeft)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addLayout(top)
        outer.addWidget(body)

        self.body = body
        self._apply()

    def _changed(self):
        self.data.name = self.name.text()
        self.data.value = self.value.toPlainText()
        self.data.inline = self.inline.isChecked()
        self.changed.emit()

    def toggle(self):
        self.data.collapsed = not self.data.collapsed
        self._apply()
        self.changed.emit()

    def _apply(self):
        self.body.setVisible(not self.data.collapsed)
        self.header.setText(("▸" if self.data.collapsed else "▾") + f"Поле #{self.number}")


class EmbedEditor(QFrame):
    changed = pyqtSignal()
    deleted = pyqtSignal(object)

    def __init__(self, data: EmbedData, number: int, parent=None):
        super().__init__(parent)
        self.data = data
        self.number = number
        self.fields: list[FieldEditor] = []
        self.setStyleSheet(
            f"QFrame#embedCard {{ background:{COLORS['panel_alt']}; border:1px solid {COLORS['border_accent']}; border-radius:2px; }}"
        )
        self.setObjectName("embedCard")

        self.header = QFrame()
        header_lay = QHBoxLayout(self.header)
        header_lay.setContentsMargins(6, 6, 6, 2)

        self.title = QPushButton(f"Embed #{number}")
        self.title.setStyleSheet(
            f"QPushButton {{ background:{COLORS['panel']}; border:1px solid {COLORS['border']}; border-radius:2px; font-size:15px; font-weight:700; text-align:left; padding:3px 6px; }}"
        )
        self.title.clicked.connect(self.toggle)
        header_lay.addWidget(self.title, 1)

        self.collapse = IconButton("down" if data.collapsed else "up", "Свернуть/развернуть")
        self.collapse.clicked.connect(self.toggle)
        self.remove = IconButton("close", "Удалить Embed")
        self.remove.clicked.connect(lambda: self.deleted.emit(self))

        header_lay.addWidget(self.collapse)
        header_lay.addWidget(self.remove)

        self.content = QWidget()
        content_lay = QVBoxLayout(self.content)
        content_lay.setContentsMargins(30, 8, 10, 10)
        content_lay.setSpacing(9)

        content_lay.addWidget(self._make_author())
        content_lay.addWidget(self._make_main())
        content_lay.addWidget(self._make_images())
        content_lay.addWidget(self._make_footer())
        content_lay.addWidget(self._make_fields())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self.header)
        outer.addWidget(self.content)
        self._apply_collapsed()

    def _make_labeled_edit(self, label: str, value: str, placeholder=""):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lay.addWidget(QLabel(label))
        edit = QLineEdit(value)
        if placeholder:
            edit.setPlaceholderText(placeholder)
        edit.textChanged.connect(self.changed.emit)
        lay.addWidget(edit)
        return box, edit

    def _make_author(self):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        for label, attr in [("Имя", "author_name"), ("URL", "author_url"), ("Иконка URL", "author_icon_url")]:
            w, edit = self._make_labeled_edit(label, getattr(self.data, attr))
            setattr(self, attr + "_edit", edit)
            edit.textChanged.connect(lambda text, a=attr: self._set_attr(a, text))
            lay.addWidget(w)
        return CollapsibleSection("Автор", box, True)

    def _make_main(self):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        w, self.title_edit = self._make_labeled_edit("Заголовок", self.data.title)
        self.title_edit.textChanged.connect(lambda t: self._set_attr("title", t))
        lay.addWidget(w)

        lay.addWidget(QLabel("Описание"))
        self.description = MarkdownTextEdit(150)
        self.description.setPlainText(self.data.description)
        self.description.textChanged.connect(lambda: self._set_attr("description", self.description.toPlainText()))
        lay.addWidget(self.description)

        w, self.url_edit = self._make_labeled_edit("URL", self.data.url)
        self.url_edit.textChanged.connect(lambda t: self._set_attr("url", t))
        lay.addWidget(w)

        color_row = QHBoxLayout()
        color_row.addWidget(QLabel("Цвет"))
        color_row.addStretch(1)
        self.color_hex = QLineEdit(self.data.color)
        self.color_hex.setFixedWidth(90)
        self.color_hex.textChanged.connect(self._color_text_changed)
        self.color_button = QPushButton()
        self.color_button.setFixedSize(28, 28)
        self.color_button.clicked.connect(self.pick_color)
        color_row.addWidget(self.color_hex)
        color_row.addWidget(self.color_button)
        lay.addLayout(color_row)
        self._update_color_button()
        return CollapsibleSection("Основное", box, True)

    def _make_images(self):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        for label, attr in [("Image URL", "image_url"), ("Thumbnail URL", "thumbnail_url")]:
            w, edit = self._make_labeled_edit(label, getattr(self.data, attr))
            edit.textChanged.connect(lambda text, a=attr: self._set_attr(a, text))
            lay.addWidget(w)
        return CollapsibleSection("Изображения", box, True)

    def _make_footer(self):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        w, self.footer_text = self._make_labeled_edit("Нижний колонтитул", self.data.footer_text)
        self.footer_text.textChanged.connect(lambda t: self._set_attr("footer_text", t))
        lay.addWidget(w)

        w, self.footer_icon = self._make_labeled_edit("URL-адрес значка в нижнем колонтитуле", self.data.footer_icon_url)
        self.footer_icon.textChanged.connect(lambda t: self._set_attr("footer_icon_url", t))
        lay.addWidget(w)

        self.timestamp = QCheckBox("Отметка времени")
        self.timestamp.setChecked(self.data.timestamp_enabled)
        self.timestamp.stateChanged.connect(lambda _: self._set_attr("timestamp_enabled", self.timestamp.isChecked()))
        lay.addWidget(self.timestamp, 0, Qt.AlignmentFlag.AlignLeft)
        return CollapsibleSection("Нижний колонтитул", box, True)

    def _make_fields(self):
        outer = QWidget()
        lay = QVBoxLayout(outer)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.fields_layout = QVBoxLayout()
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(6)
        lay.addLayout(self.fields_layout)

        buttons = QHBoxLayout()
        self.add_field = QPushButton("Создать поле")
        self.add_field.setObjectName("success")
        self.add_field.clicked.connect(self.add_field_clicked)
        self.clear_fields = QPushButton("Очистить")
        self.clear_fields.setObjectName("danger")
        self.clear_fields.clicked.connect(self.clear_fields_clicked)

        buttons.addWidget(self.add_field)
        buttons.addWidget(self.clear_fields)
        buttons.addStretch(1)
        lay.addLayout(buttons)

        self._rebuild_fields()
        return CollapsibleSection("Поля", outer, True)

    def _rebuild_fields(self):
        while self.fields_layout.count():
            item = self.fields_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.fields.clear()
        for i, data in enumerate(self.data.fields, 1):
            field = FieldEditor(data, i)
            field.changed.connect(self.changed.emit)
            field.deleted.connect(self.remove_field)
            self.fields_layout.addWidget(field)
            self.fields.append(field)
        self.add_field.setEnabled(len(self.data.fields) < MAX_FIELDS)
        self.changed.emit()

    def add_field_clicked(self):
        if len(self.data.fields) >= MAX_FIELDS:
            return
        self.data.fields.append(FieldData())
        self._rebuild_fields()

    def clear_fields_clicked(self):
        self.data.fields.clear()
        self._rebuild_fields()

    def remove_field(self, field):
        try:
            self.data.fields.remove(field.data)
        except ValueError:
            return
        self._rebuild_fields()

    def _set_attr(self, attr, value):
        setattr(self.data, attr, value)
        self.changed.emit()

    def _color_text_changed(self, value):
        if len(value) == 7 and value.startswith("#"):
            from PyQt6.QtGui import QColor
            if QColor(value).isValid():
                self.data.color = value.upper()
                self._update_color_button()
                self.changed.emit()

    def _update_color_button(self):
        self.color_button.setStyleSheet(
            f"QPushButton {{ background:{self.data.color}; border:1px solid {COLORS['border']}; border-radius:2px; }}"
        )

    def pick_color(self):
        picker = ColorPicker(self.data.color, self)
        picker.colorChanged.connect(self._set_color)
        picker.exec()

    def _set_color(self, color):
        self.data.color = color
        self.color_hex.blockSignals(True)
        self.color_hex.setText(color)
        self.color_hex.blockSignals(False)
        self._update_color_button()
        self.changed.emit()

    def toggle(self):
        self.data.collapsed = not self.data.collapsed
        self._apply_collapsed()
        self.changed.emit()

    def _apply_collapsed(self):
        self.content.setVisible(not self.data.collapsed)
        self.collapse.icon = "down" if self.data.collapsed else "up"
        self.collapse.update()


class CreatePage(QWidget):
    changed = pyqtSignal()
    server_changed = pyqtSignal(object)
    channel_changed = pyqtSignal(object)
    publish_requested = pyqtSignal(str, str)

    def __init__(self, draft: DraftState, parent=None):
        super().__init__(parent)
        self.draft = draft
        self.embed_widgets: list[EmbedEditor] = []

        self.server_selector = SearchSelector("Выбрать сервер")
        self.channel_selector = SearchSelector("Выбрать канал")
        self.server_selector.changed.connect(self._server_selected)
        self.channel_selector.changed.connect(self._channel_selected)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 8)
        top.setSpacing(10)
        top.addWidget(self.server_selector, 1)
        top.addWidget(self.channel_selector, 1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.embed_layout = QVBoxLayout(self.scroll_content)
        self.embed_layout.setContentsMargins(0, 0, 4, 8)
        self.embed_layout.setSpacing(8)
        self.embed_layout.addStretch(1)
        self.scroll.setWidget(self.scroll_content)

        self.create_embed = QPushButton("Создать Embed")
        self.create_embed.setObjectName("primary")
        self.create_embed.clicked.connect(self.add_embed)

        self.delete_embeds = QPushButton("Удалить Embeds")
        self.delete_embeds.setObjectName("danger")
        self.delete_embeds.clicked.connect(self.delete_all_embeds)

        self.publish = QPushButton("Опубликовать")
        self.publish.setObjectName("publish")
        self.publish.clicked.connect(self._publish)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 8, 0, 0)
        bottom.addWidget(self.create_embed)
        bottom.addWidget(self.delete_embeds)
        bottom.addStretch(1)
        bottom.addWidget(self.publish)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(top)
        lay.addWidget(self.scroll, 1)
        lay.addLayout(bottom)

        self._rebuild_embeds()
        self._restore_selectors()

    def _restore_selectors(self):
        if self.draft.selected_guild_name:
            self.server_selector.setText(f"▼ {self.draft.selected_guild_name}")
        if self.draft.selected_channel_name:
            self.channel_selector.setText(f"▼ {self.draft.selected_channel_name}")

    def set_servers(self, servers: list[dict]):
        self.server_selector.set_items(servers)
        wanted = self.draft.selected_guild_id
        item = next((s for s in servers if s["id"] == wanted), None)
        if item:
            self.server_selector.set_value(item)
        else:
            self.channel_selector.set_items([])
            self.channel_selector.set_value(None)

    def _server_selected(self, item):
        if not item:
            self.draft.selected_guild_id = ""
            self.draft.selected_guild_name = ""
            self.channel_selector.set_items([])
            self.channel_selector.set_value(None)
        else:
            self.draft.selected_guild_id = item["id"]
            self.draft.selected_guild_name = item["name"]
            self.channel_selector.set_items(item.get("channels", []))
            wanted = self.draft.selected_channel_id
            channel = next((c for c in item.get("channels", []) if c["id"] == wanted), None)
            self.channel_selector.set_value(channel)
        self.changed.emit()
        self.server_changed.emit(item)

    def _channel_selected(self, item):
        self.draft.selected_channel_id = item["id"] if item else ""
        self.draft.selected_channel_name = item["name"] if item else ""
        self.changed.emit()
        self.channel_changed.emit(item)

    def _rebuild_embeds(self):
        while self.embed_layout.count() > 1:
            item = self.embed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.embed_widgets.clear()
        for i, data in enumerate(self.draft.embeds, 1):
            widget = EmbedEditor(data, i)
            widget.changed.connect(self.changed.emit)
            widget.deleted.connect(self.remove_embed)
            self.embed_layout.insertWidget(self.embed_layout.count() - 1, widget)
            self.embed_widgets.append(widget)
        self.create_embed.setEnabled(len(self.draft.embeds) < MAX_EMBEDS)
        self.changed.emit()

    def add_embed(self):
        if len(self.draft.embeds) >= MAX_EMBEDS:
            return
        self.draft.embeds.append(EmbedData())
        self._rebuild_embeds()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def remove_embed(self, widget):
        try:
            self.draft.embeds.remove(widget.data)
        except ValueError:
            return
        self._rebuild_embeds()

    def delete_all_embeds(self):
        self.draft.embeds.clear()
        self._rebuild_embeds()

    def _publish(self):
        if not self.draft.selected_guild_id or not self.draft.selected_channel_id:
            self.changed.emit()
            return
        self.publish_requested.emit(self.draft.selected_guild_id, self.draft.selected_channel_id)

    def get_publish_data(self):
        return self.draft.embeds
