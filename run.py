#!/usr/bin/env python3
"""
LSFL Başlatıcı - Proje kök dizininden çalıştırma
"""

import sys
import os

# lsfl modülünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lsfl'))

# Ana programı çalıştır
from lsfl.main import main

if __name__ == "__main__":
    main()
