import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

class ThemeManager:
    def __init__(self):
        self.themes = {
            "light": {
                "background": "#ffffff",
                "foreground": "#333333",
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "warning": "#f39c12",
                "surface": "#f5f5f5",
                "border": "#dddddd",
                "hover": "#2980b9",
                "selected": "#2980b9",
                "text_primary": "#333333",
                "text_secondary": "#666666",
                "terminal_bg": "#282c34",
                "terminal_fg": "#abb2bf"
            },
            "dark": {
                "background": "#1e1e1e",
                "foreground": "#ffffff",
                "primary": "#61afef",
                "secondary": "#98c379",
                "accent": "#e06c75",
                "warning": "#d19a66",
                "surface": "#252526",
                "border": "#404040",
                "hover": "#4d4d4d",
                "selected": "#404040",
                "text_primary": "#ffffff",
                "text_secondary": "#cccccc",
                "terminal_bg": "#1e1e1e",
                "terminal_fg": "#d4d4d4"
            },
            "pardus": {
                "background": "#fafafa",
                "foreground": "#2c3e50",
                "primary": "#2980b9",
                "secondary": "#27ae60",
                "accent": "#c0392b",
                "warning": "#f1c40f",
                "surface": "#ecf0f1",
                "border": "#bdc3c7",
                "hover": "#3498db",
                "selected": "#2980b9",
                "text_primary": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "terminal_bg": "#2c3e50",
                "terminal_fg": "#ecf0f1"
            }
        }
        self.current_theme = "dark"  # Changed from "light" to "dark"
        self._load_theme()

    def _load_theme(self):
        theme = self.themes[self.current_theme]
        css_provider = Gtk.CssProvider()
        
        # Generate CSS from theme colors
        css = """
        .main-window {
            background-color: %s;
            color: %s;
        }
        
        headerbar {
            background-color: %s;
            color: %s;
            border-bottom: 1px solid %s;
        }
        
        .terminal-view {
            background-color: %s;
            color: %s;
        }

        .search-entry {
            background-color: %s;
            color: %s;
            border: 1px solid %s;
            border-radius: 4px;
            padding: 6px;
        }

        .search-entry:focus {
            border-color: %s;
        }

        .category-button {
            background-color: %s;
            color: %s;
            border: none;
            border-radius: 4px;
            padding: 8px;
        }

        .category-button:hover {
            background-color: %s;
        }
        """ % (
            theme["background"],
            theme["foreground"],
            theme["primary"],
            "#ffffff",
            theme["border"],
            theme["terminal_bg"],
            theme["terminal_fg"],
            theme["surface"],
            theme["text_primary"],
            theme["border"],
            theme["primary"],
            theme["surface"],
            theme["text_primary"],
            theme["hover"]
        )
        
        try:
            css_provider.load_from_data(css.encode())
            
            # Apply CSS
            screen = Gdk.Screen.get_default()
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"CSS loading error: {str(e)}")

    def switch_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._load_theme()
            
    def get_current_theme(self):
        return self.themes[self.current_theme]
        
    def get_color(self, name):
        """Get theme color safely"""
        theme = self.themes[self.current_theme]
        return theme.get(name, "#f0f0f0")
