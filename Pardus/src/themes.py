import os
import gi
import json
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from src.config import THEME, CSS_DIR  # Relative import yerine absolute import kullan

class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.custom_themes = {}
        self.theme_emoji = {
            "light": "☀️",
            "dark": "🌙",
            "nord": "❄️",
            "dracula": "🧛",
            "cyberpunk": "🤖",
            "material": "🎨",
            "retro": "👾"
        }
        self._load_css()
        
    def _load_css(self):
        """Load CSS style"""
        css_file = os.path.join(CSS_DIR, f"{self.current_theme}.css")
        if not os.path.exists(css_file):
            return
            
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(css_file)
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
    def switch_theme(self, theme_name):
        """Switch between light/dark themes"""
        if theme_name not in THEME:
            return False
            
        self.current_theme = theme_name
        self._load_css()
        return True
        
    def create_theme(self, name, colors):
        """Yeni tema oluştur"""
        if name in THEME or name in self.custom_themes:
            return False
            
        self.custom_themes[name] = colors
        return True
        
    def export_theme(self, name):
        """Temayı dosyaya aktar"""
        if name in THEME:
            theme = THEME[name]
        elif name in self.custom_themes:
            theme = self.custom_themes[name]
        else:
            return False
            
        filename = f"{name}_theme.json"
        with open(filename, 'w') as f:
            json.dump(theme, f, indent=4)
        return True
        
    def import_theme(self, filename):
        """Temayı dosyadan içe aktar"""
        try:
            with open(filename) as f:
                theme = json.load(f)
            name = os.path.splitext(os.path.basename(filename))[0]
            self.custom_themes[name] = theme
            return True
        except:
            return False
            
    def get_themes(self):
        """Tüm temaları listele"""
        themes = {
            **THEME,
            **self.custom_themes
        }
        return themes

    def preview_theme(self, theme_name):
        """Tema önizleme"""
        if theme_name not in THEME:
            return None
            
        colors = THEME[theme_name]
        preview = {
            'window': colors['bg'],
            'text': colors['fg'],
            'button': colors['primary'],
            'highlight': colors['selected'],
            'terminal': colors['terminal_bg']
        }
        return preview
        
    def get_theme_css(self, theme_name):
        """Tema için CSS oluştur"""
        if theme_name not in THEME:
            return ""
            
        colors = THEME[theme_name]
        css = f"""
        .window {{
            background-color: {colors['bg']};
            color: {colors['fg']};
        }}
        
        .button {{
            background-color: {colors['primary']};
            color: white;
            border-radius: 4px;
            padding: 8px 12px;
        }}
        
        .button:hover {{
            background-color: {colors['hover']};
        }}
        
        .terminal {{
            background-color: {colors['terminal_bg']};
            color: {colors['terminal_fg']};
            padding: 8px;
            border-radius: 4px;
        }}
        
        .dark-dialog {{
            background-color: {colors['bg']};
            color: {colors['fg']};
            border-radius: 8px;
            padding: 12px;
        }}
        
        .dark-dialog .button {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        .light-dialog {{
            background-color: white;
            color: #333333;
            border-radius: 8px;
            padding: 12px;
        }}
        
        .light-dialog .button {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        .suggested-action {{
            background-color: {colors['secondary']};
            color: white;
            font-weight: bold;
        }}
        
        .destructive-action {{
            background-color: {colors['accent']};
            color: white;
            font-weight: bold;
        }}

        .message-area {{
            padding: 16px;
        }}

        .dialog-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 12px;
        }}

        .dialog-content {{
            line-height: 1.5;
            margin: 12px 0;
        }}
        """
        return css

    def get_theme_icon(self, theme_name):
        """Get emoji icon for theme"""
        return self.theme_emoji.get(theme_name, "🎨")
