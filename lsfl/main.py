#!/usr/bin/env python3
"""
LSFL - Logic Sim For Linux
Modern mantık devresi simülatörü ve Verilog kod üreteci
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.welcome_dialog import WelcomeDialog
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LSFL")
    app.setOrganizationName("LSFL")
    
    # Uygulama ikonunu ayarla
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "logo.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Welcome dialog göster
    welcome = WelcomeDialog()
    if welcome.exec():
        # Ana pencereyi oluştur
        window = MainWindow()
        
        # Seçilen aksiyona göre işlem yap
        if welcome.selected_action == "open" and welcome.selected_file:
            try:
                window.circuit.load(welcome.selected_file)
                window.canvas.load_circuit()
                window.statusBar.showMessage(f"Circuit loaded: {welcome.selected_file}")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(window, "Error", f"Could not load circuit: {str(e)}")
        
        window.show()
        sys.exit(app.exec())
    else:
        # Dialog kapatıldı, uygulamadan çık
        sys.exit(0)

if __name__ == "__main__":
    main()
