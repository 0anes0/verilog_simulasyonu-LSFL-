# LSFL - Logic Sim For Linux

Modern mantık devresi simülatörü ve Verilog kod üreteci.

## Özellikler

- 🎨 Modern ve temiz arayüz
- 🔌 Kapsamlı bileşen kütüphanesi (Mantık kapıları, Flip-Flops, Multiplexer, Adder, vb.)
- 🖱️ Kolay sürükle-bırak arayüzü
- 🔗 Rahat kablo bağlantıları
- ⚡ Gerçek zamanlı simülasyon
- 📋 Tek tuşla Verilog kodu üretimi
- 💾 Devre kaydetme/yükleme
- 🔍 Zoom ve pan özellikleri

## Kurulum

### Arch Linux / Manjaro / CachyOS

```bash
sudo pacman -S python-pyqt6
```

### Diğer Dağıtımlar

```bash
pip install -r requirements.txt
```

veya sanal ortam kullanarak:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Kullanım

```bash
python lsfl/main.py
```

## Kısayol Tuşları

- `Ctrl+N`: Yeni devre
- `Ctrl+O`: Devre aç
- `Ctrl+S`: Kaydet
- `Ctrl+E`: Verilog kodu üret
- `Space`: Simülasyon başlat/durdur
- `Ctrl+R`: Simülasyonu sıfırla
- `Delete`: Seçili bileşenleri sil
- `Ctrl+A`: Tümünü seç
- `Ctrl+Scroll`: Zoom in/out
- `Orta Fare Tuşu`: Pan (kaydırma)
- `Sol Tık`: Bileşen yerleştir / Bileşen seç / Pin'den kablo çek
- `Sağ Tık`: İptal (yerleştirme/kablo)
- `Sürükle`: Bileşen taşı veya kare seçim
- `Ctrl+Tık`: Çoklu seçim
- `Esc`: Yerleştirme modundan çık

## Bileşenler

### Mantık Kapıları
- AND, OR, NOT, NAND, NOR, XOR, XNOR, Buffer

### Aritmetik
- Half Adder, Full Adder, 4-bit Adder, 8-bit Adder
- Comparator, Multiplier, Subtractor

### Multiplexer/Demultiplexer
- 2:1, 4:1, 8:1 Multiplexer
- 1:2, 1:4, 1:8 Demultiplexer

### Flip-Flops
- D, JK, T, SR Flip-Flops
- D, SR Latches

### Register/Counter
- 4-bit, 8-bit Registers
- Shift Register
- 4-bit, 8-bit Counters
- Up/Down Counter

### Bellek
- RAM (16x8, 256x8)
- ROM (16x8, 256x8)

### Giriş/Çıkış
- Input Pin, Output Pin (Manuel test için)
- Switch, Button, Clock
- LED, RGB LED
- 7-Segment Display, Hex Display

## Kullanım İpuçları

### Temel İşlemler
- **Bileşen Ekleme**: Sol panelden bileşene tıklayın, ardından canvas'ta istediğiniz yere tıklayın
- **Bileşen Taşıma**: Bileşene tıklayıp sürükleyin
- **Çoklu Seçim**: Boş alandan sürükleyerek kare oluşturun veya `Ctrl + Tık` ile tek tek seçin
- **Kablo Bağlama**: Bir pin'e tıklayın, ardından hedef pin'e tıklayın
- **İptal**: Sağ tık ile yerleştirme veya kablo bağlantısını iptal edin

### Görünüm Kontrolleri
- **Zoom**: `Ctrl + Mouse Wheel` ile yakınlaştırma/uzaklaştırma
- **Pan**: Orta fare tuşu ile sürükleyerek haritada gezinme
- **Grid**: Hassas yerleştirme için 20px grid sistemi

### Simülasyon
- **Test Modu (Simülasyon Durdurulduğunda)**:
  - Input Pin ve Switch'lere tıklayarak değerlerini değiştirebilirsiniz
  - Devre düzenlenebilir (bileşen ekleme, taşıma, silme)
  - Her değişiklik sonrası devre otomatik güncellenir
  
- **Çalışma Modu (Simülasyon Başlatıldığında)**:
  - Devre otomatik olarak 10 Hz hızında güncellenir
  - Clock bileşenleri otomatik çalışır
  - Düzenleme yapılamaz (sadece izleme)
  - Arka plan yeşilimsi renkte görünür
  
- **Gerçek Zamanlı**: Sinyal değişiklikleri anında görünür (yeşil = 1, gri = 0)

### Profesyonel Özellikler
- **IEEE Semboller**: Mantık kapıları IEEE standart sembollerle gösterilir
- **Kare Seçim**: Büyük devrelerde toplu işlem için
- **Akıllı Kablo Yönlendirme**: Proteus tarzı ortogonal kablolama

## Verilog Export

Devrenizi çizdikten sonra sağ üstteki "Verilog Kodu Üret" butonuna tıklayarak
FPGA projelerinizde kullanabileceğiniz Verilog kodunu alabilirsiniz.

## Lisans

MIT License

## Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!
