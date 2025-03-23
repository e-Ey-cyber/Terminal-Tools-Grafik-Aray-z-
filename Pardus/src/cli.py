import argparse
import sys
import logging
from src.tools import ToolManager  # Absolute import
from src.config import APP_NAME, APP_VERSION  # Absolute import

class ToolsGetCLI:
    def __init__(self):
        self.tool_manager = ToolManager()
        self.parser = self.create_parser()

    def create_parser(self):
        """Komut satırı argümanlarını oluştur"""
        parser = argparse.ArgumentParser(
            description=f"{APP_NAME} - Terminal Araçları Yöneticisi",
            usage='''toolsget <komut> [parametreler]

Komutlar:
  search      Paket ara
  install     Paket yükle
  remove      Paket kaldır
  list        Paketleri listele
  info        Paket bilgisi göster
  update      Paket listesini güncelle
  category    Kategoriye göre paketleri listele
  queue       Kuyruk işlemleri
  theme       Tema ayarları
  config      Ayarlar
  system      Sistem işlemleri
  maintain    Sistem bakımı
  security    Güvenlik kontrolleri
''')
        parser.add_argument('--version', action='version', 
                          version=f'%(prog)s {APP_VERSION}')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='Detaylı çıktı göster')

        subparsers = parser.add_subparsers(dest='command')

        # search komutu
        search_parser = subparsers.add_parser('search', help='Paket ara')
        search_parser.add_argument('query', help='Arama terimi')
        search_parser.add_argument('--category', help='Kategori filtresi')
        search_parser.add_argument('--sort', choices=['name', 'size', 'date'],
                                 help='Sıralama kriteri')
        search_parser.add_argument('--reverse', action='store_true',
                                 help='Ters sıralama')

        # install komutu
        install_parser = subparsers.add_parser('install', help='Paket yükle')
        install_parser.add_argument('packages', nargs='+', help='Yüklenecek paketler')
        install_parser.add_argument('-y', '--yes', action='store_true',
                                  help='Onay sorma')
        install_parser.add_argument('--file', help='Paket listesi dosyası')
        install_parser.add_argument('--download-only', action='store_true',
                                  help='Sadece indir')
        install_parser.add_argument('--no-deps', action='store_true',
                                  help='Bağımlılıkları kurma')

        # remove komutu  
        remove_parser = subparsers.add_parser('remove', help='Paket kaldır')
        remove_parser.add_argument('packages', nargs='+', help='Kaldırılacak paketler')
        remove_parser.add_argument('-y', '--yes', action='store_true',
                                 help='Onay sorma')

        # list komutu
        list_parser = subparsers.add_parser('list', help='Paketleri listele')
        list_parser.add_argument('--installed', action='store_true',
                               help='Sadece yüklü paketleri göster')

        # info komutu
        info_parser = subparsers.add_parser('info', help='Paket bilgisi göster')
        info_parser.add_argument('package', help='Bilgisi gösterilecek paket')

        # category komutu
        category_parser = subparsers.add_parser('category', 
                                              help='Kategoriye göre paketleri listele')
        category_parser.add_argument('category', help='Kategori adı')

        # queue komutu
        queue_parser = subparsers.add_parser('queue', help='Kuyruk işlemleri')
        queue_parser.add_argument('action', choices=['add', 'remove', 'clear', 'list', 'start'],
                                help='Kuyruk işlemi')
        queue_parser.add_argument('packages', nargs='*', help='İşlem yapılacak paketler')

        # Yeni tema komutu
        theme_parser = subparsers.add_parser('theme', help='Tema ayarları')
        theme_parser.add_argument('action', choices=['set', 'list', 'create', 'export'],
                                help='Tema işlemi')
        theme_parser.add_argument('name', nargs='?', help='Tema adı')
        theme_parser.add_argument('--colors', help='Tema renkleri (JSON formatında)')

        # Yeni ayarlar komutu
        config_parser = subparsers.add_parser('config', help='Ayarlar')
        config_parser.add_argument('action', choices=['get', 'set', 'list'],
                                 help='Ayar işlemi')
        config_parser.add_argument('key', nargs='?', help='Ayar anahtarı')
        config_parser.add_argument('value', nargs='?', help='Ayar değeri')

        # Yeni sistem komutları
        system_parser = subparsers.add_parser('system', help='Sistem işlemleri')
        system_parser.add_argument('action', 
                                 choices=['info', 'services', 'resources', 'network'],
                                 help='Sistem işlem türü')
        
        # Yeni bakım komutları
        maintain_parser = subparsers.add_parser('maintain', help='Sistem bakımı')
        maintain_parser.add_argument('action',
                                   choices=['clean', 'backup', 'repair', 'optimize'],
                                   help='Bakım işlemi')

        # Yeni güvenlik komutları
        security_parser = subparsers.add_parser('security', help='Güvenlik kontrolleri')
        security_parser.add_argument('action',
                                   choices=['scan', 'update', 'harden'],
                                   help='Güvenlik işlemi')

        return parser

    def run(self, args=None):
        """Ana çalıştırma metodu"""
        if args is None:
            args = self.parser.parse_args()
        else:
            args = self.parser.parse_args(args)

        # Verbose mod için log seviyesini ayarla
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        # Komutları işle
        try:
            if args.command == 'search':
                return self.search(args.query)
            elif args.command == 'install':
                return self.install(args.packages, args.yes)
            elif args.command == 'remove':
                return self.remove(args.packages, args.yes)
            elif args.command == 'list':
                return self.list_packages(args.installed)
            elif args.command == 'info':
                return self.show_info(args.package)
            elif args.command == 'category':
                return self.list_category(args.category)
            elif args.command == 'queue':
                return self.handle_queue(args.action, args.packages)
            elif args.command == 'theme':
                return self.handle_theme(args.action, args.name, args.colors)
            elif args.command == 'config':
                return self.handle_config(args.action, args.key, args.value)
            elif args.command == 'system':
                return self.handle_system(args.action)
            elif args.command == 'maintain':
                return self.handle_maintain(args.action)
            elif args.command == 'security':
                return self.handle_security(args.action)
            else:
                self.parser.print_help()
                return 1
        except Exception as e:
            logging.error(f"Hata: {e}")
            return 1

    def search(self, query):
        """Paket arama"""
        results = self.tool_manager.search_tools(query)
        if not results:
            print(f"'{query}' için sonuç bulunamadı.")
            return 1
            
        print(f"\nArama sonuçları: '{query}'")
        print("-" * 50)
        for tool_id, tool in results.items():
            print(f"{tool['name']:<30} - {tool['category']}")
            print(f"  {tool['description']}")
            print()
        return 0

    def install(self, packages, yes=False):
        """Paket yükleme"""
        for package in packages:
            if not yes:
                response = input(f"{package} paketi yüklensin mi? [E/h] ")
                if response.lower() not in ['', 'e', 'evet']:
                    continue
            print(f"Yükleniyor: {package}")
            # Yükleme işlemi burada yapılacak
        return 0

    def remove(self, packages, yes=False):
        """Paket kaldırma"""
        for package in packages:
            if not yes:
                response = input(f"{package} paketi kaldırılsın mı? [E/h] ")
                if response.lower() not in ['', 'e', 'evet']:
                    continue
            print(f"Kaldırılıyor: {package}")
            # Kaldırma işlemi burada yapılacak
        return 0

    def list_packages(self, installed=False):
        """Paketleri listele"""
        tools = self.tool_manager.get_tools()
        print("\nKullanılabilir Araçlar:")
        print("-" * 50)
        for tool_id, tool in tools.items():
            print(f"{tool['name']:<30} - {tool['category']}")
        return 0

    def show_info(self, package):
        """Paket bilgisi göster"""
        tools = self.tool_manager.get_tools()
        if package not in tools:
            print(f"Paket bulunamadı: {package}")
            return 1
            
        tool = tools[package]
        print(f"\nPaket Bilgisi: {tool['name']}")
        print("-" * 50)
        print(f"Açıklama: {tool['description']}")
        print(f"Kategori: {tool['category']}")
        print(f"Paket adı: {tool['package']}")
        return 0

    def list_category(self, category):
        """Kategoriye göre paketleri listele"""
        tools = self.tool_manager.get_tools_by_category(category)
        if not tools:
            print(f"'{category}' kategorisinde araç bulunamadı.")
            return 1
            
        print(f"\n{category} Kategorisindeki Araçlar:")
        print("-" * 50)
        for tool_id, tool in tools.items():
            print(f"{tool['name']:<30} - {tool['description']}")
        return 0

    def handle_queue(self, action, packages):
        """Kuyruk işlemlerini yönet"""
        if action == 'add':
            for package in packages:
                print(f"Kuyruğa eklendi: {package}")
        elif action == 'remove':
            for package in packages:
                print(f"Kuyruktan kaldırıldı: {package}")
        elif action == 'clear':
            print("Kuyruk temizlendi")
        elif action == 'list':
            print("\nKuyrukta Bekleyen Paketler:")
            print("-" * 50)
            # Kuyruk listesi burada gösterilecek
        elif action == 'start':
            print("Kuyruk işleme alındı")
        return 0

    # Yeni tema işlemleri
    def handle_theme(self, action, name=None, colors=None):
        """Tema işlemlerini yönet"""
        if action == 'list':
            themes = self.theme_manager.get_themes()
            print("\nKullanılabilir Temalar:")
            print("-" * 50)
            for theme_name, theme in themes.items():
                print(f"{theme_name:<20} - {theme['description']}")
        elif action == 'set':
            if not name:
                print("Tema adı gerekli")
                return 1
            if self.theme_manager.switch_theme(name):
                print(f"{name} teması uygulandı")
                return 0
            print(f"Tema bulunamadı: {name}")
            return 1
        elif action == 'create':
            if not name or not colors:
                print("Tema adı ve renkleri gerekli")
                return 1
            # Yeni tema oluştur
            return 0
        elif action == 'export':
            if not name:
                print("Tema adı gerekli")
                return 1
            # Temayı dışa aktar
            return 0

    # Yeni ayar işlemleri  
    def handle_config(self, action, key=None, value=None):
        """Ayar işlemlerini yönet"""
        if action == 'list':
            print("\nMevcut Ayarlar:")
            print("-" * 50)
            for k, v in self.config.items():
                print(f"{k:<30} = {v}")
        elif action == 'get':
            if not key:
                print("Ayar anahtarı gerekli")
                return 1
            value = self.config.get(key)
            if value is None:
                print(f"Ayar bulunamadı: {key}")
                return 1
            print(f"{key} = {value}")
        elif action == 'set':
            if not key or value is None:
                print("Ayar anahtarı ve değeri gerekli")
                return 1
            self.config[key] = value
            print(f"{key} = {value} olarak ayarlandı")

    def handle_system(self, action):
        """Sistem komutlarını işle"""
        if action == 'info':
            info = self.system_monitor.get_system_info()
            print("\nSistem Bilgileri:")
            for key, value in info.items():
                print(f"{key:15}: {value}")
        elif action == 'services':
            services = self.system_monitor.get_services_status()
            print("\nServis Durumları:")
            for service, status in services.items():
                print(f"{service:15}: {status}")
        elif action == 'resources':
            usage = self.system_monitor.get_resource_usage()
            print("\nKaynak Kullanımı:")
            for resource, stats in usage.items():
                print(f"\n{resource}:")
                for key, value in stats.items():
                    print(f"  {key:15}: {value}")
        elif action == 'network':
            net = self.network_utils.get_all_interfaces()
            print("\nAğ Arayüzleri:")
            for interface in net:
                info = self.network_utils.get_interface_info(interface)
                print(f"\n{interface}:")
                for key, value in info.items():
                    print(f"  {key:15}: {value}")

    def handle_maintain(self, action):
        """Bakım komutlarını işle"""
        if action == 'clean':
            print("Sistem temizleniyor...")
            # Temizleme işlemi burada yapılacak
        elif action == 'backup':
            print("Sistem yedekleniyor...")
            # Yedekleme işlemi burada yapılacak
        elif action == 'repair':
            print("Sistem onarılıyor...")
            # Onarım işlemi burada yapılacak
        elif action == 'optimize':
            print("Sistem optimize ediliyor...")
            # Optimizasyon işlemi burada yapılacak
        return 0

    def handle_security(self, action):
        """Güvenlik komutlarını işle"""
        if action == 'scan':
            print("Sistem taranıyor...")
            # Tarama işlemi burada yapılacak
        elif action == 'update':
            print("Güvenlik güncellemeleri yapılıyor...")
            # Güncelleme işlemi burada yapılacak
        elif action == 'harden':
            print("Sistem sertleştiriliyor...")
            # Sertleştirme işlemi burada yapılacak
        return 0

def main():
    """CLI giriş noktası"""
    cli = ToolsGetCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()
