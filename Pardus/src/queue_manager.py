import queue
import logging
import threading
from gi.repository import Gtk, GLib
from src.config import QUEUE  # Absolute import
from src.utils.system import SystemMonitor  # Absolute import

class QueueManager:
    def __init__(self, window):
        self.window = window
        self.is_queue_running = False  # Kuyruk durumu için flag
        self.current_package = None  # Şu an işlenen paket
        self._lock = threading.Lock()  # Thread güvenliği için lock
        
        # İşlem kuyruğu
        self.process_queue = queue.Queue(maxsize=QUEUE['max_size'])
        
        # Kuyruk listesi için store
        self.queue_store = Gtk.ListStore(str, str)  # package_name, display_name
        
        # Create queue view
        self.queue_view = Gtk.TreeView(model=self.queue_store)
        self.queue_view.set_headers_visible(False)
        
        column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)
        self.queue_view.append_column(column)
        
        # Sistem izleme için
        self.system_monitor = SystemMonitor()

    def add_package(self, package_name, display_name=None):
        """Paket ekleme"""
        if not display_name:
            display_name = package_name
            
        # Eğer paket zaten kuyrukta varsa ekleme
        iter = self.queue_store.get_iter_first()
        while iter:
            if self.queue_store[iter][0] == package_name:
                self.window.update_terminal_output(f"{display_name} zaten kuyrukta")
                return False
            iter = self.queue_store.iter_next(iter)
            
        try:
            # İşlem kuyruğuna ekle
            self.process_queue.put_nowait((package_name, display_name))
            
            # UI listesine ekle
            self.queue_store.append([package_name, display_name])
            
            self.window.update_terminal_output(f"{display_name} kuyruğa eklendi")
            self.update_status()
            return True
        except queue.Full:
            logging.error("Kuyruk dolu")
            return False

    def start_processing(self):
        """Kuyruk işlemini başlat"""
        if self.is_queue_running:
            self.window.update_terminal_output("❌ Kuyruk zaten çalışıyor")
            return False
            
        if self.process_queue.empty():
            self.window.update_terminal_output("❌ Kuyruk boş")
            return False
            
        self.is_queue_running = True
        
        # Butonları güncelle
        GLib.idle_add(self.window.queue_button.set_sensitive, False)
        GLib.idle_add(self.window.start_queue_button.set_sensitive, False) 
        GLib.idle_add(self.window.clear_queue_button.set_sensitive, False)
        
        # Thread'i başlat
        threading.Thread(target=self._process_queue, daemon=True).start()
        
        self.window.update_terminal_output("✅ Kuyruk işlemi başlatıldı")
        return True

    def clear_queue(self):
        """Kuyruğu temizle"""
        if self.is_queue_running:
            self.window.update_terminal_output("❌ Kuyruk çalışırken temizlenemez") 
            return False
            
        with self._lock:
            while not self.process_queue.empty():
                try:
                    self.process_queue.get_nowait()
                    self.process_queue.task_done()
                except queue.Empty:
                    break
                
            self.queue_store.clear()
            
            # Butonları güncelle
            GLib.idle_add(self.window.queue_button.set_sensitive, True)
            GLib.idle_add(self.window.start_queue_button.set_sensitive, False)
            GLib.idle_add(self.window.clear_queue_button.set_sensitive, False)
            
            self.window.update_terminal_output("✅ Kuyruk temizlendi")
            self.update_status()
            return True

    def _process_queue(self):
        """Kuyruktaki paketleri işle"""
        while not self.process_queue.empty() and self.is_queue_running:
            try:
                with self._lock:
                    package_name, display_name = self.process_queue.get()
                    self.current_package = package_name
                
                # Paketi yükle    
                result = self.window.install_package(package_name, display_name)
                
                if result:
                    GLib.idle_add(self._remove_from_store, package_name)
                    GLib.idle_add(self.window.update_terminal_output,
                                f"✅ {display_name} başarıyla kuruldu")
                else:
                    GLib.idle_add(self.window.update_terminal_output,
                                f"❌ {display_name} kurulumu başarısız")
                    
            except Exception as e:
                logging.error(f"Paket yükleme hatası {package_name}: {e}")
                GLib.idle_add(self.window.update_terminal_output, f"❌ Hata: {str(e)}")
                
            finally:
                self.process_queue.task_done()
                self.current_package = None
                
        # Kuyruk tamamlandı
        self.is_queue_running = False
        
        # Butonları reset et
        GLib.idle_add(self.window.queue_button.set_sensitive, True)
        GLib.idle_add(self.window.start_queue_button.set_sensitive, False)
        GLib.idle_add(self.window.clear_queue_button.set_sensitive, False)
        GLib.idle_add(self.window.update_terminal_output, "✅ Kuyruk tamamlandı")

    def _remove_from_store(self, package_name):
        """UI listesinden paketi kaldır"""
        iter = self.queue_store.get_iter_first()
        while iter:
            if self.queue_store[iter][0] == package_name:
                self.queue_store.remove(iter)
                break
            iter = self.queue_store.iter_next(iter)
        self.update_status()

    def update_status(self):
        """Durum bilgisini güncelle"""
        count = len(self.queue_store)
        status = "Kuyrukta {} araç var".format(count) if count > 0 else "Kuyruk boş"
        GLib.idle_add(self.window.status_label.set_text, status)
