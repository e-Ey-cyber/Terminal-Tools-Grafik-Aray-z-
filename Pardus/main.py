#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import logging
import sys
import traceback
from mainwindow import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("toolsget.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ToolsGet")

def center_window(window):
    """Pencereyi ekranın ortasına konumlandırır."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def initialize_app():
    """Uygulamayı başlatır ve ana pencereyi yapılandırır."""
    try:
        root = tk.Tk()
        root.withdraw()  # Önce pencereyi gizle
        
        # Hata yakalama mekanizması
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Yakalanmamış istisnaları işle"""
            if issubclass(exc_type, KeyboardInterrupt):
                # Klavye kesintilerini normal şekilde işle
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Hata mesajını logla
            logger.error("Yakalanmamış istisna:", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Kullanıcıya bilgi ver
            error_msg = f"Beklenmeyen bir hata oluştu:\n{exc_value}\n\nDetaylar günlük dosyasına kaydedildi."
            messagebox.showerror("Hata", error_msg)
        
        # Global istisna yakalayıcıyı ayarla
        sys.excepthook = handle_exception
        
        # Ana pencere ayarları
        root.title("Tools Get")
        root.geometry("1200x800")
        root.minsize(1000, 750)
        
        # Ana pencereyi oluştur
        app = MainWindow(root)
        
        # Pencereyi ortala ve göster
        center_window(root)
        root.deiconify()  # Pencereyi göster
        
        return root, app
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Uygulama başlatılırken hata oluştu: {e}\n{error_details}")
        messagebox.showerror("Başlatma Hatası", 
                            f"Uygulama başlatılırken bir hata oluştu:\n{e}\n\nLütfen günlük dosyasını kontrol edin.")
        raise

def main():
    """Ana uygulama döngüsünü başlatır."""
    try:
        root, app = initialize_app()
        root.mainloop()
    except Exception as e:
        logger.error(f"Kritik hata: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Kritik Hata", 
                            f"Uygulama çalışırken kritik bir hata oluştu:\n{e}\n\nUygulama kapatılacak.")
        sys.exit(1)

if __name__ == "__main__":
    main()