import os

import numpy as np
from manim import config

from . import fuentes  # noqa: F401  registra las fuentes al importarse

# Toda la charla va en oscuro, como la portada y «pronto iniciamos». Los nombres dicen para
# qué sirve cada color, no cómo se ve: TINTA es el texto (claro), OSCURO lo que va escrito
# sobre un relleno de color, los «_SUAVE» son rellenos apagados y los «_OSCURO» (y TEAL y
# MORADO), el color para escribir sobre el fondo.
FONDO = "#0c1f2a"
FONDO_PORTADA = FONDO
TARJETA = "#132e3c"
TINTA = "#f4f8fa"
OSCURO = "#0c1f2a"
GRIS = "#9db4be"
NOTA = "#8fa7b1"
TEXTO_SUAVE = "#c3d3da"
GRIS_LINEA = "#8fa7b1"
GRIS_MEDIO = "#5d7a87"
# Bordes y separadores: apenas se despegan del fondo.
GRIS_CLARO = "#2b4b5b"
CELESTE = "#1a3a49"

CIAN = "#2ac3d8"
TEAL = CIAN
CIAN_SUAVE = "#134350"
VERDE = "#4ad1a6"
VERDE_OSCURO = VERDE
VERDE_SUAVE = "#1a4645"
ORO = "#cca755"
ORO_SUAVE = "#363d33"
LILA = "#ab95f2"
MORADO = LILA
LILA_SUAVE = "#2f3956"
# Para fallos, bloqueos y guardrails.
CORAL = "#e2725b"
CORAL_OSCURO = "#f08a75"
CORAL_SUAVE = "#3b3135"


PIXEL = "Press Start 2P"
MONO = "JetBrains Mono"
# Diseño de las guías de Commit Academy: títulos gruesos, texto sin serifa y rótulos en mono.
TITULAR = "Archivo"
SANS = "Lexend"
FONDO_OSCURO = FONDO

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
IMAGENES = os.path.join(ASSETS, "imagenes")

# Todo se ubica en un lienzo de 1440 × 810 pt (y hacia abajo), igual que en la charla de la
# ASA, y se convierte aquí a unidades de manim.
ANCHO_PDF, ALTO_PDF = 1440, 810
U = config.frame_width / ANCHO_PDF

# Con font_size = 72 una letra mide 1 unidad de manim de cuerpo (medido a mano).
FS = 72 * U


def P(x, y):
    return np.array([(x - ANCHO_PDF / 2) * U, (ALTO_PDF / 2 - y) * U, 0.0])


def G(pt):
    """Grosor de trazo de manim para una línea de `pt` puntos del lienzo."""
    return pt * U * 100


AZUL = "#5b8def"
AZUL_OSCURO = "#8fb1f5"
AZUL_SUAVE = "#1d3755"

# Secciones: número, nombre, color de la raya, color del rótulo y relleno apagado. Del 01 al 05,
# el número del bloque es el de su notebook.
SECCIONES = {
    "inicio": ("", "INICIO", CIAN, TEAL, CIAN_SUAVE),
    "fundamentos": ("00", "FUNDAMENTOS", CIAN, TEAL, CIAN_SUAVE),
    "llamada": ("01", "UNA LLAMADA BIEN HECHA", LILA, MORADO, LILA_SUAVE),
    "anatomia": ("01", "ANATOMÍA DE UN AGENTE", CIAN, TEAL, CIAN_SUAVE),
    "interacciones": ("03", "EL AGENTE Y SU ENTORNO", CIAN, TEAL, CIAN_SUAVE),
    "patrones": ("04", "PATRONES", AZUL, AZUL_OSCURO, AZUL_SUAVE),
    "proyecto": ("05", "MINI PROYECTO", CORAL, CORAL_OSCURO, CORAL_SUAVE),
    "cierre": ("", "CIERRE", CIAN, TEAL, CIAN_SUAVE),
}
