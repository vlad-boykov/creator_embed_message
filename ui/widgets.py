from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QMouseEvent, QLinearGradient, QCursor
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QSlider, QVBoxLayout, QWidget, QColorDialog, QTextEdit
)
from config import COLORS


class SearchDialog(QDialog):
    selected = pyqtSignal(object)

    def __init__(self, title: str, items: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(440, 520)
        self.items = items
        self.filtered = items[:]
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск...")
        self.list = QListWidget()
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.reject)
        self.search.textChanged.connect(self._filter)
        self.list.itemDoubleClicked.connect(self._choose)
        self.list.itemClicked.connect(self._choose)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(self.search)
        lay.addWidget(self.list, 1)
        lay.addWidget(self.close_button)
        self._populate()

    def _filter(self, text: str):
        q = text.casefold().strip()
        self.filtered = [i for i in self.items if q in i["name"].casefold()]
        self._populate()

    def _populate(self):
        self.list.clear()
        for item in self.filtered:
            row = QListWidgetItem(item["name"])
            row.setData(Qt.ItemDataRole.UserRole, item)
            self.list.addItem(row)
        if self.list.count():
            self.list.setCurrentRow(0)

    def _choose(self, item: QListWidgetItem):
        self.selected.emit(item.data(Qt.ItemDataRole.UserRole))
        self.accept()


class SearchSelector(QPushButton):
    changed = pyqtSignal(object)

    def __init__(self, placeholder: str, parent=None):
        super().__init__(f"▼ {placeholder}", parent)
        self.placeholder = placeholder
        self.value = None
        self.items: list[dict] = []
        self.clicked.connect(self.open_dialog)
        self.setMinimumHeight(30)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())

    def set_items(self, items: list[dict]):
        self.items = items

    def set_value(self, item: dict | None):
        self.value = item
        if item:
            self.setText(f"▼ {item['name']}")
        else:
            self.setText(f"▼ {self.placeholder}")
        self.changed.emit(item)

    def open_dialog(self):
        dialog = SearchDialog(self.placeholder, self.items, self.window())
        dialog.selected.connect(self.set_value)
        dialog.exec()


class IconButton(QPushButton):
    """Small icon-only button matching the editor chrome without font glyph artifacts."""
    def __init__(self, icon: str, tooltip: str = "", parent=None):
        super().__init__(parent)
        self.icon = icon
        self.setToolTip(tooltip)
        self.setFixedSize(30, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(
            f"QPushButton {{ background:{COLORS['panel']}; border:1px solid {COLORS['border']}; "
            "border-radius:4px; padding:0; }} "
            f"QPushButton:hover {{ background:{COLORS['input_hover']}; border-color:{COLORS['border_accent']}; }} "
            f"QPushButton:pressed {{ background:{COLORS['panel_alt']}; }}"
        )

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor(COLORS['text']), 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin)
        p.setPen(pen)
        r = self.rect()
        cx, cy = r.center().x(), r.center().y()
        if self.icon == "up":
            p.drawLine(cx - 6, cy + 3, cx, cy - 3)
            p.drawLine(cx, cy - 3, cx + 6, cy + 3)
        elif self.icon == "down":
            p.drawLine(cx - 6, cy - 3, cx, cy + 3)
            p.drawLine(cx, cy + 3, cx + 6, cy - 3)
        elif self.icon == "close":
            p.drawLine(cx - 6, cy - 6, cx + 6, cy + 6)
            p.drawLine(cx + 6, cy - 6, cx - 6, cy + 6)


class CollapsibleSection(QFrame):
    toggled = pyqtSignal(bool)

    def __init__(self, title: str, content: QWidget, expanded=True, parent=None):
        super().__init__(parent)
        self.setObjectName("collapsible")
        self.content = content
        self.expanded = expanded
        self.button = QPushButton()
        self.button.setText(f"▾{title}" if expanded else f"▸{title}")
        self.button.setStyleSheet(
            f"QPushButton {{ background: {COLORS['panel']}; border: 1px solid {COLORS['border']}; "
            "padding: 2px 7px; text-align: left; font-weight: 600; border-radius: 4px; }}"
        )
        self.button.clicked.connect(self.toggle)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)
        outer.addWidget(self.button, 0, Qt.AlignmentFlag.AlignLeft)
        outer.addWidget(content)
        self._apply()

    def toggle(self):
        self.expanded = not self.expanded
        self._apply()
        self.toggled.emit(self.expanded)

    def _apply(self):
        self.content.setVisible(self.expanded)
        title = self.button.text()[1:]
        self.button.setText(("▾" if self.expanded else "▸") + title)


class ResizeHandle(QWidget):
    """Интерактивная полоса внизу текстового поля для изменения его высоты мышкой."""
    def __init__(self, target_widget: QWidget, parent=None):
        super().__init__(parent)
        self.target = target_widget
        self.setFixedHeight(8)
        self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self._drag_start_y = 0
        self._start_height = 0
        self._is_dragging = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()
        p.setPen(QPen(QColor(COLORS['scrollbar']), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(cx - 16, cy, cx + 16, cy)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_y = event.globalPosition().y()
            self._start_height = self.target.height()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            delta = event.globalPosition().y() - self._drag_start_y
            new_height = max(60, int(self._start_height + delta))
            self.target.setFixedHeight(new_height)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False


class MarkdownTextEdit(QWidget):
    textChanged = pyqtSignal()

    def __init__(self, min_height=110, parent=None):
        super().__init__(parent)
        
        self.editor = QTextEdit()
        self.editor.setFixedHeight(min_height)
        self.editor.textChanged.connect(self.textChanged.emit)

        bar = QHBoxLayout()
        bar.setContentsMargins(0, 0, 0, 4)
        bar.setSpacing(4)
        
        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['panel']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['input_hover']};
                border-color: {COLORS['border_accent']};
                color: {COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['panel_alt']};
            }}
        """

        for label, fn, tip in [
            ("B", lambda: self.wrap("**", "**"), "Жирный"),
            ("I", lambda: self.wrap("*", "*"), "Курсив"),
            ("U", lambda: self.wrap("__", "__"), "Подчёркивание"),
            ("S", lambda: self.wrap("~~", "~~"), "Зачёркивание"),
            ("```", lambda: self.wrap("```\n", "\n```"), "Блок Markdown-кода"),
        ]:
            b = QPushButton(label)
            b.setToolTip(tip)
            b.setFixedHeight(26)
            b.setMinimumWidth(28 if label != "```" else 38)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(btn_style)
            b.clicked.connect(fn)
            bar.addWidget(b)
            
        bar.addStretch(1)

        self.handle = ResizeHandle(self.editor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.addLayout(bar)
        lay.addWidget(self.editor)
        lay.addWidget(self.handle)

    def wrap(self, left: str, right: str):
        cursor = self.editor.textCursor()
        selected = cursor.selectedText()
        if selected:
            cursor.insertText(left + selected + right)
        else:
            cursor.insertText(left + right)
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, len(right))
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def setPlainText(self, text: str):
        self.editor.setPlainText(text)

    def toPlainText(self) -> str:
        return self.editor.toPlainText()


class ColorPicker(QDialog):
    colorChanged = pyqtSignal(str)

    def __init__(self, initial="#E47D3A", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор цвета")
        self.setFixedSize(360, 365)
        self._color = QColor(initial)
        self._hue = 20
        self._sat = 0.72
        self._val = 0.89
        self._sync_hsv()
        self.area = SVArea(self)
        self.area.changed.connect(self._from_sv)
        self.hue = QSlider(Qt.Orientation.Horizontal)
        self.hue.setRange(0, 359)
        self.hue.setValue(self._hue)
        self.hue.valueChanged.connect(self._from_hue)
        self.hex_edit = QLineEdit(self._color.name().upper())
        self.hex_edit.textChanged.connect(self._from_hex)
        self.swatch = QFrame()
        self.swatch.setFixedWidth(45)
        self.ok = QPushButton("Готово")
        self.cancel = QPushButton("Отмена")
        self.ok.clicked.connect(self._accept)
        self.cancel.clicked.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.addWidget(self.area)
        lay.addWidget(QLabel("Оттенок"))
        lay.addWidget(self.hue)
        row = QHBoxLayout()
        row.addWidget(QLabel("HEX"))
        row.addWidget(self.hex_edit, 1)
        row.addWidget(self.swatch)
        lay.addLayout(row)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.cancel)
        buttons.addWidget(self.ok)
        lay.addLayout(buttons)
        self._update_view()

    def _sync_hsv(self):
        h, s, v, _ = self._color.getHsvF()
        if h >= 0:
            self._hue = int(h * 359)
            self._sat = s
            self._val = v

    def _from_sv(self, s, v):
        self._sat, self._val = s, v
        self._set_color(QColor.fromHsvF(self._hue / 359.0, s, v))

    def _from_hue(self, h):
        self._hue = h
        self._set_color(QColor.fromHsvF(h / 359.0, self._sat, self._val))

    def _from_hex(self, value):
        color = QColor(value.strip())
        if color.isValid() and len(value.strip()) in (4, 7):
            self._color = color
            self._sync_hsv()
            self.area.set_values(self._sat, self._val)
            self.hue.blockSignals(True)
            self.hue.setValue(self._hue)
            self.hue.blockSignals(False)
            self._update_view()

    def _set_color(self, color):
        self._color = color
        self.hex_edit.blockSignals(True)
        self.hex_edit.setText(color.name().upper())
        self.hex_edit.blockSignals(False)
        self._update_view()

    def _update_view(self):
        self.area.set_hue(self._hue)
        self.swatch.setStyleSheet(f"background:{self._color.name()}; border:1px solid {COLORS['border']};")

    def _accept(self):
        self.colorChanged.emit(self._color.name().upper())
        self.accept()


class SVArea(QWidget):
    changed = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.hue = 20
        self.sat = 0.72
        self.val = 0.89

    def set_hue(self, hue):
        self.hue = hue
        self.update()

    def set_values(self, sat, val):
        self.sat, self.val = sat, val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        rect = self.rect()
        base = QColor.fromHsv(self.hue, 255, 255)
        p.fillRect(rect, base)

        grad1 = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.topRight()))
        grad1.setColorAt(0, QColor(255, 255, 255))
        grad1.setColorAt(1, QColor(255, 255, 255, 0))
        p.fillRect(rect, grad1)

        grad2 = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        grad2.setColorAt(0, QColor(0, 0, 0, 0))
        grad2.setColorAt(1, QColor(0, 0, 0))
        p.fillRect(rect, grad2)

        x = int(self.sat * max(1, rect.width() - 1))
        y = int((1 - self.val) * max(1, rect.height() - 1))
        p.setPen(QPen(Qt.GlobalColor.white, 2))
        p.drawEllipse(QPoint(x, y), 6, 6)

    def mousePressEvent(self, event: QMouseEvent):
        self._pick(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._pick(event.position().x(), event.position().y())

    def _pick(self, x, y):
        self.sat = max(0.0, min(1.0, x / max(1, self.width() - 1)))
        self.val = max(0.0, min(1.0, 1.0 - y / max(1, self.height() - 1)))
        self.update()
        self.changed.emit(self.sat, self.val)