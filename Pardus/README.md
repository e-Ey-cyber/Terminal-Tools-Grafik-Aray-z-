# Tools Get - Terminal Araçları Grafik Arayüzü

Terminal araçlarını kolayca yönetebileceğiniz, Pardus için geliştirilmiş grafiksel bir kullanıcı arayüzü.

## Özellikler

- 📦 Terminal araçlarını görsel arayüz ile yükleme/kaldırma
- 🔍 Gelişmiş arama ve filtreleme özellikleri
- 📂 Kategorilere göre araçları listeleme
- 🔄 Toplu yükleme için kuyruk sistemi 
- 🌙 Açık/Koyu tema desteği
- 🖥️ Entegre terminal penceresi
- 🔒 PolicyKit desteği ile güvenli yönetici izinleri
- 🌐 Çoklu dil desteği

## Gereksinimler

- Pardus 21.0 veya üzeri
- Python 3.6+
- GTK 3.0+
- Root yetkileri

## Kurulum

### 1. Sistem Paketlerini Yükleyin
```bash
sudo apt update
sudo apt install git python3-pip python3-gi gir1.2-gtk-3.0 python3-pil policykit-1-gnome
```

### 2. Projeyi İndirin
```bash 
git clone https://github.com/e-Ey-cyber/Terminal-Tools-Grafik-Aray-z-
cd Terminal-Tools-Grafik-Aray-z-
```

### 3. Kurulumu Yapın
```bash
sudo python3 setup.py install
```

### 4. Manuel Kurulum (Opsiyonel)
```bash
# Geliştirme için bağımlılıkları yükleyin
pip3 install -e ".[dev]"
```

## Kullanım

### Temel Kullanım

1. Uygulamayı başlatın:
```bash
tools-get
```

2. Sol panelden kategori seçin veya arama yapın
3. Yüklemek istediğiniz aracı seçin
4. "Yükle" butonuna tıklayın veya sıraya ekleyin

### Sık Kullanılan Özellikler

- **Arama**: Üst menüdeki arama kutusunu kullanın
- **Kategori Filtreleme**: Sol üstteki kategori menüsünden seçin  
- **Kuyruk Yönetimi**: 
  - "Sıraya Ekle" ile araçları kuyruğa ekleyin
  - "Kuyruğu Başlat" ile toplu kurulum yapın
- **Terminal**: Terminal penceresini açmak için üstteki terminal ikonuna tıklayın
- **Tema**: Aydınlık/karanlık tema için üstteki tema butonunu kullanın

### Kısayollar

- `Ctrl+F`: Arama
- `Ctrl+Q`: Çıkış
- `F5`: Paket Listesini Yenile
- `F1`: Yardım

## Sorun Giderme

### Sık Karşılaşılan Hatalar

1. "Root yetkisi gerekli" hatası:
```bash
sudo tools-get
```

2. GTK hatası alırsanız:
```bash
sudo apt install --reinstall python3-gi gir1.2-gtk-3.0
```

3. PolicyKit hatası:
```bash
sudo apt install policykit-1-gnome
# veya KDE için:
sudo apt install polkit-kde-agent-1
```

### Günlükler

Hata günlüklerini kontrol edin:
```bash
cat ~/.local/share/toolsget/toolsget.log
```

## Geliştirme

### Geliştirme Ortamı Kurulumu

```bash
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
```

### Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request gönderin

## Lisans

Bu proje GNU General Public License v3.0 lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Eyyüp Efe Adıgüzel
- Email: eyupadiguzel20@gmail.com
- GitHub: [@e-Ey-cyber](https://github.com/e-Ey-cyber)

## Teşekkürler

- Pardus Yazılım Ekibi
- GTK ve Python toplulukları
- Katkıda bulunan tüm geliştiriciler

---
**Not**: Bu araç Pardus için geliştirilmiştir ancak diğer Debian tabanlı dağıtımlarda da çalışabilir.
