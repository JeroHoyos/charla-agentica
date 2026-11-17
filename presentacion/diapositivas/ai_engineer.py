"""Los cuatro roles de datos. Cada persona va vestida para su oficio y con algo de su trabajo al
lado, todo en 3D: el analista de traje con su gráfica, el ingeniero de datos de plomero con su
tubería, la científica de bata con su campana de Gauss y el AI Engineer con el robot (el modelo)."""
import numpy as np
from manim import RIGHT, UP, FadeIn, LaggedStart, VGroup

from comun.animaciones import teclear
from comun.componentes import SEMI, caja, centrado, chip, pixel, tarjeta, titulo
from comun.estilo import CIAN, FONDO, FONDO_OSCURO, GRIS_LINEA, GRIS_MEDIO, LILA, ORO, TEAL, TINTA, VERDE
from comun.tres_d import (
    BLANCO,
    CUERO,
    ROJO,
    VIDRIO,
    figura,
    mezcla,
    mover,
    partes_persona,
    partes_robot,
)

TRAJE, OVEROL, BATA = "#4a5a78", "#3b6ea5", "#dfe8ee"


def _base(ancho, fondo):
    """La tarima donde va el objeto de cada oficio."""
    return ((0, 0.03, 0), (ancho, 0.03, fondo), GRIS_MEDIO, None)


def _analista():
    """De traje y corbata, con maletín; al lado, una gráfica de barras que sube."""
    persona = list(partes_persona(TRAJE)) + [
        ((0, 0.9, 0.262), (0.1, 0.16, 0.006), BLANCO, None, 1),          # camisa
        ((0, 0.84, 0.27), (0.035, 0.18, 0.006), ORO, None, 2),           # corbata
        ((0, 1.02, 0.27), (0.05, 0.035, 0.006), mezcla(ORO, FONDO_OSCURO, 0.2), None, 2),
        ((-0.52, 0.2, 0.06), (0.07, 0.15, 0.22), CUERO, None),           # maletín
        ((-0.52, 0.38, 0.06), (0.03, 0.03, 0.08), mezcla(CUERO, FONDO_OSCURO, 0.3), None),
    ]
    barras = [_base(0.5, 0.28)] + [
        ((x, 0.06 + h / 2, 0), (0.11, h / 2, 0.11), mezcla(ORO, FONDO_OSCURO, t), None)
        for x, h, t in ((-0.3, 0.45, 0.35), (0, 0.78, 0.18), (0.3, 1.15, 0.0))]
    return persona + list(mover(barras, dx=1.25))


def _ingeniero():
    """De plomero: overol y llave inglesa; al lado, la tubería por donde salen los datos."""
    persona = list(partes_persona(VERDE))
    persona[0] = ((-0.2, 0.17, 0), (0.13, 0.17, 0.16), OVEROL, None)
    persona[1] = ((0.2, 0.17, 0), (0.13, 0.17, 0.16), OVEROL, None)
    persona += [
        ((0, 0.6, 0.262), (0.3, 0.26, 0.006), OVEROL, None, 1),         # peto
        ((-0.2, 0.96, 0.262), (0.05, 0.1, 0.006), OVEROL, None, 1),     # tirantes
        ((0.2, 0.96, 0.262), (0.05, 0.1, 0.006), OVEROL, None, 1),
        ((0.52, 0.22, 0.12), (0.03, 0.17, 0.03), GRIS_LINEA, None),     # llave inglesa
        ((0.52, 0.04, 0.12), (0.08, 0.05, 0.035), GRIS_LINEA, None),
    ]
    tubo, union = GRIS_LINEA, GRIS_MEDIO
    tuberia = [
        ((0, 0.62, 0), (0.1, 0.5, 0.1), tubo, None),
        ((0, 0.14, 0), (0.14, 0.14, 0.14), union, None),
        ((0, 1.18, 0), (0.14, 0.14, 0.14), union, None),
        ((0.38, 1.18, 0), (0.26, 0.1, 0.1), tubo, None),
        ((0.67, 1.18, 0), (0.04, 0.14, 0.14), union, None),
        ((0, 0.66, 0.13), (0.17, 0.17, 0.02), ROJO, None, 1),           # la llave de paso
        ((0.82, 0.98, 0), (0.06, 0.06, 0.06), VERDE, None),             # los datos que salen
        ((0.86, 0.72, 0), (0.06, 0.06, 0.06), mezcla(VERDE, FONDO_OSCURO, 0.2), None),
    ]
    return persona + list(mover(tuberia, dx=1.15))


def _cientifica():
    """De bata, gafas y lapiceros en el bolsillo; al lado, un histograma con forma de campana."""
    persona = list(partes_persona(BATA)) + [
        ((0, 0.9, 0.262), (0.1, 0.16, 0.006), LILA, None, 1),           # la camisa bajo la bata
        ((0.22, 0.86, 0.264), (0.08, 0.07, 0.006), mezcla(BATA, FONDO_OSCURO, 0.15), None, 1),
        ((0.19, 0.95, 0.27), (0.015, 0.05, 0.006), LILA, None, 2),      # lapiceros
        ((0.25, 0.95, 0.27), (0.015, 0.05, 0.006), ROJO, None, 2),
        ((-0.15, 1.5, 0.365), (0.11, 0.09, 0.005), VIDRIO, None, 0.5),  # gafas
        ((0.15, 1.5, 0.365), (0.11, 0.09, 0.005), VIDRIO, None, 0.5),
        ((0, 1.53, 0.365), (0.05, 0.015, 0.005), GRIS_MEDIO, None, 0.5),
    ]
    campana = [_base(0.6, 0.2)]
    for i, x in enumerate(np.linspace(-0.48, 0.48, 7)):
        h = 0.08 + 1.1 * np.exp(-x * x / (2 * 0.25 ** 2))
        tono = mezcla(LILA, FONDO_OSCURO, 0.25 if i % 2 else 0.0)
        campana.append(((x, 0.06 + h / 2, 0), (0.07, h / 2, 0.11), tono, None))
    return persona + list(mover(campana, dx=1.32))


def _ai_engineer():
    """Quien construye con modelos, con el robot de la portada al lado."""
    return list(partes_persona(TEAL)) + list(mover(partes_robot(CIAN, luz=1.0), dx=1.35,
                                                   escala=0.82))


ROLES = (
    ("Data Analyst", "Cuenta qué pasó", ORO, _analista),
    ("Data Engineer", "Mueve los datos", VERDE, _ingeniero),
    ("Data Scientist", "Predice con datos", LILA, _cientifica),
    ("AI Engineer", "Construye con modelos", TEAL, _ai_engineer),
)
X0, X1, HUECO, Y0, Y1 = 96, 1344, 20, 180, 690
ANCHO = (X1 - X0 - 3 * HUECO) / 4
Y_PIE, ALTO, GIRO = 500, 215, 0.35


def _rol(i, nombre, verbo, color, partes):
    x0 = X0 + i * (ANCHO + HUECO)
    cx = x0 + ANCHO / 2
    contenido = VGroup(figura(partes(), cx, Y_PIE, ALTO, GIRO),
                       pixel(nombre, 21, cx, 570, color=TINTA),
                       centrado(verbo, 21, cx, 612, color=color, peso=SEMI))
    return tarjeta(x0, Y0, x0 + ANCHO, Y1), contenido


def _velo(i):
    """Apaga un cuadro: un velo del color del fondo encima (bajar la opacidad de las figuras
    dejaría ver sus caras de atrás)."""
    x0 = X0 + i * (ANCHO + HUECO)
    return caja(x0 - 2, Y0 - 2, x0 + ANCHO + 2, Y1 + 2, FONDO, radio=13, opacidad=0.62)


def construir(scene):
    scene.marco.ir("fundamentos", "0.1")
    roles = [_rol(i, *r) for i, r in enumerate(ROLES)]
    nuestro = roles[-1][0]
    sello = chip("ESTA CHARLA", X1 - 14, Y0 + 26, tam=12, alinear=RIGHT)

    scene.play(teclear(titulo("¿Qué hace un AI Engineer?")), run_time=0.8)
    scene.play(LaggedStart(*[LaggedStart(FadeIn(t, shift=UP * 0.2), FadeIn(c, shift=UP * 0.1),
                                         lag_ratio=0.3) for t, c in roles], lag_ratio=0.3),
               run_time=2.4)
    scene.next_slide()
    scene.play(nuestro.animate.set_stroke(TEAL, width=4),
               *[FadeIn(_velo(i)) for i in range(len(ROLES) - 1)],
               FadeIn(sello, scale=0.8), run_time=0.6)
