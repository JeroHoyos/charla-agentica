"""La portada del bloque «Anatomía de un agente»: el título a la izquierda y, a la derecha, una
escena en 3D como la de los fundamentos. Un robot soldador, con careta y soplete, arma a otro
pieza por pieza: caen las piernas, el cuerpo, los brazos, la cabeza y la antena, y cada unión
se suelda con chispas. Al final el robot nuevo enciende los ojos y da un brinco.

Todo lo que se mueve va en un solo mobject que se repinta en cada cuadro (como en fundamentos.py,
de donde vienen las piezas para pintar y animar)."""
import numpy as np
from manim import Circle, FadeIn, Polygon, VGroup, VMobject, linear, there_and_back

from comun.animaciones import teclear
from comun.componentes import titular
from comun.estilo import CORAL, FONDO_OSCURO, ORO, SECCIONES, VERDE, P, U
from comun.tres_d import BLANCO, PANTALLA, camara, levantar, mezcla, partes_robot

from .fundamentos import (
    HUECOS,
    _alfombra,
    _animar,
    _cambio,
    _en_pantalla,
    _mundo,
    _poligonos,
    _px,
    _sombra,
)

CLAVE = "anatomia"
X = 92

# Las piezas del robot que se arma, en el orden en que caen (índices de partes_robot).
GRUPOS = ((0, 1), (2, 3, 4), (5, 6), (7, 8, 9, 10, 11, 12, 13), (14, 15))
# Dónde se suelda cada pieza con la anterior, en las medidas del robot.
UNIONES = ((0.0, 0.0, 0.0), (0.36, 0.32, 0.2), (0.52, 1.0, 0.16), (0.3, 1.12, 0.16),
           (0.45, 1.9, 0.0))
# Dónde se para el soldador y cuánto sube el brazo para que la punta del soplete llegue a
# cada unión.
PUESTOS = (None, (0.91, 0.6), (1.42, 1.35), (1.25, 1.4), (1.02, 2.25))
CAIDA = 1.6   # desde qué altura cae cada pieza

CARETA, VIDRIO_CARETA, TANQUE = "#2b3a44", "#2f7d57", "#c4473f"
CHISPAS = 22


def _bisagra(angulo):
    """Sube la careta alrededor de su bisagra, en la frente."""
    eje = np.array([0.0, 1.88, 0.47])
    c, s = np.cos(angulo), np.sin(angulo)

    def mover(v):
        x, y, z = (v - eje).T
        return np.stack([x, y * c + z * s, -y * s + z * c], axis=1) + eje

    return mover


def _soldador(r):
    """El robot grande: careta (baja con `careta` = 1), tanque de gas a la espalda y el
    soplete en la mano derecha, que se mueve con el brazo."""
    sube = _bisagra(1.75 * (1 - r["careta"]))
    partes = [*partes_robot(r["color"], r["luz"], r["brazo"]),
              ((0, 0.72, -0.42), (0.22, 0.3, 0.12), TANQUE, None),
              ((0, 1.06, -0.42), (0.05, 0.05, 0.05), mezcla(TANQUE, FONDO_OSCURO, 0.4), None),
              ((0, 1.5, 0.47), (0.5, 0.34, 0.03), CARETA, sube, 3),
              ((0, 1.58, 0.505), (0.3, 0.08, 0.006), VIDRIO_CARETA, sube, 4),
              ((0.58, 0.35, 0.06), (0.06, 0.08, 0.08), mezcla(CARETA, BLANCO, 0.2), r["brazo"]),
              ((0.58, 0.18, 0.06), (0.025, 0.12, 0.025), "#9fb2bd", r["brazo"])]
    piezas = _poligonos(partes, lambda v: _mundo(v, r), r["escala"])
    brillo = Circle(radius=20 * r["escala"] * U).move_to(P(*_en_pantalla((0, 2.22, 0), r)))
    return [*piezas, brillo.set_stroke(width=0).set_fill(BLANCO, opacity=0.3 * r["luz"])]


def _armado(r):
    """El robot que se arma: solo las piezas que ya cayeron (`armado` de 0 a 5). Los ojos
    quedan apagados hasta que `luz` los enciende."""
    todas = list(partes_robot(r["color"], r["luz"]))
    ojo = mezcla(PANTALLA, BLANCO, 0.15 + 0.85 * r["luz"])
    for i in (10, 11):
        todas[i] = (*todas[i][:2], ojo, *todas[i][3:])
    partes = []
    for k, grupo in enumerate(GRUPOS):
        p = float(np.clip(r["armado"] - k, 0, 1))
        if p <= 0:
            continue
        baja = CAIDA * (1 - p * p)
        partes += [((c[0], c[1] + baja, c[2]), *resto) for i in grupo
                   for c, *resto in (todas[i],)]
    return _poligonos(partes, lambda v: _mundo(v, r), r["escala"])


def _chispas(centro, t, fuego):
    """El resplandor del soplete y las chispas que saltan y caen."""
    if fuego <= 0.01:
        return []
    x0, y0 = centro
    pulso = 1 + 0.25 * np.sin(2 * np.pi * 9 * t)
    piezas = [Circle(radius=34 * pulso * fuego * U).move_to(P(x0, y0))
              .set_stroke(width=0).set_fill(ORO, opacity=0.35 * fuego),
              Circle(radius=13 * pulso * fuego * U).move_to(P(x0, y0))
              .set_stroke(width=0).set_fill(BLANCO, opacity=0.95 * fuego)]
    azar = np.random.default_rng(7)
    for i in range(CHISPAS):
        angulo = azar.uniform(0.15, np.pi - 0.15)
        rapidez = azar.uniform(90, 200)
        f = (1.6 * t + i / CHISPAS) % 1
        x = x0 + np.cos(angulo) * rapidez * f
        y = y0 - np.sin(angulo) * rapidez * 0.8 * f + 230 * f * f
        lado = 4.5 * (1 - 0.6 * f)
        color = (BLANCO, ORO, CORAL)[i % 3]
        piezas.append(Polygon(*[P(x + a * lado, y + b * lado)
                                for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
                      .set_stroke(width=0).set_fill(color, opacity=fuego * (1 - f)))
    return piezas


def _encendido(t):
    """El soplete se prende rápido, se queda prendido y se apaga al final."""
    return min(1.0, t / 0.15, (1 - t) / 0.15)


def _escena(e):
    soldador, nuevo, obra = e["soldador"], e["nuevo"], e["obra"]
    if obra["fuego"] > 0:
        soldador["brazo"] = obra["brazo"] + 0.05 * np.sin(2 * np.pi * 6 * obra["t"])
    cosas, piezas = [], []
    if soldador["escala"] > 0.05:
        piezas.append(_sombra(soldador))
        cosas.append((soldador["z"], _soldador(soldador)))
    if nuevo["armado"] > 0:
        piezas.append(_sombra(nuevo))
        cosas.append((nuevo["z"], _armado(nuevo)))
    for _, dibujo in sorted(cosas, key=lambda cosa: cosa[0]):
        piezas += dibujo
    union = UNIONES[int(obra["union"])]
    return piezas + _chispas(_en_pantalla(union, nuevo), obra["t"], obra["fuego"])


def _punta(r):
    """La punta del soplete en el lienzo (para ajustar dónde se para el soldador)."""
    v = levantar(np.array([[0.58, 0.06, 0.06]]), r["brazo"])
    return _px(camara(_mundo(v, r)))[0]


def construir(scene):
    scene.marco.ir(CLAVE)
    color = SECCIONES[CLAVE][2]
    arriba = titular("Anatomía", 80, X, 388)
    abajo = titular("de un agente", 80, X, 476, t2c={"agente": color})

    soldador = dict(color=color, x=1.27, z=-0.13, giro=-0.6, escala=0.0, salto=0.0, brazo=0.0,
                    luz=0.0, careta=0.0)
    nuevo = dict(color=VERDE, x=-0.1, z=0.65, giro=0.5, escala=0.95, salto=0.0, luz=0.0,
                 armado=0.0)
    obra = dict(t=0.0, fuego=0.0, union=0, brazo=0.0)
    escenario = VGroup(*[VMobject() for _ in range(HUECOS)])
    escenario.estado = dict(soldador=soldador, nuevo=nuevo, obra=obra)
    escenario.dibujar = _escena

    # El título se escribe mientras aparece la alfombra; después caen las piernas y entra el soldador.
    scene.play(teclear(arriba), FadeIn(_alfombra(color), scale=0.7), run_time=0.8)
    scene.play(teclear(abajo), _animar(escenario, _cambio(nuevo, 0.0, 0.5, linear, armado=1.0),
                                       _cambio(soldador, 0.3, 1.0, escala=1.15, giro=-1.5)),
               run_time=1.2)
    # Se baja la careta y levanta el soplete.
    scene.play(_animar(escenario, _cambio(soldador, 0.0, 0.5, careta=1.0),
                       _cambio(soldador, 0.4, 1.0, brazo=1.1), run_time=0.9))

    # Cae cada pieza y se suelda a la anterior: el brazo sube hasta la unión.
    for k in range(1, len(GRUPOS)):
        x, brazo = PUESTOS[k]
        obra.update(union=k, brazo=brazo)
        scene.play(_animar(escenario, _cambio(nuevo, curva=linear, armado=k + 1.0),
                           _cambio(soldador, 0.3, 1.0, x=x, brazo=brazo), run_time=0.6))
        scene.play(_animar(escenario, _cambio(obra, curva=linear, t=obra["t"] + 1.0),
                           _cambio(obra, curva=_encendido, fuego=1.0), run_time=1.0))

    # Listo: el soldador sube la careta y baja el soplete; el robot nuevo se enciende y brinca.
    scene.play(_animar(escenario, _cambio(soldador, careta=0.0, brazo=0.0, giro=-0.7, x=1.35),
                       _cambio(nuevo, 0.4, 1.0, luz=1.0), run_time=1.0))
    scene.play(_animar(escenario, _cambio(nuevo, curva=there_and_back, salto=0.3),
                       _cambio(soldador, 0.4, 1.0, there_and_back, salto=0.15),
                       _cambio(soldador, 0.4, 1.0, luz=1.0), run_time=1.0))
