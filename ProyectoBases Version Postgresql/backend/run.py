import sys
import os

# Agregar la carpeta backend al path para que encuentre el módulo app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app