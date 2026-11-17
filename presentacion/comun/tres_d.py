"""Figuras en 3D hechas de cajas, las de la portada: cada caja se gira, se proyecta y se pintan
sus caras visibles de atrás hacia adelante, con más o menos luz según hacia dónde miran.

La portada las repinta en cada cuadro para animarlas; las analogías usan `figura()`, que
devuelve el dibujo ya quieto (un robot, una persona) para moverlo entero por la escena."""

import numpy as np
from manim import Polygon, VGroup

from .estilo import (
    CIAN,
    FONDO_OSCURO,
    GRIS_LINEA,
    GRIS_MEDIO,
    LILA,
    OSCURO,
    VERDE,
    G,
    P,
)

BLANCO = "#f4f8fa"
PANTALLA = "#0a1820"
PIEL, PELO, PANTALON = "#f1c9a5", "#6b5144", "#0a1820"

INCLINACION = np.radians(26)  # cuánto mira la cámara hacia abajo
LUZ = np.array([-0.5, 0.5, 0.7]) / np.linalg.norm([-0.5, 0.5, 0.7])

# Las ocho esquinas de una caja y sus seis caras.
_ESQUINAS = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)])
_CARAS = ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5))


def mezcla(a, b, t):
    """Color entre `a` (t = 0) y `b` (t = 1)."""
    ca, cb = ([int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in (a, b))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def camara(p):
    """Puntos del mundo vistos por la cámara: x a la derecha, y arriba, z hacia quien mira."""
    c, s = np.cos(INCLINACION), np.sin(INCLINACION)
    x, y, z = p.T
    return np.stack([x, y * c - z * s, z * c + y * s], axis=1)


def girar(v, giro):
    """Gira los puntos alrededor del eje vertical."""
    c, s = np.cos(giro), np.sin(giro)
    x, y, z = v.T
    return np.stack([x * c + z * s, y, -x * s + z * c], axis=1)


def levantar(v, angulo):
    """Sube el brazo hacia adelante alrededor del hombro, sin salirse del ancho del robot."""
    hombro = np.array([0.58, 1.0, 0.0])
    c, s = np.cos(angulo), np.sin(angulo)
    x, y, z = (v - hombro).T
    return np.stack([x, y * c + z * s, -y * s + z * c], axis=1) + hombro


def caras_caja(q, color):
    """Las caras de una caja (ya en cámara) que miran hacia quien ve: profundidad, puntos y
    color con su luz."""
    centro = q.mean(axis=0)
    for indices in _CARAS:
        cara = q[list(indices)]
        n = np.cross(cara[1] - cara[0], cara[2] - cara[0])
        n = n / np.linalg.norm(n)
        if n @ (cara.mean(axis=0) - centro) < 0:
            n = -n
        if n[2] > 0.01:
            sombra = 0.5 * (1 - max(0.0, n @ LUZ))
            yield cara[:, 2].mean(), cara, mezcla(color, FONDO_OSCURO, sombra)


def caras(partes, mundo, escala=1.0):
    """Las caras visibles de una figura, de atrás hacia adelante. `partes` son sus cajas:
    centro, medio tamaño, color, giro del brazo (o None, o una función que mueve sus puntos) y, si va pintada sobre otra, su capa.
    `mundo` lleva los puntos de la figura a su lugar."""
    lista = []
    for centro, medio, color, brazo, *encima in partes:
        v = np.array(centro) + _ESQUINAS * np.array(medio)
        if callable(brazo):
            v = brazo(v)
        elif brazo is not None:
            v = levantar(v, brazo)
        # Lo pintado sobre una cara (pantallas, ojos) va siempre después que ella.
        adelante = 0.4 * escala * sum(encima)
        lista += [(fondo + adelante, cara, tono)
                  for fondo, cara, tono in caras_caja(camara(mundo(v)), color)]
    return sorted(lista, key=lambda cara: cara[0])


AMARILLO, ROJO, CUERO, VIDRIO = "#f2c230", "#d9534a", "#7a5a44", "#bfeaf1"

# Los oficios de los robots pequeños: lo que cada uno lleva puesto o en la mano, para que no
# se distingan solo por el color.
OFICIOS = {
    # Casco de obra: más ancho y hondo que la cabeza, para taparla entera, y la visera al frente.
    "ingeniero": (
        ((0, 1.98, 0), (0.6, 0.11, 0.46), AMARILLO, None),
        ((0, 1.9, 0.58), (0.6, 0.025, 0.14), mezcla(AMARILLO, FONDO_OSCURO, 0.12), None),
    ),
    # Gafas y una gráfica de barras en la pantalla del cuerpo.
    "analista": (
        ((-0.2, 1.52, 0.445), (0.15, 0.15, 0.006), VIDRIO, None, 1.5),
        ((0.2, 1.52, 0.445), (0.15, 0.15, 0.006), VIDRIO, None, 1.5),
        ((0, 1.56, 0.445), (0.06, 0.025, 0.006), VIDRIO, None, 1.5),
        ((-0.12, 0.66, 0.335), (0.04, 0.06, 0.008), BLANCO, None, 3),
        ((0, 0.69, 0.335), (0.04, 0.09, 0.008), BLANCO, None, 3),
        ((0.12, 0.72, 0.335), (0.04, 0.12, 0.008), BLANCO, None, 3),
    ),
    # Corbatín y maletín.
    "abogado": (
        ((-0.09, 0.97, 0.31), (0.07, 0.055, 0.012), ROJO, None, 1),
        ((0.09, 0.97, 0.31), (0.07, 0.055, 0.012), ROJO, None, 1),
        ((0, 0.97, 0.32), (0.03, 0.03, 0.012), mezcla(ROJO, FONDO_OSCURO, 0.3), None, 2),
        ((-0.62, 0.3, 0.12), (0.17, 0.13, 0.06), CUERO, None),
        ((-0.62, 0.45, 0.12), (0.07, 0.025, 0.02), mezcla(CUERO, FONDO_OSCURO, 0.3), None),
    ),
    # Lápiz en una mano y una hoja en la otra.
    "redactor": (
        ((0.62, 0.62, 0.2), (0.035, 0.24, 0.035), AMARILLO, None),
        ((0.62, 0.9, 0.2), (0.035, 0.04, 0.035), ROJO, None),
        ((0.62, 0.34, 0.2), (0.035, 0.04, 0.035), PANTALLA, None),
        ((-0.62, 0.5, 0.17), (0.14, 0.18, 0.012), BLANCO, None),
    ),
    # Diadema con audífonos y micrófono: el que atiende a los clientes.
    "asesor": (
        ((0, 1.95, 0), (0.62, 0.035, 0.07), GRIS_MEDIO, None),
        ((-0.64, 1.75, 0), (0.035, 0.2, 0.07), GRIS_MEDIO, None),
        ((0.64, 1.75, 0), (0.035, 0.2, 0.07), GRIS_MEDIO, None),
        ((-0.66, 1.5, 0), (0.07, 0.15, 0.15), PANTALLA, None),
        ((0.66, 1.5, 0), (0.07, 0.15, 0.15), PANTALLA, None),
        ((0.67, 1.36, 0.26), (0.025, 0.025, 0.24), GRIS_MEDIO, None),
        ((0.48, 1.3, 0.48), (0.2, 0.025, 0.025), GRIS_MEDIO, None),
        ((0.26, 1.3, 0.48), (0.06, 0.05, 0.04), ROJO, None),
    ),
    # Gorra de revisor de tren (azul, con banda dorada y visera), placa en el pecho y lupa.
    "revisor": (
        ((0, 2.0, 0), (0.6, 0.12, 0.46), "#1f3f73", None),
        ((0, 1.9, 0), (0.61, 0.035, 0.47), AMARILLO, None),
        ((0, 1.88, 0.58), (0.6, 0.025, 0.14), "#14284a", None),
        ((-0.2, 0.92, 0.31), (0.07, 0.07, 0.012), AMARILLO, None, 2),
        ((0.66, 1.0, 0.22), (0.17, 0.17, 0.025), VIDRIO, None),
        ((0.66, 0.68, 0.22), (0.03, 0.15, 0.03), GRIS_MEDIO, None),
    ),
    # Lupa en la mano y visera.
    "discriminador": (
        ((0.66, 1.0, 0.22), (0.17, 0.17, 0.025), VIDRIO, None),
        ((0.66, 0.68, 0.22), (0.03, 0.15, 0.03), GRIS_MEDIO, None),
        ((0, 1.8, 0.5), (0.5, 0.025, 0.1), VERDE, None),
    ),
}


def _balanceo(altura, angulo):
    """Mueve una pierna o un brazo hacia adelante (ángulo positivo) o hacia atrás, colgando
    de `altura`: el paso de quien camina."""
    if not angulo:
        return None
    c, s = np.cos(angulo), np.sin(angulo)

    def mueve(v):
        x, y, z = v.T
        return np.stack([x, altura + (y - altura) * c + z * s, z * c - (y - altura) * s], axis=1)

    return mueve


def partes_robot(color, luz=0.0, brazo=None, oficio=None, paso=0.0):
    """Las cajas del robot. `luz` (de 0 a 1) enciende el bombillo y la antena; `oficio` (una
    clave de OFICIOS) le pone lo que lleva; `paso` es cuánto lleva adelantada una pierna (y
    atrasada la otra, con los brazos al contrario) al caminar."""
    c2, c3 = mezcla(color, FONDO_OSCURO, 0.22), mezcla(color, FONDO_OSCURO, 0.45)
    bombillo = mezcla(c3, BLANCO, luz)
    if paso:
        brazo = (brazo or 0.0) - 0.8 * paso
    return (
        ((-0.24, 0.15, 0), (0.13, 0.15, 0.17), c3, _balanceo(0.3, -paso)),  # piernas
        ((0.24, 0.15, 0), (0.13, 0.15, 0.17), c3, _balanceo(0.3, paso)),
        ((0, 0.68, 0), (0.45, 0.38, 0.3), color, None),         # cuerpo
        ((0, 0.72, 0.31), (0.24, 0.15, 0.012), PANTALLA, None, 1),
        ((0.1, 0.76, 0.33), (0.05, 0.05, 0.01), bombillo, None, 2),
        ((-0.58, 0.72, 0), (0.1, 0.3, 0.12), c2, _balanceo(1.0, 0.8 * paso)),  # brazos
        ((0.58, 0.72, 0), (0.1, 0.3, 0.12), c2, brazo),
        ((0, 1.1, 0), (0.16, 0.05, 0.16), c3, None),            # cuello
        ((0, 1.52, 0), (0.56, 0.38, 0.42), color, None),        # cabeza
        ((0, 1.5, 0.43), (0.44, 0.24, 0.012), PANTALLA, None, 1),
        ((-0.2, 1.52, 0.45), (0.08, 0.1, 0.01), BLANCO, None, 2),  # ojos
        ((0.2, 1.52, 0.45), (0.08, 0.1, 0.01), BLANCO, None, 2),
        ((-0.6, 1.52, 0), (0.05, 0.12, 0.12), c2, None),        # orejas
        ((0.6, 1.52, 0), (0.05, 0.12, 0.12), c2, None),
        ((0, 2.02, 0), (0.03, 0.13, 0.03), GRIS_LINEA, None),   # antena
        ((0, 2.22, 0), (0.08, 0.08, 0.08), bombillo, None),
        *OFICIOS.get(oficio, ()),
    )


def partes_persona(ropa, gorra=None):
    """Las cajas de una persona, del mismo tamaño y estilo que el robot. Con `gorra`, lleva
    una de ese color (quien revisa)."""
    manga = mezcla(ropa, FONDO_OSCURO, 0.22)
    if gorra:
        arriba = (((0, 1.93, 0), (0.41, 0.1, 0.39), gorra, None),
                  ((0, 1.86, 0.52), (0.3, 0.03, 0.16), mezcla(gorra, FONDO_OSCURO, 0.15), None))
    else:
        arriba = (((0, 1.9, -0.03), (0.41, 0.07, 0.38), PELO, None),)
    return (
        ((-0.2, 0.17, 0), (0.13, 0.17, 0.16), PANTALON, None),  # piernas
        ((0.2, 0.17, 0), (0.13, 0.17, 0.16), PANTALON, None),
        ((0, 0.7, 0), (0.4, 0.36, 0.26), ropa, None),           # cuerpo
        ((-0.52, 0.74, 0), (0.1, 0.3, 0.12), manga, None),      # brazos
        ((0.52, 0.74, 0), (0.1, 0.3, 0.12), manga, None),
        ((-0.52, 0.4, 0), (0.09, 0.06, 0.1), PIEL, None),       # manos
        ((0.52, 0.4, 0), (0.09, 0.06, 0.1), PIEL, None),
        ((0, 1.1, 0), (0.13, 0.05, 0.13), mezcla(PIEL, FONDO_OSCURO, 0.2), None),
        ((0, 1.49, 0), (0.38, 0.34, 0.35), PIEL, None),         # cabeza
        ((0, 1.52, -0.33), (0.41, 0.33, 0.08), PELO, None),     # pelo, por detrás
        ((-0.15, 1.5, 0.36), (0.045, 0.065, 0.01), OSCURO, None, 1),  # ojos
        ((0.15, 1.5, 0.36), (0.045, 0.065, 0.01), OSCURO, None, 1),
        *arriba,
    )


def partes_computador():
    """Un portátil abierto: la base con su teclado y la pantalla con las celdas de un
    notebook (cuatro barras de colores)."""
    celdas = ((-0.2, 1.08, 0.58, CIAN), (-0.36, 0.86, 0.42, GRIS_LINEA), (-0.1, 0.64, 0.68, LILA),
              (-0.3, 0.42, 0.48, VERDE))
    return (
        ((0, 0.04, 0.4), (1.0, 0.04, 0.62), GRIS_LINEA, None),            # base
        ((0, 0.082, 0.34), (0.84, 0.004, 0.4), GRIS_MEDIO, None, 1),      # teclado
        ((0, 0.76, -0.25), (1.0, 0.68, 0.035), GRIS_LINEA, None),         # tapa
        ((0, 0.76, -0.212), (0.9, 0.58, 0.004), PANTALLA, None, 1),       # pantalla
        *[((x, y, -0.205), (ancho, 0.065, 0.003), color, None, 2)
          for x, y, ancho, color in celdas],
    )


def mover(partes, dx=0.0, dz=0.0, escala=1.0):
    """Las mismas cajas, más grandes o más pequeñas y corridas en el suelo: para juntar
    varias figuras en un solo dibujo."""
    return tuple((tuple(np.array(centro) * escala + (dx, 0, dz)), tuple(np.array(medio) * escala),
                  *resto) for centro, medio, *resto in partes)


def figura(partes, cx, piso, alto, giro=0.0):
    """La figura ya dibujada y quieta: de pie en `piso`, centrada en `cx`, de `alto` pt del
    lienzo y girada `giro` (positivo, mira a la derecha)."""
    lista = caras(partes, lambda v: girar(v, giro))
    puntos = np.concatenate([cara for _, cara, _ in lista])
    k = alto / (puntos[:, 1].max() - puntos[:, 1].min())
    medio, abajo = (puntos[:, 0].max() + puntos[:, 0].min()) / 2, puntos[:, 1].min()
    dibujo = VGroup()
    for _, cara, tono in lista:
        esquinas = [P(cx + k * (x - medio), piso - k * (y - abajo)) for x, y, _ in cara]
        dibujo.add(Polygon(*esquinas).set_fill(tono, opacity=1).set_stroke(tono, width=G(0.5)))
    return dibujo
