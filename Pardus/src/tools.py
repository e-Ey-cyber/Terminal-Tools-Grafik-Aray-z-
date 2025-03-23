import json
import os
import subprocess
from src.utils.network import NetworkUtils  # Absolute import
from src.utils.system import SystemMonitor  # Absolute import

class ToolManager:
    def __init__(self):
        # İkon URL'lerini ilk önce tanımla 
        self.icon_urls = {
            "htop": "https://raw.githubusercontent.com/htop-dev/htop/main/htop.png",
            "neofetch": "https://raw.githubusercontent.com/dylanaraps/neofetch/master/neofetch.png",
            # ...existing code...
        }

        # Araçları daha sonra tanımla
        self.tools = {
            "htop": self._create_tool("htop", "Gelişmiş sistem izleme aracı", "Sistem İzleme"),
            "neofetch": self._create_tool("Neofetch", "Sistem bilgilerini gösteren komut satırı aracı", "Sistem Bilgisi"),
            # ...existing tools...
            
            # Yeni araçlar
            "nmon": self._create_tool("Nmon", "Sistem performans monitörü", "Sistem İzleme", "nmon"),
            "iotop": self._create_tool("IOtop", "I/O izleme aracı", "Sistem İzleme", "iotop"),
            "ncdu": self._create_tool("NCurses Disk Usage", "Disk kullanım analizi", "Sistem İzleme", "ncdu"),
            "btop": self._create_tool("Btop++", "Gelişmiş sistem monitörü", "Sistem İzleme", "btop"),
            "glances": self._create_tool("Glances", "Sistem izleme aracı", "Sistem İzleme", "glances"),
            
            # Ağ araçları
            "iftop": self._create_tool("Iftop", "Ağ bant genişliği izleme aracı", "Ağ Araçları", "iftop"),
            "aircrack-ng": self._create_tool("Aircrack-ng", "Kablosuz ağ güvenliği aracı", "Güvenlik Araçları", "aircrack-ng"),
            "tcpdump": self._create_tool("Tcpdump", "Ağ trafiği analiz aracı", "Ağ Araçları", "tcpdump"),
            "nmap": self._create_tool("Nmap", "Ağ keşif ve güvenlik tarayıcı", "Ağ Araçları", "nmap"),
            "wireshark": self._create_tool("Wireshark", "Ağ protokol analiz aracı", "Güvenlik Araçları", "wireshark"),
            "curl": self._create_tool("Curl", "Veri transfer aracı", "Ağ Araçları", "curl"),
            "wget": self._create_tool("Wget", "Web'den veri indirme aracı", "Ağ Araçları", "wget"),
            "ping": self._create_tool("Ping", "Ağ bağlantısını test etme aracı", "Ağ Araçları", "ping"),
            "traceroute": self._create_tool("Traceroute", "Ağ yolu izleme aracı", "Ağ Araçları", "traceroute"),
            "iperf": self._create_tool("Iperf", "Ağ performans testi aracı", "Ağ Araçları", "iperf"),
            "netstat": self._create_tool("Netstat", "Ağ bağlantılarını görüntüleme aracı", "Ağ Araçları", "netstat"),
            "airgeddon": self._create_tool("Airgeddon", "Kablosuz ağ güvenliği aracı", "Güvenlik Araçları", "airgeddon"),

            # Güvenlik araçları
            "ufw": self._create_tool("UFW", "Basit güvenlik duvarı aracı", "Güvenlik Araçları", "ufw"),
            "clamtk": self._create_tool("ClamTk", "Antivirüs tarayıcı", "Güvenlik Araçları", "clamtk"),
            "rkhunter": self._create_tool("RKHunter", "Rootkit tarayıcı", "Güvenlik Araçları", "rkhunter"),            
            "burpsuite": self._create_tool("Burp Suite", "Web uygulama güvenliği test aracı", "Güvenlik Araçları", "burpsuite"),
            "kali-linux": self._create_tool("Kali Linux", "Penetrasyon testi dağıtımı", "Güvenlik Araçları", "kali-linux"),
            "metasploit": self._create_tool("Metasploit", "Güvenlik açığı testi aracı", "Güvenlik Araçları", "metasploit"),
            "nikto": self._create_tool("Nikto", "Web sunucu tarayıcı", "Güvenlik Araçları", "nikto"),
            

            # Şifreleme araçları (saldırısı)
            "john": self._create_tool("John the Ripper", "Şifre kırıcı", "Şifreleme", "john"),
            "hashcat": self._create_tool("Hashcat", "Şifre kırma aracı", "Şifreleme", "hashcat"),
            "crunch": self._create_tool("Crunch", "Şifre listesi oluşturucu", "Şifreleme", "crunch"),
            "cewl": self._create_tool("Cewl", "Web sayfasından kelime listesi oluşturucu", "Şifreleme", "cewl"),
            "chntpw": self._create_tool("CHNTpw", "Windows şifre sıfırlama aracı", "Şifreleme", "chntpw"),
            "hashcat": self._create_tool("Hashcat", "Şifre kırma aracı", "Şİfreleme", "hashcat"),
            "medusa": self._create_tool("Medusa", "Parola kırma aracı", "Şifreleme", "medusa"),
            "wordlist": self._create_tool("Wordlist", "Parola listesi oluşturucu", "Şifreleme", "wordlist"),


            # Veritabanı araçları
            "mycli": self._create_tool("MyCLI", "MySQL/MariaDB terminal arayüzü", "Veritabanı", "mycli"),
            "pgcli": self._create_tool("PgCLI", "PostgreSQL terminal arayüzü", "Veritabanı", "pgcli"),
            "sqlmap": self._create_tool("SQLMap", "SQL enjeksiyon testi aracı", "Veritabanı", "sqlmap"),
            "burpsuite": self._create_tool("Burp Suite", "Web uygulama güvenliği aracı", "Veritabanı", "burpsuite"),            
            "sqlitebrowser": self._create_tool("SQLite Browser", "SQLite veritabanı tarayıcı", "Veritabanı", "sqlitebrowser"),
            "litecli": self._create_tool("LiteCLI", "SQLite terminal arayüzü", "Veritabanı", "litecli"),

            # Yeni araçlar
            "docker": {
                "name": "Docker",
                "package": "docker.io",
                "category": "development",
                "description": "Container yönetim platformu"
            },
            "kubernetes-cli": {
                "name": "Kubernetes CLI",
                "package": "kubectl",
                "category": "development",
                "description": "Kubernetes komut satırı aracı"
            },
            "nginx": {
                "name": "Nginx",
                "package": "nginx",
                "category": "network",
                "description": "Yüksek performanslı web sunucusu"
            },
            "postgresql": {
                "name": "PostgreSQL",
                "package": "postgresql",
                "category": "development",
                "description": "Gelişmiş açık kaynak veritabanı"
            }
        }

        self.tools.update({
            # Sistem araçları
            "bashtop": self._create_tool("Bashtop", "Terminal tabanlı sistem monitörü", "Sistem İzleme", "bashtop"),
            "gotop": self._create_tool("Gotop", "Terminal sistem monitörü", "Sistem İzleme", "gotop"),
            "byobu": self._create_tool("Byobu", "Terminal multiplexer", "Terminal Araçları", "byobu"),
            "tmux": self._create_tool("Tmux", "Terminal oturum yöneticisi", "Terminal Araçları", "tmux"),
            "beef-xss": self._create_tool("Beef XSS", "Web uygulama güvenliği aracı", "Sistem Servisi", "beef-xss"),
    
            # Ağ araçları
            "netcat": self._create_tool("Netcat", "Ağ bağlantı aracı", "Ağ Araçları", "netcat"),
            "mtr": self._create_tool("MTR", "Ağ tanılama aracı", "Ağ Araçları", "mtr"),
            "nethogs": self._create_tool("NetHogs", "Ağ trafiği izleme", "Ağ Araçları", "nethogs"),
            "speedtest-cli": self._create_tool("Speedtest CLI", "İnternet hız testi", "Ağ Araçları", "speedtest-cli"),
            
            # Güvenlik araçları
            "clamav": self._create_tool("ClamAV", "Antivirüs tarayıcı", "Güvenlik Araçları", "clamav"),
            "rkhunter": self._create_tool("RKHunter", "Rootkit tarayıcı", "Güvenlik Araçları", "rkhunter"),
            "chkrootkit": self._create_tool("Chkrootkit", "Rootkit tespit aracı", "Güvenlik Araçları", "chkrootkit"),
            "lynis": self._create_tool("Lynis", "Güvenlik denetim aracı", "Güvenlik Araçları", "lynis"),
            
            # Geliştirici araçları
            "git": self._create_tool("Git", "Versiyon kontrol sistemi", "Geliştirici Araçları", "git"),
            "vim": self._create_tool("Vim", "Metin editörü", "Geliştirici Araçları", "vim"),
            "nodejs": self._create_tool("Node.js", "JavaScript runtime", "Geliştirici Araçları", "nodejs"),
            "python3-pip": self._create_tool("Python PIP", "Python paket yöneticisi", "Geliştirici Araçları", "python3-pip"),
            
            # Multimedya araçları
            "ffmpeg": self._create_tool("FFmpeg", "Multimedya dönüştürücü", "Multimedya", "ffmpeg"),
            "vlc": self._create_tool("VLC", "Medya oynatıcı", "Multimedya", "vlc"),
            "audacity": self._create_tool("Audacity", "Ses düzenleyici", "Multimedya", "audacity"),
            "obs-studio": self._create_tool("OBS Studio", "Ekran kaydedici", "Multimedya", "obs-studio")
        })

        self.tools.update({
            # IDE & Editörler
            "vscodium": self._create_tool("VSCodium", "Özgür VS Code", "development/ide"),
            "sublime-text": self._create_tool("Sublime Text", "Hızlı metin editörü", "development/ide"),
            "atom": self._create_tool("Atom", "GitHub'ın metin editörü", "development/ide"),
            
            # Programlama Dilleri
            "go": self._create_tool("Go Lang", "Google'ın programlama dili", "development/lang"),
            "rust": self._create_tool("Rust", "Sistem programlama dili", "development/lang"),
            "kotlin": self._create_tool("Kotlin", "Modern JVM dili", "development/lang"),
            
            # Multimedya İşleme
            "kdenlive": self._create_tool("Kdenlive", "Video düzenleme", "multimedia/video"),
            "blender": self._create_tool("Blender", "3D modelleme", "multimedia/graphics"),
            "obs-studio": self._create_tool("OBS Studio", "Ekran kaydı", "multimedia/streaming"),
            
            # Güvenlik Araçları
            "wifite": self._create_tool("Wifite", "Kablosuz ağ testi", "security/pentest"),
            "foremost": self._create_tool("Foremost", "Veri kurtarma", "security/forensic"),
            "ghidra": self._create_tool("Ghidra", "Tersine mühendislik", "security/forensic"),
            
            # Sanallaştırma
            "virtualbox": self._create_tool("VirtualBox", "Sanallaştırma platformu", "system/virtualization"),
            "vagrant": self._create_tool("Vagrant", "Geliştirme ortamları", "system/virtualization"),
            "docker-compose": self._create_tool("Docker Compose", "Container orkestrasyon", "system/virtualization"),
            
            # Terminal Araçları
            "terminator": self._create_tool("Terminator", "Gelişmiş terminal", "system/terminal"),
            "zsh": self._create_tool("Zsh", "Z shell", "system/terminal"),
            "ranger": self._create_tool("Ranger", "Terminal dosya yöneticisi", "system/terminal")
        })

        # İkon URL'lerini güncelle
        self.icon_urls.update({
            "nmon": "https://example.com/nmon.png",
            "iftop": "https://example.com/iftop.png",
            "aircrack-ng": "https://example.com/aircrack-ng.png",
            "tcpdump": "https://example.com/tcpdump.png",
            "nmap": "https://example.com/nmap.png",
            "wireshark": "https://example.com/wireshark.png",
            "curl": "https://example.com/curl.png",
            "wget": "https://example.com/wget.png",
            "ping": "https://example.com/ping.png",
            "traceroute": "https://example.com/traceroute.png",
            "iperf": "https://example.com/iperf.png",
            "netstat": "https://example.com/netstat.png",
            "airgeddon": "https://example.com/airgeddon.png",
            "sqlmap": "https://example.com/sqlmap.png",
            "burpsuite": "https://example.com/burpsuite.png",
            "kali-linux": "https://example.com/kali-linux.png",
            "metasploit": "https://example.com/metasploit.png",
            "sqlmap": "https://example.com/sqlmap.png",
            "burpsuite": "https://example.com/burpsuite.png",
            "kali-linux": "https://example.com/kali-linux.png",
            "metasploit": "https://example.com/metasploit.png",
            "htop": "https://example.com/htop.png",
            "neofetch": "https://example.com/neofetch.png",
            "iftop": "https://example.com/iftop.png",
            "iotop": "https://example.com/iotop.png",
            "ncdu": "https://example.com/ncdu.png",
            "btop": "https://example.com/btop.png",
            "glances": "https://example.com/glances.png",
            "nikto": "https://example.com/nikto.png",
            "hashcat": "https://example.com/hashcat.png",
            "john": "https://example.com/john.png",
            "mycli": "https://example.com/mycli.png",
            "pgcli": "https://example.com/pgcli.png",
            "litecli": "https://example.com/litecli.png",
            "vscodium": "https://example.com/vscodium.png",
            "sublime-text": "https://example.com/sublime.png",
            # ...diğer yeni ikonlar...
        })

        self.queue = []  # Kurulum kuyruğu
        self.network = NetworkUtils()
        self.system = SystemMonitor()

    def _create_tool(self, name, description, category, package=None, emoji=None):
        """Tool nesnesi oluştur"""
        if package is None:
            package = name.lower()
        
        if emoji is None:
            # Kategori bazlı varsayılan emoji
            emoji_map = {
                "Sistem İzleme": "📊",
                "Ağ Araçları": "🌐",
                "Güvenlik": "🔒",
                "Geliştirme": "💻",
                "Terminal": "⌨️",
                "Veritabanı": "🗃️"
            }
            emoji = emoji_map.get(category, "🔧")
            
        return {
            "name": f"{emoji} {name}",
            "description": description,
            "category": category,
            "package": package,
            "icon": f"{package}.png"
        }
    
    def get_tools(self):
        """Tüm araçları döndür"""
        return self.tools.copy()  # Güvenli kopya döndür
    
    def get_categories(self):
        """Tüm kategorileri döndür"""
        categories = set()
        for tool in self.tools.values():
            categories.add(tool["category"])
        return sorted(list(categories))
    
    def get_tools_by_category(self, category):
        """Kategoriye göre araçları filtrele"""
        return {k: v for k, v in self.tools.items() 
                if v["category"] == category}
    
    def search_tools(self, query):
        """Araçlarda arama yap"""
        query = query.lower()
        return {k: v for k, v in self.tools.items() 
                if query in v["name"].lower() or 
                   query in v["description"].lower() or
                   query in v["category"].lower()}
    
    def save_to_file(self, filepath):
        """Araçları JSON dosyasına kaydet"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.tools, f, indent=4, ensure_ascii=False)
    
    def load_from_file(self, filepath):
        """Araçları JSON dosyasından yükle"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.tools = json.load(f)

    def add_tool(self, tool_id, name, description, category, package=None, icon_url=None):
        """Yeni araç ekle"""
        self.tools[tool_id] = self._create_tool(name, description, category, package)
        if icon_url:
            self.icon_urls[tool_id] = icon_url

    def get_icon_urls(self):
        """İkon URL'lerini döndür"""
        return self.icon_urls

    def add_to_queue(self, tool_id):
        """Aracı kuyruğa ekle"""
        if tool_id not in self.queue and tool_id in self.tools:
            self.queue.append(tool_id)
            return True
        return False
        
    def remove_from_queue(self, tool_id):
        """Aracı kuyruktan kaldır"""
        if tool_id in self.queue:
            self.queue.remove(tool_id)
            return True
        return False
            
    def get_queue(self):
        """Kurulum kuyruğunu getir"""
        return [(tid, self.tools[tid]) for tid in self.queue]

    def install_package(self, package_name):
        """Install a package with checks"""
        if not self.system.check_root():
            raise PermissionError("Root privileges required")
            
        if not self.network.check_connection():
            raise ConnectionError("No internet connection")
            
        # ...existing code...

    def get_package_info(self, package_name):
        """Get detailed package information"""
        try:
            output = subprocess.check_output(['apt-cache', 'show', package_name])
            info = {}
            current_field = None
            current_value = []
            
            for line in output.decode().split('\n'):
                if line.startswith(' '):  # Devam eden satır
                    current_value.append(line.strip())
                elif line:  # Yeni alan
                    if current_field:  # Önceki alanı kaydet
                        info[current_field] = '\n'.join(current_value)
                    if ':' in line:
                        current_field = line.split(':', 1)[0]
                        current_value = [line.split(':', 1)[1].strip()]
                        
            if current_field:  # Son alanı kaydet
                info[current_field] = '\n'.join(current_value)
                
            # Emoji ve formatlamalar ekle
            formatted_info = {
                "📦 Paket": info.get("Package", ""),
                "📝 Açıklama": info.get("Description", ""),
                "🔄 Versiyon": info.get("Version", ""),
                "💾 Boyut": self._format_size(info.get("Size", "0")),
                "👤 Geliştirici": info.get("Maintainer", ""),
                "🔗 Web Sitesi": info.get("Homepage", ""),
                "📥 İndirme Boyutu": self._format_size(info.get("Download-Size", "0")),
                "📚 Bağımlılıklar": info.get("Depends", "").replace(",", "\n"),
                "🏷️ Bölüm": info.get("Section", ""),
                "💫 Öncelik": info.get("Priority", "")
            }
            return formatted_info
        except subprocess.CalledProcessError:
            return None
            
    def _format_size(self, size_str):
        """Format byte size to human readable"""
        try:
            size = int(size_str)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Bilinmiyor"

class PackageManager:
    def __init__(self):
        self.packages = {
            "Development": {
                "VSCode": {
                    "name": "📝 Visual Studio Code",
                    "package": "code",
                    "description": "Güçlü kod editörü",
                    "icon": "vscode",
                    "category": "development"
                },
                "PyCharm": {
                    "name": "🐍 PyCharm Community",
                    "package": "pycharm-community",
                    "description": "Python IDE",
                    "icon": "pycharm",
                    "category": "development"
                },
                "Git": {
                    "name": "🌿 Git",
                    "package": "git",
                    "description": "Versiyon kontrol sistemi",
                    "icon": "git",
                    "category": "development"
                }
            },
            "Internet": {
                "Chrome": {
                    "name": "🌐 Google Chrome",
                    "package": "google-chrome-stable",
                    "description": "Google'ın web tarayıcısı",
                    "icon": "chrome",
                    "category": "internet"
                },
                "Firefox": {
                    "name": "🦊 Firefox",
                    "package": "firefox",
                    "description": "Mozilla web tarayıcısı",
                    "icon": "firefox",
                    "category": "internet"
                }
            },
            "Multimedia": {
                "VLC": {
                    "name": "🎥 VLC",
                    "package": "vlc",
                    "description": "Medya oynatıcı",
                    "icon": "vlc",
                    "category": "multimedia"
                },
                "GIMP": {
                    "name": "🎨 GIMP",
                    "package": "gimp",
                    "description": "Görüntü düzenleyici",
                    "icon": "gimp",
                    "category": "multimedia"
                }
            },
            "System": {
                "Stacer": {
                    "name": "🔧 Stacer",
                    "package": "stacer",
                    "description": "Sistem optimizasyon aracı",
                    "icon": "stacer",
                    "category": "system"
                },
                "Timeshift": {
                    "name": "⏰ Timeshift",
                    "package": "timeshift",
                    "description": "Sistem yedekleme aracı",
                    "icon": "timeshift",
                    "category": "system"
                }
            }
        }
        self.user_packages = []

    def add_custom_package(self, name, package, category, description=""):
        """Kullanıcının özel paket eklemesi"""
        if category not in self.packages:
            self.packages[category] = {}
            
        self.packages[category][name] = {
            "name": f"📦 {name}",
            "package": package,
            "description": description,
            "icon": "package",
            "category": category.lower(),
            "custom": True
        }
        self.user_packages.append(name)
        return True

    def remove_custom_package(self, name, category):
        """Kullanıcının eklediği paketi kaldırma"""
        if category in self.packages and name in self.packages[category]:
            if name in self.user_packages:
                del self.packages[category][name]
                self.user_packages.remove(name)
                return True
        return False

    def get_packages_by_category(self, category):
        """Kategoriye göre paketleri getir"""
        return self.packages.get(category, {})

    def search_packages(self, query):
        """Paket arama"""
        results = {}
        query = query.lower()
        
        for category, packages in self.packages.items():
            for name, info in packages.items():
                if (query in name.lower() or 
                    query in info["description"].lower()):
                    if category not in results:
                        results[category] = {}
                    results[category][name] = info
                    
        return results

"""
Created by Eyyüp Efe Adıgüzel
Contact: eyupadiguzel20@gmail.com
"""
