"""La portada del bloque de fundamentos: el título en grande a la izquierda y, a la derecha,
una escena en 3D: el robot ingeniero manda a trabajar a uno más pequeño, que se sienta en su
puesto y se pone a teclear.

Todo lo que se mueve va en un solo mobject que se repinta en cada cuadro, de atrás hacia
adelante (como en la portada)."""
import numpy as np
from manim import (
    Circle,
    Ellipse,
    UP,
    FadeIn,
    Polygon,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    smooth,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import titular
from comun.estilo import CIAN, FONDO_OSCURO, LILA, ORO, SECCIONES, VERDE, G, P, U
from comun.tres_d import (
    BLANCO,
    INCLINACION,
    camara,
    caras,
    mezcla,
    mover,
    partes_computador,
    partes_robot,
)

CLAVE = "fundamentos"
X = 92
CX, CY, K = 1063, 580, 118   # el suelo en el centro de la escena y pt por unidad del modelo
VUELTA = 4.0                 # segundos de cada vuelta del loop
HUECOS = 280                # trazos de sobra para todo lo que se pinta en un cuadro

MADERA, MADERA_OSCURA, METAL = "#c2a273", "#96784b", "#3a6578"
# El puesto, en las medidas del robot que se sienta: el banco bajo su cuerpo y la mesa al frente.
BANCO = (((0, 0.15, -0.02), (0.3, 0.15, 0.26), METAL, None),)
MESA = (((-0.68, 0.29, 1.0), (0.04, 0.29, 0.34), MADERA_OSCURA, None),
        ((0.68, 0.29, 1.0), (0.04, 0.29, 0.34), MADERA_OSCURA, None),
        ((0, 0.62, 1.0), (0.75, 0.04, 0.4), MADERA, None))
PORTATIL = mover(partes_computador(), escala=0.42)
CELDAS = (CIAN, VERDE, LILA, ORO)


def _px(q):
    return [(CX + K * x, CY - K * y) for x, y, _ in q]


def _mundo(v, r):
    """Puntos de una figura (con su tamaño, su giro y su salto) en el mundo."""
    c, s = np.cos(r["giro"]), np.sin(r["giro"])
    x, y, z = (v * r["escala"]).T
    return np.stack([x * c + z * s + r["x"], y + r["salto"], -x * s + z * c + r["z"]], axis=1)


def _en_pantalla(punto, r):
    """Un punto de la figura, en el lienzo."""
    return _px(camara(_mundo(np.array([punto], dtype=float), r)))[0]


def _poligonos(partes, mundo, escala):
    return [Polygon(*[P(*p) for p in _px(cara)]).set_fill(color, opacity=1)
            .set_stroke(color, width=G(0.5)) for _, cara, color in caras(partes, mundo, escala)]


def _sombra(r, ancho=1.5):
    lado = ancho * r["escala"] * K * U / (1 + r["salto"])
    centro = _px(camara(np.array([[r["x"], 0.0, r["z"]]])))[0]
    return (Ellipse(width=lado, height=lado * np.sin(INCLINACION)).move_to(P(*centro))
            .set_fill("#000000", opacity=0.35).set_stroke(width=0))


def _robot(r):
    """El robot como está ahora. Al sentarse (`sentado` de 0 a 1) estira las piernas al frente."""
    partes = list(partes_robot(r["color"], r["luz"], r["brazo"], r["oficio"]))
    s = r["sentado"]
    for i, lado in enumerate((-1, 1)):
        partes[i] = ((0.24 * lado, 0.15 + 0.02 * s, 0.5 * s), (0.13, 0.15 - 0.03 * s, 0.17 + 0.05 * s),
                     partes[i][2], None)
    piezas = _poligonos(partes, lambda v: _mundo(v, r), r["escala"])
    brillo = Circle(radius=20 * r["escala"] * U).move_to(P(*_en_pantalla((0, 2.22, 0), r)))
    return [*piezas, brillo.set_stroke(width=0).set_fill(BLANCO, opacity=0.3 * r["luz"])]


def _celdas(puesto, t):
    """Lo que sale del trabajo: barras de colores (las celdas del notebook) que suben del portátil."""
    if t <= 0:
        return []
    x0, y0 = _en_pantalla((0, 1.2, 1.0), puesto)
    piezas = []
    for i, color in enumerate(CELDAS):
        f = (0.5 * t + i / len(CELDAS)) % 1   # se repite cada 2 s (así el loop no salta)
        w, cx, cy = 13 + 5 * (i % 3), x0 + 12 * (i - 1.5) - 45 * f, y0 - 95 * f
        barra = Polygon(*[P(cx + a * w, cy + b * 5) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
        piezas.append(barra.set_stroke(width=0)
                      .set_fill(color, opacity=np.sin(np.pi * f) * min(1.0, 2 * t)))
    return piezas


def _puesto(puesto, t):
    """La sombra del puesto y, aparte, el banco y la mesa con el portátil (y sus celdas cuando
    se trabaja), cada uno con su profundidad para ordenarlos con lo demás."""
    mesa_z = puesto["z"] + np.cos(puesto["giro"]) * puesto["escala"]
    mesa = dict(puesto, x=puesto["x"] + np.sin(puesto["giro"]) * puesto["escala"], z=mesa_z)
    en_puesto = lambda v: _mundo(v, puesto)
    en_mesa = lambda v: _mundo(v * (-1, 1, -1) + (0, 0.66, 0.95), puesto)
    return _sombra(mesa, ancho=2.2), [
        (puesto["z"] - 0.01, _poligonos(BANCO, en_puesto, puesto["escala"])),
        (mesa_z, _poligonos(MESA, en_puesto, puesto["escala"])
         + _poligonos(PORTATIL, en_mesa, puesto["escala"]) + _celdas(puesto, t))]


def _escena(e):
    """Todo en orden: las sombras y, encima, cada cosa de la más lejana a la más cercana."""
    grande, chico, puesto, t = e["grande"], e["chico"], e["puesto"], e["obra"]["t"]
    if t > 0:
        chico["brazo"] = 1.2 + 0.2 * np.sin(2 * np.pi * 2.5 * t)
    cosas, piezas = [], []
    for r in (grande, chico):
        if r["escala"] > 0.05:
            piezas.append(_sombra(r))
            cosas.append((r["z"], _robot(r)))
    if puesto["escala"] > 0.05:
        sombra, partes = _puesto(puesto, t)
        piezas.append(sombra)
        cosas += partes
    for _, dibujo in sorted(cosas, key=lambda cosa: cosa[0]):
        piezas += dibujo
    return piezas


def _pintar(escenario):
    """Copia el dibujo de este cuadro en los trazos fijos del escenario (nunca se cambian por
    otros: manim pintaría también los del primer cuadro)."""
    piezas = escenario.dibujar(escenario.estado)
    assert len(piezas) <= HUECOS
    for hueco, pieza in zip(escenario, piezas):
        hueco.points = pieza.points
        hueco.match_style(pieza)
    for hueco in escenario[len(piezas):]:
        hueco.clear_points()


def _cambio(estado, inicio=0.0, fin=1.0, curva=smooth, **hasta):
    """Un cambio de un estado, entre `inicio` y `fin` (de 0 a 1) de la animación."""
    return estado, hasta, inicio, fin, curva


def _animar(escenario, *cambios, run_time=1.0):
    desde = [{k: estado[k] for k in hasta} for estado, hasta, *_ in cambios]

    def paso(mob, alpha):
        for (estado, hasta, inicio, fin, curva), antes in zip(cambios, desde):
            t = curva(float(np.clip((alpha - inicio) / (fin - inicio), 0, 1)))
            for k, v in hasta.items():
                estado[k] = antes[k] + (v - antes[k]) * t
        _pintar(escenario)

    return UpdateFromAlphaFunc(escenario, paso, run_time=run_time, rate_func=linear)


def _pasitos(t):
    """Dos pasitos: sube y baja dos veces."""
    return abs(np.sin(2 * np.pi * t))


def _alfombra(color):
    lado = 6.0 * K * U
    centro = _px(camara(np.array([[0.1, 0.0, 0.3]])))[0]
    return (Ellipse(width=lado, height=lado * np.sin(INCLINACION)).move_to(P(*centro))
            .set_fill(mezcla(color, FONDO_OSCURO, 0.86), opacity=1)
            .set_stroke(mezcla(color, FONDO_OSCURO, 0.4), width=G(2)))


def construir(scene):
    scene.marco.ir(CLAVE)
    color = SECCIONES[CLAVE][2]
    arriba = titular("Fundamentos", 80, X, 388)
    abajo = titular("del AI Engineer", 80, X, 476, t2c={"AI Engineer": color})

    quieto = dict(escala=0.0, salto=0.0, brazo=0.0, luz=0.0, sentado=0.0)
    grande = dict(quieto, color=color, oficio="ingeniero", x=1.45, z=-0.2, giro=-1.5)
    chico = dict(quieto, color=LILA, oficio="analista", x=0.35, z=0.95, giro=-0.8)
    puesto = dict(x=-0.5, z=0.4, giro=-1.1, escala=0.0, salto=0.0)
    obra = {"t": 0.0}
    escenario = VGroup(*[VMobject() for _ in range(HUECOS)])
    escenario.estado = dict(grande=grande, chico=chico, puesto=puesto, obra=obra)
    escenario.dibujar = _escena

    # El título se escribe mientras aparece el puesto de trabajo; después entran los dos robots.
    scene.play(teclear(arriba), FadeIn(_alfombra(color), scale=0.7), run_time=0.8)
    scene.play(teclear(abajo), _animar(escenario, _cambio(puesto, escala=0.95)), run_time=0.9)
    scene.play(_animar(escenario, _cambio(grande, 0.0, 0.55, escala=1.15, giro=-0.2),
                       _cambio(chico, 0.45, 1.0, escala=0.95, giro=0.5), run_time=2.2))
    # El ingeniero señala el puesto: «a trabajar». El pequeño da un brinco.
    scene.play(_animar(escenario, _cambio(grande, 0.0, 0.6, giro=-0.9, brazo=1.75, luz=1.0),
                       _cambio(chico, 0.45, 1.0, there_and_back, salto=0.22),
                       _cambio(chico, 0.45, 0.8, luz=1.0), run_time=1.7))
    # Va hasta el banco con dos pasitos, se sube de un salto y se sienta.
    scene.play(_animar(escenario, _cambio(chico, x=-0.05, z=0.65, giro=-1.1),
                       _cambio(chico, curva=_pasitos, salto=0.07), run_time=1.1))
    scene.play(_animar(escenario, _cambio(chico, x=puesto["x"], z=puesto["z"]),
                       _cambio(chico, curva=there_and_back, salto=0.4),
                       _cambio(chico, 0.3, 0.9, sentado=1.0),
                       _cambio(grande, brazo=0.0, giro=-0.35), run_time=1.2))
    # Y se pone a teclear: del portátil salen las celdas. El ingeniero queda contento.
    scene.play(_animar(escenario, _cambio(chico, brazo=1.2), run_time=0.6))
    scene.play(_animar(escenario, _cambio(obra, curva=linear, t=3.6),
                       _cambio(grande, 0.55, 0.85, there_and_back, salto=0.18), run_time=3.6),
               FadeIn(scene.indicador(), shift=UP * 0.1, run_time=0.3))
    # Sin parar, sigue en loop: teclea y salen celdas hasta que se pasa la diapositiva. Las celdas
    # se repiten cada 2 s y el brazo cada 0.4 s, así que 4 s cierran la vuelta sin salto.
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    scene.play(_animar(escenario, _cambio(obra, curva=linear, t=3.6 + VUELTA), run_time=VUELTA))
