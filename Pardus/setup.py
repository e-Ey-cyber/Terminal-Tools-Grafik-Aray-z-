#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import requests
import json
from setuptools import setup, find_packages

VERSION = "1.0.0"
APP_NAME = "Tools Get"

INSTALL_DIR = {
    'share': "/usr/share/pardus/toolsget",
    'config': "/etc/pardus/toolsget", 
    'bin': "/usr/bin",
    'icons': "/usr/share/icons/hicolor",
    'applications': "/usr/share/applications",
    'polkit': "/usr/share/polkit-1/actions",
    'themes': "/usr/share/pardus/toolsget/themes",
    'locale': "/usr/share/locale"
}

DEPENDENCIES = {
    'system': [
        "python3-tk",
        "python3-gi",
        "gir1.2-gtk-3.0", 
        "python3-pil",
        "python3-pil.imagetk",
        "python3-requests",
        "fonts-dejavu",
        "python3-apt",
        "policykit-1-gnome",  # policykit-1 yerine policykit-1-gnome kullan
        "gir1.2-notify-0.7",
        "python3-pillow",  # pip yerine sistem paketi
        "python3-requests",  # pip yerine sistem paketi
        "python3-gi"  # pygobject yerine python3-gi
    ],
    'python': []  # Artık pip kullanmıyoruz
}

def check_root():
    if os.geteuid() != 0:
        sys.exit("Bu betiğin root olarak çalıştırılması gerekiyor!")

def install_dependencies():
    try:
        print("Sistem güncelleştiriliyor...")
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        
        print("Bağımlılıklar yükleniyor...")
        # Her paketi tek tek yüklemeyi dene
        for package in DEPENDENCIES['system']:
            try:
                # policykit-1-gnome yoksa polkit-kde-agent-1 dene
                if package == "policykit-1-gnome":
                    try:
                        subprocess.run(["apt-get", "install", "-y", "-qq", package], check=True)
                        print(f"✓ {package} yüklendi")
                    except:
                        alt_package = "polkit-kde-agent-1"
                        subprocess.run(["apt-get", "install", "-y", "-qq", alt_package], check=True)
                        print(f"✓ {alt_package} yüklendi (policykit-1-gnome alternatifi)")
                else:
                    subprocess.run(["apt-get", "install", "-y", "-qq", package], check=True)
                    print(f"✓ {package} yüklendi")
            except subprocess.CalledProcessError:
                print(f"! {package} yüklenemedi, devam ediliyor...")
                continue
                     
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

def create_directories():
    for dir_path in INSTALL_DIR.values():
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o755)

def install_files():
    try:
        # Program dosyaları
        for file in ["main.py", "mainwindow.py", "themes.py", "tools.py", 
                    "categories.py", "style.css"]:
            shutil.copy2(file, INSTALL_DIR['share'])
            
        # Çalıştırılabilir dosya
        bin_path = os.path.join(INSTALL_DIR['bin'], "toolsget")
        shutil.copy2("toolsget", bin_path)
        os.chmod(bin_path, 0o755)
        
        # Desktop dosyası
        desktop_path = os.path.join(INSTALL_DIR['applications'], 
                                  "tr.org.pardus.toolsget.desktop")
        shutil.copy2("tr.org.pardus.toolsget.desktop", desktop_path)
        os.chmod(desktop_path, 0o755)
        
        # Polkit kuralı
        shutil.copy2("tr.org.pardus.toolsget.policy", INSTALL_DIR['polkit'])
        
        # Temalar ve dil dosyaları
        if os.path.exists("themes"):
            shutil.copytree("themes", INSTALL_DIR['themes'], dirs_exist_ok=True)
        if os.path.exists("locale"):
            shutil.copytree("locale", INSTALL_DIR['locale'], dirs_exist_ok=True)
            
        return True
    except Exception as e:
        print(f"Dosya kopyalama hatası: {e}")
        return False

def post_install():
    try:
        # Masaüstü kısayolu
        user = os.environ.get('SUDO_USER', os.environ.get('USER'))
        if user != "root":
            desktop_dir = f"/home/{user}/Masaüstü"
            if os.path.exists(desktop_dir):
                desktop_file = os.path.join(INSTALL_DIR['applications'],
                                          "tr.org.pardus.toolsget.desktop")
                dest = os.path.join(desktop_dir, "Tools Get.desktop")
                shutil.copy2(desktop_file, dest)
                subprocess.run(["chown", f"{user}:{user}", dest])
                os.chmod(dest, 0o755)
        
        # İkon önbelleğini güncelle
        subprocess.run(["gtk-update-icon-cache", "-f", "-t", 
                       "/usr/share/icons/hicolor"], check=False)
        
        # Dil dosyalarını derle
        for lang in os.listdir(INSTALL_DIR['locale']):
            mo_dir = os.path.join(INSTALL_DIR['locale'], lang, "LC_MESSAGES")
            if os.path.exists(mo_dir):
                for po in os.listdir(mo_dir):
                    if po.endswith(".po"):
                        mo = po[:-3] + ".mo"
                        subprocess.run(["msgfmt", "-o", 
                                     os.path.join(mo_dir, mo),
                                     os.path.join(mo_dir, po)], check=False)
        
        print(f"\n{APP_NAME} v{VERSION} başarıyla kuruldu!")
        return True
        
    except Exception as e:
        print(f"Kurulum sonrası işlem hatası: {e}")
        return False

def create_terminal_script():
    script_path = "/usr/bin/toolsget"
    try:
        # Launcher script'i kopyala
        shutil.copy2("toolsget", script_path)
        # İzinleri ayarla
        os.chmod(script_path, 0o755)
        # Sahipliği değiştir
        user = os.environ.get('SUDO_USER', os.environ.get('USER'))
        if user and user != "root":
            subprocess.run(["chown", f"{user}:{user}", script_path])
        return True
    except Exception as e:
        print(f"Terminal script oluşturma hatası: {e}")
        return False

def main():
    check_root()
    
    print(f"\n=== {APP_NAME} v{VERSION} Kurulum ===\n")
    
    if not install_dependencies():
        sys.exit(1)
        
    print("\nDizinler oluşturuluyor...")
    create_directories()
    
    print("\nDosyalar kopyalanıyor...")
    if not install_files():
        sys.exit(1)
    
    print("\nTerminal scripti kuruluyor...")
    if not create_terminal_script():
        sys.exit(1)
        
    print("\nKurulum tamamlanıyor...")
    if not post_install():
        sys.exit(1)

    # Otomatik başlat
    user = os.environ.get('SUDO_USER')
    if user and user != "root":
        try:
            subprocess.Popen(["su", "-c", "toolsget", user])
        except:
            print("Program otomatik başlatılamadı")

if __name__ == "__main__":
    main()

setup(
    name="tools-get",
    version="1.0.0",
    description="Terminal Tools Graphical Interface for Pardus",
    author="Eyyüp Efe Adıgüzel",
    author_email="eyupadiguzel20@gmail.com",
    url="https://github.com/e-Ey-cyber/Terminal-Tools-Grafik-Aray-z-",
    packages=find_packages(),
    install_requires=[
        'PyGObject>=3.36.0',
        'Pillow>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'tools-get=src.main:main',
        ],
    },
    package_data={
        'src': ['icons/*', 'data/*', 'themes/*'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Software Distribution',
    ],
    python_requires='>=3.6',
)

"""
Created by Eyyüp Efe Adıgüzel
Contact: eyupadiguzel20@gmail.com
"""