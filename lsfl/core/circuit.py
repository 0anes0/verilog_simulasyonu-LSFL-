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
        
    def add_component(self, component):
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
        # Clock bileşenlerini başlat
        for component in self.components:
            if component.type == "CLOCK":
                component.start()
        # İlk durumu hesapla
        self.step()
        # Timer'ı başlat
        if self.simulation_timer is None:
            self.simulation_timer = QTimer()
            self.simulation_timer.timeout.connect(self.step)
        self.simulation_timer.start(100)  # 10 Hz
        
    def stop_simulation(self):
        self.is_running = False
        if self.simulation_timer:
            self.simulation_timer.stop()
        # Clock bileşenlerini durdur
        for component in self.components:
            if component.type == "CLOCK":
                component.stop()
            
    def step(self):
        """Bir simülasyon adımı çalıştır"""
        # Çoklu geçiş ile sinyallerin yayılmasını sağla
        # (kombinasyonel devreler için gerekli)
        max_iterations = 10
        
        for iteration in range(max_iterations):
            # Önce tüm kabloları güncelle
            for wire in self.wires:
                wire.update()
            
            # Sonra tüm bileşenleri güncelle
            for component in self.components:
                component.update()
            
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
