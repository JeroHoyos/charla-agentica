from manim import Circle, FadeIn, Group, GrowFromCenter

from comun.animaciones import teclear
from comun.componentes import imagen, pixel
from comun.estilo import CIAN, FONDO_OSCURO, G, P, U

# Como en charla-git y charla-redes-neuronales: el gato de la tostada en un círculo blanco.
CENTRO = (720, 322)
DIAMETRO = 420
# La foto va sin fondo (el blanco pasó a transparente): al aparecer no se ve su cuadro.
OCUPACION = 0.62


def construir(scene):
    scene.marco.ir(None, con_puntos=False, color_fondo=FONDO_OSCURO)
    disco = Circle(radius=DIAMETRO / 2 * U).move_to(P(*CENTRO))
    disco.set_fill("#ffffff", opacity=1).set_stroke(width=0)
    lado = DIAMETRO * OCUPACION
    gato = imagen("gato_tostada_sin_fondo.png", 0, 0, lado * 253 / 265, lado).move_to(P(*CENTRO))
    borde = Circle(radius=DIAMETRO / 2 * U, color=CIAN, stroke_width=G(6)).move_to(P(*CENTRO))
    mensaje = pixel("Pronto iniciamos", 34, 720, 650, color="#f4f8fa")

    scene.play(FadeIn(Group(disco, gato), scale=0.85), GrowFromCenter(borde), run_time=0.9)
    scene.play(teclear(mensaje), run_time=0.8)
