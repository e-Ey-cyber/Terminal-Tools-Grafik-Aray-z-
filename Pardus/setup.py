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
    'locale': "/usr/share/locale",
    'cli_completions': "/etc/bash_completion.d",
    'man_pages': "/usr/share/man/man1"
}

DEPENDENCIES = {
    'system': [
        "python3-gi",
        "gir1.2-gtk-3.0",
        "python3-pil",
        "python3-requests",
        "python3-apt",
        "policykit-1-gnome",
        "gir1.2-notify-0.7",
        "python3-setproctitle",  # Process title support
        "python3-psutil",  # System monitoring
        "gir1.2-vte-2.91",  # Terminal emulator
        "python3-argcomplete",  # CLI otomatik tamamlama
        "python3-colorama",     # Renkli terminal çıktısı
        "python3-tabulate",     # Tablo formatında çıktı
        "python3-rich",         # Zengin terminal çıktıları
        "python3-yaml",         # Tema yapılandırması için
        "python3-vte", 
        "python3-notify2",
        "python3-psutil",
        "python3-netifaces",
        "python3-speedtest-cli",
        "python3-tabulate",
        "python3-yaml"
    ],
    'python': [
        'PyGObject>=3.36.0',
        'Pillow>=8.0.0',
        'requests>=2.25.0',
        'psutil>=5.8.0',
        'setproctitle>=1.2.2',
        'python-apt>=2.0.0',
        'argcomplete>=1.12.0',
        'colorama>=0.4.4',
        'tabulate>=0.8.9',
        'rich>=10.0.0',
        'PyYAML>=5.4.1',
        'speedtest-cli>=2.1.3',
        'netifaces>=0.11.0',
        'notify2>=0.3.1',
        'tabulate>=0.8.10',
        'PyYAML>=6.0'  
    ],
    'dev': [
        'pytest>=6.0.0',
        'pylint>=2.8.0',
        'black>=21.0',
        'mypy>=0.900',
        'black>=22.3.0',
        'isort>=5.10.1',
        'flake8>=4.0.1'
    ]
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
        
        # CLI ve tema dosyaları
        shutil.copy2("src/cli.py", INSTALL_DIR['share'])
        shutil.copy2("src/themes.py", INSTALL_DIR['share'])
        
        # Tema dizinleri
        theme_dirs = ['light', 'dark', 'nord', 'dracula', 'solarized']
        for theme in theme_dirs:
            theme_path = os.path.join(INSTALL_DIR['themes'], theme)
            os.makedirs(theme_path, exist_ok=True)
            if os.path.exists(f"themes/{theme}"):
                shutil.copytree(f"themes/{theme}", theme_path, dirs_exist_ok=True)
        
        # Bash completion dosyası
        completion_path = os.path.join(INSTALL_DIR['cli_completions'], "tools-get")
        shutil.copy2("completion/tools-get", completion_path)
        os.chmod(completion_path, 0o644)
        
        # Man sayfası
        man_path = os.path.join(INSTALL_DIR['man_pages'], "tools-get.1")
        shutil.copy2("man/tools-get.1", man_path)
        os.chmod(man_path, 0o644)
            
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
        
        # CLI bash completion'ı yenile
        subprocess.run(["source", "/etc/bash_completion.d/tools-get"], shell=True)
        
        # Man sayfalarını güncelle
        subprocess.run(["mandb", "-q"], check=False)
        
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

def verify_installation():
    """Verify installation was successful"""
    checks = [
        ("GTK3", "gi.repository.Gtk"),
        ("PIL", "PIL.Image"),
        ("Requests", "requests"),
        ("PolicyKit", "gi.repository.Polkit")
    ]
    
    failed = []
    for name, module in checks:
        try:
            __import__(module.split('.')[0])
        except ImportError:
            failed.append(name)
            
    if failed:
        print(f"Kurulum doğrulama hatası - Eksik modüller: {', '.join(failed)}")
        return False
        
    print("Kurulum başarıyla doğrulandı!")
    return True

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

    print("\nKurulum doğrulanıyor...")
    if not verify_installation():
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
    version=VERSION,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=DEPENDENCIES['python'],
    entry_points={
        'console_scripts': [
            'tools-get=src.main:main',
            'tools-get-cli=src.cli:main',
        ],
    },
    package_data={
        'src': [
            'icons/*',
            'data/*',
            'themes/*',
            'themes/*/style.css',
            'themes/*/colors.json'
        ]
    },
    data_files=[
        ('share/bash-completion/completions', ['completion/tools-get']),
        ('share/man/man1', ['man/tools-get.1']),
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
    ],
    python_requires='>=3.6',
)

"""
Created by Eyyüp Efe Adıgüzel
Contact: eyupadiguzel20@gmail.com
"""