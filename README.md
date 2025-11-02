Tools Get - Terminal Araçları Grafik Arayüzü
Terminal araçlarını kolayca yönetebileceğiniz, Pardus için geliştirilmiş grafiksel ve komut satırı arayüzü.

Özellikler
📦 Modern paket yönetim arayüzü ve terminal emülatörü
🎨 Özelleştirilebilir temalar (Açık/Koyu/Nord/Dracula)
🔍 Gelişmiş paket arama ve filtreleme
📊 Sistem kaynak izleme ve performans grafikleri
🔒 PolicyKit entegrasyonu ile güvenli yönetim
🌐 Ağ izleme ve hız testi özellikleri
💾 Toplu kurulum ve güncelleme kuyruğu
🔄 Otomatik güncellemeler
📝 Detaylı paket bilgileri
🎛️ Terminal özelleştirme seçenekleri
Gereksinimler
Pardus 21.0 veya üzeri
Python 3.6+
GTK 3.0+
Root yetkileri
Gereksinimler
# Temel sistem gereksinimleri
sudo apt install python3-gi gir1.2-gtk-3.0 python3-vte python3-notify2
sudo apt install python3-psutil python3-netifaces python3-speedtest-cli
sudo apt install python3-yaml python3-tabulate

# Python gereksinimleri
pip install -r requirements.txt
Kurulum
1. Sistem Paketlerini Yükleyin
sudo apt update
sudo apt install git python3-pip python3-gi gir1.2-gtk-3.0 python3-pil policykit-1-gnome
2. Projeyi İndirin
git clone https://github.com/e-Ey-cyber/Terminal-Tools-Grafik-Aray-z-
cd Terminal-Tools-Grafik-Aray-z-
3. Kurulumu Yapın
sudo python3 setup.py install
4. Manuel Kurulum (Opsiyonel)
# Geliştirme için bağımlılıkları yükleyin
pip3 install -e ".[dev]"
CLI Kurulum
# Doğrudan kurulum
sudo python3 setup.py install

# Geliştirici kurulumu  
pip install -e ".[dev]"
Kullanım
GUI Arayüzü
tools-get
Komut Satırı (CLI) Arayüzü
Temel Komutlar
# Yardım görüntüle  
tools-get-cli --help

# Paket arama
tools-get-cli search <paket_adı>

# Paket yükleme
tools-get-cli install <paket_adı> [<paket_adı2> ...]
tools-get-cli install -y <paket_adı>  # Onay sormadan yükle

# Paket kaldırma
tools-get-cli remove <paket_adı>
tools-get-cli remove -y <paket_adı>  # Onay sormadan kaldır

# Paket bilgisi görüntüleme
tools-get-cli info <paket_adı>

# Paket listesini görüntüleme
tools-get-cli list
tools-get-cli list --installed  # Sadece yüklü paketleri göster

# Sistem durumu
tools-get-cli system info  
Tema Komutları
# Tema listesi
tools-get-cli theme list

# Tema değiştir 
tools-get-cli theme set <tema_adı>

# Yeni tema oluştur
tools-get-cli theme create <tema_adı> --colors <renk_json> 
Kategori İşlemleri
# Kategorileri listeleme
tools-get-cli category list

# Kategorideki paketleri listeleme
tools-get-cli category <kategori_adı>
Kuyruk İşlemleri
# Kuyruğa paket ekleme
tools-get-cli queue add <paket_adı> [<paket_adı2> ...]

# Kuyruktan paket çıkarma
tools-get-cli queue remove <paket_adı>

# Kuyruğu görüntüleme
tools-get-cli queue list

# Kuyruğu temizleme
tools-get-cli queue clear

# Kuyruğu işleme alma
tools-get-cli queue start
Sistem İzleme
# Sistem bilgileri
tools-get-cli system info

# Kaynak kullanımı
tools-get-cli system resources

# Servis durumları  
tools-get-cli system services

# Ağ durumu
tools-get-cli system network
Bakım İşlemleri
# Sistem temizliği
tools-get-cli maintain clean

# Sistem yedekleme
tools-get-cli maintain backup

# Sistem onarımı
tools-get-cli maintain repair

# Sistem optimizasyonu
tools-get-cli maintain optimize
Güvenlik Kontrolleri
# Güvenlik taraması
tools-get-cli security scan

# Güvenlik güncellemeleri
tools-get-cli security update

# Sistem sertleştirme
tools-get-cli security harden
Diğer Seçenekler
# Versiyon bilgisi
tools-get-cli --version

# Detaylı çıktı
tools-get-cli -v search <paket_adı>

# Yardım görüntüleme
tools-get-cli --help
tools-get-cli <komut> --help
Örnek Kullanımlar
# Htop paketini ara
tools-get-cli search htop

# Birden fazla paket yükle
tools-get-cli install htop neofetch vim

# Sistem izleme kategorisindeki paketleri listele
tools-get-cli category "Sistem İzleme"

# Sıraya paketler ekle ve işleme al
tools-get-cli queue add htop neofetch
tools-get-cli queue add vim
tools-get-cli queue list
tools-get-cli queue start
Sık Kullanılan Özellikler
Arama: Üst menüdeki arama kutusunu kullanın
Kategori Filtreleme: Sol üstteki kategori menüsünden seçin
Kuyruk Yönetimi:
"Sıraya Ekle" ile araçları kuyruğa ekleyin
"Kuyruğu Başlat" ile toplu kurulum yapın
Terminal: Terminal penceresini açmak için üstteki terminal ikonuna tıklayın
Tema: Aydınlık/karanlık tema için üstteki tema butonunu kullanın
Kısayollar
Ctrl+F: Arama
Ctrl+Q: Çıkış
F5: Paket Listesini Yenile
F1: Yardım
Sorun Giderme
Sık Karşılaşılan Hatalar
"Root yetkisi gerekli" hatası:
sudo tools-get
GTK hatası alırsanız:
sudo apt install --reinstall python3-gi gir1.2-gtk-3.0
PolicyKit hatası:
sudo apt install policykit-1-gnome
# veya KDE için:
sudo apt install polkit-kde-agent-1
Günlükler
Hata günlüklerini kontrol edin:

cat ~/.local/share/toolsget/toolsget.log
Geliştirme
Geliştirme Ortamı Kurulumu
# Gerekli paketleri yükleyin
sudo apt install python3-dev python3-pip git

# Projeyi klonlayın
git clone https://github.com/e-Ey-cyber/Terminal-Tools-Grafik-Aray-z-
cd Terminal-Tools-Grafik-Aray-z-

# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Geliştirme bağımlılıklarını yükleyin
pip install -e ".[dev]"
Katkıda Bulunma
Projeyi fork edin
Feature branch oluşturun (git checkout -b feature/AmazingFeature)
Değişikliklerinizi commit edin (git commit -m 'Add some AmazingFeature')
Branch'inizi push edin (git push origin feature/AmazingFeature)
Pull Request gönderin
Lisans
Bu proje GNU General Public License v3.0 lisansı ile lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

İletişim
Eyyüp Efe Adıgüzel

Email: eyupadiguzel20@gmail.com
GitHub: @e-Ey-cyber
Teşekkürler
Pardus Yazılım Ekibi
GTK ve Python toplulukları
Katkıda bulunan tüm geliştiriciler
