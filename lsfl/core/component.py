"""
Temel bileşen sınıfı
"""

from PyQt6.QtCore import QPoint


class Pin:
    def __init__(self, name, component, is_input=True):
        self.name = name
        self.component = component
        self.is_input = is_input
        self.value = False
        self.connected_wires = []
        
    def get_position(self):
        """Pin'in ekrandaki konumunu hesapla"""
        if self.is_input:
            # Giriş pinleri sol tarafta
            index = self.component.input_pins.index(self)
            y = self.component.y + (index + 1) * self.component.height // (len(self.component.input_pins) + 1)
            return QPoint(self.component.x, y)
        else:
            # Çıkış pinleri sağ tarafta
            index = self.component.output_pins.index(self)
            y = self.component.y + (index + 1) * self.component.height // (len(self.component.output_pins) + 1)
            return QPoint(self.component.x + self.component.width, y)
            
    def set_value(self, value):
        self.value = bool(value)
        # Bağlı kabloları güncelle
        for wire in self.connected_wires:
            wire.update()


class Component:
    def __init__(self, name, x=0, y=0, width=100, height=60):
        self.name = name
        self.type = "GENERIC"
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.input_pins = []
        self.output_pins = []
        
    def add_input_pin(self, name):
        pin = Pin(name, self, is_input=True)
        self.input_pins.append(pin)
        return pin
        
    def add_output_pin(self, name):
        pin = Pin(name, self, is_input=False)
        self.output_pins.append(pin)
        return pin
        
    def get_position(self):
        return QPoint(self.x, self.y)
        
    def move(self, x, y):
        self.x = x
        self.y = y
        
    def update(self):
        """Bileşen mantığını çalıştır - alt sınıflarda override edilecek"""
        pass
        
    def reset(self):
        """Bileşeni sıfırla"""
        for pin in self.input_pins + self.output_pins:
            pin.value = False
            
    def to_dict(self):
        """Bileşeni dictionary'ye çevir (kaydetmek için)"""
        return {
            'type': self.type,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
        
    @staticmethod
    def from_dict(data):
        """Dictionary'den bileşen oluştur"""
        comp = Component(data['name'], data['x'], data['y'], data['width'], data['height'])
        comp.type = data['type']
        return comp
