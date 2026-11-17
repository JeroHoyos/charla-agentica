"""Las dos diapositivas de cada práctica: «Pasando a la práctica», igual siempre (el robot de
los fundamentos saluda, se sienta en su puesto y programa), y la del
notebook de esa práctica, con una celda por cada parte del notebook (salen de PRACTICAS)."""

import numpy as np
from manim import (
    LEFT,
    UP,
    FadeIn,
    GrowFromEdge,
    VGroup,
    VMobject,
    linear,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import (
    raya,
    titular,
)
from comun.estilo import (
    CIAN,
    SECCIONES,
    TEAL,
)
from diapositivas import fundamentos as escena

# --- La genérica: el título en grande y un robot que saluda, se sienta y programa ---------


def _escena(e):
    """El robot y su puesto (banco, mesa y portátil), de atrás hacia adelante."""
    robot, puesto, t = e["robot"], e["puesto"], e["obra"]["t"]
    if t > 0:  # teclea: las manos suben y bajan
        robot["brazo"] = 1.2 + 0.2 * np.sin(2 * np.pi * 2.5 * t)
    piezas, cosas = [], []
    if puesto["escala"] > 0.05:
        sombra, partes = escena._puesto(puesto, t)
        piezas.append(sombra)
        cosas += partes
    if robot["escala"] > 0.05:
        piezas.append(escena._sombra(robot))
        pose = dict(robot, brazo=_al_lado(robot["mano"])) if robot["mano"] > 0 else robot
        cosas.append((robot["z"], escena._robot(pose)))
    for _, dibujo in sorted(cosas, key=lambda cosa: cosa[0]):
        piezas += dibujo
    return piezas


def _al_lado(angulo):
    """El brazo derecho girado hacia afuera alrededor del hombro, para saludar de lado (al
    levantarlo al frente lo taparía la cabeza)."""
    hombro = np.array([0.58, 0.95, 0.0])
    c, s = np.cos(angulo), np.sin(angulo)

    def mover_brazo(v):
        x, y, z = (v - hombro).T
        return np.stack([x * c - y * s, x * s + y * c, z], axis=1) + hombro

    return mover_brazo


def _saludo(t):
    """La mano va y viene tres veces."""
    return np.sin(2 * np.pi * 3 * t)


def construir(scene, en_loop=False):
    # Se queda el rótulo del módulo; solo se quita la lección.
    # (Al renderizar solo la diapositiva que sigue, todavía no hay rótulo.)
    clave = scene.marco.clave
    scene.marco.ir(clave)
    pasando(scene, SECCIONES[clave][2] if clave in SECCIONES else CIAN, en_loop=en_loop)


def construir_en_loop(scene):
    """La misma, pero al final el robot sigue programando en loop hasta que se pasa."""
    construir(scene, en_loop=True)


def pasando(scene, color, arriba="Pasando a", abajo="la práctica", en_loop=False):
    """El título en dos renglones y el robot que saluda, se sienta y programa. También cierra
    el caso de la inmobiliaria (observar.py), con «Pasando al código». Con `en_loop`, sigue
    programando en loop hasta que se pasa la diapositiva."""
    arriba = titular(arriba, 96, 92, 372)
    abajo = titular(abajo, 96, 92, 476, color=TEAL)
    trazo = raya(96, 526, 196, CIAN, grosor=5)

    quieto = dict(salto=0.0, brazo=0.0, mano=0.0, luz=0.0, sentado=0.0, oficio=None)
    robot = dict(quieto, color=CIAN, escala=0.0, x=1.25, z=0.9, giro=-1.4)
    puesto = dict(x=-0.5, z=0.4, giro=-1.1, escala=0.0, salto=0.0)
    obra = {"t": 0.0}
    escenario = VGroup(*[VMobject() for _ in range(escena.HUECOS)])
    escenario.estado = dict(robot=robot, puesto=puesto, obra=obra)
    escenario.dibujar = _escena
    animar, cambio = escena._animar, escena._cambio

    # El título se escribe mientras aparece el puesto: la mesa con el computador.
    scene.play(teclear(arriba), FadeIn(escena._alfombra(color), scale=0.7), run_time=0.8)
    scene.play(teclear(abajo), animar(escenario, cambio(puesto, escala=1.0)), run_time=0.9)
    scene.play(GrowFromEdge(trazo, LEFT),
               animar(escenario, cambio(robot, escala=1.05, giro=-0.15), run_time=1.0))
    # Saluda: levanta la mano, se le prende el bombillo y la mueve de un lado a otro.
    scene.play(animar(escenario, cambio(robot, 0.0, 0.6, mano=2.5, luz=1.0),
                      cambio(robot, 0.2, 0.8, there_and_back, salto=0.15), run_time=0.7))
    scene.play(animar(escenario, cambio(robot, curva=_saludo, mano=2.85), run_time=1.4))
    scene.play(animar(escenario, cambio(robot, mano=0.0), run_time=0.4))
    # Va hasta el banco con dos pasitos.
    scene.play(animar(escenario, cambio(robot, x=0.0, z=0.7, giro=-1.1),
                      cambio(robot, curva=escena._pasitos, salto=0.07), run_time=1.1))
    # Se sube de un salto y se sienta frente al computador.
    scene.play(animar(escenario, cambio(robot, x=puesto["x"], z=puesto["z"]),
                      cambio(robot, curva=there_and_back, salto=0.4),
                      cambio(robot, 0.3, 0.9, sentado=1.0), run_time=1.2))
    # Y se pone a programar: del portátil salen las celdas del notebook.
    scene.play(animar(escenario, cambio(robot, brazo=1.2), run_time=0.6))
    if not en_loop:
        scene.play(animar(escenario, cambio(obra, curva=linear, t=3.6), run_time=3.6))
        return
    scene.play(animar(escenario, cambio(obra, curva=linear, t=3.6), run_time=3.6),
               FadeIn(scene.indicador(), shift=UP * 0.1, run_time=0.3))
    # Las celdas se repiten cada 2 s y el brazo cada 0.4 s: 4 s cierran la vuelta sin salto.
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    scene.play(animar(escenario, cambio(obra, curva=linear, t=3.6 + VUELTA), run_time=VUELTA))


# --- La de cada práctica: el notebook con sus celdas --------------------------------------

VUELTA = escena.VUELTA  # segundos de cada vuelta del loop
X0, X1, Y0 = 96, 1344, 214
CABEZA, ALTO, HUECO = 48, 44, 8


def _y(k):
    return Y0 + CABEZA + 18 + k * (ALTO + HUECO)


