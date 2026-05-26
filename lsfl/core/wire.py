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
        self.junction_node = None  # Junction düğümü (eğer bu kablo bir junction'a bağlıysa)
        
        # Pin'lere kabloyu ekle
        if from_pin:
            from_pin.connected_wires.append(self)
        if to_pin:
            to_pin.connected_wires.append(self)
    
    def split_at_point(self, split_point):
        """Kabloyu verilen noktada iki parçaya böl (Wire Splitting)
        
        Returns:
            tuple: (wire1, wire2, junction_index) - İki yeni kablo ve junction vertex index'i
        """
        from PyQt6.QtCore import QPoint
        
        # Kablonun tüm noktalarını al
        path_points = []
        if self.from_pin:
            path_points.append(self.from_pin.get_position())
        path_points.extend(self.vertices)
        if self.to_pin:
            path_points.append(self.to_pin.get_position())
        
        # Split noktasına en yakın segment'i bul
        min_distance = float('inf')
        split_segment_index = 0
        
        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]
            
            # Segment üzerinde en yakın nokta
            closest = self._closest_point_on_segment(split_point, p1, p2)
            distance = (closest - split_point).manhattanLength()
            
            if distance < min_distance:
                min_distance = distance
                split_segment_index = i
        
        # Kabloyu böl: vertices'i ikiye ayır
        # Wire 1: from_pin -> split_point
        # Wire 2: split_point -> to_pin
        
        wire1_vertices = self.vertices[:split_segment_index]
        wire1_vertices.append(split_point)
        
        wire2_vertices = [split_point]
        wire2_vertices.extend(self.vertices[split_segment_index + 1:])
        
        # Yeni kablolar oluştur
        wire1 = Wire(self.from_pin, None)
        wire1.vertices = wire1_vertices
        wire1.is_floating = True
        wire1.junction_node = split_point
        
        wire2 = Wire(None, self.to_pin)
        wire2.vertices = wire2_vertices
        wire2.is_floating = True
        wire2.junction_node = split_point
        
        return wire1, wire2, len(wire1_vertices) - 1
    
    def _closest_point_on_segment(self, point, seg_start, seg_end):
        """Segment üzerinde verilen noktaya en yakın noktayı bul"""
        from PyQt6.QtCore import QPoint
        
        # Orthogonal segment için basitleştirilmiş hesaplama
        if seg_start.x() == seg_end.x():  # Dikey segment
            y_clamped = max(min(point.y(), max(seg_start.y(), seg_end.y())), 
                           min(seg_start.y(), seg_end.y()))
            return QPoint(seg_start.x(), y_clamped)
        elif seg_start.y() == seg_end.y():  # Yatay segment
            x_clamped = max(min(point.x(), max(seg_start.x(), seg_end.x())), 
                           min(seg_start.x(), seg_end.x()))
            return QPoint(x_clamped, seg_start.y())
        else:
            # Diagonal (olmamalı ama fallback)
            return seg_start
        
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
