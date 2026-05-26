"""
Devre modeli - bileşenler ve kablolar
"""

import json
from typing import List
from PyQt6.QtCore import QTimer


class Circuit:
    def __init__(self):
        self.components = []
        self.wires = []
        self.is_running = False
        self.simulation_timer = None
        self.filename = None
        # Otomatik isimlendirme için sayaçlar
        self.component_counters = {}
        
    def add_component(self, component):
        """Bileşen ekle ve otomatik isim ver"""
        # Otomatik eşsiz isim oluştur
        comp_type = component.type
        if comp_type not in self.component_counters:
            self.component_counters[comp_type] = 0
        
        self.component_counters[comp_type] += 1
        
        # Kısa isim formatı
        type_prefix = {
            'INPUT_PIN': 'IN',
            'OUTPUT_PIN': 'OUT',
            'SWITCH': 'SW',
            'LED': 'LED',
            'CLOCK': 'CLK',
            'AND': 'AND',
            'OR': 'OR',
            'NOT': 'NOT',
            'NAND': 'NAND',
            'NOR': 'NOR',
            'XOR': 'XOR',
            'XNOR': 'XNOR',
        }.get(comp_type, comp_type[:3].upper())
        
        component.name = f"{type_prefix}_{self.component_counters[comp_type]}"
        self.components.append(component)
        
    def remove_component(self, component):
        if component in self.components:
            # İlgili kabloları da sil
            self.wires = [w for w in self.wires 
                         if w.from_pin.component != component and 
                            w.to_pin.component != component]
            self.components.remove(component)
            
    def add_wire(self, from_pin, to_pin):
        from core.wire import Wire
        
        # Aynı bağlantı var mı kontrol et
        for wire in self.wires:
            if wire.from_pin == from_pin and wire.to_pin == to_pin:
                return
                
        wire = Wire(from_pin, to_pin)
        self.wires.append(wire)
        
    def remove_wire(self, wire):
        if wire in self.wires:
            self.wires.remove(wire)
            
    def start_simulation(self):
        self.is_running = True
        # Clock bileşenlerini sıfırla
        import time
        current_time = int(time.time() * 1000)
        for component in self.components:
            if component.type == "CLOCK":
                component.last_toggle_time = current_time
        # İlk durumu hesapla
        self.step()
        # Timer'ı başlat - daha hızlı güncelleme için 50ms
        if self.simulation_timer is None:
            self.simulation_timer = QTimer()
            self.simulation_timer.timeout.connect(self.step)
        self.simulation_timer.start(50)  # 20 Hz güncelleme
        
    def stop_simulation(self):
        self.is_running = False
        if self.simulation_timer:
            self.simulation_timer.stop()
            
    def step(self):
        """Bir simülasyon adımı çalıştır - Doğru sinyal yayılımı"""
        # 1. Önce tüm bileşenlerin mantığını çalıştır
        for component in self.components:
            try:
                component.update()
            except Exception as e:
                print(f"Bileşen güncelleme hatası {component.name}: {e}")
        
        # 2. Kabloları güncelle (sinyal yayılımı)
        for wire in self.wires:
            try:
                wire.update()
            except Exception as e:
                print(f"Kablo güncelleme hatası: {e}")
        
        # 3. Kombinasyonel devreler için ikinci geçiş
        for component in self.components:
            try:
                component.update()
            except Exception as e:
                pass
            
    def reset(self):
        """Simülasyonu sıfırla"""
        for component in self.components:
            component.reset()
        for wire in self.wires:
            wire.reset()
            
    def clear(self):
        """Devreyi temizle"""
        self.components = []
        self.wires = []
        self.stop_simulation()
        
    def save(self, filename):
        """Devreyi dosyaya kaydet"""
        data = {
            'components': [comp.to_dict() for comp in self.components],
            'wires': [wire.to_dict() for wire in self.wires]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
    def load(self, filename):
        """Devreyi dosyadan yükle"""
        with open(filename, 'r') as f:
            data = json.load(f)
            
        self.clear()
        
        # Bileşenleri yükle
        from core.component_factory import ComponentFactory
        for comp_data in data['components']:
            comp = ComponentFactory.from_dict(comp_data)
            self.components.append(comp)
            
        # Kabloları yükle
        from core.wire import Wire
        for wire_data in data['wires']:
            wire = Wire.from_dict(wire_data, self.components)
            self.wires.append(wire)
            
        self.filename = filename
