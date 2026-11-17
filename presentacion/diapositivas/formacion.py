"""La portada del bloque «Patrones agénticos»: el título a la izquierda y, a la derecha, una
escena en 3D como las de los bloques 1 a 3. Cinco robots, cada uno con su oficio, esperan en
fila. El del casco levanta el brazo y grita «¡En formación!»: todos saltan a su puesto y hacen
una pose de equipo, unos agachados al frente y otros de pie atrás, con los brazos abiertos. Bajo
sus pies se abre una estera de colores que gira en loop hasta que se pasa la diapositiva.

Todo lo que se mueve va en un solo mobject que se repinta en cada cuadro (como en fundamentos.py,
de donde vienen las piezas para pintar y animar)."""
import numpy as np
from manim import (
    Ellipse,
    UP,
    Circle,
    FadeIn,
    FadeOut,
    Polygon,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import titular
from comun.escena import globo
from comun.estilo import AZUL, CIAN, FONDO_OSCURO, LILA, ORO, VERDE, G, P, U
from comun.tres_d import BLANCO, INCLINACION, camara, mezcla, partes_robot

from .fundamentos import (K, X, _cambio, _en_pantalla, _mundo, _poligonos,
                          _px, _sombra)

CLAVE = "patrones"
HUECOS = 700
GAJOS = 20
# Todo el equipo va corrido a la izquierda y un poco atrás de donde están las otras portadas,
# para que quede cerca del título y lejos del logo.
DX, DZ = -0.45, -0.3
GRANDE = 1.22   # el tamaño de toda la escena: robots, distancias y estera
CENTRO, RADIO = (0.15 + DX, -0.05 + DZ), 2.3 * GRANDE  # la estera en el suelo: centro (x, z) y radio
COLORES = (AZUL, ORO, LILA, CIAN, VERDE)
VUELTA = 4.0                      # segundos de cada cuarto de vuelta del loop

# La postura de pie: brazos abajo, piernas rectas, sin agacharse ni inclinarse.
QUIETO = dict(bi=0.0, bd=0.0, fi=0.0, fd=0.0, pi=0.0, pd=0.0, agacha=0.0, inclina=0.0,
              salto=0.0, luz=0.0)

# Cada robot: oficio, color, tamaño, su lugar en la fila y su pose en la formación.
# bi y bd suben cada brazo por el costado; fi y fd lo llevan al frente; pi y pd suben la
# rodilla; agacha baja el cuerpo; inclina lo ladea (positivo, hacia la izquierda).
EQUIPO = (
    ("analista", LILA, 0.7, -1.9,
     dict(x=-1.1, z=0.85, giro=0.5, agacha=0.9, bi=0.4, bd=0.9, fd=1.0, inclina=-0.1)),
    ("abogado", ORO, 0.92, -0.95,
     dict(x=-0.8, z=-0.6, giro=0.45, bi=0.9, bd=2.45, inclina=0.3, pd=0.3)),
    ("ingeniero", CIAN, 0.84, 0.0,
     dict(x=0.1, z=0.95, giro=-0.1, agacha=1.0, bi=1.05, fi=0.6, bd=1.3, fd=0.3)),
    ("redactor", VERDE, 0.76, 0.95,
     dict(x=0.75, z=0.15, giro=-0.35, agacha=0.4, bd=2.3, fd=0.5, bi=0.6, inclina=-0.2)),
    ("asesor", AZUL, 0.9, 1.9,
     dict(x=1.3, z=-0.55, giro=-0.45, bi=1.6, bd=1.9, pi=1.6, inclina=-0.15)),
)
JEFE = 2   # el del casco: el que da la orden


# ---------- la pose: cómo se mueve cada caja ----------

def _brazo(lado, sube, frente):
    """Gira el brazo de ese lado alrededor del hombro: `sube` lo abre por el costado y
    `frente` lo lleva hacia adelante."""
    hombro = np.array([0.58 * lado, 1.0, 0.0])
    a = lado * sube
    c, s = np.cos(a), np.sin(a)
    cf, sf = np.cos(frente), np.sin(frente)

    def mover(v):
        x, y, z = (v - hombro).T
        x, y = x * c - y * s, x * s + y * c
        return np.stack([x, y * cf + z * sf, -y * sf + z * cf], axis=1) + hombro

    return mover


def _rodilla(lado, sube):
    """Sube la pierna de ese lado hacia adelante, alrededor de la cadera."""
    cadera = np.array([0.24 * lado, 0.3, 0.0])
    c, s = np.cos(sube), np.sin(sube)

    def mover(v):
        x, y, z = (v - cadera).T
        return np.stack([x, y * c + z * s, -y * s + z * c], axis=1) + cadera

    return mover


def _agachar(v, a, pierna=0):
    """Agacharse: las piernas se acortan y se abren; lo demás baja lo que ellas pierden."""
    v = v.copy()
    if pierna:
        v[:, 1] *= 1 - 0.7 * a
        v[:, 0] += pierna * 0.18 * a
    else:
        v[:, 1] -= 0.21 * a
    return v


def _cuerpo(r):
    """Lo que mueve todas las cajas a la vez: ladearse sobre los pies."""
    c, s = np.cos(r["inclina"]), np.sin(r["inclina"])

    def mover(v):
        x, y, z = v.T
        return _mundo(np.stack([x * c - y * s, x * s + y * c, z], axis=1), r)

    return mover


def _lado(i, centro):
    """De qué brazo es la caja: los brazos (5 y 6) y lo que lleva en las manos."""
    if i == 5 or (i >= 16 and centro[0] < -0.5 and centro[1] < 1.2):
        return -1
    if i == 6 or (i >= 16 and centro[0] > 0.5 and centro[1] < 1.2):
        return 1
    return 0


def _mover(r, i, centro):
    """La función que lleva la caja `i` a su lugar en la pose."""
    a = r["agacha"]
    if i < 2:
        lado = -1 if i == 0 else 1
        rodilla = _rodilla(lado, r["pi"] if lado < 0 else r["pd"])
        return lambda v: _agachar(rodilla(v), a, lado)
    lado = _lado(i, centro)
    if lado:
        brazo = _brazo(lado, r["bi"], r["fi"]) if lado < 0 else _brazo(lado, r["bd"], r["fd"])
        return lambda v: _agachar(brazo(v), a)
    return lambda v: _agachar(v, a)


def _pose(r):
    """Las cajas del robot en su pose, cada una con la función que la mueve."""
    return [(centro, medio, color, _mover(r, i, centro), *encima)
            for i, (centro, medio, color, _, *encima)
            in enumerate(partes_robot(r["color"], r["luz"], None, r["oficio"]))]


def _robot(r):
    mundo = _cuerpo(r)
    piezas = _poligonos(_pose(r), mundo, r["escala"])
    foco = mundo(_agachar(np.array([[0.0, 2.22, 0.0]]), r["agacha"]))


    x, y = _px(camara(foco))[0]
    brillo = Circle(radius=20 * r["escala"] * U).move_to(P(x, y))
    return [*piezas, brillo.set_stroke(width=0).set_fill(BLANCO, opacity=0.3 * r["luz"])]


# ---------- la alfombra y la estera que gira ----------

def _lugar(x, z):
    """Un punto del suelo de la escena, agrandado alrededor del centro de la estera."""
    return CENTRO[0] + GRANDE * (x + DX - CENTRO[0]), CENTRO[1] + GRANDE * (z + DZ - CENTRO[1])


def _alfombra(color):
    """La alfombra bajo el equipo, un poco más grande que la estera."""
    lado = 2 * (RADIO + 0.15) * K * U
    centro = _px(camara(np.array([[CENTRO[0], 0.0, CENTRO[1]]])))[0]
    return (Ellipse(width=lado, height=lado * np.sin(INCLINACION)).move_to(P(*centro))
            .set_fill(mezcla(color, FONDO_OSCURO, 0.86), opacity=1)
            .set_stroke(mezcla(color, FONDO_OSCURO, 0.4), width=G(2)))


def _estera(obra):
    """La estera del suelo, con gajos de colores que giran bajo el equipo. Cada cinco gajos se
    repiten los colores: un cuarto de vuelta deja la estera igual (así el loop no salta)."""
    f = obra["estera"]
    if f <= 0.01:
        return []
    paso = 2 * np.pi / GAJOS
    piezas = []
    for i in range(GAJOS):
        a0 = i * paso + obra["giro"]
        borde = np.linspace(a0, a0 + paso * 0.55, 8)
        suelo = [(CENTRO[0], 0.0, CENTRO[1])] + [
            (CENTRO[0] + RADIO * f * np.cos(a), 0.0, CENTRO[1] + RADIO * f * np.sin(a))
            for a in borde]
        puntos = _px(camara(np.array(suelo)))
        piezas.append(Polygon(*[P(*p) for p in puntos]).set_stroke(width=0)
                      .set_fill(COLORES[i % 5], opacity=0.3 * f))
    return piezas


# ---------- pintar y animar ----------

def _escena(e):
    robots, obra = e["robots"], e["obra"]
    piezas = _estera(obra)
    vivos = [r for r in robots if r["escala"] > 0.05]
    piezas += [_sombra(r) for r in vivos]
    for r in sorted(vivos, key=lambda r: r["z"]):
        piezas += _robot(r)
    return piezas


def _pintar(escenario):
    """Copia el dibujo de este cuadro en los trazos fijos del escenario."""
    piezas = _escena(escenario.estado)
    assert len(piezas) <= HUECOS, len(piezas)
    for hueco, pieza in zip(escenario, piezas):
        hueco.points = pieza.points
        hueco.match_style(pieza)
    for hueco in escenario[len(piezas):]:
        hueco.clear_points()


def _animar(escenario, *cambios, run_time=1.0):
    desde = [{k: estado[k] for k in hasta} for estado, hasta, *_ in cambios]

    def paso(mob, alpha):
        for (estado, hasta, inicio, fin, curva), antes in zip(cambios, desde):
            t = curva(float(np.clip((alpha - inicio) / (fin - inicio), 0, 1)))
            for k, v in hasta.items():
                estado[k] = antes[k] + (v - antes[k]) * t
        _pintar(escenario)

    return UpdateFromAlphaFunc(escenario, paso, run_time=run_time, rate_func=linear)


# ---------- la diapositiva ----------

def construir(scene):
    scene.marco.ir(CLAVE)
    color = CIAN
    arriba = titular("Patrones", 80, X, 388)
    abajo = titular("agénticos", 80, X, 476, t2c={"agénticos": color})

    robots = [dict(QUIETO, oficio=oficio, color=tono, x=_lugar(0.9 * x, 0.1)[0],
                   z=_lugar(0.9 * x, 0.1)[1], giro=0.0, escala=0.0)
              for oficio, tono, _, x, _ in EQUIPO]
    obra = dict(giro=0.0, estera=0.0)
    escenario = VGroup(*[VMobject() for _ in range(HUECOS)])
    escenario.estado = dict(robots=robots, obra=obra)

    # El título se escribe mientras aparece la alfombra; los robots llegan uno por uno a la fila.
    scene.play(teclear(arriba), FadeIn(_alfombra(color), scale=0.7), run_time=0.8)
    scene.play(teclear(abajo), _animar(escenario, *[
        _cambio(r, 0.12 * i, 0.12 * i + 0.4, escala=0.62 * GRANDE) for i, r in enumerate(robots)],
        run_time=1.4))
    scene.wait(0.4)

    # El del casco se enciende, levanta el brazo y da la orden.
    jefe = robots[JEFE]
    scene.play(_animar(escenario, _cambio(jefe, 0.0, 0.6, bd=2.2, luz=1.0),
                       _cambio(jefe, 0.3, 1.0, there_and_back, salto=0.15), run_time=0.8))
    x, y = _en_pantalla((0, 2.4, 0), jefe)
    orden = globo("¡En formación!", x - 20, y - 50, tam=22, hacia=x)
    scene.play(FadeIn(orden, shift=UP * 0.1, scale=0.8), run_time=0.35)
    scene.wait(0.9)

    # Todos saltan a su puesto, uno detrás de otro.
    saltos = []
    for i, (r, (*_, tam, _, pose)) in enumerate(zip(robots, EQUIPO)):
        inicio = 0.1 * i
        saltos += [_cambio(r, inicio, inicio + 0.5, x=_lugar(pose["x"], pose["z"])[0],
                           z=_lugar(pose["x"], pose["z"])[1], giro=pose["giro"],
                           escala=tam * GRANDE, bd=0.0, luz=1.0),
                   _cambio(r, inicio, inicio + 0.5, there_and_back, salto=0.55)]
    scene.play(FadeOut(orden, run_time=0.3), _animar(escenario, *saltos, run_time=1.6))

    # ¡La pose! Bajo sus pies se abre la estera de colores y empieza a girar.
    poses = [_cambio(r, 0.0, 0.7, **{k: v for k, v in pose.items() if k in QUIETO})
             for r, (*_, pose) in zip(robots, EQUIPO)]
    girar = 0.5 * np.pi / VUELTA   # lo que gira en un segundo
    scene.play(_animar(escenario, *poses, _cambio(obra, 0.3, 1.0, estera=1.0),
                       _cambio(obra, curva=linear, giro=girar), run_time=1.0),
               FadeIn(scene.indicador(), shift=UP * 0.1, run_time=0.3))
    # Sin parar, sigue en loop: la estera da un cuarto de vuelta hasta que se pasa la diapositiva.
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    scene.play(_animar(escenario, _cambio(obra, curva=linear, giro=girar + 0.5 * np.pi),
                       run_time=VUELTA))
