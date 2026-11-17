"""¿Qué es un agente?, contado con figuras en 3D que se mueven: una persona pide ayuda porque su
osito tiene frío. Primero el robot (el modelo) solo responde y no pasa nada. Después recorre un
circuito en el suelo: observa al osito, planea y actúa (sube el termostato), vuelve a observar,
y repite (le lleva una manta) hasta que el osito está bien.

Las figuras son modelos de cajas (comun/tres_d.py), como en la portada: en cada cuadro se
mueven, se proyectan y se pintan de atrás hacia adelante, todas en un solo dibujo."""

import numpy as np
from manim import (
    DOWN,
    UP,
    Circle,
    Create,
    Ellipse,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    Polygon,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    smooth,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import caja, chip, flecha, titulo
from comun.escena import MADERA, MADERA_OSCURA, globo
from comun.estilo import (
    AZUL,
    AZUL_OSCURO,
    CIAN,
    CORAL,
    CORAL_OSCURO,
    FONDO,
    GRIS_CLARO,
    GRIS_LINEA,
    GRIS_MEDIO,
    LILA,
    ORO,
    OSCURO,
    TARJETA,
    TEAL,
    TINTA,
    G,
    P,
    U,
)
from comun.tres_d import (
    INCLINACION,
    PANTALLA,
    camara,
    caras,
    mezcla,
    partes_persona,
    partes_robot,
)

# --- El mundo ---------------------------------------------------------------------------

# Sin frases abajo, la escena crece y baja hasta ocupar el alto libre.
CX, CY = 725, 575   # el centro del suelo, en el lienzo
K = 100             # pt del lienzo por unidad del modelo

PELUCHE, PELUCHE_CLARO, HELADO = "#b98556", "#e6c8a0", "#5f9fe0"
COPO = "#d6e9ff"
TAM_OSO = 0.62
MANTA_DOBLADA = np.array((0.3, 0.09, 0.22))
# La manta ya abierta y de pie, a la espalda del osito (en las medidas del osito).
MANTA_PUESTA = np.array((0.66, 0.42, 0.03))
ESPALDA = -0.42
# Los copos que caen alrededor del osito mientras tiene frío: x, z, desfase y tamaño.
COPOS = [(x, z, fase, lado) for (x, z, fase), lado in zip(
    np.random.default_rng(7).uniform((-0.7, -0.45, 0), (0.7, 0.55, 1), (11, 3)),
    (0.03, 0.045, 0.035, 0.05, 0.03, 0.04, 0.05, 0.035, 0.045, 0.03, 0.04))]
BAUL = (5.2, 1.4)
# Las paradas del circuito: nombre y lugar en el suelo (x, z hacia quien mira).
ESTACIONES = (("OBSERVAR", -1.5, 0.9), ("PLANEAR", 0.9, -1.3), ("ACTUAR", 3.0, 0.9))
RADIO = 0.75
RX, RY = RADIO * K, RADIO * K * np.sin(INCLINACION)


def _gira(eje_y, angulo):
    """Mueve una pierna o un brazo: lo gira hacia adelante alrededor de su cadera u hombro."""
    c, s = np.cos(angulo), np.sin(angulo)

    def mover(v):
        x, y, z = v[:, 0], v[:, 1] - eje_y, v[:, 2]
        return np.stack([x, y * c + z * s + eje_y, -y * s + z * c], axis=1)

    return mover


def _mueve(partes, giros):
    """Las mismas cajas, con las de `giros` (índice: movimiento) movidas."""
    partes = list(partes)
    for i, giro in giros.items():
        partes[i] = (*partes[i][:3], giro, *partes[i][4:])
    return partes


def _robot(a):
    """El robot: al caminar balancea piernas y brazos; `carga` le pone la manta en la mano."""
    v = 0.55 * np.sin(a["paso"])
    partes = _mueve(partes_robot(CIAN, a["luz"]), {
        0: _gira(0.3, v), 1: _gira(0.3, -v),
        5: _gira(1.0, a["brazo2"] - v), 6: _gira(1.0, a["brazo"] + v)})
    if a["carga"]:
        partes.append(((0.58, 1.06, 0.5), tuple(MANTA_DOBLADA), CORAL, None))
    return partes


def _persona(a):
    derecho, izquierdo = _gira(1.04, a["brazo"]), _gira(1.04, a["brazo2"])
    return _mueve(partes_persona(LILA), {3: izquierdo, 5: izquierdo, 4: derecho, 6: derecho})


def _tabla(x, y, z, color=CORAL):
    """Una caja entre dos esquinas: de dónde a dónde va en cada eje."""
    return (tuple(float(np.mean(e)) for e in (x, y, z)),
            tuple(abs(e[1] - e[0]) / 2 for e in (x, y, z)), color, None)


def _vuelta(ancho, grueso, franjas, atras, frente, libre, llega, cierra):
    """Una vuelta de la manta alrededor del osito: la espalda, los dos lados (con `llega`
    alcanzan el frente) y las dos solapas (con `cierra` se juntan adelante). `franjas` son
    sus tiras, de abajo hacia arriba (desde, hasta, color); las solapas solo llevan las que
    empiezan en `libre` o más arriba, para que las patas queden por fuera."""
    ancho = MANTA_PUESTA[0] + (ancho - MANTA_PUESTA[0]) * min(1.0, 4 * llega)
    lado = (atras + grueso, atras + grueso + 0.01 + (frente - atras - grueso) * llega)
    borde = ancho - (ancho - 0.1) * cierra
    piezas = []
    for desde, hasta, color in franjas:
        y = (desde, hasta)
        piezas.append(_tabla((-ancho, ancho), y, (atras, atras + grueso), color))
        piezas += [_tabla((s * (ancho - grueso), s * ancho), y, lado, color) for s in (-1, 1)]
        if cierra > 0 and desde >= libre:
            piezas += [_tabla((s * borde, s * ancho), y, (frente - grueso, frente), color)
                       for s in (-1, 1)]
    return piezas


def _manta_puesta(cuanto):
    """La manta sobre el osito, como una capa: empieza de pie a su espalda (0), le rodea los
    lados y se cierra adelante (1). Abajo cae más ancha y gruesa, con su franja dorada, y
    deja salir las patas; arriba le cubre los hombros, y la cabeza queda por fuera."""
    llega, cierra = min(1.0, 2 * cuanto), max(0.0, 2 * cuanto - 1)
    alto = 0.84 + 0.12 * llega
    falda = _vuelta(0.84, 0.16, ((0, 0.26, CORAL), (0.26, 0.4, ORO), (0.4, 0.6, CORAL)),
                    -0.52, 0.52, 0.26, llega, cierra)
    capa = _vuelta(0.74, 0.04, ((0.6, alto, CORAL),), -0.44, 0.42, 0, llega, cierra)
    hombros = [_tabla((s * 0.42, s * (0.66 + 0.08 * llega)), (alto - 0.03, alto + 0.01),
                      (-0.44, -0.39 + 0.81 * llega)) for s in (-1, 1)]
    return (*falda, *capa, *hombros)


def _oso(a):
    """El osito, sentado. Con frío se pone azulado y se abraza (y tiembla, en
    `_Mundo.pintar`); con `abrigo`, lleva la manta."""
    color = mezcla(PELUCHE, HELADO, 0.6 * a["frio"])
    oscuro, brazo = mezcla(color, FONDO, 0.25), _gira(0.85, a["brazo"] + 0.8 * a["frio"])
    # La panza clara se pinta encima de todo: se angosta al paso que la manta se cierra.
    panza = min(0.24, 1.38 - 1.28 * a["manta"])
    # Y los brazos se recogen bajo la manta mientras se cierra, para no asomar a través.
    manga = tuple(np.array((0.11, 0.26, 0.13)) * max(0.02, min(1.0, 2 - 2 * a["manta"])))
    return (
        ((-0.3, 0.12, 0.35), (0.16, 0.12, 0.3), oscuro, None),          # piernas
        ((0.3, 0.12, 0.35), (0.16, 0.12, 0.3), oscuro, None),
        ((0, 0.55, 0), (0.42, 0.4, 0.32), color, None),                 # cuerpo
        ((0, 0.5, 0.325), (panza, 0.24, 0.012), PELUCHE_CLARO, None, 1),
        ((-0.52, 0.62, 0.05), manga, oscuro, brazo),                    # brazos
        ((0.52, 0.62, 0.05), manga, oscuro, brazo),
        ((0, 1.3, 0), (0.42, 0.34, 0.36), color, None),                 # cabeza
        ((0, 1.2, 0.4), (0.18, 0.13, 0.06), PELUCHE_CLARO, None),       # hocico
        ((0, 1.27, 0.465), (0.06, 0.04, 0.01), OSCURO, None, 1),
        ((-0.18, 1.43, 0.365), (0.045, 0.055, 0.01), OSCURO, None, 1),  # ojos
        ((0.18, 1.43, 0.365), (0.045, 0.055, 0.01), OSCURO, None, 1),
        ((-0.34, 1.7, 0), (0.13, 0.11, 0.08), oscuro, None),            # orejas
        ((0.34, 1.7, 0), (0.13, 0.11, 0.08), oscuro, None),
        *(_manta_puesta(a["manta"]) if a["abrigo"] else ()),
    )


def _copos(a):
    """El frío del osito: copos que caen a su alrededor, más pequeños cuanto menos frío."""
    frio, ahora = a["oso"]["frio"], a["ahora"]
    if frio < 0.05:
        return ()
    return tuple(((x + 0.05 * np.sin(3 * ahora + 6 * fase),
                   0.1 + 1.5 * (1 - (0.4 * ahora + fase) % 1), z),
                  (lado * frio,) * 3, COPO, None) for x, z, fase, lado in COPOS)


def _termostato(a):
    """Un poste con su tablero: la barra sube y pasa de azul a coral con la temperatura."""
    alto = 0.12 + 0.24 * a["temp"]
    return (
        ((0, 0.04, 0), (0.3, 0.04, 0.3), GRIS_MEDIO, None),
        ((0, 0.8, 0), (0.06, 0.8, 0.06), GRIS_MEDIO, None),
        ((0, 1.85, 0), (0.42, 0.5, 0.1), GRIS_LINEA, None),
        ((0, 1.85, 0.105), (0.34, 0.42, 0.006), PANTALLA, None, 1),
        ((0, 1.5 + alto, 0.112), (0.11, alto, 0.004), mezcla(AZUL, CORAL, a["temp"]), None, 2),
    )


def _baul(_):
    return (((0, 0.22, 0), (0.5, 0.22, 0.34), MADERA, None),
            ((0, 0.47, 0), (0.54, 0.04, 0.38), MADERA_OSCURA, None))


def _manta(a):
    """La manta suelta: doblada (`abre` = 0) o ya abierta y de pie, con su franja (1)."""
    abre = a["abre"]
    ancho, alto, fondo = MANTA_DOBLADA + (TAM_OSO * MANTA_PUESTA - MANTA_DOBLADA) * abre
    franja = ((0, 1.48 * alto, 0), (ancho + 0.005, 0.037 * abre, fondo + 0.005), ORO, None)
    return (((0, alto, 0), (ancho, alto, fondo), CORAL, None), *((franja,) if abre > 0.05 else ()))


FIGURAS = {"robot": _robot, "persona": _persona, "oso": _oso, "termostato": _termostato,
           "baul": _baul, "manta": _manta, "copos": _copos}


def _actor(tipo, x, z, giro=0.0, tam=1.0, sombra=1.4, **extra):
    """Una figura todavía sin tamaño y de medio lado: entra creciendo y girando hasta `mira`."""
    return dict(tipo=tipo, x=x, z=z, giro=giro - 1.2, mira=giro, tam=tam, sombra=sombra,
                escala=0.0, salto=0.0, ahora=0.0) | extra


def _lugar(v, a):
    """Puntos de una figura (con su tamaño, su giro y su salto) en el mundo."""
    c, s = np.cos(a["giro"]), np.sin(a["giro"])
    x, y, z = (v * a["escala"]).T
    temblor = a.get("temblor", 0.0)
    return np.stack([x * c + z * s + a["x"] + temblor, y + a["salto"] + 0.4 * abs(temblor),
                     -x * s + z * c + a["z"]], axis=1)


def _lienzo(q):
    """Puntos ya en cámara, en pt del lienzo."""
    return [(CX + K * x, CY - K * y) for x, y, _ in q]


def _suelo(x, z):
    return _lienzo(camara(np.array([[x, 0.0, z]])))[0]


def _punto(a, local):
    """Dónde cae en el lienzo un punto de la figura `a` (en sus propias medidas)."""
    return _lienzo(camara(_lugar(np.array([local], dtype=float), a)))[0]


def _tinte(a):
    """Color y fuerza de la sombra. La de los copos es el halo del osito: azul mientras
    tiene frío y dorado cuando ya está abrigado."""
    oso = a.get("oso")
    if oso is None:
        return "#000000", 0.35
    return mezcla(ORO, HELADO, min(1.0, 2 * oso["frio"])), 0.45 * max(oso["frio"], oso["manta"])


def _sombra(a):
    ancho = a["sombra"] * a["escala"] * K * U / (1 + a["salto"])
    color, fuerza = _tinte(a)
    sombra = Ellipse(width=ancho, height=ancho * np.sin(INCLINACION))
    return sombra.set_fill(color, opacity=fuerza).set_stroke(width=0).move_to(
        P(*_suelo(a["x"], a["z"])))


def _figura(a):
    lista = caras(FIGURAS[a["tipo"]](a), lambda v: _lugar(v, a), a["escala"])
    return [Polygon(*[P(*p) for p in _lienzo(cara)]).set_fill(color, opacity=1)
            .set_stroke(color, width=G(0.5)) for _, cara, color in lista]


def _cambio(estado, inicio=0.0, fin=1.0, curva=smooth, **hasta):
    """Un cambio del estado de una figura, entre `inicio` y `fin` (de 0 a 1) de la animación."""
    return estado, hasta, inicio, fin, curva


def _aplicar(cambio, antes, alpha):
    """Lleva un cambio hasta `alpha`. `antes` guarda de dónde partió, desde que empieza: así
    dos cambios seguidos de lo mismo (girar, caminar y volver a girar) no se pisan."""
    estado, hasta, inicio, fin, curva = cambio
    if alpha < inicio:
        return
    if not antes:
        antes.update({k: estado[k] for k in hasta})
    t = curva(float(np.clip((alpha - inicio) / (fin - inicio), 0, 1)))
    for k, v in hasta.items():
        estado[k] = antes[k] + (v - antes[k]) * t


class _Mundo:
    """Todas las figuras en un solo dibujo: un fondo fijo de trazos vacíos que se rellena en
    cada cuadro (como en la portada), con las sombras abajo y las figuras de atrás hacia
    adelante. Lleva un reloj, para que el osito tiemble aunque nadie más se mueva."""

    def __init__(self, *actores):
        self.actores, self.reloj, self.ahora = actores, 0.0, 0.0
        huecos = sum(3 * len(FIGURAS[a["tipo"]](a)) + 13 for a in actores)
        self.dibujo = VGroup(*[VMobject() for _ in range(huecos)]).set_z_index(1)

    def pintar(self):
        vivos = [a for a in self.actores if a["escala"] > 0.05]
        for a in vivos:
            a["ahora"] = self.ahora
            a["temblor"] = 0.07 * a.get("frio", 0.0) * np.sin(38 * self.ahora)
        piezas = [_sombra(a) for a in vivos if a["sombra"]]
        for a in sorted(vivos, key=lambda a: a["z"]):
            piezas += _figura(a)
        assert len(piezas) <= len(self.dibujo)
        for hueco, pieza in zip(self.dibujo, piezas):
            hueco.points = pieza.points
            hueco.match_style(pieza)
        for hueco in self.dibujo[len(piezas):]:
            hueco.clear_points()

    def animar(self, *cambios, run_time=1.0):
        """Aplica los cambios a la vez y repinta el mundo en cada cuadro."""
        inicio, self.reloj = self.reloj, self.reloj + run_time
        antes = [{} for _ in cambios]

        def paso(_, alpha):
            self.ahora = inicio + alpha * run_time
            for cambio, partida in zip(cambios, antes):
                _aplicar(cambio, partida, alpha)
            self.pintar()

        return UpdateFromAlphaFunc(self.dibujo, paso, run_time=run_time, rate_func=linear)


def _camina(a, x, z, giro):
    """Camina hasta (x, z): se gira hacia donde va, da pasos y al llegar queda mirando a `giro`."""
    pasos = max(1, round(0.8 * np.hypot(x - a["x"], z - a["z"])))
    rumbo = 1.0 if x > a["x"] else -1.0
    return [_cambio(a, 0, 0.2, giro=rumbo), _cambio(a, x=x, z=z),
            _cambio(a, curva=linear, paso=a["paso"] + 2 * np.pi * pasos),
            _cambio(a, curva=lambda t: abs(np.sin(2 * np.pi * pasos * t)), salto=0.05),
            _cambio(a, 0.8, 1, giro=giro)]


def _mano(robot):
    """Dónde va la manta doblada cuando el robot la lleva en el brazo levantado."""
    c, s = np.cos(robot["giro"]), np.sin(robot["giro"])
    return dict(x=robot["x"] + 0.58 * c + 0.5 * s, z=robot["z"] - 0.58 * s + 0.5 * c,
                salto=0.97, giro=robot["giro"])


def _parpadeo(t):
    return float(np.sin(2 * np.pi * t) ** 2)



# --- Lo que va pintado en el suelo y encima ---------------------------------------------

def _piso():
    (x0, y0), (x1, y1) = _suelo(-6.1, -2.4), _suelo(6.1, 2.9)
    return caja(x0, y0, x1, y1, "#102633", radio=20, borde=GRIS_CLARO, grosor=1.2)


def _tramo(a, b):
    """La flecha de una parada a la siguiente, de borde a borde de sus discos."""
    a, d = np.array(a), np.subtract(b, a)
    r = 1 / np.hypot(d[0] / (RX + 10), d[1] / (RY + 10))
    return flecha(tuple(a + d * r), tuple(a + d * (1 - r)), color=GRIS_MEDIO, grosor=2,
                  punteada=True, punta=11)


def _rotulo(nombre, lugar, encendido):
    return chip(nombre, lugar[0], lugar[1] + RY + 24, tam=13, alinear=UP * 0, alto=28,
                color=OSCURO if encendido else TINTA, relleno=CIAN if encendido else TARJETA,
                borde=None if encendido else GRIS_LINEA)


class _Pista:
    """El circuito del agente, pintado en el suelo: tres paradas y las flechas entre ellas."""

    APAGADO, ENCENDIDO = mezcla(CIAN, FONDO, 0.86), mezcla(CIAN, FONDO, 0.45)

    def __init__(self):
        lugares = [_suelo(x, z) for _, x, z in ESTACIONES]
        nombres = [nombre for nombre, *_ in ESTACIONES]
        self.flechas = [_tramo(a, b) for a, b in zip(lugares, lugares[1:] + lugares[:1])]
        self.discos = [Ellipse(width=2 * RX * U, height=2 * RY * U).move_to(P(*lugar))
                       .set_fill(self.APAGADO, opacity=1).set_stroke(CIAN, width=G(2))
                       for lugar in lugares]
        self.rotulos = [_rotulo(n, lugar, False) for n, lugar in zip(nombres, lugares)]
        self.vivos = [_rotulo(n, lugar, True).set_opacity(0) for n, lugar in zip(nombres, lugares)]

    def entra(self):
        return [LaggedStart(*[Create(f) for f in self.flechas], lag_ratio=0.3),
                *[FadeIn(m, scale=0.6) for m in self.discos],
                *[FadeIn(m, shift=UP * 0.1) for m in self.rotulos]]

    def enciende(self, *activas):
        """Deja encendidas solo esas paradas."""
        discos = [d.animate.set_fill(self.ENCENDIDO if i in activas else self.APAGADO)
                  for i, d in enumerate(self.discos)]
        rotulos = [r.animate.set_opacity(1 if i in activas else 0)
                   for i, r in enumerate(self.vivos)]
        return discos + rotulos


def _mirada(robot, oso):
    """El haz con que el robot mira al osito: de sus ojos a todo el osito."""
    puntas = (_punto(robot, (0, 1.5, 0.45)), _punto(oso, (0, 1.8, 0)), _punto(oso, (0, 0, 0.5)))
    haz = Polygon(*[P(*p) for p in puntas]).set_fill(CIAN, opacity=0.22)
    return haz.set_stroke(CIAN, width=G(1.2), opacity=0.6).set_z_index(2)


def _visor(oso):
    """El visor con que el robot analiza al osito: cuatro esquinas a su alrededor y la raya
    que lo recorre. Devuelve también cuánto baja la raya."""
    (x0, _), (x1, y1), (_, y0) = (_punto(oso, p) for p in ((-0.95, 0, 0), (0.95, 0, 0.6),
                                                           (0, 2.0, 0)))
    esquinas = VGroup(*[
        VMobject().set_points_as_corners([P(x + 16 * dx, y), P(x, y), P(x, y + 16 * dy)])
        for x, dx in ((x0, 1), (x1, -1)) for y, dy in ((y0, 1), (y1, -1))])
    esquinas.set_stroke(CIAN, width=G(2.5)).set_fill(opacity=0).set_z_index(2)
    raya = Line(P(x0 + 4, y0 + 4), P(x1 - 4, y0 + 4)).set_stroke(CIAN, width=G(2.5))
    return esquinas, raya.set_z_index(2), (y1 - y0 - 8) * U


def _ondas(termostato):
    """El calor que sale del termostato: tres ondas que crecen y se apagan."""
    centro = P(*_punto(termostato, (0, 1.85, 0.1)))
    ondas = [Circle(radius=16 * U).move_to(centro).set_stroke(CORAL, width=G(3))
             .set_fill(opacity=0).set_z_index(2) for _ in range(3)]
    return LaggedStart(*[o.animate.scale(5).set_stroke(opacity=0) for o in ondas],
                       lag_ratio=0.3)


def _nube(contenido, robot):
    """Lo que piensa el robot: una nube sobre su cabeza, unida a ella por tres burbujas que
    crecen de la cabeza a la nube."""
    x, y = _punto(robot, (0.3, 2.35, 0))
    burbujas = [Circle(radius=r * U).move_to(P(x + 14 + 18 * i, y - 8 - 18 * i))
                .set_fill(TARJETA, opacity=1).set_stroke(GRIS_MEDIO, width=G(1.6))
                for i, r in enumerate((4, 6, 8))]
    nube = globo(contenido, x + 90, y - 92, cola=False, tam=17)
    return VGroup(*burbujas, nube).set_z_index(2)


# --- El cuento --------------------------------------------------------------------------

class _Cuento:
    """Las figuras, el circuito y lo que pasa en cada pausa."""

    def __init__(self, scene):
        self.scene = scene
        self.persona = _actor("persona", -5.0, 0.6, 0.5, sombra=1.2, brazo=0.0, brazo2=0.0)
        self.oso = _actor("oso", -3.6, 0.9, 0.35, tam=TAM_OSO, sombra=1.3, frio=1.0, brazo=0.0,
                          manta=0.0, abrigo=0)
        copos = _actor("copos", -3.6, 0.92, 0.35, sombra=1.9, oso=self.oso)
        self.robot = _actor("robot", -0.7, 0.3, -0.3, sombra=1.5, luz=0.0, paso=0.0, brazo=0.0,
                            brazo2=0.0, carga=0)
        self.termostato = _actor("termostato", 4.3, -0.2, -0.45, sombra=0.8, temp=0.0)
        self.manta = _actor("manta", BAUL[0], BAUL[1] + 0.01, -0.3, sombra=0.0, salto=0.51,
                            abre=0.0)
        self.mundo = _Mundo(self.persona, self.oso, copos, self.robot, self.termostato,
                            _actor("baul", *BAUL, -0.3, sombra=1.3), self.manta)
        self.pista = _Pista()

    def toca(self, *anims, cambios=(), run_time=0.6):
        """Una jugada: el mundo siempre se repinta, para que el osito no deje de temblar."""
        self.scene.play(self.mundo.animar(*cambios, run_time=run_time), *anims,
                        run_time=run_time)

    def _globo(self, contenido, a, alto, color=TINTA, tam=17):
        x, y = _punto(a, (0, alto, 0))
        return globo(contenido, x, y - tam - 17, color=color, tam=tam, hacia=x).set_z_index(2)

    def dice(self, contenido, a, alto, *anims, cambios=(), **kw):
        g = self._globo(contenido, a, alto, **kw)
        self.toca(FadeIn(g, shift=UP * 0.1), *anims, cambios=cambios, run_time=0.6)
        return g

    def _grados(self, contenido, color):
        x, y = _punto(self.termostato, (0, 2.4, 0))
        return globo(contenido, x, y - 26, color=color, tam=20, cola=False).set_z_index(2)

    def va(self, parada, giro, *anims):
        """El robot camina hasta una parada del circuito, que se enciende."""
        _, x, z = ESTACIONES[parada]
        tramo = np.hypot(x - self.robot["x"], z - self.robot["z"])
        self.toca(*self.pista.enciende(parada), *anims,
                  cambios=_camina(self.robot, x, z, giro), run_time=0.5 + 0.3 * tramo)

    def observa(self, contenido, bien=False):
        """Va a mirar al osito, lo recorre con el visor y dice (el robot) cómo lo ve."""
        self.va(0, -0.8)
        haz = _mirada(self.robot, self.oso)
        esquinas, raya, alto = _visor(self.oso)
        self.toca(FadeIn(haz), FadeIn(esquinas, scale=1.15), FadeIn(raya), run_time=0.4)
        self.toca(raya.animate(rate_func=there_and_back).shift(alto * DOWN), run_time=1.1)
        nota = self.dice(contenido, self.robot, 2.35, FadeOut(raya),
                         color=TEAL if bien else CORAL_OSCURO)
        self.toca(FadeOut(haz), FadeOut(esquinas), run_time=0.3)
        return nota

    def planea(self, contenido, nota):
        """Va a la parada de planear: se le prende el bombillo y lo que va a hacer aparece en
        una nube de pensamiento (no lo dice)."""
        self.va(1, 0.0, FadeOut(nota))
        nube = _nube(contenido, self.robot)
        self.toca(LaggedStart(*[FadeIn(m, scale=0.4) for m in nube], lag_ratio=0.35),
                  cambios=[_cambio(self.robot, curva=_parpadeo, luz=0.1)], run_time=1.0)
        return nube

    def entra(self):
        self.scene.play(FadeIn(_piso()), run_time=0.4)
        entradas = [_cambio(a, 0.12 * i, 0.4 + 0.12 * i, escala=a["tam"], giro=a["mira"])
                    for i, a in enumerate(self.mundo.actores)]
        self.toca(cambios=entradas, run_time=1.8)
        self.grados = self._grados("18°", AZUL_OSCURO)
        self.toca(FadeIn(self.grados, shift=UP * 0.1), run_time=0.4)

    def solo_responde(self):
        """El problema: el modelo dice qué hacer y se queda quieto. Devuelve lo que sobra."""
        persona, robot = self.persona, self.robot
        self.dice("Mi osito tiene frío", persona, 2.0, cambios=[_cambio(persona, brazo2=1.9)])
        self.toca(cambios=[_cambio(persona, brazo2=0.0), _cambio(robot, giro=-0.7, luz=1.0)])
        consejo = self.dice("Puedes subir la calefacción", robot, 2.35,
                            cambios=[_cambio(robot, brazo=1.9)])
        self.toca(cambios=[_cambio(robot, brazo=0.0)], run_time=1.2)
        return (consejo,)

    def primera_vuelta(self, sobras):
        """El mismo pedido con un agente: observa, planea y actúa (sube el termostato)."""
        self.toca(*[FadeOut(m) for m in sobras], *self.pista.entra(), run_time=1.0)
        idea = self.planea("Subo la calefacción", self.observa("Tiene frío"))
        self.va(2, 0.9, FadeOut(idea))
        self.toca(cambios=[_cambio(self.robot, brazo2=1.7)], run_time=0.5)
        self.toca(Transform(self.grados, self._grados("21°", CORAL_OSCURO)),
                  _ondas(self.termostato),
                  cambios=[_cambio(self.termostato, temp=1.0), _cambio(self.oso, frio=0.5)],
                  run_time=1.4)
        self.toca(cambios=[_cambio(self.robot, brazo2=0.0)], run_time=0.4)

    def segunda_vuelta(self):
        """Vuelve a observar: todavía tiembla. Otra vuelta, ahora con una manta."""
        robot, manta, oso = self.robot, self.manta, self.oso
        idea = self.planea("Le llevo una manta", self.observa("Aún tiembla"))
        self.va(2, 0.9, FadeOut(idea))
        self.toca(cambios=[_cambio(robot, brazo=1.4), _cambio(manta, **_mano(robot))],
                  run_time=0.7)
        # La manta pasa a ser una caja más del robot mientras la lleva, y al llegar se suelta.
        robot["carga"], manta["escala"] = 1, 0.0
        self.toca(cambios=_camina(robot, -2.1, 1.0, -1.0), run_time=2.3)
        robot["carga"] = 0
        manta.update(_mano(robot), escala=1.0)
        self.abriga()

    def abriga(self):
        """La manta se abre en el aire, baja a la espalda del osito y lo envuelve."""
        robot, manta, oso = self.robot, self.manta, self.oso
        atras = TAM_OSO * ESPALDA
        espalda = dict(x=oso["x"] + atras * np.sin(oso["giro"]),
                       z=oso["z"] + atras * np.cos(oso["giro"]), giro=oso["giro"])
        self.toca(cambios=[_cambio(manta, **espalda, salto=1.3, abre=1.0)], run_time=1.0)
        self.toca(cambios=[_cambio(manta, salto=0.0), _cambio(robot, brazo=0.0)], run_time=0.6)
        # Ya en su sitio, la manta pasa a ser del osito: así la cabeza le queda por fuera.
        manta["escala"], oso["abrigo"] = 0.0, 1
        self.toca(cambios=[_cambio(oso, manta=1.0), _cambio(oso, 0.3, 1, frio=0.0)],
                  run_time=1.1)

    def logrado(self):
        """Observa otra vez: ya está bien. Solo entonces responde."""
        nota = self.observa("Ya está bien", bien=True)
        # Salta sin levantar los brazos: los tiene bajo la manta.
        self.toca(cambios=[_cambio(self.oso, curva=there_and_back, salto=0.3)],
                  run_time=0.7)
        self.dice("Listo, ya entró en calor", self.robot, 2.35, FadeOut(nota), color=TEAL,
                  cambios=[_cambio(self.robot, brazo=1.9)])
        salto = _cambio(self.persona, curva=there_and_back, salto=0.3, brazo=2.6, brazo2=2.6)
        self.toca(*self.pista.enciende(0, 1, 2),
                  cambios=[salto, _cambio(self.robot, brazo=0.0)], run_time=0.9)


def construir(scene):
    scene.marco.ir("inicio")
    cuento = _Cuento(scene)
    scene.play(teclear(titulo("¿Qué es un agente?")), run_time=0.6)
    cuento.entra()

    # 1. Lo normal: un modelo que solo responde.
    sobras = cuento.solo_responde()
    scene.next_slide()

    # 2. El mismo pedido con un agente: observa, planea y actúa.
    cuento.primera_vuelta(sobras)
    scene.next_slide()

    # 3. Vuelve a observar y, como no bastó, da otra vuelta.
    cuento.segunda_vuelta()
    scene.next_slide()

    # 4. Hasta que lo logra: entonces responde.
    cuento.logrado()
