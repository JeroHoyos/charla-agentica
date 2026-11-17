import os

import manimpango

_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")

# Como en las guías de Commit Academy: Archivo Black para títulos, Lexend para el texto y
# JetBrains Mono para rótulos y etiquetas.
_ARCHIVOS = (
    "PressStart2P-Regular.ttf",
    "ArchivoBlack-Regular.ttf",
    "Lexend-Regular.ttf",
    "Lexend-Medium.ttf",
    "Lexend-SemiBold.ttf",
    "Lexend-Bold.ttf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
    "JetBrainsMono-SemiBold.ttf",
    "JetBrainsMono-Bold.ttf",
    "JetBrainsMono-BoldItalic.ttf",
)

_registradas = False


def registrar():
    global _registradas
    if _registradas:
        return
    for archivo in _ARCHIVOS:
        manimpango.register_font(os.path.join(_DIR, archivo))
    _registradas = True


registrar()
