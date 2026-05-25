"""
Giriş/Çıkış bileşenleri
"""

from core.component import Component
from PyQt6.QtCore import QTimer


class Switch(Component):
    def __init__(self, x=0, y=0):
        super().__init__("Switch", x, y, 60, 40)
        self.type = "SWITCH"
        self.add_output_pin("Out")
        self.state = False
        
    def toggle(self):
        self.state = not self.state
        self.update()
        
    def update(self):
        self.output_pins[0].set_value(self.state)


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
        super().__init__("Clock", x, y, 70, 50)
        self.type = "CLOCK"
        self.add_output_pin("CLK")
        
        self.state = False
        self.timer = None
        self.frequency = 2  # Hz (daha yavaş, gözlemlenebilir)
        self.tick_count = 0
        
    def start(self):
        """Clock'u başlat"""
        if self.timer is None:
            self.timer = QTimer()
            self.timer.timeout.connect(self.toggle)
        self.timer.start(int(1000 / (2 * self.frequency)))
        
    def stop(self):
        """Clock'u durdur"""
        if self.timer:
            self.timer.stop()
        
    def toggle(self):
        """Clock sinyalini değiştir"""
        self.state = not self.state
        self.tick_count += 1
        self.update()
        
    def update(self):
        """Çıkış pinini güncelle"""
        self.output_pins[0].set_value(self.state)
        
    def reset(self):
        """Clock'u sıfırla"""
        super().reset()
        self.state = False
        self.tick_count = 0
        self.stop()


class InputPin(Component):
    def __init__(self, x=0, y=0):
        super().__init__("INPUT", x, y, 70, 40)
        self.type = "INPUT_PIN"
        self.add_output_pin("Out")
        self.state = False
        
    def toggle(self):
        self.state = not self.state
        self.update()
        
    def update(self):
        self.output_pins[0].set_value(self.state)


class OutputPin(Component):
    def __init__(self, x=0, y=0):
        super().__init__("OUTPUT", x, y, 70, 40)
        self.type = "OUTPUT_PIN"
        self.add_input_pin("In")
        
    def update(self):
        # Output sadece görselleştirme için
        pass
