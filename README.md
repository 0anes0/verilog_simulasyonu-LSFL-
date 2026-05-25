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

```bash
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
- Switch, Button, Clock
- LED, RGB LED
- 7-Segment Display, Hex Display

## Verilog Export

Devrenizi çizdikten sonra sağ üstteki "Verilog Kodu Üret" butonuna tıklayarak
FPGA projelerinizde kullanabileceğiniz Verilog kodunu alabilirsiniz.

## Lisans

MIT License

## Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!
