from config import COLORS

def app_stylesheet() -> str:
    c = COLORS
    return f"""
* {{
    font-family: Segoe UI, Arial, sans-serif;
    color: {c['text']};
    font-size: 13px;
}}

QMainWindow, QWidget {{
    background: {c['bg']};
}}

/* Сбрасываем контуры и рамки у всех QLabel и их возможных контейнеров */
QLabel {{
    border: none !important;
    background: transparent !important;
    outline: none !important;
}}

QLabel#settingsLabel, QLabel#settingsHint, QLabel#settingsLink {{
    border: none !important;
    background: transparent !important;
}}

QLabel#settingsHint a, QLabel#settingsLink a {{
    color: #6EA6FF;
    text-decoration: underline;
}}

QFrame#settingsCard {{
    background: {c['input']};
    border: 1px solid {c['border']};
    border-radius: 2px;
}}

QFrame#topBar {{
    background: {c['bg']};
    border: 1px solid {c['border_accent']};
    border-radius: 2px;
}}

QLabel#appTitle {{
    color: {c['accent']};
    font-size: 17px;
    font-weight: 700;
}}

/* Кнопки */
QPushButton {{
    outline: none;
    background: {c['panel']};
    border: 1px solid {c['border_accent']};
    border-radius: 2px;
    padding: 5px 10px;
    min-height: 25px;
}}

QPushButton:hover {{
    background: {c['input_hover']};
}}

QPushButton:pressed {{
    background: {c['panel_alt']};
}}

QPushButton#primary {{
    background: {c['primary']};
    border-color: #4E78BA;
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background: {c['primary_hover']};
}}

QPushButton#success {{
    background: {c['success']};
    border-color: #87B76D;
    font-weight: 600;
}}

QPushButton#success:hover {{
    background: {c['success_hover']};
}}

QPushButton#danger {{
    background: {c['danger']};
    border-color: #D47B70;
    font-weight: 600;
}}

QPushButton#danger:hover {{
    background: {c['danger_hover']};
}}

QPushButton#publish {{
    background: {c['accent']};
    border-color: #F09B61;
    font-weight: 700;
}}

QPushButton#publish:hover {{
    background: {c['accent_hover']};
}}

QPushButton#navActive {{
    background: {c['panel_alt']};
}}

/* Поля ввода: границы должны быть только у самих полей QLineEdit/QTextEdit */
QLineEdit, QTextEdit {{
    background: {c['input']};
    border: 1px solid {c['border']};
    border-radius: 2px;
    selection-background-color: {c['selection']};
    padding: 5px 7px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {c['border_accent']};
}}

QLineEdit[readOnly="true"] {{
    color: {c['muted']};
}}

/* Скроллбары */
QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 12px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {c['scrollbar']};
    min-height: 42px;
    border-radius: 6px;
    margin: 1px;
}}

QScrollBar::handle:vertical:hover {{
    background: {c['scrollbar_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    height: 0px;
}}

/* Списки */
QListWidget {{
    background: {c['input']};
    border: 1px solid {c['border']};
    outline: none;
}}

QListWidget::item {{
    padding: 8px;
    border-radius: 2px;
}}

QListWidget::item:hover {{
    background: {c['input_hover']};
}}

QListWidget::item:selected {{
    background: {c['selection']};
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
}}

QToolTip {{
    background: {c['panel']};
    border: 1px solid {c['border']};
    padding: 4px;
}}

QDialog {{
    background: {c['panel']};
    border: 1px solid {c['border_accent']};
}}
"""