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
        self.selected_wires = []  # Seçili kablolar
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
        
        # Kablo köşe noktaları (Vertex sistemi)
        self.wire_vertices = []  # Kalıcı köşe noktaları
        self.temp_wire_path = []  # Geçici kablo yolu
        self.dragging_vertex = None  # Sürüklenen vertex
        self.dragging_vertex_index = None
        
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
        
        # Bileşen adı (düzenlenebilir etiket)
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        
        # İsmi bileşenin üstünde göster
        name_rect = QRect(component.x, component.y - 18, component.width, 15)
        
        # Eğer bu bileşen düzenleme modundaysa farklı renk
        if hasattr(self, 'editing_component') and self.editing_component == component:
            painter.setPen(QPen(QColor(100, 200, 255)))
            painter.drawRect(name_rect)
        
        painter.setPen(QPen(QColor(220, 220, 220)))
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, component.name)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_switch(self, painter, component):
        """İnteraktif Switch/Button çiz"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Basılı durumunu kontrol et
        is_pressed = hasattr(component, 'is_pressed') and component.is_pressed
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Switch durumuna ve basılı durumuna göre renk
        if is_pressed:
            # Basılı: Koyu yeşil
            painter.setBrush(QBrush(QColor(60, 150, 60)))
        elif component.state:
            # ON: Açık yeşil
            painter.setBrush(QBrush(QColor(100, 200, 100)))
        else:
            # OFF: Gri
            painter.setBrush(QBrush(QColor(80, 80, 80)))
        
        # 3D buton efekti
        if is_pressed:
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 5, 5)
        else:
            painter.drawRoundedRect(rect, 5, 5)
            # Gölge efekti
            painter.setPen(QPen(QColor(40, 40, 40), 1))
            painter.drawRoundedRect(rect.adjusted(2, 2, 2, 2), 5, 5)
        
        # Switch metni
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        status = "ON" if component.state else "OFF"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, status)
        
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
        """IEEE Std 91-1984 standart mantık kapısı çiz - Matematiksel olarak kusursuz"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        x, y, w, h = component.x, component.y, component.width, component.height
        
        if component.type == "AND":
            # IEEE AND: Düz sol kenar + yarım daire sağ kenar
            path = QPainterPath()
            path.moveTo(x, y)
            path.lineTo(x + w * 0.5, y)
            path.arcTo(x + w * 0.1, y, w * 0.8, h, 90, -180)
            path.lineTo(x, y + h)
            path.closeSubpath()
            painter.drawPath(path)
            
        elif component.type == "OR":
            # IEEE OR: Kavisli giriş + sivri çıkış
            path = QPainterPath()
            # Sol kavis (giriş tarafı)
            path.moveTo(x, y)
            path.quadTo(x + w * 0.2, y + h * 0.5, x, y + h)
            # Alt kenar
            path.quadTo(x + w * 0.4, y + h * 0.85, x + w * 0.9, y + h * 0.5)
            # Üst kenar
            path.quadTo(x + w * 0.4, y + h * 0.15, x, y)
            painter.drawPath(path)
            
        elif component.type == "NAND":
            # IEEE NAND: AND + inversion bubble
            path = QPainterPath()
            bubble_radius = 5
            path.moveTo(x, y)
            path.lineTo(x + w * 0.5, y)
            path.arcTo(x + w * 0.1, y, w * 0.7, h, 90, -180)
            path.lineTo(x, y + h)
            path.closeSubpath()
            painter.drawPath(path)
            
            # Inversion bubble (çıkışta)
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPoint(int(x + w * 0.85), int(y + h / 2)), bubble_radius, bubble_radius)
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            
        elif component.type == "NOR":
            # IEEE NOR: OR + inversion bubble
            path = QPainterPath()
            bubble_radius = 5
            path.moveTo(x, y)
            path.quadTo(x + w * 0.2, y + h * 0.5, x, y + h)
            path.quadTo(x + w * 0.35, y + h * 0.85, x + w * 0.8, y + h * 0.5)
            path.quadTo(x + w * 0.35, y + h * 0.15, x, y)
            painter.drawPath(path)
            
            # Inversion bubble
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPoint(int(x + w * 0.85), int(y + h / 2)), bubble_radius, bubble_radius)
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            
        elif component.type == "XOR":
            # IEEE XOR: Çift kavisli giriş + sivri çıkış
            path = QPainterPath()
            # Ana gövde
            path.moveTo(x + 12, y)
            path.quadTo(x + w * 0.25, y + h * 0.5, x + 12, y + h)
            path.quadTo(x + w * 0.45, y + h * 0.85, x + w * 0.95, y + h * 0.5)
            path.quadTo(x + w * 0.45, y + h * 0.15, x + 12, y)
            painter.drawPath(path)
            
            # Ekstra giriş kavisi (double curved shield)
            extra_path = QPainterPath()
            extra_path.moveTo(x + 2, y + 2)
            extra_path.quadTo(x + w * 0.15, y + h * 0.5, x + 2, y + h - 2)
            painter.drawPath(extra_path)
            
        elif component.type == "XNOR":
            # IEEE XNOR: XOR + inversion bubble
            path = QPainterPath()
            bubble_radius = 5
            # Ana gövde
            path.moveTo(x + 12, y)
            path.quadTo(x + w * 0.25, y + h * 0.5, x + 12, y + h)
            path.quadTo(x + w * 0.4, y + h * 0.85, x + w * 0.85, y + h * 0.5)
            path.quadTo(x + w * 0.4, y + h * 0.15, x + 12, y)
            painter.drawPath(path)
            
            # Ekstra giriş kavisi
            extra_path = QPainterPath()
            extra_path.moveTo(x + 2, y + 2)
            extra_path.quadTo(x + w * 0.15, y + h * 0.5, x + 2, y + h - 2)
            painter.drawPath(extra_path)
            
            # Inversion bubble
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPoint(int(x + w * 0.9), int(y + h / 2)), bubble_radius, bubble_radius)
            painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_not_gate(self, painter, component):
        """IEEE NOT kapısı çiz - Üçgen + inversion bubble"""
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 2))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        x, y, w, h = component.x, component.y, component.width, component.height
        bubble_radius = 5
        
        # IEEE NOT: Üçgen gövde
        path = QPainterPath()
        # Sol kenar (giriş)
        path.moveTo(x + 5, y + 5)
        # Üst köşe
        path.lineTo(x + w - bubble_radius - 8, y + h / 2)
        # Alt köşe
        path.lineTo(x + 5, y + h - 5)
        # Kapat
        path.closeSubpath()
        painter.drawPath(path)
        
        # Inversion bubble (çıkışta)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPoint(int(x + w - bubble_radius - 3), int(y + h / 2)), bubble_radius, bubble_radius)
        
        # Pinleri çiz
        painter.setBrush(QBrush(QColor(60, 60, 60)))
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
        """Input Pin çiz - state ile tam senkronize"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Durum rengine göre - state değerine bakarak
        actual_state = bool(component.state)
        if actual_state:
            painter.setBrush(QBrush(QColor(50, 205, 50)))  # Parlak yeşil
        else:
            painter.setBrush(QBrush(QColor(85, 85, 85)))  # Koyu gri
        
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
        
        # Durum altta - state ile senkronize
        status = "1" if actual_state else "0"
        status_rect = QRect(component.x, component.y + component.height // 2, component.width, component.height // 2 - 5)
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_output_pin(self, painter, component):
        """Output Pin çiz - giriş değeri ile tam senkronize"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        # Seçili mi?
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Gerçek değeri al - display_value kullan
        is_on = bool(component.display_value) if hasattr(component, 'display_value') else False
        
        if is_on:
            painter.setBrush(QBrush(QColor(50, 205, 50)))  # Parlak yeşil
        else:
            painter.setBrush(QBrush(QColor(85, 85, 85)))  # Koyu gri
        
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
        
        # Durum altta - gerçek değer
        status = "1" if is_on else "0"
        status_rect = QRect(component.x, component.y + component.height // 2, component.width, component.height // 2 - 5)
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_vcc(self, painter, component):
        """VCC bileşeni çiz - her zaman 1"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Her zaman yeşil (1)
        painter.setBrush(QBrush(QColor(50, 205, 50)))
        painter.drawRoundedRect(rect, 5, 5)
        
        # VCC sembolü
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "VCC\n1")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_ground(self, painter, component):
        """GROUND bileşeni çiz - her zaman 0"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Her zaman gri (0)
        painter.setBrush(QBrush(QColor(85, 85, 85)))
        painter.drawRoundedRect(rect, 5, 5)
        
        # GND sembolü
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "GND\n0")
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_constant(self, painter, component):
        """CONSTANT bileşeni çiz - ayarlanabilir sabit"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Değere göre renk
        const_val = bool(component.constant_value) if hasattr(component, 'constant_value') else True
        if const_val:
            painter.setBrush(QBrush(QColor(50, 205, 50)))
        else:
            painter.setBrush(QBrush(QColor(85, 85, 85)))
        
        painter.drawRoundedRect(rect, 5, 5)
        
        # CONST ve değer
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(component.x, component.y + 15, component.width, 15, 
                        Qt.AlignmentFlag.AlignCenter, "CONST")
        
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        status = "1" if const_val else "0"
        painter.drawText(component.x, component.y + 25, component.width, 20,
                        Qt.AlignmentFlag.AlignCenter, status)
        
        # Pinleri çiz
        self.draw_pins(painter, component)
    
    def draw_probe(self, painter, component):
        """PROBE bileşeni çiz - logic göstergesi"""
        rect = QRect(component.x, component.y, component.width, component.height)
        
        if component in self.selected_components:
            painter.setPen(QPen(QColor(100, 150, 255), 3))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Probe değerine göre renk
        probe_val = bool(component.probe_value) if hasattr(component, 'probe_value') else False
        if probe_val:
            painter.setBrush(QBrush(QColor(50, 205, 50)))
        else:
            painter.setBrush(QBrush(QColor(85, 85, 85)))
        
        # Daire şeklinde probe
        center = rect.center()
        radius = min(component.width, component.height) // 2 - 5
        painter.drawEllipse(center, radius, radius)
        
        # PROBE ve değer
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(component.x, component.y + 5, component.width, 15,
                        Qt.AlignmentFlag.AlignCenter, "PROBE")
        
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        status = "1" if probe_val else "0"
        painter.drawText(component.x, component.y + 20, component.width, 25,
                        Qt.AlignmentFlag.AlignCenter, status)
        
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
            
            # Pin değerine göre dinamik renk
            pin_val = bool(pin.value)
            if pin_val:
                # Logic 1: Parlak yeşil
                painter.setBrush(QBrush(QColor(50, 205, 50)))
                painter.setPen(QPen(QColor(34, 139, 34), 2))
            else:
                # Logic 0: Koyu gri
                painter.setBrush(QBrush(QColor(85, 85, 85)))
                painter.setPen(QPen(QColor(100, 100, 100), 2))
                
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
            
            # Pin değerine göre dinamik renk
            pin_val = bool(pin.value)
            if pin_val:
                # Logic 1: Parlak yeşil
                painter.setBrush(QBrush(QColor(50, 205, 50)))
                painter.setPen(QPen(QColor(34, 139, 34), 2))
            else:
                # Logic 0: Koyu gri
                painter.setBrush(QBrush(QColor(85, 85, 85)))
                painter.setPen(QPen(QColor(100, 100, 100), 2))
                
            painter.drawEllipse(QPoint(component.x + component.width, y), pin_radius, pin_radius)
            
            # Pin etiketi - içeride, sağa hizalı
            painter.setPen(QPen(QColor(200, 200, 200)))
            text_width = painter.fontMetrics().horizontalAdvance(pin.name)
            painter.drawText(component.x + component.width - text_width - 10, y + 3, pin.name)
            
    def draw_wire(self, painter, wire):
        """Manuel orthogonal kablo çiz - Kullanıcı waypoint'leri korunur"""
        # Kablo seçili mi?
        is_selected = wire in getattr(self, 'selected_wires', [])
        
        # Kablo değerine göre dinamik renk
        wire_val = bool(wire.value)
        if is_selected:
            # Seçili: Mavi
            pen_color = QColor(100, 150, 255)
            pen_width = 4
        elif wire_val:
            # Logic 1: Parlak yeşil
            pen_color = QColor(50, 205, 50)
            pen_width = 3
        else:
            # Logic 0: Koyu gri
            pen_color = QColor(85, 85, 85)
            pen_width = 2
        
        painter.setPen(QPen(pen_color, pen_width))
        
        # Başlangıç ve bitiş noktaları
        start = wire.from_pin.get_position()
        end = wire.to_pin.get_position()
        
        # Kullanıcının eklediği vertex'lerle yol oluştur
        if hasattr(wire, 'vertices') and wire.vertices:
            path_points = [start] + wire.vertices + [end]
            
            # Kullanıcının belirlediği waypoint'ler arasında DOĞRUDAN çiz
            # Otomatik optimizasyon YOK
            for i in range(len(path_points) - 1):
                p1 = path_points[i]
                p2 = path_points[i + 1]
                
                # Sadece orthogonal zorunluluğu - diagonal varsa L-şekli yap
                if p1.x() != p2.x() and p1.y() != p2.y():
                    # Hangi yön daha uzunsa önce o yönde git
                    dx = abs(p2.x() - p1.x())
                    dy = abs(p2.y() - p1.y())
                    
                    if dx > dy:
                        mid = QPoint(p2.x(), p1.y())
                    else:
                        mid = QPoint(p1.x(), p2.y())
                    
                    painter.drawLine(p1, mid)
                    painter.drawLine(mid, p2)
                else:
                    # Zaten orthogonal
                    painter.drawLine(p1, p2)
            
            # Kullanıcının eklediği waypoint'leri göster
            if is_selected:
                painter.setBrush(QBrush(QColor(100, 150, 255)))
                painter.setPen(QPen(QColor(80, 120, 200), 2))
            else:
                painter.setBrush(QBrush(QColor(120, 120, 120)))
                painter.setPen(QPen(QColor(100, 100, 100), 1))
            
            for vertex in wire.vertices:
                painter.drawEllipse(vertex, 5, 5)
        else:
            # Vertex yoksa basit L-şekli (sadece 2 nokta arası)
            dx = abs(end.x() - start.x())
            dy = abs(end.y() - start.y())
            
            if dx > dy:
                intermediate = QPoint(end.x(), start.y())
            else:
                intermediate = QPoint(start.x(), end.y())
            
            painter.drawLine(start, intermediate)
            painter.drawLine(intermediate, end)
        
    def draw_temp_wire(self, painter):
        """Manuel orthogonal kablolama - Kullanıcı waypoint'leri ZORUNLU"""
        painter.setPen(QPen(QColor(150, 150, 255), 2, Qt.PenStyle.DashLine))
        start = self.connecting_from.get_position()
        
        # Kullanıcının tıkladığı tüm waypoint'leri koru
        path_points = [start] + self.wire_vertices
        
        if self.temp_wire_end:
            # Son waypoint'ten fare pozisyonuna SADECE orthogonal çizgi
            if path_points:
                last_point = path_points[-1]
                
                # Manuel orthogonal: Kullanıcı nereye tıklarsa oraya git
                # Sadece son segment için otomatik L-şekli (fare takibi için)
                dx = abs(self.temp_wire_end.x() - last_point.x())
                dy = abs(self.temp_wire_end.y() - last_point.y())
                
                # Hangi yön daha baskınsa önce o yönde git
                if dx > dy:
                    # Önce yatay
                    mid = QPoint(self.temp_wire_end.x(), last_point.y())
                else:
                    # Önce dikey
                    mid = QPoint(last_point.x(), self.temp_wire_end.y())
                
                # Sadece son segment için ara nokta ekle
                if mid != last_point and mid != self.temp_wire_end:
                    path_points.append(mid)
            
            path_points.append(self.temp_wire_end)
        
        # Kullanıcının eklediği waypoint'ler arasında DOĞRUDAN çizgi çek
        # Otomatik routing YOK - sadece orthogonal zorunluluğu
        for i in range(len(path_points) - 1):
            p1 = path_points[i]
            p2 = path_points[i + 1]
            
            # Eğer diagonal ise (kullanıcı hatalı tıklamış), L-şekli yap
            if p1.x() != p2.x() and p1.y() != p2.y():
                # Hangi yön daha uzunsa önce o yönde git
                dx = abs(p2.x() - p1.x())
                dy = abs(p2.y() - p1.y())
                
                if dx > dy:
                    mid = QPoint(p2.x(), p1.y())
                else:
                    mid = QPoint(p1.x(), p2.y())
                
                painter.drawLine(p1, mid)
                painter.drawLine(mid, p2)
            else:
                # Zaten orthogonal
                painter.drawLine(p1, p2)
        
        # Kullanıcının eklediği waypoint'leri vurgula
        painter.setBrush(QBrush(QColor(150, 150, 255)))
        painter.setPen(QPen(QColor(100, 100, 200), 2))
        for vertex in self.wire_vertices:
            painter.drawEllipse(vertex, 6, 6)
    
    def calculate_orthogonal_point(self, start, end):
        """Manhattan routing için ara nokta hesapla"""
        dx = abs(end.x() - start.x())
        dy = abs(end.y() - start.y())
        
        if dx > dy:
            # Önce yatay git
            return QPoint(end.x(), start.y())
        else:
            # Önce dikey git
            return QPoint(start.x(), end.y())
        
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
                    # Kablo bağlantısı başlat
                    self.connecting_from = pin
                    self.temp_wire_end = pos
                    self.wire_vertices = []
                else:
                    # Kablo bağlantısını tamamla
                    if pin != self.connecting_from:
                        if self.connecting_from.is_input != pin.is_input:
                            # Kabloyu oluştur
                            if self.connecting_from.is_input:
                                self.circuit.add_wire(pin, self.connecting_from)
                                # Son eklenen kabloyu bul
                                wire = self.circuit.wires[-1] if self.circuit.wires else None
                            else:
                                self.circuit.add_wire(self.connecting_from, pin)
                                wire = self.circuit.wires[-1] if self.circuit.wires else None
                            
                            # Kullanıcının eklediği waypoint'leri ZORUNLU olarak kaydet
                            if wire and hasattr(wire, 'vertices'):
                                wire.vertices = self.wire_vertices.copy()
                        
                        self.connecting_from = None
                        self.temp_wire_end = None
                        self.wire_vertices = []
                        self.update()
                    else:
                        self.connecting_from = None
                        self.temp_wire_end = None
                        self.wire_vertices = []
                        self.update()
                return
            
            # Kablo çizimi sırasında boşluğa tıklama - ZORUNLU Waypoint ekle
            if self.connecting_from:
                # Grid'e snap yap - kullanıcının tıkladığı nokta ZORUNLU waypoint
                snapped_pos = self.snap_to_grid(pos)
                # Aynı noktaya tekrar tıklanmışsa ekleme
                if not self.wire_vertices or self.wire_vertices[-1] != snapped_pos:
                    self.wire_vertices.append(snapped_pos)
                self.update()
                return
            
            # Bileşen seçimi
            component = self.get_component_at(pos)
            if component:
                # Switch/Button basma (simülasyon çalışırken)
                if component.type == "SWITCH" and self.circuit.is_running:
                    component.press()
                    # Simülasyonu tetikle - sinyal yayılımı
                    self.circuit.step()
                    self.update()
                    return
                
                # INPUT_PIN toggle (simülasyon çalışırken)
                if component.type == "INPUT_PIN" and self.circuit.is_running:
                    component.toggle()
                    # Simülasyonu tetikle - sinyal yayılımı
                    self.circuit.step()
                    self.update()
                    return
                
                # CONSTANT toggle (simülasyon durdurulduğunda)
                if component.type == "CONSTANT" and not self.circuit.is_running:
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
            # Switch/Button bırakma
            pos = self.map_to_canvas(event.pos())
            component = self.get_component_at(pos)
            if component and component.type == "SWITCH":
                component.release()
                self.update()
            
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
        """Çift tıklama - bileşen ismini düzenle veya özellikleri aç"""
        if self.circuit.is_running:
            return
        
        pos = self.map_to_canvas(event.pos())
        component = self.get_component_at(pos)
        
        if component:
            # İsim alanına tıklandı mı kontrol et
            name_rect = QRect(component.x, component.y - 18, component.width, 15)
            if name_rect.contains(pos):
                # İsim düzenleme modu
                self.edit_component_name(component)
            else:
                # Özellikler dialogu
                self.show_component_properties(component)
    
    def edit_component_name(self, component):
        """Bileşen ismini düzenle"""
        from PyQt6.QtWidgets import QInputDialog
        
        new_name, ok = QInputDialog.getText(
            self,
            "Bileşen İsmini Düzenle",
            f"{component.type} için yeni isim:",
            text=component.name
        )
        
        if ok and new_name:
            component.name = new_name
            self.update()
            
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
    
    def snap_to_grid(self, pos):
        """Pozisyonu grid'e hizala"""
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        return QPoint(x, y)
    
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
