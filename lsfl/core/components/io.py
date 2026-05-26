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
        if self.state:
            # ON: Sinyali geçir
            self.output_pins[0].set_value(self.input_pins[0].value)
        else:
            # OFF: Çıkışı 0 yap (açık devre)
            self.output_pins[0].set_value(False)


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
        self.frequency = 1  # Hz
        self.tick_count = 0
        self.half_period_ms = 500  # 1 Hz için 500ms yarım periyot
        self.last_toggle_time = 0
        
    def set_frequency(self, freq):
        """Frekansı ayarla"""
        self.frequency = freq
        self.half_period_ms = int(1000 / (2 * freq))
        
    def update(self):
        """Simülasyon her adımında çağrılır - otomatik toggle"""
        # Simülasyon çalışıyorsa otomatik toggle
        import time
        current_time = int(time.time() * 1000)  # ms cinsinden
        
        if current_time - self.last_toggle_time >= self.half_period_ms:
            self.state = not self.state
            self.tick_count += 1
            self.last_toggle_time = current_time
        
        self.output_pins[0].set_value(self.state)
        
    def reset(self):
        """Clock'u sıfırla"""
        super().reset()
        self.state = False
        self.tick_count = 0
        self.last_toggle_time = 0


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
        self.update()
        
    def update(self):
        """Çıkış pinini güncelle"""
        try:
            if len(self.output_pins) > 0:
                self.output_pins[0].set_value(bool(self.state))
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
        
    def update(self):
        """Output pin - giriş sinyalini oku (görselleştirme için)"""
        # Giriş değerini oku ama hiçbir şey yapma
        try:
            if len(self.input_pins) > 0:
                _ = self.input_pins[0].value
        except (IndexError, AttributeError):
            pass
    
    def set_custom_name(self, name):
        """Özel isim ata"""
        self.custom_name = name
        self.name = name
