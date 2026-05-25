"""
Devre çizim alanı - sürükle-bırak, zoom, pan özellikleri ile
"""

from PyQt6.QtWidgets import QWidget, QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QWheelEvent, QMouseEvent, QPainterPath, QPolygonF, QKeyEvent

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
        
        # Kare seçim aracı
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        
        # Bileşen yerleştirme modu
        self.placing_component = None
        self.placing_component_type = None
        
        # Kablo köşe noktaları
        self.wire_waypoints = []
        
        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        
        self.setStyleSheet("background-color: #2b2b2b;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Simülasyon çalışıyorsa arka plan rengini değiştir (yeşilimsi)
        if self.circuit.is_running:
            painter.fillRect(self.rect(), QColor(35, 42, 35))
        else:
            # Durdurulduğunda normal koyu gri
            painter.fillRect(self.rect(), QColor(43, 43, 43))
        
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
        
        # Kare seçim alanını çiz
        if self.selecting and self.selection_start and self.selection_end:
            painter.setPen(QPen(QColor(100, 150, 255), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(100, 150, 255, 30)))
            rect = QRect(self.selection_start, self.selection_end).normalized()
            painter.drawRect(rect)
        
        # Yerleştirilecek bileşeni göster
        if self.placing_component:
            painter.setOpacity(0.5)
            self.draw_component(painter, self.placing_component)
            painter.setOpacity(1.0)
            
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
        
        # Bileşen adı (üstte, pinlerle çakışmayacak şekilde)
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        name_rect = QRect(component.x, component.y + 5, component.width, 20)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, component.name)
        
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
        """Mantık kapısı çiz - yazılı isimlerle"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # Dikdörtgen şekil
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # Kapı ismi (büyük ve net)
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, component.type)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_not_gate(self, painter, component):
        """NOT kapısı çiz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # Dikdörtgen
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # "NOT" yazısı
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "NOT")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_buffer_gate(self, painter, component):
        """Buffer çiz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # Dikdörtgen
        rect = QRect(component.x, component.y, component.width, component.height)
        painter.drawRect(rect)
        
        # "BUFFER" yazısı
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "BUF")
        
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
        
        # Dikdörtgen şekil
        painter.drawRoundedRect(rect, 5, 5)
        
        # İsim ve durum
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # İsim üstte
        name_rect = QRect(component.x, component.y + 5, component.width, component.height // 2)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, component.name)
        
        # Durum altta
        status = "1" if component.state else "0"
        status_rect = QRect(component.x, component.y + component.height // 2, component.width, component.height // 2 - 5)
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status)
        
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
        
        # Dikdörtgen şekil
        painter.drawRoundedRect(rect, 5, 5)
        
        # İsim ve durum
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # İsim üstte
        name_rect = QRect(component.x, component.y + 5, component.width, component.height // 2)
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, component.name)
        
        # Durum altta
        status = "1" if is_on else "0"
        status_rect = QRect(component.x, component.y + component.height // 2, component.width, component.height // 2 - 5)
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
        
    def draw_pins(self, painter, component):
        pin_radius = 6  # Biraz daha büyük pinler
        
        # Font ayarları
        font = painter.font()
        font.setPointSize(7)
        painter.setFont(font)
        
        # Giriş pinleri (sol taraf)
        for i, pin in enumerate(component.input_pins):
            # Pin pozisyonu - üstten ve alttan boşluk bırak
            y_offset = 25  # Üstten boşluk (isim için)
            available_height = component.height - y_offset - 10  # Alttan da boşluk
            if len(component.input_pins) > 1:
                y = component.y + y_offset + (i * available_height // (len(component.input_pins) - 1))
            else:
                y = component.y + component.height // 2
            
            # Pin durumuna göre renk
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
                painter.setPen(QPen(QColor(50, 200, 50), 2))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.setPen(QPen(QColor(150, 150, 150), 2))
                
            painter.drawEllipse(QPoint(component.x, y), pin_radius, pin_radius)
            
            # Pin etiketi - içeride
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(component.x + 10, y + 3, pin.name)
        
        # Çıkış pinleri (sağ taraf)
        for i, pin in enumerate(component.output_pins):
            # Pin pozisyonu
            y_offset = 25
            available_height = component.height - y_offset - 10
            if len(component.output_pins) > 1:
                y = component.y + y_offset + (i * available_height // (len(component.output_pins) - 1))
            else:
                y = component.y + component.height // 2
            
            if pin.value:
                painter.setBrush(QBrush(QColor(100, 255, 100)))
                painter.setPen(QPen(QColor(50, 200, 50), 2))
            else:
                painter.setBrush(QBrush(QColor(50, 50, 50)))
                painter.setPen(QPen(QColor(150, 150, 150), 2))
                
            painter.drawEllipse(QPoint(component.x + component.width, y), pin_radius, pin_radius)
            
            # Pin etiketi - içeride, sağa hizalı
            painter.setPen(QPen(QColor(200, 200, 200)))
            text_width = painter.fontMetrics().horizontalAdvance(pin.name)
            painter.drawText(component.x + component.width - text_width - 10, y + 3, pin.name)
            
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
        
        # Köşe noktaları varsa onları kullan
        if self.wire_waypoints:
            # İlk segment
            prev_point = start
            for waypoint in self.wire_waypoints:
                painter.drawLine(prev_point, waypoint)
                # Köşe noktasını işaretle
                painter.setBrush(QBrush(QColor(150, 150, 255)))
                painter.drawEllipse(waypoint, 3, 3)
                prev_point = waypoint
            
            # Son segment (mouse pozisyonuna)
            if self.temp_wire_end:
                painter.drawLine(prev_point, self.temp_wire_end)
        else:
            # Köşe noktası yoksa direkt çiz
            end = self.temp_wire_end
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
        # Simülasyon durdurulduğunda düzenlemeyi engelle (sadece input değiştirme)
        # Simülasyon çalışırken input değiştirme ve pan'e izin ver
        
        # Zoom ve offset'i hesaba kat
        pos = self.map_to_canvas(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Bileşen yerleştirme modu
            if self.placing_component:
                self.placing_component.move(pos.x() - self.placing_component.width // 2,
                                           pos.y() - self.placing_component.height // 2)
                self.circuit.add_component(self.placing_component)
                self.placing_component = None
                self.placing_component_type = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update()
                return
            
            # Pin tıklaması kontrolü (kablo bağlantısı için)
            pin = self.get_pin_at(pos)
            if pin:
                if self.connecting_from is None:
                    # Kablo bağlantısı başlat - her pin'den başlayabilir
                    self.connecting_from = pin
                    self.temp_wire_end = pos
                    self.wire_waypoints = []
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
                        self.wire_waypoints = []
                        self.update()
                    else:
                        # Aynı pin, iptal et
                        self.connecting_from = None
                        self.temp_wire_end = None
                        self.wire_waypoints = []
                        self.update()
                return
            
            # Kablo çizimi sırasında boşluğa tıklama - köşe noktası ekle
            if self.connecting_from:
                self.wire_waypoints.append(pos)
                self.update()
                return
            
            # Bileşen seçimi
            component = self.get_component_at(pos)
            if component:
                # Çift tıklama kontrolü için - tek tıklamada sadece seçim/toggle
                # Switch ve INPUT_PIN bileşenine tıklama - toggle (SADECE simülasyon çalışırken)
                if component.type in ["SWITCH", "INPUT_PIN"] and self.circuit.is_running:
                    component.toggle()
                    self.update()
                    return
                
                # Simülasyon çalışırken düzenlemeyi engelle
                if self.circuit.is_running:
                    return
                    
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Ctrl ile çoklu seçim
                    if component in self.selected_components:
                        self.selected_components.remove(component)
                    else:
                        self.selected_components.append(component)
                else:
                    if component not in self.selected_components:
                        self.selected_components = [component]
                    self.dragging_component = component
                self.update()
            else:
                # Boş alana tıklama - kare seçim başlat
                self.selected_components = []
                self.selecting = True
                self.selection_start = pos
                self.selection_end = pos
                self.update()
                
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Pan başlat
            self.panning = True
            self.pan_start = event.pos()  # Ekran koordinatlarını kullan
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        elif event.button() == Qt.MouseButton.RightButton:
            # Kablo bağlantısını veya yerleştirmeyi iptal et
            if self.connecting_from:
                # Son köşe noktasını sil veya tamamen iptal et
                if self.wire_waypoints:
                    self.wire_waypoints.pop()
                else:
                    self.connecting_from = None
                    self.temp_wire_end = None
                self.update()
            elif self.placing_component:
                self.cancel_placing()
                
    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.map_to_canvas(event.pos())
        
        # Bileşen yerleştirme modu - önizleme
        if self.placing_component:
            self.placing_component.move(pos.x() - self.placing_component.width // 2,
                                       pos.y() - self.placing_component.height // 2)
            self.update()
            return
        
        # Simülasyon çalışırken düzenlemeyi engelle
        if self.circuit.is_running and not self.placing_component:
            return
        
        if self.dragging_component and self.selected_components:
            
            # Bileşenleri sürükle
            delta = pos - self.dragging_component.get_position()
            for comp in self.selected_components:
                comp.move(comp.x + delta.x(), comp.y + delta.y())
            self.update()
            
        elif self.selecting and self.selection_start:
            # Kare seçim alanını güncelle
            self.selection_end = pos
            self.update()
            
        elif self.panning and self.pan_start:
            # Pan - ekran koordinatlarıyla
            delta = event.pos() - self.pan_start
            new_offset = self.offset + delta
            
            # Canvas sınırlarını kontrol et (canvas dışına çıkmayı engelle)
            # Maksimum offset (sağ ve alt sınır)
            max_offset_x = 100  # Biraz boşluk bırak
            max_offset_y = 100
            
            # Minimum offset (sol ve üst sınır)
            # Parent widget'ın boyutunu al
            parent_widget = self.parent()
            if parent_widget:
                viewport_width = parent_widget.width() if hasattr(parent_widget, 'width') else 800
                viewport_height = parent_widget.height() if hasattr(parent_widget, 'height') else 600
            else:
                viewport_width = 800
                viewport_height = 600
            
            min_offset_x = -(self.width() - viewport_width + 100)
            min_offset_y = -(self.height() - viewport_height + 100)
            
            # Offset'i sınırla
            new_offset.setX(max(min_offset_x, min(max_offset_x, new_offset.x())))
            new_offset.setY(max(min_offset_y, min(max_offset_y, new_offset.y())))
            
            self.offset = new_offset
            self.pan_start = event.pos()
            self.update()
            
        elif self.connecting_from:
            # Geçici kablo ucunu güncelle
            self.temp_wire_end = pos
            self.update()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_component = None
            
            # Kare seçim tamamlandı
            if self.selecting and self.selection_start and self.selection_end:
                self.selecting = False
                # Seçim alanındaki bileşenleri bul
                selection_rect = QRect(self.selection_start, self.selection_end).normalized()
                self.selected_components = []
                for component in self.circuit.components:
                    comp_rect = QRect(component.x, component.y, component.width, component.height)
                    if selection_rect.intersects(comp_rect):
                        self.selected_components.append(component)
                self.selection_start = None
                self.selection_end = None
                self.update()
            
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.pan_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Çift tıklama - bileşen özelliklerini düzenle"""
        if self.circuit.is_running:
            return  # Simülasyon çalışırken özellik değiştirme
        
        pos = self.map_to_canvas(event.pos())
        component = self.get_component_at(pos)
        
        if component:
            self.show_component_properties(component)
            
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
            # Pan modundaysa scroll'u engelle
            if self.panning:
                event.ignore()
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
        
    def add_component(self, component_type, pos=None):
        """Yeni bileşen ekle - yerleştirme moduna geç"""
        from core.component_factory import ComponentFactory
        
        if pos:
            # Doğrudan pozisyonda oluştur (eski davranış)
            component = ComponentFactory.create(component_type, pos.x(), pos.y())
            self.circuit.add_component(component)
            self.update()
        else:
            # Yerleştirme moduna geç
            self.placing_component = ComponentFactory.create(component_type, 0, 0)
            self.placing_component_type = component_type
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.update()
    
    def start_placing_component(self, component_type):
        """Bileşen yerleştirme modunu başlat"""
        from core.component_factory import ComponentFactory
        self.placing_component = ComponentFactory.create(component_type, 0, 0)
        self.placing_component_type = component_type
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.update()
    
    def cancel_placing(self):
        """Bileşen yerleştirmeyi iptal et"""
        self.placing_component = None
        self.placing_component_type = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
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
        
    def keyPressEvent(self, event: QKeyEvent):
        """Klavye olaylarını işle"""
        if event.key() == Qt.Key.Key_Escape:
            # ESC ile yerleştirme veya kablo bağlantısını iptal et
            if self.placing_component:
                self.cancel_placing()
            elif self.connecting_from:
                self.connecting_from = None
                self.temp_wire_end = None
                self.wire_waypoints = []
                self.update()
            elif self.selected_components:
                self.selected_components = []
                self.update()
        elif event.key() == Qt.Key.Key_Delete:
            # Delete ile seçili bileşenleri sil
            if not self.circuit.is_running:
                self.delete_selected()
        elif event.key() == Qt.Key.Key_Home:
            # Home tuşu ile başlangıç pozisyonuna dön
            self.offset = QPoint(0, 0)
            self.zoom = 1.0
            if self.main_window:
                self.main_window.statusBar.showMessage("Canvas başlangıç pozisyonuna döndü")
            self.update()
        super().keyPressEvent(event)
    
    def show_component_properties(self, component):
        """Bileşen özelliklerini düzenle"""
        dialog = ComponentPropertiesDialog(component, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update()
    
    def export_png(self, filename):
        pixmap = self.grab()
        pixmap.save(filename)


class ComponentPropertiesDialog(QDialog):
    """Bileşen özellikleri düzenleme dialogu"""
    def __init__(self, component, parent=None):
        super().__init__(parent)
        self.component = component
        self.setWindowTitle(f"{component.type} Özellikleri")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # İsim
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("İsim:"))
        self.name_edit = QLineEdit(self.component.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Clock için frekans ayarı
        if self.component.type == "CLOCK":
            freq_layout = QHBoxLayout()
            freq_layout.addWidget(QLabel("Frekans (Hz):"))
            self.freq_spin = QDoubleSpinBox()
            self.freq_spin.setRange(0.1, 10.0)
            self.freq_spin.setValue(self.component.frequency)
            self.freq_spin.setSingleStep(0.1)
            freq_layout.addWidget(self.freq_spin)
            layout.addLayout(freq_layout)
        
        # Input/Output Pin için özel isim
        if self.component.type in ["INPUT_PIN", "OUTPUT_PIN"]:
            custom_layout = QHBoxLayout()
            custom_layout.addWidget(QLabel("Özel İsim:"))
            self.custom_name_edit = QLineEdit(self.component.custom_name)
            custom_layout.addWidget(self.custom_name_edit)
            layout.addLayout(custom_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Tamam")
        ok_btn.clicked.connect(self.accept_changes)
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def accept_changes(self):
        """Değişiklikleri uygula"""
        self.component.name = self.name_edit.text()
        
        if self.component.type == "CLOCK":
            self.component.set_frequency(self.freq_spin.value())
        
        if self.component.type in ["INPUT_PIN", "OUTPUT_PIN"]:
            self.component.set_custom_name(self.custom_name_edit.text())
        
        self.accept()
