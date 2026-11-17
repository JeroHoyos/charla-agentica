"""El cierre: la pantalla empieza vacía. Llega el robot de la portada, tira de una soga y baja
la pancarta de «¡Gracias!» con toda la fiesta (banderines, focos, estrellas y serpentinas).
Después llama a dos compañeros, que traen el aviso con el QR de asistencia, y a uno más pequeño,
que llega corriendo con el banderín del semillero en la mano, resbala, cae de espaldas y,
tendido en el suelo, lo levanta con el brazo. Al final todos celebran, y siguen celebrando en
loop hasta que se pasa la diapositiva."""
import random

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    Flash,
    Group,
    GrowFromEdge,
    GrowFromPoint,
    LaggedStart,
    Polygon,
    VGroup,
    VMobject,
    linear,
    rush_from,
    rush_into,
    smooth,
    there_and_back,
)
from manim.constants import RESAMPLING_ALGORITHMS
from manim.utils.rate_functions import ease_out_back

from comun.componentes import caja, centrado, imagen, linea, logo, punto, raya, titular
from comun.estilo import (
    CIAN,
    CORAL,
    FONDO_OSCURO,
    GRIS_MEDIO,
    LILA,
    ORO,
    OSCURO,
    TARJETA,
    TINTA,
    VERDE,
    G,
    P,
    U,
)
from comun.tres_d import INCLINACION, PANTALLA, camara, levantar

# Los robots se pintan con el escenario de la portada.
from .portada import CX as X_MUNDO
from .portada import CY as Y_MUNDO
from .portada import K, _animar, _cambio, _escenario, _lienzo, _mundo

SUELO = 690
# Dónde se para el robot que tira de la soga, la soga y hasta dónde cuelga su manija.
X_ROBOT, X_SOGA, Y_MANIJA = 215, 292, 545
# La pancarta de las gracias (x0, y0, x1, y1) y desde cuán arriba baja.
PANCARTA = (360, 150, 850, 300)
ALTO = 440
# El aviso: su tablero (x0, y0, x1, y1) y desde cuán lejos lo traen.
AVISO = (925, 130, 1225, 480)
LEJOS = 640
# El robot pequeño: dónde cae, su suelo (más cerca de quien mira) y cómo lleva el brazo del
# banderín al correr (en alto y hacia adelante, para que el asta no le tape la cara).
X_CHICO, SUELO_CHICO, BRAZO_EN_ALTO = 545, 716, 2.4
MADERA = "#b58a55"

FIESTA = (CIAN, LILA, VERDE, ORO, CORAL)
# Donde no cae la decoración: la soga y su robot, la pancarta, el pequeño y su bandera, el
# aviso con quienes lo traen y el indicador de la esquina.
OCUPADO = ((140, 380, 345, 740), (265, 0, 320, 580), (335, 125, 875, 325),
           (420, 325, 835, 770), (780, 105, 1375, 740), (1240, 690, 1440, 810))
# Los fuegos del final: dónde estallan y de qué color.
FUEGOS = ((130, 250, LILA), (1320, 330, ORO), (620, 362, CORAL), (160, 560, VERDE),
          (1400, 150, CIAN))


def _x(sx):
    """La x del mundo de los robots que cae en `sx` del lienzo."""
    return (sx - X_MUNDO) / K


def _robot(color, sx, giro, escala, oficio=None, suelo=SUELO):
    z = (suelo - Y_MUNDO) / (K * np.sin(INCLINACION))
    return dict(color=color, x=_x(sx), z=z, giro=giro, escala=escala, salto=0.0, brazo=0.0,
                luz=0.0, oficio=oficio, paso=0.0, caida=0.0)


def _caminar(r, pasos, hasta, inicio=0.0, fin=1.0, largo=0.55, curva=smooth, **mas):
    """El robot va hasta `hasta` (x del lienzo) moviendo las piernas: da `pasos` pasos."""
    return (_cambio(r, inicio, fin, curva, x=_x(hasta), **mas),
            _cambio(r, inicio, fin, lambda t: np.sin(np.pi * pasos * t), paso=largo),
            _cambio(r, inicio, fin, lambda t: abs(np.sin(np.pi * pasos * t)), salto=0.04))


def _senas(t):
    """El brazo va y vuelve dos veces: una seña para que vengan."""
    return np.sin(2 * np.pi * t) ** 2


def _fuego(x, y, color, largo=0.34):
    return Flash(P(x, y), color=color, line_length=largo, num_lines=14, flash_radius=0.16,
                 line_stroke_width=G(4))


# --- La decoración ----------------------------------------------------------------------

def _estrella(x, y, radio, color):
    """Un destello de cuatro puntas."""
    puntos = [P(x + r * np.cos(i * np.pi / 4), y + r * np.sin(i * np.pi / 4))
              for i, r in ((i, radio if i % 2 == 0 else 0.34 * radio) for i in range(8))]
    return Polygon(*puntos).set_fill(color, opacity=1).set_stroke(width=0)


def _libre(x, y):
    return not any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in OCUPADO)


def _decoracion():
    """Estrellas y serpentinas repartidas por el fondo, sin tapar nada."""
    azar = random.Random(11)
    estrellas, serpentinas = VGroup(), VGroup()
    while len(estrellas) + len(serpentinas) < 46:
        x, y, color = azar.uniform(30, 1410), azar.uniform(125, 785), azar.choice(FIESTA)
        if not _libre(x, y):
            continue
        if len(estrellas) <= len(serpentinas):
            estrellas.add(_estrella(x, y, azar.uniform(8, 18), color))
        else:
            serpentinas.add(caja(x - 12, y - 3.5, x + 12, y + 3.5, color, radio=3.5)
                            .rotate(azar.uniform(0, np.pi)))
    return estrellas, serpentinas


def _altura_cuerda(x):
    """La guirnalda cuelga en dos ondas."""
    t = x % 720 / 720
    return 16 + 46 * 4 * t * (1 - t)


def _banderines():
    cuerda, banderas = VMobject(), VGroup()
    cuerda.set_points_smoothly([P(x, _altura_cuerda(x)) for x in range(0, 1440, 60)]
                               + [P(1440, 16)])
    cuerda.set_stroke(GRIS_MEDIO, width=G(2)).set_fill(opacity=0)
    for i, x in enumerate(range(48, 1440, 64)):
        y = _altura_cuerda(x)
        bandera = Polygon(P(x - 21, y), P(x + 21, y), P(x, y + 40))
        banderas.add(bandera.set_fill(FIESTA[i % len(FIESTA)], opacity=1).set_stroke(width=0))
    return VGroup(cuerda, banderas)


def _focos():
    """Dos haces de luz que bajan desde las esquinas y se cruzan sobre el escenario."""
    haces = (((70, -20), (300, 830), (960, 830), CIAN), ((1370, -20), (480, 830), (1140, 830), LILA))
    return VGroup(*[Polygon(P(*a), P(*b), P(*c)).set_fill(color, opacity=0.07).set_stroke(width=0)
                    for a, b, c, color in haces])


# --- La soga, la pancarta, el aviso y la bandera ----------------------------------------

def _soga():
    cuerda = linea(X_SOGA, -500, X_SOGA, Y_MANIJA, "#d9c8a0", 4.5)
    manija = caja(X_SOGA - 15, Y_MANIJA - 4, X_SOGA + 15, Y_MANIJA + 10, CORAL, radio=5)
    return VGroup(cuerda, manija).set_z_index(2)


def _pancarta():
    """La pancarta de las gracias, colgada de dos cuerdas."""
    x0, y0, x1, y1 = PANCARTA
    cx = (x0 + x1) / 2
    cuerdas = [linea(x, -700, x, y0 + 10, GRIS_MEDIO, 3) for x in (x0 + 55, x1 - 55)]
    rayas = [raya(cx - 114 + 58 * i, y1 - 24, cx - 114 + 58 * i + 50, color, grosor=5)
             for i, color in enumerate((CIAN, LILA, VERDE, ORO))]
    dice = titular("¡Gracias!", 82, cx, y1 - 52, color=OSCURO, alinear=np.zeros(3))
    return VGroup(*cuerdas, caja(x0, y0, x1, y1, TINTA, radio=22), dice, *rayas).set_z_index(2)


def _aviso():
    """El tablero con su letrero y la pantalla todavía apagada; aparte, los postes y el QR
    que se enciende después."""
    x0, y0, x1, y1 = AVISO
    cx = (x0 + x1) / 2
    pantalla = (cx - 128, y0 + 70, cx + 128, y0 + 326)
    tablero = VGroup(caja(x0, y0, x1, y1, TARJETA, radio=14, borde=CIAN, grosor=3.5),
                     centrado("Registra tu asistencia", 22, cx, y0 + 46, color=CIAN),
                     caja(*pantalla, PANTALLA, radio=10))
    postes = VGroup(*[caja(x - 7, y1, x + 7, SUELO + 4, GRIS_MEDIO) for x in (cx - 95, cx + 95)])
    qr = imagen("qr_asistencia.png", pantalla[0] + 14, pantalla[1] + 14,
                pantalla[2] - 14, pantalla[3] - 14)
    qr.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    luz = Group(caja(*pantalla, "#ffffff", radio=10), qr)
    return tablero.set_z_index(2), postes, luz.set_z_index(3)


def _banderin():
    """El banderín del semillero, derecho y con la mano en `mano`: el asta de madera (va primero), el
    triángulo cian con su borde blanco, el sello redondo con el logo y el nombre."""
    xm, ym = 600, 600
    x0, y0 = xm + 4, ym - 186
    cx, cy = x0 + 30, y0 + 48
    tela = [Polygon(*[P(x0 + x, y0 + y) for x, y in puntos]).set_fill(color, opacity=1)
            .set_stroke(width=0)
            for puntos, color in ((((0, 0), (172, 48), (0, 96)), TINTA),
                                  (((20, 7.5), (159, 48), (20, 88.5)), CIAN))]
    sello = [punto(cx, cy, 34, TINTA), punto(cx, cy, 30, PANTALLA),
             punto(cx, cy, 25, PANTALLA, borde=CIAN, grosor=1.5), logo(cx - 20, cy - 20, 40)]
    nombre = titular("APERTURE", 11.5, cx + 39, cy + 4.5, color=TINTA)
    banderin = Group(caja(xm - 4, ym - 192, xm + 4, ym + 16, MADERA, radio=4), *tela, *sello,
                     nombre).set_z_index(4)
    banderin.scale(1.44, about_point=P(xm, ym))
    banderin.mano, banderin.giro = P(xm, ym), 0.0
    return banderin


def _brazo(r):
    """El hombro y la mano del brazo que mueve el robot, en la pantalla."""
    angulo = r["brazo"] - 0.8 * r["paso"] if r["paso"] else r["brazo"]
    puntos = levantar(np.array([[0.58, 1.0, 0.0], [0.58, 0.42, 0.0]]), angulo)
    return [np.array(p) for p in _lienzo(camara(_mundo(puntos, r)))]


def _en_la_mano(robot):
    """Mantiene el banderín en la mano del robot y apuntando hacia donde apunta su brazo, sin
    el vaivén de los pasos."""
    def sigue(banderin):
        _, mano = _brazo(robot)
        hombro, quieta = _brazo(robot | {"paso": 0.0})
        giro = np.arctan2(quieta[1] - hombro[1], quieta[0] - hombro[0]) - np.pi / 2
        banderin.rotate(giro - banderin.giro, about_point=banderin.mano)
        banderin.shift(mano - banderin.mano)
        banderin.mano, banderin.giro = mano, giro
    return sigue


# --- Los pasos --------------------------------------------------------------------------

def _bajar_gracias(scene, escenario, cian):
    """Baja una soga, el robot llega caminando y tira de ella: cae la pancarta de las
    gracias y, con ella, los banderines, los focos, las estrellas y las serpentinas."""
    soga, pancarta = _soga().shift(600 * U * UP), _pancarta().shift(ALTO * U * UP)
    estrellas, serpentinas = _decoracion()
    origen = P((PANCARTA[0] + PANCARTA[2]) / 2, (PANCARTA[1] + PANCARTA[3]) / 2)
    scene.add(soga)
    scene.play(_animar(escenario, *_caminar(cian, 6, X_ROBOT), run_time=2.6),
               soga.animate(rate_func=ease_out_back, run_time=1.4).shift(600 * U * DOWN))
    scene.play(_animar(escenario, _cambio(cian, giro=0.15), _cambio(cian, 0.3, 1.0, brazo=2.5),
                       run_time=0.7))
    # El tirón: la soga baja y vuelve, y arriba se suelta todo.
    scene.add(pancarta)
    scene.play(soga.animate(rate_func=there_and_back, run_time=0.9).shift(60 * U * DOWN),
               _animar(escenario, _cambio(cian, 0.0, 0.75, there_and_back, brazo=1.5),
                       _cambio(cian, 0.5, 1.0, luz=1.0), run_time=1.2),
               pancarta.animate(rate_func=ease_out_back, run_time=1.2).shift(ALTO * U * DOWN),
               FadeIn(_focos(), run_time=1.2), FadeIn(_banderines(), shift=DOWN * 0.8, run_time=1.2))
    scene.play(LaggedStart(*[GrowFromPoint(m, origen) for m in (*estrellas, *serpentinas)],
                           lag_ratio=0.02, run_time=1.5),
               LaggedStart(*[_fuego(*f) for f in FUEGOS[:3]], lag_ratio=0.25, run_time=1.5),
               _animar(escenario, _cambio(cian, 0.0, 0.4, there_and_back, salto=0.22),
                       _cambio(cian, 0.5, 1.0, brazo=0.0), run_time=1.5))
    return estrellas


def _llamar(scene, escenario, cian, giro, hasta, colores):
    """Se vuelve hacia un lado y hace señas: los mensajes salen por el suelo a buscar a otros."""
    escenario.mensajes[:] = [dict(de=(cian["x"], cian["z"]), a=(_x(hasta), cian["z"]), t=0.0,
                                  color=color) for color in colores]
    n = len(colores)
    scene.play(_animar(escenario, _cambio(cian, 0.0, 0.25, giro=giro),
                       _cambio(cian, curva=_senas, brazo=2.5),
                       *[_cambio(m, 0.2 * (i + 1), 1.0 - 0.2 * (n - 1 - i), t=1.0)
                         for i, m in enumerate(escenario.mensajes)], run_time=1.8))
    escenario.mensajes.clear()


def _traer_aviso(scene, escenario, cian, cargan):
    """Los dos compañeros traen el aviso sobre la cabeza, lo plantan en sus postes, se hacen
    a los lados y el aviso se enciende."""
    lila, oro = cargan
    cx = (AVISO[0] + AVISO[2]) / 2
    tablero, postes, luz = _aviso()
    scene.add(tablero.shift(LEJOS * U * RIGHT))
    scene.play(_animar(escenario, *_caminar(lila, 8, cx - 80), *_caminar(oro, 8, cx + 80),
                       run_time=3.0),
               tablero.animate(rate_func=smooth).shift(LEJOS * U * LEFT), run_time=3.0)
    scene.play(_animar(escenario, *[_cambio(r, giro=0.0) for r in cargan],
                       *[_cambio(r, curva=there_and_back, salto=0.14) for r in cargan]),
               LaggedStart(*[GrowFromEdge(p, DOWN) for p in postes], lag_ratio=0.3), run_time=0.7)
    scene.play(_animar(escenario, *_caminar(lila, 3, AVISO[0] - 75, giro=0.4),
                       *_caminar(oro, 3, AVISO[2] + 75, giro=-0.4),
                       _cambio(cian, giro=0.2), run_time=1.2))
    scene.play(FadeIn(luz, rate_func=lambda t: smooth(t) * (0.6 + 0.4 * (int(t * 9) % 2))),
               _animar(escenario, *[_cambio(r, luz=1.0) for r in cargan]), run_time=1.0)
    luz.set_opacity(1)


def _izar_banderin(scene, escenario, chico):
    """El pequeño llega corriendo con el banderín en alto, frena tarde, resbala y cae de
    espaldas con el banderín por delante; tendido, lo levanta con el brazo."""
    banderin = _banderin()
    banderin.add_updater(_en_la_mano(chico))
    banderin.update()
    scene.add(banderin)
    scene.play(_animar(escenario, *_caminar(chico, 8, X_CHICO - 170, largo=0.7, curva=linear),
                       run_time=1.3))
    # Frena echándose hacia atrás, los pies se le van y queda tendido.
    scene.play(_animar(escenario, _cambio(chico, curva=rush_from, x=_x(X_CHICO)),
                       _cambio(chico, 0.0, 0.3, caida=-0.35),
                       _cambio(chico, 0.0, 0.3, paso=0.5),
                       _cambio(chico, 0.3, 0.75, rush_into, caida=-np.pi / 2),
                       _cambio(chico, 0.3, 0.8, brazo=0.0),
                       _cambio(chico, 0.5, 0.8, paso=0.0),
                       _cambio(chico, 0.75, 1.0, there_and_back, salto=0.12), run_time=1.0),
               _fuego(X_CHICO - 30, SUELO_CHICO - 4, TINTA, largo=0.2).set_run_time(1.0))
    scene.wait(0.5)
    # Desde el suelo, sube el brazo y el banderín queda derecho.
    scene.play(_animar(escenario, _cambio(chico, curva=ease_out_back, brazo=np.pi / 2),
                       _cambio(chico, 0.4, 1.0, luz=1.0), run_time=1.1))
    return banderin


def construir(scene):
    scene.marco.ir(None, con_logo=False, con_puntos=False, color_fondo=FONDO_OSCURO)
    cx = (AVISO[0] + AVISO[2]) / 2
    cian = _robot(CIAN, -160, 0.8, 1.2)
    lila = _robot(LILA, cx - 80 + LEJOS, -0.7, 0.8, "analista")
    oro = _robot(ORO, cx + 80 + LEJOS, -0.7, 0.8, "ingeniero")
    chico = _robot(VERDE, -160, 0.9, 0.6, suelo=SUELO_CHICO) | {"brazo": BRAZO_EN_ALTO}
    # Los postes van detrás de los robots; la soga, la pancarta, el aviso y el banderín, delante.
    escenario = _escenario([cian, lila, oro, chico]).set_z_index(1)

    estrellas = _bajar_gracias(scene, escenario, cian)
    _llamar(scene, escenario, cian, 0.8, 1560, (LILA, ORO))
    _traer_aviso(scene, escenario, cian, (lila, oro))
    _llamar(scene, escenario, cian, -0.8, -140, (VERDE,))
    banderin = _izar_banderin(scene, escenario, chico)

    # Todos celebran, uno tras otro, con fuegos; el pequeño agita el banderín y las estrellas
    # titilan. Y siguen en loop: cada celebración termina como empieza, así la vuelta no salta.
    robots = (cian, lila, oro, chico)
    _celebrar(scene, escenario, robots, estrellas, 2.2,
              FadeIn(scene.indicador(), shift=UP * 0.1, run_time=0.3))
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    _celebrar(scene, escenario, robots, estrellas, 3.0)
    banderin.clear_updaters()


def _celebrar(scene, escenario, robots, estrellas, segundos, *extra):
    """Brincan uno tras otro con fuegos, el pequeño agita el banderín y las estrellas titilan."""
    cian, lila, oro, chico = robots
    scene.play(_animar(escenario,
                       _cambio(cian, 0.0, 0.2, giro=0.2),
                       _cambio(cian, 0.1, 0.5, there_and_back, salto=0.2),
                       _cambio(chico, 0.2, 0.9, lambda t: np.sin(2 * np.pi * t), brazo=np.pi / 2 + 0.3),
                       _cambio(lila, 0.3, 0.7, there_and_back, salto=0.22),
                       _cambio(oro, 0.45, 0.85, there_and_back, salto=0.22),
                       _cambio(cian, 0.5, 1.0, brazo=2.5), run_time=segundos),
               LaggedStart(*[_fuego(*f) for f in FUEGOS], lag_ratio=0.2, run_time=0.8 * segundos),
               LaggedStart(*[e.animate(rate_func=there_and_back).scale(1.7) for e in estrellas],
                           lag_ratio=0.04, run_time=segundos), *extra)
