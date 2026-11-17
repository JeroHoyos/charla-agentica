"""El caso del taller: la Inmobiliaria Señor Gato, de Medellín. Solo el problema, en 3D: de
noche el asesor se va y los clientes siguen escribiendo; cada pregunta es un trabajo distinto
que se hace a mano; al otro día todo le cae a un asesor y los clientes se van. Termina en
«Pasando al código», sin decir qué se construye ni con qué (eso lo cuenta quien dicta)."""

from manim import LEFT, RIGHT, UP, FadeIn, FadeOut, LaggedStart, Polygon, VGroup

from comun.animaciones import contar, latido, teclear
from comun.componentes import caja, chip, icono_centrado, punto, titulo
from comun.escena import (
    BORDE_SUELO,
    PARED,
    SUELO,
    TECHO,
    X0,
    X1,
    escritorio,
    globo,
    persona,
)
from comun.estilo import AZUL, CIAN, CORAL, GRIS_LINEA, GRIS_MEDIO, LILA, ORO, OSCURO, VERDE, P
from comun.tres_d import (
    BLANCO,
    CUERO,
    PANTALLA,
    ROJO,
    VIDRIO,
    figura,
    girar,
    partes_computador,
    partes_persona,
)
from diapositivas.practica import pasando

PISO = 665                   # más abajo que en las otras: esta va sin frase debajo
CX_MESA = 1060
ALTO_MESA = 56
MESA = PISO - ALTO_MESA      # la tapa del escritorio
NOCHE, DIA = "#0a1820", "#1f5a78"
E_CLIENTE, E_ASESOR = 1.12, 1.25

# Cada cliente: dónde se para, su ropa y lo que pregunta.
CLIENTES = (
    (200, LILA, "¿Aceptan gatos?"),
    (395, AZUL, "¿3 alcobas en Laureles?"),
    (590, VERDE, "¿Cuánto queda la cuota?"),
    (785, "#f2a0c0", "¿Puedo verlo el domingo?"),
)
CABEZA = PISO - 179 * E_CLIENTE   # dónde acaba la cabeza de un cliente


# --- Los cuatro trabajos, en cajas ----------------------------------------------------------


def _pdf():
    """Una pila de hojas mal puestas."""
    hojas = zip((BLANCO, "#cfdbe0", BLANCO, CORAL), (0.0, 0.25, -0.15, 0.1))
    return tuple(((0, 0.04 + 0.09 * i, 0), (0.42, 0.035, 0.56), color,
                  lambda v, a=a: girar(v, a)) for i, (color, a) in enumerate(hojas))


def _lupa():
    return (((0, 0.62, 0), (0.34, 0.34, 0.04), GRIS_MEDIO, None),
            ((0, 0.62, 0.045), (0.26, 0.26, 0.004), VIDRIO, None, 1),
            ((0, 0.14, 0), (0.06, 0.14, 0.04), CUERO, None))


def _teclas(filas, columnas, x0, y0, rara, color, z):
    """Una rejilla de cuadritos sobre el frente de una caja; `rara` va en coral."""
    return tuple(((x0 + 0.2 * c, y0 - 0.2 * f, z), (0.07, 0.06, 0.004),
                  CORAL if (f, c) == rara else color, None, 1)
                 for f in range(filas) for c in range(columnas))


def _calculadora():
    return (((0, 0.5, 0), (0.36, 0.5, 0.07), GRIS_MEDIO, None),
            ((0, 0.82, 0.075), (0.28, 0.1, 0.004), PANTALLA, None, 1),
            *_teclas(3, 3, -0.2, 0.56, (2, 2), BLANCO, 0.075))


def _calendario():
    return (((0, 0.45, 0), (0.5, 0.45, 0.05), BLANCO, None),
            ((0, 0.82, 0.055), (0.5, 0.09, 0.004), ROJO, None, 1),
            *_teclas(3, 4, -0.3, 0.58, (1, 2), GRIS_MEDIO, 0.055))


TRABAJOS = (_pdf, _lupa, _calculadora, _calendario)


# --- La oficina -----------------------------------------------------------------------------


def _sala():
    """El cuarto de las analogías, con el suelo más abajo."""
    pared = caja(X0, TECHO, X1, PISO, PARED, radio=14)
    suelo = Polygon(P(X0, PISO), P(X1, PISO), P(X1 + 22, PISO + 50), P(X0 - 22, PISO + 50))
    suelo.set_fill(SUELO, opacity=1).set_stroke(width=0)
    return VGroup(pared, suelo, caja(X0, PISO - 1.5, X1, PISO + 1.5, BORDE_SUELO))


def _ventana():
    """La ventana con el sol; el mordisco lo vuelve luna."""
    vidrio = caja(1200, 236, 1300, 326, DIA, radio=8, borde=GRIS_LINEA, grosor=1.4)
    return vidrio, punto(1250, 281, 18, ORO), punto(1259, 274, 15, NOCHE)


def _pendientes(n):
    return chip(f"{int(n)} sin responder", CX_MESA, MESA - 100, color=OSCURO, relleno=CORAL,
                tam=15, alinear=UP * 0)


def _globos():
    """Lo que pregunta cada cliente, a dos alturas para que no se pisen."""
    return [globo(pregunta, cx, CABEZA - (100 if i % 2 == 0 else 40), tam=17, hacia=cx)
            for i, (cx, _, pregunta) in enumerate(CLIENTES)]


def _trabajos():
    """Sobre cada cliente, el trabajo que trae su pregunta."""
    return [figura(partes(), cx, CABEZA - 30, 100, 0.4)
            for partes, (cx, *_) in zip(TRABAJOS, CLIENTES)]


def _de_noche(scene, asesor, vidrio, mordisco, clientes):
    """El asesor se va, cae la noche y los clientes siguen llegando con sus preguntas."""
    scene.play(asesor.animate.shift(RIGHT * 0.8).set_opacity(0), run_time=0.8)
    scene.play(vidrio.animate.set_fill(NOCHE), FadeIn(mordisco), run_time=0.6)
    contador, cuenta = contar(_pendientes, 0, 47, run_time=2.6)
    globos = _globos()
    scene.play(FadeIn(contador, scale=0.8), run_time=0.3)
    scene.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.4) for c in clientes], lag_ratio=0.4),
               LaggedStart(*[FadeIn(g, shift=UP * 0.12) for g in globos], lag_ratio=0.4),
               cuenta, run_time=2.6)
    return contador, globos


def _al_otro_dia(scene, asesor, vidrio, mordisco, portatil, contador, figuras):
    """Amanece, vuelve el asesor y los cuatro trabajos le caen encima."""
    scene.play(vidrio.animate.set_fill(DIA), FadeOut(mordisco),
               asesor.animate.shift(LEFT * 0.8).set_opacity(1), FadeOut(portatil),
               contador.animate.move_to(P(1250, 375)), run_time=0.8)
    scene.play(LaggedStart(*[f.animate(path_arc=-0.7).scale(0.6).move_to(P(968 + 61 * i,
                                                                            MESA - 32))
                             for i, f in enumerate(figuras)], lag_ratio=0.25), run_time=1.8)
    scene.play(latido(contador, 1.2))


def construir(scene):
    scene.marco.ir("proyecto", "5.1")
    cabecera = titulo("Inmobiliaria Señor Gato")
    sala = _sala()
    vidrio, sol, mordisco = _ventana()
    gato = icono_centrado("gato", CX_MESA, 300, 6)
    asesor = persona(CX_MESA, ORO, piso=PISO, e=E_ASESOR)
    mesa = escritorio(CX_MESA, ancho_=260, alto=ALTO_MESA, piso=PISO)
    portatil = figura(partes_computador(), CX_MESA, MESA, 74, -0.4)
    # Todos los clientes miran hacia el asesor, aunque pasen del centro del cuarto.
    clientes = [figura(partes_persona(ropa), cx, PISO, 179 * E_CLIENTE, 0.4)
                for cx, ropa, *_ in CLIENTES]

    # 1. De noche nadie responde.
    scene.play(teclear(cabecera), run_time=0.7)
    scene.play(FadeIn(sala), FadeIn(vidrio), FadeIn(sol), FadeIn(gato, scale=0.7),
               FadeIn(asesor), FadeIn(mesa), FadeIn(portatil), run_time=0.7)
    contador, globos = _de_noche(scene, asesor, vidrio, mordisco, clientes)
    scene.next_slide()

    # 2. Cada pregunta es un trabajo distinto.
    figuras = _trabajos()
    scene.play(FadeOut(VGroup(*globos), shift=UP * 0.1), run_time=0.4)
    scene.play(LaggedStart(*[FadeIn(f, scale=0.7) for f in figuras], lag_ratio=0.35), run_time=1.8)
    scene.next_slide()

    # 3. Todo le cae a un asesor, y los clientes se van.
    _al_otro_dia(scene, asesor, vidrio, mordisco, portatil, contador, figuras)
    scene.play(LaggedStart(*[FadeOut(c, shift=LEFT * 0.7) for c in reversed(clientes)],
                           lag_ratio=0.3), run_time=1.6)
    scene.next_slide()

    # 4. Pasando al código.
    resto = VGroup(cabecera, sala, vidrio, sol, gato, asesor, mesa, contador, *figuras)
    scene.play(FadeOut(resto), run_time=0.6)
    pasando(scene, CIAN, "Pasando", "al código", en_loop=True)
