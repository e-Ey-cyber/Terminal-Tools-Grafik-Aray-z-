import json
import os

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
            "sqlmap" : self._create_tool("SQLMap", "SQL enjeksiyon testi aracı", "Güvenlik Araçları", "sqlmap"),
            "burpsuite": self._create_tool("Burp Suite", "Web uygulama güvenliği test aracı", "Güvenlik Araçları", "burpsuite"),
            "kali-linux": self._create_tool("Kali Linux", "Penetrasyon testi dağıtımı", "Güvenlik Araçları", "kali-linux"),
            "metasploit": self._create_tool("Metasploit", "Güvenlik açığı testi aracı", "Güvenlik Araçları", "metasploit"),
            "nikto": self._create_tool("Nikto", "Web sunucu tarayıcı", "Güvenlik Araçları", "nikto"),
            "hashcat": self._create_tool("Hashcat", "Şifre kırma aracı", "Güvenlik Araçları", "hashcat"),
            "john": self._create_tool("John the Ripper", "Şifre kırıcı", "Güvenlik Araçları", "john"),
            
            # Veritabanı araçları
            "mycli": self._create_tool("MyCLI", "MySQL/MariaDB terminal arayüzü", "Veritabanı", "mycli"),
            "pgcli": self._create_tool("PgCLI", "PostgreSQL terminal arayüzü", "Veritabanı", "pgcli"),
            "litecli": self._create_tool("LiteCLI", "SQLite terminal arayüzü", "Veritabanı", "litecli")
        }

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
            "litecli": "https://example.com/litecli.png"
        })

    def _create_tool(self, name, description, category, package=None):
        """Tool nesnesi oluştur"""
        if package is None:
            package = name.lower()
            
        return {
            "name": name,
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
