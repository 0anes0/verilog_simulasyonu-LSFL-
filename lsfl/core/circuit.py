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
        self.junctions = []  # Düğüm noktaları (Junction points) - QPoint listesi
        self.junction_connections = {}  # Junction -> Wire listesi mapping
        self.is_running = False
        self.simulation_timer = None
        self.filename = None
        # Otomatik isimlendirme için sayaçlar
        self.component_counters = {}
        # ID Recycling: Boşalan ID'leri geri kazanma (Min-Heap benzeri)
        self.available_ids = {}  # {component_type: set of available IDs}
        # ID Recycling: Boşalan ID'leri geri kazanma (Min-Heap benzeri)
        self.available_ids = {}  # {component_type: set of available IDs}
        
    def add_component(self, component):
        """Bileşen ekle ve otomatik isim ver - ID Recycling ile"""
        comp_type = component.type
        
        # ID Recycling: Önce boşta ID var mı kontrol et
        if comp_type in self.available_ids and self.available_ids[comp_type]:
            # En küçük boşta ID'yi al (sorted set'ten min)
            component_id = min(self.available_ids[comp_type])
            self.available_ids[comp_type].remove(component_id)
        else:
            # Boşta ID yok, sayaç artır
            if comp_type not in self.component_counters:
                self.component_counters[comp_type] = 0
            self.component_counters[comp_type] += 1
            component_id = self.component_counters[comp_type]
        
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
        
        component.name = f"{type_prefix}_{component_id}"
        self.components.append(component)
        
    def remove_component(self, component):
        if component in self.components:
            # Kabloları SİLME, sadece bağlantıları kes (floating state)
            for wire in self.wires:
                for pin in component.input_pins + component.output_pins:
                    wire.disconnect_pin(pin)
            
            # ID Recycling: Silinen bileşenin ID'sini havuza geri koy
            comp_type = component.type
            # İsimden ID'yi çıkar (örn: "AND_5" -> 5)
            try:
                component_id = int(component.name.split('_')[-1])
                if comp_type not in self.available_ids:
                    self.available_ids[comp_type] = set()
                self.available_ids[comp_type].add(component_id)
            except (ValueError, IndexError):
                # İsim formatı standart değilse atla
                pass
            
            # Bileşeni kaldır
            self.components.remove(component)
            
    def add_wire(self, from_pin, to_pin):
        from core.wire import Wire
        
        # Aynı bağlantı var mı kontrol et
        for wire in self.wires:
            if wire.from_pin == from_pin and wire.to_pin == to_pin:
                return wire
                
        wire = Wire(from_pin, to_pin)
        self.wires.append(wire)
        return wire
    
    def add_junction(self, position, wire1, wire2):
        """İki kablo arasında junction (düğüm noktası) oluştur
        
        Args:
            position: QPoint - Junction noktasının koordinatı
            wire1: Wire - İlk kablo
            wire2: Wire - İkinci kablo (yeni çizilen)
        """
        from PyQt6.QtCore import QPoint
        
        # Junction noktasını ekle (eğer yoksa)
        junction_exists = False
        for existing_junction in self.junctions:
            if (existing_junction - position).manhattanLength() < 5:
                position = existing_junction  # Mevcut junction'ı kullan
                junction_exists = True
                break
        
        if not junction_exists:
            self.junctions.append(position)
        
        # Junction bağlantılarını kaydet
        if position not in self.junction_connections:
            self.junction_connections[position] = []
        
        if wire1 not in self.junction_connections[position]:
            self.junction_connections[position].append(wire1)
        if wire2 not in self.junction_connections[position]:
            self.junction_connections[position].append(wire2)
        
        # Wire2'nin vertex listesine junction noktasını ekle
        if hasattr(wire2, 'vertices'):
            # Junction noktasını en yakın konuma ekle
            if not wire2.vertices or (wire2.vertices[-1] - position).manhattanLength() > 5:
                wire2.vertices.append(position)
        
    def remove_wire(self, wire):
        if wire in self.wires:
            self.wires.remove(wire)
            
    def start_simulation(self):
        self.is_running = True
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
        """Bir simülasyon adımı çalıştır - Topological sort ile sinyal yayılımı"""
        # Çoklu geçiş ile tüm sinyallerin yayılmasını sağla
        max_iterations = 5
        
        for iteration in range(max_iterations):
            # 1. Tüm bileşenlerin mantığını çalıştır
            for component in self.components:
                try:
                    component.update()
                except Exception as e:
                    if iteration == 0:  # Sadece ilk iterasyonda hata göster
                        print(f"Bileşen güncelleme hatası {component.name}: {e}")
            
            # 2. Kabloları güncelle (sinyal yayılımı)
            for wire in self.wires:
                try:
                    wire.update()
                except Exception as e:
                    if iteration == 0:
                        print(f"Kablo güncelleme hatası: {e}")
            
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
        self.junctions = []
        self.junction_connections = {}
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
