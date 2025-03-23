import os

# Application info
APP_NAME = "Tools Get"
APP_ID = "org.pardus.toolsget"
APP_VERSION = "1.0.0"
APP_ICON = "toolsget1.png"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, "icons")
CSS_DIR = os.path.join(BASE_DIR, "css")

# Theme colors
THEME = {
    "light": {
        "primary": "#3498db",
        "secondary": "#2ecc71",
        "bg": "#ffffff",
        "fg": "#333333",
        "accent": "#e74c3c",
        "warning": "#f39c12",
        "terminal_bg": "#282c34",
        "terminal_fg": "#abb2bf"
    },
    "dark": {
        "primary": "#2980b9",
        "secondary": "#27ae60",
        "bg": "#2c3e50",
        "fg": "#ecf0f1",
        "accent": "#c0392b",
        "warning": "#d35400",
        "terminal_bg": "#1e1e1e",
        "terminal_fg": "#d4d4d4"
    }
}

# Icons
ICONS = {
    "app_logo": APP_ICON,
    "default_tool": "tool-default.png",
    "category_icons": {
        "development": "category/dev.png",
        "network": "category/net.png",
        "system": "category/sys.png",
        "security": "category/sec.png",
        "multimedia": "category/media.png",
        "office": "category/office.png",
        "internet": "category/web.png",
        "accessories": "category/tools.png"
    }
}

# CSS dosyasını yükle
with open(os.path.join(CSS_DIR, 'style.css'), 'r') as f:
    STYLE = f.read()
