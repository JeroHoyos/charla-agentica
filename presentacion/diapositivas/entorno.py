"""La portada del bloque «El agente y su entorno»: el título a la izquierda y, a la derecha, una
escena en 3D como la de la anatomía. El robot del modelo entra caminando con una antena de
platillo en la mano, levantada al lado de la cabeza; anda perdido, da vueltas y mueve el brazo buscando
señal. Entra un satélite, el robot lo encuentra, le apunta y le manda paquetes de información
en un haz de ondas. El satélite reparte la información hacia el mundo y le contesta.

Todo lo que se mueve va en un solo mobject que se repinta en cada cuadro (como en fundamentos.py,
de donde vienen las piezas para pintar y animar).

Al final sigue en loop hasta que se pasa la diapositiva: el robot manda paquetes, el satélite le
contesta y el robot brinca. Todo lo que se mueve con el tiempo se repite en VUELTA_LOOP
segundos (las estrellas, las ondas y el satélite que flota y gira), así la vuelta no salta."""
import numpy as np
from manim import UP, FadeIn, Polygon, VGroup, VMobject, linear, there_and_back

from comun.animaciones import teclear
from comun.componentes import titular
from comun.estilo import ORO, SECCIONES, G, P
from comun.tres_d import BLANCO, PANTALLA, camara, mezcla, partes_robot

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

CLAVE = "interacciones"
X = 92
MANO = (-0.58, 0.42, 0.0)   # la mano que sostiene el platillo, antes de levantar el brazo
HOMBRO = np.array([-0.58, 0.98, 0.0])
ARRIBA = 2.0                # cuánto sube ese brazo por el costado: hacia arriba y afuera
PALO = 80                   # el largo del palo del platillo, en pt del lienzo
VUELTA = (-0.4, -0.2, 0.65)  # el círculo por el que camina perdido: centro (x, z) y radio
VUELTA_LOOP = 10.0          # segundos de cada vuelta del loop del final
GIRO_SATELITE = 2 * np.pi / VUELTA_LOOP   # el satélite se ladea una vez por vuelta
PAQUETES = 3                # cuántos viajan juntos en cada envío
METAL, METAL_CLARO = "#9fb2bd", "#d7e1e6"
PANEL, RAYA_PANEL = "#2d4f8f", "#5b86cc"
ESTRELLAS = ((1180, 150), (1250, 250), (1390, 140), (1330, 330), (1120, 230), (1400, 270),
             (1010, 170), (1220, 110))


def _rombo(x, y, lado, color, brillo):
    return (Polygon(P(x, y - lado), P(x + lado * 0.4, y), P(x, y + lado), P(x - lado * 0.4, y))
            .set_stroke(width=0).set_fill(color, opacity=brillo))


def _figura(puntos, color):
    return (Polygon(*[P(*p) for p in puntos]).set_fill(color, opacity=1)
            .set_stroke(color, width=G(0.5)))


def _estrellas(t, brillo):
    if brillo <= 0.01:
        return []
    return [_rombo(x, y, 5 + 2 * (i % 2), BLANCO,
                   brillo * (0.4 + 0.35 * np.sin(2 * np.pi * (0.5 * t + i / 5))))
            for i, (x, y) in enumerate(ESTRELLAS)]


# ---------- el robot que camina con su platillo ----------

def _al_costado(angulo, adelante=0.0):
    """Sube el brazo por el costado, alrededor del hombro, y lo lleva `adelante` (o atrás,
    si es negativo)."""
    c, s = np.cos(-angulo), np.sin(-angulo)
    ca, sa = np.cos(adelante), np.sin(adelante)

    def mover(v):
        x, y, z = (v - HOMBRO).T
        x, y = x * c - y * s, x * s + y * c
        return np.stack([x, y * ca - z * sa, y * sa + z * ca], axis=1) + HOMBRO

    return mover


def _camino(ruta):
    """Dónde va el robot perdido (`ruta` de 0 a 1): una vuelta y cuarto alrededor de VUELTA,
    y hacia dónde mira (hacia donde camina)."""
    cx, cz, radio = VUELTA
    fi = np.pi - 2.5 * np.pi * ruta
    x, z = cx + radio * np.cos(fi), cz + radio * np.sin(fi)
    return x, z, np.arctan2(np.sin(fi), -np.cos(fi))


def _postura(r, t):
    """El robot de este cuadro: va por su camino rebotando un poco con cada paso y, al buscar
    (`buscar`), mueve el brazo del platillo arriba y abajo y adelante y atrás. Con `mirar` = 1
    deja de mirar hacia donde camina y mira hacia `giro`."""
    x, z, rumbo = _camino(r["ruta"])
    rebote = 0.05 * abs(np.sin(2 * np.pi * r["paso"]))
    sube = r["buscar"] * 0.25 * np.sin(2 * np.pi * 0.6 * t)
    adelante = r["buscar"] * 0.45 * np.sin(2 * np.pi * 0.45 * t + 1.0)
    return dict(r, x=x, z=z, giro=rumbo + (r["giro"] - rumbo) * r["mirar"],
                salto=r["salto"] + rebote, brazo=r["brazo"] + sube, adelante=adelante)


def _modelo(r, t):
    """El robot con audífonos y sin su antena de palito: un brazo arriba con el platillo y el
    otro que se balancea al caminar; las piernas se turnan con cada paso."""
    partes = list(partes_robot(r["color"], r["luz"], None, "asesor"))
    del partes[14:16]
    s = np.sin(2 * np.pi * r["paso"])
    for i, lado in enumerate((-1, 1)):
        centro, medio, tono, _ = partes[i]
        partes[i] = ((centro[0], centro[1] + 0.06 * max(0.0, lado * s), 0.14 * lado * s),
                     medio, tono, None)
    partes[5] = (*partes[5][:3], _al_costado(r["brazo"], r["adelante"]))
    partes[6] = (*partes[6][:3], 0.45 * s)
    if np.cos(r["giro"]) < 0.15:
        # De espaldas o de lado no se ve la cara: lo pintado encima de ella (ojos, pantallas)
        # se saltaría el orden y quedaría sobre la cabeza.
        partes = [p for p in partes if len(p) == 4 or p[0][2] <= 0]
    return _poligonos(partes, lambda v: _mundo(v, r), r["escala"])


def _mano(r):
    """La mano que sostiene el platillo, en el lienzo."""
    v = _al_costado(r["brazo"], r["adelante"])(np.array([MANO]))
    return np.array(_px(camara(_mundo(v, r)))[0])


def _girada(v, angulo):
    """Una dirección del lienzo, girada `angulo` (lo que gira la mano al mover el brazo)."""
    a = np.arctan2(v[1], v[0]) + angulo
    return np.array([np.cos(a), np.sin(a)])


def _platillo(base, k, u, d, luz):
    """El palo que sale de la mano hacia `u`, la taza del platillo vista de lado mirando hacia
    `d`, su borde y la bocina al frente. Devuelve las piezas y la punta de la bocina, de donde
    salen las ondas."""
    alto, radio = PALO * k, 40 * k
    centro = base + u * alto
    n = np.array([-d[1], d[0]])
    m = np.array([-u[1], u[0]]) * 3.5 * k
    taza = [centro + n * radio * a - d * radio * 0.55 * (1 - a * a) for a in np.linspace(-1, 1, 15)]
    borde = [centro + n * radio * np.cos(a) + d * radio * 0.28 * np.sin(a)
             for a in np.linspace(0, 2 * np.pi, 24)]
    punta = centro + d * radio * 0.95
    gris = mezcla(METAL, PANTALLA, 0.35)
    palo = [base - m - u * 8 * k, base + m - u * 8 * k, centro + m, centro - m]
    piezas = [_figura(palo, gris), _figura(taza, gris), _figura(borde, METAL_CLARO),
              _figura([centro + n * 3 * k, centro - n * 3 * k, punta], METAL),
              _rombo(*punta, 7 * k, mezcla(METAL, BLANCO, luz), 1)]
    return piezas, punta


# ---------- el satélite ----------

def _partes_satelite(abrir, luz):
    foco = mezcla("#55606a", BLANCO, luz)
    partes = [((0, 0, 0), (0.32, 0.28, 0.28), ORO, None),
              ((0, 0, 0.29), (0.2, 0.16, 0.01), mezcla(ORO, PANTALLA, 0.35), None, 1),
              ((0, 0.34, 0), (0.06, 0.06, 0.06), foco, None),
              ((0, -0.36, 0), (0.14, 0.08, 0.14), METAL_CLARO, None)]
    if abrir > 0.02:
        w = 0.62 * abrir
        for lado in (-1, 1):
            partes += [((lado * 0.44, 0, 0), (0.12, 0.025, 0.025), METAL, None),
                       ((lado * (0.56 + w), 0, 0), (w, 0.24, 0.015), PANEL, None),
                       ((lado * (0.56 + w), 0, 0.016), (w, 0.02, 0.004), RAYA_PANEL, None, 1)]
    return partes


def _satelite(sat, t):
    """El satélite flotando: sube y baja un poco y gira despacio."""
    ahora = dict(sat, salto=sat["altura"] + 0.06 * np.sin(2 * np.pi * 0.4 * t),
                 giro=sat["giro"] + 0.25 * np.sin(GIRO_SATELITE * t))
    centro = np.array(_en_pantalla((0, 0, 0), ahora))
    return _poligonos(_partes_satelite(sat["abrir"], sat["luz"]),
                      lambda v: _mundo(v, ahora), sat["escala"]), centro


# ---------- las señales ----------

def _haz(origen, d, t, fuerza, color, abertura=0.55):
    """Ondas que salen de `origen` hacia `d`: arcos que crecen y se apagan."""
    if fuerza <= 0.01:
        return []
    base = np.arctan2(d[1], d[0])
    arcos = []
    for i in range(3):
        f = (1.1 * t + i / 3) % 1
        radio = 14 + 95 * f
        puntos = [P(origen[0] + radio * np.cos(base + a), origen[1] + radio * np.sin(base + a))
                  for a in np.linspace(-abertura, abertura, 12)]
        arcos.append(VMobject().set_points_as_corners(puntos).set_fill(opacity=0)
                     .set_stroke(color, width=G(3), opacity=fuerza * (1 - f)))
    return arcos


def _paquete(x, y, color, brillo):
    """Un sobre: el cuerpo de color con la solapa en blanco."""
    w, h = 13, 9
    cuerpo = Polygon(*[P(x + a * w, y + b * h) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    solapa = Polygon(P(x - w, y - h), P(x + w, y - h), P(x, y + 1))
    return [cuerpo.set_fill(color, opacity=brillo).set_stroke(BLANCO, width=G(1.2), opacity=brillo),
            solapa.set_fill(BLANCO, opacity=0.85 * brillo).set_stroke(width=0)]


def _envio(viaje, punta, foco):
    """Los paquetes en línea recta entre la bocina y el satélite (`avance` de 0 a 1); con
    `vuelta` van del satélite al platillo."""
    if not 0 < viaje["avance"] < 1:
        return []
    p0, p1 = (foco, punta) if viaje["vuelta"] else (punta, foco)
    piezas = []
    for k in range(PAQUETES):
        f = float(np.clip(viaje["avance"] * 1.6 - k * 0.3, 0, 1))
        if 0 < f < 1:
            piezas += _paquete(*((1 - f) * p0 + f * p1), viaje["color"],
                               min(1.0, 6 * f, 6 * (1 - f)))
    return piezas


def _escena(e):
    robot, sat, obra = e["robot"], e["satelite"], e["obra"]
    t = obra["t"]
    satelite, foco = _satelite(sat, t)
    piezas = _estrellas(t, obra["estrellas"]) + satelite
    if robot["escala"] <= 0.05:
        return piezas
    ahora = _postura(robot, t)
    mano = _mano(ahora)
    # La mano sostiene el palo derecho: el platillo sube y baja con el brazo, sin ladearse.
    u = np.array([0.0, -1.0])
    tope = mano + u * PALO * ahora["escala"]
    hacia = (foco - tope) / np.linalg.norm(foco - tope)
    d = _girada((1 - robot["apuntar"]) * u + robot["apuntar"] * hacia, 0.0)
    plato, punta = _platillo(mano, ahora["escala"], u, d, robot["luz"])
    piezas += [_sombra(ahora), *_modelo(ahora, t), *plato]
    piezas += _haz(punta, d, t, obra["haz"], SECCIONES[CLAVE][2])
    piezas += _haz(foco + (0, 30), np.array([-0.45, 0.89]), t, obra["mundo"], ORO, 0.8)
    return piezas + _envio(obra["viaje"], punta, foco)


# ---------- la diapositiva ----------

def _mandar(escenario, vuelta, color, segundos=1.4, *extra):
    """Un envío de paquetes, con lo que pase mientras tanto."""
    obra = escenario.estado["obra"]
    obra["viaje"] = dict(vuelta=vuelta, color=color, avance=0.0)
    return _animar(escenario, _cambio(obra["viaje"], curva=linear, avance=1.0),
                   _cambio(obra, curva=linear, t=obra["t"] + segundos), *extra,
                   run_time=segundos)


def construir(scene):
    scene.marco.ir(CLAVE)
    color = SECCIONES[CLAVE][2]
    arriba = titular("El agente", 80, X, 388)
    abajo = titular("y su entorno", 80, X, 476, t2c={"entorno": color})

    robot = dict(color=color, giro=0.35, escala=0.0, salto=0.0, brazo=ARRIBA, luz=0.0,
                 apuntar=0.0, buscar=1.0, paso=0.0, ruta=0.0, mirar=0.0)
    satelite = dict(x=3.8, z=-0.6, giro=-0.8, escala=0.85, salto=3.0, altura=3.0, abrir=0.0,
                    luz=0.0)
    obra = dict(t=0.0, estrellas=0.0, haz=0.0, mundo=0.0,
                viaje=dict(vuelta=False, color=color, avance=0.0))
    escenario = VGroup(*[VMobject() for _ in range(HUECOS)])
    escenario.estado = dict(robot=robot, satelite=satelite, obra=obra)
    escenario.dibujar = _escena

    # El título se escribe mientras aparece la alfombra.
    scene.play(teclear(arriba), FadeIn(_alfombra(color), scale=0.7), run_time=0.8)
    # Anda perdido: da vueltas con el platillo en alto, moviendo el brazo para buscar señal.
    # Mientras tanto llega el satélite por detrás.
    scene.play(teclear(abajo), _animar(
        escenario, _cambio(robot, 0.0, 0.08, escala=1.2),
        _cambio(robot, curva=linear, ruta=1.0, paso=10.0),
        _cambio(obra, estrellas=1.0), _cambio(obra, curva=linear, t=4.2),
        _cambio(satelite, 0.5, 0.95, x=1.6), run_time=4.2))
    # Se para y se voltea hacia el cielo, todavía buscando; el satélite abre los paneles.
    scene.play(_animar(escenario, _cambio(robot, 0.0, 0.5, mirar=1.0),
                       _cambio(satelite, 0.2, 0.8, abrir=1.0),
                       _cambio(obra, curva=linear, t=5.8), run_time=1.6))
    # ¡Lo encontró! Apunta el platillo y da un brinco.
    scene.play(_animar(escenario, _cambio(robot, 0.0, 0.5, apuntar=1.0, buscar=0.0),
                       _cambio(robot, 0.4, 1.0, there_and_back, salto=0.2),
                       _cambio(obra, curva=linear, t=6.6), run_time=0.8))
    # Se enciende y llama: el haz sale del platillo y el satélite prende su luz.
    scene.play(_animar(escenario, _cambio(robot, 0.0, 0.3, luz=1.0),
                       _cambio(obra, 0.0, 0.3, haz=1.0),
                       _cambio(satelite, 0.5, 0.8, luz=1.0),
                       _cambio(obra, curva=linear, t=7.6), run_time=1.0))
    # Manda la información; el satélite la reparte hacia el mundo.
    scene.play(_mandar(escenario, False, color))
    scene.play(_animar(escenario, _cambio(obra, 0.0, 0.4, mundo=1.0),
                       _cambio(obra, curva=linear, t=obra["t"] + 1.0), run_time=1.0))
    # Le contesta y el robot brinca contento mientras todo sigue transmitiendo.
    scene.play(_mandar(escenario, True, ORO, 1.4,
                       _cambio(robot, 0.75, 1.0, there_and_back, salto=0.2)))
    scene.play(_animar(escenario, _cambio(robot, 0.3, 0.8, there_and_back, salto=0.25),
                       _cambio(obra, curva=linear, t=obra["t"] + 1.6), run_time=1.6),
               FadeIn(scene.indicador(), shift=UP * 0.1, run_time=0.3))
    _en_loop(scene, escenario, color)


def _en_loop(scene, escenario, color):
    """Sin parar, sigue en loop: manda, espera, le contestan y brinca, en VUELTA_LOOP segundos."""
    obra, robot = escenario.estado["obra"], escenario.estado["robot"]
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    for vuelta, tono, extra in ((False, color, ()),
                                (True, ORO, (_cambio(robot, 0.75, 1.0, there_and_back, salto=0.2),))):
        scene.play(_mandar(escenario, vuelta, tono, 1.4, *extra))
        scene.play(_animar(escenario, _cambio(obra, curva=linear, t=obra["t"] + 3.6),
                           run_time=3.6))
