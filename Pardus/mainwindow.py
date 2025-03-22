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
from themes import ModernTheme
from tools import ToolManager

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

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Tools Get")
        self.root.geometry("1000x750")
        self.root.minsize(900, 700)
        
        # Modern tema uygula
        self.style = ModernTheme()
        
        # Arka plan rengi ayarla - bg_color yerine get_color kullan
        self.root.configure(bg=self.style.get_color("background"))
        
        # İkonları yükleme dizini
        self.icon_cache = {}
        self.icon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        os.makedirs(self.icon_dir, exist_ok=True)
        
        # Uygulama durumu
        self.is_installing = False
        
        # İndirme kuyruğu
        self.download_queue = queue.Queue()
        self.is_queue_running = False
        
        # Tools yöneticisini başlat ve ikonları al
        self.tool_manager = ToolManager()
        self.terminal_tools = self.tool_manager.get_tools()
        self.categories = self.tool_manager.get_categories()
        self.icon_urls = self.tool_manager.get_icon_urls()
        
        # İkonları indir
        self.download_icons()
        
        # Ana menü oluşturma
        self.create_menu()
        
        # Ana içerik alanı
        self.create_content()
        
        # Başlangıç mesajı
        self.update_terminal_output("Tools Get başlatıldı. Terminal araçlarını yüklemek için hazır.")
        self.update_terminal_output(f"İşletim Sistemi: {platform.system()} {platform.release()}")
        self.update_terminal_output(f"Python Sürümü: {platform.python_version()}")
        self.update_terminal_output("Kullanmaya başlamak için bir Araç seçin veya Arama yapın.")
    
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
    
    def load_tools(self):
        try:
            # Önce mevcut araçları temizle
            for widget in self.tools_scrollable_frame.winfo_children():
                widget.destroy()
                
            # Seçilen kategoriye göre filtrele
            selected_category = self.category_var.get()
            filtered_tools = {}
            
            if selected_category == "Tümü":  # String karşılaştırması düzeltildi
                filtered_tools = self.terminal_tools
            else:
                filtered_tools = {
                    tool_id: tool_info 
                    for tool_id, tool_info in self.terminal_tools.items() 
                    if tool_info["category"] == selected_category
                }
            
            # Araçları alfabetik sıraya göre sırala
            sorted_tools = sorted(filtered_tools.items(), key=lambda x: x[1]["name"].lower())
            
            # Her araç için bir satır oluştur
            for i, (tool_id, tool_info) in enumerate(sorted_tools):
                tool_frame = ttk.Frame(self.tools_scrollable_frame)
                tool_frame.pack(fill=tk.X, pady=2)
                
                # İkon ve arka plan rengini güvenli şekilde al
                bg_color = self.style.get_color("background")
                icon = self.get_icon(tool_id, size=(24, 24))
                
                icon_label = tk.Label(
                    tool_frame, 
                    image=icon,
                    bg=bg_color
                )
                icon_label.image = icon  # Referansı koru
                icon_label.pack(side=tk.LEFT, padx=5)
                
                # Araç adı butonu
                tool_button = tk.Button(
                    tool_frame,
                    text=tool_info["name"],
                    font=("Arial", 10),
                    anchor=tk.W,
                    relief=tk.FLAT,
                    bg=self.style.get_color("background"),
                    activebackground=self.style.get_color("primary"),
                    activeforeground="white",
                    padx=5,
                    pady=5,
                    highlightthickness=0,
                    command=lambda t_id=tool_id: self.show_tool_details(t_id)
                )
                tool_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Kategori etiketi
                category_label = ttk.Label(
                    tool_frame,
                    text=tool_info["category"],
                    style="Category.TLabel"
                )
                category_label.pack(side=tk.RIGHT, padx=5)
                
        except Exception as e:
            print(f"Araçlar yüklenirken hata: {str(e)}")
        
        # Kaydırma çubuğunu güncelle
        self.tools_scrollable_frame.update_idletasks()
    
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
        """Paketi indirme kuyruğuna ekle"""
        if not display_name:
            display_name = package_name
        
        # Paketi kuyruğa ekle
        self.download_queue.put((package_name, display_name))
        
        # Listbox'a ekle
        self.queue_listbox.insert(tk.END, display_name)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Bilgi mesajı
        self.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
    
    def update_queue_count(self):
        """Kuyruk sayısını güncelle"""
        count = self.queue_listbox.size()
        self.queue_count_label.config(text=f"Kuyrukta {count} araç var")
    
    def start_queue(self):
        """İndirme kuyruğunu başlat"""
        if self.is_installing:
            messagebox.showwarning("İşlem Devam Ediyor", "Lütfen mevcut işlemin tamamlanmasını bekleyin.")
            return
        
        if self.download_queue.empty():
            messagebox.showinfo("Bilgi", "İndirme kuyruğu boş.")
            return
        
        self.is_queue_running = True
        self.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next_in_queue()
    
    def process_next_in_queue(self):
        """Kuyruktan sıradaki paketi işle"""
        if self.is_installing or self.download_queue.empty():
            if self.download_queue.empty():
                self.is_queue_running = False
                self.update_terminal_output("İndirme kuyruğu tamamlandı.")
            return
        
        # Kuyruktan bir sonraki paketi al
        package_name, display_name = self.download_queue.get()
        
        # Listbox'tan kaldır
        self.queue_listbox.delete(0)
        
        # Kuyruk sayısını güncelle
        self.update_queue_count()
        
        # Paketi yükle
        self.update_terminal_output(f"Kuyruktan yükleniyor: {display_name}")
        self.run_command(
            ["pkexec", "apt-get", "install", "-y", package_name],
            f"{display_name} paketi başarıyla yüklendi."
        )
    
    def clear_queue(self):
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
    
    def show_package_info(self, package_name):
        # Paket bilgisi gösterme işlemleri
        pass
    
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
        """Hakkında penceresini göster"""
        about_text = """Tools Get v1.0

Terminal araçlarını kolayca yükleyebileceğiniz bir grafiksel araç.

Geliştirici: Pardus Yazılım Ekibi
Lisans: GPL v3
Web: https://www.pardus.org.tr

© 2025 Pardus"""
        messagebox.showinfo("Hakkında", about_text)

    def show_package_installer(self):
        """Paket yükleyici penceresini göster"""
        messagebox.showinfo("Paket Yükleyici", "Bu özellik henüz tamamlanmadı.")

    def show_package_remover(self):  
        """Paket kaldırıcı penceresini göster"""
        messagebox.showinfo("Paket Kaldırıcı", "Bu özellik henüz tamamlanmadı.")