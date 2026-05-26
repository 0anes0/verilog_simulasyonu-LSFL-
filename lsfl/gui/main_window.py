"""
Ana pencere ve kullanıcı arayüzü
"""

from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QDockWidget,
                              QVBoxLayout, QWidget, QPushButton, QMessageBox,
                              QFileDialog, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence
import os

from gui.canvas import Canvas
from gui.component_palette import ComponentPalette
from core.circuit import Circuit
from export.verilog_generator import VerilogGenerator
from core.i18n import tr, get_translator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.circuit = Circuit()
        self.translator = get_translator()
        
        # Menü ve action referanslarını sakla
        self.menu_file = None
        self.menu_edit = None
        self.menu_simulation = None
        self.menu_export = None
        self.menu_help = None
        
        self.action_new = None
        self.action_open = None
        self.action_save = None
        self.action_save_as = None
        self.action_exit = None
        
        self.init_ui()
        self.apply_translations()
        
        # Logo ikonunu ayarla
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
    def init_ui(self):
        self.setWindowTitle(tr("app_title"))
        # Daha küçük başlangıç boyutu ve maksimize edilebilir
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 600)
        
        # Canvas (merkezi widget)
        self.canvas = Canvas(self.circuit, self)
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(False)  # Canvas'ın kendi boyutunu kullan
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Toolbar
        self.create_toolbar()
        
        # Component Palette (sol dock)
        self.create_component_palette()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(tr("ready"))
        
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
        self.save_action = QAction("Kaydet", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_circuit)
        toolbar.addAction(self.save_action)
        
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
        self.palette_dock = QDockWidget(tr("components"), self)
        self.palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                            Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.palette = ComponentPalette(self.canvas)
        self.palette_dock.setWidget(self.palette)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.palette_dock)
        
    def apply_translations(self):
        """Çevirileri uygula - Tüm UI'ı güncelle"""
        self.retranslate_ui()
    
    def retranslate_ui(self):
        """Tüm arayüzü yeniden çevir - Menüler, toolbar, palette"""
        # Pencere başlığı
        self.setWindowTitle(tr("app_title"))
        
        # Status bar
        if not self.circuit.is_running:
            self.statusBar.showMessage(tr("ready"))
        
        # Toolbar butonları - mevcut action'ları güncelle
        if hasattr(self, 'sim_action'):
            self.sim_action.setText(tr("start_simulation") if not self.circuit.is_running else tr("stop_simulation"))
        
        # Menü başlıklarını güncelle
        if self.menu_file:
            self.menu_file.setTitle(tr("file"))
        if self.menu_edit:
            self.menu_edit.setTitle(tr("edit"))
        if self.menu_simulation:
            self.menu_simulation.setTitle(tr("simulation"))
        if self.menu_export:
            self.menu_export.setTitle(tr("export"))
        if self.menu_help:
            self.menu_help.setTitle(tr("help"))
        
        # Action metinlerini güncelle
        if self.action_new:
            self.action_new.setText(tr("new"))
        if self.action_open:
            self.action_open.setText(tr("open"))
        if self.action_save:
            self.action_save.setText(tr("save"))
        if self.action_save_as:
            self.action_save_as.setText(tr("save_as"))
        if self.action_exit:
            self.action_exit.setText(tr("exit"))
        
        # Component palette'i güncelle
        if hasattr(self, 'palette'):
            self.palette.retranslate_ui()
        
        # Palette dock başlığını güncelle
        if hasattr(self, 'palette_dock'):
            self.palette_dock.setWindowTitle(tr("components"))
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Dosya menüsü
        if self.menu_file is None:
            self.menu_file = menubar.addMenu(tr("file"))
        
        # Action'ları sadece bir kez oluştur
        if self.action_new is None:
            self.action_new = QAction(tr("new"), self)
            self.action_new.setShortcut(QKeySequence.StandardKey.New)
            self.action_new.triggered.connect(self.new_circuit)
            self.menu_file.addAction(self.action_new)
        
        if self.action_open is None:
            self.action_open = QAction(tr("open"), self)
            self.action_open.setShortcut(QKeySequence.StandardKey.Open)
            self.action_open.triggered.connect(self.open_circuit)
            self.menu_file.addAction(self.action_open)
        
        # Kaydet action'ı toolbar'dan kullan
        if self.save_action not in self.menu_file.actions():
            self.menu_file.addAction(self.save_action)
        
        if self.action_save_as is None:
            self.action_save_as = QAction(tr("save_as"), self)
            self.action_save_as.triggered.connect(self.save_circuit_as)
            self.menu_file.addAction(self.action_save_as)
        
        if len([a for a in self.menu_file.actions() if a.isSeparator()]) == 0:
            self.menu_file.addSeparator()
        
        if self.action_exit is None:
            self.action_exit = QAction(tr("exit"), self)
            self.action_exit.setShortcut(QKeySequence("Ctrl+Q"))
            self.action_exit.triggered.connect(self.close)
            self.menu_file.addAction(self.action_exit)
        
        # Düzenle menüsü
        if self.menu_edit is None:
            self.menu_edit = menubar.addMenu(tr("edit"))
            
            undo_action = QAction(tr("undo"), self)
            undo_action.setShortcut(QKeySequence.StandardKey.Undo)
            undo_action.triggered.connect(self.canvas.undo)
            self.menu_edit.addAction(undo_action)
            
            redo_action = QAction(tr("redo"), self)
            redo_action.setShortcut(QKeySequence.StandardKey.Redo)
            redo_action.triggered.connect(self.canvas.redo)
            self.menu_edit.addAction(redo_action)
            
            self.menu_edit.addSeparator()
            
            delete_action = QAction(tr("delete"), self)
            delete_action.setShortcut(QKeySequence.StandardKey.Delete)
            delete_action.triggered.connect(self.canvas.delete_selected)
            self.menu_edit.addAction(delete_action)
            
            select_all_action = QAction(tr("select_all"), self)
            select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
            select_all_action.triggered.connect(self.canvas.select_all)
            self.menu_edit.addAction(select_all_action)
        
        # Simülasyon menüsü
        if self.menu_simulation is None:
            self.menu_simulation = menubar.addMenu(tr("simulation"))
            
            toggle_sim_action = QAction(tr("start_stop"), self)
            toggle_sim_action.setShortcut(QKeySequence("Space"))
            toggle_sim_action.triggered.connect(self.toggle_simulation)
            self.menu_simulation.addAction(toggle_sim_action)
            
            reset_sim_action = QAction(tr("reset"), self)
            reset_sim_action.setShortcut(QKeySequence("Ctrl+R"))
            reset_sim_action.triggered.connect(self.reset_simulation)
            self.menu_simulation.addAction(reset_sim_action)
            
            self.menu_simulation.addSeparator()
            
            step_action = QAction(tr("step"), self)
            step_action.setShortcut(QKeySequence("Ctrl+T"))
            step_action.triggered.connect(self.step_simulation)
            self.menu_simulation.addAction(step_action)
        
        # Export menüsü
        if self.menu_export is None:
            self.menu_export = menubar.addMenu(tr("export"))
            
            verilog_export_action = QAction(tr("export_verilog"), self)
            verilog_export_action.setShortcut(QKeySequence("Ctrl+E"))
            verilog_export_action.triggered.connect(self.export_verilog)
            self.menu_export.addAction(verilog_export_action)
            
            png_export_action = QAction(tr("export_png"), self)
            png_export_action.triggered.connect(self.export_png)
            self.menu_export.addAction(png_export_action)
        
        # Yardım menüsü
        if self.menu_help is None:
            self.menu_help = menubar.addMenu(tr("help"))
            
            about_action = QAction(tr("about"), self)
            about_action.triggered.connect(self.show_about)
            self.menu_help.addAction(about_action)
        
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
            self.sim_action.setText(tr("start_simulation"))
            self.statusBar.showMessage(tr("stopped"))
            self.canvas.cancel_placing()
            # Global clock timer'ı durdur
            if hasattr(self, 'global_clock_timer'):
                self.global_clock_timer.stop()
        else:
            self.canvas.cancel_placing()
            self.circuit.start_simulation()
            self.sim_action.setText(tr("stop_simulation"))
            self.statusBar.showMessage(tr("running"))
            # Global clock timer'ı başlat
            self.start_global_clock()
        self.canvas.update()
    
    def start_global_clock(self):
        """Global clock generator - tüm Clock bileşenlerini senkronize çalıştır"""
        from PyQt6.QtCore import QTimer
        
        if not hasattr(self, 'global_clock_timer'):
            self.global_clock_timer = QTimer()
            self.global_clock_timer.timeout.connect(self.tick_global_clock)
        
        # 500ms periyot (1 Hz clock için)
        self.global_clock_timer.start(500)
    
    def tick_global_clock(self):
        """Her timer tick'inde tüm Clock bileşenlerini toggle et ve devreyi güncelle"""
        # 1. Tüm Clock bileşenlerini bul ve toggle et
        for component in self.circuit.components:
            if component.type == "CLOCK":
                component.state = not component.state
                component.output_pins[0].value = bool(component.state)
        
        # 2. ZORUNLU: Devreyi evaluate et (sinyal yayılımı)
        self.circuit.step()
        
        # 3. UI'ı güncelle (renkleri yenile)
        self.canvas.update()
        
    def reset_simulation(self):
        self.circuit.reset()
        self.canvas.update()
        self.statusBar.showMessage(tr("simulation_reset"))
        
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
            
            self.statusBar.showMessage(tr("verilog_generated"))
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
