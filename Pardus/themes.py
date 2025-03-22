from tkinter import ttk

class ModernTheme(ttk.Style):
    def __init__(self):
        super().__init__()
        
        # Temel renkler
        self.colors = {
            "primary": "#4484ce",
            "secondary": "#37b24d",
            "accent": "#f03e3e",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#212529",
            "text_secondary": "#868e96"
        }
        
        self.theme_use('clam')
        self._apply_theme()
        
    def get_color(self, name):
        """Tema rengini güvenli şekilde al"""
        return self.colors.get(name, "#f0f0f0")

    def _apply_theme(self):
        """Temel widget stillerini uygula"""
        # Frame stilleri
        self.configure("TFrame",
            background=self.colors["background"])
            
        # Button stilleri
        self.configure("TButton",
            background=self.colors["primary"],
            foreground="white",
            padding=(10, 5))
            
        # Label stilleri  
        self.configure("TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"])
