# Windows: doble clic aqui para abrir la interfaz del portal (sin ventana negra).
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

import app  # noqa: E402

app.main()
