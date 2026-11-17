"""Cómo responde un LLM, como el juego de adivinar de Shannon: Sancho y Don Quijote caminan de
noche por la llanura de La Mancha y juegan a acabar la frase. Sancho la empieza; en cada
hueco Don Quijote (el robot, el modelo) reparte probabilidades entre las palabras que podrían
seguir, dice la más probable y esa palabra sube a la frase.

Todo lo que se mueve (lomas, molinos, matas y los dos caminantes) se repinta en cada cuadro
sobre un juego fijo de trazos vacíos, como en la portada: cambiar los mobjects a mitad de una
animación los pintaría dos veces.

En cada pausa siguen caminando en loop. Para que la vuelta no salte, todo lo que pasa se repite
en VUELTA segundos: las matas cada TRAMO, los molinos (que van a la mitad) cada dos de cuatro,
la loma de adelante (a tres cuartos) cada ola, las aspas cada cuarto de giro y los pasos cada
paso. La loma de atrás, muy lejos, no se mueve."""
import numpy as np
from manim import (
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Ellipse,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    LaggedStart,
    Line,
    Polygon,
    Rectangle,
    ReplacementTransform,
    UpdateFromAlphaFunc,
    VGroup,
    VMobject,
    linear,
    smooth,
    there_and_back,
    there_and_back_with_pause,
)

from comun.animaciones import teclear
from comun.componentes import (
    MEDIO,
    SEMI,
    _en_orden,
    caja,
    punto,
    tarjeta,
    texto,
    titulo,
)
from comun.estilo import (
    CIAN,
    FONDO_OSCURO,
    GRIS,
    GRIS_CLARO,
    GRIS_MEDIO,
    ORO,
    TARJETA,
    TINTA,
    VERDE,
    G,
    P,
    U,
)
from comun.tres_d import (
    BLANCO,
    CUERO,
    INCLINACION,
    PELO,
    camara,
    caras,
    girar,
    mezcla,
    partes_persona,
    partes_robot,
)

INICIO = "En un lugar de la"
COMPLETA = INICIO + " Mancha, de cuyo nombre no quiero acordarme"
# En cada hueco, las tres palabras más probables. Es un texto que el modelo vio muchísimas
# veces al entrenarse: por eso la primera gana de lejos.
CANDIDATOS = (
    (("Mancha", 92), ("ciudad", 3), ("montaña", 2)),
    ((",", 88), (".", 6), ("y", 3)),
    (("de", 90), ("había", 4), ("en", 3)),
    (("cuyo", 94), ("su", 2), ("un", 2)),
    (("nombre", 97), ("pueblo", 1), ("dueño", 1)),
    (("no", 96), ("nadie", 2), ("ya", 1)),
    (("quiero", 95), ("puedo", 3), ("recuerdo", 1)),
    (("acordarme", 96), ("recordar", 2), ("decir", 1)),
)
Y_FRASE, TAM = 246, 36
PISO, K = 690, 88             # el suelo y pt del lienzo por unidad del modelo de las figuras
X_SANCHO, X_QUIJOTE = 390, 600
PASO_PT = 70                  # pt de suelo que pasan por segundo al caminar
VUELTA = 24.0                 # segundos de cada vuelta del loop de las pausas
TRAMO = PASO_PT * VUELTA      # pt de suelo que pasan en una vuelta: 1680
GIRO_ASPAS = 17 * (np.pi / 2) / VUELTA   # 17 cuartos de giro por vuelta
X_PANEL, ANCHO_PANEL, Y_PANEL, PASO_FILA, LARGO_100 = 740, 390, 392, 40, 170
PIEZAS_MOLINO = 14
HORIZONTE = PISO - 34         # donde se apoyan los molinos, tras la loma de adelante
BARBA, ACERO = "#eef2f4", "#b4c0c8"
ACERO_OSCURO = mezcla(ACERO, FONDO_OSCURO, 0.35)
PAJA, SAYO = "#c9b182", mezcla(VERDE, FONDO_OSCURO, 0.4)
LOMA_LEJOS, LOMA_CERCA, SUELO, MATA = "#0f2531", "#122c3a", "#153443", "#21495b"


# --- Los dos caminantes --------------------------------------------------------------------

def _quijote():
    """Lo que vuelve Don Quijote al robot: la bacía de barbero por yelmo (más ancha que la
    cabeza, para taparla), la armadura, la barba en punta con bigote y la lanza en la mano
    izquierda (con la derecha señala)."""
    bacia = mezcla(ORO, FONDO_OSCURO, 0.12)
    yelmo = (
        ((0, 1.98, 0), (0.6, 0.11, 0.46), ORO, None),
        ((0, 1.9, 0.54), (0.74, 0.025, 0.08), bacia, None),
        ((-0.67, 1.9, 0), (0.07, 0.025, 0.46), bacia, None),
        ((0.67, 1.9, 0), (0.07, 0.025, 0.46), bacia, None),
    )
    armadura = (
        ((0, 0.72, 0.32), (0.43, 0.35, 0.02), ACERO, None, 3),           # peto
        ((0, 0.56, 0.345), (0.43, 0.025, 0.008), ACERO_OSCURO, None, 4),  # sus placas
        ((0, 0.74, 0.345), (0.43, 0.025, 0.008), ACERO_OSCURO, None, 4),
        ((0, 0.34, 0), (0.47, 0.045, 0.32), CUERO, None),                # cinturón
        ((-0.6, 1.04, 0), (0.17, 0.07, 0.17), ACERO, None),              # hombreras
        ((0.6, 1.04, 0), (0.17, 0.07, 0.17), ACERO, None),
    )
    barba = (
        ((0, 1.2, 0.44), (0.24, 0.07, 0.02), BARBA, None, 3),            # sobre el mentón
        ((0, 1.04, 0.4), (0.2, 0.11, 0.05), BARBA, None, 5),             # y en punta
        ((0, 0.88, 0.4), (0.12, 0.08, 0.05), BARBA, None, 5),
        ((0, 0.76, 0.4), (0.05, 0.06, 0.05), BARBA, None, 5),
        ((-0.15, 1.31, 0.45), (0.13, 0.035, 0.01), BARBA, None, 3),      # bigote
        ((0.15, 1.31, 0.45), (0.13, 0.035, 0.01), BARBA, None, 3),
        ((-0.3, 1.36, 0.45), (0.035, 0.06, 0.01), BARBA, None, 3),
        ((0.3, 1.36, 0.45), (0.035, 0.06, 0.01), BARBA, None, 3),
    )
    lanza = (
        ((-0.76, 1.1, 0.14), (0.035, 1.05, 0.035), CUERO, None),
        ((-0.76, 2.24, 0.14), (0.05, 0.1, 0.05), ACERO, None),
    )
    return yelmo + armadura + barba + lanza


def _sancho():
    """Lo que vuelve Sancho a la persona: la panza, el sombrero de paja y la barba cerrada."""
    return (
        ((0, 0.6, 0.14), (0.43, 0.27, 0.26), SAYO, None),                # panza
        ((0, 0.36, 0), (0.44, 0.04, 0.3), CUERO, None),                  # cinturón
        ((0, 1.9, 0), (0.66, 0.025, 0.62), PAJA, None),                  # ala del sombrero
        ((0, 2.0, 0), (0.43, 0.1, 0.4), mezcla(PAJA, FONDO_OSCURO, 0.1), None),
        ((0, 1.27, 0.36), (0.3, 0.11, 0.02), PELO, None, 3),             # barba
    )


def _con_pasos(partes, p, medio, color=None):
    """Las mismas cajas con las piernas a medio paso: levanta una y luego la otra."""
    paso = np.sin(np.pi * p["fase"])
    for i, lado in enumerate((-1, 1)):
        centro, tam, tono, *resto = partes[i]
        alto = 0.1 * max(0.0, -lado * paso)
        partes[i] = ((medio * lado, centro[1] + alto, 0), tam, color or tono, *resto)
    return partes


def _partes_quijote(p):
    partes = list(partes_robot(CIAN, p["luz"], p["brazo"])) + list(_quijote())
    return _con_pasos(partes, p, 0.24, ACERO)   # grebas


def _partes_sancho(p):
    partes = list(partes_persona(SAYO)) + list(_sancho())
    for i in (4, 6):   # el brazo derecho y su mano se levantan juntos
        partes[i] = (*partes[i][:3], p["brazo"])
    return _con_pasos(partes, p, 0.2)


def _figura(p, partes):
    """La figura de pie en el suelo, con su sombra. Devuelve también cómo llevar un punto de
    su modelo al lienzo."""
    e = p["escala"]
    salto = 0.05 * abs(np.sin(np.pi * p["fase"])) + p["brinco"]

    def lienzo(v):
        q = camara(girar(np.array(v) * e, p["giro"]) + (0, salto, 0))
        return [P(p["x"] + K * x, PISO - K * y) for x, y, _ in q]

    def mundo(v):
        return girar(v * e, p["giro"]) + (0, salto, 0)

    ancho = 1.5 * K * U * e
    sombra = (Ellipse(width=ancho, height=ancho * np.sin(INCLINACION)).move_to(P(p["x"], PISO))
              .set_fill("#000000", opacity=0.35).set_stroke(width=0))
    piezas = [sombra]
    for _, cara, color in caras(partes, mundo, e):
        esquinas = [P(p["x"] + K * x, PISO - K * y) for x, y, _ in cara]
        piezas.append(Polygon(*esquinas).set_fill(color, opacity=1)
                      .set_stroke(color, width=G(0.5)))
    return piezas, lienzo


def _dibujo_quijote(p):
    piezas, lienzo = _figura(p, _partes_quijote(p))
    brillo = Circle(radius=18 * U * p["escala"]).move_to(lienzo([[0, 2.22, 0]])[0])
    return piezas + [brillo.set_stroke(width=0).set_fill(BLANCO, opacity=0.3 * p["luz"])]


def _dibujo_sancho(p):
    return _figura(p, _partes_sancho(p))[0]


def _pintar(trazos, piezas):
    for hueco, pieza in zip(trazos, piezas):
        hueco.points = pieza.points
        hueco.match_style(pieza)
    for hueco in trazos[len(piezas):]:
        hueco.clear_points()


def _cambio(p, curvas=None, **hasta):
    """Lleva el estado de una figura a `hasta`: devuelve la función que lo pone en su punto
    del camino. Cada clave sigue su curva (`smooth` si no se dice otra)."""
    desde = {k: p[k] for k in hasta}
    curvas = curvas or {}

    def poner(alpha):
        for k, v in hasta.items():
            p[k] = desde[k] + (v - desde[k]) * curvas.get(k, smooth)(alpha)

    return poner


# --- La llanura ------------------------------------------------------------------------------

def _loma(alto, onda, corrida):
    xs = np.arange(0, 1441, 40)
    cima = [P(x, PISO - alto * (0.55 + 0.45 * np.sin(x / onda + corrida))) for x in xs]
    return Polygon(*cima, P(1440, PISO), P(0, PISO))


def _aspas(m, eje):
    """Las cuatro aspas de un molino: el palo desde el eje y la vela a un lado."""
    radio, piezas = 150 * m["s"] * U, []
    for k in range(4):
        a = m["ang"] + k * np.pi / 2
        d = np.array([np.cos(a), np.sin(a), 0.0])
        n = np.array([-d[1], d[0], 0.0])
        vela = Polygon(eje + 0.26 * radio * d, eje + radio * d,
                       eje + radio * d + 0.26 * radio * n, eje + 0.26 * radio * d + 0.26 * radio * n)
        piezas.append(vela.set_fill(GRIS, opacity=0.8).set_stroke(width=0))
        piezas.append(Line(eje, eje + radio * d).set_stroke(GRIS, width=G(5 * m["s"])))
    return piezas


def _molino(m):
    """Un molino manchego a lo lejos: la torre, su lado en sombra, el techo, la puerta, la
    ventana, las aspas y el eje."""
    def forma(color, *puntos):
        esquinas = [P(m["x"] + x * m["s"], HORIZONTE - y * m["s"]) for x, y in puntos]
        return Polygon(*esquinas).set_fill(color, opacity=1).set_stroke(width=0)

    eje = P(m["x"], HORIZONTE - 226 * m["s"])
    return [
        forma(GRIS_MEDIO, (-50, 0), (50, 0), (34, 250), (-34, 250)),
        forma(mezcla(GRIS_MEDIO, FONDO_OSCURO, 0.22), (12, 0), (50, 0), (34, 250), (8, 250)),
        forma("#3f5c6a", (-42, 246), (42, 246), (0, 306)),
        forma(FONDO_OSCURO, (-13, 0), (13, 0), (13, 46), (-13, 46)),
        forma(FONDO_OSCURO, (-9, 118), (9, 118), (9, 142), (-9, 142)),
        *_aspas(m, eje),
        Circle(radius=10 * m["s"] * U).move_to(eje).set_fill(GRIS, opacity=1).set_stroke(width=0),
    ]


def _vacio(color):
    return VMobject().set_fill(color, opacity=1).set_stroke(width=0)


class _Llanura:
    """Lo que se mueve: las lomas, los molinos y las matas pasan hacia atrás mientras Sancho y
    Don Quijote caminan. `andar()` es la animación que lo repinta todo en cada cuadro."""

    def __init__(self):
        azar = np.random.default_rng(3)
        self.avance, self.reloj = 0.0, 0.0
        self.lomas = VGroup(_vacio(LOMA_LEJOS), _vacio(LOMA_CERCA))
        # Cuatro molinos, uno cada cuarto de TRAMO, grande y chico alternados: en una vuelta
        # cada uno llega al sitio del que estaba dos puestos más allá, que es igual a él.
        self.molinos = [dict(x0=1130 + k * TRAMO / 4, s=(0.36, 0.27)[k % 2], x=0.0, ang=0.0)
                        for k in range(4)]
        self.aspas = VGroup(*[VGroup(*[VMobject() for _ in range(PIEZAS_MOLINO)])
                              for _ in self.molinos])
        self.semillas = [(azar.uniform(0, TRAMO), azar.uniform(PISO + 18, PISO + 108))
                         for _ in range(18)]
        self.matas = _vacio(MATA)
        self.sancho = dict(x=X_SANCHO - 720, giro=0.75, fase=0.0, brazo=0.0, brinco=0.0,
                           escala=0.86, ritmo=2.5)
        self.quijote = dict(x=X_QUIJOTE - 720, giro=0.75, fase=0.0, brazo=0.0, brinco=0.0,
                            escala=1.0, luz=0.0, ritmo=50 / VUELTA)
        self.trazos = VGroup(VGroup(*[VMobject() for _ in range(80)]),
                             VGroup(*[VMobject() for _ in range(130)]))
        # Los molinos van entre las dos lomas: la de adelante les tapa el pie y quedan lejos.
        self.todo = VGroup(self.lomas[0], self.aspas, self.lomas[1],
                           caja(0, PISO, 1440, 810, SUELO), self.matas, self.trazos)
        self.pintar()

    def pintar(self):
        ola = 0.75 * TRAMO / (2 * np.pi)
        self.lomas[0].points = _loma(120, 210, 0.6).points
        self.lomas[1].points = _loma(56, ola, 2.4 + 0.75 * self.avance / ola).points
        for trazos, m in zip(self.aspas, self.molinos):
            m["x"] = (m["x0"] - 0.5 * self.avance) % TRAMO - 180
            m["ang"] = -GIRO_ASPAS * self.reloj
            _pintar(trazos, _molino(m))
        molde = Rectangle(width=16 * U, height=3 * U).points
        self.matas.clear_points()
        for x, y in self.semillas:
            self.matas.append_points(molde + P((x - self.avance) % TRAMO - 120, y))
        _pintar(self.trazos[0], _dibujo_sancho(self.sancho))
        _pintar(self.trazos[1], _dibujo_quijote(self.quijote))

    def andar(self, run_time, *cambios):
        """Los dos caminan durante `run_time` y, de paso, cada `_cambio` lleva a su figura a
        su nueva pose."""
        avance, reloj = self.avance, self.reloj
        fases = [(p, p["fase"]) for p in (self.sancho, self.quijote)]

        def paso(_, alpha):
            for poner in cambios:
                poner(alpha)
            self.avance = avance + PASO_PT * run_time * alpha
            self.reloj = reloj + run_time * alpha
            for p, fase in fases:
                p["fase"] = fase + p["ritmo"] * run_time * alpha
            self.pintar()

        return UpdateFromAlphaFunc(self.todo, paso, run_time=run_time, rate_func=linear)


def _cielo():
    """Lo que no se mueve: las estrellas (en un solo trazo, fuera del título) y la luna en
    menguante, un disco y otro del color del cielo que lo muerde."""
    azar, molde, estrellas = np.random.default_rng(7), Circle(radius=U).points, VMobject()
    for _ in range(70):
        x, y, radio = azar.uniform(20, 1420), azar.uniform(100, 560), azar.uniform(0.8, 2.0)
        if x > 760 or y > 170:
            estrellas.append_points(molde * radio + P(x, y))
    luna = VGroup(Circle(radius=40 * U).move_to(P(170, 420)).set_fill("#e9f0f3", opacity=0.9),
                  Circle(radius=36 * U).move_to(P(188, 409)).set_fill(FONDO_OSCURO, opacity=1))
    return VGroup(estrellas.set_fill(TINTA, opacity=0.4), luna).set_stroke(width=0)


# --- El juego: la frase y las probabilidades ---------------------------------------------------

def _globo(frase):
    """El globo de lo que va de la frase, del ancho de la frase entera con su margen y con el
    pico hacia Sancho, que la empezó."""
    x0 = frase.get_left()[0] / U + 720 - 40
    x1 = frase.get_right()[0] / U + 720 + 40
    pico = Polygon(P(X_SANCHO + 10, Y_FRASE + 34), P(X_SANCHO + 54, Y_FRASE + 34),
                   P(X_SANCHO + 4, Y_FRASE + 76))
    return VGroup(tarjeta(x0, Y_FRASE - 56, x1, Y_FRASE + 36, radio=22),
                  pico.set_fill(TARJETA, opacity=1).set_stroke(width=0))


def _trozos(frase):
    """Las letras del comienzo y, por cada hueco, las de la palabra que gana."""
    letras = _en_orden(frase)

    def tramo(desde, hasta):
        a = len(COMPLETA[:desde].replace(" ", ""))
        b = len(COMPLETA[:hasta].replace(" ", ""))
        return VGroup(*letras[a:b])

    inicio, piezas, desde = tramo(0, len(INICIO)), [], len(INICIO)
    for candidatos in CANDIDATOS:
        palabra = candidatos[0][0]
        donde = COMPLETA.index(palabra, desde)
        piezas.append(tramo(donde, donde + len(palabra)).set_color(CIAN))
        desde = donde + len(palabra)
    return inicio, piezas


def _hueco(pieza):
    """La raya bajo el lugar de la frase donde va la palabra que falta."""
    x0, x1 = (borde[0] / U + 720 for borde in (pieza.get_left(), pieza.get_right()))
    medio, largo = (x0 + x1) / 2, max(26, x1 - x0)
    return caja(medio - largo / 2, Y_FRASE + 12, medio + largo / 2, Y_FRASE + 16, CIAN, radio=2)


def _mostrar(palabra):
    return f"«{palabra}»" if palabra in ",." else palabra


def _panel(candidatos):
    """Lo que piensa Don Quijote: las tres palabras que podrían seguir, con su probabilidad,
    en una tarjeta unida a su cabeza por dos burbujas."""
    x0 = X_PANEL
    fondo = VGroup(punto(x0 - 48, Y_PANEL + 96, 6, TARJETA), punto(x0 - 24, Y_PANEL + 72, 10, TARJETA),
                   tarjeta(x0, Y_PANEL, x0 + ANCHO_PANEL, Y_PANEL + 3 * PASO_FILA + 24))
    filas = []
    for i, (palabra, pct) in enumerate(candidatos):
        y = Y_PANEL + 32 + i * PASO_FILA
        gana = i == 0
        nombre = texto(_mostrar(palabra), 21, x0 + 132, y + 7, color=TINTA if gana else GRIS,
                       peso=SEMI if gana else MEDIO, alinear=RIGHT)
        largo = max(4, LARGO_100 * pct / 100)
        barra = caja(x0 + 146, y - 10, x0 + 146 + largo, y + 10, CIAN if gana else GRIS_CLARO,
                     radio=3)
        valor = texto(f"{pct} %", 17, x0 + 156 + largo, y + 6, color=TINTA if gana else GRIS)
        filas.append((nombre, barra, valor))
    return fondo, filas


def _aparecer(panel):
    fondo, filas = panel
    return LaggedStart(FadeIn(fondo, shift=UP * 0.1),
                       *[LaggedStart(FadeIn(n), GrowFromEdge(b, LEFT), FadeIn(v), lag_ratio=0.3)
                         for n, b, v in filas], lag_ratio=0.2)


def _quitar(panel):
    fondo, filas = panel
    return FadeOut(VGroup(fondo, *[m for fila in filas for m in fila]))


# --- La diapositiva ----------------------------------------------------------------------------

def construir(scene):
    scene.marco.ir("fundamentos", "0.2")
    frase = texto(COMPLETA, TAM, 720, Y_FRASE, color=TINTA, peso=MEDIO, alinear=ORIGIN)
    inicio, piezas = _trozos(frase)
    llanura = _Llanura()
    sancho, quijote = llanura.sancho, llanura.quijote

    def play(*anims, t, cambios=()):
        scene.play(*anims, llanura.andar(t, *cambios), run_time=t)

    def en_loop():
        """La pausa: el tramo anterior pasa solo a este, que se repite caminando hasta que se
        pasa. El indicador ya está puesto."""
        scene._base_slide_config.auto_next = True
        scene.next_slide(indicador=False, loop=True)
        play(t=VUELTA)

    scene.play(teclear(titulo("¿Cómo responde un LLM?")), run_time=0.7)
    scene.play(FadeIn(_cielo()), FadeIn(llanura.todo), run_time=0.8)
    # Llegan caminando juntos por la llanura, y ya no paran.
    play(t=2.2, cambios=[_cambio(sancho, x=X_SANCHO), _cambio(quijote, x=X_QUIJOTE)])
    # Sancho propone el juego: empieza la frase y la deja a medias.
    play(FadeIn(_globo(frase), shift=UP * 0.1),
         LaggedStart(*[FadeIn(g) for g in inicio], lag_ratio=0.1), t=1.3,
         cambios=[_cambio(sancho, {"brazo": there_and_back}, brazo=2.0)])

    # El primer hueco va despacio para explicarlo; después el juego se acelera.
    anterior = None
    for i, (candidatos, pieza) in enumerate(zip(CANDIDATOS, piezas)):
        ritmo = max(0.4, 0.75 ** i)
        panel, hueco = _panel(candidatos), _hueco(pieza)
        salida = [_quitar(anterior)] if anterior else []
        # Don Quijote piensa: se le prende el bombillo y reparte las probabilidades.
        play(_aparecer(panel), FadeIn(hueco), *salida, t=1.2 * ritmo,
             cambios=[_cambio(quijote, luz=1.0)])
        # Dice la más probable, que sube a la frase, y Sancho la celebra con un brinco.
        indicador = [FadeIn(scene.indicador(), shift=UP * 0.1)] if i == 0 else []
        play(ReplacementTransform(panel[1][0][0].copy(), pieza, path_arc=-0.5), FadeOut(hueco),
             *indicador, t=1.0 * ritmo,
             cambios=[_cambio(quijote, {"brazo": there_and_back}, brazo=2.4, luz=0.0),
                      _cambio(sancho, {"brinco": there_and_back}, brinco=0.22)])
        anterior = panel
        if i == 0:
            en_loop()
            scene.next_slide(indicador=False)
            scene.remove(scene.indicador())

    # Terminan la frase y siguen su camino.
    saludo = {"brazo": there_and_back_with_pause}
    play(_quitar(anterior), FadeIn(scene.indicador(), shift=UP * 0.1), t=1.6,
         cambios=[_cambio(quijote, saludo, brazo=2.4, luz=1.0), _cambio(sancho, saludo, brazo=2.0)])
    # Y siguen caminando en loop hasta que se pasa la diapositiva.
    en_loop()
