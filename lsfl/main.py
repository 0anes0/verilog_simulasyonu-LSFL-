#!/usr/bin/env python3
"""
LSFL - Logic Sim For Linux
Modern mantık devresi simülatörü ve Verilog kod üreteci
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LSFL")
    app.setOrganizationName("LSFL")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
