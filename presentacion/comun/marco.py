from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    Rectangle,
    VGroup,
    config,
)

from .componentes import formas_fondo, logo, mono, raya
from .estilo import FONDO, GRIS, GRIS_MEDIO, SECCIONES


class Marco:
    """Lo que se queda entre diapositivas: fondo, rótulo de módulo y lección, logo y puntos."""

    def __init__(self, scene, color_fondo):
        self.scene = scene
        self.fondo = Rectangle(width=config.frame_width + 0.1, height=config.frame_height + 0.1)
        self.fondo.set_fill(color_fondo, opacity=1).set_stroke(width=0)
        scene.add(self.fondo)
        self.clave = None
        self.rotulo = None
        self.logo = None
        self.puntos = None

    @property
    def fijos(self):
        # Con toda su familia: las animaciones meten a la escena las piezas sueltas (la raya y el
        # texto del rótulo, cada punto de la esquina), no el grupo.
        grupos = (self.fondo, self.rotulo, self.logo, self.puntos)
        return {m for g in grupos if g is not None for m in g.get_family()}

    def ir(self, seccion=None, numero=None, con_logo=True, con_puntos=True, color_fondo=FONDO):
        """Deja el marco listo para la siguiente diapositiva, animando solo lo que cambia.
        `numero` es la lección (p. ej. "1.3"); su nombre sale del temario."""
        anims = [self.fondo.animate.set_fill(color_fondo)]
        anims += self._cambiar_rotulo(seccion, numero)
        # El logo ya no va arriba: es el indicador de espera (cursor_esquina).
        anims += self._cambiar_logo(False)
        anims += self._cambiar_puntos(seccion if con_puntos else None)
        self.scene.play(*anims, run_time=0.7)

    def _cambiar_rotulo(self, seccion, numero):
        # La cabecera solo cambia con el bloque: entre lecciones del mismo bloque se queda.
        clave = seccion
        if clave == self.clave and self.rotulo is not None:
            return []
        anims = []
        if self.rotulo is not None:
            anims.append(FadeOut(self.rotulo, shift=UP * 0.12))
            self.rotulo = None
        self.clave = clave
        if seccion is None:
            return anims
        # A la izquierda, siempre el nombre de la charla, sobre la raya.
        self.rotulo = VGroup(
            raya(96, 82, 1344, GRIS_MEDIO, grosor=1.5),
            mono("DE PROMPTS A AGENTES", 14, 96, 64, color=GRIS),
        )
        anims += [GrowFromEdge(self.rotulo[0], LEFT),
                  *[FadeIn(m, shift=UP * 0.12) for m in self.rotulo[1:]]]
        return anims

    def _cambiar_logo(self, con_logo):
        if con_logo and self.logo is None:
            self.logo = logo()
            return [FadeIn(self.logo, scale=0.6)]
        if not con_logo and self.logo is not None:
            viejo, self.logo = self.logo, None
            return [FadeOut(viejo, scale=0.6)]
        return []

    def _cambiar_puntos(self, seccion):
        color = SECCIONES[seccion][2] if seccion else None
        if self.puntos is None:
            if color is None:
                return []
            self.puntos = formas_fondo(color)
            return [FadeIn(self.puntos, shift=LEFT * 0.3)]
        if color is None:
            viejo, self.puntos = self.puntos, None
            return [FadeOut(viejo, shift=DOWN * 0.1)]
        return [self.puntos.animate.set_color(color)]
