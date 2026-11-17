import numpy as np
from manim import LEFT, ORIGIN, RIGHT, UP, Create, FadeIn, FadeOut, VGroup, VMobject

from comun.animaciones import teclear
from comun.componentes import (
    MEDIO,
    SEMI,
    caja,
    centrado,
    discontinua,
    linea,
    mono,
    nota,
    rotulo,
    tarjeta,
    texto,
    titular,
    titulo,
)
from comun.estilo import (
    CORAL,
    CORAL_OSCURO,
    GRIS,
    GRIS_CLARO,
    GRIS_MEDIO,
    TEAL,
    TINTA,
    G,
    P,
    U,
)

# La hoja del manual de IBM, dibujada con sus proporciones (1080 × 778 px en la foto).
PROPORCION = 778 / 1080
TINTA_HOJA = "#2a2a2a"
# Las cuatro líneas de la hoja: el texto y su altura, de 0 (arriba) a 1 (abajo).
LINEAS_HOJA = (("A COMPUTER", 0.14), ("CAN NEVER BE HELD ACCOUNTABLE", 0.27),
               ("THEREFORE A COMPUTER MUST NEVER", 0.76), ("MAKE A MANAGEMENT DECISION", 0.88))
FUENTE = ("Fuente: Anthropic, Measuring AI agent autonomy in practice "
          "(anthropic.com/research/measuring-agent-autonomy)")

# La curva de la gráfica de Anthropic, leída de la imagen original: la altura en px de 90
# puntos parejos entre los px 355 y 1743. En esa imagen 25 min caen en el px 806.2 y 45 min en
# el 393.8; el eje del tiempo va del px 298 al 1789.
CURVA = (836, 857, 858, 844, 836, 833, 824, 820, 813, 808, 805, 804, 802, 784, 765, 744, 726,
         717, 715, 715, 715, 714, 714, 711, 710, 703, 691, 680, 670, 661, 660, 656, 653, 651,
         654, 653, 624, 595, 571, 550, 547, 559, 571, 569, 565, 564, 566, 561, 560, 563, 566,
         566, 568, 557, 543, 530, 511, 484, 464, 443, 419, 401, 392, 384, 389, 402, 378, 343,
         337, 322, 330, 383, 405, 409, 409, 408, 405, 403, 402, 402, 408, 430, 459, 491, 519,
         530, 514, 491, 474, 461)
MESES = (("oct 2025", 385), ("nov", 697), ("dic", 1010), ("ene 2026", 1322), ("feb", 1635))
MODELOS = (("Sonnet 4.5", 356), ("Opus 4.5", 936), ("Opus 4.6", 1680))

# Las dos columnas tienen la misma altura: la hoja a la izquierda y la tarjeta a la derecha.
ARRIBA, ABAJO = 212, 684
ANCHO_CHICA = (ABAJO - ARRIBA) / PROPORCION
# La tarjeta y, dentro, el área de la curva: de 20 a 50 minutos.
X0, Y0, X1, Y1 = 96 + ANCHO_CHICA + 40, ARRIBA, 1344, ABAJO
AX0, AX1, AY0, AY1 = X0 + 72, X1 - 28, Y0 + 92, Y1 - 53


# El manual cerrado: tapa azul con el logo de ocho rayas que IBM usaba desde 1972.
AZUL_IBM = "#1f5fa8"
LOMO_IBM = "#16477f"
PAPEL = "#ece6d6"
LX0, LY0, LX1, LY1 = 560, 150, 880, 650
LCX = (LX0 + 22 + LX1) / 2


def _logo_ibm(cx, base, tam):
    """«IBM» grueso cortado por siete rayas del color de la tapa: quedan ocho franjas."""
    letras = titular("IBM", tam, cx, base, color=PAPEL, alinear=ORIGIN, espaciado=tam * 0.04)
    alto = letras.height / U
    medio = letras.width / U / 2 + 4
    paso = alto / 15
    arriba = base - alto
    rayas = VGroup(*[caja(cx - medio, arriba + (2 * i + 1) * paso, cx + medio,
                          arriba + (2 * i + 2) * paso, AZUL_IBM) for i in range(7)])
    return VGroup(letras, rayas)


def _libro():
    """Las hojas que asoman, la primera página (vacía) y la tapa encima."""
    hojas = VGroup(caja(LX0 + 10, LY0 + 8, LX1 + 8, LY1 + 8, "#cfc7b2", radio=4),
                   caja(LX0 + 5, LY0 + 4, LX1 + 4, LY1 + 4, PAPEL, radio=4))
    pagina = caja(LX0, LY0, LX1, LY1, PAPEL, radio=4)
    tapa = VGroup(
        caja(LX0, LY0, LX1, LY1, AZUL_IBM, radio=4),
        caja(LX0, LY0, LX0 + 22, LY1, LOMO_IBM),
        _logo_ibm(LCX, 300, 104),
        caja(LCX - 100, 352, LCX + 100, 354, PAPEL, opacidad=0.6),
        centrado("MANUAL DE", 24, LCX, 404, color=PAPEL, peso=SEMI),
        centrado("CAPACITACIÓN", 24, LCX, 438, color=PAPEL, peso=SEMI),
        mono("1979", 22, LCX, 604, color=PAPEL, alinear=ORIGIN, espaciado=4),
    )
    return hojas, pagina, tapa


def _hoja(x0, y0, x1, y1):
    """La página del manual: papel claro y las cuatro líneas en mayúsculas espaciadas."""
    tam = (x1 - x0) * 0.036
    hoja = VGroup(caja(x0, y0, x1, y1, PAPEL))
    for frase, alto in LINEAS_HOJA:
        hoja.add(centrado(frase, tam, (x0 + x1) / 2, y0 + alto * (y1 - y0) + tam * 0.35,
                          color=TINTA_HOJA, peso=MEDIO, espaciado=tam * 0.12))
    return hoja


def _x(px):
    return AX0 + (px - 298) / (1789 - 298) * (AX1 - AX0)


def _y(minutos):
    return AY1 - (minutos - 20) / 30 * (AY1 - AY0)


def _ejes():
    partes = VGroup(
        texto("¿Cuánto trabaja Claude Code sin detenerse?", 17, X0 + 24, Y0 + 36, peso=SEMI),
        texto("Minutos por turno, en los turnos más largos (percentil 99,9)", 13, X0 + 24,
              Y0 + 58, color=GRIS),
    )
    for minutos in (25, 30, 35, 40, 45):
        partes.add(linea(AX0, _y(minutos), AX1, _y(minutos), GRIS_CLARO, 1),
                   texto(str(minutos), 13, AX0 - 12, _y(minutos) + 5, color=GRIS, alinear=RIGHT))
    partes.add(linea(AX0, AY1, AX1, AY1, GRIS_MEDIO, 1.5))
    for mes, px in MESES:
        partes.add(linea(_x(px), AY1, _x(px), AY1 + 6, GRIS_MEDIO, 1.5),
                   centrado(mes, 13, _x(px), AY1 + 26, color=GRIS))
    return partes


def _lanzamientos():
    """Las rayas punteadas de cada modelo nuevo, con su nombre arriba (el último, a la izquierda
    de su raya para no tocar el borde de la tarjeta)."""
    partes = VGroup()
    for nombre, px in MODELOS:
        ultimo = px == MODELOS[-1][1]
        partes.add(discontinua(_x(px), AY0, _x(px), AY1, GRIS_MEDIO),
                   texto(nombre, 12, _x(px) + (-6 if ultimo else 6), AY0 + 10, color=TINTA,
                         alinear=RIGHT if ultimo else LEFT))
    return partes


def _curva():
    pxs = np.linspace(355.2, 1742.7, len(CURVA))
    minutos = [25 + (806.2 - y) / 20.62 for y in CURVA]
    curva = VMobject().set_points_as_corners([P(_x(px), _y(m)) for px, m in zip(pxs, minutos)])
    return curva.set_stroke(CORAL, width=G(2.8)).set_fill(opacity=0)


def construir(scene):
    scene.marco.ir("inicio")
    sobre = mono("IBM, MANUAL DE CAPACITACIÓN, 1979", 14, 720, 120, color=TEAL, alinear=ORIGIN)
    ancho_hoja = 580 / PROPORCION
    hoja = _hoja(720 - ancho_hoja / 2, 142, 720 + ancho_hoja / 2, 722)

    pregunta = titulo("¿Sigue siendo así?")
    antes = rotulo("IBM, 1979", 96, 196, color=CORAL_OSCURO)
    ahora = rotulo("CLAUDE CODE, 2026", X0, 196, color=TEAL)

    # 1. El manual cerrado, con el logo de IBM de la época y el año.
    hojas, pagina, tapa = _libro()
    scene.play(FadeIn(VGroup(hojas, pagina, tapa), shift=UP * 0.2), run_time=0.8)
    scene.next_slide()

    # 2. El libro se abre en la página y la hoja de 1979 crece hasta llenar la pantalla.
    scene.play(tapa.animate.stretch(0.02, 0, about_edge=LEFT).set_opacity(0), run_time=0.7)
    scene.remove(tapa)
    chica = (LX1 - LX0 - 36) / ancho_hoja
    hoja.scale(chica).move_to(P((LX0 + LX1) / 2, (LY0 + LY1) / 2))
    scene.play(FadeIn(hoja), run_time=0.4)
    scene.play(FadeOut(VGroup(hojas, pagina)), hoja.animate.scale(1 / chica).move_to(P(720, 432)),
               FadeIn(sobre, shift=UP * 0.1), run_time=0.9)
    scene.next_slide()

    # 3. La pregunta: la hoja se hace a un lado.
    scene.play(FadeOut(sobre), run_time=0.4)
    scene.play(hoja.animate.scale(ANCHO_CHICA / ancho_hoja)
               .move_to(P(96 + ANCHO_CHICA / 2, (ARRIBA + ABAJO) / 2)), run_time=1.0)
    scene.play(teclear(pregunta), FadeIn(antes), run_time=0.7)
    scene.next_slide()

    # 4. Lo que pasa hoy: la curva se dibuja sola.
    scene.play(FadeIn(ahora), FadeIn(tarjeta(X0, Y0, X1, Y1), shift=UP * 0.2), run_time=0.5)
    scene.play(FadeIn(_ejes()), FadeIn(_lanzamientos()), run_time=0.6)
    scene.play(Create(_curva()), run_time=2.4)
    scene.play(FadeIn(nota(FUENTE, base=ABAJO + 40)), run_time=0.5)
