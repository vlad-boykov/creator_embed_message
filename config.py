from pathlib import Path

APP_NAME = "Rustik Fox - Creator Embed Message"
APP_DIR = Path.home() / "AppData" / "Local" / "RustikFoxCreatorEmbedMessage"
APP_DIR.mkdir(parents=True, exist_ok=True)
DRAFT_PATH = APP_DIR / "draft.json"
TOKEN_PATH = APP_DIR / "token.bin"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 800

COLORS = {
    "bg": "#171A20",
    "panel": "#20242C",
    "panel_alt": "#292F39",
    "input": "#1B2028",
    "input_hover": "#222832",
    "border": "#6E7076",
    "border_accent": "#C96C32",
    "accent": "#E47D3A",
    "accent_hover": "#F08B45",
    "text": "#F2F2F2",
    "muted": "#A7A9AE",
    "success": "#69A94A",
    "success_hover": "#79B85A",
    "danger": "#C45A4D",
    "danger_hover": "#D2695A",
    "primary": "#3265B8",
    "primary_hover": "#3D75CF",
    "selection": "#394D68",
    "scrollbar": "#555B66",
    "scrollbar_hover": "#747B87",
}

MAX_EMBEDS = 10
MAX_FIELDS = 25