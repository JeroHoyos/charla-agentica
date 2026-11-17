from manim import LEFT, RIGHT, UP, FadeIn, GrowFromEdge, LaggedStart, VGroup

from comun.animaciones import teclear
from comun.componentes import SEMI, caja, nota, tarjeta, texto, titulo
from comun.estilo import GRIS, GRIS_MEDIO, TEAL, TINTA

# Porcentaje de las llamadas a herramientas en cada dominio (Anthropic, 2026).
DOMINIOS = (
    ("Ingeniería de software", 49.7),
    ("Automatización de back-office", 9.1),
    ("Otros", 7.1),
    ("Marketing y redacción", 4.4),
    ("Ventas y CRM", 4.3),
    ("Finanzas y contabilidad", 4.0),
    ("Análisis de datos y BI", 3.5),
    ("Investigación académica", 2.8),
    ("Ciberseguridad", 2.4),
    ("Servicio al cliente", 2.2),
    ("Videojuegos y medios interactivos", 2.1),
    ("Documentos y presentaciones", 1.9),
    ("Educación y tutorías", 1.8),
    ("Comercio electrónico", 1.3),
    ("Medicina y salud", 1.0),
    ("Legal", 0.9),
    ("Viajes y logística", 0.8),
)
FUENTES = ("Porcentaje de llamadas a herramientas. Fuentes: "
           "anthropic.com/research/measuring-agent-autonomy, claude.com/solutions/agents")

# Las barras salen de X_BARRA; el 49,7 % mide LARGO pt.
X_BARRA, LARGO, PASO = 440, 760, 28


def _fila(i, nombre, valor):
    cy = 204 + PASO * i
    primero = i == 0
    color = TEAL if primero else GRIS_MEDIO
    fin = X_BARRA + LARGO * valor / DOMINIOS[0][1]
    etiqueta = texto(nombre, 16, X_BARRA - 16, cy + 6, color=TINTA if primero else GRIS,
                     peso=SEMI if primero else "NORMAL", alinear=RIGHT)
    barra = caja(X_BARRA, cy - 9, fin, cy + 9, color, radio=3)
    cifra = texto(f"{valor:.1f} %".replace(".", ","), 16, fin + 10, cy + 6,
                  color=TEAL if primero else TINTA, peso=SEMI)
    return etiqueta, barra, cifra


def construir(scene):
    scene.marco.ir("inicio")
    filas = [_fila(i, *d) for i, d in enumerate(DOMINIOS)]
    etiquetas, barras, cifras = (VGroup(*columna) for columna in zip(*filas))

    scene.play(teclear(titulo("¿Dónde trabajan hoy los agentes?")), run_time=0.7)
    scene.play(FadeIn(tarjeta(96, 176, 1344, 680), shift=UP * 0.2), FadeIn(etiquetas),
               FadeIn(nota(FUENTES, base=716)), run_time=0.7)
    scene.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in barras], lag_ratio=0.08),
               run_time=1.8)
    scene.play(FadeIn(cifras, shift=RIGHT * 0.1), run_time=0.5)
