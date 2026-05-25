"""
Devre çizim alanı - sürükle-bırak, zoom, pan özellikleri ile
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QWheelEvent, QMouseEvent, QPainterPath, QPolygonF

from core.component import Component
from core.wire import Wire


class Canvas(QWidget):
    def __init__(self, circuit, main_window=None):
        super().__init__()
        self.circuit = circuit
        self.main_window = main_window
        # Daha büyük çalışma alanı
        self.setFixedSize(3000, 3000)
        self.setMouseTracking(True)
        
        # Görünüm ayarları
        self.zoom = 1.0
        self.offset = QPoint(0, 0)
        self.grid_size = 20
        self.show_grid = True
        
        # Etkileşim durumu
        self.dragging_component = None
        self.selected_components = []
        self.connecting_from = None  # Kablo bağlantısı için
        self.temp_wire_end = None
        self.panning = False
        self.pan_start = None
        
        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        
        self.setStyleSheet("background-color: #2b2b2b;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Zoom ve offset uygula
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)
        
        # Grid çiz
        if self.show_grid:
            self.draw_grid(painter)
        
        # Kabloları çiz
        for wire in self.circuit.wires:
            self.draw_wire(painter, wire)
            
        # Geçici kablo çiz (bağlantı yapılırken)
        if self.connecting_from and self.temp_wire_end:
            self.draw_temp_wire(painter)
        
        # Bileşenleri çiz
        for component in self.circuit.components:
            self.draw_component(painter, component)
            
    def draw_grid(self, painter):
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        
        width = self.width()
        height = self.height()
        
        # Dikey çizgiler
        x = 0
        while x < width:
            painter.drawLine(x, 0, x, height)
            x += self.grid_size
            
        # Yatay çizgiler
        y = 0
        while y < height:
            painter.drawLine(0, y, width, y)
            y += self.grid_size
            
    def draw_component(self, painter, component):
        # Özel bileşen çizimleri
        if component.type == "SWITCH":
            self.draw_switch(painter, component)
            return
        elif component.type == "LED":
            self.draw_led(painter, component)
            return
        elif component.type == "INPUT_PIN":
            self.draw_input_pin(painter, component)
            return
        elif component.type == "OUTPUT_PIN":
            self.draw_output_pin(painter, component)
            return
        elif component.type in ["AND", "OR", "NAND", "NOR", "XOR", "XNOR"]:
            self.draw_logic_gate(painter, component)
            return
        elif component.type == "NOT":
            self.draw_not_gate(painter, component)
            return
        elif component.type == "BUFFER":
            self.draw_buffer_gate(painter, component)
            return
            
        # Seçili bileşenleri vurgula
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
            painter.setBrush(QBrush(QColor(50, 50, 80)))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # Bileşen dikdörtgeni
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # Bileşen adı
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, component.name)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_switch(self, painter, component):
        """Switch bileşenini özel çiz"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Switch durumuna göre renk
        if component.state:
            painter.setBrush(QBrush(QColor(100, 200, 100)))
        else:
            painter.setBrush(QBrush(QColor(80, 80, 80)))
        
        painter.drawRoundedRect(rect, 5, 5)
        
        # Switch metni
        painter.setPen(QPen(QColor(255, 255, 255)))
        status = "ON" if component.state else "OFF"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"Switch\n{status}")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_led(self, painter, component):
        """LED bileşenini özel çiz"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # LED durumuna göre renk
        if len(component.input_pins) > 0 and component.input_pins[0].value:
            painter.setBrush(QBrush(QColor(255, 100, 100)))
        else:
            painter.setBrush(QBrush(QColor(60, 30, 30)))
        
        # Daire şeklinde LED
        center = rect.center()
        radius = min(component.width, component.height) // 2 - 5
        painter.drawEllipse(center, radius, radius)
        
        # LED metni
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "LED")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_logic_gate(self, painter, component):
        """IEEE standart mantık kapısı çiz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # IEEE standart dikdörtgen şekil
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # Kapı sembolü
        painter.setPen(QPen(QColor(255, 255, 255)))
        symbol = ""
        if component.type == "AND":
            symbol = "&"
        elif component.type == "OR":
            symbol = "≥1"
        elif component.type == "NAND":
            symbol = "&"
        elif component.type == "NOR":
            symbol = "≥1"
        elif component.type == "XOR":
            symbol = "=1"
        elif component.type == "XNOR":
            symbol = "=1"
        
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)
        
        # NAND, NOR, XNOR için çıkışta inverter balonu
        if component.type in ["NAND", "NOR", "XNOR"]:
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            bubble_x = component.x + component.width
            bubble_y = component.y + component.height // 2
            painter.drawEllipse(QPoint(bubble_x, bubble_y), 4, 4)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_not_gate(self, painter, component):
        """IEEE standart NOT kapısı çiz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # IEEE standart dikdörtgen
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # "1" sembolü
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "1")
        
        # Çıkışta inverter balonu
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        bubble_x = component.x + component.width
        bubble_y = component.y + component.height // 2
        painter.drawEllipse(QPoint(bubble_x, bubble_y), 4, 4)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_buffer_gate(self, painter, component):
        """IEEE standart Buffer çiz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # IEEE standart dikdörtgen
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # "1" sembolü
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "1")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_input_pin(self, painter, component):
        """Input Pin çiz"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Durum rengine göre
        if component.state:
            painter.setBrush(QBrush(QColor(100, 200, 100)))
        else:
            painter.setBrush(QBrush(QColor(80, 80, 80)))
        
        # Üçgen şekli (sağa bakan ok)
        points = [
            QPoint(component.x, component.y),
            QPoint(component.x, component.y + component.height),
            QPoint(component.x + component.width, component.y + component.height // 2)
        ]
        painter.drawPolygon(QPolygonF(points))
        
        # Metin
        painter.setPen(QPen(QColor(255, 255, 255)))
        status = "1" if component.state else "0"
        text_rect = QRect(component.x, component.y, component.width - 10, component.height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_output_pin(self, painter, component):
        """Output Pin çiz"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Durum rengine göre
        is_on = len(component.input_pins) > 0 and component.input_pins[0].value
        if is_on:
            painter.setBrush(QBrush(QColor(100, 200, 100)))
        else:
            painter.setBrush(QBrush(QColor(80, 80, 80)))
        
        # Üçgen şekli (sola bakan ok)
        points = [
            QPoint(component.x + component.width, component.y),
            QPoint(component.x + component.width, component.y + component.height),
            QPoint(component.x, component.y + component.height // 2)
        ]
        painter.drawPolygon(QPolygonF(points))
        
        # Metin
        painter.setPen(QPen(QColor(255, 255, 255)))
        status = "1" if is_on else "0"
        text_rect = QRect(component.x + 10, component.y, component.width - 10, component.height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
        
    def draw_pins(self, painter, component):
        pin_radius = 6  # Biraz daha büyük pinler
        
        # Giriş pinleri (sol taraf)
        for i, pin in enumerate(component.input_pins):
            y = component.y + (i + 1) * component.height // (len(component.input_pins) + 1)
            
            # Pin durumuna göre renk
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
                painter.setPen(QPen(QColor(50, 200, 50), 2))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.setPen(QPen(QColor(150, 150, 150), 2))
                
            painter.drawEllipse(QPoint(component.x, y), pin_radius, pin_radius)
            
            # Pin etiketi - daha iyi konumlandırma
            painter.setPen(QPen(QColor(220, 220, 220)))
            painter.drawText(component.x + 12, y + 4, pin.name)
        
        # Çıkış pinleri (sağ taraf)
        for i, pin in enumerate(component.output_pins):
            y = component.y + (i + 1) * component.height // (len(component.output_pins) + 1)
            
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
                painter.setPen(QPen(QColor(50, 200, 50), 2))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.setPen(QPen(QColor(150, 150, 150), 2))
                
            painter.drawEllipse(QPoint(component.x + component.width, y), pin_radius, pin_radius)
            
            # Pin etiketi - sağa hizalı
            painter.setPen(QPen(QColor(220, 220, 220)))
            text_width = painter.fontMetrics().horizontalAdvance(pin.name)
            painter.drawText(component.x + component.width - text_width - 12, y + 4, pin.name)
            
    def draw_wire(self, painter, wire):
        # Kablo değerine göre renk
        if wire.value:
            painter.setPen(QPen(QColor(100, 255, 100), 3))
        else:
            painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        # Başlangıç ve bitiş noktaları
        start = wire.from_pin.get_position()
        end = wire.to_pin.get_position()
        
        # Proteus tarzı ortogonal kablo yönlendirmesi
        # Yatay mesafe
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # Minimum segment uzunluğu
        min_segment = 30
        
        if abs(dx) > abs(dy):
            # Yatay öncelikli
            mid_x = start.x() + dx // 2
            
            # İlk yatay segment
            painter.drawLine(start.x(), start.y(), mid_x, start.y())
            # Dikey segment
            painter.drawLine(mid_x, start.y(), mid_x, end.y())
            # Son yatay segment
            painter.drawLine(mid_x, end.y(), end.x(), end.y())
        else:
            # Dikey öncelikli
            mid_y = start.y() + dy // 2
            
            # İlk dikey segment
            painter.drawLine(start.x(), start.y(), start.x(), mid_y)
            # Yatay segment
            painter.drawLine(start.x(), mid_y, end.x(), mid_y)
            # Son dikey segment
            painter.drawLine(end.x(), mid_y, end.x(), end.y())
        
    def draw_temp_wire(self, painter):
        painter.setPen(QPen(QColor(150, 150, 255), 2, Qt.PenStyle.DashLine))
        start = self.connecting_from.get_position()
        end = self.temp_wire_end
        
        # Proteus tarzı geçici kablo çizimi
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        if abs(dx) > abs(dy):
            # Yatay öncelikli
            mid_x = start.x() + dx // 2
            painter.drawLine(start.x(), start.y(), mid_x, start.y())
            painter.drawLine(mid_x, start.y(), mid_x, end.y())
            painter.drawLine(mid_x, end.y(), end.x(), end.y())
        else:
            # Dikey öncelikli
            mid_y = start.y() + dy // 2
            painter.drawLine(start.x(), start.y(), start.x(), mid_y)
            painter.drawLine(start.x(), mid_y, end.x(), mid_y)
            painter.drawLine(end.x(), mid_y, end.x(), end.y())
        
    def mousePressEvent(self, event: QMouseEvent):
        # Zoom ve offset'i hesaba kat
        pos = self.map_to_canvas(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Pin tıklaması kontrolü (kablo bağlantısı için)
            pin = self.get_pin_at(pos)
            if pin:
                if self.connecting_from is None:
                    # Kablo bağlantısı başlat - her pin'den başlayabilir
                    self.connecting_from = pin
                    self.temp_wire_end = pos
                else:
                    # Kablo bağlantısını tamamla
                    # Aynı pin değilse ve uygun yönde ise bağla
                    if pin != self.connecting_from:
                        # Çıkış -> Giriş veya Giriş -> Çıkış
                        if self.connecting_from.is_input != pin.is_input:
                            # Doğru yönde bağlantı yap (her zaman çıkış -> giriş)
                            if self.connecting_from.is_input:
                                self.circuit.add_wire(pin, self.connecting_from)
                            else:
                                self.circuit.add_wire(self.connecting_from, pin)
                        self.connecting_from = None
                        self.temp_wire_end = None
                        self.update()
                    else:
                        # Aynı pin, iptal et
                        self.connecting_from = None
                        self.temp_wire_end = None
                        self.update()
                return
            
            # Bileşen seçimi
            component = self.get_component_at(pos)
            if component:
                # Switch ve INPUT_PIN bileşenine tıklama - toggle
                if component.type in ["SWITCH", "INPUT_PIN"]:
                    component.toggle()
                    self.update()
                    return
                    
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Ctrl ile çoklu seçim
                    if component in self.selected_components:
                        self.selected_components.remove(component)
                    else:
                        self.selected_components.append(component)
                else:
                    self.selected_components = [component]
                    self.dragging_component = component
                self.update()
            else:
                self.selected_components = []
                self.update()
                
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Pan başlat
            self.panning = True
            self.pan_start = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        elif event.button() == Qt.MouseButton.RightButton:
            # Kablo bağlantısını iptal et
            if self.connecting_from:
                self.connecting_from = None
                self.temp_wire_end = None
                self.update()
                
    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.map_to_canvas(event.pos())
        
        if self.dragging_component and self.selected_components:
            # Bileşenleri sürükle
            delta = pos - self.dragging_component.get_position()
            for comp in self.selected_components:
                comp.move(comp.x + delta.x(), comp.y + delta.y())
            self.update()
            
        elif self.panning and self.pan_start:
            # Pan
            delta = event.pos() - self.pan_start
            self.offset += delta
            self.pan_start = event.pos()
            self.update()
            
        elif self.connecting_from:
            # Geçici kablo ucunu güncelle
            self.temp_wire_end = pos
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_component = None
            
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def wheelEvent(self, event: QWheelEvent):
        # Zoom (Ctrl tuşu ile)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            zoom_factor = 1.1 if delta > 0 else 0.9
            
            # Mouse pozisyonunu merkez al
            old_pos = event.position()
            
            self.zoom *= zoom_factor
            self.zoom = max(0.3, min(3.0, self.zoom))
            
            # Status bar'ı güncelle
            if self.main_window:
                self.main_window.statusBar.showMessage(f"Zoom: {self.zoom:.0%}")
            
            self.update()
        else:
            # Normal scroll - kaydırma
            super().wheelEvent(event)
        
    def get_component_at(self, pos):
        for component in reversed(self.circuit.components):
            rect = QRect(component.x, component.y, component.width, component.height)
            if rect.contains(pos):
                return component
        return None
        
    def map_to_canvas(self, screen_pos):
        """Ekran koordinatlarını canvas koordinatlarına çevir"""
        # Offset ve zoom'u tersine uygula
        x = (screen_pos.x() - self.offset.x()) / self.zoom
        y = (screen_pos.y() - self.offset.y()) / self.zoom
        return QPoint(int(x), int(y))
    
    def get_pin_at(self, pos):
        pin_radius = 15  # Çok daha büyük tıklama alanı
        for component in self.circuit.components:
            for pin in component.input_pins + component.output_pins:
                pin_pos = pin.get_position()
                distance = (pos - pin_pos).manhattanLength()
                if distance < pin_radius:
                    return pin
        return None
        
    def add_component(self, component_type, pos):
        """Yeni bileşen ekle"""
        from core.component_factory import ComponentFactory
        component = ComponentFactory.create(component_type, pos.x(), pos.y())
        self.circuit.add_component(component)
        self.update()
        
    def delete_selected(self):
        for component in self.selected_components:
            self.circuit.remove_component(component)
        self.selected_components = []
        self.update()
        
    def select_all(self):
        self.selected_components = self.circuit.components.copy()
        self.update()
        
    def undo(self):
        # TODO: Implement undo
        pass
        
    def redo(self):
        # TODO: Implement redo
        pass
        
    def clear(self):
        self.selected_components = []
        self.connecting_from = None
        self.temp_wire_end = None
        self.update()
        
    def load_circuit(self):
        self.clear()
        self.update()
        
    def export_png(self, filename):
        pixmap = self.grab()
        pixmap.save(filename)
