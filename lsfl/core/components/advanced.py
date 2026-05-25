"""
Gelişmiş MSI/LSI bileşenleri - Tam simülasyon mantığı ile
"""

from core.component import Component


class Adder8Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("8-bit Adder", x, y, 140, 160)
        self.type = "ADDER_8BIT"
        
        # 8-bit A girişi
        for i in range(8):
            self.add_input_pin(f"A{i}")
        # 8-bit B girişi
        for i in range(8):
            self.add_input_pin(f"B{i}")
        # Carry in
        self.add_input_pin("Cin")
        
        # 8-bit Sum çıkışı
        for i in range(8):
            self.add_output_pin(f"S{i}")
        # Carry out
        self.add_output_pin("Cout")
        
    def update(self):
        # 8-bit toplama
        a = sum(self.input_pins[i].value << i for i in range(8))
        b = sum(self.input_pins[8+i].value << i for i in range(8))
        cin = self.input_pins[16].value
        
        result = a + b + cin
        
        # Sonucu bit bit çıkışa yaz
        for i in range(8):
            self.output_pins[i].set_value((result >> i) & 1)
        # Carry out
        self.output_pins[8].set_value((result >> 8) & 1)


class Subtractor(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Subtractor", x, y, 120, 100)
        self.type = "SUBTRACTOR"
        
        # 4-bit girişler
        for i in range(4):
            self.add_input_pin(f"A{i}")
        for i in range(4):
            self.add_input_pin(f"B{i}")
        self.add_input_pin("Bin")  # Borrow in
        
        # 4-bit çıkış
        for i in range(4):
            self.add_output_pin(f"D{i}")
        self.add_output_pin("Bout")  # Borrow out
        
    def update(self):
        # A - B - Bin
        a = sum(self.input_pins[i].value << i for i in range(4))
        b = sum(self.input_pins[4+i].value << i for i in range(4))
        bin_val = self.input_pins[8].value
        
        result = a - b - bin_val
        
        # Sonuç negatifse borrow var
        if result < 0:
            result = (1 << 4) + result  # 2'nin tümleyeni
            borrow = True
        else:
            borrow = False
        
        for i in range(4):
            self.output_pins[i].set_value((result >> i) & 1)
        self.output_pins[4].set_value(borrow)


class Multiplier(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Multiplier", x, y, 120, 100)
        self.type = "MULTIPLIER"
        
        # 4-bit girişler
        for i in range(4):
            self.add_input_pin(f"A{i}")
        for i in range(4):
            self.add_input_pin(f"B{i}")
        
        # 8-bit çıkış (4x4=8 bit)
        for i in range(8):
            self.add_output_pin(f"P{i}")
        
    def update(self):
        a = sum(self.input_pins[i].value << i for i in range(4))
        b = sum(self.input_pins[4+i].value << i for i in range(4))
        
        product = a * b
        
        for i in range(8):
            self.output_pins[i].set_value((product >> i) & 1)


class Mux8to1(Component):
    def __init__(self, x=0, y=0):
        super().__init__("MUX 8:1", x, y, 110, 140)
        self.type = "MUX_8TO1"
        
        # 8 veri girişi
        for i in range(8):
            self.add_input_pin(f"I{i}")
        # 3 seçim girişi (2^3 = 8)
        self.add_input_pin("S0")
        self.add_input_pin("S1")
        self.add_input_pin("S2")
        
        self.add_output_pin("Y")
        
    def update(self):
        inputs = [self.input_pins[i].value for i in range(8)]
        s0 = self.input_pins[8].value
        s1 = self.input_pins[9].value
        s2 = self.input_pins[10].value
        
        sel = (s2 << 2) | (s1 << 1) | s0
        self.output_pins[0].set_value(inputs[sel])


class Demux1to2(Component):
    def __init__(self, x=0, y=0):
        super().__init__("DEMUX 1:2", x, y, 90, 70)
        self.type = "DEMUX_1TO2"
        
        self.add_input_pin("In")
        self.add_input_pin("Sel")
        
        self.add_output_pin("Y0")
        self.add_output_pin("Y1")
        
    def update(self):
        in_val = self.input_pins[0].value
        sel = self.input_pins[1].value
        
        if sel:
            self.output_pins[0].set_value(False)
            self.output_pins[1].set_value(in_val)
        else:
            self.output_pins[0].set_value(in_val)
            self.output_pins[1].set_value(False)


class Demux1to4(Component):
    def __init__(self, x=0, y=0):
        super().__init__("DEMUX 1:4", x, y, 100, 100)
        self.type = "DEMUX_1TO4"
        
        self.add_input_pin("In")
        self.add_input_pin("S0")
        self.add_input_pin("S1")
        
        for i in range(4):
            self.add_output_pin(f"Y{i}")
        
    def update(self):
        in_val = self.input_pins[0].value
        s0 = self.input_pins[1].value
        s1 = self.input_pins[2].value
        
        sel = (s1 << 1) | s0
        
        for i in range(4):
            self.output_pins[i].set_value(in_val if i == sel else False)


class Demux1to8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("DEMUX 1:8", x, y, 110, 140)
        self.type = "DEMUX_1TO8"
        
        self.add_input_pin("In")
        self.add_input_pin("S0")
        self.add_input_pin("S1")
        self.add_input_pin("S2")
        
        for i in range(8):
            self.add_output_pin(f"Y{i}")
        
    def update(self):
        in_val = self.input_pins[0].value
        s0 = self.input_pins[1].value
        s1 = self.input_pins[2].value
        s2 = self.input_pins[3].value
        
        sel = (s2 << 2) | (s1 << 1) | s0
        
        for i in range(8):
            self.output_pins[i].set_value(in_val if i == sel else False)


class Encoder4to2(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Encoder 4:2", x, y, 90, 80)
        self.type = "ENCODER_4TO2"
        
        for i in range(4):
            self.add_input_pin(f"I{i}")
        
        self.add_output_pin("Y0")
        self.add_output_pin("Y1")
        
    def update(self):
        # Priority encoder - en yüksek öncelikli girişi kodla
        inputs = [self.input_pins[i].value for i in range(4)]
        
        # En yüksek aktif biti bul
        encoded = 0
        for i in range(3, -1, -1):
            if inputs[i]:
                encoded = i
                break
        
        self.output_pins[0].set_value(encoded & 1)
        self.output_pins[1].set_value((encoded >> 1) & 1)


class Encoder8to3(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Encoder 8:3", x, y, 100, 120)
        self.type = "ENCODER_8TO3"
        
        for i in range(8):
            self.add_input_pin(f"I{i}")
        
        self.add_output_pin("Y0")
        self.add_output_pin("Y1")
        self.add_output_pin("Y2")
        
    def update(self):
        inputs = [self.input_pins[i].value for i in range(8)]
        
        encoded = 0
        for i in range(7, -1, -1):
            if inputs[i]:
                encoded = i
                break
        
        self.output_pins[0].set_value(encoded & 1)
        self.output_pins[1].set_value((encoded >> 1) & 1)
        self.output_pins[2].set_value((encoded >> 2) & 1)


class Decoder2to4(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Decoder 2:4", x, y, 90, 80)
        self.type = "DECODER_2TO4"
        
        self.add_input_pin("A0")
        self.add_input_pin("A1")
        self.add_input_pin("EN")  # Enable
        
        for i in range(4):
            self.add_output_pin(f"Y{i}")
        
    def update(self):
        a0 = self.input_pins[0].value
        a1 = self.input_pins[1].value
        en = self.input_pins[2].value
        
        if not en:
            # Disable durumunda tüm çıkışlar 0
            for i in range(4):
                self.output_pins[i].set_value(False)
        else:
            addr = (a1 << 1) | a0
            for i in range(4):
                self.output_pins[i].set_value(i == addr)


class Decoder3to8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Decoder 3:8", x, y, 100, 120)
        self.type = "DECODER_3TO8"
        
        self.add_input_pin("A0")
        self.add_input_pin("A1")
        self.add_input_pin("A2")
        self.add_input_pin("EN")
        
        for i in range(8):
            self.add_output_pin(f"Y{i}")
        
    def update(self):
        a0 = self.input_pins[0].value
        a1 = self.input_pins[1].value
        a2 = self.input_pins[2].value
        en = self.input_pins[3].value
        
        if not en:
            for i in range(8):
                self.output_pins[i].set_value(False)
        else:
            addr = (a2 << 2) | (a1 << 1) | a0
            for i in range(8):
                self.output_pins[i].set_value(i == addr)


class SRFlipFlop(Component):
    def __init__(self, x=0, y=0):
        super().__init__("SR FF", x, y, 90, 80)
        self.type = "SR_FLIPFLOP"
        
        self.add_input_pin("S")
        self.add_input_pin("R")
        self.add_input_pin("CLK")
        
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        self.last_clk = False
        
    def update(self):
        s = self.input_pins[0].value
        r = self.input_pins[1].value
        clk = self.input_pins[2].value
        
        # Rising edge tetiklemeli
        if clk and not self.last_clk:
            if s and not r:
                self.state = True  # Set
            elif r and not s:
                self.state = False  # Reset
            # S=R=1 durumu tanımsız, değişiklik yapma
            # S=R=0 durumu önceki durumu koru
        
        self.last_clk = clk
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False
        self.last_clk = False


class TFlipFlop(Component):
    def __init__(self, x=0, y=0):
        super().__init__("T FF", x, y, 90, 70)
        self.type = "T_FLIPFLOP"
        
        self.add_input_pin("T")
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        self.last_clk = False
        
    def update(self):
        t = self.input_pins[0].value
        clk = self.input_pins[1].value
        rst = self.input_pins[2].value
        
        if rst:
            self.state = False
        elif clk and not self.last_clk:
            if t:
                self.state = not self.state  # Toggle
        
        self.last_clk = clk
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False
        self.last_clk = False


class DLatch(Component):
    def __init__(self, x=0, y=0):
        super().__init__("D Latch", x, y, 80, 70)
        self.type = "LATCH_D"
        
        self.add_input_pin("D")
        self.add_input_pin("EN")  # Enable (level-triggered)
        
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        
    def update(self):
        d = self.input_pins[0].value
        en = self.input_pins[1].value
        
        # Level-triggered: EN=1 iken D'yi takip et
        if en:
            self.state = d
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False


class SRLatch(Component):
    def __init__(self, x=0, y=0):
        super().__init__("SR Latch", x, y, 80, 70)
        self.type = "LATCH_SR"
        
        self.add_input_pin("S")
        self.add_input_pin("R")
        
        self.add_output_pin("Q")
        self.add_output_pin("Q'")
        
        self.state = False
        
    def update(self):
        s = self.input_pins[0].value
        r = self.input_pins[1].value
        
        # Asenkron latch
        if s and not r:
            self.state = True
        elif r and not s:
            self.state = False
        # S=R=1 tanımsız, S=R=0 önceki durumu koru
        
        self.output_pins[0].set_value(self.state)
        self.output_pins[1].set_value(not self.state)
        
    def reset(self):
        super().reset()
        self.state = False


class Register4Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("4-bit Reg", x, y, 100, 100)
        self.type = "REGISTER_4BIT"
        
        # 4-bit veri girişi
        for i in range(4):
            self.add_input_pin(f"D{i}")
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        
        # 4-bit veri çıkışı
        for i in range(4):
            self.add_output_pin(f"Q{i}")
        
        self.data = 0
        self.last_clk = False
        
    def update(self):
        clk = self.input_pins[4].value
        rst = self.input_pins[5].value
        
        if rst:
            self.data = 0
        elif clk and not self.last_clk:
            # Rising edge'de veriyi kaydet
            self.data = sum(self.input_pins[i].value << i for i in range(4))
        
        self.last_clk = clk
        
        # Çıkışa yaz
        for i in range(4):
            self.output_pins[i].set_value((self.data >> i) & 1)
        
    def reset(self):
        super().reset()
        self.data = 0
        self.last_clk = False


class Register8Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("8-bit Reg", x, y, 120, 140)
        self.type = "REGISTER_8BIT"
        
        for i in range(8):
            self.add_input_pin(f"D{i}")
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        
        for i in range(8):
            self.add_output_pin(f"Q{i}")
        
        self.data = 0
        self.last_clk = False
        
    def update(self):
        clk = self.input_pins[8].value
        rst = self.input_pins[9].value
        
        if rst:
            self.data = 0
        elif clk and not self.last_clk:
            self.data = sum(self.input_pins[i].value << i for i in range(8))
        
        self.last_clk = clk
        
        for i in range(8):
            self.output_pins[i].set_value((self.data >> i) & 1)
        
    def reset(self):
        super().reset()
        self.data = 0
        self.last_clk = False


class ShiftRegister(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Shift Reg", x, y, 100, 100)
        self.type = "SHIFT_REGISTER"
        
        self.add_input_pin("SI")  # Serial In
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        
        # 4-bit paralel çıkış
        for i in range(4):
            self.add_output_pin(f"Q{i}")
        
        self.data = 0
        self.last_clk = False
        
    def update(self):
        si = self.input_pins[0].value
        clk = self.input_pins[1].value
        rst = self.input_pins[2].value
        
        if rst:
            self.data = 0
        elif clk and not self.last_clk:
            # Sola kaydır ve yeni biti sağdan ekle
            self.data = ((self.data << 1) | si) & 0xF
        
        self.last_clk = clk
        
        for i in range(4):
            self.output_pins[i].set_value((self.data >> i) & 1)
        
    def reset(self):
        super().reset()
        self.data = 0
        self.last_clk = False


class Counter4Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("4-bit Counter", x, y, 100, 90)
        self.type = "COUNTER_4BIT"
        
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        self.add_input_pin("EN")  # Enable
        
        for i in range(4):
            self.add_output_pin(f"Q{i}")
        
        self.count = 0
        self.last_clk = False
        
    def update(self):
        clk = self.input_pins[0].value
        rst = self.input_pins[1].value
        en = self.input_pins[2].value
        
        if rst:
            self.count = 0
        elif en and clk and not self.last_clk:
            self.count = (self.count + 1) & 0xF
        
        self.last_clk = clk
        
        for i in range(4):
            self.output_pins[i].set_value((self.count >> i) & 1)
        
    def reset(self):
        super().reset()
        self.count = 0
        self.last_clk = False


class Counter8Bit(Component):
    def __init__(self, x=0, y=0):
        super().__init__("8-bit Counter", x, y, 120, 130)
        self.type = "COUNTER_8BIT"
        
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        self.add_input_pin("EN")
        
        for i in range(8):
            self.add_output_pin(f"Q{i}")
        
        self.count = 0
        self.last_clk = False
        
    def update(self):
        clk = self.input_pins[0].value
        rst = self.input_pins[1].value
        en = self.input_pins[2].value
        
        if rst:
            self.count = 0
        elif en and clk and not self.last_clk:
            self.count = (self.count + 1) & 0xFF
        
        self.last_clk = clk
        
        for i in range(8):
            self.output_pins[i].set_value((self.count >> i) & 1)
        
    def reset(self):
        super().reset()
        self.count = 0
        self.last_clk = False


class UpDownCounter(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Up/Down Counter", x, y, 110, 100)
        self.type = "UP_DOWN_COUNTER"
        
        self.add_input_pin("CLK")
        self.add_input_pin("RST")
        self.add_input_pin("UP")  # 1=Up, 0=Down
        self.add_input_pin("EN")
        
        for i in range(4):
            self.add_output_pin(f"Q{i}")
        
        self.count = 0
        self.last_clk = False
        
    def update(self):
        clk = self.input_pins[0].value
        rst = self.input_pins[1].value
        up = self.input_pins[2].value
        en = self.input_pins[3].value
        
        if rst:
            self.count = 0
        elif en and clk and not self.last_clk:
            if up:
                self.count = (self.count + 1) & 0xF
            else:
                self.count = (self.count - 1) & 0xF
        
        self.last_clk = clk
        
        for i in range(4):
            self.output_pins[i].set_value((self.count >> i) & 1)
        
    def reset(self):
        super().reset()
        self.count = 0
        self.last_clk = False


class RAM16x8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("RAM 16x8", x, y, 130, 160)
        self.type = "RAM_16X8"
        
        # 4-bit adres
        for i in range(4):
            self.add_input_pin(f"A{i}")
        # 8-bit veri girişi
        for i in range(8):
            self.add_input_pin(f"DI{i}")
        self.add_input_pin("WE")  # Write Enable
        self.add_input_pin("CLK")
        
        # 8-bit veri çıkışı
        for i in range(8):
            self.add_output_pin(f"DO{i}")
        
        self.memory = [0] * 16
        self.last_clk = False
        
    def update(self):
        # Adresi oku
        addr = sum(self.input_pins[i].value << i for i in range(4))
        we = self.input_pins[12].value
        clk = self.input_pins[13].value
        
        # Yazma işlemi (rising edge)
        if we and clk and not self.last_clk:
            data_in = sum(self.input_pins[4+i].value << i for i in range(8))
            self.memory[addr] = data_in
        
        self.last_clk = clk
        
        # Okuma işlemi (asenkron)
        data_out = self.memory[addr]
        for i in range(8):
            self.output_pins[i].set_value((data_out >> i) & 1)
        
    def reset(self):
        super().reset()
        self.memory = [0] * 16
        self.last_clk = False


class RAM256x8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("RAM 256x8", x, y, 150, 200)
        self.type = "RAM_256X8"
        
        # 8-bit adres
        for i in range(8):
            self.add_input_pin(f"A{i}")
        # 8-bit veri girişi
        for i in range(8):
            self.add_input_pin(f"DI{i}")
        self.add_input_pin("WE")
        self.add_input_pin("CLK")
        
        # 8-bit veri çıkışı
        for i in range(8):
            self.add_output_pin(f"DO{i}")
        
        self.memory = [0] * 256
        self.last_clk = False
        
    def update(self):
        addr = sum(self.input_pins[i].value << i for i in range(8))
        we = self.input_pins[16].value
        clk = self.input_pins[17].value
        
        if we and clk and not self.last_clk:
            data_in = sum(self.input_pins[8+i].value << i for i in range(8))
            self.memory[addr] = data_in
        
        self.last_clk = clk
        
        data_out = self.memory[addr]
        for i in range(8):
            self.output_pins[i].set_value((data_out >> i) & 1)
        
    def reset(self):
        super().reset()
        self.memory = [0] * 256
        self.last_clk = False


class ROM16x8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("ROM 16x8", x, y, 120, 140)
        self.type = "ROM_16X8"
        
        # 4-bit adres
        for i in range(4):
            self.add_input_pin(f"A{i}")
        
        # 8-bit veri çıkışı
        for i in range(8):
            self.add_output_pin(f"DO{i}")
        
        # ROM içeriği (örnek: sayma tablosu)
        self.memory = [i for i in range(16)]
        
    def update(self):
        addr = sum(self.input_pins[i].value << i for i in range(4))
        data_out = self.memory[addr]
        
        for i in range(8):
            self.output_pins[i].set_value((data_out >> i) & 1)


class ROM256x8(Component):
    def __init__(self, x=0, y=0):
        super().__init__("ROM 256x8", x, y, 140, 180)
        self.type = "ROM_256X8"
        
        # 8-bit adres
        for i in range(8):
            self.add_input_pin(f"A{i}")
        
        # 8-bit veri çıkışı
        for i in range(8):
            self.add_output_pin(f"DO{i}")
        
        self.memory = [i & 0xFF for i in range(256)]
        
    def update(self):
        addr = sum(self.input_pins[i].value << i for i in range(8))
        data_out = self.memory[addr]
        
        for i in range(8):
            self.output_pins[i].set_value((data_out >> i) & 1)


class Splitter(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Splitter", x, y, 80, 100)
        self.type = "SPLITTER"
        
        # 8-bit giriş
        for i in range(8):
            self.add_input_pin(f"I{i}")
        
        # 2x 4-bit çıkış
        for i in range(4):
            self.add_output_pin(f"L{i}")  # Lower nibble
        for i in range(4):
            self.add_output_pin(f"H{i}")  # Higher nibble
        
    def update(self):
        # Alt 4 bit
        for i in range(4):
            self.output_pins[i].set_value(self.input_pins[i].value)
        # Üst 4 bit
        for i in range(4):
            self.output_pins[4+i].set_value(self.input_pins[4+i].value)


class Merger(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Merger", x, y, 80, 100)
        self.type = "MERGER"
        
        # 2x 4-bit giriş
        for i in range(4):
            self.add_input_pin(f"L{i}")
        for i in range(4):
            self.add_input_pin(f"H{i}")
        
        # 8-bit çıkış
        for i in range(8):
            self.add_output_pin(f"O{i}")
        
    def update(self):
        # Alt 4 bit
        for i in range(4):
            self.output_pins[i].set_value(self.input_pins[i].value)
        # Üst 4 bit
        for i in range(4):
            self.output_pins[4+i].set_value(self.input_pins[4+i].value)
