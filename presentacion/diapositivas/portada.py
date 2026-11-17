"""La portada: a la izquierda el título y los datos del taller; a la derecha un equipo de
robots en 3D sobre una red: cada uno es un agente en su nodo y los mensajes van de uno a otro,
en loop hasta que se pasa la diapositiva.

Los robots son modelos de cajas (comun/tres_d.py): en cada cuadro se giran, se proyectan y se
pintan sus caras visibles de atrás hacia adelante."""
import numpy as np
from manim import (
    UP,
    Circle,
    Create,
    DashedVMobject,
    Ellipse,
    FadeIn,
    LaggedStart,
    Line,
    Polygon,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    smooth,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import chip, mono, texto, titular
from comun.estilo import (
    AZUL,
    CIAN,
    FONDO_OSCURO,
    GRIS_LINEA,
    LILA,
    ORO,
    TEXTO_SUAVE,
    VERDE,
    G,
    P,
    U,
)
from comun.tres_d import BLANCO, INCLINACION, caras, partes_robot
from comun.tres_d import camara as _camara
from comun.tres_d import mezcla as _mezcla

# --- El modelo 3D -----------------------------------------------------------------------

CX, CY = 1085, 548           # el suelo bajo el robot del centro, en el lienzo
K = 104                      # pt del lienzo por unidad del modelo

# Los compañeros: color, x, z (hacia quien mira) y hacia dónde están girados. Los de atrás
# van cerca del centro y los de adelante más afuera, para que en la pantalla ninguno tape a
# otro, ni quieto ni al moverse.
EQUIPO = ((LILA, -1.5, -1.2, 0.3), (AZUL, 1.5, -1.2, -0.3),
          (VERDE, -2.55, 1.2, 0.5), (ORO, 2.55, 1.2, -0.5))
ESCALA_CENTRO, ESCALA_EQUIPO = 1.2, 0.72
# Quién le habla a quién alrededor del centro (índices de EQUIPO).
VECINOS = ((0, 1), (1, 3), (3, 2), (2, 0))
GIRO_CENTRO = -0.3
BRAZO_ARRIBA = 2.5
# El oficio de cada compañero (tres_d.OFICIOS), en el orden de EQUIPO.
OFICIOS_EQUIPO = ("analista", "abogado", "redactor", "ingeniero")
# Trazos del escenario: por robot, sombra, brillo y hasta tres caras de cada una de sus
# cajas (16 y las de su oficio); y dos por mensaje.
HUECOS = 5 * 70 + 2 * 4


def _lienzo(q):
    return [P(CX + K * x, CY - K * y) for x, y, _ in q]


def _suelo(x, z):
    """Punto del suelo en la pantalla."""
    return _lienzo(_camara(np.array([[x, 0.0, z]])))[0]


def _mundo(v, r):
    """Puntos del robot (ya con su tamaño, su giro y su salto) en el mundo. Con `caida`
    (un cuarto de giro) queda tendido en el suelo: de frente si es positiva y de espaldas si no."""
    caida = r.get("caida", 0.0)
    if caida:
        c, s = np.cos(caida), np.sin(caida)
        x, y, z = v.T
        v = np.stack([x, y * c - z * s + 0.45 * abs(s), y * s + z * c], axis=1)
    c, s = np.cos(r["giro"]), np.sin(r["giro"])
    x, y, z = (v * r["escala"]).T
    return np.stack([x * c + z * s + r["x"], y + r["salto"], -x * s + z * c + r["z"]], axis=1)


def _caras(r):
    partes = partes_robot(r["color"], r["luz"], r["brazo"], r.get("oficio"), r.get("paso", 0.0))
    return caras(partes, lambda v: _mundo(v, r), r["escala"])


def _robot(r):
    """El robot como se ve en este momento: sombra, caras y el brillo de la antena."""
    ancho = 1.5 * r["escala"] * K * U / (1 + r["salto"])
    sombra = Ellipse(width=ancho, height=ancho * np.sin(INCLINACION))
    sombra.set_fill("#000000", opacity=0.35).set_stroke(width=0).move_to(_suelo(r["x"], r["z"]))
    piezas = [sombra]
    for _, cara, color in _caras(r):
        piezas.append(Polygon(*_lienzo(cara)).set_fill(color, opacity=1)
                      .set_stroke(color, width=G(0.5)))
    punta = _lienzo(_camara(_mundo(np.array([[0, 2.22, 0]]), r)))[0]
    piezas.append(Circle(radius=20 * r["escala"] * U).move_to(punta).set_stroke(width=0)
                  .set_fill(BLANCO, opacity=0.3 * r["luz"]))
    return piezas


def _mensaje(m):
    """Un mensaje que va por el suelo de un agente a otro; `t` es cuánto lleva del camino."""
    if not 0 < m["t"] < 1:
        return []
    de, a = np.array(m["de"]), np.array(m["a"])
    lugar = _suelo(*(de + (a - de) * m["t"]))
    halo = Circle(radius=19 * U).set_fill(m["color"], opacity=0.45).set_stroke(width=0)
    nucleo = Circle(radius=7.5 * U).set_fill(BLANCO, opacity=1).set_stroke(width=0)
    return [halo.move_to(lugar), nucleo.move_to(lugar)]


def _escena(robots, mensajes):
    """Todo lo que se mueve, en un solo dibujo y ya en orden: los mensajes en el suelo y
    encima los robots, del más lejano al más cercano."""
    piezas = [p for m in mensajes for p in _mensaje(m)]
    for r in sorted(robots, key=lambda r: r["z"]):
        if r["escala"] > 0.05:
            piezas += _robot(r)
    return piezas


def _escenario(robots):
    """El mobject que se anima: un fondo fijo de trazos vacíos que `_pintar` rellena en cada
    cuadro. Son siempre los mismos trazos: si se cambiaran por otros a mitad de una animación,
    manim seguiría pintando también los del primer cuadro y cada robot saldría dos veces."""
    escenario = VGroup(*[VMobject() for _ in range(HUECOS)])
    escenario.robots, escenario.mensajes = robots, []
    return escenario


def _pintar(escenario):
    piezas = _escena(escenario.robots, escenario.mensajes)
    assert len(piezas) <= HUECOS
    for hueco, pieza in zip(escenario, piezas):
        hueco.points = pieza.points
        hueco.match_style(pieza)
    for hueco in escenario[len(piezas):]:
        hueco.clear_points()


def _estado(color, x, z, giro):
    """Un robot todavía sin tamaño y de medio lado: entra creciendo y girando hasta su sitio."""
    return dict(color=color, x=x, z=z, giro=giro - 1.3, escala=0.0, salto=0.0, brazo=0.0,
                luz=0.0)


def _cambio(estado, inicio=0.0, fin=1.0, curva=smooth, **hasta):
    """Un cambio del estado de un robot o de un mensaje, entre `inicio` y `fin` (de 0 a 1)
    de la animación."""
    return estado, hasta, inicio, fin, curva


def _animar(escenario, *cambios, run_time=1.0):
    """Aplica los cambios a la vez y repinta el escenario entero en cada cuadro. Va todo en
    un solo mobject para que el orden de pintado sea siempre el mismo: quien está adelante
    tapa a quien está atrás, se mueva o no."""
    desde = [{k: estado[k] for k in hasta} for estado, hasta, *_ in cambios]

    def paso(mob, alpha):
        for (estado, hasta, inicio, fin, curva), antes in zip(cambios, desde):
            t = curva(float(np.clip((alpha - inicio) / (fin - inicio), 0, 1)))
            for k, v in hasta.items():
                estado[k] = antes[k] + (v - antes[k]) * t
        _pintar(escenario)

    return UpdateFromAlphaFunc(escenario, paso, run_time=run_time, rate_func=linear)


def _enviar(escenario, pares, run_time=1.3):
    """Manda un mensaje por cada par (de, a) de robots; quien lo recibe se enciende y da un
    saltito."""
    escenario.mensajes[:] = [dict(de=(de["x"], de["z"]), a=(a["x"], a["z"]), t=0.0,
                                  color=de["color"]) for de, a in pares]
    destinos = list({id(a): a for _, a in pares}.values())
    return _animar(escenario,
                   *[_cambio(m, 0.0, 0.65, t=1.0) for m in escenario.mensajes],
                   *[_cambio(a, 0.55, 1.0, there_and_back, salto=0.16) for a in destinos],
                   *[_cambio(a, 0.55, 0.85, luz=1.0) for a in destinos if a["luz"] < 1],
                   run_time=run_time)


# --- La red en el suelo -----------------------------------------------------------------

def _base(color, x, z, radio):
    """El nodo de un agente: un disco en el suelo con el borde de su color."""
    ancho = 2 * radio * K * U
    disco = Ellipse(width=ancho, height=ancho * np.sin(INCLINACION)).move_to(_suelo(x, z))
    return disco.set_fill(_mezcla(color, FONDO_OSCURO, 0.85), opacity=1).set_stroke(
        color, width=G(2))


def _enlace(a, b, color):
    linea = Line(_suelo(*a), _suelo(*b), color=_mezcla(color, FONDO_OSCURO, 0.15),
                 stroke_width=G(2.6))
    return DashedVMobject(linea, num_dashes=max(4, int(linea.get_length() / (10 * U))),
                          dashed_ratio=0.6)


def _red():
    """Los enlaces entre los agentes (del centro a cada uno y de cada uno a su vecino) y,
    encima, sus nodos."""
    lugares = [(x, z) for _, x, z, _ in EQUIPO]
    enlaces = [_enlace((0, 0), lugar, color) for lugar, (color, *_) in zip(lugares, EQUIPO)]
    enlaces += [_enlace(lugares[i], lugares[j], GRIS_LINEA) for i, j in VECINOS]
    bases = [_base(CIAN, 0, 0, 0.8)] + [_base(color, x, z, 0.62) for color, x, z, _ in EQUIPO]
    return enlaces, bases


# --- El texto ---------------------------------------------------------------------------

X = 90


def construir(scene):
    scene.marco.ir(None, con_logo=False, con_puntos=False, color_fondo=FONDO_OSCURO)
    semillero = chip("SEMILLERO APERTURE", X, 270, color=FONDO_OSCURO, relleno=CIAN, tam=21)
    arriba = titular("De Prompts", 88, X, 402, color=BLANCO)
    abajo = titular("a Agentes", 88, X, 490, color=BLANCO, t2c={"Agentes": CIAN})
    bajada = texto("Inteligencia Artificial Agéntica con Python", 25, X, 542, color=TEXTO_SUAVE)
    firma = VGroup(mono("DICTA", 16, X, 626, color=CIAN, espaciado=1.8),
                   texto("Jerónimo Hoyos Botero", 30, X + 92, 628, color=BLANCO))

    centro = _estado(CIAN, 0, 0, GIRO_CENTRO)
    equipo = [_estado(*datos) | {"oficio": oficio}
              for datos, oficio in zip(EQUIPO, OFICIOS_EQUIPO)]
    escenario = _escenario([centro, *equipo])
    enlaces, bases = _red()

    # Primero la red (enlaces y nodos) y después un agente sobre cada nodo.
    scene.play(FadeIn(semillero, shift=UP * 0.1), run_time=0.4)
    scene.play(teclear(arriba),
               LaggedStart(*[Create(e) for e in enlaces], lag_ratio=0.1), run_time=0.8)
    scene.play(teclear(abajo),
               LaggedStart(*[FadeIn(b, scale=0.5) for b in bases], lag_ratio=0.15), run_time=0.7)
    entradas = [_cambio(r, 0.28 + 0.14 * i, 0.58 + 0.14 * i, escala=ESCALA_EQUIPO, giro=giro)
                for i, (r, (*_, giro)) in enumerate(zip(equipo, EQUIPO))]
    entra = _cambio(centro, 0.0, 0.36, escala=ESCALA_CENTRO, giro=GIRO_CENTRO)
    scene.play(_animar(escenario, entra, *entradas, run_time=3.2),
               FadeIn(bajada, shift=UP * 0.1, run_time=0.5))
    scene.play(_animar(escenario, *[_cambio(r, luz=1.0) for r in (centro, *equipo)],
                       run_time=0.6))

    scene.play(FadeIn(firma, shift=UP * 0.1), FadeIn(scene.indicador(), shift=UP * 0.1),
               run_time=0.5)
    _en_loop(scene, escenario, centro, equipo)


def _en_loop(scene, escenario, centro, equipo):
    """Sin parar, sigue en loop hasta que se pasa la diapositiva: el del centro levanta el
    brazo y reparte, los compañeros hablan entre sí, le responden y baja el brazo. Cada
    vuelta termina como empieza, así no salta."""
    scene._base_slide_config.auto_next = True
    scene.next_slide(indicador=False, loop=True)
    scene.play(_animar(escenario, _cambio(centro, brazo=BRAZO_ARRIBA), run_time=0.9))
    scene.play(_enviar(escenario, [(centro, r) for r in equipo]))
    scene.play(_enviar(escenario, [(equipo[i], equipo[j]) for i, j in VECINOS]))
    scene.play(_enviar(escenario, [(r, centro) for r in equipo]))
    escenario.mensajes.clear()
    scene.play(_animar(escenario, _cambio(centro, brazo=0.0), run_time=0.9))
    scene.wait(0.6)
