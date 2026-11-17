"""Piezas de las diapositivas de analogía: una oficina, su gente,
sus muebles y los rótulos que primero nombran la analogía y después el concepto. El robot de la
portada es siempre el modelo; las personas son clientes, empleados o quien revisa. Todos van
en 3D, hechos de cajas (tres_d.py)."""

from manim import ORIGIN, UP, FadeIn, FadeOut, LaggedStart, Polygon, Transform, VGroup

from .animaciones import teclear
from .componentes import (
    MEDIO,
    NEGRITA,
    ancho,
    caja,
    chip,
    marca,
    punto,
    tarjeta,
    texto,
    titulo,
)
from .estilo import (
    CIAN,
    CORAL,
    CORAL_OSCURO,
    FONDO,
    GRIS_CLARO,
    GRIS_LINEA,
    GRIS_MEDIO,
    OSCURO,
    SANS,
    TARJETA,
    TINTA,
    VERDE_OSCURO,
    G,
    P,
)
from .tres_d import figura, mezcla, partes_persona, partes_robot

# La oficina de noche: pared y suelo oscuros, y los muebles y la gente con color.
PARED, SUELO, BORDE_SUELO = "#16323f", "#1d3f4e", "#2b5263"
MADERA, MADERA_OSCURA = "#c2a273", "#96784b"
METAL = "#24485a"
FONDO_MUEBLE = 46  # cuánto se ve de la tapa y del costado de un mueble
X0, X1, TECHO, PISO = 96, 1344, 206, 540
Y_LUGAR, Y_CIERRE = 566, 656


def cuarto():
    pared = caja(X0, TECHO, X1, PISO, PARED, radio=14)
    suelo = Polygon(P(X0, PISO), P(X1, PISO), P(X1 + 22, PISO + 50), P(X0 - 22, PISO + 50))
    suelo.set_fill(SUELO, opacity=1).set_stroke(width=0)
    borde = caja(X0, PISO - 1.5, X1, PISO + 1.5, BORDE_SUELO)
    return VGroup(pared, suelo, borde)


def _mira(cx):
    """Hacia dónde se gira una figura: todas miran un poco hacia el centro del cuarto."""
    return 0.4 if cx < 720 else -0.4


def persona(cx, ropa, piso=PISO, gorra=None, e=1.0):
    """Una persona de pie, en 3D y de cajas como los robots. `gorra` es el color de la gorra
    (quien revisa la lleva)."""
    return figura(partes_persona(ropa, gorra), cx, piso, 179 * e, _mira(cx))


def robot(cx, piso=PISO, alto=176, color=CIAN, oficio=None):
    """El robot de la portada: en todas las analogías es el modelo. Detrás de un escritorio
    va primero en la escena, para que el escritorio le tape las piernas. Los robots pequeños
    que hacen un trabajo llevan su `oficio` (tres_d.OFICIOS)."""
    return figura(partes_robot(color, luz=1.0, oficio=oficio), cx, piso, alto, _mira(cx))


def _bloque(x0, y0, x1, y1, color, fondo=FONDO_MUEBLE):
    """La tapa y el costado derecho de un mueble visto un poco desde arriba; el frente (de
    x0, y0 a x1, y1) lo dibuja cada mueble."""
    dx, dy = fondo * 0.45, fondo * 0.42
    tapa = Polygon(P(x0, y0), P(x1, y0), P(x1 + dx, y0 - dy), P(x0 + dx, y0 - dy))
    lado = Polygon(P(x1, y0), P(x1 + dx, y0 - dy), P(x1 + dx, y1 - dy), P(x1, y1))
    tapa.set_fill(mezcla(color, "#ffffff", 0.18), opacity=1).set_stroke(width=0)
    lado.set_fill(mezcla(color, FONDO, 0.45), opacity=1).set_stroke(width=0)
    return [lado, tapa]


def escritorio(cx, ancho_=200, alto=44, piso=PISO):
    """Un escritorio bajo: al robot que va detrás se le ven la cabeza y el cuerpo."""
    x0, x1 = cx - ancho_ / 2, cx + ancho_ / 2
    tablero = caja(x0, piso - alto, x1, piso - alto + 12, MADERA_OSCURA)
    cuerpo = caja(x0 + 10, piso - alto + 12, x1 - 10, piso, MADERA)
    costado = _bloque(x0 + 10, piso - alto + 12, x1 - 10, piso, MADERA, 36)[0]
    return VGroup(costado, cuerpo,
                  *_bloque(x0, piso - alto, x1, piso - alto + 12, MADERA_OSCURA, 36),
                  tablero)


def hoja(cx, cy, w=44, h=56, lineas=3, color=GRIS_MEDIO, relleno=TARJETA, borde=GRIS_LINEA):
    """Una hoja de papel con renglones."""
    papel = caja(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, relleno, radio=4, borde=borde,
                 grosor=1.4)
    paso = (h - 16) / max(lineas, 1)
    renglones = [caja(cx - w / 2 + 7, cy - h / 2 + 10 + i * paso,
                      cx + w / 2 - (7 if i % 2 == 0 else 15), cy - h / 2 + 13 + i * paso, color,
                      radio=1.5) for i in range(lineas)]
    return VGroup(papel, *renglones)


def sello(cx, cy, bien=True, radio=13):
    """El visto bueno (o el rechazo) que queda sobre una hoja."""
    color = VERDE_OSCURO if bien else CORAL
    return VGroup(punto(cx, cy, radio, color), marca(cx, cy, radio, OSCURO, bien))


def puerta(cx, nombre, color, piso=PISO, ancho_=96, alto=170):
    marco = caja(cx - ancho_ / 2, piso - alto, cx + ancho_ / 2, piso, MADERA_OSCURA, radio=4)
    hoja_ = caja(cx - ancho_ / 2 + 7, piso - alto + 7, cx + ancho_ / 2 - 7, piso, MADERA)
    pomo = punto(cx + ancho_ / 2 - 20, piso - alto / 2 + 10, 4.5, OSCURO)
    letrero = chip(nombre, cx, piso - alto - 22, color=TINTA, relleno=color, tam=14,
                   alinear=UP * 0)
    return VGroup(marco, hoja_, pomo, letrero)


def archivador(cx, piso=PISO, ancho_=96, alto=170, cajones=3):
    x0, x1 = cx - ancho_ / 2, cx + ancho_ / 2
    cuerpo = caja(x0, piso - alto, x1, piso, METAL, borde=GRIS_LINEA, grosor=1.5)
    paso = (alto - 12) / cajones
    partes = [*_bloque(x0, piso - alto, x1, piso, METAL), cuerpo]
    for i in range(cajones):
        y0 = piso - alto + 8 + i * paso
        partes.append(caja(x0 + 8, y0, x1 - 8, y0 + paso - 8, "#2f5a6e", radio=4,
                           borde=GRIS_LINEA, grosor=1.2))
        partes.append(caja(cx - 14, y0 + paso / 2 - 7, cx + 14, y0 + paso / 2 - 2, GRIS_LINEA,
                           radio=2))
    return VGroup(*partes)


def _cola(cx, largo, x0, x1, hacia):
    """Dónde nace la cola del globo y hacia qué lado se inclina. Sin `hacia`, sale del medio
    y baja derecha: así no apunta a nadie equivocado."""
    if hacia is None:
        return cx, 0
    return min(max(hacia, x0 + 24), x1 - 24), (-1 if hacia < cx else 1)


def globo(contenido, cx, cy, color=TINTA, relleno=TARJETA, tam=17, hacia=None, cola=True):
    """Lo que alguien dice: un globo centrado en (cx, cy), con sombra y una cola abajo que
    apunta a quien habla (`hacia` es su x). Con `cola=False` es solo un letrero. El borde
    toma el color del texto: coral lo que sale mal, teal lo que sale bien."""
    t = texto(contenido, tam, cx, cy + 0.36 * tam, color=color, peso=MEDIO, fuente=SANS,
              alinear=ORIGIN)
    largo, alto = ancho(t) + 34, tam + 24
    x0, y0, x1, y1 = cx - largo / 2, cy - alto / 2, cx + largo / 2, cy + alto / 2
    linea = GRIS_MEDIO if color == TINTA else mezcla(color, relleno, 0.3)
    partes = [caja(x0 + 2, y0 + 5, x1 + 2, y1 + 6, FONDO, radio=13, opacidad=0.6),
              caja(x0, y0, x1, y1, relleno, radio=13, borde=linea, grosor=1.6)]
    if cola:
        base, lado = _cola(cx, largo, x0, x1, hacia)
        pico = Polygon(P(base - 9, y1 - 1), P(base + 9, y1 - 1), P(base + 7 * lado, y1 + 13))
        pico.set_fill(relleno, opacity=1).set_stroke(linea, width=G(1.6))
        # Tapa el borde del globo donde nace la cola, para que sean una sola pieza.
        partes += [pico, caja(base - 7.5, y1 - 3, base + 7.5, y1 + 0.6, relleno)]
    return VGroup(*partes, t)


def lugar(nombre, cx, concepto=False):
    """Rótulo bajo una pieza de la escena. Con `concepto`, es el nombre que tiene en el taller."""
    # En la analogía, una etiqueta con borde; en el taller, la píldora cian llena.
    return chip(nombre, cx, Y_LUGAR, color=OSCURO if concepto else TINTA,
                relleno=CIAN if concepto else TARJETA, tam=14, alinear=UP * 0,
                borde=CIAN if concepto else GRIS_LINEA, alto=30)


def cierre(frase, resalte="", cy=Y_CIERRE, tam=20, malo=False):
    """La frase que queda: una sola, con lo importante resaltado. Con `malo`, es el problema."""
    cuerpo = texto(frase, tam, 124, cy + 0.36 * tam, color=TINTA if malo else OSCURO,
                   peso=MEDIO,
                   t2c={resalte: CORAL_OSCURO} if resalte and malo else None,
                   t2w={resalte: NEGRITA} if resalte else None)
    if malo:
        # El problema: una nota oscura con el canto coral.
        fondo = VGroup(tarjeta(X0, cy - 30, X1, cy + 30, TARJETA, radio=12, borde=GRIS_CLARO,
                               grosor=1.2),
                       caja(X0, cy - 22, X0 + 5, cy + 22, CORAL, radio=2.5))
    else:
        # La idea: la franja de color de las guías.
        fondo = tarjeta(X0, cy - 30, X1, cy + 30, CIAN, radio=12)
    return VGroup(fondo, cuerpo)


def llevar(mob, x, y, arco=0):
    """Mueve una pieza hasta el punto (x, y) del lienzo; con `arco`, por un camino curvo."""
    return mob.animate(path_arc=arco).move_to(P(x, y))


def analogia(bloque, numero, pregunta, pista, dibujo, rotulos, problema, frase, definicion):
    """Diapositiva de analogía, en tres tiempos. `dibujo()` devuelve lo que ya está en el
    cuarto y dos funciones: la que anima el problema (devuelve lo que hay que quitar después)
    y la que anima la solución. `rotulos` son (x, en la analogía, en el taller); `problema`,
    `frase` y `definicion` son (texto, parte resaltada). Primero se ve qué salía mal, después
    la analogía que lo arregla y, al final, los rótulos pasan a ser los del concepto."""

    def construir(scene):
        scene.marco.ir(bloque, numero)
        fijo, falla, arreglo = dibujo()
        lugares = [lugar(a, x) for x, a, _ in rotulos]
        nuevos = [lugar(b, x, concepto=True) for x, _, b in rotulos]
        antes, primera, segunda = cierre(*problema, malo=True), cierre(*frase), cierre(*definicion)

        scene.play(teclear(titulo(pregunta)), run_time=0.7)
        scene.play(FadeIn(cuarto()), run_time=0.5)
        scene.play(LaggedStart(*[FadeIn(m, shift=UP * 0.12) for m in fijo], lag_ratio=0.15),
                   run_time=0.8)
        sobras = falla(scene)
        scene.play(FadeIn(antes, shift=UP * 0.15), run_time=0.5)
        scene.next_slide()
        scene.play(FadeOut(antes), *[FadeOut(m) for m in sobras], run_time=0.5)
        arreglo(scene)
        scene.play(LaggedStart(*[FadeIn(m, scale=0.9) for m in lugares], lag_ratio=0.2),
                   FadeIn(primera, shift=UP * 0.15), run_time=0.8)
        scene.next_slide()
        scene.play(*[Transform(a, b) for a, b in zip(lugares, nuevos)], run_time=0.7)
        scene.play(FadeOut(primera, shift=UP * 0.1), FadeIn(segunda, shift=UP * 0.15),
                   run_time=0.6)

    return construir
