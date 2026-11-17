import os
from statistics import median

import numpy as np
from manim import (
    HEAVY,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    UP,
    CapStyleType,
    Circle,
    DashedVMobject,
    ImageMobject,
    Line,
    Polygon,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
    VMobject,
)

from .estilo import (
    CIAN,
    CIAN_SUAVE,
    CORAL,
    CORAL_OSCURO,
    CORAL_SUAVE,
    FONDO,
    FS,
    GRIS,
    GRIS_CLARO,
    GRIS_LINEA,
    IMAGENES,
    LILA_SUAVE,
    MONO,
    MORADO,
    NOTA,
    OSCURO,
    PIXEL,
    SANS,
    TARJETA,
    TEAL,
    TINTA,
    TITULAR,
    G,
    P,
    U,
)

MEDIO = "MEDIUM"
SEMI = "SEMIBOLD"
NEGRITA = "BOLD"

# Letras que se apoyan en la línea base: sirven para ubicar el texto.
_SIN_COLA = set("gjpqyQ")


def _en_orden(t):
    # A veces los espacios vienen como letras vacías y Pango no siempre respeta el orden
    # del texto: se dejan solo las letras con trazo, ordenadas por posición.
    letras = [g for g in t if g.width + g.height > 1e-6]
    return sorted(letras, key=lambda g: g.get_center()[0])


def _linea_base(t, contenido, pixel, tam):
    letras = [c for c in contenido if not c.isspace()]
    fondos = [g.get_bottom()[1] for c, g in zip(letras, _en_orden(t))
              if c.isalnum() and c not in _SIN_COLA]
    if not fondos:
        return t.get_center()[1] - 0.35 * tam * U
    # Press Start 2P deja un píxel libre (1/8 del cuerpo) bajo cada letra.
    return median(fondos) - (0.125 * tam * U if pixel else 0)


def _espaciar(t, contenido, extra):
    letras = (i for i, c in enumerate(contenido) if not c.isspace())
    for g, i in zip(_en_orden(t), letras):
        g.shift(RIGHT * extra * i)


def texto(contenido, tam, x, base, color=TINTA, peso=NORMAL, fuente=SANS, alinear=LEFT,
          espaciado=0, inclinada=NORMAL, t2c=None, t2w=None):
    """Texto en el lienzo: `tam` en pt, `base` es la línea base y `x` el borde izquierdo, el
    centro o el borde derecho según `alinear` (LEFT, ORIGIN o RIGHT)."""
    opciones = dict(font=fuente, font_size=tam * FS, color=color, weight=peso, slant=inclinada,
                    t2c=t2c or {}, t2w=t2w or {})
    try:
        t = Text(contenido, disable_ligatures=True, **opciones)
    except ValueError:
        # JetBrains Mono une `->`, `!=` o `}}` aunque se pidan sin ligaduras; así sale igual,
        # solo que esas letras quedan pegadas en un glifo.
        t = Text(contenido, **opciones)
    if espaciado:
        _espaciar(t, contenido, espaciado * U)
    pixel = fuente == PIXEL
    t.shift(UP * (P(0, base)[1] - _linea_base(t, contenido, pixel, tam)))
    borde = {-1: t.get_left()[0], 0: t.get_center()[0], 1: t.get_right()[0]}[int(alinear[0])]
    t.shift(RIGHT * (P(x, 0)[0] - borde))
    return t


def titular(contenido, tam, x, base, color=TINTA, alinear=LEFT, **kw):
    """Texto grueso de título (Archivo Black), como los títulos de las guías."""
    return texto(contenido, tam, x, base, color=color, fuente=TITULAR, peso=HEAVY,
                 alinear=alinear, **kw)


def mono(contenido, tam, x, base, color=GRIS, peso=MEDIO, espaciado=1.2, **kw):
    """Rótulo en mono, para etiquetas en mayúsculas."""
    return texto(contenido, tam, x, base, color=color, peso=peso, fuente=MONO,
                 espaciado=espaciado, **kw)


def pixel(contenido, tam, x, base, color=TINTA, alinear=ORIGIN, **kw):
    """Título corto dentro de una diapositiva. Los tamaños vienen de cuando era Press Start
    2P, más ancha: se agrandan para que pesen lo mismo."""
    return titular(contenido, tam * 1.25, x, base, color=color, alinear=alinear, **kw)


def centrado(contenido, tam, cx, base, **kw):
    return texto(contenido, tam, cx, base, alinear=ORIGIN, **kw)


def renglones(lineas, tam, x, base, paso, **kw):
    """Varias líneas seguidas, cada una `paso` pt más abajo que la anterior."""
    return VGroup(*[texto(s, tam, x, base + i * paso, **kw) for i, s in enumerate(lineas)])


def ancho(mob):
    """Ancho de un mobject en pt del lienzo."""
    return mob.width / U


def caja(x0, y0, x1, y1, color, radio=0, borde=None, grosor=0, opacidad=1.0):
    ancho_, alto = (x1 - x0) * U, (y1 - y0) * U
    if radio:
        r = RoundedRectangle(corner_radius=min(radio, (x1 - x0) / 2, (y1 - y0) / 2) * U,
                             width=ancho_, height=alto)
    else:
        r = Rectangle(width=ancho_, height=alto)
    r.set_fill(color, opacity=opacidad)
    r.set_stroke(borde or color, width=G(grosor) if borde else 0)
    return r.move_to(P((x0 + x1) / 2, (y0 + y1) / 2))


def tarjeta(x0, y0, x1, y1, color=TARJETA, radio=12, **kw):
    return caja(x0, y0, x1, y1, color, radio=radio, **kw)


def pildora(x0, y0, x1, y1, color, **kw):
    return caja(x0, y0, x1, y1, color, radio=(y1 - y0) / 2, **kw)


def chip(contenido, x, cy, color=TEAL, relleno=CIAN_SUAVE, tam=16, peso=SEMI, alinear=LEFT,
         borde=None, alto=None, margen=12, fuente=MONO):
    """Texto dentro de una píldora que se ajusta a su ancho. `x` es el borde izquierdo, el
    centro o el borde derecho según `alinear`; `cy` es el centro vertical."""
    t = texto(contenido, tam, 0, cy + 0.36 * tam, color=color, peso=peso, fuente=fuente)
    alto = alto or tam + 14
    largo = ancho(t) + 2 * margen
    x0 = {-1: x, 0: x - largo / 2, 1: x - largo}[int(alinear[0])]
    fondo = pildora(x0, cy - alto / 2, x0 + largo, cy + alto / 2, relleno, borde=borde,
                    grosor=1.5 if borde else 0)
    t.shift(RIGHT * (P(x0 + margen, 0)[0] - t.get_left()[0]))
    return VGroup(fondo, t)


def linea(x0, y0, x1, y1, color, grosor, redondeada=False):
    ln = Line(P(x0, y0), P(x1, y1), color=color, stroke_width=G(grosor))
    if redondeada:
        ln.set_cap_style(CapStyleType.ROUND)
    return ln


def punto(x, y, radio, relleno, borde=None, grosor=0):
    d = Circle(radius=radio * U).move_to(P(x, y))
    d.set_fill(relleno, opacity=1)
    d.set_stroke(borde or relleno, width=G(grosor) if borde else 0)
    return d


def marca(cx, cy, radio, color, bien=True):
    """Un visto bueno (o una equis) dibujado con trazos: las fuentes no traen esos signos."""
    if bien:
        puntos = [(-0.5, 0.05), (-0.12, 0.42), (0.52, -0.38)]
        trazos = [VMobject().set_points_as_corners([P(cx + x * radio, cy + y * radio)
                                                    for x, y in puntos])]
    else:
        trazos = [Line(P(cx - s * 0.4 * radio, cy - 0.4 * radio),
                       P(cx + s * 0.4 * radio, cy + 0.4 * radio)) for s in (-1, 1)]
    signo = VGroup(*trazos).set_stroke(color, width=G(radio * 0.24)).set_fill(opacity=0)
    for trazo in signo:
        trazo.set_cap_style(CapStyleType.ROUND)
    return signo


def raya(x0, y, x1, color, grosor=3):
    return caja(x0, y - grosor / 2, x1, y + grosor / 2, color)


def discontinua(x0, y0, x1, y1, color, grosor=1.5, trazos=None):
    ln = linea(x0, y0, x1, y1, color, grosor)
    largo = np.hypot(x1 - x0, y1 - y0)
    return DashedVMobject(ln, num_dashes=trazos or max(3, int(largo / 9)), dashed_ratio=0.55)


def imagen(nombre, x0, y0, x1, y1):
    img = ImageMobject(os.path.join(IMAGENES, nombre))
    img.stretch_to_fit_width((x1 - x0) * U).stretch_to_fit_height((y1 - y0) * U)
    return img.move_to(P((x0 + x1) / 2, (y0 + y1) / 2))


def logo(x0=1272, y0=34.5, lado=72):
    """El ojo de Aperture centrado en el cuadro de `lado`; la imagen (520 × 359 px) va
    recortada a su borde, así que ocupa casi todo el ancho del cuadro."""
    ancho_ = 0.96 * lado
    alto = ancho_ * 359 / 520
    cx, cy = x0 + lado / 2, y0 + lado / 2
    return imagen("ojo_aperture.png", cx - ancho_ / 2, cy - alto / 2, cx + ancho_ / 2,
                  cy + alto / 2)


def cursor_esquina():
    """El logo de Aperture abajo a la derecha: aparece cuando la diapositiva espera la flecha."""
    return logo(1338, 712, 76)


def formas_fondo(color, opacidad=0.07, x0=1040):
    """Las dos formas grandes del borde derecho, como la marca de agua de las guías: un
    paralelogramo arriba y un cuarto de disco abajo."""
    arriba = Polygon(P(x0, 330), P(1440, 190), P(1440, 600), P(x0, 600))
    arco = [P(x0 + 400 * np.cos(a), 640 + 400 * np.sin(a)) for a in np.linspace(0, np.pi / 2, 24)]
    abajo = Polygon(P(x0, 640), *arco)
    formas = VGroup(arriba, abajo)
    return formas.set_fill(color, opacity=opacidad).set_stroke(width=0)


def titulo(contenido, base=146, tam=44, color=TINTA):
    """Título de diapositiva: grueso y a la izquierda, bajo la raya de la cabecera."""
    return titular(contenido, tam, 94, base, color=color)


def nota(contenido, base=742, **kw):
    """Fuente o aclaración al pie de la diapositiva."""
    return centrado(contenido, 15, 720, base, color=NOTA, **kw)


def rotulo(contenido, x, base, color=TEAL, tam=16, alinear=LEFT):
    """Rótulo en mayúsculas espaciadas, como «HOW WE MEASURE INEQUALITY» en la ASA."""
    return texto(contenido, tam, x, base, color=color, peso=SEMI, espaciado=1.4, alinear=alinear,
                 fuente=MONO)


# --- Diagramas ------------------------------------------------------------------------

# Tipos de caja de los diagramas: relleno, borde, texto y subtexto (leyenda de la guía de
# patrones: entrada/salida, LLM, control, herramienta, humano y guardrail).
TIPOS = {
    "io": (TARJETA, TINTA, TINTA, GRIS),
    "llm": (CIAN, CIAN, OSCURO, OSCURO),
    "control": (TINTA, TINTA, OSCURO, "#4d6b78"),
    "herramienta": ("#1f3f4e", GRIS_LINEA, TINTA, GRIS),
    "humano": (LILA_SUAVE, MORADO, TINTA, MORADO),
    "guardrail": (CORAL_SUAVE, CORAL, TINTA, CORAL_OSCURO),
    "bloqueo": (CORAL, CORAL, OSCURO, OSCURO),
    "apagado": (FONDO, GRIS_CLARO, GRIS_LINEA, GRIS_LINEA),
}


def nodo(x0, y0, x1, y1, nombre, sub=None, tipo="io", tam=17, tam_sub=13, punteado=False,
         radio=10):
    """Caja de diagrama con su nombre (y una línea de detalle) centrados."""
    relleno, borde, color, color_sub = TIPOS[tipo]
    fondo = caja(x0, y0, x1, y1, relleno, radio=radio, borde=borde, grosor=1.6)
    if punteado:
        fondo.set_stroke(opacity=0)
        marco = DashedVMobject(caja(x0, y0, x1, y1, relleno, radio=radio, borde=borde,
                                    grosor=1.6), num_dashes=int((x1 - x0 + y1 - y0) / 7))
        fondo = VGroup(fondo, marco)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if sub is None:
        partes = [centrado(nombre, tam, cx, cy + 0.36 * tam, color=color, peso=SEMI)]
    else:
        partes = [centrado(nombre, tam, cx, cy + 0.36 * tam - 8, color=color, peso=SEMI),
                  centrado(sub, tam_sub, cx, cy + 0.36 * tam_sub + 11, color=color_sub)]
    grupo = VGroup(fondo, *partes)
    grupo.caja = (x0, y0, x1, y1)
    grupo.tipo = tipo
    return grupo


def _punta(fin, direccion, color, largo, ancho_):
    d = direccion / np.linalg.norm(direccion)
    normal = np.array([-d[1], d[0], 0.0])
    base = fin - d * largo * U
    tri = Polygon(fin, base + normal * ancho_ / 2 * U, base - normal * ancho_ / 2 * U)
    return tri.set_fill(color, opacity=1).set_stroke(color, width=0)


def flecha(*puntos, color=TINTA, grosor=1.8, punteada=False, punta=9):
    """Flecha en codos por los `puntos` del lienzo, con la punta en el último."""
    pts = [P(x, y) for x, y in puntos]
    direccion = pts[-1] - pts[-2]
    tip = _punta(pts[-1], direccion, color, punta, punta * 0.95)
    # El trazo termina donde empieza la punta, para que no la atraviese.
    pts[-1] = pts[-1] - direccion / np.linalg.norm(direccion) * punta * 0.8 * U
    trazo = VMobject().set_points_as_corners(pts)
    trazo.set_stroke(color, width=G(grosor)).set_fill(opacity=0)
    if punteada:
        largo = sum(np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])) / U
        trazo = DashedVMobject(trazo, num_dashes=max(2, int(largo / 9)), dashed_ratio=0.55)
    return VGroup(trazo, tip)


def etiqueta(contenido, cx, cy, color=GRIS, relleno=FONDO, tam=13):
    """Rótulo pequeño sobre una flecha, con fondo para que la línea no lo cruce."""
    return chip(contenido, cx, cy, color=color, relleno=relleno, tam=tam, peso=NORMAL,
                alinear=ORIGIN, alto=tam + 8, margen=7)


NOMBRES_TIPO = {"io": "Entrada o salida", "llm": "Modelo", "control": "Control",
                "guardrail": "Guardrail", "bloqueo": "Bloqueo", "herramienta": "Herramienta",
                "humano": "Humano"}


def leyenda(tipos, x, cy, tam=12):
    """La fila de la leyenda al pie de un diagrama: un cuadrito por tipo de caja y su nombre."""
    partes = VGroup()
    for tipo in tipos:
        relleno, borde = TIPOS[tipo][:2]
        t = texto(NOMBRES_TIPO[tipo], tam, x + 24, cy + 0.36 * tam, color=GRIS)
        partes.add(caja(x, cy - 6, x + 16, cy + 6, relleno, radio=3.5, borde=borde, grosor=1.2), t)
        x += 24 + ancho(t) + 24
    return partes


# --- Pixel art --------------------------------------------------------------------------

def pixel_arte(mapa, colores, x0, y0, lado):
    """Dibujo de cuadritos: cada letra del mapa es un color de `colores` ('.' es vacío).
    Va un solo trazo por color para que no pese en el render."""
    capas = {}
    molde = Rectangle(width=lado * U * 1.02, height=lado * U * 1.02).points
    for j, fila in enumerate(mapa):
        for i, c in enumerate(fila):
            if c in colores:
                capas.setdefault(c, VMobject()).append_points(
                    molde + P(x0 + (i + 0.5) * lado, y0 + (j + 0.5) * lado))
    grupo = VGroup()
    for c, capa in capas.items():
        grupo.add(capa.set_fill(colores[c], opacity=1).set_stroke(width=0))
    return grupo


def icono(nombre, x0, y0, lado, colores=None):
    from .iconos import COLORES, ICONOS  # import tardío: iconos usa este módulo

    mapa = ICONOS[nombre]
    return pixel_arte(mapa, {**COLORES, **(colores or {})}, x0, y0, lado)


def icono_centrado(nombre, cx, cy, lado, colores=None):
    from .iconos import ICONOS

    mapa = ICONOS[nombre]
    ancho_, alto = len(mapa[0]) * lado, len(mapa) * lado
    return icono(nombre, cx - ancho_ / 2, cy - alto / 2, lado, colores)
