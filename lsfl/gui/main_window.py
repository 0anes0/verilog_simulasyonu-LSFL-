"""
Ana pencere ve kullanıcı arayüzü
"""

from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QDockWidget,
                              QVBoxLayout, QWidget, QPushButton, QMessageBox,
                              QFileDialog, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from gui.canvas import Canvas
from gui.component_palette import ComponentPalette
from core.circuit import Circuit
from export.verilog_generator import VerilogGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.circuit = Circuit()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LSFL - Logic Sim For Linux")
        self.setGeometry(100, 100, 1400, 900)
        
        # Canvas (merkezi widget)
        self.canvas = Canvas(self.circuit)
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)
        
        # Toolbar
        self.create_toolbar()
        
        # Component Palette (sol dock)
        self.create_component_palette()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Hazır")
        
        # Menü
        self.create_menu()
        
    def create_toolbar(self):
        toolbar = QToolBar("Ana Araçlar")
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # Yeni devre
        new_action = QAction("Yeni", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_circuit)
        toolbar.addAction(new_action)
        
        # Aç
        open_action = QAction("Aç", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_circuit)
        toolbar.addAction(open_action)
        
        # Kaydet
        save_action = QAction("Kaydet", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_circuit)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Simülasyon başlat/durdur
        self.sim_action = QAction("▶ Simülasyon Başlat", self)
        self.sim_action.triggered.connect(self.toggle_simulation)
        toolbar.addAction(self.sim_action)
        
        # Sıfırla
        reset_action = QAction("⟲ Sıfırla", self)
        reset_action.triggered.connect(self.reset_simulation)
        toolbar.addAction(reset_action)
        
        toolbar.addSeparator()
        
        # Verilog Export (SAĞ ÜSTTE BÜYÜK BUTON)
        verilog_action = QAction("📋 Verilog Kodu Üret", self)
        verilog_action.triggered.connect(self.export_verilog)
        toolbar.addAction(verilog_action)
        
        # Toolbar'ı sağa hizala için spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
    def create_component_palette(self):
        dock = QDockWidget("Bileşenler", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.palette = ComponentPalette(self.canvas)
        dock.setWidget(self.palette)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu("Dosya")
        file_menu.addAction("Yeni", self.new_circuit, QKeySequence.StandardKey.New)
        file_menu.addAction("Aç", self.open_circuit, QKeySequence.StandardKey.Open)
        file_menu.addAction("Kaydet", self.save_circuit, QKeySequence.StandardKey.Save)
        file_menu.addAction("Farklı Kaydet", self.save_circuit_as)
        file_menu.addSeparator()
        file_menu.addAction("Çıkış", self.close, QKeySequence("Ctrl+Q"))
        
        # Düzenle menüsü
        edit_menu = menubar.addMenu("Düzenle")
        edit_menu.addAction("Geri Al", self.canvas.undo, QKeySequence.StandardKey.Undo)
        edit_menu.addAction("Yinele", self.canvas.redo, QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Sil", self.canvas.delete_selected, QKeySequence.StandardKey.Delete)
        edit_menu.addAction("Tümünü Seç", self.canvas.select_all, QKeySequence.StandardKey.SelectAll)
        
        # Simülasyon menüsü
        sim_menu = menubar.addMenu("Simülasyon")
        sim_menu.addAction("Başlat/Durdur", self.toggle_simulation, QKeySequence("Space"))
        sim_menu.addAction("Sıfırla", self.reset_simulation, QKeySequence("Ctrl+R"))
        sim_menu.addSeparator()
        sim_menu.addAction("Tek Adım", self.step_simulation, QKeySequence("Ctrl+T"))
        
        # Export menüsü
        export_menu = menubar.addMenu("Export")
        export_menu.addAction("Verilog Kodu Üret", self.export_verilog, QKeySequence("Ctrl+E"))
        export_menu.addAction("PNG Olarak Kaydet", self.export_png)
        
        # Yardım menüsü
        help_menu = menubar.addMenu("Yardım")
        help_menu.addAction("Hakkında", self.show_about)
        
    def new_circuit(self):
        reply = QMessageBox.question(self, "Yeni Devre",
                                    "Mevcut devreyi kapatmak istediğinizden emin misiniz?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.circuit.clear()
            self.canvas.clear()
            self.statusBar.showMessage("Yeni devre oluşturuldu")
            
    def open_circuit(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Devre Aç", "", 
                                                  "LSFL Devre (*.lsfl);;Tüm Dosyalar (*)")
        if filename:
            try:
                self.circuit.load(filename)
                self.canvas.load_circuit()
                self.statusBar.showMessage(f"Devre yüklendi: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Devre yüklenemedi: {str(e)}")
                
    def save_circuit(self):
        if hasattr(self.circuit, 'filename') and self.circuit.filename:
            self.circuit.save(self.circuit.filename)
            self.statusBar.showMessage(f"Devre kaydedildi: {self.circuit.filename}")
        else:
            self.save_circuit_as()
            
    def save_circuit_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Devre Kaydet", "", 
                                                  "LSFL Devre (*.lsfl);;Tüm Dosyalar (*)")
        if filename:
            if not filename.endswith('.lsfl'):
                filename += '.lsfl'
            self.circuit.save(filename)
            self.circuit.filename = filename
            self.statusBar.showMessage(f"Devre kaydedildi: {filename}")
            
    def toggle_simulation(self):
        if self.circuit.is_running:
            self.circuit.stop_simulation()
            self.sim_action.setText("▶ Simülasyon Başlat")
            self.statusBar.showMessage("Simülasyon durduruldu")
        else:
            self.circuit.start_simulation()
            self.sim_action.setText("⏸ Simülasyon Durdur")
            self.statusBar.showMessage("Simülasyon çalışıyor")
        self.canvas.update()
        
    def reset_simulation(self):
        self.circuit.reset()
        self.canvas.update()
        self.statusBar.showMessage("Simülasyon sıfırlandı")
        
    def step_simulation(self):
        self.circuit.step()
        self.canvas.update()
        
    def export_verilog(self):
        """Verilog kodu üret ve göster"""
        try:
            generator = VerilogGenerator(self.circuit)
            verilog_code = generator.generate()
            
            # Verilog kodunu göster
            from gui.verilog_dialog import VerilogDialog
            dialog = VerilogDialog(verilog_code, self)
            dialog.exec()
            
            self.statusBar.showMessage("Verilog kodu üretildi")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Verilog kodu üretilemedi: {str(e)}")
            
    def export_png(self):
        filename, _ = QFileDialog.getSaveFileName(self, "PNG Olarak Kaydet", "", 
                                                  "PNG Dosyası (*.png);;Tüm Dosyalar (*)")
        if filename:
            if not filename.endswith('.png'):
                filename += '.png'
            self.canvas.export_png(filename)
            self.statusBar.showMessage(f"PNG kaydedildi: {filename}")
            
    def show_about(self):
        QMessageBox.about(self, "LSFL Hakkında",
                         "<h2>LSFL - Logic Sim For Linux</h2>"
                         "<p>Modern mantık devresi simülatörü ve Verilog kod üreteci</p>"
                         "<p>Sürüm: 1.0.0</p>"
                         "<p>© 2026 LSFL Project</p>")
