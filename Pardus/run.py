#!/usr/bin/env python3

import os
import sys

# Ana dizini Python path'ine ekle
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
