"""
Bileşen paleti - sürüklenebilir bileşenler
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QPushButton,
                              QLabel, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag


class ComponentPalette(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.init_ui()
        
    def init_ui(self):
        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area oluştur
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # İçerik widget'ı
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Temel Mantık Kapıları
        gates_group = self.create_group("Mantık Kapıları", [
            ("AND", "AND Kapısı"),
            ("OR", "OR Kapısı"),
            ("NOT", "NOT Kapısı"),
            ("NAND", "NAND Kapısı"),
            ("NOR", "NOR Kapısı"),
            ("XOR", "XOR Kapısı"),
            ("XNOR", "XNOR Kapısı"),
            ("BUFFER", "Buffer"),
        ])
        layout.addWidget(gates_group)
        
        # Aritmetik Bileşenler
        arith_group = self.create_group("Aritmetik", [
            ("HALF_ADDER", "Yarım Toplayıcı"),
            ("FULL_ADDER", "Tam Toplayıcı"),
            ("ADDER_4BIT", "4-bit Toplayıcı"),
            ("ADDER_8BIT", "8-bit Toplayıcı"),
            ("SUBTRACTOR", "Çıkarıcı"),
            ("MULTIPLIER", "Çarpıcı"),
            ("COMPARATOR", "Karşılaştırıcı"),
        ])
        layout.addWidget(arith_group)
        
        # Multiplexer/Demultiplexer
        mux_group = self.create_group("Mux/Demux", [
            ("MUX_2TO1", "2:1 Multiplexer"),
            ("MUX_4TO1", "4:1 Multiplexer"),
            ("MUX_8TO1", "8:1 Multiplexer"),
            ("DEMUX_1TO2", "1:2 Demultiplexer"),
            ("DEMUX_1TO4", "1:4 Demultiplexer"),
            ("DEMUX_1TO8", "1:8 Demultiplexer"),
        ])
        layout.addWidget(mux_group)
        
        # Encoder/Decoder
        codec_group = self.create_group("Encoder/Decoder", [
            ("ENCODER_4TO2", "4:2 Encoder"),
            ("ENCODER_8TO3", "8:3 Encoder"),
            ("DECODER_2TO4", "2:4 Decoder"),
            ("DECODER_3TO8", "3:8 Decoder"),
            ("PRIORITY_ENCODER", "Priority Encoder"),
        ])
        layout.addWidget(codec_group)
        
        # Flip-Flops
        ff_group = self.create_group("Flip-Flops", [
            ("D_FLIPFLOP", "D Flip-Flop"),
            ("JK_FLIPFLOP", "JK Flip-Flop"),
            ("T_FLIPFLOP", "T Flip-Flop"),
            ("SR_FLIPFLOP", "SR Flip-Flop"),
            ("LATCH_D", "D Latch"),
            ("LATCH_SR", "SR Latch"),
        ])
        layout.addWidget(ff_group)
        
        # Registers & Counters
        reg_group = self.create_group("Register/Counter", [
            ("REGISTER_4BIT", "4-bit Register"),
            ("REGISTER_8BIT", "8-bit Register"),
            ("SHIFT_REGISTER", "Shift Register"),
            ("COUNTER_4BIT", "4-bit Counter"),
            ("COUNTER_8BIT", "8-bit Counter"),
            ("UP_DOWN_COUNTER", "Up/Down Counter"),
        ])
        layout.addWidget(reg_group)
        
        # Memory
        mem_group = self.create_group("Bellek", [
            ("RAM_16X8", "16x8 RAM"),
            ("RAM_256X8", "256x8 RAM"),
            ("ROM_16X8", "16x8 ROM"),
            ("ROM_256X8", "256x8 ROM"),
        ])
        layout.addWidget(mem_group)
        
        # Input/Output
        io_group = self.create_group("Giriş/Çıkış", [
            ("INPUT_PIN", "Input Pin"),
            ("OUTPUT_PIN", "Output Pin"),
            ("SWITCH", "Switch"),
            ("BUTTON", "Button"),
            ("CLOCK", "Clock"),
            ("LED", "LED"),
            ("LED_RGB", "RGB LED"),
            ("SEVEN_SEGMENT", "7-Segment Display"),
            ("HEX_DISPLAY", "Hex Display"),
        ])
        layout.addWidget(io_group)
        
        # Diğer
        other_group = self.create_group("Diğer", [
            ("SPLITTER", "Splitter"),
            ("MERGER", "Merger"),
            ("CONSTANT", "Sabit Değer"),
            ("PROBE", "Probe"),
            ("GROUND", "Ground"),
            ("VCC", "VCC"),
        ])
        layout.addWidget(other_group)
        
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def create_group(self, title, components):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QGridLayout()
        
        for i, (comp_type, comp_name) in enumerate(components):
            btn = ComponentButton(comp_type, comp_name, self.canvas)
            layout.addWidget(btn, i // 2, i % 2)
            
        group.setLayout(layout)
        return group


class ComponentButton(QPushButton):
    def __init__(self, component_type, component_name, canvas):
        super().__init__(component_name)
        self.component_type = component_type
        self.canvas = canvas
        
        self.setMinimumHeight(35)
        self.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #888;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Canvas'ın görünür alanının ortasına ekle
            scroll_area = self.canvas.parent()
            if scroll_area:
                # Scroll area'nın görünür alanının merkezi
                viewport_center = scroll_area.viewport().rect().center()
                # Canvas koordinatlarına çevir
                canvas_pos = scroll_area.widget().mapFrom(scroll_area.viewport(), viewport_center)
                self.canvas.add_component(self.component_type, canvas_pos)
            else:
                center = QPoint(self.canvas.width() // 2, self.canvas.height() // 2)
                self.canvas.add_component(self.component_type, center)
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        # Çift tıklama da aynı işlevi yapar
        self.mousePressEvent(event)
