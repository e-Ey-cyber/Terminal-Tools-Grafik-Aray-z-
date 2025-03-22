#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import requests
import tempfile
from setuptools import setup, find_packages

# Sabit dizin tanımlamaları
SHARE_DIR = "/usr/share/pardus/toolsget"
ICON_DIR = os.path.join(SHARE_DIR, "icons")
CONFIG_DIR = "/etc/pardus/toolsget"
LOG_DIR = "/var/log/toolsget"

def install_dependencies():
    """Sistem bağımlılıklarını yükle"""
    dependencies = [
        "python3-tk",
        "python3-pil",
        "python3-pil.imagetk",
        "python3-requests",
        "fonts-dejavu",
        "python3-apt",
        "policykit-1"
    ]
    
    print("\n[*] Sistem bağımlılıkları yükleniyor...")
    try:
        subprocess.run(["apt-get", "install", "-y"] + dependencies, check=True)
        print("✓ Sistem bağımlılıkları yüklendi")
    except Exception as e:
        print(f"✗ Hata: {e}")
        sys.exit(1)

def setup_directories():
    """Gerekli dizinleri oluştur"""
    dirs = [SHARE_DIR, ICON_DIR, CONFIG_DIR, LOG_DIR]
    
    print("\n[*] Sistem dizinleri oluşturuluyor...")
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            # Dizin izinlerini ayarla
            os.chmod(d, 0o755)
            print(f"✓ {d} oluşturuldu")
        except Exception as e:
            print(f"✗ {d} oluşturulamadı: {e}")

def download_icons():
    """İkon dosyalarını indir"""
    from tools import ToolManager
    tool_manager = ToolManager()
    icon_urls = tool_manager.get_icon_urls()
    
    print("\n[*] İkonlar indiriliyor...")
    for tool_id, url in icon_urls.items():
        icon_path = os.path.join(ICON_DIR, f"{tool_id}.png")
        
        if not os.path.exists(icon_path):
            try:
                response = requests.get(url, stream=True, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"✓ {tool_id} ikonu indirildi")
                else:
                    print(f"✗ {tool_id} ikonu indirilemedi (HTTP {response.status_code})")
            except Exception as e:
                print(f"✗ {tool_id} ikonu indirilemedi: {e}")

def create_config():
    """Yapılandırma dosyasını oluştur"""
    config = {
        "icon_dir": ICON_DIR,
        "log_file": os.path.join(LOG_DIR, "toolsget.log"),
        "theme": "default",
        "update_interval": 3600,
        "notification": True
    }
    
    config_file = os.path.join(CONFIG_DIR, "toolsget.conf")
    print("\n[*] Yapılandırma dosyası oluşturuluyor...")
    
    try:
        with open(config_file, "w") as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print(f"✓ {config_file} oluşturuldu")
    except Exception as e:
        print(f"✗ Yapılandırma dosyası oluşturulamadı: {e}")

def install_polkit():
    """Polkit kurallarını yükle"""
    policy_file = "tr.org.pardus.toolsget.policy"
    dest_dir = "/usr/share/polkit-1/actions"
    
    print("\n[*] Polkit kuralları yükleniyor...")
    try:
        shutil.copy2(policy_file, os.path.join(dest_dir, policy_file))
        print("✓ Polkit kuralları yüklendi")
    except Exception as e:
        print(f"✗ Polkit kuralları yüklenemedi: {e}")

def post_install():
    """Kurulum sonrası işlemler"""
    # İzinleri ayarla
    subprocess.run(["chmod", "+x", "/usr/bin/toolsget"])
    
    # Desktop dosyasını yükle
    shutil.copy2("tr.org.pardus.toolsget.desktop", 
                 "/usr/share/applications/")
    
    print("""
Kurulum tamamlandı!

Programı başlatmak için:
    toolsget

Günlük dosyası:
    /var/log/toolsget/toolsget.log
    
Yapılandırma dosyası:
    /etc/pardus/toolsget/toolsget.conf
""")

def download_program():
    """Program kaynak kodunu indir"""
    print("\n[*] Program aranıyor...")
    
    try:
        # Önce yerel dizinde toolsget.zip dosyası var mı kontrol et
        if os.path.exists("toolsget.zip"):
            print("✓ toolsget.zip yerel dizinde bulundu")
            return
            
        # GitHub releases sayfasından en son sürümü al
        repos = [
            "https://github.com/pardus/toolsget/archive/refs/tags/v1.0.0.zip",
            "https://sourceforge.net/projects/toolsget/files/latest/download",
            "https://gitlab.com/pardus/toolsget/-/archive/main/toolsget-main.zip"
        ]
        
        for repo_url in repos:
            try:
                print(f"\nDeneniyor: {repo_url}")
                response = requests.get(repo_url, stream=True, timeout=10)
                if response.status_code == 200:
                    print("✓ Bağlantı başarılı, indiriliyor...")
                    
                    with open("toolsget.zip", 'wb') as f:
                        total_size = int(response.headers.get('content-length', 0))
                        block_size = 8192
                        downloaded = 0
                        
                        for chunk in response.iter_content(block_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size:
                                percent = int((downloaded/total_size) * 100)
                                sys.stdout.write(f"\rİndiriliyor: %{percent}")
                                sys.stdout.flush()
                                
                    print("\n✓ toolsget.zip başarıyla indirildi")
                    return
                    
            except Exception as e:
                print(f"! Bu kaynaktan indirilemedi: {e}")
                continue
                
        print("\n✗ Hiçbir kaynaktan indirilemedi!")
        print("\nLütfen toolsget.zip dosyasını manuel olarak indirip")
        print("setup.py ile aynı dizine kopyalayın:")
        print("https://github.com/pardus/toolsget/releases")
        sys.exit(1)
        
    except Exception as e:
        print(f"✗ Beklenmeyen hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Bu betiğin root olarak çalıştırılması gerekiyor!")
        sys.exit(1)

    # Önce programı indir
    download_program()
        
    if "install" in sys.argv:
        install_dependencies()
        setup_directories()
        download_icons()
        create_config()
        install_polkit()
    
    # Python paketini kur
    setup(
        name="toolsget",
        version="1.0.0",
        packages=find_packages(),
        scripts=["toolsget"],
        install_requires=[
            "Pillow>=9.0.0",
            "requests>=2.25.0"
        ],
        data_files=[
            ("/usr/bin", ["toolsget"]),
            (CONFIG_DIR, ["toolsget.conf"]),
            ("/usr/share/applications", ["tr.org.pardus.toolsget.desktop"]),
            ("/usr/share/polkit-1/actions", ["tr.org.pardus.toolsget.policy"]),
        ],
        author="Eyüp Adıgüzel",
        author_email="eyupadiguzel20@gmail.com",
        description="Terminal araçları yönetim arayüzü",
        license="GPL-3.0",
        keywords="package manager, terminal tools",
        url="https://www.pardus.org.tr",
    )
    
    if "install" in sys.argv:
        post_install()