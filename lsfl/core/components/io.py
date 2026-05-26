"""
Giriş/Çıkış bileşenleri
"""

from core.component import Component
from PyQt6.QtCore import QTimer


class Switch(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Switch", x, y, 70, 50)
        self.type = "SWITCH"
        # Seri anahtar: 1 giriş, 1 çıkış
        self.add_input_pin("In")
        self.add_output_pin("Out")
        self.state = True  # Varsayılan: ON (kapalı devre)
        self.is_pressed = False  # Görsel basılı durumu
        
    def toggle(self):
        self.state = not self.state
        self.update()
    
    def press(self):
        """Butona basıldı - görsel ve mantıksal"""
        self.is_pressed = True
        self.state = True
        self.update()
    
    def release(self):
        """Buton bırakıldı - görsel güncelleme"""
        self.is_pressed = False
        # State değişmez (toggle switch gibi)
        
    def update(self):
        """Switch ON ise: Out = In, Switch OFF ise: Out = 0 (açık devre)"""
        try:
            if self.state:
                # ON: Sinyali geçir
                in_val = self.input_pins[0].value if len(self.input_pins) > 0 else False
                self.output_pins[0].value = bool(in_val)
            else:
                # OFF: Çıkışı 0 yap (açık devre)
                self.output_pins[0].value = False
        except (IndexError, AttributeError):
            self.output_pins[0].value = False


class LED(Component):
    def __init__(self, x=0, y=0):
        super().__init__("LED", x, y, 50, 50)
        self.type = "LED"
        self.add_input_pin("In")
        
    def update(self):
        # LED sadece görselleştirme için, mantık yok
        pass


class Clock(Component):
    def __init__(self, x=0, y=0):
        super().__init__("CLK", x, y, 70, 50)
        self.type = "CLOCK"
        self.add_output_pin("Out")
        
        self.state = False
        self.frequency = 1  # Hz (kullanılmıyor, global clock tarafından yönetiliyor)
        self.tick_count = 0
        
    def set_frequency(self, freq):
        """Frekansı ayarla (şimdilik sadece sakla)"""
        self.frequency = freq
        
    def update(self):
        """Çıkış pinini güncelle - state global clock tarafından yönetiliyor"""
        self.output_pins[0].value = bool(self.state)
        
    def reset(self):
        """Clock'u sıfırla"""
        super().reset()
        self.state = False
        self.tick_count = 0


class InputPin(Component):
    def __init__(self, x=0, y=0):
        super().__init__("IN", x, y, 70, 50)
        self.type = "INPUT_PIN"
        self.add_output_pin("Out")
        self.state = False
        self.custom_name = "IN"
        
    def toggle(self):
        """Durumu değiştir ve sinyali yay"""
        self.state = not self.state
        # Çıkış pinini hemen güncelle
        self.update()
        
    def update(self):
        """Çıkış pinini güncelle - state ile senkronize"""
        try:
            if len(self.output_pins) > 0:
                # State değerini doğrudan çıkışa yaz
                self.output_pins[0].value = bool(self.state)
        except (IndexError, AttributeError):
            pass
    
    def set_custom_name(self, name):
        """Özel isim ata"""
        self.custom_name = name
        self.name = name


class OutputPin(Component):
    def __init__(self, x=0, y=0):
        super().__init__("OUT", x, y, 70, 50)
        self.type = "OUTPUT_PIN"
        self.add_input_pin("In")
        self.custom_name = "OUT"
        self.display_value = False  # Görüntülenen değer
        
    def update(self):
        """Output pin - giriş sinyalini oku ve görüntüle"""
        try:
            if len(self.input_pins) > 0:
                # Giriş değerini al ve görüntüleme için sakla
                self.display_value = bool(self.input_pins[0].value)
        except (IndexError, AttributeError):
            self.display_value = False
    
    def set_custom_name(self, name):
        """Özel isim ata"""
        self.custom_name = name
        self.name = name


class VCC(Component):
    """VCC - Sabit 1 (High) kaynağı"""
    def __init__(self, x=0, y=0):
        super().__init__("VCC", x, y, 60, 40)
        self.type = "VCC"
        # 0 giriş, 1 çıkış
        self.add_output_pin("Out")
        
    def update(self):
        """Her zaman 1 (True) üret"""
        self.output_pins[0].value = True


class Ground(Component):
    """GROUND - Sabit 0 (Low) kaynağı"""
    def __init__(self, x=0, y=0):
        super().__init__("GND", x, y, 60, 40)
        self.type = "GROUND"
        # 0 giriş, 1 çıkış
        self.add_output_pin("Out")
        
    def update(self):
        """Her zaman 0 (False) üret"""
        self.output_pins[0].value = False


class Constant(Component):
    """CONSTANT - Ayarlanabilir sabit değer"""
    def __init__(self, x=0, y=0):
        super().__init__("CONST", x, y, 70, 50)
        self.type = "CONSTANT"
        # 0 giriş, 1 çıkış
        self.add_output_pin("Out")
        self.constant_value = True  # Varsayılan: 1
        
    def toggle(self):
        """Sabit değeri değiştir (0/1)"""
        self.constant_value = not self.constant_value
        self.update()
        
    def update(self):
        """Sabit değeri üret"""
        self.output_pins[0].value = bool(self.constant_value)


class Probe(Component):
    """PROBE - Logic göstergesi"""
    def __init__(self, x=0, y=0):
        super().__init__("PROBE", x, y, 70, 50)
        self.type = "PROBE"
        # 1 giriş, 0 çıkış
        self.add_input_pin("In")
        self.probe_value = False  # Görüntülenen değer
        
    def update(self):
        """Giriş sinyalini oku ve sakla"""
        try:
            if len(self.input_pins) > 0:
                self.probe_value = bool(self.input_pins[0].value)
        except (IndexError, AttributeError):
            self.probe_value = False
