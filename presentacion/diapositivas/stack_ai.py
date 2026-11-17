"""Las herramientas de un AI Engineer: el ranking completo, barra por barra, y después se apagan
todas menos LangChain y LangGraph, que son las que usamos en el taller."""
from manim import LEFT, RIGHT, FadeIn, LaggedStart, VGroup

from comun.animaciones import crecer, teclear
from comun.componentes import (
    MEDIO,
    SEMI,
    caja,
    centrado,
    pildora,
    texto,
    titulo,
)
from comun.estilo import (
    CIAN_SUAVE,
    FONDO,
    GRIS,
    GRIS_CLARO,
    GRIS_MEDIO,
    LILA_SUAVE,
    MORADO,
    TEAL,
    TINTA,
)

# Nombre, para qué sirve y porcentaje.
STACK = (
    ("LangChain", "Construir apps con LLM", 15.4),
    ("PyTorch", "Entrenar redes neuronales", 11.8),
    ("LangGraph", "Agentes y flujos", 11.0),
    ("OpenAI", "Modelos de lenguaje", 10.9),
    ("Anthropic", "Modelos de lenguaje", 9.0),
    ("TensorFlow", "Entrenar redes neuronales", 8.6),
    ("LlamaIndex", "Buscar en documentos", 5.6),
    ("Hugging Face", "Modelos abiertos", 4.7),
    ("Gemini", "Modelos de lenguaje", 4.5),
)
NUESTRAS = {"LangChain": (TEAL, CIAN_SUAVE), "LangGraph": (MORADO, LILA_SUAVE)}

Y0, PASO = 222, 54
X_RANGO, X_NOMBRE, X_USO = 100, 160, 420
X_BARRA, LARGO, X_PCT = 760, 420, 1340


def _fila(i, nombre, uso, pct):
    cy = Y0 + i * PASO
    franja = caja(84, cy - PASO / 2 + 4, 1356, cy + PASO / 2 - 4, FONDO, radio=10, opacidad=0)
    rango = texto(f"{i + 1:02d}", 18, X_RANGO, cy + 7, color=GRIS, peso=MEDIO)
    nom = texto(nombre, 26, X_NOMBRE, cy + 9, color=TINTA, peso=SEMI)
    para = texto(uso, 17, X_USO, cy + 6, color=GRIS)
    riel = pildora(X_BARRA, cy - 7, X_BARRA + LARGO, cy + 7, GRIS_CLARO)
    barra = pildora(X_BARRA, cy - 7, X_BARRA + LARGO * pct / STACK[0][2], cy + 7, GRIS_MEDIO)
    num = texto(f"{pct:.1f} %".replace(".", ","), 22, X_PCT, cy + 8, color=TINTA, peso=SEMI,
                alinear=RIGHT)
    fila = VGroup(franja, rango, nom, para, riel, barra, num)
    fila.partes = dict(franja=franja, nombre=nom, uso=para, barra=barra, num=num, rango=rango)
    return fila


def construir(scene):
    scene.marco.ir("fundamentos", "0.4")
    filas = [_fila(i, *s) for i, s in enumerate(STACK)]
    fuente = centrado("Fuente: Data with Baraa, «AI Engineer Roadmap: Built From 40,000 Real Job Ads»",
                      18, 720, 724, color=GRIS)

    scene.play(teclear(titulo("Las herramientas de un AI Engineer")), run_time=0.9)
    scene.play(FadeIn(fuente), run_time=0.4)
    scene.play(LaggedStart(*[
        LaggedStart(FadeIn(VGroup(*[m for m in f if m is not f.partes["barra"]]),
                           shift=RIGHT * 0.1),
                    crecer(f.partes["barra"], desde=LEFT), lag_ratio=0.4)
        for f in filas], lag_ratio=0.18), run_time=3.0)
    scene.next_slide()

    # Se apagan todas menos las dos que vamos a usar.
    otras = [f for f, s in zip(filas, STACK) if s[0] not in NUESTRAS]
    nuestras = [(f, *NUESTRAS[s[0]]) for f, s in zip(filas, STACK) if s[0] in NUESTRAS]
    anims = [f.animate.set_opacity(0.22) for f in otras]
    for f, color, suave in nuestras:
        p = f.partes
        anims += [p["franja"].animate.set_fill(suave, opacity=1),
                  p["barra"].animate.set_fill(color),
                  p["nombre"].animate.set_color(color),
                  p["num"].animate.set_color(color),
                  p["rango"].animate.set_color(color)]
    scene.play(*anims, run_time=0.8)
