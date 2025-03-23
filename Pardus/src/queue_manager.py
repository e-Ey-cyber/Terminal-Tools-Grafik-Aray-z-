from gi.repository import Gtk, GLib

class QueueManager:
    def __init__(self, window):
        self.window = window
        self.queue_store = Gtk.ListStore(str, str)  # package_name, display_name
        self.is_running = False
        
        # Create queue view
        self.queue_view = Gtk.TreeView(model=self.queue_store)
        self.queue_view.set_headers_visible(False)
        
        column = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)
        self.queue_view.append_column(column)

    def add_to_queue(self, package_name, display_name=None):
        """Add package to installation queue"""
        if not display_name:
            display_name = package_name
            
        self.queue_store.append([package_name, display_name])
        self.window.update_terminal_output(f"{display_name} indirme kuyruğuna eklendi.")
        self.update_status()

    def start_queue(self):
        """Start processing the installation queue"""
        if self.window.is_installing:
            return
            
        if len(self.queue_store) == 0:
            self.window.update_terminal_output("Kuyruk boş!")
            return
            
        self.is_running = True
        self.window.update_terminal_output("İndirme kuyruğu başlatıldı.")
        self.process_next()

    def process_next(self):
        """Process next package in queue"""
        if self.window.is_installing:
            return
            
        iter = self.queue_store.get_iter_first()
        if iter:
            package_name = self.queue_store[iter][0]
            display_name = self.queue_store[iter][1]
            self.window.install_package(package_name, display_name)
            self.queue_store.remove(iter)
            self.update_status()
            
        elif self.is_running:
            self.is_running = False
            self.window.update_terminal_output("Kuyruk tamamlandı.")

    def clear_queue(self):
        """Clear installation queue"""
        self.queue_store.clear()
        self.is_running = False
        self.window.update_terminal_output("İndirme kuyruğu temizlendi.")
        self.update_status()
        
    def update_status(self):
        """Update queue status in UI"""
        count = len(self.queue_store)
        if count == 0:
            status = "Kuyruk boş"
        else:
            status = f"Kuyrukta {count} araç var"
            
        GLib.idle_add(self.window.status_label.set_text, status)
