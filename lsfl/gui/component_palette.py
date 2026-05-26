"""
Bileşen paleti - sürüklenebilir bileşenler
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QPushButton,
                              QLabel, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag

from core.i18n import tr


class ComponentPalette(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.groups = []  # Grup referanslarını sakla
        self.init_ui()
    
    def retranslate_ui(self):
        """Dil değiştiğinde tüm grupları yeniden oluştur"""
        # Mevcut içeriği temizle
        layout = self.layout()
        if layout:
            scroll = layout.itemAt(0).widget()
            if scroll:
                content = scroll.widget()
                if content:
                    # Eski layout'u temizle
                    old_layout = content.layout()
                    if old_layout:
                        while old_layout.count():
                            item = old_layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()
        
        # Yeniden oluştur
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
        
        # Input/Output (EN ÜSTTE)
        io_group = self.create_group(tr("io_components"), [
            ("INPUT_PIN", tr("input_pin")),
            ("OUTPUT_PIN", tr("output_pin")),
            ("SWITCH", tr("switch")),
            ("CLOCK", tr("clock")),
            ("LED", tr("led")),
        ])
        layout.addWidget(io_group)
        
        # Temel Mantık Kapıları
        gates_group = self.create_group(tr("logic_gates"), [
            ("AND", tr("and_gate")),
            ("OR", tr("or_gate")),
            ("NOT", tr("not_gate")),
            ("NAND", tr("nand_gate")),
            ("NOR", tr("nor_gate")),
            ("XOR", tr("xor_gate")),
            ("XNOR", tr("xnor_gate")),
            ("BUFFER", tr("buffer")),
        ])
        layout.addWidget(gates_group)
        
        # Aritmetik Bileşenler
        arith_group = self.create_group(tr("arithmetic"), [
            ("HALF_ADDER", tr("half_adder")),
            ("FULL_ADDER", tr("full_adder")),
            ("ADDER_4BIT", tr("adder_4bit")),
            ("ADDER_8BIT", tr("adder_8bit")),
            ("SUBTRACTOR", tr("subtractor")),
            ("MULTIPLIER", tr("multiplier")),
            ("COMPARATOR", tr("comparator")),
        ])
        layout.addWidget(arith_group)
        
        # Multiplexer/Demultiplexer
        mux_group = self.create_group(tr("mux_demux"), [
            ("MUX_2TO1", tr("mux_2to1")),
            ("MUX_4TO1", tr("mux_4to1")),
            ("MUX_8TO1", tr("mux_8to1")),
            ("DEMUX_1TO2", tr("demux_1to2")),
            ("DEMUX_1TO4", tr("demux_1to4")),
            ("DEMUX_1TO8", tr("demux_1to8")),
        ])
        layout.addWidget(mux_group)
        
        # Encoder/Decoder
        codec_group = self.create_group(tr("encoder_decoder"), [
            ("ENCODER_4TO2", tr("encoder_4to2")),
            ("ENCODER_8TO3", tr("encoder_8to3")),
            ("DECODER_2TO4", tr("decoder_2to4")),
            ("DECODER_3TO8", tr("decoder_3to8")),
            ("PRIORITY_ENCODER", tr("priority_encoder")),
        ])
        layout.addWidget(codec_group)
        
        # Flip-Flops
        ff_group = self.create_group(tr("flipflops"), [
            ("D_FLIPFLOP", tr("d_flipflop")),
            ("JK_FLIPFLOP", tr("jk_flipflop")),
            ("T_FLIPFLOP", tr("t_flipflop")),
            ("SR_FLIPFLOP", tr("sr_flipflop")),
            ("LATCH_D", tr("d_latch")),
            ("LATCH_SR", tr("sr_latch")),
        ])
        layout.addWidget(ff_group)
        
        # Registers & Counters
        reg_group = self.create_group(tr("registers"), [
            ("REGISTER_4BIT", tr("register_4bit")),
            ("REGISTER_8BIT", tr("register_8bit")),
            ("SHIFT_REGISTER", tr("shift_register")),
            ("COUNTER_4BIT", tr("counter_4bit")),
            ("COUNTER_8BIT", tr("counter_8bit")),
            ("UP_DOWN_COUNTER", tr("updown_counter")),
        ])
        layout.addWidget(reg_group)
        
        # Memory
        mem_group = self.create_group(tr("memory"), [
            ("RAM_16X8", tr("ram_16x8")),
            ("RAM_256X8", tr("ram_256x8")),
            ("ROM_16X8", tr("rom_16x8")),
            ("ROM_256X8", tr("rom_256x8")),
        ])
        layout.addWidget(mem_group)
        
        # Diğer
        other_group = self.create_group(tr("other"), [
            ("VCC", tr("vcc")),
            ("GROUND", tr("ground")),
            ("CONSTANT", tr("constant")),
            ("PROBE", tr("probe")),
            ("SPLITTER", tr("splitter")),
            ("MERGER", tr("merger")),
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
            # Yerleştirme modunu başlat
            self.canvas.start_placing_component(self.component_type)
        super().mousePressEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        # Çift tıklama da aynı işlevi yapar
        self.mousePressEvent(event)
