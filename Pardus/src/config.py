import os
import logging

# Application info
APP_NAME = "Tools Get"
APP_ID = "org.pardus.toolsget"
APP_VERSION = "1.0.0"
APP_ICON = "toolsget1.png"
APP_AUTHOR = "Eyyüp Efe Adıgüzel"
APP_EMAIL = "eyupadiguzel20@gmail.com"
APP_WEBSITE = "https://github.com/e-Ey-cyber/Terminal-Tools-Grafik-Aray-z-"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, "icons")
CSS_DIR = os.path.join(BASE_DIR, "css")
CONFIG_DIR = "/etc/pardus/toolsget"
SHARE_DIR = "/usr/share/pardus/toolsget"
ICONS_DIR = "/usr/share/icons/hicolor"
CACHE_DIR = "~/.cache/toolsget"
LOG_DIR = "~/.local/share/toolsget"

# Logging configuration
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.expanduser('~/.local/share/toolsget/toolsget.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}

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
        "terminal_fg": "#abb2bf",
        'bg_color': '#ffffff',
        'fg_color': '#333333'
    },
    "dark": {
        "primary": "#2980b9",
        "secondary": "#27ae60",
        "bg": "#2c3e50",
        "fg": "#ecf0f1",
        "accent": "#c0392b",
        "warning": "#d35400",
        "terminal_bg": "#1e1e1e",
        "terminal_fg": "#d4d4d4",
        'bg_color': '#2d2d2d',
        'fg_color': '#ffffff'
    }
}

# Yeni tema renkleri
THEME["dark"].update({
    "hover": "#34495e",
    "selected": "#2980b9",
    "border": "#7f8c8d"
})

THEME["light"].update({
    "hover": "#bdc3c7", 
    "selected": "#3498db",
    "border": "#95a5a6"
})

# Yeni tema renkleri ve özellikleri
THEME.update({
    "nord": {
        "primary": "#88C0D0",
        "secondary": "#A3BE8C",
        "bg": "#2E3440",
        "fg": "#ECEFF4",
        "accent": "#BF616A",
        "warning": "#D08770",
        "hover": "#434C5E",
        "selected": "#81A1C1",
        "border": "#4C566A",
        "terminal_bg": "#2E3440",
        "terminal_fg": "#D8DEE9"
    },
    "dracula": {
        "primary": "#BD93F9",
        "secondary": "#50FA7B",
        "bg": "#282A36",
        "fg": "#F8F8F2",
        "accent": "#FF5555",
        "warning": "#FFB86C",
        "hover": "#44475A",
        "selected": "#6272A4",
        "border": "#44475A",
        "terminal_bg": "#282A36",
        "terminal_fg": "#F8F8F2"
    },
    "solarized": {
        "primary": "#268BD2",
        "secondary": "#859900",
        "bg": "#002B36",
        "fg": "#839496",
        "accent": "#DC322F",
        "warning": "#B58900",
        "hover": "#073642",
        "selected": "#586E75",
        "border": "#657B83",
        "terminal_bg": "#002B36",
        "terminal_fg": "#839496"
    }
})

# Yeni tema renkleri
THEMES = {
    # ...existing themes...
    
    "cyberpunk": {
        "primary": "#00ff9f",
        "secondary": "#ff00ff",
        "bg": "#1a1a1a",
        "fg": "#00ff9f",
        "accent": "#ff00ff",
        "warning": "#ffff00",
        "hover": "#2d2d2d",
        "selected": "#00ffff",
        "border": "#ff00ff",
        "terminal_bg": "#000000",
        "terminal_fg": "#00ff9f"
    },
    "material": {
        "primary": "#2196F3",
        "secondary": "#4CAF50",
        "bg": "#FAFAFA",
        "fg": "#212121",
        "accent": "#FF4081",
        "warning": "#FFC107",
        "hover": "#EEEEEE",
        "selected": "#BBDEFB",
        "border": "#BDBDBD",
        "terminal_bg": "#263238",
        "terminal_fg": "#B2CCD6"
    },
    "retro": {
        "primary": "#92CD41",
        "secondary": "#76C2AF",
        "bg": "#222222",
        "fg": "#F7F2DA",
        "accent": "#FE8019",
        "warning": "#D08770",
        "hover": "#333333",
        "selected": "#4A9F45",
        "border": "#4A9F45",
        "terminal_bg": "#1C1C1C",
        "terminal_fg": "#F7F2DA"
    }
}

# Tema açıklamaları
THEME_DESCRIPTIONS = {
    "light": "Açık renkli varsayılan tema",
    "dark": "Koyu renkli varsayılan tema",
    "nord": "Nord renk şeması",
    "dracula": "Dracula renk şeması",
    "solarized": "Solarized Dark renk şeması"
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

# Performance settings
CACHE_SIZE = 100  # Max items in icon cache
QUEUE_CHUNK_SIZE = 5  # Number of packages to process at once
UPDATE_INTERVAL = 1000  # UI update interval in ms

# Error messages
ERRORS = {
    'root_required': 'Bu işlem için yönetici yetkileri gerekli',
    'install_failed': 'Paket kurulumu başarısız: {package}',
    'remove_failed': 'Paket kaldırma başarısız: {package}',
    'update_failed': 'Paket listesi güncellenemedi',
    'polkit_missing': 'PolicyKit bulunamadı'
}

# Terminal settings
TERMINAL = {
    'font': 'Monospace 10',
    'scrollback_lines': 10000,
    'buffer_size': 8192
}

# Queue settings
QUEUE = {
    'max_size': 100,
    'timeout': 300,  # seconds
    'retry_count': 3
}

# Yeni ayarlar
SETTINGS = {
    'auto_update': True,
    'show_terminal': True,
    'minimize_to_tray': True,
    'startup_check': True,
    'save_queue': True
}

# Notification settings
NOTIFICATIONS = {
    'enabled': True,
    'duration': 5000,
    'position': 'top-right'
}

# Yeni komutlar ve kısayollar
SHORTCUTS = {
    'search': 'Ctrl+F',
    'quit': 'Ctrl+Q', 
    'update': 'F5',
    'help': 'F1',
    'terminal': 'F12',
    'clear': 'Ctrl+L',
    'category': 'Alt+C',
    'theme': 'Alt+T'
}

# Terminal komutları
COMMANDS = {
    'update': 'apt-get update',
    'install': 'apt-get install -y {}',
    'remove': 'apt-get remove {}',
    'purge': 'apt-get purge {}',
    'search': 'apt-cache search {}'
}

# Kategoriler ve emojiler
CATEGORIES = {
    'system': {
        'name': '🖥️ Sistem Araçları',
        'icon': 'sys.png',
        'subcategories': {
            'monitor': '📊 Sistem İzleme',
            'backup': '💾 Yedekleme',
            'virtualization': '🔄 Sanallaştırma',
            'terminal': '⌨️ Terminal'
        }
    },
    'network': {
        'name': '🌐 Ağ Araçları',
        'icon': 'net.png',
        'subcategories': {
            'monitor': '📡 Ağ İzleme',
            'security': '🔒 Ağ Güvenliği',
            'analysis': '📊 Ağ Analizi',
            'transfer': '📤 Veri Transfer'
        }
    },
    'security': {
        'name': '🔐 Güvenlik',
        'icon': 'sec.png',
        'subcategories': {
            'scan': '🔍 Güvenlik Tarama',
            'crypto': '🔑 Kriptografi',
            'forensic': '🔎 Adli Analiz',
            'pentest': '🛡️ Penetrasyon Testi'
        }
    },
    'development': {
        'name': '👨‍💻 Geliştirme',
        'icon': 'dev.png',
        'subcategories': {
            'ide': '📝 IDE & Editörler',
            'lang': '🔧 Programlama Dilleri',
            'db': '🗃️ Veritabanları',
            'web': '🌐 Web Geliştirme'
        }
    }
}

# Paket filtreleri
FILTERS = {
    'installed': 'Yüklü Paketler',
    'not_installed': 'Yüklü Olmayan Paketler',
    'updatable': 'Güncellenebilir Paketler',
    'all': 'Tüm Paketler'
}

# Sıralama seçenekleri
SORT_OPTIONS = {
    'name': 'İsme Göre',
    'size': 'Boyuta Göre', 
    'date': 'Tarihe Göre',
    'rating': 'Değerlendirmeye Göre'
}

# Sistem limitleri
LIMITS = {
    'max_concurrent_downloads': 3,
    'max_queue_size': 100,
    'max_retries': 3,
    'timeout': 30,
    'cache_size': 1000,
    'log_size': 10 * 1024 * 1024  # 10MB
}

# CSS dosyasını yükleme kontrolü
CSS_FILE = os.path.join(CSS_DIR, 'style.css')
try:
    with open(CSS_FILE, 'r') as f:
        STYLE = f.read()
except FileNotFoundError:
    logging.error(f"CSS dosyası bulunamadı: {CSS_FILE}")
    STYLE = ""  # Varsayılan boş stil
except Exception as e:
    logging.error(f"CSS dosyası yüklenirken hata: {e}")
    STYLE = ""

# Log dizini oluşturma
try:
    log_path = os.path.expanduser(LOG_DIR)
    os.makedirs(log_path, exist_ok=True)
except Exception as e:
    logging.error(f"Log dizini oluşturulamadı: {e}")
