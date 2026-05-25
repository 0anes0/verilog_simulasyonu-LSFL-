"""
Verilog kodu gösterme ve kaydetme dialogu
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton,
                              QHBoxLayout, QFileDialog, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class VerilogDialog(QDialog):
    def __init__(self, verilog_code, parent=None):
        super().__init__(parent)
        self.verilog_code = verilog_code
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Verilog Kodu")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        # Kod editörü
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.verilog_code)
        self.text_edit.setReadOnly(True)
        
        # Monospace font
        font = QFont("Courier New", 10)
        self.text_edit.setFont(font)
        
        # Syntax highlighting (basit)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout.addWidget(self.text_edit)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Panoya Kopyala")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("💾 Dosyaya Kaydet")
        save_btn.clicked.connect(self.save_to_file)
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def copy_to_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.verilog_code)
        QMessageBox.information(self, "Başarılı", "Verilog kodu panoya kopyalandı!")
        
    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Verilog Dosyası Kaydet", "",
            "Verilog Dosyası (*.v);;Tüm Dosyalar (*)"
        )
        
        if filename:
            if not filename.endswith('.v'):
                filename += '.v'
                
            try:
                with open(filename, 'w') as f:
                    f.write(self.verilog_code)
                QMessageBox.information(self, "Başarılı", 
                                       f"Verilog kodu kaydedildi:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", 
                                    f"Dosya kaydedilemedi:\n{str(e)}")
