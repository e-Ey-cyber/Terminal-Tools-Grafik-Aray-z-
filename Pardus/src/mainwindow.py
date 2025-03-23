import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import json
import queue
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
import sys
import platform
import webbrowser
import time
import shutil
from themes import ThemeManager  # ModernTheme yerine ThemeManager kullanodernTheme
from tools import ToolManager
from queue_manager import QueueManager  # src. ile import et
from config import THEME, ICONS, STYLE  # src. ile import et
import gi
import psutil
import queue
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application)
        
        # Initialize queue
        self.queue_manager = QueueManager(self)
        self.download_queue = queue.Queue()
        
        # Set application icon
        try:
            icon_path = os.path.join("icons", ICONS["app_logo"]) 
            icon = GdkPixbuf.Pixbuf.new_from_file(icon_path)
            self.set_icon(icon)
            Gtk.Window.set_default_icon(icon)
        except Exception as e:
            print(f"Icon loading error: {e}")

class ModernUI(ttk.Style):
    def __init__(self):
        ttk.Style.__init__(self)
        self.theme_use('clam')
        
        # Renkler
        self.primary = "#3498db"  # Ana renk (mavi)
        self.secondary = "#2ecc71"  # İkincil renk (yeşil)
        self.bg_color = "#f5f5f5"  # Arka plan rengi (açık gri)
        self.fg_color = "#333333"  # Yazı rengi (koyu gri)
        self.accent = "#e74c3c"  # Vurgu rengi (kırmızı)
        self.warning = "#f39c12"  # Uyarı rengi (turuncu)
        
        # Buton stilleri
        self.configure('TButton', 
                      background=self.primary, 
                      foreground='white', 
                      font=('Arial', 10),
                      padding=6,
                      borderwidth=0,
                      relief="flat")
        
        self.map('TButton', 
                background=[('active', self.primary), 
                           ('pressed', '#2980b9')])
        
        # Oval butonlar için özel stil
        self.configure('Oval.TButton', 
                      background=self.primary,
                      foreground='white',
                      borderwidth=0,
                      focusthickness=0,
                      focuscolor=self.primary)
        
        # Sekme stilleri
        self.configure('TNotebook', 
                      background=self.bg_color)
        
        self.configure('TNotebook.Tab', 
                      background=self.bg_color,
                      foreground=self.fg_color,
                      padding=[12, 4],
                      font=('Arial', 10))
        
        self.map('TNotebook.Tab', 
                background=[('selected', self.primary)],
                foreground=[('selected', 'white')])
        
        # Çerçeve stilleri
        self.configure('TFrame', 
                      background=self.bg_color)
        
        # Etiket stilleri
        self.configure('TLabel', 
                      background=self.bg_color, 
                      foreground=self.fg_color,
                      font=('Arial', 10))
        
        # Kategori etiketi stili
        self.configure('Category.TLabel',
                      background=self.primary,
                      foreground='white',
                      font=('Arial', 8),
                      padding=[4, 2])
        
        # Giriş kutusu stilleri
        self.configure('TEntry', 
                      fieldbackground='white',
                      foreground=self.fg_color,
                      padding=6)
        
        # İlerleme çubuğu stilleri
        self.configure('Horizontal.TProgressbar', 
                      background=self.secondary,
                      troughcolor=self.bg_color)
        
        # Alternatif satır renkleri için stiller
        self.configure('EvenRow.TFrame', 
                      background='#f0f0f0')
        
        self.configure('OddRow.TFrame', 
                      background='#ffffff')

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=15, bg="#3498db", fg="white", 
                 hover_bg="#2980b9", width=120, height=30, **kwargs):
        
        # Parent widget'ın arka plan rengini güvenli şekilde al
        parent_bg = "#f0f0f0"
        try:
            if isinstance(parent, ttk.Frame):
                parent_bg = parent.winfo_toplevel().cget("background")
            else:
                parent_bg = "#f0f0f0"
        except:
            pass
            
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, background=parent_bg)
                        
        self.radius = radius
        self.bg = bg
        self.original_bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.state = "normal"
        
        self.create_rounded_rect()
        self.create_text_on_button()
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def create_rounded_rect(self):
        self.rect = self.create_rounded_rectangle(0, 0, self.width, self.height, 
                                                 self.radius, fill=self.bg, outline="")
        
    def create_text_on_button(self):
        self.button_text = self.create_text(self.width/2, self.height/2, 
                                           text=self.text, fill=self.fg, 
                                           font=("Arial", 10, "bold"))
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        if self.state == "normal":
            self.itemconfig(self.rect, fill=self.hover_bg)
        
    def on_leave(self, event):
        if self.state == "normal":
            self.itemconfig(self.rect, fill=self.bg)
        
    def on_click(self, event):
        if self.state == "normal" and self.command:
            self.command()
            
    def config(self, **kwargs):
        if "state" in kwargs:
            if kwargs["state"] == "disabled":
                self.state = "disabled"
                self.itemconfig(self.rect, fill="#cccccc")
                self.bg = "#cccccc"
            elif kwargs["state"] == "normal":
                self.state = "normal"
                self.itemconfig(self.rect, fill=self.original_bg)
                self.bg = self.original_bg
        
        if "command" in kwargs:
            self.command = kwargs["command"]
            
        if "text" in kwargs:
            self.text = kwargs["text"]
            self.itemconfig(self.button_text, text=self.text)

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application)
        
        # Temel değişkenler
        self.icon_cache = {}
        self.icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        self.is_installing = False
        self.selected_tool_id = None
        
        # Queue manager'ı başlat
        self.queue_manager = QueueManager(self)
        
        # Tools ve Theme manager başlat 
        self.tool_manager = ToolManager()
        self.terminal_tools = self.tool_manager.get_tools()
        self.categories = self.tool_manager.get_categories()
        self.icon_urls = self.tool_manager.get_icon_urls()
        self.theme_manager = ThemeManager()
        
        # Pencere ayarları
        self.set_title("Tools Get")
        self.set_default_size(1000, 750)
        self.get_style_context().add_class('main-window')
        
        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Tools Get")
        header.set_subtitle("Terminal Araçları Yükleyici")
        
        # Add logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ToolsGet1.png")
            logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 50,  100, True)
            logo_image = Gtk.Image.new_from_pixbuf(logo_pixbuf)
            header.pack_start(logo_image)
        except Exception as e:
            print(f"Logo yüklenemedi: {str(e)}")

        # Üst menü butonları
        menu_button = Gtk.MenuButton()
        menu_button.set_tooltip_text("Menü")
        
        menu = Gio.Menu()
        menu.append("Paket Listesini Güncelle", "app.update")
        menu.append("Sistem Bilgisi", "app.sysinfo")
        menu.append("Hakkında", "app.about")
        
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        # Tema değiştirme butonu
        theme_button = Gtk.Button()
        theme_icon = Gio.ThemedIcon(name="display-brightness-symbolic")
        theme_image = Gtk.Image.new_from_gicon(theme_icon, Gtk.IconSize.BUTTON)
        theme_button.add(theme_image)
        theme_button.connect("clicked", self.on_theme_button_clicked)
        header.pack_end(theme_button)
        
        # Terminal açma butonu
        terminal_button = Gtk.Button()
        terminal_icon = Gio.ThemedIcon(name="utilities-terminal-symbolic")
        terminal_image = Gtk.Image.new_from_gicon(terminal_icon, Gtk.IconSize.BUTTON)
        terminal_button.add(terminal_image)
        terminal_button.connect("clicked", self.show_terminal)
        header.pack_end(terminal_button)
        
        self.set_titlebar(header)
        
        # Ana container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

        # Arama çubuğu
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(12)
        
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Araç ara...")
        search_box.pack_start(self.search_entry, True, True, 0)
        
        search_button = Gtk.Button(label="Ara")
        search_button.connect("clicked", self.on_search_clicked)
        search_box.pack_start(search_button, False, False, 0)
        
        main_box.pack_start(search_box, False, False, 0)

        # Ana içerik bölümü
        paned = Gtk.Paned()
        paned.set_position(250)
        main_box.pack_start(paned, True, True, 0)
        
        # Sol panel - Kategoriler ve araç listesi
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Kategori seçici
        category_store = Gtk.ListStore(str)
        category_store.append(["Tümü"])
        for category in self.categories:
            category_store.append([category])
        
        self.category_combo = Gtk.ComboBoxText()
        self.category_combo.set_model(category_store)
        self.category_combo.set_active(0)
        self.category_combo.connect("changed", self.on_category_changed)
        left_box.pack_start(self.category_combo, False, False, 0)
        
        # Araç listesi
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.tools_list = Gtk.ListBox()
        self.tools_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.tools_list.connect('row-activated', self.on_tool_selected)
        scrolled.add(self.tools_list)
        left_box.pack_start(scrolled, True, True, 0)
        
        paned.add1(left_box)
        
        # Sağ panel - Araç detayları
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Detay alanı
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.detail_box.set_margin_start(12)
        self.detail_box.set_margin_end(12)
        self.detail_box.set_margin_top(12)
        
        self.tool_name_label = Gtk.Label()
        self.tool_name_label.set_markup("<big><b>Bir araç seçin</b></big>")
        self.tool_name_label.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(self.tool_name_label, False, False, 0)
        
        self.tool_desc_label = Gtk.Label()
        self.tool_desc_label.set_text("Detayları görmek için sol panelden bir araç seçin")
        self.tool_desc_label.set_line_wrap(True)
        self.tool_desc_label.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(self.tool_desc_label, False, False, 0)
        
        # Progress info area
        progress_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.detail_box.pack_start(progress_info, False, False, 0)
        
        self.progress_label = Gtk.Label(label="")
        progress_info.pack_start(self.progress_label, False, False, 0)
        
        # Queue buttons
        queue_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.detail_box.pack_start(queue_box, False, False, 0)
        
        self.queue_button = Gtk.Button(label="Sıraya Ekle")
        self.queue_button.connect("clicked", self.add_to_queue_clicked)
        self.queue_button.set_sensitive(False)
        queue_box.pack_start(self.queue_button, False, False, 0)
        
        self.start_queue_button = Gtk.Button(label="Sırayı Başlat")
        self.start_queue_button.connect("clicked", self.start_queue)
        queue_box.pack_start(self.start_queue_button, False, False, 0)
        
        self.clear_queue_button = Gtk.Button(label="Sırayı Temizle")
        self.clear_queue_button.connect("clicked", self.clear_queue)
        queue_box.pack_start(self.clear_queue_button, False, False, 0)
        
        # Buton grubu
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.install_button = Gtk.Button(label="Yükle")
        self.install_button.connect("clicked", self.on_install_clicked)
        self.install_button.set_sensitive(False)
        button_box.pack_start(self.install_button, False, False, 0)
        
        self.remove_button = Gtk.Button(label="Kaldır")
        self.remove_button.connect("clicked", self.on_remove_clicked)
        self.remove_button.set_sensitive(False)
        button_box.pack_start(self.remove_button, False, False, 0)
        
        self.info_button = Gtk.Button(label="Paket Bilgisi")
        self.info_button.connect("clicked", self.show_package_info)
        self.info_button.set_sensitive(False)
        button_box.pack_start(self.info_button, False, False, 0)
        
        self.detail_box.pack_start(button_box, False, False, 0)
        right_box.pack_start(self.detail_box, False, False, 0)
        
        paned.add2(right_box)
        
        # Terminal için frame
        self.terminal_frame = Gtk.Frame(label="Terminal")
        self.terminal_frame.set_margin_start(12)
        self.terminal_frame.set_margin_end(12)
        self.terminal_frame.set_margin_bottom(12)
        main_box.pack_end(self.terminal_frame, True, True, 0)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        self.terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        terminal_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(terminal_toolbar, False, False, 0)
        
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        terminal_toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)

        # İlerleme çubuğu
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        main_box.pack_end(self.progress_bar, False, False, 0)
        
        # Add status label after the progress bar
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_margin_bottom(6)
        right_box.pack_end(self.status_label, False, False, 0)
        
        self.show_all()
        self.progress_bar.hide()

        # Add SIGINT handler
        self.connect('destroy', self.on_destroy)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

        # Keep level bar in details area and remove bottom progress bar
        self.level_bar = Gtk.LevelBar()
        self.level_bar.set_min_value(0)
        self.level_bar.set_max_value(100)
        self.level_bar.set_value(0)
        self.detail_box.pack_start(self.level_bar, False, False, 0)
        
        # Remove bottom progress bar reference
        # self.progress_bar = Gtk.ProgressBar()
        # self.progress_bar.set_show_text(True)
        # main_box.pack_end(self.progress_bar, False, False, 0)
        
        # Add performance optimizations
        self.tools_list.set_activate_on_single_click(True) # Faster list response
        
        # Cache commonly used widgets
        self._terminal_buffer = self.terminal_view.get_buffer()
        self._status_label = self.status_label
        self._level_bar = self.level_bar
        
        # Optimize terminal output
        self._terminal_text_cache = []
        self._update_terminal_timeout = None

        # Add queue listbox
        self.queue_store = Gtk.ListStore(str, str)  # package_name, display_name
        self.queue_view = Gtk.TreeView(model=self.queue_store)
        self.queue_view.set_headers_visible(False)
        
        column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)
        self.queue_view.append_column(column)
        
        queue_scroll = Gtk.ScrolledWindow()
        queue_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        queue_scroll.add(self.queue_view)
        queue_scroll.set_size_request(-1, 100)
        self.detail_box.pack_start(queue_scroll, True, True, 0)

    def update_progress(self, fraction, text=None):
        """İlerleme çubuğunu güncelle"""
        GLib.idle_add(self.level_bar.set_value, fraction * 100)
        if text:
            GLib.idle_add(self.update_terminal_output, text)
            
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.update_terminal_output(f"$ {' '.join(command)}\n")
        self.update_progress(0.0, "Başlatılıyor...")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
            except Exception as e:
                update_terminal(f"İşlem başlatılamadı: {str(e)}")
                return
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
            except Exception as e:
                update_terminal(f"İşlem başlatılamadı: {str(e)}")
                return
                
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                        
                    if line:
                        update_terminal(line.strip())
                        # İlerlemeyi güncelle
                        if "Unpacking" in line:
                            GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                        elif "Setting up" in line:
                            GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                            
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        update_terminal(success_message)
                    GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
                else:
                    GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
            except Exception as e:
                update_terminal(f"Hata: {str(e)}")
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
            finally:
                self.is_installing = False
                GLib.idle_add(self.status_label.set_text, "Hazır")
                
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
        
        # Update status label immediately
        GLib.idle_add(self.status_label.set_text, "Çalışıyor: " + " ".join(command))

    # Diğer metodları ekle
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start queue processing"""
        if hasattr(self, "queue_manager"):
            self.queue_manager.start_queue()
        else:
            print("Queue manager not initialized")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
            """Process next package in queue"""
            if self.is_installing or not self.is_queue_running:
                return
                
            # Get first item in queue
            iter = self.queue_store.get_iter_first()
            if iter:
                package_name = self.queue_store.get_value(iter, 0)
                display_name = self.queue_store.get_value(iter, 1)
                
                # Remove from queue
                self.queue_store.remove(iter)
                
                # Install package
                self.install_package(package_name, display_name)
                
                # Check progress after delay
                GLib.timeout_add(1000, self.check_queue_progress)
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
    def process_next_package(self):
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        
    def clear_queue(self, button=None):
        """Clear queue"""
        if hasattr(self, "queue_manager"):
            self.queue_manager.clear_queue()
        else:
            print("Queue manager not initialized")
    
    def check_queue_progress(self):
            """Check if current install completed and process next item"""
            if not self.is_installing:
                self.process_next_in_queue()
            return False

    def check_queue_progress(self):
        """Check if current install completed and process next item"""
        if not self.is_installing:
            self.process_next_in_queue()
        return False
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            if self.queue_manager.add_to_queue(tool_info['package'], tool_info['name']):
                self.update_terminal_output(f"{tool_info['name']} kuyruğa eklendi")
            else:
                self.update_terminal_output(f"{tool_info['name']} zaten kuyrukta!")
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.queue_manager.add_to_queue(tool_info['package'], tool_info['name'])
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start processing the installation queue"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
        """Process next package in queue"""
        if self.is_installing or len(self.queue_store) == 0:
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )

    def clear_queue(self, button=None):
        """Clear installation queue"""
        self.queue_store.clear()
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start processing the installation queue"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
        """Process next package in queue"""
        if self.is_installing or len(self.queue_store) == 0:
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )

    def clear_queue(self, button=None):
        """Clear installation queue"""
        self.queue_store.clear()
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start processing the installation queue"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
        """Process next package in queue"""
        if self.is_installing or len(self.queue_store) == 0:
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )

    def clear_queue(self, button=None):
        """Clear installation queue"""
        self.queue_store.clear()
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start processing the installation queue"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
        """Process next package in queue"""
        if self.is_installing or len(self.queue_store) == 0:
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )

    def clear_queue(self, button=None):
        """Clear installation queue"""
        self.queue_store.clear()
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", 
                                       font=("Arial", 14, "bold"), bg=self.style.get_color("background"))
        self.tool_name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.tool_desc_label = tk.Label(details_text_frame, text="Detayları görmek için sol panelden bir araç seçin.", 
                                       wraplength=400, justify=tk.LEFT, bg=self.style.get_color("background"))
        self.tool_desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.tool_buttons_frame = ttk.Frame(self.details_frame)
        self.tool_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Oval butonlar
        self.install_button = RoundedButton(
            self.tool_buttons_frame, text="Yükle", 
            width=100, height=30, bg=self.style.get_color("primary")
        )
        self.install_button.pack(side=tk.LEFT, padx=(0, 5))
        self.install_button.config(state="disabled")
        
        self.queue_button = RoundedButton(
            self.tool_buttons_frame, text="Sıraya Ekle", 
            width=120, height=30, bg=self.style.get_color("secondary")
        )
        self.queue_button.pack(side=tk.LEFT, padx=5)
        self.queue_button.config(state="disabled")
        
        self.info_button = RoundedButton(
            self.tool_buttons_frame, text="Bilgi", 
            width=100, height=30, bg="#9b59b6"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        self.info_button.config(state="disabled")
        
        self.remove_button = RoundedButton(
            self.tool_buttons_frame, text="Kaldır", 
            width=100, height=30, bg=self.style.get_color("accent")
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.config(state="disabled")
        
        # İndirme kuyruğu
        queue_frame = ttk.LabelFrame(right_frame, text="İndirme Kuyruğu", padding=5)
        queue_frame.pack(fill=tk.X, pady=(0, 5))
        
        queue_toolbar = ttk.Frame(queue_frame)
        queue_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.queue_count_label = ttk.Label(queue_toolbar, text="Kuyrukta 0 araç var")
        self.queue_count_label.pack(side=tk.LEFT)
        
        queue_start_button = RoundedButton(queue_toolbar, text="Kuyruğu Başlat", 
                                          width=120, height=25, bg=self.style.get_color("secondary"),
                                          command=self.start_queue)
        queue_start_button.pack(side=tk.RIGHT, padx=5)
        
        queue_clear_button = RoundedButton(queue_toolbar, text="Kuyruğu Temizle", 
                                          width=120, height=25, bg=self.style.get_color("accent"),
                                          command=self.clear_queue)
        queue_clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Kuyruk listesi
        queue_list_frame = ttk.Frame(queue_frame)
        queue_list_frame.pack(fill=tk.X, pady=5)
        
        self.queue_listbox = tk.Listbox(queue_list_frame, height=3, bg="#f9f9f9", 
                                       font=("Consolas", 10))
        self.queue_listbox.pack(fill=tk.X, expand=True)
        
        # Terminal çıktısı
        terminal_frame = ttk.LabelFrame(right_frame, text="Terminal Çıktısı", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        terminal_toolbar = ttk.Frame(terminal_frame)
        terminal_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = RoundedButton(terminal_toolbar, text="Temizle", 
                                    width=80, height=25, bg=self.style.get_color("primary"),
                                    command=self.clear_terminal)
        clear_button.pack(side=tk.RIGHT)
        
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=15, 
                                                       font=("Consolas", 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.config(state=tk.DISABLED, bg="#282c34", fg="#abb2bf")
        
        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           mode='indeterminate', length=150)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def filter_tools(self):
        self.load_tools()
    
    def show_tool_details(self, tool_id):
        tool_info = self.terminal_tools[tool_id]
        
        # İkonu güncelle
        try:
            icon = self.get_icon(tool_id, size=(48, 48))
            self.tool_icon_label.config(image=icon)
            self.tool_icon_label.image = icon  # Referansı koru
        except Exception as e:
            print(f"İkon gösterilirken hata: {str(e)}")
        
        # Araç adını güncelle
        self.tool_name_label.config(text=tool_info["name"])
        
        # Açıklamayı güncelle
        self.tool_desc_label.config(text=tool_info["description"])
        
        # Butonları etkinleştir ve komutları güncelle
        self.install_button.config(
            state="normal",
            command=lambda: self.install_package(tool_info["package"], tool_info["name"])
        )
        
        self.queue_button.config(
            state="normal",
            command=lambda: self.add_to_queue(tool_info["package"], tool_info["name"])
        )
        
        self.info_button.config(
            state="normal",
            command=lambda: self.show_package_info(tool_info["package"])
        )
        
        self.remove_button.config(
            state="normal",
            command=lambda: self.remove_package(tool_info["package"], tool_info["name"])
        )
    
    def update_terminal_output(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text + "\n")
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_terminal(self):
        # Terminal çıktısını temizleme işlemleri
        pass
    
    def run_command(self, command, success_message=None):
        self.is_installing = True
        self.status_var.set("Çalışıyor: " + " ".join(command))
        self.update_terminal_output("> " + " ".join(command))
        
        # İlerleme çubuğunu başlat
        self.progress_bar.start(10)
        
        def execute_command():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                for line in process.stdout:
                    self.update_terminal_output(line.strip())
                
                for line in process.stderr:
                    self.update_terminal_output("HATA: " + line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    if success_message:
                        self.update_terminal_output(success_message)
                    self.status_var.set("İşlem başarıyla tamamlandı")
                else:
                    self.status_var.set(f"İşlem başarısız oldu (Kod: {process.returncode})")
            except Exception as e:
                self.update_terminal_output(f"Hata oluştu: {str(e)}")
                self.status_var.set("Hata oluştu")
            finally:
                self.is_installing = False
                # İlerleme çubuğunu durdur
                self.progress_bar.stop()
                
                # Kuyruk çalışıyorsa bir sonraki işleme geç
                if self.is_queue_running and not self.download_queue.empty():
                    self.root.after(1000, self.process_next_in_queue)
        
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
    
    def install_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Yükleme", f"{display_name} paketini yüklemek istiyor musunuz?"):
            # Parola sorma işlemi için pkexec kullanıyoruz
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
    
    def remove_package(self, package_name, display_name=None):
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if not display_name:
            display_name = package_name
            
        if messagebox.askyesno("Paket Kaldırma", f"{display_name} paketini kaldırmak istiyor musunuz?"):
            self.run_command(
                ["pkexec", "apt-get", "remove", "-y", package_name],
                f"{display_name} paketi başarıyla kaldırıldı."
            )
    
    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        # Add to queue store
        self.queue_store.append([package_name, display_name])
        
        # Update UI
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.status_label.set_text(f"Kuyrukta {len(self.queue_store)} araç var")

    def start_queue(self, button=None):
        """Start processing the installation queue"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor"
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
            
        # Change from checking download_queue to queue_store
        if len(self.queue_store) == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Kuyruk boş"
            )
            dialog.run()
            dialog.destroy()
            return
            
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()

    def process_next_in_queue(self):
        """Process next package in queue"""
        if self.is_installing or len(self.queue_store) == 0:
            if len(self.queue_store) == 0:
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                self.status_label.set_text("Kuyruk tamamlandı")
            return
            
        # Get first item in queue
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            
            # Remove from queue
            self.queue_store.remove(iter)
            
            # Install package
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )

    def clear_queue(self, button=None):
        """Clear installation queue"""
        self.queue_store.clear()
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.status_label.set_text("Kuyruk temizlendi")
        self.is_queue_running = False
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
    def start_queue(self, button=None):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="İşlem Devam Ediyor",
            )
            dialog.format_secondary_text("Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            dialog.run()
            dialog.destroy()
            return
        
        if self.download_queue.empty():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="İndirme kuyruğu boş"
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        try:
            if self.is_installing or self.download_queue.empty():
                if self.download_queue.empty():
                    self.is_queue_running = False
                    self.update_terminal_output("İndirme kuyruğu tamamlandı.")
                return

            # Kuyruktan bir sonraki paketi al
            package_name, display_name = self.download_queue.get()
            
            # Paketi yükle
            self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
            self.run_command(
                ["pkexec", "apt-get", "install", "-y", package_name],
                f"{display_name} paketi başarıyla yüklendi."
            )
        except Exception as e:
            self.update_terminal_output(f"Hata oluştu: {str(e)}")
        finally:
            self.update_progress(0, "İşlem tamamlandı")
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Clear the queue
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Clear the queue items list
        self.queue_items.clear()
        
        # Update UI
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_progress(0, "Kuyruk temizlendi")
        self.status_label.set_text("Kuyruk boş")
        self.is_queue_running = False
    
    def clear_queue(self, button=None):
        """İndirme kuyruğunu temizle"""
        # Kuyruğu boşalt
        while not self.download_queue.empty():
            self.download_queue.get()
        
        # Listbox'ı temizle
        self.queue_listbox.delete(0, tk.END)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output("İndirme kuyruğu temizlendi.")
    
    def search_package(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Hata", "Lütfen Aradığınız Araç İsmini Girin...")
            return
        
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        self.run_command(
            ["apt-cache", "search", search_term],
            f"'{search_term}' için arama tamamlandı."
        )
    
    def show_package_info(self, button):
        if not hasattr(self, 'selected_tool_id'):
            return
            
        tool_info = self.terminal_tools[self.selected_tool_id]
        package_name = tool_info['package']
        
        try:
            # Paket bilgilerini al
            size = self.get_package_size(package_name)
            version = self.get_package_version(package_name)
            description = self.get_package_description(package_name)
            dependencies = self.get_package_dependencies(package_name)
            installed_size = self.get_package_installed_size(package_name)
            maintainer = self.get_package_maintainer(package_name)
            homepage = self.get_package_homepage(package_name)
            
            # Bilgi penceresini oluştur
            dialog = Gtk.Dialog(
                title=f"Paket Bilgisi - {tool_info['name']}",
                parent=self,
                flags=0,
                buttons=("Kapat", Gtk.ResponseType.CLOSE)
            )
            dialog.set_default_size(600, 400)
            
            content = dialog.get_content_area()
            content.set_spacing(12)
            content.set_margin_start(12)
            content.set_margin_end(12)
            content.set_margin_top(12)
            content.set_margin_bottom(12)
            
            # Bilgi grid'i
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.get_style_context().add_class('package-info')
            
            row = 0
            for label, value in [
                ("Paket Adı:", package_name),
                ("Versiyon:", version),
                ("Boyut:", size),
                ("Kurulum Boyutu:", installed_size),
                ("Geliştirici:", maintainer),
                ("Web Sayfası:", homepage),
                ("Açıklama:", description),
                ("Bağımlılıklar:", dependencies)
            ]:
                label_widget = Gtk.Label(label=label, xalign=0)
                label_widget.get_style_context().add_class('info-label')
                grid.attach(label_widget, 0, row, 1, 1)
                
                value_widget = Gtk.Label(label=value)
                value_widget.set_line_wrap(True)
                value_widget.set_xalign(0)
                value_widget.set_selectable(True)
                value_widget.get_style_context().add_class('info-value')
                grid.attach(value_widget, 1, row, 1, 1)
                
                row += 1
            
            content.add(grid)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Paket bilgisi gösterilirken hata: {str(e)}")

    def get_package_installed_size(self, package):
        """Kurulu paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Installed-Size:'):
                    size_kb = int(line.split()[1])
                    return self.format_size(size_kb * 1024)
        except:
            return "Bilinmiyor"

    def get_package_maintainer(self, package):
        """Paket geliştiricisini al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Maintainer:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Bilinmiyor"

    def get_package_homepage(self, package):
        """Paket web sayfasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Homepage:'):
                    return line.split(':', 1)[1].strip()
        except:
            return "Belirtilmemiş"

    def get_package_version(self, package):
        """Paket versiyonunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "policy", package])
            for line in output.decode().split('\n'):
                if "Installed:" in line:
                    version = line.split(": ")[1].strip()
                    return version if version != "(none)" else "Yüklü değil"
        except:
            return "Bilinmiyor"

    def get_package_description(self, package):
        """Paket açıklamasını al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            description = ""
            desc_started = False
            
            for line in output.decode().split('\n'):
                if line.startswith("Description-tr:"):
                    desc_started = True
                    description = line.split(":", 1)[1].strip()
                elif desc_started and line.startswith(" "):
                    description += "\n" + line.strip()
                elif desc_started:
                    break
                    
            return description or "Açıklama bulunamadı"
        except:
            return "Açıklama alınamadı"

    def get_package_dependencies(self, package):
        """Paket bağımlılıklarını al"""
        try:
            output = subprocess.check_output(["apt-cache", "depends", package])
            deps = []
            
            for line in output.decode().split('\n'):
                if "Depends:" in line:
                    dep = line.split(":", 1)[1].strip()
                    deps.append(dep)
                    
            return "\n".join(deps) if deps else "Bağımlılık yok"
        except:
            return "Bağımlılıklar alınamadı"

    def update_package_list(self):
        # Paket listesini güncelleme işlemleri
        pass
    
    def show_installed_packages(self):
        # Yüklü paketleri gösterme işlemleri
        pass
    
    def show_system_info(self):
        # Sistem bilgilerini gösterme işlemleri
        pass
    
    def export_config(self):
        # Yapılandırmayı dışa aktarma işlemleri
        pass
    
    def import_config(self):
        # Yapılandırmayı içe aktarma işlemleri
        pass
    
    def refresh_icons(self):
        # Simgeleri yenileme işlemleri
        pass
    
    def show_usage(self):
        # Kullanım kılavuzunu gösterme işlemleri
        pass
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for(self)
        about_dialog.set_modal(True)
        
        about_dialog.set_program_name("Tools Get")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.")
        about_dialog.set_copyright("© 2025 Pardus")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_website("https://www.pardus.org.tr")
        about_dialog.set_website_label("Pardus Web Sitesi")
        about_dialog.set_authors(["Pardus Yazılım Ekibi"])
        
        logo = GdkPixbuf.Pixbuf.new_from_file("/usr/share/icons/hicolor/256x256/apps/pardus.png")
        about_dialog.set_logo(logo)
        
        about_dialog.run()
        about_dialog.destroy()

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")

    def get_package_size(self, package):
        """Paket boyutunu al"""
        try:
            output = subprocess.check_output(["apt-cache", "show", package])
            for line in output.decode().split('\n'):
                if line.startswith('Size:'):
                    size_bytes = int(line.split()[1])
                    return self.format_size(size_bytes)
        except:
            return "N/A"
            
    def format_size(self, size):
        """Byte cinsinden boyutu formatla"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def show_terminal(self, button):
        """Terminal penceresini göster"""
        terminal = Gtk.Window(title="Terminal")
        terminal.set_default_size(600, 400)
        
        scrolled = Gtk.ScrolledWindow()
        terminal.add(scrolled)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_view.set_editable(False)
        scrolled.add(self.terminal_view)
        
        terminal.show_all()

    def on_theme_button_clicked(self, button):
        """Theme change handler"""
        current = self.theme_manager.current_theme
        new_theme = "dark" if current == "light" else "light"
        self.theme_manager.switch_theme(new_theme)

    def on_destroy(self, window):
        """Window destroy handler"""
        self.get_application().quit()

        # Get main box from window
        main_box = window.get_child()

        # Create right box for terminal
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(right_box, True, True, 0)

        # Terminal için frame ve buffer
        terminal_frame = Gtk.Frame(label="Terminal")
        terminal_frame.set_margin_start(12)
        terminal_frame.set_margin_end(12)
        terminal_frame.set_margin_bottom(12)
        
        terminal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        terminal_box.set_margin_start(6)
        terminal_box.set_margin_end(6)
        terminal_box.set_margin_top(6)
        terminal_box.set_margin_bottom(6)
        terminal_frame.add(terminal_box)
        
        # Terminal toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        terminal_box.pack_start(toolbar, False, False, 0)
        
        # Terminal temizleme butonu
        clear_button = Gtk.Button(label="Temizle")
        clear_button.connect("clicked", self.clear_terminal)
        toolbar.pack_end(clear_button, False, False, 0)
        
        # Terminal scroll
        terminal_scroll = Gtk.ScrolledWindow()
        terminal_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        terminal_box.pack_start(terminal_scroll, True, True, 0)
        
        self.terminal_view = Gtk.TextView()
        self.terminal_view.set_editable(False)
        self.terminal_view.get_style_context().add_class('terminal-view')
        self.terminal_buffer = self.terminal_view.get_buffer()
        terminal_scroll.add(self.terminal_view)
        
        right_box.pack_start(terminal_frame, True, True, 0)

        # Durum çubuğu için label
        self.status_label = Gtk.Label(label="Hazır")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_end(self.status_label, False, False, 0)

        # Terminal hoşgeldin mesajı
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                      Tools Get v1.0.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Yapımcı: Eyyüp Efe Adıgüzel                               ║
║  GitHub: https://github.com/e-Ey-cyber                      ║
║  E-posta: eyupadiguzel20@gmail.com                         ║
╠══════════════════════════════════════════════════════════════╣
║  Terminal araçlarını kolayca yükleyebileceğiniz            ║
║  bir grafiksel kullanıcı arayüzü.                          ║
║                                                            ║
║  Kullanım:                                                 ║
║  - Sol panelden bir araç seçin                            ║
║  - Yükle butonuna tıklayın                                ║
║  - Kurulum ilerlemesini buradan takip edin                ║
╚══════════════════════════════════════════════════════════════╝
"""
        self.update_terminal_output(welcome_text)

    def clear_terminal(self, button=None):
        """Terminal çıktısını temizle"""
        if self.terminal_buffer:
            self.terminal_buffer.set_text("")
            self.update_terminal_output("Terminal temizlendi...")
            self.update_terminal_output("Tools Get v1.0.0 - Terminal hazır...")

    def update_terminal_output(self, text):
        """Terminal çıktısını güncelle"""
        if self.terminal_buffer:
            end_iter = self.terminal_buffer.get_end_iter()
            self.terminal_buffer.insert(end_iter, text + "\n")
            # Otomatik kaydırma
            self.terminal_view.scroll_to_iter(self.terminal_buffer.get_end_iter(), 0, False, 0, 0)

    def execute_command(self, command, success_message):
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
    def run_command(self, command, success_message=None):
        """Komutu çalıştır ve çıktıyı terminale yaz"""
        self.is_installing = True
        self.status_label.set_text("Çalışıyor: " + " ".join(command))
        self.update_terminal_output(f"$ {' '.join(command)}")
        
        def update_terminal(line):
            GLib.idle_add(self.update_terminal_output, line)
            
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                    
                if line:
                    update_terminal(line.strip())
                    # İlerlemeyi güncelle
                    if "Unpacking" in line:
                        GLib.idle_add(self.update_progress, 0.3, "Paketler açılıyor...")
                    elif "Setting up" in line:
                        GLib.idle_add(self.update_progress, 0.7, "Kurulum yapılıyor...")
                        
            process.wait()
            
            if process.returncode == 0:
                if success_message:
                    update_terminal(success_message)
                GLib.idle_add(self.update_progress, 1.0, "İşlem tamamlandı")
            else:
                GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
                
        except Exception as e:
            update_terminal(f"Hata: {str(e)}")
            GLib.idle_add(self.update_progress, 0.0, "Hata oluştu")
        finally:
            self.is_installing = False
            GLib.idle_add(self.status_label.set_text, "Hazır")

        # Create and start thread
        thread = threading.Thread(target=lambda: self._execute_command(command, success_message))
        thread.daemon = True
        thread.start()

    def add_to_queue_clicked(self, *args):
        """Add current package to queue"""
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.add_to_queue(tool_info['package'], tool_info['name'])
            
    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip().lower()
        self.load_tools(search_text)

    def on_category_changed(self, combo):
        self.load_tools()

    def on_tool_selected(self, listbox, row):
        if row is None:
            return
            
        tool_id = row.get_name()
        tool_info = self.terminal_tools[tool_id]
        
        # Detayları güncelle
        self.tool_name_label.set_markup(f"<big><b>{tool_info['name']}</b></big>")
        self.tool_desc_label.set_text(tool_info['description'])
        
        # Butonları aktif et
        self.install_button.set_sensitive(True)
        self.remove_button.set_sensitive(True)
        self.info_button.set_sensitive(True)
        self.queue_button.set_sensitive(True)
        
        # Seçili tool_id'yi sakla
        self.selected_tool_id = tool_id

    def on_install_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.install_package(tool_info['package'], tool_info['name'])

    def on_remove_clicked(self, button):
        if hasattr(self, 'selected_tool_id'):
            tool_info = self.terminal_tools[self.selected_tool_id]
            self.remove_package(tool_info['package'], tool_info['name'])

    def load_tools(self, search_filter=None):
        # Mevcut listeyi temizle
        for child in self.tools_list.get_children():
            self.tools_list.remove(child)
            
        # Kategori filtresini al
        selected_category = self.category_combo.get_active_text()
        
        # Araçları filtrele ve sırala
        filtered_tools = {}
        for tool_id, tool_info in self.terminal_tools.items():
            if selected_category != "Tümü" and tool_info["category"] != selected_category:
                continue
                
            if search_filter:
                if (search_filter not in tool_info["name"].lower() and 
                    search_filter not in tool_info["description"].lower()):
                    continue
                    
            filtered_tools[tool_id] = tool_info
            
        # Sıralı araçları listele
        for tool_id, tool_info in sorted(filtered_tools.items(), key=lambda x: x[1]["name"]):
            row = Gtk.ListBoxRow()
            row.set_name(tool_id)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.add(hbox)
            
            # İkon ekle
            icon = Gtk.Image()
            icon_theme = Gtk.IconTheme.get_default()
            try:
                pixbuf = icon_theme.load_icon(tool_info["package"], 24, 0)
                icon.set_from_pixbuf(pixbuf)
            except:
                icon.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
            hbox.pack_start(icon, False, False, 0)
            
            # İsim ve açıklama
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=tool_info["name"], xalign=0)
            name.get_style_context().add_class('tool-name')
            vbox.pack_start(name, False, False, 0)
            
            desc = Gtk.Label(label=tool_info["description"], xalign=0)
            desc.get_style_context().add_class('tool-description')
            desc.set_line_wrap(True)
            vbox.pack_start(desc, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            self.tools_list.add(row)
            
        self.show_all()

    def download_icons(self):
        """İkon dosyalarını indir"""
        # İkon dizini yoksa oluştur
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
        
        # Her araç için ikon indir
        for tool_id, tool_info in self.terminal_tools.items():
            icon_path = os.path.join(self.icon_dir, tool_info["icon"])
            
            # İkon dosyası yoksa ve URL varsa indir
            if not os.path.exists(icon_path) and tool_id in self.icon_urls:
                try:
                    url = self.icon_urls[tool_id]
                    response = requests.get(url, stream=True, timeout=5)
                    if response.status_code == 200:
                        with open(icon_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    print(f"İkon indirilemedi: {tool_id} - {str(e)}")
    
    def get_icon(self, tool_id, size=(32, 32)):
        """Araç için ikon al, yoksa varsayılan ikon kullan"""
        cache_key = f"{tool_id}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        tool_info = self.terminal_tools[tool_id]
        icon_path = os.path.join(self.icon_dir, tool_info["icon"])
        
        try:
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(img)
                self.icon_cache[cache_key] = icon
                return icon
        except Exception as e:
            print(f"İkon yüklenemedi: {tool_id} - {str(e)}")
        
        # Varsayılan ikon
        default_icon = self.create_default_icon(tool_info["name"], size)
        self.icon_cache[cache_key] = default_icon
        return default_icon
    
    def create_default_icon(self, name, size=(32, 32)):
        """Varsayılan ikon oluştur"""
        img = Image.new('RGBA', size, color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)  # ImageTk.Draw yerine ImageDraw.Draw kullan
        
        # Font boyutunu hesapla
        font_size = min(size[0], size[1]) // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        
        # İlk harfi ekle
        first_letter = name[0].upper() if name else "T"
        
        # Text boyutunu hesapla ve merkeze yerleştir
        text_bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), first_letter, fill="white", font=font)
        
        icon = ImageTk.PhotoImage(img)
        return icon
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Paket Listesini Güncelle", command=self.update_package_list)
        file_menu.add_command(label="Yapılandırmayı Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Yapılandırmayı İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Yüklü Paketleri Göster", command=self.show_installed_packages)
        tools_menu.add_command(label="Sistem Bilgisi", command=self.show_system_info)
        tools_menu.add_command(label="Terminal Çıktısını Temizle", command=self.clear_terminal)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        # Yardımcı araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Paket Yükleyici", command=self.show_package_installer)
        tools_menu.add_command(label="Paket Kaldırıcı", command=self.show_package_remover)
        tools_menu.add_command(label="Paket Bilgisi", command=self.show_package_info)
        menubar.add_cascade(label="Yardımcı Araçlar", menu=tools_menu)

        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Simgeleri Yenile", command=self.refresh_icons)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Kullanım", command=self.show_usage)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_content(self):
        # Ana çerçeve
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Üst kısım (başlık ve arama)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo ve başlık
        header_frame = ttk.Frame(top_frame)
        header_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Logo eklemek için - bg_color yerine get_color kullan
        logo_text = tk.Label(header_frame, text="🛠️", font=("Arial", 24), 
                            background=self.style.get_color("background"))
        logo_text.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Label'ların arka plan renklerini düzelt
        label = tk.Label(title_frame, text="Tools Get", font=("Arial", 20, "bold"), 
                        fg=self.style.get_color("primary"), 
                        background=self.style.get_color("background"))
        label.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Terminal Araçları Yükleyici", 
                          font=("Arial", 12), 
                          fg=self.style.get_color("text"), 
                          background=self.style.get_color("background"))
        subtitle.pack(anchor=tk.W)
        
        # Arama çubuğu
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        search_label = ttk.Label(search_frame, text="Araç Ara:")
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_package())
        
        # Oval arama butonu
        search_button = RoundedButton(
            search_frame, 
            text="Ara", 
            command=self.search_package,
            width=80, 
            height=30, 
            bg=self.style.get_color("primary")
        )
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Ana içerik bölümü (paned window)
        content_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel (kategoriler ve araçlar)
        left_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(left_frame, weight=3)
        
        # Kategori seçimi
        category_frame = ttk.LabelFrame(left_frame, text="Kategoriler", padding=5)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.category_var = tk.StringVar(value="Tümü")
        category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                        state="readonly", width=30)
        category_combobox["values"] = ["Tümü"] + self.categories
        category_combobox.pack(fill=tk.X, padx=5, pady=5)
        category_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_tools())
        
        # Araçlar listesi
        tools_frame = ttk.LabelFrame(left_frame, text="Terminal Araçları", padding=5)
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araçlar için kaydırılabilir çerçeve
        tools_canvas = tk.Canvas(tools_frame, bg=self.style.get_color("background"), highlightthickness=0)
        tools_scrollbar = ttk.Scrollbar(tools_frame, orient="vertical", command=tools_canvas.yview)
        self.tools_scrollable_frame = ttk.Frame(tools_canvas)
        
        self.tools_scrollable_frame.bind(
            "<Configure>",
            lambda e: tools_canvas.configure(scrollregion=tools_canvas.bbox("all"))
        )
        
        tools_canvas.create_window((0, 0), window=self.tools_scrollable_frame, anchor="nw")
        tools_canvas.configure(yscrollcommand=tools_scrollbar.set)
        
        tools_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tools_scrollbar.pack(side="right", fill="y")
        
        # Araçları yükle
        self.load_tools()
        
        # Sağ panel (araç detayları ve terminal)
        right_frame = ttk.Frame(content_paned, padding=5)
        content_paned.add(right_frame, weight=4)
        
        # Araç detayları
        self.details_frame = ttk.LabelFrame(right_frame, text="Araç Detayları", padding=10)
        self.details_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Varsayılan detay içeriği
        self.tool_icon_label = tk.Label(self.details_frame, bg=self.style.get_color("background"))
        self.tool_icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        details_text_frame = ttk.Frame(self.details_frame)
        details_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tool_name_label = tk.Label(details_text_frame, text="Bir araç seçin", )