"""Las analogías del taller. Cada concepto se cuenta en tres tiempos dentro de una
oficina (el system prompt en un teatro, el prompt caching en un control de trenes, la
memoria en hilos de mensajes, las tools en una cabina con tubos y MCP en una estación
espacial): primero
el problema que había, después la escena que lo arregla y al final su nombre. El robot es el
modelo; las personas, quienes lo rodean. Aquí no hay
código: el código está en los notebooks.

Cada `_escena()` devuelve lo que ya está en el cuarto, la función que anima el problema (y
devuelve lo que hay que quitar) y la función que anima la solución. Un robot detrás de un
escritorio va antes que él en la lista, para que el escritorio le tape las piernas."""

import math
import random

from manim import (
    DOWN,
    PI,
    UP,
    CapStyleType,
    Create,
    FadeIn,
    FadeOut,
    Flash,
    Indicate,
    LaggedStart,
    Polygon,
    Rotate,
    Transform,
    VGroup,
    VMobject,
    Wiggle,
    there_and_back,
)

from comun.animaciones import teclear
from comun.componentes import (
    NEGRITA,
    caja,
    centrado,
    etiqueta,
    icono_centrado,
    linea,
    marca,
    punto,
    titulo,
)
from comun.escena import (
    BORDE_SUELO,
    PARED,
    SUELO,
    TECHO,
    X0,
    X1,
    globo,
    hoja,
    llevar,
    persona,
    robot,
    sello,
)
from comun.estilo import (
    AZUL,
    AZUL_SUAVE,
    CELESTE,
    CIAN,
    CIAN_SUAVE,
    CORAL,
    GRIS,
    GRIS_LINEA,
    GRIS_MEDIO,
    LILA,
    LILA_SUAVE,
    ORO,
    ORO_SUAVE,
    OSCURO,
    TARJETA,
    TEAL,
    TINTA,
    VERDE,
    VERDE_SUAVE,
    G,
    P,
)
from comun.tres_d import figura, mezcla, partes_robot


def _entra(scene, *mobs, run_time=0.45):
    scene.play(*[FadeIn(m, shift=UP * 0.12) for m in mobs], run_time=run_time)


def _camina(mob, x):
    """Lleva una figura de pie hasta `x`, sin despegarla del suelo."""
    return mob.animate.set_x(P(x, 0)[0])


def _dice(scene, contenido, x, y, color=None, tam=17, hacia=None):
    """Aparece un globo y lo devuelve. En coral, lo que sale mal; en teal, lo que sale bien.
    `hacia` es la x de quien habla: la cola del globo apunta ahí."""
    g = globo(contenido, x, y, **({"color": color} if color else {}), tam=tam, hacia=hacia)
    scene.play(FadeIn(g, shift=UP * 0.1), run_time=0.45)
    return g


def _marca(scene, x, y, bien=True, radio=13):
    s = sello(x, y, bien=bien, radio=radio)
    scene.play(FadeIn(s, scale=0.4), Flash(s, color=TEAL if bien else CORAL, line_length=0.12,
                                           flash_radius=0.28), run_time=0.45)
    return s


# --- Piezas que usan varias escenas ---------------------------------------------------------

MINI = 150  # alto de los robots pequeños que hacen un oficio


def _letrero(contenido, x, y, color=TINTA, tam=14, relleno=TARJETA):
    return globo(contenido, x, y, color=color, tam=tam, cola=False, relleno=relleno)


# Lo que sale mal en las analogías rehechas: un rojo rosado, no el coral (se ve naranja).
ERROR = "#f0607a"


# --- Bloque 1: una llamada ------------------------------------------------------------------


# --- Bloque 2: del modelo al agente ---------------------------------------------------------

# El teatro: el actor es el mismo, el guion lo cambia el director tras el telón.
TELON, TELON_OSCURO, TABLAS = "#a9433a", "#7f2f29", "#c2a273"
TABLAS_OSCURAS = "#96784b"
# Sin las frases de abajo, el teatro baja hasta casi el borde y las figuras crecen.
ESCENA_X0, ESCENA_X1, TABLADO, SALA_PISO = 400, 1040, 620, 670
GRANDE = 1.3
# (guion que escribe el director, papel del actor, lo que responde)
GUIONES = (("Eres abogado", "abogado", "Lee bien el contrato"),
           ("Eres analista de datos", "analista", "Mira primero los números"),
           ("Eres asesor inmobiliario", "asesor", "El apartamento de Laureles"))
MANO = (800, 556)
DIRECTOR = 1185


def _telon(x0, x1):
    """Un paño del telón con sus pliegues; abierto o cerrado tiene las mismas piezas, para
    que pase de un estado al otro con Transform."""
    paso = (x1 - x0) / 5
    pliegues = [caja(x0 + (i + 0.5) * paso - 2.5, 242, x0 + (i + 0.5) * paso + 2.5, TABLADO,
                     TELON_OSCURO) for i in range(5)]
    return VGroup(caja(x0, 242, x1, TABLADO, TELON), *pliegues)


def _telones(abierto):
    medio = (ESCENA_X0 + ESCENA_X1) / 2
    if abierto:
        return _telon(ESCENA_X0, ESCENA_X0 + 56), _telon(ESCENA_X1 - 56, ESCENA_X1)
    return _telon(ESCENA_X0, medio), _telon(medio, ESCENA_X1)


def _sala():
    """El cuarto de siempre, con el piso más abajo."""
    pared = caja(X0, TECHO, X1, SALA_PISO, PARED, radio=14)
    suelo = Polygon(P(X0, SALA_PISO), P(X1, SALA_PISO), P(X1 + 22, SALA_PISO + 48),
                    P(X0 - 22, SALA_PISO + 48))
    suelo.set_fill(SUELO, opacity=1).set_stroke(width=0)
    return VGroup(pared, suelo, caja(X0, SALA_PISO - 1.5, X1, SALA_PISO + 1.5, BORDE_SUELO))


def _salta(mob, alto=16, veces=1):
    """Saltitos en el sitio: así se mueven las figuras cuando hablan o reaccionan."""
    return mob.animate(rate_func=lambda t: there_and_back(t * veces % 1)).shift(
        P(0, -alto) - P(0, 0))


def _pasos(scene, mob, dx, n=2, run_time=0.5):
    """Camina `dx` en `n` pasos cortos, cada uno con un pequeño arco."""
    for _ in range(n):
        scene.play(mob.animate(path_arc=-0.5 if dx > 0 else 0.5).shift(P(dx / n, 0) - P(0, 0)),
                   run_time=run_time / n)


PROP = (560, 470)  # donde el actor muestra lo que recomienda, a la luz del foco


def _prop(papel):
    """Lo que el actor le muestra al público según su papel."""
    cx, cy = PROP
    marco = caja(cx - 58, cy - 58, cx + 58, cy + 58, TARJETA, radio=12, borde=ORO, grosor=2)
    if papel == "abogado":
        dibujo = VGroup(hoja(cx - 4, cy, 58, 74, lineas=5), sello(cx + 20, cy + 26, radio=14))
    elif papel == "analista":
        dibujo = icono_centrado("barras", cx, cy, 10)
    else:
        dibujo = icono_centrado("casa", cx, cy - 4, 9)
    return VGroup(marco, dibujo)


def _escenario(abierto=False):
    """El tablado, el foco, los dos paños del telón y la cenefa de arriba."""
    tablado = VGroup(caja(ESCENA_X0 - 20, TABLADO, ESCENA_X1 + 20, SALA_PISO, TABLAS),
                     caja(ESCENA_X0 - 20, TABLADO, ESCENA_X1 + 20, TABLADO + 8, TABLAS_OSCURAS))
    foco = Polygon(P(680, 242), P(760, 242), P(880, TABLADO), P(560, TABLADO))
    foco.set_fill(ORO, opacity=0.16 if abierto else 0).set_stroke(width=0)
    izq, der = _telones(abierto)
    cenefa = VGroup(caja(ESCENA_X0 - 20, 206, ESCENA_X1 + 20, 244, TELON_OSCURO),
                    caja(ESCENA_X0 - 20, 240, ESCENA_X1 + 20, 244, ORO))
    return tablado, foco, izq, der, cenefa


class _Teatro:
    """El actor (el modelo) es siempre el mismo y el público le pregunta lo mismo; el director
    le cambia el guion tras el telón y con cada guion responde otra cosa y muestra algo de su
    papel. Las figuras dan saltitos al hablar y el director camina hasta el telón."""

    def __init__(self):
        self.publico = [persona(165, AZUL, piso=SALA_PISO, e=GRANDE),
                        persona(300, LILA, piso=SALA_PISO, e=GRANDE * 0.92)]
        self.tablado, self.foco, self.izq, self.der, self.cenefa = _escenario()
        self.actor = robot(720, piso=TABLADO, alto=176 * GRANDE)
        self.director = persona(DIRECTOR, TEAL, piso=SALA_PISO, e=GRANDE)
        self.pregunta, self.guion, self.sobras = None, None, []

    def fijo(self):
        return [*self.publico, self.tablado, self.foco, self.actor, self.izq, self.der,
                self.cenefa, self.director]

    def telon(self, abierto):
        a, b = _telones(abierto)
        return [Transform(self.izq, a), Transform(self.der, b),
                self.foco.animate.set_fill(opacity=0.16 if abierto else 0)]

    def preguntar(self, scene):
        if self.pregunta is not None:
            scene.play(Indicate(self.pregunta, color=TINTA, scale_factor=1.06),
                       _salta(self.publico[0], 14), run_time=0.45)
            return
        self.pregunta = globo("¿Qué me recomiendas?", 260, 392, hacia=230)
        scene.play(FadeIn(self.pregunta, shift=UP * 0.1), _salta(self.publico[0], 14),
                   run_time=0.5)

    def falla(self, scene):
        scene.play(*self.telon(abierto=True), run_time=0.8)
        scene.play(_salta(self.actor, 12), run_time=0.4)
        self.preguntar(scene)
        duda = globo("Eh... ¿de qué obra hablamos?", 720, 345, color=ERROR, hacia=720)
        scene.play(FadeIn(duda, shift=UP * 0.1), Wiggle(self.actor, rotation_angle=0.06),
                   run_time=0.8)
        scene.play(*[Wiggle(m, rotation_angle=0.05, n_wiggles=4) for m in self.publico],
                   run_time=0.7)
        sobras, self.pregunta = [self.pregunta, duda], None
        return sobras

    def nuevo_guion(self, scene, escrito, papel):
        """Cierra el telón, el director escribe el guion, lo lleva hasta el telón, se lo lanza
        al actor (que se viste para el papel) y vuelve a su sitio."""
        # Lo que dice el director, en un globo como los demás; en oro, el color del guion.
        nota = globo(escrito, DIRECTOR - 20, 392, color=ORO, hacia=DIRECTOR)
        hoja_ = hoja(DIRECTOR - 55, 585, 42, 54, lineas=4, relleno=ORO_SUAVE, borde=ORO)
        salen = [FadeOut(m) for m in self.sobras]
        if self.guion is not None:
            salen.append(self.guion.animate.move_to(P(DIRECTOR - 55, 585)).set_opacity(0))
        scene.play(*salen, *self.telon(abierto=False), FadeIn(nota, shift=UP * 0.1),
                   FadeIn(hoja_, scale=0.6), run_time=0.5)
        _pasos(scene, VGroup(self.director, hoja_), -70, run_time=0.5)
        scene.play(llevar(hoja_, *MANO, arco=0.7),
                   Transform(self.actor, robot(720, piso=TABLADO, alto=176 * GRANDE,
                                               oficio=papel)), run_time=0.6)
        _pasos(scene, self.director, 70, run_time=0.4)
        self.guion, self.sobras = hoja_, [nota]

    def responder(self, scene, papel, dice):
        """El actor responde con un saltito y muestra lo que recomienda; el público aplaude."""
        respuesta = globo(dice, 720, 345, color=TEAL, hacia=720)
        prop = _prop(papel)
        desde = prop.copy().scale(0.2).move_to(P(*MANO))
        scene.play(FadeIn(respuesta, shift=UP * 0.1), _salta(self.actor, 14, veces=2),
                   run_time=0.6)
        scene.play(Transform(desde, prop, path_arc=0.6), run_time=0.5)
        scene.remove(desde)
        scene.add(prop)
        scene.play(Flash(prop, color=ORO, line_length=0.15, flash_radius=0.75),
                   *[_salta(m, 18, veces=2) for m in self.publico], run_time=0.7)
        self.sobras += [respuesta, prop]

    def arreglo(self, scene):
        for i, (escrito, papel, dice) in enumerate(GUIONES):
            if i:
                scene.next_slide()
            self.nuevo_guion(scene, escrito, papel)
            scene.play(*self.telon(abierto=True), run_time=0.4 if i else 0.6)
            self.preguntar(scene)
            self.responder(scene, papel, dice)


def _teatro():
    obra = _Teatro()
    return obra.fijo(), obra.falla, obra.arreglo


def _en_teatro(scene, numero, pregunta, pista, dibujo, bloque="anatomia", sala=None):
    """Como `analogia`, pero sin frases ni rótulos abajo: el escenario ocupa todo el alto y
    cada paso lleva su pausa (las pone `arreglo`)."""
    scene.marco.ir(bloque, numero)
    fijo, falla, arreglo = dibujo()
    scene.play(teclear(titulo(pregunta)), run_time=0.7)
    scene.play(FadeIn((sala or _sala)()), run_time=0.5)
    scene.play(LaggedStart(*[FadeIn(m, shift=UP * 0.12) for m in fijo], lag_ratio=0.15),
               run_time=0.8)
    sobras = falla(scene)
    scene.next_slide()
    scene.play(*[FadeOut(m) for m in sobras], run_time=0.4)
    arreglo(scene)


def manual(scene):
    """El público ve primero al actor sin guion, después un guion por pausa."""
    _en_teatro(scene, "2.1", "¿Qué es el system prompt?", "Piensa en una obra de teatro.",
               _teatro)


# El prompt caching: el prompt es un tren que pasa por un control. El revisor recuerda el
# último tren y lo compara vagón por vagón desde la locomotora: lo que coincide pasa gratis y,
# desde el primer vagón distinto, lee todo lo que sigue y cada vagón leído cuesta una moneda.
MONEDA_OSCURA, LOCOMOTORA, METAL_OSCURO = "#8a6d2e", "#3a6578", "#24485a"
ARCO, RIEL = 760, 640  # dónde está el control y la altura de los rieles
PASO, MEDIO_VAGON = 132, 60  # de un vagón al siguiente, y la mitad de su ancho
RECUERDO_X, RECUERDO_Y = (200, 328, 456, 584), 350
REPISA, VIAJES = 430, (985, 1075, 1165, 1255)  # dónde caen las monedas de cada viaje
# Las partes de un prompt de verdad: las instrucciones y los documentos no cambian; la fecha y
# la pregunta cambian en cada llamada.
FIJOS = ("Instrucciones", "Catálogo")
CAMBIA_COLOR = AZUL


def _moneda(x, y):
    return VGroup(caja(x - 17, y - 4, x + 17, y + 7, MONEDA_OSCURA, radio=5),
                  caja(x - 17, y - 8, x + 17, y + 3, ORO, radio=5))


def _color(nombre):
    """Lo fijo va en cian; lo que cambia en cada llamada, en azul."""
    return CIAN if nombre in FIJOS else CAMBIA_COLOR


def _vagon(nombre, cx):
    color, w = _color(nombre), MEDIO_VAGON
    return VGroup(caja(cx - w, RIEL - 68, cx + w, RIEL - 14, color, radio=7),
                  caja(cx - w, RIEL - 22, cx + w, RIEL - 14, mezcla(color, OSCURO, 0.35),
                       radio=3),
                  centrado(nombre, 12, cx, RIEL - 41, color=OSCURO, peso=NEGRITA),
                  punto(cx - 32, RIEL - 9, 8, METAL_OSCURO),
                  punto(cx + 32, RIEL - 9, 8, METAL_OSCURO))


def _locomotora(cx):
    return VGroup(caja(cx - 50, RIEL - 60, cx + 30, RIEL - 14, LOCOMOTORA, radio=6),
                  caja(cx - 50, RIEL - 96, cx - 8, RIEL - 60, LOCOMOTORA, radio=4),
                  caja(cx - 42, RIEL - 88, cx - 16, RIEL - 70, CELESTE, radio=3),
                  caja(cx + 6, RIEL - 82, cx + 20, RIEL - 60, GRIS_MEDIO, radio=2),
                  caja(cx + 30, RIEL - 34, cx + 46, RIEL - 22, ORO, radio=3),
                  punto(cx - 28, RIEL - 9, 9, METAL_OSCURO), punto(cx + 12, RIEL - 9, 9,
                                                                   METAL_OSCURO))


def _tren(nombres, frente):
    """La locomotora en `frente` y los vagones detrás, en el orden del prompt."""
    vagones = [_vagon(n, frente - 116 - PASO * i) for i, n in enumerate(nombres)]
    return _locomotora(frente), vagones


def _recuerdo(nombre, cx):
    """Lo que el revisor recuerda de un vagón: una ficha pequeña en su pizarra."""
    if nombre is None:
        return caja(cx - 58, RECUERDO_Y - 20, cx + 58, RECUERDO_Y + 20, PARED, radio=6,
                    borde=GRIS_MEDIO, grosor=1.2)
    return VGroup(caja(cx - 58, RECUERDO_Y - 20, cx + 58, RECUERDO_Y + 20, _color(nombre),
                       radio=6),
                  centrado(nombre, 12, cx, RECUERDO_Y + 4, color=OSCURO, peso=NEGRITA))


def _inspector():
    """El modelo vestido de revisor de tren, en lo alto del arco y mirando un poco al tren que
    llega. No se gira durante la escena: al cambiar de vista, las caras se deforman."""
    return figura(partes_robot(CIAN, luz=1.0, oficio="revisor"), ARCO, RIEL - 182, 150, -0.25)


class _Control:
    """El revisor en lo alto del arco, su pizarra con el último tren y la repisa de monedas."""

    def __init__(self):
        self.revisor = _inspector()
        poste = dict(radio=3)
        self.arco = VGroup(caja(ARCO - 78, RIEL - 180, ARCO - 66, RIEL + 4, METAL_OSCURO, **poste),
                           caja(ARCO + 66, RIEL - 180, ARCO + 78, RIEL + 4, METAL_OSCURO, **poste),
                           caja(ARCO - 86, RIEL - 182, ARCO + 86, RIEL - 164, LOCOMOTORA,
                                radio=4))
        self.rieles = VGroup(caja(X0 + 10, RIEL, X1 - 10, RIEL + 5, GRIS_MEDIO, radio=2),
                             *[caja(x, RIEL + 5, x + 26, RIEL + 11, TABLAS_OSCURAS, radio=1)
                               for x in range(X0 + 20, X1 - 30, 54)])
        self.pizarra = caja(126, RECUERDO_Y - 40, 658, RECUERDO_Y + 40, TARJETA, radio=10,
                            borde=GRIS_LINEA, grosor=1.4)
        self.fichas = [_recuerdo(None, x) for x in RECUERDO_X]
        self.memoria = [None] * 4
        self.repisa = caja(VIAJES[0] - 40, REPISA, VIAJES[-1] + 40, REPISA + 10, TABLAS_OSCURAS,
                           radio=3)
        self.loco, self.vagones, self.viaje, self.sobras, self.monedas = None, [], 0, [], 0

    def fijo(self):
        return [self.rieles, self.pizarra, *self.fichas, self.repisa, self.revisor, self.arco]

    def entra(self, scene, nombres):
        """Sale el tren anterior por la derecha y entra uno nuevo por la izquierda."""
        if self.loco is not None:
            viejo = VGroup(self.loco, *self.vagones)
            scene.play(viejo.animate.shift(P(420, 0) - P(0, 0)).set_opacity(0), run_time=0.6)
            scene.remove(viejo)
        self.loco, self.vagones = _tren(nombres, ARCO - 120)
        tren = VGroup(self.loco, *self.vagones)
        scene.add_foreground_mobject(self.arco)
        scene.play(FadeIn(tren, shift=P(120, 0) - P(0, 0)), run_time=0.6)

    def avanza(self, scene, i, rapido):
        """Mueve el tren hasta que el vagón `i` queda bajo el arco."""
        mover = P(ARCO, 0)[0] - self.vagones[i].get_center()[0]
        scene.play(VGroup(self.loco, *self.vagones).animate.shift([mover, 0, 0]),
                   run_time=0.3 if rapido else 0.5)

    def coincide(self, scene, i):
        scene.play(Indicate(self.fichas[i], color=TEAL, scale_factor=1.08),
                   _salta(self.revisor, 7), run_time=0.3)
        self.sobras.append(_marca(scene, RECUERDO_X[i] + 40, RECUERDO_Y - 18, radio=10))

    def lee(self, scene, i, nombre, pila):
        """El revisor lee el vagón: lo anota en la pizarra y suelta una moneda en la repisa."""
        haz = Polygon(P(ARCO - 20, RIEL - 164), P(ARCO + 20, RIEL - 164), P(ARCO + 48, RIEL - 66),
                      P(ARCO - 48, RIEL - 66))
        haz.set_fill(CIAN, opacity=0.35).set_stroke(width=0)
        moneda = _moneda(ARCO, RIEL - 40)
        # Se inclina un poco hacia el vagón, con los pies quietos, y vuelve.
        agacha = self.revisor.animate(rate_func=there_and_back).rotate(
            -0.08, about_point=self.revisor.get_bottom())
        scene.play(FadeIn(haz), FadeIn(moneda, scale=0.5), agacha,
                   Transform(self.fichas[i], _recuerdo(nombre, RECUERDO_X[i])), run_time=0.35)
        destino = P(pila, REPISA - 6 - 13 * self.monedas)
        scene.play(FadeOut(haz), moneda.animate(path_arc=-1.0).move_to(destino), run_time=0.45)
        self.monedas += 1
        self.memoria[i] = nombre

    def pasa(self, scene, nombres):
        """Un viaje completo: compara cada vagón con lo que recuerda, desde la locomotora."""
        self.entra(scene, nombres)
        pila = VIAJES[self.viaje]
        self.viaje, self.monedas, igual = self.viaje + 1, 0, True
        scene.play(FadeIn(_letrero(f"viaje {self.viaje}", pila, REPISA + 30, tam=11)),
                   run_time=0.25)
        for i, nombre in enumerate(nombres):
            igual = igual and self.memoria[i] == nombre
            self.avanza(scene, i, rapido=igual)
            if igual:
                self.coincide(scene, i)
            else:
                self.lee(scene, i, nombre, pila)
        quitar, self.sobras = self.sobras, []
        if quitar:
            scene.play(*[FadeOut(m) for m in quitar], run_time=0.3)

    def dice(self, scene, contenido, color, bien):
        g = globo(contenido, ARCO, 262, color=color, hacia=ARCO)
        mueve = (_salta(self.revisor, 14, veces=2) if bien
                 else Wiggle(self.revisor, rotation_angle=0.07))
        scene.play(FadeIn(g, shift=UP * 0.1), mueve, run_time=0.6)
        return g

    def falla(self, scene):
        self.pasa(scene, ["Lunes 9:00", *FIJOS, "¿Hay casas?"])
        scene.next_slide()
        self.pasa(scene, ["Lunes 9:05", *FIJOS, "¿Cuánto cuesta?"])
        return [self.dice(scene, "Cambió el primero: leo todo", ERROR, bien=False)]

    def reordena(self, scene):
        """El tren parado se reacomoda: la fecha pasa de primera a tercera, detrás de lo fijo."""
        fecha, fijos, pregunta = self.vagones[0], self.vagones[1:3], self.vagones[3]
        puestos = [v.get_center() for v in self.vagones]
        scene.play(*[v.animate.move_to(puestos[i]) for i, v in enumerate(fijos)],
                   fecha.animate(path_arc=-2.2).move_to(puestos[2]), run_time=1.0)
        self.vagones = [*fijos, fecha, pregunta]

    def arreglo(self, scene):
        self.reordena(scene)
        g = self.dice(scene, "Lo fijo adelante, lo que cambia atrás", TEAL, bien=True)
        scene.next_slide()
        scene.play(FadeOut(g), run_time=0.3)
        self.pasa(scene, [*FIJOS, "Lunes 9:05", "¿Cuánto cuesta?"])
        scene.next_slide()
        self.pasa(scene, [*FIJOS, "Lunes 9:10", "¿Y con garaje?"])
        self.dice(scene, "Solo leo lo nuevo", TEAL, bien=True)


def _cache():
    control = _Control()
    return control.fijo(), control.falla, control.arreglo


def cache(scene):
    """Con la fecha en el primer vagón lo lee todo en cada viaje; con la fecha detrás de lo
    fijo, solo lee la fecha y la pregunta."""
    _en_teatro(scene, "2.2", "¿Qué es el prompt caching?",
               "Piensa en un tren que pasa por un control.", _cache)


# La memoria: el modelo olvida todo entre una llamada y otra. Cada conversación es un hilo
# (un tendedero) donde se cuelgan sus mensajes, y en cada llamada el hilo entero vuelve al modelo.
ASESOR_X, HILO_X0, HILO_X1 = 1160, 140, 1000


def _mensaje(contenido, de_cliente):
    """Un mensaje colgado: azul lo que dice el cliente, cian lo que responde el asesor."""
    return _letrero(contenido, 0, 0, color=OSCURO, relleno=AZUL if de_cliente else CIAN,
                    tam=15)


# Las tools: el robot es un operario de fábrica. Las máquinas están ahí, pero solo puede usar
# las que tienen un botón en su tablero. La jefa (tú) le instala los botones; él decide cuál
# oprimir y con qué datos, y la máquina (tu código) hace el trabajo y le devuelve el resultado.
OPERARIO_X, CABLE_Y, JEFA_X = 470, 645, 700
MAQUINAS = {"Catálogo": (900, "casa"), "Calculadora": (1060, "calculadora"),
            "Agenda": (1220, "calendario")}
BOTONES_X = (405, 470, 535)  # un botón por máquina, en el mismo orden
# (lo que pregunta Ana, el pedido del robot, la máquina, lo que devuelve, lo que responde)
PEDIDOS_TOOLS = (("¿Qué hay hoy en Laureles?", "Catálogo: buscar en Laureles", "Catálogo",
                  "2 apartamentos, desde 345 M", "Hay dos, desde 345 millones"),
                 ("¿Y la cuota mensual?", "Calculadora: 345 M a 20 años", "Calculadora",
                  "2,9 M al mes", "Unos 2,9 millones al mes"),
                 ("¿Lo puedo ver el sábado?", "Agenda: visita el sábado", "Agenda",
                  "Sábado 10:00, apartado", "Listo, el sábado a las 10"))


def _maquina(nombre):
    x, dibujo = MAQUINAS[nombre]
    return VGroup(caja(x - 66, 470, x + 66, SALA_PISO, LOCOMOTORA, radio=8),
                  caja(x - 54, 484, x + 54, 512, OSCURO, radio=5),
                  centrado(nombre, 13, x, 503, color=TINTA, peso=NEGRITA),
                  icono_centrado(dibujo, x, 580, 7),
                  punto(x + 48, 645, 6, GRIS_MEDIO))


def _consola():
    """La mesita del tablero, delante del operario y a la altura de su cintura: le tapa las
    piernas y tiene un hueco por botón."""
    return VGroup(caja(362, 580, 578, 596, METAL_OSCURO, radio=6),
                  caja(370, 592, 570, SALA_PISO, LOCOMOTORA, radio=10),
                  *[caja(x - 27, 610, x + 27, 652, OSCURO, radio=8, borde=GRIS_MEDIO, grosor=1.5)
                    for x in BOTONES_X])


def _boton(nombre):
    i = list(MAQUINAS).index(nombre)
    x = BOTONES_X[i]
    return VGroup(caja(x - 25, 612, x + 25, 650, TARJETA, radio=8, borde=CIAN, grosor=2),
                  icono_centrado(MAQUINAS[nombre][1], x, 631, 3))


def _papel(contenido, relleno):
    return _letrero(contenido, 0, 0, color=OSCURO, relleno=relleno, tam=14)


class _Fabrica:
    """Sin botones el operario solo adivina; con los botones que le instala la jefa, oprime el
    que toca, la máquina trabaja y el resultado le llega antes de responder."""

    def __init__(self):
        self.ana = persona(150, AZUL, piso=SALA_PISO, e=1.15)
        self.robot = robot(OPERARIO_X, piso=SALA_PISO, alto=176 * 1.2)
        self.tablero = _consola()
        self.cable = VGroup(linea(560, CABLE_Y, 1230, CABLE_Y, GRIS_MEDIO, 6, redondeada=True),
                            *[punto(MAQUINAS[n][0], CABLE_Y, 7, GRIS_MEDIO) for n in MAQUINAS])
        self.maquinas = {n: _maquina(n) for n in MAQUINAS}
        self.jefa = persona(JEFA_X, TEAL, piso=SALA_PISO, e=1.05)
        self.botones = {n: _boton(n) for n in MAQUINAS}
        self.sobras = []

    def fijo(self):
        return [self.ana, self.robot, self.tablero, self.cable, *self.maquinas.values()]

    def pregunta(self, scene, contenido):
        g = globo(contenido, 200, 425, hacia=150)
        scene.play(FadeIn(g, shift=UP * 0.1), _salta(self.ana, 12), run_time=0.5)
        return g

    def responde(self, scene, contenido, color):
        g = globo(contenido, OPERARIO_X, 405, color=color, hacia=OPERARIO_X)
        scene.play(FadeIn(g, shift=UP * 0.1), _salta(self.robot, 12), run_time=0.5)
        return g

    def falla(self, scene):
        dijo = self.pregunta(scene, "¿Qué hay hoy en Laureles?")
        # Busca un botón y no hay ninguno.
        huecos = self.tablero[2:]
        scene.play(_salta(self.robot, 8), LaggedStart(
            *[Indicate(h, color=ERROR, scale_factor=1.1) for h in huecos], lag_ratio=0.3),
            run_time=0.8)
        adivina = self.responde(scene, "Mmm… ¿unos diez?", ERROR)
        scene.play(Wiggle(self.robot, rotation_angle=0.06), run_time=0.5)
        return [dijo, adivina]

    def instala(self, scene):
        """La jefa entra y le pone un botón por cada máquina que le deja usar."""
        scene.play(FadeIn(self.jefa, shift=P(-80, 0) - P(0, 0)), run_time=0.5)
        for nombre, boton in self.botones.items():
            destino = boton.get_center()
            boton.move_to(P(JEFA_X - 30, 560)).scale(0.6)
            scene.play(_salta(self.jefa, 10), FadeIn(boton), run_time=0.3)
            scene.play(boton.animate(path_arc=0.8).scale(1 / 0.6).move_to(destino),
                       Indicate(self.maquinas[nombre], color=CIAN, scale_factor=1.03),
                       run_time=0.45)

    def trabaja(self, scene, maquina):
        """La máquina se sacude y se le enciende la luz."""
        x = MAQUINAS[maquina][0]
        luz = punto(x + 48, 645, 6, VERDE)
        scene.play(Wiggle(self.maquinas[maquina], rotation_angle=0.03, n_wiggles=5),
                   FadeIn(luz), run_time=0.7)
        scene.play(FadeOut(luz), run_time=0.2)

    def usa(self, scene, pedido, maquina, devuelve):
        """Escribe el pedido, oprime el botón, la señal corre por el cable y vuelve el dato."""
        papel = _papel(pedido, CIAN).move_to(P(OPERARIO_X, 405))
        scene.play(FadeIn(papel, shift=UP * 0.1), run_time=0.4)
        boton = self.botones[maquina]
        oprime = boton.animate(rate_func=there_and_back).shift(P(0, 5) - P(0, 0))
        senal = punto(570, CABLE_Y, 8, CIAN)
        scene.play(oprime, FadeOut(papel, target_position=boton.get_center(), scale=0.3),
                   _salta(self.robot, 6), run_time=0.45)
        scene.play(FadeIn(senal, scale=0.5), run_time=0.15)
        scene.play(senal.animate.move_to(P(MAQUINAS[maquina][0], CABLE_Y)), run_time=0.6)
        scene.play(FadeOut(senal, scale=2), run_time=0.2)
        self.trabaja(scene, maquina)
        resultado = _papel(devuelve, VERDE).move_to(P(MAQUINAS[maquina][0], 425))
        scene.play(FadeIn(resultado, shift=UP * 0.15), run_time=0.35)
        scene.play(resultado.animate(path_arc=0.7).move_to(P(OPERARIO_X, 330)),
                   run_time=0.7)
        scene.play(Indicate(self.robot, color=CIAN, scale_factor=1.04), run_time=0.35)
        return resultado

    def arreglo(self, scene):
        self.instala(scene)
        for i, (pregunta, pedido, maquina, devuelve, dice) in enumerate(PEDIDOS_TOOLS):
            if i:
                scene.next_slide()
                scene.play(*[FadeOut(m) for m in self.sobras], run_time=0.3)
            dijo = self.pregunta(scene, pregunta)
            resultado = self.usa(scene, pedido, maquina, devuelve)
            self.sobras = [dijo, resultado, self.responde(scene, dice, TEAL)]


def _aparatos():
    fabrica = _Fabrica()
    return fabrica.fijo(), fabrica.falla, fabrica.arreglo


def aparatos(scene):
    """Sin botones el operario solo adivina; con los botones que le das, hace el trabajo."""
    _en_teatro(scene, "2.3", "¿Qué son las tools?",
               "Piensa en un operario que solo usa los botones que le das.", _aparatos)


# MCP: el anillo de acople de una estación espacial. Cada módulo (Catálogo, Agenda, Correo)
# trae una escotilla con su propia forma y cada nave, su propia punta: hay que fabricar un
# adaptador por cada pareja de nave y módulo. Con un mismo anillo para todos, cualquier nave
# se acopla a cualquier módulo y, al acoplarse, el módulo se enciende y le cuenta qué ofrece.
# (módulo, ícono, y, forma de su escotilla)
MODULOS_MCP = (("Catálogo", "casa", 365, "triangulo"),
               ("Agenda", "calendario", 490, "cuadrado"),
               ("Correo", "sobre", 615, "barra"))
# (x donde espera, color, forma de su punta, hacia dónde mira)
NAVES = ((250, CIAN, "redondo", 1), (1190, AZUL, "rombo", -1))
ESTACION_X, MODULO_ANCHO, ESCOTILLA, PUNTA = 720, 80, 26, 102  # PUNTA: del centro a la punta
CARRIL = MODULOS_MCP[1][2]  # la altura a la que esperan las naves
VISITAS = (0, 2, 1)  # el orden en que una nave recorre los módulos: termina en el del medio
OFERTA_Y = (440, 484, 528)  # donde se apila, en el sitio de cada nave, lo que ya sabe usar
AVISO_Y = 258
CIELO, CASCO = "#081721", "#2f5a6e"
APAGADO = {k: "#2f4b58" for k in "Xoswcgmlvr"}
PUNTAS = {"triangulo": ((-1, 1), (1, 1), (0, -1)), "rombo": ((-1, 0), (0, -1), (1, 0), (0, 1))}


def _forma(forma, cx, cy, lado, relleno, borde=None):
    """La forma de una punta o de una escotilla: cada quien trae la suya."""
    if forma in ("redondo", "anillo"):
        f = punto(cx, cy, lado, relleno)
    elif forma in ("cuadrado", "barra"):
        medio = lado if forma == "cuadrado" else lado / 2.5
        f = caja(cx - medio, cy - lado, cx + medio, cy + lado, relleno, radio=2)
    else:
        f = Polygon(*[P(cx + lado * a, cy + lado * b) for a, b in PUNTAS[forma]])
        f.set_fill(relleno, opacity=1)
    return f.set_stroke(borde or relleno, width=G(2.5) if borde else 0)


def _conector(cx, cy, forma, color=None):
    """La punta de una nave o, sin `color`, la escotilla de un módulo (un hueco). El anillo
    estándar es igual en las dos, y va en cian."""
    estandar = forma == "anillo"
    base = caja(cx - 13, cy - 26, cx + 13, cy + 26, METAL_OSCURO, radio=5,
                borde=CIAN if estandar else GRIS_MEDIO, grosor=2)
    if estandar:
        return VGroup(base, _forma(forma, cx, cy, 9, OSCURO, CIAN))
    return VGroup(base, _forma(forma, cx, cy, 9, color or OSCURO, None if color else GRIS_LINEA))


def _escotilla(n, i, forma=None):
    """La escotilla del módulo `i` que mira hacia la nave `n`."""
    x = ESTACION_X - NAVES[n][3] * (MODULO_ANCHO + ESCOTILLA / 2)
    return _conector(x, MODULOS_MCP[i][2], forma or MODULOS_MCP[i][3])


def _muelle(n):
    """La x del centro de la nave `n` cuando su punta toca la escotilla."""
    return ESTACION_X - NAVES[n][3] * (MODULO_ANCHO + ESCOTILLA + PUNTA)


def _modulo(i, encendido=False):
    nombre, dibujo, y, *_ = MODULOS_MCP[i]
    x0, x1 = ESTACION_X - MODULO_ANCHO, ESTACION_X + MODULO_ANCHO
    return VGroup(caja(x0, y - 48, x1, y + 48, LOCOMOTORA, radio=16),
                  caja(x0 + 14, y - 38, x1 - 14, y + 16, CELESTE if encendido else OSCURO,
                       radio=6, borde=CIAN if encendido else GRIS_MEDIO, grosor=1.5),
                  icono_centrado(dibujo, ESTACION_X, y - 11, 4, None if encendido else APAGADO),
                  centrado(nombre, 12, ESTACION_X, y + 38, color=TINTA, peso=NEGRITA))


def _estacion():
    """El eje que une los módulos, con su antena."""
    arriba, abajo = MODULOS_MCP[0][2], MODULOS_MCP[-1][2]
    return VGroup(caja(ESTACION_X - 9, arriba, ESTACION_X + 9, abajo, METAL_OSCURO),
                  linea(ESTACION_X, arriba - 48, ESTACION_X, arriba - 70, GRIS_MEDIO, 3),
                  punto(ESTACION_X, arriba - 72, 5, CIAN))


def _nave(n):
    """Una nave abierta con su robot adentro. La punta es la última pieza: se cambia sola."""
    cx, color, forma, d = NAVES[n]
    cy = CARRIL

    def tramo(a, b, y0, y1, relleno, **kw):
        xa, xb = sorted((cx + a * d, cx + b * d))
        return caja(xa, cy + y0, xb, cy + y1, relleno, **kw)

    def triangulo(puntas, relleno, opacidad=1.0):
        t = Polygon(*[P(cx + a * d, cy + b) for a, b in puntas])
        return t.set_fill(relleno, opacity=opacidad).set_stroke(width=0)

    llama = VGroup(triangulo(((-98, -12), (-98, 12), (-132, 0)), color, 0.55),
                   triangulo(((-98, -6), (-98, 6), (-116, 0)), TINTA))
    aletas = VGroup(*[triangulo(((-84, 14 * s), (-46, 14 * s), (-92, 52 * s)),
                                mezcla(color, OSCURO, 0.35)) for s in (-1, 1)])
    cupula = punto(cx - 6 * d, cy - 44, 66, TINTA, borde=GRIS_LINEA, grosor=1.5)
    cupula.set_fill(TINTA, opacity=0.07)
    return VGroup(llama, tramo(-98, -84, -14, 14, METAL_OSCURO, radio=3), aletas,
                  robot(cx - 6 * d, piso=cy + 22, alto=124, color=color), cupula,
                  tramo(-84, 66, -22, 26, CASCO, radio=13),
                  tramo(-70, 52, 9, 14, color, radio=2),
                  tramo(66, 76, -10, 10, METAL_OSCURO),
                  _conector(cx + (PUNTA - 13) * d, cy, forma, color))


def _adaptador(n, i):
    """La pieza que une la punta de la nave `n` con la escotilla del módulo `i`."""
    _, color, punta, d = NAVES[n]
    y, escotilla = MODULOS_MCP[i][2], MODULOS_MCP[i][3]
    cx = ESTACION_X - d * (MODULO_ANCHO + ESCOTILLA + 30)
    return VGroup(caja(cx - 28, y - 18, cx + 28, y + 18, TARJETA, radio=6, borde=color, grosor=2),
                  _forma(punta, cx - 13 * d, y, 7, color),
                  _forma(escotilla, cx + 13 * d, y, 7, GRIS_LINEA))


def _cielo():
    """El espacio en vez del cuarto: un cielo oscuro con estrellas y un planeta."""
    azar = random.Random(4)
    estrellas = [punto(azar.uniform(X0 + 20, X1 - 20), azar.uniform(TECHO + 16, SALA_PISO + 34),
                       azar.choice((1.2, 1.6, 2.4)), GRIS_LINEA) for _ in range(48)]
    planeta = VGroup(punto(1240, 292, 44, AZUL_SUAVE), punto(1224, 278, 10, CELESTE),
                     punto(1256, 306, 6, CELESTE), punto(1254, 270, 4, CELESTE))
    return VGroup(caja(X0, TECHO, X1, SALA_PISO + 48, CIELO, radio=14, borde=BORDE_SUELO,
                       grosor=1.5), *estrellas, planeta)


def _contador(n, color=ERROR):
    cuenta = "1 adaptador" if n == 1 else f"{n} adaptadores"
    return centrado(cuenta, 24, ESTACION_X, AVISO_Y, color=color, peso=NEGRITA)


class _Acople:
    """Primero, un adaptador por cada pareja de nave y módulo; después, un mismo anillo: las
    naves vuelan de módulo en módulo y cada uno les cuenta qué ofrece."""

    def __init__(self):
        self.naves = [_nave(n) for n in range(len(NAVES))]
        self.donde = [(x, CARRIL) for x, *_ in NAVES]
        self.modulos = [_modulo(i) for i in range(len(MODULOS_MCP))]
        self.escotillas = [[_escotilla(n, i) for i in range(len(MODULOS_MCP))]
                           for n in range(len(NAVES))]
        self.sobras = []

    def fijo(self):
        return [_estacion(), *self.escotillas[0], *self.escotillas[1], *self.modulos,
                self.naves[0]]

    def vuela(self, n, x, y, **kw):
        """La animación que lleva el centro de la nave `n` hasta (x, y)."""
        desde, self.donde[n] = self.donde[n], (x, y)
        return self.naves[n].animate(**kw).shift(P(x, y) - P(*desde))

    def choca(self, scene):
        """La primera nave llega a la Agenda con su punta redonda, no encaja y rebota."""
        scene.play(self.vuela(0, _muelle(0), CARRIL), run_time=0.8)
        golpe = P(ESTACION_X - MODULO_ANCHO - ESCOTILLA, CARRIL)
        scene.play(Flash(golpe, color=ERROR, line_length=0.14, flash_radius=0.3),
                   self.vuela(0, NAVES[0][0], CARRIL), run_time=0.6)
        queja = globo("No encaja", NAVES[0][0], 350, color=ERROR, hacia=NAVES[0][0])
        scene.play(FadeIn(queja, shift=UP * 0.1), Wiggle(self.naves[0], rotation_angle=0.05),
                   run_time=0.6)
        return queja

    def fabrica(self, scene, n, i, total, contador):
        """Un adaptador más para la pareja de la nave `n` y el módulo `i`."""
        pieza = _adaptador(n, i)
        scene.play(FadeIn(pieza, scale=0.4), Transform(contador, _contador(total)),
                   Flash(pieza, color=TINTA, line_length=0.1, flash_radius=0.3), run_time=0.4)
        return pieza

    def falla(self, scene):
        contador = _contador(0)
        maraña = [self.choca(scene), contador]
        scene.play(FadeIn(contador, shift=UP * 0.1), run_time=0.3)
        for n in range(len(NAVES)):
            if n:
                scene.play(FadeIn(self.naves[n], shift=P(-110, 0) - P(0, 0)), run_time=0.6)
            for i in range(len(MODULOS_MCP)):
                maraña.append(self.fabrica(scene, n, i, len(maraña) - 1, contador))
        cuenta = centrado("2 naves por 3 módulos: 6 adaptadores", 24, ESTACION_X, AVISO_Y,
                          color=ERROR, peso=NEGRITA)
        scene.play(Transform(contador, cuenta), run_time=0.5)
        scene.play(*[Wiggle(nave, rotation_angle=0.04) for nave in self.naves], run_time=0.6)
        return maraña

    def estandar(self, scene):
        """Todas las escotillas y todas las puntas pasan a ser el mismo anillo."""
        aviso = _letrero("Un mismo anillo para todos", ESTACION_X, AVISO_Y - 6, color=TEAL,
                         tam=17)
        cambios = [Transform(e, _escotilla(n, i, "anillo"))
                   for n, lado in enumerate(self.escotillas) for i, e in enumerate(lado)]
        for nave in self.naves:
            punta = nave[-1]
            cambios += [Transform(punta, _conector(0, 0, "anillo").move_to(punta)),
                        Flash(punta.get_center(), color=CIAN, line_length=0.12,
                              flash_radius=0.4)]
        scene.play(FadeIn(aviso, shift=UP * 0.1), *cambios, run_time=0.8)
        scene.play(*[_salta(nave, 10) for nave in self.naves], run_time=0.5)
        self.sobras = [aviso]

    def acopla(self, scene, n, k, i):
        """La nave `n` hace su visita número `k`: se acopla al módulo `i`, que se enciende y
        le manda la tarjeta con su nombre."""
        nombre, _, y, *_ = MODULOS_MCP[i]
        d, x = NAVES[n][3], _muelle(n)
        if k:
            scene.play(self.vuela(n, x - 60 * d, self.donde[n][1]), run_time=0.25)
        scene.play(self.vuela(n, x - 60 * d, y, path_arc=-0.3 * d), run_time=0.55)
        scene.play(self.vuela(n, x, y), run_time=0.3)
        papel = _papel(nombre, VERDE).move_to(P(ESTACION_X, y - 10))
        scene.play(Flash(self.escotillas[n][i].get_center(), color=CIAN, line_length=0.12,
                         flash_radius=0.35),
                   Transform(self.modulos[i], _modulo(i, encendido=True)),
                   FadeIn(papel, scale=0.5), run_time=0.45)
        scene.play(papel.animate(path_arc=0.5 * d).move_to(P(NAVES[n][0] - 20 * d, OFERTA_Y[k])),
                   _salta(self.naves[n], 8), run_time=0.6)

    def arreglo(self, scene):
        self.estandar(scene)
        for n in range(len(NAVES)):
            scene.next_slide()
            if self.sobras:
                scene.play(*[FadeOut(m) for m in self.sobras], run_time=0.3)
                self.sobras = []
            for k, i in enumerate(VISITAS):
                self.acopla(scene, n, k, i)
        scene.play(FadeIn(_contador(0, color=VERDE), scale=1.2), run_time=0.4)


def _estacion_espacial():
    acople_ = _Acople()
    return acople_.fijo(), acople_.falla, acople_.arreglo


def acople(scene):
    """Sin estándar, un adaptador por pareja; con un mismo anillo, cualquier nave se acopla a
    cualquier módulo. Termina en la escena."""
    _en_teatro(scene, "3.1", "¿Qué es MCP?",
               "Piensa en el anillo de acople de una estación espacial.", _estacion_espacial,
               bloque="interacciones", sala=_cielo)


# --- Bloque 3: el agente y su entorno -------------------------------------------------------
# (MCP no es analogía: está en mcp.py.)


def _plano(cx, cy):
    return VGroup(caja(cx - 32, cy - 26, cx + 32, cy + 26, AZUL_SUAVE, radio=3, borde=AZUL,
                       grosor=1.6),
                  linea(cx - 4, cy - 26, cx - 4, cy + 4, AZUL, 1.6),
                  linea(cx - 32, cy + 4, cx + 12, cy + 4, AZUL, 1.6))


# Multimodal: una oficina que solo recibía cartas por una ranura. El plano no cabe, así que el
# cliente lo dicta con palabras y el practicante, de oído, dibuja otro plano. Cuando la ranura
# se abre en ventanilla, el plano, el contrato, la nota de voz y la pregunta pasan juntos en
# una sola bandeja, y cada pieza lleva su tipo.
MURO_X, RANURA, VENTANILLA = 620, (456, 496), (380, 572)
BANDEJA_Y = 476
ENTREGA = (420, 860)  # el centro de la bandeja: del lado del cliente y del lado del robot
CLIENTE_X, PRACTICANTE_X = 170, 1170
PIEZAS_X = (-120, -40, 40, 120)
BLOQUES = ("imagen", "PDF", "audio", "texto")
DICTADO = ("sala al norte", "alcoba de 3 por 4", "baño junto a la cocina")
ONDA = (8, 18, 12, 26, 14, 20, 8)


def _muro(hueco):
    """La pared que separa al cliente del practicante, con su hueco: ranura o ventanilla."""
    y0, y1 = hueco
    return VGroup(caja(MURO_X - 14, TECHO, MURO_X + 14, y0, BORDE_SUELO),
                  caja(MURO_X - 14, y1, MURO_X + 14, SALA_PISO, BORDE_SUELO))


def _audio(cx, cy):
    """Una nota de voz: la onda del sonido."""
    return VGroup(caja(cx - 32, cy - 22, cx + 32, cy + 22, LILA_SUAVE, radio=6, borde=LILA,
                       grosor=1.6),
                  *[caja(cx - 26 + 8 * i, cy - h / 2, cx - 22 + 8 * i, cy + h / 2, LILA, radio=2)
                    for i, h in enumerate(ONDA)])


def _piezas(cx):
    """El plano, el contrato, la nota de voz y la pregunta, en el orden de BLOQUES."""
    x = [cx + d for d in PIEZAS_X]
    return [_plano(x[0], BANDEJA_Y),
            hoja(x[1], BANDEJA_Y, 44, 56, lineas=4, relleno=ORO_SUAVE, borde=ORO),
            _audio(x[2], BANDEJA_Y), hoja(x[3], BANDEJA_Y, 34, 42, lineas=2)]


def _garabato(cx, cy):
    """Lo que el practicante dibuja de oído: un plano torcido, que no es el del cliente."""
    tablero = caja(cx - 80, cy - 66, cx + 80, cy + 66, TARJETA, radio=8, borde=GRIS_MEDIO,
                   grosor=1.5)
    borde = Polygon(*[P(cx + a, cy + b) for a, b in ((-52, -34), (40, -46), (56, 30), (-44, 42))])
    borde.set_fill(opacity=0).set_stroke(ERROR, width=G(2.2))
    return tablero, [borde, linea(cx - 10, cy - 40, cx + 8, cy + 36, ERROR, 2.2),
                     linea(cx + 4, cy + 2, cx + 52, cy - 12, ERROR, 2.2)]


class _Ventanilla:
    def __init__(self):
        self.cliente = persona(CLIENTE_X, AZUL, piso=SALA_PISO, e=1.15)
        self.robot = robot(PRACTICANTE_X, piso=SALA_PISO, alto=176 * 1.2)
        self.muro = _muro(RANURA)

    def fijo(self):
        return [self.cliente, self.robot, *self.muro]

    def rebota(self, scene):
        """El plano va hacia la ranura, no cabe y vuelve a la mano del cliente."""
        plano = _plano(330, BANDEJA_Y)
        dijo = _dice(scene, "Mire el plano", 250, 420, hacia=CLIENTE_X)
        _entra(scene, plano)
        scene.play(llevar(plano, MURO_X - 50, BANDEJA_Y), run_time=0.5)
        aviso = _letrero("Por la ranura solo pasan palabras", MURO_X, 262, color=ERROR, tam=17)
        scene.play(Flash(P(MURO_X - 14, BANDEJA_Y), color=ERROR, line_length=0.14,
                         flash_radius=0.3), llevar(plano, 330, 572, arco=-0.4),
                   FadeIn(aviso, shift=UP * 0.1), FadeOut(dijo), run_time=0.6)
        return plano, aviso

    def dicta(self, scene, frase, trazo):
        """Una frase pasa por la ranura y el practicante dibuja lo que entendió."""
        palabra = _letrero(frase, 370, BANDEJA_Y, tam=13)
        scene.play(FadeIn(palabra, shift=UP * 0.1), _salta(self.cliente, 8), run_time=0.3)
        scene.play(llevar(palabra, MURO_X + 60, BANDEJA_Y), run_time=0.6)
        scene.play(FadeOut(palabra, target_position=trazo.get_center(), scale=0.3),
                   Create(trazo), run_time=0.5)

    def falla(self, scene):
        plano, aviso = self.rebota(scene)
        tablero, trazos = _garabato(ENTREGA[1], BANDEJA_Y)
        scene.play(FadeIn(tablero, shift=UP * 0.1), run_time=0.3)
        for frase, trazo in zip(DICTADO, trazos):
            self.dicta(scene, frase, trazo)
        duda = _dice(scene, "¿Así?", PRACTICANTE_X, 405, ERROR, hacia=PRACTICANTE_X)
        equis = sello(ENTREGA[1] + 74, BANDEJA_Y - 62, bien=False)
        scene.play(FadeIn(equis, scale=0.4), Wiggle(self.robot, rotation_angle=0.05),
                   Wiggle(plano, rotation_angle=0.08), run_time=0.6)
        return [plano, aviso, tablero, *trazos, duda, equis]

    def abre(self, scene):
        """La ranura se abre en ventanilla y el cliente arma una sola bandeja con todo."""
        x = ENTREGA[0]
        aviso = _letrero("Ahora cabe todo", MURO_X, 262, color=TEAL, tam=17)
        scene.play(*[Transform(a, b) for a, b in zip(self.muro, _muro(VENTANILLA))],
                   FadeIn(aviso, shift=UP * 0.1), run_time=0.7)
        self.bandeja = caja(x - 170, BANDEJA_Y - 58, x + 170, BANDEJA_Y + 58, TARJETA, radio=12,
                            borde=CIAN, grosor=2)
        self.piezas = _piezas(x)
        scene.play(FadeIn(self.bandeja, shift=UP * 0.1), run_time=0.3)
        scene.play(LaggedStart(*[FadeIn(p, shift=P(0, 30) - P(0, 0)) for p in self.piezas],
                               lag_ratio=0.3), _salta(self.cliente, 10), run_time=1.0)
        return [aviso, _dice(scene, "¿Cabe una cama doble?", 285, 385, hacia=CLIENTE_X)]

    def entrega(self, scene, sobras):
        """La bandeja cruza la ventanilla; el practicante mira cada pieza y responde."""
        paquete = VGroup(self.bandeja, *self.piezas)
        scene.play(*[FadeOut(m) for m in sobras], run_time=0.3)
        scene.play(paquete.animate.shift(P(ENTREGA[1] - ENTREGA[0], 0) - P(0, 0)), run_time=1.0)
        for pieza, tipo, dx in zip(self.piezas, BLOQUES, PIEZAS_X):
            nombre = etiqueta(tipo, ENTREGA[1] + dx, BANDEJA_Y + 78, color=TEAL,
                              relleno=CIAN_SUAVE)
            scene.play(pieza.animate(rate_func=there_and_back).scale(1.25),
                       FadeIn(nombre, shift=UP * 0.08), run_time=0.4)
        _dice(scene, "Sí cabe: la alcoba mide 3 por 4", 1160, 385, TEAL, hacia=PRACTICANTE_X)
        scene.play(_salta(self.robot, 12), run_time=0.4)

    def arreglo(self, scene):
        sobras = self.abre(scene)
        scene.next_slide()
        self.entrega(scene, sobras)


def _ventanilla():
    oficina = _Ventanilla()
    return oficina.fijo(), oficina.falla, oficina.arreglo


def multimodal(scene):
    """Por la ranura solo pasaban palabras y el plano se perdía al dictarlo; por la ventanilla
    pasa todo junto, en una bandeja. Va sin frases ni rótulos abajo (pedido así): termina en
    la escena."""
    _en_teatro(scene, "3.2", "¿Qué es multimodal?",
               "Piensa en una oficina que solo recibía cartas por una ranura.", _ventanilla,
               bloque="interacciones")


# --- Bloque 3: grafos -----------------------------------------------------------------------
# (¿Workflow o agente? está en workflow_o_agente.py.)

# LangChain y LangGraph: el mapa de un videojuego. Con LangChain el camino es una cadena, solo
# va hacia adelante: si la búsqueda trae una sola casa, el robot no se puede devolver. Con
# LangGraph es un mapa: una señal que manda por un desvío mientras falten casas, dos carriles
# que se recorren a la vez, banderas donde se guarda la partida y una barrera que solo abre
# una persona. Lo que consigue en cada parada va a la mochila (el estado). Al final el mapa
# entero se encoge: es una parada de un mapa más grande.
CAMINO, INICIO_X, ANDA = 530, 170, 112  # la altura del camino, la salida y el alto del robot
PARADAS = {"Interpretar": (290, CAMINO), "Buscar": (460, CAMINO), "Ampliar": (460, 350),
           "Cuota": (800, 465), "Agenda": (800, 595), "Resumir": (990, CAMINO),
           "Enviar": (1230, CAMINO)}
CADENA = ("Interpretar", "Buscar", "Resumir", "Enviar")
SENAL, PARTIDA, JUNTA, BARRERA_X = (610, CAMINO), (700, CAMINO), (900, CAMINO), 1110
DESVIO = ((610, CAMINO - 20), (610, 350), (460, 350), (460, CAMINO - 27))
# Por dónde va cada mitad del robot cuando se parte en dos.
CARRILES = [(PARTIDA, (740, PARADAS[n][1]), PARADAS[n], (860, PARADAS[n][1]), JUNTA)
            for n in ("Cuota", "Agenda")]
BANDERAS = (PARADAS["Interpretar"], PARADAS["Buscar"], JUNTA)
RANURA_X, RANURA_Y, RANURA_PASO = 965, 262, 54
# Lo que cabe en la mochila, en orden: el pedido, tres casas, la cuota, la agenda y el resumen.
EN_MOCHILA = ("pedido", "casa", "casa", "casa", "calculadora", "calendario", "resumen")
TERRENO, VIA = "#0d2731", "#2f5a6e"
MUNDO = (("Buscador", 312), ("Crédito", 720), ("Contratos", 1128))
MUNDO_Y, ISLA_ANCHO, ISLA_ALTO = 522, 192, 112


def _terreno():
    """El suelo del mapa en vez del cuarto, con unas matas."""
    azar = random.Random(7)
    matas = [punto(azar.uniform(X0 + 20, X1 - 20), azar.uniform(TECHO + 16, SALA_PISO + 34),
                   azar.choice((3, 4, 6)), VERDE_SUAVE) for _ in range(40)]
    return VGroup(caja(X0, TECHO, X1, SALA_PISO + 48, TERRENO, radio=14, borde=BORDE_SUELO,
                       grosor=1.5), *matas)


def _via(*puntos, grosor=14):
    """Un camino que pasa por los `puntos`."""
    via = VMobject().set_points_as_corners([P(x, y) for x, y in puntos])
    via.set_stroke(VIA, width=G(grosor)).set_fill(opacity=0)
    via.set_cap_style(CapStyleType.ROUND)
    return via


def _sentido(a, b):
    """Una punta en la mitad del tramo de `a` a `b`: el camino tiene un solo sentido."""
    (x0, y0), (x1, y1) = a, b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    punta = Polygon(P(cx - 5, cy - 6), P(cx - 5, cy + 6), P(cx + 6, cy))
    punta.set_fill(GRIS_LINEA, opacity=1).set_stroke(width=0)
    return punta.rotate(math.atan2(y0 - y1, x1 - x0), about_point=P(cx, cy))


def _parada(nombre):
    x, y = PARADAS[nombre]
    return VGroup(punto(x, y, 25, LOCOMOTORA, borde=CIAN, grosor=2.5),
                  centrado(nombre, 14, x, y + 50, color=TINTA, peso=NEGRITA))


def _senal(color=TINTA):
    """La señal del cruce: mira la mochila y decide por dónde se sigue."""
    x, y = SENAL
    return VGroup(_forma("rombo", x, y, 17, color),
                  centrado("¿hay 3?", 13, x, y + 44, color=GRIS))


def _bandera(x, y):
    tela = Polygon(P(x + 38, y - 60), P(x + 62, y - 51), P(x + 38, y - 42))
    return VGroup(linea(x + 38, y - 8, x + 38, y - 60, GRIS_LINEA, 2.5),
                  tela.set_fill(VERDE, opacity=1).set_stroke(width=0))


def _mochila():
    """El tablero de arriba, como el inventario de un juego: una ranura por cosa."""
    x0, x1 = RANURA_X - 35, RANURA_X + 6 * RANURA_PASO + 35
    ranuras = [caja(x - 23, RANURA_Y - 23, x + 23, RANURA_Y + 23, OSCURO, radio=7,
                    borde=GRIS_MEDIO, grosor=1.5)
               for x in (RANURA_X + RANURA_PASO * i for i in range(len(EN_MOCHILA)))]
    return VGroup(caja(x0, RANURA_Y - 34, x1, RANURA_Y + 34, TARJETA, radio=12, borde=GRIS_MEDIO,
                       grosor=1.5), *ranuras)


def _cosa(i):
    """Lo que va en la ranura `i` de la mochila."""
    x, que = RANURA_X + RANURA_PASO * i, EN_MOCHILA[i]
    if que == "pedido":
        return hoja(x, RANURA_Y, 26, 32)
    if que == "resumen":
        return hoja(x, RANURA_Y, 26, 32, color=VERDE, relleno=VERDE_SUAVE, borde=VERDE)
    return icono_centrado(que, x, RANURA_Y, 3)


def _cartel(contenido, color):
    """El nombre del mapa, pegado a la izquierda del terreno."""
    letrero = _letrero(contenido, 250, 250, color=color, tam=16)
    return letrero.shift((P(140, 0)[0] - letrero.get_left()[0], 0, 0))


def _aviso(x, y, bien):
    """Un visto bueno verde o una equis roja sobre quien está en (x, y)."""
    return VGroup(punto(x, y, 15, VERDE if bien else ERROR), marca(x, y, 15, OSCURO, bien))


# Los otros dos mapas, vistos de lejos: (caminos, paradas, cruces), relativos al centro de la isla.
# Crédito reparte entre tres paradas y vuelve a decidir por arriba; Contratos reparte entre tres
# a la vez, revisa y, si no pasa, vuelve por abajo.
MAPITAS = (
    ((((-150, 0), (150, 0)), ((-25, -62), (-25, 62)),
      ((-25, -62), (55, -62), (55, 62), (-25, 62)), ((95, 0), (95, -92), (-70, -92), (-70, 0)),
      ((95, 0), (95, 62), (150, 62))),
     ((-120, 0), (15, -62), (15, 0), (15, 62), (150, 0), (150, 62)),
     ((-70, 0), (95, 0))),
    ((((-150, 0), (150, 0)), ((-30, -66), (-30, 66)),
      ((-30, -66), (90, -66), (90, 66), (-30, 66)), ((120, 0), (120, 94), (-90, 94), (-90, 0)),
      ((-90, 0), (-90, -94), (40, -94))),
     ((30, -66), (30, 0), (30, 66), (150, 0), (40, -94)),
     ((-90, 0), (120, 0))),
)


def _mapita(cx, cual):
    """Otro mapa visto de lejos, más enredado que el primero: paradas, cruces, vueltas y su
    robot."""
    y = MUNDO_Y
    caminos, paradas, cruces = MAPITAS[cual]
    vias = [_via(*[(cx + dx, y + dy) for dx, dy in c], grosor=4) for c in caminos]
    nodos = [punto(cx + dx, y + dy, 9, LOCOMOTORA, borde=CIAN, grosor=1.5) for dx, dy in paradas]
    rombos = [_forma("rombo", cx + dx, y + dy, 10, TINTA) for dx, dy in cruces]
    return VGroup(*vias, *nodos, *rombos, robot(cx - 160, piso=y + 26, alto=46))


def _isla(cx):
    """El marco de un mapa visto de lejos."""
    return caja(cx - ISLA_ANCHO, MUNDO_Y - ISLA_ALTO, cx + ISLA_ANCHO, MUNDO_Y + ISLA_ALTO,
                TARJETA, radio=14, borde=CIAN, grosor=2, opacidad=0)


class _Mapa:
    """El robot recorre el mapa y guarda en la mochila lo que consigue en cada parada."""

    def __init__(self):
        self.robot = robot(INICIO_X, piso=CAMINO + 8, alto=ANDA)
        self.donde = (INICIO_X, CAMINO)
        self.cartel = _cartel("LangChain", TINTA)
        fin = PARADAS["Enviar"]
        self.medio = _via(PARTIDA, JUNTA)
        self.sentidos = [_sentido((x - 10, CAMINO), (x + 10, CAMINO))
                         for x in (230, 375, 535, 655, 945, 1170)]
        self.paradas = {n: _parada(n) for n in PARADAS}
        self.mochila = _mochila()
        self.senal = _senal()
        self.cosas, self.banderas = {}, []
        # Todo lo que queda en el mapa, para encogerlo al final.
        self.todo = [_via((INICIO_X - 40, CAMINO), PARTIDA), self.medio, _via(JUNTA, fin),
                     *self.sentidos, *[self.paradas[n] for n in CADENA], self.cartel,
                     self.mochila]

    def fijo(self):
        return [*self.todo, self.robot]

    # --- Cómo se mueve ---

    def va(self, x, y, **kw):
        desde, self.donde = self.donde, (x, y)
        return self.robot.animate(**kw).shift(P(x, y) - P(*desde))

    def anda(self, scene, *puntos):
        """Camina de punto en punto y da un saltito al llegar."""
        for x, y in puntos:
            largo = abs(x - self.donde[0]) + abs(y - self.donde[1])
            scene.play(self.va(x, y), run_time=max(0.25, largo * 0.0022))
        scene.play(_salta(self.robot, 10), run_time=0.25)

    def pone(self, scene, *mobs, run_time=0.6):
        """Agrega piezas al mapa; el robot queda encima."""
        scene.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in mobs], lag_ratio=0.2),
                   run_time=run_time)
        scene.add(self.robot)
        self.todo += mobs

    def guarda(self, scene, *ranuras, desde=None):
        """Lo que consigue en una parada vuela a su ranura de la mochila."""
        nuevas = [_cosa(i) for i in ranuras]
        destinos = [c.get_center() for c in nuevas]
        x, y = self.donde
        for c, (cx, cy) in zip(nuevas, desde or [(x, y - ANDA - 22)] * len(nuevas)):
            c.move_to(P(cx, cy)).scale(0.7)
        scene.play(*[FadeIn(c, scale=0.5) for c in nuevas], run_time=0.25)
        scene.play(*[c.animate(path_arc=-0.6).scale(1 / 0.7).move_to(d)
                     for c, d in zip(nuevas, destinos)], run_time=0.5)
        self.cosas.update(zip(ranuras, nuevas))

    def reaparece(self, scene, punto_, *otras, **kw):
        """El robot, que no está a la vista, vuelve a salir en otro punto."""
        self.robot.shift(P(*punto_) - P(*self.donde))
        self.donde = punto_
        scene.play(FadeIn(self.robot, **kw), *otras, run_time=0.4)

    # --- LangChain: la cadena ---

    def falla(self, scene):
        """Encuentra una sola casa, quiere devolverse y el camino no lo deja."""
        self.anda(scene, PARADAS["Interpretar"])
        self.guarda(scene, 0)
        self.anda(scene, PARADAS["Buscar"])
        self.guarda(scene, 1)
        scene.play(*[Indicate(r, color=ERROR, scale_factor=1.12) for r in self.mochila[3:5]],
                   run_time=0.6)
        scene.play(self.robot.animate(rate_func=there_and_back).shift(P(-45, 0) - P(0, 0)),
                   Indicate(self.sentidos[1], color=ERROR, scale_factor=2), run_time=0.7)
        scene.play(Wiggle(self.robot, rotation_angle=0.05), run_time=0.4)
        self.anda(scene, PARADAS["Resumir"])
        self.guarda(scene, 6)
        self.anda(scene, PARADAS["Enviar"])
        queja = globo("Solo encontré 1", 1190, 372, color=ERROR, hacia=1230)
        scene.play(FadeIn(queja, shift=UP * 0.1), Wiggle(self.robot, rotation_angle=0.06),
                   run_time=0.7)
        return [queja]

    # --- LangGraph: el mapa ---

    def reinicia(self, scene):
        """De vuelta a la salida, con la mochila vacía; el cartel cambia de nombre."""
        scene.play(*[FadeOut(c) for c in self.cosas.values()], FadeOut(self.robot, scale=0.6),
                   run_time=0.3)
        self.cosas = {}
        self.reaparece(scene, (INICIO_X, CAMINO),
                       Transform(self.cartel, _cartel("LangGraph", CIAN)), scale=0.6)

    def abre_desvio(self, scene):
        marcas = [_sentido((610, 450), (610, 430)), _sentido((545, 350), (525, 350)),
                  _sentido((460, 420), (460, 440))]
        self.pone(scene, _via(*DESVIO), *marcas, self.paradas["Ampliar"], self.senal)

    def vuelta(self, scene):
        """Busca, la señal ve que faltan casas, toma el desvío, amplía y vuelve a buscar."""
        antes = (SENAL[0] - 45, CAMINO)
        self.anda(scene, PARADAS["Interpretar"])
        self.guarda(scene, 0)
        self.anda(scene, PARADAS["Buscar"])
        self.guarda(scene, 1)
        self.anda(scene, antes)
        scene.play(Transform(self.senal, _senal(ERROR)), run_time=0.3)
        self.anda(scene, SENAL, DESVIO[1], PARADAS["Ampliar"])
        self.anda(scene, PARADAS["Buscar"])
        self.guarda(scene, 2, 3)
        self.anda(scene, antes)
        scene.play(Transform(self.senal, _senal(VERDE)), run_time=0.3)
        self.anda(scene, PARTIDA)

    def abre_carriles(self, scene):
        scene.play(FadeOut(self.medio), run_time=0.3)
        self.todo.remove(self.medio)
        self.pone(scene, *[_via(*carril) for carril in CARRILES], self.paradas["Cuota"],
                  self.paradas["Agenda"])

    def en_paralelo(self, scene):
        """Se parte en dos, cada mitad va por su carril al mismo tiempo y se juntan al final."""
        mitades = [robot(PARTIDA[0], piso=CAMINO + 6, alto=74) for _ in CARRILES]

        def avanzan(tramos):
            for k in tramos:
                scene.play(*[m.animate.shift(P(*carril[k + 1]) - P(*carril[k]))
                             for m, carril in zip(mitades, CARRILES)], run_time=0.35)

        scene.play(FadeOut(self.robot, scale=0.6), *[FadeIn(m, scale=1.4) for m in mitades],
                   run_time=0.35)
        avanzan((0, 1))
        scene.play(*[_salta(m, 8) for m in mitades], run_time=0.25)
        self.guarda(scene, 4, 5, desde=[(c[2][0], c[2][1] - 95) for c in CARRILES])
        avanzan((2, 3))
        self.reaparece(scene, JUNTA, *[FadeOut(m, scale=1.4) for m in mitades], scale=0.6)
        scene.play(_salta(self.robot, 10), run_time=0.25)

    def guarda_partida(self, scene):
        self.banderas = [_bandera(x, y) for x, y in BANDERAS]
        scene.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in self.banderas],
                               lag_ratio=0.3), run_time=0.8)
        self.todo += self.banderas

    def se_cae(self, scene):
        """Falla al resumir y no vuelve a la salida: reaparece en la última bandera, con la
        mochila llena."""
        x, y = PARADAS["Resumir"]
        self.anda(scene, (x, y))
        equis = _aviso(x, y - ANDA - 24, bien=False)
        scene.play(FadeIn(equis, scale=0.4), Wiggle(self.robot, rotation_angle=0.08),
                   run_time=0.6)
        scene.play(FadeOut(self.robot, shift=DOWN * 0.5), FadeOut(equis), run_time=0.45)
        self.reaparece(scene, JUNTA,
                       Flash(self.banderas[-1][1], color=VERDE, line_length=0.14,
                             flash_radius=0.4),
                       *[Indicate(c, color=VERDE, scale_factor=1.15)
                         for c in self.cosas.values()], shift=DOWN * 0.4)
        self.anda(scene, (x, y))
        self.guarda(scene, 6)

    def pide_permiso(self, scene):
        """Antes de enviar hay una barrera: solo la abre una persona."""
        eje = (BARRERA_X, CAMINO + 34)
        barra = caja(BARRERA_X - 5, CAMINO - 34, BARRERA_X + 5, CAMINO + 34, ERROR, radio=5)
        guardia = persona(BARRERA_X + 20, AZUL, piso=CAMINO - 20, e=0.7)
        self.pone(scene, guardia, barra, punto(*eje, 8, GRIS_MEDIO))
        self.anda(scene, (BARRERA_X - 55, CAMINO))
        pide = globo("¿Lo envío?", 1040, 388, hacia=1055)
        scene.play(FadeIn(pide, shift=UP * 0.1), _salta(self.robot, 10), run_time=0.5)
        si = globo("Sí, envíalo", 1195, 350, color=TEAL, hacia=1150)
        scene.play(FadeIn(si, shift=UP * 0.1), _salta(guardia, 12), run_time=0.5)
        scene.play(Rotate(barra, -PI / 2, about_point=P(*eje)), run_time=0.5)
        scene.play(barra.animate.set_fill(VERDE), FadeOut(pide), FadeOut(si), run_time=0.3)
        self.envia(scene)

    def envia(self, scene):
        x, y = PARADAS["Enviar"]
        self.anda(scene, (x, y))
        sobre = icono_centrado("sobre", x, y - ANDA - 26, 3)
        scene.play(FadeIn(sobre, scale=0.5), run_time=0.25)
        scene.play(FadeOut(sobre, shift=P(50, -80) - P(0, 0)), run_time=0.5)
        hecho = _aviso(x, y - ANDA - 26, bien=True)
        scene.play(FadeIn(hecho, scale=0.4), Flash(hecho, color=VERDE, line_length=0.12,
                                                   flash_radius=0.3), run_time=0.45)
        self.todo.append(hecho)

    def mundo(self, scene):
        """El mapa entero se encoge: es una parada más de un mapa más grande."""
        mapa = VGroup(*self.todo, *self.cosas.values(), self.robot)
        islas = [_isla(x) for _, x in MUNDO]
        scene.play(mapa.animate.scale(0.3, scale_stroke=True).move_to(P(MUNDO[0][1], MUNDO_Y)),
                   run_time=1.0)
        scene.play(FadeIn(islas[0]), run_time=0.3)
        arriba = MUNDO_Y - ISLA_ALTO
        y = arriba - 40
        vias = VGroup(_via((MUNDO[0][1], arriba), (MUNDO[0][1], y), (MUNDO[2][1], y),
                           (MUNDO[2][1], arriba), grosor=8),
                      _via((720, y - 20), (720, arriba), grosor=8))
        jefe = robot(720, piso=y - 12, alto=110)
        otras = [VGroup(isla, _mapita(x, i))
                 for i, (isla, (_, x)) in enumerate(zip(islas[1:], MUNDO[1:]))]
        scene.play(LaggedStart(*[FadeIn(m, shift=UP * 0.12) for m in (vias, jefe, *otras)],
                               lag_ratio=0.25), run_time=1.2)
        scene.play(_salta(jefe, 12), run_time=0.5)

    def arreglo(self, scene):
        pasos = ((self.reinicia, self.abre_desvio, self.vuelta),
                 (self.abre_carriles, self.en_paralelo), (self.guarda_partida, self.se_cae),
                 (self.pide_permiso,), (self.mundo,))
        for i, paso in enumerate(pasos):
            if i:
                scene.next_slide()
            for parte in paso:
                parte(scene)


def _mapa():
    mapa = _Mapa()
    return mapa.fijo(), mapa.falla, mapa.arreglo


def grafo(scene):
    """Con LangChain el camino solo va hacia adelante; con LangGraph es un mapa con desvíos,
    carriles, banderas y una barrera, y un mapa entero cabe en una parada de otro."""
    _en_teatro(scene, "3.4", "¿Qué agrega LangGraph?", "Piensa en el mapa de un videojuego.",
               _mapa, bloque="interacciones", sala=_terreno)


# --- Bloque 4: patrones ----------------------------------------------------------------------


PUESTOS = (("Sacar los datos", 300, "analista"), ("Redactar", 720, "redactor"),
           ("Pulir", 1140, "discriminador"))


# --- Bloque 4: orquestador ----------------------------------------------------------------------------


# --- Bloque 4: guardrails --------------------------------------------------------------------------


# --- Fuera del mazo: sus llamadas están comentadas en main.py -------------------------------


