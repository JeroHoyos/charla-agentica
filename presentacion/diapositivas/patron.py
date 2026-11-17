"""La ficha de cada patrón: el título y su diagrama en grande, como el de la guía, sin frases
debajo (pedido así). El bloque 4 son las diez fichas seguidas, sin analogías. Resume la guía
«Patrones de desarrollo agéntico» de Commit Academy."""

from manim import UP, FadeIn, LaggedStart, VGroup

from comun.animaciones import teclear
from comun.componentes import (
    TIPOS,
    discontinua,
    etiqueta,
    flecha,
    leyenda,
    nodo,
    tarjeta,
    titulo,
)
from comun.estilo import (
    CORAL,
    CORAL_OSCURO,
    GRIS,
    GRIS_CLARO,
    MORADO,
    TARJETA,
    VERDE_OSCURO,
    P,
    U,
)

# --- Diagramas: cada uno cabe en una tarjeta de 608 × 222 que empieza en (x, y) ------------


def _n(x0, y0, x1, y1, nombre, tipo, **kw):
    return nodo(x0, y0, x1, y1, nombre, tipo=tipo, tam=13, radio=8, **kw)


def _s(x0, y0, x1, y1, nombre, sub, tipo, **kw):
    """Caja con su nombre y una línea de detalle."""
    return nodo(x0, y0, x1, y1, nombre, sub, tipo=tipo, tam=13, tam_sub=11, radio=8, **kw)


def _fila(x, m, cajas, ancho, hueco, alto=18):
    """Cajas en fila, centradas en `m`, con una flecha entre cada par."""
    nodos, flechas, x0 = [], [], x
    for i, (nombre, tipo) in enumerate(cajas):
        nodos.append(_n(x0, m - alto, x0 + ancho, m + alto, nombre, tipo))
        if i:
            flechas.append(flecha((x0 - hueco, m), (x0, m)))
        x0 += ancho + hueco
    return nodos, flechas


def _centro(i):
    """El centro de la caja `i` de una fila de seis que empieza en x + 18."""
    return 18 + 97 * i + 43


def _router(x, y):
    m = y + 104
    salidas = [y + 56, y + 104, y + 152]
    return VGroup(
        _n(x + 16, m - 18, x + 96, m + 18, "Usuario", "io"),
        _s(x + 126, m - 24, x + 246, m + 24, "Router", "modelo pequeño", "control"),
        *[_n(x + 300, s - 16, x + 450, s + 16, n, "llm")
          for s, n in zip(salidas, ("Facturación", "Soporte", "Ventas"))],
        _n(x + 300, y + 180, x + 450, y + 210, "Humano o fallback", "humano"),
        _n(x + 498, m - 18, x + 592, m + 18, "Respuesta", "io"),
        flecha((x + 96, m), (x + 126, m)),
        *[flecha((x + 246, m), (x + 273, m), (x + 273, s), (x + 300, s)) for s in salidas],
        *[flecha((x + 450, s), (x + 474, s), (x + 474, m), (x + 498, m)) for s in salidas],
        flecha((x + 273, salidas[2]), (x + 273, y + 195), (x + 300, y + 195), color=CORAL,
               punteada=True),
        etiqueta("confianza < 0.7", x + 196, y + 195, color=CORAL, relleno=TARJETA, tam=12),
    )


def _guardrail_entrada(x, y):
    m = y + 100
    cajas = (("Entrada", "io"), ("Validar", "guardrail"), ("Autorizar", "guardrail"),
             ("Clasificar", "guardrail"), ("Separar", "guardrail"), ("Agente", "llm"))
    nodos, flechas = _fila(x + 18, m, cajas, 86, 11)
    return VGroup(
        *nodos, *flechas,
        _n(x + 120, y + 168, x + 400, y + 202, "Bloquear + respuesta segura", "bloqueo"),
        _n(x + 436, y + 168, x + 592, y + 202, "Log de incidentes", "herramienta"),
        *[flecha((x + _centro(i), m + 18), (x + _centro(i), y + 168), color=CORAL)
          for i in (1, 2, 3)],
        flecha((x + 400, y + 185), (x + 436, y + 185), color=GRIS),
    )


def _guardrail_salida(x, y):
    m = y + 100
    cajas = (("Agente", "llm"), ("Estructura", "guardrail"), ("Política", "guardrail"),
             ("Grounding", "guardrail"), ("Negocio", "guardrail"), ("Usuario", "io"))
    nodos, flechas = _fila(x + 18, m, cajas, 86, 11)
    return VGroup(
        *nodos, *flechas,
        _n(x + 120, y + 168, x + 480, y + 202, "Reintentar con feedback, máximo N", "bloqueo"),
        _n(x + 508, y + 168, x + 592, y + 202, "Fallback", "control"),
        *[flecha((x + _centro(i), m + 18), (x + _centro(i), y + 168), color=CORAL)
          for i in (1, 2, 3, 4)],
        flecha((x + 480, y + 185), (x + 508, y + 185), color=GRIS),
        flecha((x + 120, y + 185), (x + _centro(0), y + 185), (x + _centro(0), m + 18),
               color=CORAL, punteada=True),
    )


def _cadena(x, y):
    m = y + 104
    cajas = (("Entrada", "io"), ("LLM 1", "llm"), ("Gate", "guardrail"), ("LLM 2", "llm"),
             ("LLM 3", "llm"), ("Salida", "io"))
    nodos, flechas = _fila(x + 18, m, cajas, 86, 11)
    return VGroup(
        *nodos, *flechas,
        *[etiqueta(s, x + _centro(i), m - 38, relleno=TARJETA, tam=12)
          for i, s in ((1, "crear índice"), (2, "código"), (3, "redactar"), (4, "pulir"))],
        _n(x + 170, y + 170, x + 340, y + 202, "Abortar o reintentar", "bloqueo"),
        flecha((x + _centro(2), m + 18), (x + _centro(2), y + 170), color=CORAL, punteada=True),
    )


def _paralelo(x, y):
    m = y + 122
    ramas = [y + 74, y + 122, y + 170]
    return VGroup(
        _n(x + 16, m - 18, x + 104, m + 18, "Entrada", "io"),
        *[_n(x + 150, s - 17, x + 300, s + 17, n, "llm")
          for s, n in zip(ramas, ("Seguridad", "Lógica", "Rendimiento"))],
        _s(x + 346, m - 24, x + 466, m + 24, "Agregador", "modelo o código", "control"),
        _n(x + 496, m - 18, x + 592, m + 18, "Resultado", "io"),
        *[flecha((x + 104, m), (x + 127, m), (x + 127, s), (x + 150, s)) for s in ramas],
        *[flecha((x + 300, s), (x + 323, s), (x + 323, m), (x + 346, m)) for s in ramas],
        flecha((x + 466, m), (x + 496, m)),
        etiqueta("fan-out", x + 127, y + 202, relleno=TARJETA, tam=12),
        etiqueta("fan-in", x + 323, y + 202, relleno=TARJETA, tam=12),
    )


def _orquestador(x, y):
    m = y + 132
    ramas = [y + 84, y + 132, y + 180]
    return VGroup(
        _n(x + 8, m - 18, x + 72, m + 18, "Tarea", "io"),
        _s(x + 98, m - 24, x + 228, m + 24, "Orquestador", "planifica", "control"),
        _n(x + 268, ramas[0] - 17, x + 388, ramas[0] + 17, "Trabajador 1", "llm"),
        _n(x + 268, ramas[1] - 17, x + 388, ramas[1] + 17, "Trabajador 2", "llm"),
        _n(x + 268, ramas[2] - 17, x + 388, ramas[2] + 17, "Trabajador N…", "llm",
           punteado=True),
        _n(x + 428, m - 20, x + 540, m + 20, "Sintetizador", "control"),
        _n(x + 562, m - 18, x + 604, m + 18, "Fin", "io"),
        flecha((x + 72, m), (x + 98, m)),
        *[flecha((x + 228, m), (x + 248, m), (x + 248, s), (x + 268, s)) for s in ramas],
        *[flecha((x + 388, s), (x + 408, s), (x + 408, m), (x + 428, m)) for s in ramas],
        flecha((x + 540, m), (x + 562, m)),
        flecha((x + 484, m - 20), (x + 484, y + 50), (x + 163, y + 50), (x + 163, m - 24),
               color=GRIS, punteada=True),
        etiqueta("¿falta algo? replanifica", x + 324, y + 50, relleno=TARJETA, tam=12),
    )


def _evaluador(x, y):
    m = y + 100
    return VGroup(
        _n(x + 8, m - 18, x + 78, m + 18, "Tarea", "io"),
        _n(x + 106, m - 22, x + 226, m + 22, "Generador", "llm"),
        _n(x + 254, m - 18, x + 354, m + 18, "Borrador", "io"),
        _s(x + 382, m - 24, x + 502, m + 24, "Evaluador", "rúbrica o tests", "control"),
        _n(x + 530, m - 18, x + 604, m + 18, "Salida", "io"),
        flecha((x + 78, m), (x + 106, m)),
        flecha((x + 226, m), (x + 254, m)),
        flecha((x + 354, m), (x + 382, m)),
        flecha((x + 502, m), (x + 530, m)),
        flecha((x + 442, m + 24), (x + 442, m + 76), (x + 166, m + 76), (x + 166, m + 22),
               color=CORAL, punteada=True),
        etiqueta("feedback, máximo N vueltas", x + 304, m + 76, color=CORAL, relleno=TARJETA,
                 tam=12),
        etiqueta("pasa", x + 516, m - 40, color=VERDE_OSCURO, relleno=TARJETA, tam=12),
    )


def _bucle(x, y):
    m = y + 122
    return VGroup(
        _n(x + 24, m - 18, x + 104, m + 18, "Tarea", "io"),
        _s(x + 150, m - 26, x + 300, m + 26, "Modelo", "decide la acción", "llm"),
        _s(x + 420, m - 26, x + 584, m + 26, "Herramientas", "API, datos, código",
           "herramienta"),
        _n(x + 150, y + 182, x + 300, y + 210, "Respuesta final", "io"),
        flecha((x + 104, m), (x + 150, m)),
        flecha((x + 300, m - 13), (x + 420, m - 13)),
        flecha((x + 420, m + 13), (x + 300, m + 13)),
        flecha((x + 225, m + 26), (x + 225, y + 182)),
        etiqueta("acción", x + 360, m - 13, relleno=TARJETA, tam=12),
        etiqueta("resultado", x + 360, m + 13, relleno=TARJETA, tam=12),
        etiqueta("el sistema pone límites: pasos, tiempo, coste, permisos", x + 304, y + 68,
                 color=CORAL_OSCURO, relleno=TARJETA, tam=12),
    )


def _humano(x, y):
    m = y + 96
    abajo = y + 177
    return VGroup(
        _s(x + 16, m - 22, x + 110, m + 22, "Agente", "propone", "llm"),
        _n(x + 150, m - 18, x + 250, m + 18, "¿Riesgo?", "control"),
        _n(x + 330, m - 18, x + 450, m + 18, "Ejecutar", "herramienta"),
        _n(x + 490, m - 18, x + 592, m + 18, "Resultado", "io"),
        _n(x + 140, abajo - 17, x + 310, abajo + 17, "Cola de aprobación", "guardrail"),
        _n(x + 350, abajo - 17, x + 450, abajo + 17, "Humano", "humano"),
        flecha((x + 110, m), (x + 150, m)),
        flecha((x + 250, m), (x + 330, m)),
        flecha((x + 450, m), (x + 490, m)),
        flecha((x + 200, m + 18), (x + 200, abajo - 17), color=CORAL),
        flecha((x + 310, abajo), (x + 350, abajo)),
        flecha((x + 400, abajo - 17), (x + 400, m + 18), color=MORADO),
        flecha((x + 400, abajo + 17), (x + 400, y + 212), (x + 63, y + 212), (x + 63, m + 22),
               color=CORAL, punteada=True),
        etiqueta("bajo", x + 290, m, relleno=TARJETA, tam=12),
        etiqueta("alto", x + 200, m + 42, color=CORAL, relleno=TARJETA, tam=12),
        etiqueta("aprueba", x + 400, m + 42, color=MORADO, relleno=TARJETA, tam=12),
        etiqueta("rechaza: el agente replanifica", x + 232, y + 212, color=CORAL,
                 relleno=TARJETA, tam=12),
    )


def _memoria(x, y):
    m = y + 118
    return VGroup(
        _s(x + 206, y + 30, x + 376, y + 72, "Compactador", "resume si pasa de N tokens",
           "control"),
        _s(x + 16, m - 30, x + 186, m + 30, "Corto plazo", "historial + resumen",
           "herramienta"),
        _n(x + 236, m - 24, x + 346, m + 24, "Agente", "llm"),
        _s(x + 416, m - 30, x + 592, m + 30, "Largo plazo", "vector o KV store",
           "herramienta"),
        _s(x + 416, y + 168, x + 592, y + 212, "Guardrail de escritura", "¿hecho fiable?",
           "guardrail"),
        flecha((x + 206, y + 51), (x + 101, y + 51), (x + 101, m - 30), color=GRIS),
        flecha((x + 186, m), (x + 236, m)),
        flecha((x + 416, m), (x + 346, m)),
        flecha((x + 291, m + 24), (x + 291, y + 190), (x + 416, y + 190)),
        flecha((x + 504, y + 168), (x + 504, m + 30)),
        etiqueta("compacta", x + 150, y + 51, relleno=TARJETA, tam=12),
        etiqueta("recupera k", x + 504, m - 48, relleno=TARJETA, tam=12),
        etiqueta("hechos nuevos", x + 352, y + 190, relleno=TARJETA, tam=12),
    )


# --- Las fichas ---------------------------------------------------------------------------

# clave: (lección, nombre, qué es, diagrama, úsalo cuando, error típico). El número del patrón
# es el de su lección: 4.1 es el 01.
FICHAS = {
    "router": (
        "4.1", "Router", "Clasifica la petición y la envía al especialista adecuado",
        _router, "Hay categorías claras", "Obligarlo a elegir sin información"),
    "guardrail_entrada": (
        "4.2", "Guardrails de entrada", "Trata lo que llega de afuera como datos no confiables",
        _guardrail_entrada, "Algo de afuera puede cambiar lo que hace",
        "Confiar en una frase del prompt"),
    "guardrail_salida": (
        "4.3", "Guardrails de salida", "Valida la respuesta antes de mostrarla o actuar",
        _guardrail_salida, "La respuesta llega a un usuario o a otro sistema",
        "Revisar solo el formato"),
    "cadena": (
        "4.4", "Prompt chaining", "Parte una tarea grande en pasos pequeños que se revisan",
        _cadena, "Conoces los pasos de antemano", "No revisar entre un paso y otro"),
    "paralelo": (
        "4.5", "Paralelización", "Corre tareas independientes a la vez y junta los resultados",
        _paralelo, "Las tareas no dependen entre sí", "Más llamadas sin medir el beneficio"),
    "orquestador": (
        "4.6", "Orquestador y trabajadores", "Divide el trabajo sobre la marcha y lo reparte",
        _orquestador, "Las subtareas dependen del pedido", "Darles todo el contexto a todos"),
    "evaluador": (
        "4.7", "Evaluador-optimizador", "Genera, evalúa con criterios claros y corrige lo que falla",
        _evaluador, "Puedes decir qué significa aprobar", "Un bucle sin límite de vueltas"),
    "bucle": (
        "4.8", "Bucle agéntico con herramientas",
        "El modelo elige la acción, mira el resultado y sigue",
        _bucle, "No puedes fijar los pasos de antemano",
        "Herramientas ambiguas o muy poderosas"),
    "humano": (
        "4.9", "Human in the loop", "Lo que tiene alto impacto lo aprueba una persona",
        _humano, "La acción cuesta dinero o no se puede deshacer",
        "Permitir lo que aún no se clasificó"),
    "memoria": (
        "4.10", "Memoria", "Decide qué recordar, por cuánto tiempo y para qué",
        _memoria, "Hay relaciones largas con el usuario", "Tantos recuerdos que se vuelven ruido"),
}

BLOQUE = "patrones"
# La tarjeta va de lado a lado y cada diagrama se escala hasta llenar su hueco (sobre la
# leyenda), centrado. Sin contador de patrón ni frases debajo (pedido así).
XC0, XC1, Y0, Y1 = 96, 1344, 186, 680
HUECO = (XC0 + 60, Y0 + 30, XC1 - 60, Y1 - 18)
ESCALA_MAX = 2.2
Y_LEYENDA = Y1 + 22


def _leyenda(partes):
    """La leyenda del diagrama, con los tipos de caja que usa y en el orden de TIPOS."""
    usados = {getattr(p, "tipo", None) for p in partes}
    return VGroup(discontinua(XC0 + 28, Y1 + 2, XC1 - 28, Y1 + 2, GRIS_CLARO, grosor=1.2),
                  leyenda([t for t in TIPOS if t in usados], XC0 + 28, Y_LEYENDA))


def _encajar(partes):
    """Escala el diagrama hasta llenar HUECO, sin pasar de ESCALA_MAX, y lo centra en él."""
    x0, y0, x1, y1 = HUECO
    escala = min((x1 - x0) * U / partes.width, (y1 - y0) * U / partes.height, ESCALA_MAX)
    partes.scale(escala).move_to(P((x0 + x1) / 2, (y0 + y1) / 2))


def ficha(clave):
    """La diapositiva de un patrón de FICHAS."""
    numero, nombre, dibujo = FICHAS[clave][0], FICHAS[clave][1], FICHAS[clave][3]

    def construir(scene):
        scene.marco.ir(BLOQUE, numero)
        partes = dibujo(0, 0)
        marco = VGroup(
            tarjeta(XC0, Y0, XC1, Y_LEYENDA + 24, radio=14, borde=GRIS_CLARO, grosor=1.2),
            _leyenda(partes),
        )
        _encajar(partes)

        scene.play(teclear(titulo(nombre)), run_time=0.6)
        scene.play(FadeIn(marco, shift=UP * 0.15), run_time=0.5)
        scene.play(LaggedStart(*[FadeIn(p, shift=UP * 0) for p in partes], lag_ratio=0.12),
                   run_time=1.6)

    return construir
