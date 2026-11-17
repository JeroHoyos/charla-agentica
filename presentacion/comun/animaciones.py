from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AddTextLetterByLetter,
    Create,
    FadeIn,
    GrowFromEdge,
    LaggedStart,
    MoveAlongPath,
    UpdateFromAlphaFunc,
    VMobject,
    linear,
    smooth,
    there_and_back,
)

from .estilo import P


def entrar(*mobs, shift=UP * 0.15, lag=0.15, run_time=0.8, scale=1.0):
    return LaggedStart(*[FadeIn(m, shift=shift, scale=scale) for m in mobs],
                       lag_ratio=lag, run_time=run_time)


def subir(*mobs, **kw):
    return entrar(*mobs, shift=UP * 0.2, **kw)


def bajar(*mobs, **kw):
    return entrar(*mobs, shift=DOWN * 0.2, **kw)


def teclear(t, run_time=None):
    """Escribe un texto letra por letra, como una consola de 8 bits."""
    return AddTextLetterByLetter(t, run_time=run_time or min(1.2, 0.04 * len(t) + 0.2))


def crecer(barra, desde=LEFT, **kw):
    return GrowFromEdge(barra, desde, **kw)


def trazar(*lineas, lag=0.0, run_time=0.8):
    return LaggedStart(*[Create(ln) for ln in lineas], lag_ratio=lag, run_time=run_time)


def escribir(codigo, desde=0, hasta=None, run_time=None):
    """Hace aparecer las líneas de una ventana de código, una tras otra."""
    lineas = [ln for ln in codigo.lineas[desde:hasta] if len(ln.submobjects)]
    return LaggedStart(*[FadeIn(ln, shift=RIGHT * 0.12) for ln in lineas], lag_ratio=0.35,
                       run_time=run_time or min(2.2, 0.25 + 0.16 * len(lineas)))


def ventana(codigo, run_time=0.5):
    """Hace aparecer solo el marco de una ventana de código."""
    return FadeIn(codigo.ventana, shift=UP * 0.15, run_time=run_time)


def latido(mob, escala=1.12, run_time=0.6):
    return mob.animate(rate_func=there_and_back, run_time=run_time).scale(escala)


def recorrer(mob, *puntos, run_time=1.0):
    """Lleva `mob` por un camino en codos (puntos del lienzo) a velocidad constante."""
    camino = VMobject().set_points_as_corners([P(x, y) for x, y in puntos])
    return MoveAlongPath(mob, camino, run_time=run_time, rate_func=linear)


def contar(fabrica, desde, hasta, run_time=1.0):
    """Número que cuenta de `desde` a `hasta`. `fabrica(valor)` arma el mobject de cada cuadro;
    devuelve el mobject (ya en su valor inicial) y la animación."""
    m = fabrica(desde)

    def actualizar(mob, alpha):
        mob.become(fabrica(desde + (hasta - desde) * smooth(alpha)))

    return m, UpdateFromAlphaFunc(m, actualizar, run_time=run_time)
