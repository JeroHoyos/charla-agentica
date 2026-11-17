"""El enfoque de la charla. El AI Engineer de la diapositiva anterior tiene dos caminos: los
agentic workflows (varios agentes: un orquestador reparte la tarea entre robots con su oficio)
y RAG (el modelo responde con documentos que alguien le busca). Cada camino lleva su diagrama,
con puntos que lo recorren. Al final se enciende el primero, el de esta charla, y RAG queda
como otro enfoque. Va de corrido, sin pausas."""
from manim import RIGHT, UP, FadeIn, FadeOut, LaggedStart, VGroup, there_and_back

from comun.animaciones import recorrer, teclear, trazar
from comun.componentes import (
    SEMI,
    caja,
    centrado,
    chip,
    flecha,
    nodo,
    pixel,
    punto,
    renglones,
    tarjeta,
    titular,
    titulo,
)
from comun.escena import archivador, globo, hoja, robot
from comun.estilo import CIAN, FONDO, GRIS, GRIS_CLARO, GRIS_LINEA, ORO, TINTA, P

from . import ai_engineer

X0, X1 = 440, 1344             # las dos tarjetas
AGENTES = (180, 494)           # alto de cada tarjeta
RAG = (516, 716)
CENTRO = 448                   # de aquí salen los dos caminos
DIAGRAMA = 770                 # donde empiezan los diagramas
FILAS = (-92, 0, 92)           # los tres agentes, respecto al centro de su tarjeta
OFICIOS = ("analista", "ingeniero", "redactor")
X_ROBOT = 1105


def _medio(tarjeta_):
    return sum(tarjeta_) / 2


def _camino(tarjeta_, color=GRIS_LINEA):
    """El camino de la persona a una tarjeta."""
    cy = _medio(tarjeta_)
    return flecha((345, CENTRO), (392, CENTRO), (392, cy), (X0 - 6, cy), color=color,
                  grosor=2.2, punta=11)


def _letrero(tarjeta_, nombre, lineas, color):
    """La tarjeta de un camino, con su nombre y lo que hace el modelo en él, a la izquierda."""
    y0, y1 = tarjeta_
    cy = _medio(tarjeta_)
    return VGroup(tarjeta(X0, y0, X1, y1),
                  titular(nombre, 26, X0 + 30, cy - 12),
                  renglones(lineas, 18, X0 + 30, cy + 24, 25, color=color, peso=SEMI))


def _paso(x0, x1, cy, nombre, tipo="io"):
    return nodo(x0, cy - 22, x1, cy + 22, nombre, tipo=tipo, tam=15)


def _entre(a, b):
    """La flecha de una caja a la que tiene a su derecha."""
    cy = (a.caja[1] + a.caja[3]) / 2
    return flecha((a.caja[2] + 3, cy), (b.caja[0] - 3, cy), color=GRIS_LINEA, punta=8)


def _multiagente():
    """Tarea, orquestador, tres agentes con su oficio y resultado. Devuelve las cajas, los
    robots, las flechas y los recorridos: hasta el orquestador, de él a cada agente y de
    cada agente al resultado."""
    cy = _medio(AGENTES)
    tarea, jefe = _paso(DIAGRAMA, 850, cy, "Tarea"), _paso(890, 1030, cy, "Orquestador", "llm")
    fin = _paso(1180, 1315, cy, "Resultado")
    robots = VGroup(*[robot(X_ROBOT, cy + dy + 35, alto=70, oficio=o)
                      for dy, o in zip(FILAS, OFICIOS)])
    flechas = [_entre(tarea, jefe)]
    ida, vuelta = [], []
    for dy in FILAS:
        y = cy + dy
        flechas += [flecha((1033, cy), (1052, cy), (1052, y), (1076, y), color=GRIS_LINEA,
                           punta=8),
                    flecha((1134, y), (1155, y), (1155, cy), (1177, cy), color=GRIS_LINEA,
                           punta=8)]
        ida.append([(960, cy), (1052, cy), (1052, y), (1072, y)])
        vuelta.append([(1138, y), (1155, y), (1155, cy), (1247, cy)])
    return [tarea, jefe, fin], robots, flechas, ([(810, cy), (960, cy)], ida, vuelta)


X_ARCHIVO, X_MODELO = 965, 1100


def _rag():
    """Pregunta, el archivador con tus documentos, el robot (el modelo) y respuesta. Devuelve
    las piezas, las flechas, la hoja que el archivador le pasa al modelo y el recorrido (hasta
    el archivador y del modelo a la respuesta)."""
    cy = _medio(RAG)
    piso = cy + 46
    pregunta, respuesta = _paso(DIAGRAMA, 862, cy, "Pregunta"), _paso(1196, 1315, cy, "Respuesta")
    archivo = VGroup(archivador(X_ARCHIVO, piso, ancho_=66, alto=92, cajones=3),
                     centrado("Tus documentos", 13, X_ARCHIVO + 8, piso + 24, color=GRIS))
    modelo = robot(X_MODELO, piso, alto=96)
    flechas = [flecha((865, cy), (926, cy), color=GRIS_LINEA, punta=8),
               flecha((1026, cy), (1070, cy), color=GRIS_LINEA, punta=8),
               flecha((1134, cy), (1193, cy), color=GRIS_LINEA, punta=8)]
    papel = hoja(X_ARCHIVO, piso - 118, w=30, h=38, color=ORO, relleno=TINTA, borde=ORO)
    piezas = [pregunta, archivo, modelo, respuesta]
    return piezas, flechas, papel, ([(816, cy), (922, cy)], [(1134, cy), (1255, cy)])


def _bolita(lugar, color):
    return punto(*lugar, 7, TINTA, borde=color, grosor=3).set_z_index(3)


def _persona():
    """El AI Engineer de la diapositiva anterior, con el robot al lado, y su nombre."""
    return VGroup(ai_engineer.figura(ai_engineer.ROLES[-1][3](), 215, 540, 210, 0.35),
                  pixel("AI Engineer", 20, 215, 592))


def _salta(m, alto=0.15):
    return m.animate(rate_func=there_and_back).shift(UP * alto)


def _recorridos(scene, robots, tramos_a, modelo, papel, tramos_r):
    """Arriba, el orquestador reparte la tarea: un punto por agente, que trabaja (salta) y
    entrega al resultado. Abajo, la pregunta llega al archivador, de él sale una hoja que
    vuela hasta el modelo y el modelo responde."""
    llega, ida, vuelta = tramos_a
    a, r = _bolita(llega[0], CIAN), _bolita(tramos_r[0][0], ORO)
    scene.play(FadeIn(a, scale=0.5), FadeIn(r, scale=0.5), run_time=0.3)
    scene.play(recorrer(a, *llega, run_time=0.8), recorrer(r, *tramos_r[0], run_time=0.8))
    tres = [_bolita(ida[0][0], CIAN) for _ in ida]
    scene.add(*tres)
    scene.remove(a)
    alto = papel.get_center()
    papel.shift(UP * -0.5).set_opacity(0)
    scene.play(*[recorrer(b, *camino, run_time=0.8) for b, camino in zip(tres, ida)],
               FadeOut(r, scale=0.4), papel.animate.move_to(alto).set_opacity(1), run_time=0.8)
    scene.play(*[FadeOut(b) for b in tres],
               LaggedStart(*[_salta(m) for m in robots], lag_ratio=0.25),
               papel.animate(path_arc=-1.2).move_to(P(X_MODELO, _medio(RAG) - 10)).scale(0.5),
               run_time=0.8)
    tres = [_bolita(camino[0], CIAN) for camino in vuelta]
    r = _bolita(tramos_r[1][0], ORO)
    scene.add(r)
    scene.play(*[recorrer(b, *camino) for b, camino in zip(tres, vuelta)],
               FadeOut(papel, scale=0.3), _salta(modelo), recorrer(r, *tramos_r[1]),
               run_time=0.9)
    scene.play(*[FadeOut(b, scale=1.8) for b in tres], FadeOut(r, scale=1.8), run_time=0.4)


def construir(scene):
    scene.marco.ir("fundamentos", "0.1")
    persona = _persona()
    duda = globo("¿Qué camino tomo?", 215, 292, hacia=190)
    caminos = [_camino(AGENTES), _camino(RAG)]
    letreros = [_letrero(AGENTES, "Agentic workflows",
                         ("Varios agentes", "se reparten el trabajo"), CIAN),
                _letrero(RAG, "RAG", ("El modelo responde", "con tus documentos"), ORO)]
    cajas_a, robots, flechas_a, tramos_a = _multiagente()
    piezas_r, flechas_r, papel, tramos_r = _rag()

    scene.play(teclear(titulo("Dos caminos para un AI Engineer")), run_time=0.8)
    scene.play(FadeIn(persona, shift=UP * 0.15), run_time=0.6)
    scene.play(FadeIn(duda, shift=UP * 0.1), run_time=0.4)

    # Los dos caminos, cada uno con su diagrama, y los puntos que los recorren.
    scene.play(trazar(*[c[0] for c in caminos]), *[FadeIn(c[1]) for c in caminos],
               LaggedStart(*[FadeIn(m, shift=RIGHT * 0.15) for m in letreros], lag_ratio=0.3),
               run_time=1.0)
    scene.play(LaggedStart(*[FadeIn(m, scale=0.85) for m in [*cajas_a, *robots, *piezas_r]],
                           lag_ratio=0.08), run_time=1.3)
    scene.play(*[FadeIn(f) for f in flechas_a + flechas_r], run_time=0.5)
    _recorridos(scene, robots, tramos_a, piezas_r[2], papel, tramos_r)

    # El de esta charla; RAG es otro enfoque.
    y0, y1 = RAG
    velo = caja(X0 - 2, y0 - 2, X1 + 2, y1 + 2, FONDO, radio=13, opacidad=0.62)
    sellos = [chip("ESTA CHARLA", X1 - 14, AGENTES[0] + 24, tam=12, alinear=RIGHT),
              chip("OTRO ENFOQUE", X1 - 14, y0 + 24, tam=12, alinear=RIGHT, color=GRIS,
                   relleno=GRIS_CLARO)]
    scene.play(FadeOut(duda), letreros[0][0].animate.set_stroke(CIAN, width=4),
               FadeIn(_camino(AGENTES, CIAN)), caminos[1][0].animate.set_stroke(opacity=0.3),
               caminos[1][1].animate.set_opacity(0.3), FadeIn(velo),
               *[FadeIn(s, scale=0.8) for s in sellos],
               persona[0].animate(rate_func=there_and_back).shift(UP * 0.25), run_time=0.7)
