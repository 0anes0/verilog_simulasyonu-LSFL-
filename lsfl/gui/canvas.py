"""
Devre çizim alanı - sürükle-bırak, zoom, pan özellikleri ile
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QWheelEvent, QMouseEvent

from core.component import Component
from core.wire import Wire


class Canvas(QWidget):
    def __init__(self, circuit):
        super().__init__()
        self.circuit = circuit
        self.setMinimumSize(2000, 2000)
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
        
    def draw_pins(self, painter, component):
        pin_radius = 5
        
        # Giriş pinleri (sol taraf)
        for i, pin in enumerate(component.input_pins):
            y = component.y + (i + 1) * component.height // (len(component.input_pins) + 1)
            
            # Pin durumuna göre renk
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.drawEllipse(QPoint(component.x, y), pin_radius, pin_radius)
            
            # Pin etiketi
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(component.x + 10, y + 5, pin.name)
        
        # Çıkış pinleri (sağ taraf)
        for i, pin in enumerate(component.output_pins):
            y = component.y + (i + 1) * component.height // (len(component.output_pins) + 1)
            
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.drawEllipse(QPoint(component.x + component.width, y), pin_radius, pin_radius)
            
            # Pin etiketi
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(component.x + component.width - 30, y + 5, pin.name)
            
    def draw_wire(self, painter, wire):
        # Kablo değerine göre renk
        if wire.value:
            painter.setPen(QPen(QColor(100, 255, 100), 3))
        else:
            painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        # Başlangıç ve bitiş noktaları
        start = wire.from_pin.get_position()
        end = wire.to_pin.get_position()
        
        # Manhattan yönlendirme (dik açılı kablolar)
        mid_x = (start.x() + end.x()) // 2
        
        painter.drawLine(start.x(), start.y(), mid_x, start.y())
        painter.drawLine(mid_x, start.y(), mid_x, end.y())
        painter.drawLine(mid_x, end.y(), end.x(), end.y())
        
    def draw_temp_wire(self, painter):
        painter.setPen(QPen(QColor(150, 150, 255), 2, Qt.PenStyle.DashLine))
        start = self.connecting_from.get_position()
        painter.drawLine(start, self.temp_wire_end)
        
    def mousePressEvent(self, event: QMouseEvent):
        pos = event.pos()
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Pin tıklaması kontrolü (kablo bağlantısı için)
            pin = self.get_pin_at(pos)
            if pin:
                if self.connecting_from is None:
                    # Kablo bağlantısı başlat
                    self.connecting_from = pin
                    self.temp_wire_end = pos
                else:
                    # Kablo bağlantısını tamamla
                    self.circuit.add_wire(self.connecting_from, pin)
                    self.connecting_from = None
                    self.temp_wire_end = None
                    self.update()
                return
            
            # Bileşen seçimi
            component = self.get_component_at(pos)
            if component:
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
        pos = event.pos()
        
        if self.dragging_component and self.selected_components:
            # Bileşenleri sürükle
            delta = pos - self.dragging_component.get_position()
            for comp in self.selected_components:
                comp.move(comp.x + delta.x(), comp.y + delta.y())
            self.update()
            
        elif self.panning and self.pan_start:
            # Pan
            delta = pos - self.pan_start
            self.offset += delta
            self.pan_start = pos
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
        # Zoom
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.zoom = max(0.1, min(5.0, self.zoom))
        self.update()
        
    def get_component_at(self, pos):
        for component in reversed(self.circuit.components):
            rect = QRect(component.x, component.y, component.width, component.height)
            if rect.contains(pos):
                return component
        return None
        
    def get_pin_at(self, pos):
        pin_radius = 5
        for component in self.circuit.components:
            for pin in component.input_pins + component.output_pins:
                pin_pos = pin.get_position()
                if (pos - pin_pos).manhattanLength() < pin_radius * 2:
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
