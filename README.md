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
- `Sol Tık`: Bileşen seç / Pin'den kablo çek
- `Sağ Tık`: Kablo bağlantısını iptal et

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

- **Zoom**: `Ctrl + Mouse Wheel` ile yakınlaştırma/uzaklaştırma
- **Pan**: Orta fare tuşu ile sürükleyerek haritada gezinme
- **Kablo Bağlama**: Herhangi bir pin'e tıklayın, ardından hedef pin'e tıklayın
- **Input Test**: Input Pin veya Switch'e tıklayarak ON/OFF yapabilirsiniz
- **Bileşen Ekleme**: Sol panelden bileşene tıklayın, görünür alanda ortaya eklenir
- **IEEE Semboller**: Mantık kapıları IEEE standart sembollerle gösterilir

## Verilog Export

Devrenizi çizdikten sonra sağ üstteki "Verilog Kodu Üret" butonuna tıklayarak
FPGA projelerinizde kullanabileceğiniz Verilog kodunu alabilirsiniz.

## Lisans

MIT License

## Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!
