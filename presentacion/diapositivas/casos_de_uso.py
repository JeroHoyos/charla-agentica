"""Para qué se usa un LLM dentro de un software: tres casos, cada uno con su robot vestido
para el oficio y haciendo su trabajo. Primero uno por pausa, en un cuarto que llena la
pantalla; al final los tres en franjas, uno debajo del otro, trabajando a la vez.

Cada caso es `_caso(L, hablar)`: devuelve lo que ya está en la escena y un generador de
tiempos (las animaciones de cada tiempo y cuánto duran). Los casos se dibujan en las
coordenadas del cuarto grande de `comun.escena`; `L` las lleva a su lugar: más grandes en el
cuarto de la pausa, más pequeñas en su franja de la vista general. En pequeño no hay globos:
los textos no se alcanzarían a leer.

Los robots se redibujan en cada cuadro (`Robot`): el brazo sube y baja en un solo movimiento
y al caminar dan pasos, en vez de saltar entre dos poses quietas."""
from itertools import zip_longest
from math import cos, pi, sin

import numpy as np
from manim import (
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    Flash,
    Polygon,
    Transform,
    UpdateFromAlphaFunc,
    VGroup,
    there_and_back,
)
from manim.utils.rate_functions import smooth

from comun.animaciones import teclear
from comun.componentes import (
    SEMI,
    caja,
    chip,
    icono_centrado,
    linea,
    punto,
    tarjeta,
    texto,
    titulo,
)
from comun.escena import (
    BORDE_SUELO,
    PISO,
    SUELO,
    X0,
    X1,
    archivador,
    escritorio,
    globo,
    hoja,
    persona,
    sello,
)
from comun.escena import PARED as PARED_CUARTO
from comun.estilo import (
    AZUL,
    CIAN,
    CORAL,
    GRIS,
    GRIS_MEDIO,
    LILA,
    ORO,
    OSCURO,
    TARJETA,
    TEAL,
    TINTA,
    VERDE,
    G,
    P,
)
from comun.tres_d import caras, girar, partes_robot

CENTRO = (720, 373)
ALTO_ROBOT = 176


class Lienzo:
    """Agranda o encoge y mueve lo que se dibuja en el cuarto grande: `k` es la escala y
    (cx, cy) el punto al que va el centro del cuarto."""

    def __init__(self, k=1.0, cx=CENTRO[0], cy=CENTRO[1]):
        self.k, self.d = k, P(cx, cy) - P(*CENTRO)

    def p(self, x, y):
        return P(*CENTRO) + (P(x, y) - P(*CENTRO)) * self.k + self.d

    def m(self, mob):
        return mob.scale(self.k, about_point=P(*CENTRO)).shift(self.d)

    def ir(self, mob, x, y, arco=-0.5):
        return mob.animate(path_arc=arco).move_to(self.p(x, y))


def _centrado(k, medio, cx, piso):
    """El lienzo que pone el punto `medio` del suelo del cuarto grande en (cx, piso)."""
    return Lienzo(k, cx - (medio - CENTRO[0]) * k, piso - (PISO - CENTRO[1]) * k)


def _lomo(a):
    """Sube y baja suave: 0 al empezar y al terminar, 1 en la mitad."""
    return sin(pi * a) ** 2


class Robot:
    """El robot del caso, con su oficio. Se redibuja en cada cuadro: `gesto()` levanta el
    brazo y lo baja en un solo movimiento, `mover()` lo lleva a otra x dando pasos (piernas
    y brazos al vaivén, un rebote leve) y `quieto()` lo deja respirar mientras pasa lo demás."""

    def __init__(self, L, cx, color, oficio, giro):
        self.L, self.x, self.giro = L, cx, giro
        self.base = partes_robot(color, luz=1.0, brazo=0.0, oficio=oficio)
        # La escala y el suelo salen de la pose quieta: así el robot no cambia de tamaño
        # cuando levanta el brazo o una pierna.
        puntos = np.concatenate([c for _, c, _ in caras(self.base, lambda v: girar(v, giro))])
        self.k = ALTO_ROBOT / (puntos[:, 1].max() - puntos[:, 1].min())
        self.medio, self.abajo = (puntos[:, 0].max() + puntos[:, 0].min()) / 2, puntos[:, 1].min()
        self.mob = self._dibujo(cx, giro)

    def _partes(self, brazo, fase, aire):
        """Las cajas en una pose: `brazo` sube el brazo derecho, `fase` mueve piernas y
        brazos al caminar y `aire` sube el cuerpo (el rebote del paso o la respiración)."""
        vaiven = sin(fase)
        partes = []
        for i, (centro, medio, color, giro_brazo, *capa) in enumerate(self.base):
            x, y, z = centro
            if i in (0, 1):  # piernas: una adelante y la otra atrás; la que avanza sube
                lado = 1 if i == 0 else -1
                z += 0.16 * vaiven * lado
                y += 0.07 * max(0.0, vaiven * lado)
            else:
                y += aire
            if i == 5:  # brazo izquierdo: va al contrario de la pierna izquierda
                giro_brazo = -0.45 * vaiven
            elif i == 6:
                giro_brazo = brazo + 0.45 * vaiven
            partes.append(((x, y, z), medio, color, giro_brazo, *capa))
        return partes

    def _dibujo(self, x, giro, brazo=0.0, fase=0.0, aire=0.0):
        dibujo = VGroup()
        for _, cara, tono in caras(self._partes(brazo, fase, aire), lambda v: girar(v, giro)):
            esquinas = [P(x + self.k * (px - self.medio), PISO - self.k * (py - self.abajo))
                        for px, py, _ in cara]
            dibujo.add(Polygon(*esquinas).set_fill(tono, opacity=1)
                       .set_stroke(tono, width=G(0.5)))
        return self.L.m(dibujo)

    def _anim(self, hasta=None, brazo=0.0):
        desde = self.x
        hasta = desde if hasta is None else hasta
        self.x = hasta
        pasos = round(abs(hasta - desde) / 70)
        # Si camina hacia donde no mira, se voltea al salir y vuelve a mirar al llegar.
        vuelta = -2 * self.giro if (hasta - desde) * self.giro < 0 else 0.0

        def pose(mob, a):
            s = smooth(a)
            giro = self.giro + vuelta * smooth(min(1.0, 5 * a, 5 * (1 - a)))
            if pasos:
                fase = 2 * pi * pasos * s
                aire = 0.05 * abs(sin(fase))
            else:
                fase, aire = 0.0, 0.03 * _lomo(a)
            mob.become(self._dibujo(desde + (hasta - desde) * s, giro, brazo * _lomo(a),
                                    fase, aire))

        return UpdateFromAlphaFunc(self.mob, pose)

    def gesto(self, brazo=1.6):
        return self._anim(brazo=brazo)

    def mover(self, x):
        return self._anim(hasta=x)

    def quieto(self):
        return self._anim()


def _globo(L, hablar, contenido, x, y, quien, color=TINTA, tam=16):
    """Un globo, o nada si la escena va en pequeño."""
    return [L.m(globo(contenido, x, y, color=color, tam=tam, hacia=quien))] if hablar else []


def _aparece(mobs):
    return [FadeIn(m, shift=UP * 0.1) for m in mobs]


def _visto(L, x, y):
    s = L.m(sello(x, y))
    return [FadeIn(s, scale=0.4), Flash(s, color=TEAL, line_length=0.12 * L.k,
                                         flash_radius=0.28 * L.k)], s


# --- 1. Atender clientes --------------------------------------------------------------------

# El color del cliente, la hora (en horas desde la medianoche), la pregunta y la respuesta.
CHARLAS = ((LILA, 10, "¿Hay apartamentos en Laureles?", "Sí, tres. ¿Agendamos visita?"),
           (VERDE, 27, "¿Aceptan mascotas?", "Sí, en el 302 y en el 405"))

RELOJ, RADIO_RELOJ = (1110, 300), 50
CARATULA, ARO = "#eef3f5", "#2b5263"


def _reloj(L, horas):
    """El reloj de pared de la oficina con las manecillas en `horas`. Abajo, en la carátula,
    un sol de día o una luna de noche: las manecillas no dicen si es a. m. o p. m."""
    (cx, cy), r = RELOJ, RADIO_RELOJ
    partes = [punto(cx, cy, r + 7, ARO), punto(cx, cy, r, CARATULA)]
    for i in range(12):
        a = i * pi / 6
        largo = 9 if i % 3 == 0 else 5
        partes.append(linea(cx + (r - 5) * sin(a), cy - (r - 5) * cos(a),
                            cx + (r - 5 - largo) * sin(a), cy - (r - 5 - largo) * cos(a),
                            OSCURO, 3 if i % 3 == 0 else 1.6))
    if 6 <= horas % 24 < 18:
        partes.append(punto(cx, cy + 22, 7, ORO))
    else:
        partes += [punto(cx, cy + 22, 7, GRIS_MEDIO), punto(cx + 4, cy + 19, 6, CARATULA)]
    for angulo, largo, grosor in ((horas * pi / 6, 0.5 * r, 5), (horas * 2 * pi, 0.78 * r, 3)):
        partes.append(linea(cx, cy, cx + largo * sin(angulo), cy - largo * cos(angulo),
                            OSCURO, grosor, redondeada=True))
    partes.append(punto(cx, cy, 4, CORAL))
    return L.m(VGroup(*partes))


def _atender(L, hablar=True):
    asesor = Robot(L, 880, CIAN, "asesor", -0.4)
    mesa = L.m(escritorio(880, 220))
    # El reloj va solo en grande: en la franja pequeña no cabe en la pared.
    reloj = _reloj(L, CHARLAS[0][1]) if hablar else VGroup()
    hora = [CHARLAS[0][1]]

    def girar_a(cuando):
        """Las manecillas avanzan hasta `cuando`, dando las vueltas que haga falta."""
        if not hablar or cuando == hora[0]:
            return []
        desde, hora[0] = hora[0], cuando
        return [UpdateFromAlphaFunc(reloj, lambda m, a: m.become(
            _reloj(L, desde + (cuando - desde) * smooth(a))))]

    def tiempos():
        for color, cuando, pregunta, respuesta in CHARLAS:
            cliente = L.m(persona(420, color))
            vueltas = girar_a(cuando)
            yield [FadeIn(cliente, shift=RIGHT * 0.4 * L.k), *vueltas,
                   asesor.quieto()], 1.6 if vueltas else 0.6
            dice = _globo(L, hablar, pregunta, 400, 290, 420)
            yield [*_aparece(dice), asesor.quieto()], 0.6
            contesta = _globo(L, hablar, respuesta, 900, 280, 880, color=TEAL)
            yield [asesor.gesto(2.4), *_aparece(contesta)], 1.0
            yield [FadeOut(cliente), *[FadeOut(g) for g in dice + contesta]], 0.4

    return [asesor.mob, mesa, reloj], tiempos()


# --- 2. Leer documentos ---------------------------------------------------------------------

AREAS = (("VENTAS", VERDE, 900), ("ARRIENDOS", AZUL, 1030), ("QUEJAS", CORAL, 1160))
LEIDO = "Venta, Laureles, 3 alcobas"


def _ficha(L, color, x, y):
    """Lo que sale de leer una hoja: los datos en renglones de colores."""
    renglones = [caja(x - 20, y - 18 + 12 * i, x + 20 - 8 * (i % 2), y - 12 + 12 * i, c,
                      radio=2) for i, c in enumerate((color, CIAN, LILA))]
    return L.m(VGroup(caja(x - 28, y - 28, x + 28, y + 28, TARJETA, radio=5, borde=color,
                           grosor=1.6), *renglones))


def _leer(L, hablar=True):
    lector = Robot(L, 600, VERDE, "analista", 0.3)
    mesas = [L.m(escritorio(600, 200)), L.m(escritorio(300, 150))]
    pila = [L.m(hoja(290 + 6 * i, 470 - 6 * i, lineas=4)) for i in range(3)]
    cajones = [L.m(archivador(x, ancho_=104, alto=110, cajones=1)) for _, _, x in AREAS]
    letreros = [L.m(chip(n, x, PISO - 140, color=OSCURO, relleno=c, tam=12,
                         alinear=UP * 0)) for n, c, x in AREAS]

    def tiempos():
        for i, (_, color, x) in enumerate(AREAS):
            papel = pila.pop()
            yield [L.ir(papel, 560, 440), lector.quieto()], 0.6
            dice = _globo(L, hablar and i == 0, LEIDO, 640, 290, 600, color=TEAL, tam=15)
            ficha = _ficha(L, color, 560, 440)
            yield [lector.gesto(2.4), *_aparece(dice), Transform(papel, ficha)], 0.9
            yield [L.ir(papel, x, PISO - 70), *[FadeOut(g) for g in dice],
                   lector.quieto()], 0.7
            yield [FadeOut(papel, scale=0.5),
                   cajones[i].animate(rate_func=there_and_back).scale(1.06)], 0.4

    return [lector.mob, *mesas, *pila, *cajones, *letreros], tiempos()


# --- 3. Automatizar un proceso --------------------------------------------------------------

PASOS = ((700, "calendario", "Agendo la visita"), (960, "sobre", "Le aviso al asesor"))
ASESORA = 1150


def _automatizar(L, hablar=True):
    operario = Robot(L, 440, CORAL, "ingeniero", 0.35)
    cosas = [L.m(icono_centrado(n, x, 420, 8)) for x, n, _ in PASOS]
    asesora = L.m(persona(ASESORA, LILA))
    pedido = L.m(hoja(300, 430, lineas=3))

    def tiempos():
        pide = _globo(L, hablar, "Visita el sábado, 10 a. m.", 300, 340, 300)
        yield [FadeIn(pedido, shift=UP * 0.1), *_aparece(pide), operario.quieto()], 0.6
        yield [L.ir(pedido, 400, 440), *[FadeOut(g) for g in pide], operario.quieto()], 0.6
        yield [FadeOut(pedido, scale=0.6)], 0.3
        hechos = []
        for (x, _, dice), cosa in zip(PASOS, cosas):
            dicho = _globo(L, hablar, dice, x - 110, 290, x - 130, color=TEAL, tam=15)
            yield [operario.mover(x - 130), *_aparece(dicho)], 1.0
            yield [operario.gesto(1.4), cosa.animate(rate_func=there_and_back).scale(1.15)], 0.7
            flash, visto = _visto(L, x + 34, 448)
            hechos.append(visto)
            yield [*flash, *[FadeOut(g) for g in dicho], operario.quieto()], 0.5
        aviso = cosas[1].copy()
        yield [L.ir(aviso, ASESORA, 330), operario.quieto()], 0.7
        listo = _globo(L, hablar, "Me llegó", ASESORA, 270, ASESORA, color=TEAL)
        yield [FadeOut(aviso, scale=0.5), *_aparece(listo), operario.quieto()], 0.5
        yield [operario.mover(440), *[FadeOut(m) for m in hechos + listo]], 1.3

    # El robot va de último: al caminar pasa por delante del calendario, no por detrás.
    return [*cosas, asesora, operario.mob], tiempos()


# El nombre, el ejemplo, el color, el caso y la x del suelo que va al medio de su cuarto.
CASOS = (
    ("Atender clientes", "Contesta preguntas a cualquier hora", CIAN, _atender, 715),
    ("Leer documentos", "Saca los datos y los ordena", VERDE, _leer, 718),
    ("Automatizar procesos", "Hace los pasos que antes eran a mano", CORAL, _automatizar, 690),
)


def _correr(scene, *generadores):
    """Corre los tiempos de varios casos a la vez: cada tiempo dura lo del más largo."""
    for tiempos in zip_longest(*generadores):
        anims = [a for t in tiempos if t for a in t[0]]
        scene.play(*anims, run_time=max(t[1] for t in tiempos if t))


# --- Uno por pausa, en un cuarto que llena la pantalla --------------------------------------

K_GRANDE, TECHO_G, PISO_G = 1.2, 206, 650


def _cuarto():
    """El cuarto de `comun.escena`, más alto: baja hasta casi el borde de la pantalla."""
    pared = caja(X0, TECHO_G, X1, PISO_G, PARED_CUARTO, radio=14)
    suelo = Polygon(P(X0, PISO_G), P(X1, PISO_G), P(X1 + 22, PISO_G + 50),
                    P(X0 - 22, PISO_G + 50))
    suelo.set_fill(SUELO, opacity=1).set_stroke(width=0)
    borde = caja(X0, PISO_G - 1.5, X1, PISO_G + 1.5, BORDE_SUELO)
    return VGroup(pared, suelo, borde)


def _uno(scene, i, nombre, color, caso, medio):
    numero = chip(f"{i + 1}  {nombre}", 124, 240, color=OSCURO, relleno=color, tam=18)
    fijo, tiempos = caso(_centrado(K_GRANDE, medio, (X0 + X1) / 2, PISO_G))
    scene.play(FadeIn(numero, shift=UP * 0.1), *_aparece(fijo), run_time=0.6)
    _correr(scene, tiempos)
    scene.next_slide()


# --- Los tres a la vez, en franjas ----------------------------------------------------------

K_MINI, ALTO_FRANJA, HUECO, Y_FRANJA = 0.6, 158, 12, 222
X_FRANJA, X_FIN, X_CUARTO = X0, 1330, 500
PARED, SUELO_MINI = "#16323f", "#1d3f4e"


def _franja(i, nombre, ejemplo, color, caso, medio):
    """Un caso en pequeño: su franja con el nombre a la izquierda y el cuarto a la derecha,
    con lo que hay en él, y sus tiempos."""
    y0 = Y_FRANJA + i * (ALTO_FRANJA + HUECO)
    y1, piso = y0 + ALTO_FRANJA, y0 + 126
    fijo, tiempos = caso(_centrado(K_MINI, medio, (X_CUARTO + X_FIN) / 2, piso), hablar=False)
    pared = VGroup(caja(X_CUARTO, y0 + 12, X_FIN - 14, piso, PARED, radio=8),
                   caja(X_CUARTO, piso - 1, X_FIN - 14, piso + 12, SUELO_MINI))
    grupo = VGroup(tarjeta(X_FRANJA, y0, X_FIN, y1),
                   caja(X_FRANJA, y0 + 14, X_FRANJA + 5, y1 - 14, color, radio=2), pared, *fijo,
                   texto(nombre, 26, X_FRANJA + 34, y0 + 72, color=TINTA, peso=SEMI),
                   texto(ejemplo, 17, X_FRANJA + 34, y0 + 106, color=GRIS))
    return grupo, tiempos


def _general(scene):
    pares = [_franja(i, *caso) for i, caso in enumerate(CASOS)]
    scene.play(*[FadeIn(t, shift=UP * 0.15) for t, _ in pares], run_time=0.8)
    _correr(scene, *[g for _, g in pares])


def construir(scene):
    scene.marco.ir("fundamentos", "0.3")
    scene.play(teclear(titulo("¿Para qué sirve un LLM en tu software?")), run_time=0.8)
    fondo = _cuarto()
    scene.play(FadeIn(fondo), run_time=0.4)
    for i, (nombre, _, color, caso, medio) in enumerate(CASOS):
        antes = list(scene.mobjects)
        _uno(scene, i, nombre, color, caso, medio)
        nuevos = [m for m in scene.mobjects if m not in antes]
        scene.play(*[FadeOut(m) for m in nuevos], run_time=0.5)
    scene.play(FadeOut(fondo), run_time=0.4)
    _general(scene)
