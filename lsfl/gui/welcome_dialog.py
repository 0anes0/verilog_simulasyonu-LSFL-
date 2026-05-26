"""
Hoş geldiniz ekranı - Logo, dil seçimi ve proje yönetimi
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QComboBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer
import os

from core.i18n import get_translator, tr


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = get_translator()
        self.selected_action = None  # "new", "open", veya None
        self.selected_file = None
        self.selected_language = self.translator.current_language  # Seçilen dil
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(tr("welcome"))
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        # Ana layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo (SVG -> Pixmap) - SVG içinde zaten yazılar var, ayrı label eklemeyelim
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.svg")
        if os.path.exists(logo_path):
            # SVG'yi QPixmap'e render et
            renderer = QSvgRenderer(logo_path)
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            from PyQt6.QtGui import QPainter
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            logo_label = QLabel()
            logo_label.setPixmap(pixmap)
            logo_label.setFixedSize(200, 200)
            logo_layout = QHBoxLayout()
            logo_layout.addStretch()
            logo_layout.addWidget(logo_label)
            logo_layout.addStretch()
            layout.addLayout(logo_layout)
        else:
            # Fallback: Text logo (SVG yoksa)
            title_label = QLabel("LSFL")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #4a9eff;
                }
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            # Subtitle (sadece fallback durumunda)
            subtitle = QLabel("Logic Sim For Linux")
            subtitle.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #cccccc;
                }
            """)
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Dil seçimi
        lang_layout = QHBoxLayout()
        lang_label = QLabel(tr("language") + ":")
        lang_label.setStyleSheet("color: white; font-size: 14px;")
        self.lang_combo = QComboBox()
        
        # Dilleri ekle
        available_langs = self.translator.get_available_languages()
        for code, name in available_langs.items():
            self.lang_combo.addItem(name, code)
        
        # Mevcut dili seç
        current_index = self.lang_combo.findData(self.translator.current_language)
        if current_index >= 0:
            self.lang_combo.setCurrentIndex(current_index)
        
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #404040;
                color: white;
                border: 2px solid #4a9eff;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 10px;
            }
        """)
        
        lang_layout.addStretch()
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        layout.addSpacing(20)
        
        # Aksiyon butonları
        button_style = """
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #5ab0ff;
            }
            QPushButton:pressed {
                background-color: #3a8edf;
            }
        """
        
        # Yeni Proje butonu
        self.new_btn = QPushButton(tr("new_project"))
        self.new_btn.setStyleSheet(button_style)
        self.new_btn.clicked.connect(self.on_new_project)
        layout.addWidget(self.new_btn)
        
        # Proje Aç butonu
        self.open_btn = QPushButton(tr("open_project"))
        self.open_btn.setStyleSheet(button_style)
        self.open_btn.clicked.connect(self.on_open_project)
        layout.addWidget(self.open_btn)
        
        layout.addStretch()
        
        # Arka plan rengi
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
        """)
        
        self.setLayout(layout)
    
    def on_language_changed(self, index):
        """Dil değiştirildiğinde - Global state'i güncelle"""
        lang_code = self.lang_combo.itemData(index)
        self.translator.set_language(lang_code)
        
        # UI'ı güncelle
        self.update_ui_texts()
        
        # Seçilen dili sakla (MainWindow'a aktarılacak)
        self.selected_language = lang_code
    
    def update_ui_texts(self):
        """UI metinlerini güncelle"""
        self.setWindowTitle(tr("welcome"))
        self.new_btn.setText(tr("new_project"))
        self.open_btn.setText(tr("open_project"))
        # Lang label'ı güncelle
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.layout():
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if isinstance(widget, QLabel) and ":" in widget.text():
                        widget.setText(tr("language") + ":")
                        break
    
    def on_new_project(self):
        """Yeni proje oluştur"""
        self.selected_action = "new"
        self.accept()
    
    def on_open_project(self):
        """Proje aç"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            tr("open_project"), 
            "", 
            "LSFL Circuit (*.lsfl);;All Files (*)"
        )
        
        if filename:
            self.selected_action = "open"
            self.selected_file = filename
            self.accept()
