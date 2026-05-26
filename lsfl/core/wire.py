"""
Kablo bağlantısı
"""


class Wire:
    def __init__(self, from_pin, to_pin=None):
        self.from_pin = from_pin
        self.to_pin = to_pin  # None olabilir (floating/dangling state)
        self.value = False
        self.vertices = []  # Kablo köşe noktaları (Proteus-style routing)
        self.is_floating = (to_pin is None)  # Floating state flag
        
        # Pin'lere kabloyu ekle
        if from_pin:
            from_pin.connected_wires.append(self)
        if to_pin:
            to_pin.connected_wires.append(self)
        
    def update(self):
        """Kablo değerini güncelle ve hedef pin'e yaz - senkronize"""
        # Kaynak pin'den değeri al
        if self.from_pin:
            self.value = bool(self.from_pin.value)
        # Hedef pin'e değeri doğrudan yaz (eğer bağlıysa)
        if self.to_pin:
            self.to_pin.value = self.value
    
    def disconnect_pin(self, pin):
        """Bir pin'i kabloden ayır (bileşen silindiğinde)"""
        if self.from_pin == pin:
            self.from_pin = None
            self.is_floating = True
        if self.to_pin == pin:
            self.to_pin = None
            self.is_floating = True
    
    def is_valid(self):
        """Kablo en az bir uca bağlı mı?"""
        return self.from_pin is not None or self.to_pin is not None
        
    def reset(self):
        self.value = False
        
    def to_dict(self):
        """Kabloyu dictionary'ye çevir"""
        return {
            'from_component': self.from_pin.component.name,
            'from_pin': self.from_pin.name,
            'to_component': self.to_pin.component.name,
            'to_pin': self.to_pin.name
        }
        
    @staticmethod
    def from_dict(data, components):
        """Dictionary'den kablo oluştur"""
        # Bileşenleri bul
        from_comp = next(c for c in components if c.name == data['from_component'])
        to_comp = next(c for c in components if c.name == data['to_component'])
        
        # Pin'leri bul
        from_pin = next(p for p in from_comp.output_pins if p.name == data['from_pin'])
        to_pin = next(p for p in to_comp.input_pins if p.name == data['to_pin'])
        
        return Wire(from_pin, to_pin)
