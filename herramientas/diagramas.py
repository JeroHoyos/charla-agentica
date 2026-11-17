# /// script
# dependencies = ["matplotlib"]
# ///
"""Dibuja los diagramas de los notebooks en `practica/assets/diagramas/` (un PNG por concepto),
con los colores de las diapositivas: el modelo en cian, el control en blanco, los guardrails en
coral, las herramientas en gris y la entrada y la salida solo con borde.

Cada diagrama es una función de DIAGRAMAS. Para ponerlo en un notebook, agrega en su celda de
texto una línea `<img src="assets/diagramas/NOMBRE.png" width="760"/>`.

Uso: uv run herramientas/diagramas.py"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Arc, Ellipse, FancyBboxPatch, Polygon, Rectangle

RAIZ = Path(__file__).parent.parent
SALIDA = RAIZ / "practica" / "assets" / "diagramas"
FUENTES = RAIZ / "presentacion" / "assets" / "fonts"

FONDO, BORDE = "#0c1f2a", "#2b4b5b"
TINTA, OSCURO, GRIS, GRIS_LINEA = "#f4f8fa", "#0c1f2a", "#9db4be", "#8fa7b1"
CIAN, CIAN_SUAVE = "#2ac3d8", "#134350"
CORAL, CORAL_SUAVE, CORAL_CLARO = "#e2725b", "#3b3135", "#f08a75"
ORO, VERDE, LILA, LILA_SUAVE = "#cca755", "#4ad1a6", "#ab95f2", "#2f3956"

# Por tipo de caja: relleno, borde, texto, subtexto y su nombre en la leyenda.
TIPOS = {
    "io": (FONDO, TINTA, TINTA, GRIS, "Entrada o salida"),
    "llm": (CIAN, CIAN, OSCURO, OSCURO, "Modelo o agente"),
    "control": (TINTA, TINTA, OSCURO, "#4d6b78", "Control (tu código)"),
    "guardrail": (CORAL_SUAVE, CORAL, TINTA, CORAL_CLARO, "Guardrail"),
    "bloqueo": (CORAL, CORAL, OSCURO, OSCURO, "Bloqueo"),
    "herramienta": ("#1f3f4e", GRIS_LINEA, TINTA, GRIS, "Herramienta o datos"),
    "humano": (LILA_SUAVE, LILA, TINTA, LILA, "Persona"),
}
ANCHO = 960
PT = 0.72  # una unidad del lienzo en puntos tipográficos (el lienzo va a 100 unidades por pulgada)


def _fuente(archivo):
    return FontProperties(fname=str(FUENTES / archivo))


NOMBRE, TEXTO, MONO = (_fuente(f) for f in ("Lexend-SemiBold.ttf", "Lexend-Regular.ttf",
                                            "JetBrainsMono-Medium.ttf"))


class Diagrama:
    """Un lienzo de 960 de ancho (y hacia abajo). Las cajas se nombran con una clave y las
    flechas van de una clave a otra."""

    def __init__(self, alto, leyenda=True):
        self.leyenda = leyenda
        self.alto = alto + (62 if leyenda else 14)  # la leyenda va en una franja al pie
        self.fig = plt.figure(figsize=(ANCHO / 100, self.alto / 100), dpi=200)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, ANCHO)
        self.ax.set_ylim(self.alto, 0)
        self.ax.axis("off")
        self.cajas, self.usados = {}, []
        self._redonda(2, 2, ANCHO - 2, self.alto - 2, FONDO, BORDE, radio=16, grosor=1.5)

    # --- piezas -----------------------------------------------------------------------------

    def _redonda(self, x0, y0, x1, y1, relleno, borde, radio=10, grosor=1.6, punteado=False):
        self.ax.add_patch(FancyBboxPatch(
            (x0, y0), x1 - x0, y1 - y0, boxstyle=f"round,pad=0,rounding_size={radio}",
            fc=relleno, ec=borde, lw=grosor * PT, ls=(0, (4, 3)) if punteado else "-"))

    def texto(self, contenido, x, y, tam=13, color=TINTA, fuente=TEXTO, alinear="center",
              fondo=None):
        caja = {"fc": fondo, "ec": "none", "pad": 2.5} if fondo else None
        self.ax.text(x, y, contenido, fontsize=tam * PT, color=color, fontproperties=fuente,
                     ha=alinear, va="center", bbox=caja)

    def rotulo(self, contenido, x, y, color=CIAN):
        """Un rótulo en mayúsculas, como el nombre de una fila."""
        self.texto(contenido.upper(), x, y, 11, color, MONO, "left")

    def nodo(self, clave, x, y, nombre, sub=None, tipo="io", w=150, h=54, punteado=False):
        """Una caja centrada en (x, y) con su nombre y, si la trae, una línea de detalle."""
        relleno, borde, color, color_sub, _ = TIPOS[tipo]
        self._redonda(x - w / 2, y - h / 2, x + w / 2, y + h / 2, relleno, borde,
                      punteado=punteado)
        self.texto(nombre, x, y - (8 if sub else 0), 14.5, color, NOMBRE)
        if sub:
            self.texto(sub, x, y + 11, 11, color_sub)
        self.cajas[clave] = (x, y, w, h)
        if tipo not in self.usados:
            self.usados.append(tipo)

    def base(self, clave, x, y, w=56, h=40):
        """El cilindro de una base de datos, centrado en (x, y)."""
        relleno, borde, *_ = TIPOS["herramienta"]
        ry, lw = h / 7, 1.6 * PT
        arriba, abajo = y - h / 2 + ry, y + h / 2 - ry
        self.ax.add_patch(Ellipse((x, abajo), w, 2 * ry, fc=relleno, ec=borde, lw=lw))
        self.ax.add_patch(Rectangle((x - w / 2, arriba), w, abajo - arriba, fc=relleno, ec="none"))
        self.ax.plot([x - w / 2] * 2, [arriba, abajo], color=borde, lw=lw)
        self.ax.plot([x + w / 2] * 2, [arriba, abajo], color=borde, lw=lw)
        self.ax.add_patch(Arc((x, y), w, 2 * ry, theta1=0, theta2=180, ec=borde, lw=lw))
        self.ax.add_patch(Ellipse((x, arriba), w, 2 * ry, fc=relleno, ec=borde, lw=lw))
        self.cajas[clave] = (x, y, w, h)
        if "herramienta" not in self.usados:
            self.usados.append("herramienta")

    def nota(self, contenido, x, y, w, color=CORAL):
        """Una franja punteada con una advertencia o una regla."""
        self._redonda(x - w / 2, y - 18, x + w / 2, y + 18, CORAL_SUAVE if color == CORAL
                      else CIAN_SUAVE, color, punteado=True)
        self.texto(contenido, x, y, 12.5, TINTA, NOMBRE)

    def barra(self, x0, y, x1, contenido, relleno, color=OSCURO, h=40, borde=None):
        """Un tramo de una barra horizontal, con su texto adentro."""
        self._redonda(x0, y - h / 2, x1, y + h / 2, relleno, borde or relleno, radio=6)
        self.texto(contenido, (x0 + x1) / 2, y, 12, color, NOMBRE)

    # --- flechas ----------------------------------------------------------------------------

    def punto(self, clave, lado, d=0):
        """El punto medio de un lado de la caja (l, r, t, b), corrido `d` a lo largo del lado."""
        x, y, w, h = self.cajas[clave]
        return {"l": (x - w / 2, y + d), "r": (x + w / 2, y + d),
                "t": (x + d, y - h / 2), "b": (x + d, y + h / 2)}[lado]

    def ruta(self, *puntos, color=TINTA, punteada=False, etiqueta=None, en=None):
        """Una flecha en codos por `puntos`, con la punta en el último."""
        (xa, ya), (xb, yb) = puntos[-2], puntos[-1]
        largo = max(abs(xb - xa) + abs(yb - ya), 1)
        ux, uy = (xb - xa) / largo, (yb - ya) / largo
        base = (xb - ux * 10, yb - uy * 10)
        xs, ys = zip(*puntos[:-1], base)
        self.ax.plot(xs, ys, color=color, lw=1.7 * PT, ls=(0, (4, 3)) if punteada else "-",
                     solid_capstyle="butt", solid_joinstyle="miter")
        self.ax.add_patch(Polygon([(xb, yb), (base[0] - uy * 5, base[1] + ux * 5),
                                   (base[0] + uy * 5, base[1] - ux * 5)], fc=color, ec=color,
                                  lw=0))
        if etiqueta:
            x, y = en or self._medio(puntos)
            self.texto(etiqueta, x, y, 10.5, GRIS if color == TINTA else color, MONO,
                       fondo=FONDO)

    @staticmethod
    def _medio(puntos):
        """El centro del tramo más largo de la ruta: ahí cabe su etiqueta."""
        a, b = max(zip(puntos, puntos[1:]),
                   key=lambda t: abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]))
        return (a[0] + b[0]) / 2, (a[1] + b[1]) / 2

    def flecha(self, a, b, d=0, **kw):
        """De la caja `a` a la caja `b`, de lado a lado; si no están a la misma altura, con un
        codo a mitad de camino."""
        derecha = self.cajas[b][0] > self.cajas[a][0]
        (x0, y0), (x1, y1) = self.punto(a, "r" if derecha else "l", d), self.punto(
            b, "l" if derecha else "r", d)
        if abs(y0 - y1) < 1:
            return self.ruta((x0, y0), (x1, y1), **kw)
        medio = (x0 + x1) / 2
        return self.ruta((x0, y0), (medio, y0), (medio, y1), (x1, y1), **kw)

    def baja(self, a, b, d=0, **kw):
        """De la caja `a` a la caja `b`, de arriba abajo (o al revés si `b` está más arriba)."""
        abajo = self.cajas[b][1] > self.cajas[a][1]
        (x0, y0), (x1, y1) = self.punto(a, "b" if abajo else "t", d), self.punto(
            b, "t" if abajo else "b", d)
        if abs(x0 - x1) < 1:
            return self.ruta((x0, y0), (x1, y1), **kw)
        medio = (y0 + y1) / 2
        return self.ruta((x0, y0), (x0, medio), (x1, medio), (x1, y1), **kw)

    def fila(self, y, cajas, x0=110, x1=850, **kw):
        """Cajas repartidas de x0 a x1 a la altura `y`, con una flecha entre cada par. Cada
        caja es (clave, nombre, detalle, tipo)."""
        paso = (x1 - x0) / (len(cajas) - 1)
        for i, (clave, nombre, sub, tipo) in enumerate(cajas):
            self.nodo(clave, x0 + i * paso, y, nombre, sub, tipo, **kw)
        for (a, *_), (b, *_) in zip(cajas, cajas[1:]):
            self.flecha(a, b)

    # --- salida -----------------------------------------------------------------------------

    def _leyenda(self):
        y = self.alto - 30
        self.ax.plot([30, ANCHO - 30], [y - 24, y - 24], color=BORDE, lw=1.2 * PT,
                     ls=(0, (4, 3)))
        x = 30
        for tipo in [t for t in TIPOS if t in self.usados]:
            relleno, borde, *_, nombre = TIPOS[tipo]
            self._redonda(x, y - 6, x + 17, y + 6, relleno, borde, radio=3, grosor=1.2)
            self.texto(nombre, x + 25, y, 11, GRIS, alinear="left")
            x += 25 + 6.3 * len(nombre) + 26

    def guardar(self, nombre):
        if self.leyenda:
            self._leyenda()
        self.fig.savefig(SALIDA / f"{nombre}.png", transparent=True)
        plt.close(self.fig)


# --- Notebook 1: fundamentos ----------------------------------------------------------------


def mensajes():
    d = Diagrama(230)
    d.rotulo("La lista de mensajes", 60, 34)
    d.nodo("human", 170, 86, "Human", "lo que pide el usuario", w=220)
    d.nodo("previa", 170, 166, "AI", "lo que ya respondió", w=220)
    d.nodo("modelo", 520, 126, "Modelo", "lee toda la lista", "llm", w=170, h=64)
    d.nodo("ai", 800, 126, "AI", "la respuesta", w=170)
    d.flecha("human", "modelo")
    d.flecha("previa", "modelo")
    d.flecha("modelo", "ai")
    d.texto("Cada mensaje lleva su rol. La respuesta se agrega a la lista para la siguiente "
            "llamada.", 480, 214, 12, GRIS)
    return d


def temperatura():
    d = Diagrama(270, leyenda=False)
    d.rotulo("Probabilidad del siguiente token", 60, 34)
    for i, (token, p) in enumerate((("hogar", 62), ("casa", 25), ("nido", 9), ("cueva", 4))):
        y = 74 + 44 * i
        d.texto(token, 118, y, 13, TINTA, MONO, "right")
        d.barra(134, y, 134 + p * 4.6, "", CIAN if i < 3 else BORDE, h=26)
        d.texto(f"{p} %", 146 + p * 4.6, y, 12, GRIS, alinear="left")
    d.ax.plot([60, 470], [184, 184], color=CORAL, lw=1.5 * PT, ls=(0, (4, 3)))
    d.texto("top_p = 0.95: lo de abajo no entra al sorteo", 268, 240, 11, CORAL_CLARO, MONO)
    d.nodo("cero", 730, 84, "Temperatura 0", "casi siempre «hogar»", "herramienta", w=300)
    d.nodo("uno", 730, 156, "Temperatura 1", "sortea según la probabilidad", "herramienta",
           w=300)
    d.nodo("dos", 730, 228, "Temperatura 2", "empareja las opciones: se arriesga",
           "herramienta", w=300)
    return d


def limite_tokens():
    d = Diagrama(230, leyenda=False)
    d.rotulo("Mucho razonamiento", 60, 36, CORAL_CLARO)
    d.barra(60, 76, 520, "razonamiento", ORO)
    d.barra(524, 76, 700, "respuesta…", CIAN)
    d.texto("se cortó: llegó al límite", 716, 76, 12, CORAL_CLARO, alinear="left")
    d.rotulo("Razonamiento mínimo", 60, 136)
    d.barra(60, 176, 150, "razona", ORO)
    d.barra(154, 176, 560, "respuesta completa", CIAN)
    d.texto("terminó sola", 716, 176, 12, VERDE, alinear="left")
    d.ax.plot([700, 700], [44, 208], color=TINTA, lw=1.5 * PT, ls=(0, (4, 3)))
    d.texto("límite de tokens", 700, 222, 11, GRIS, MONO)
    return d


def salida_estructurada():
    d = Diagrama(220)
    d.nodo("esquema", 400, 60, "Esquema", "campos y tipos", "control", w=180)
    d.fila(160, (("anuncio", "Anuncio", "texto libre", "io"),
                 ("modelo", "Modelo", "llena el esquema", "llm"),
                 ("ficha", "Ficha", "barrio, precio, alcobas", "control"),
                 ("codigo", "Tu código", "usa cada campo", "herramienta")), w=180)
    d.baja("esquema", "modelo")
    return d


# --- Notebook 2: system prompt, caché y herramientas -------------------------------------


def cache():
    d = Diagrama(260, leyenda=False)
    d.rotulo("Lo fijo arriba", 60, 36)
    d.barra(60, 78, 600, "system prompt y documentos", CIAN_SUAVE, TINTA, borde=CIAN)
    d.barra(606, 78, 700, "la hora", LILA_SUAVE, TINTA, borde=LILA)
    d.barra(706, 78, 830, "pregunta", FONDO, TINTA, borde=TINTA)
    d.texto("comienzo idéntico en cada llamada: sale de la caché y se cobra menos", 60, 118,
            12, CIAN, alinear="left")
    d.rotulo("La hora arriba", 60, 162, CORAL_CLARO)
    d.barra(60, 204, 154, "la hora", LILA_SUAVE, TINTA, borde=LILA)
    d.barra(160, 204, 700, "system prompt y documentos", CORAL_SUAVE, TINTA, borde=CORAL)
    d.barra(706, 204, 830, "pregunta", FONDO, TINTA, borde=TINTA)
    d.texto("el comienzo cambia cada minuto: todo se lee y se cobra completo", 60, 244, 12,
            CORAL_CLARO, alinear="left")
    return d


def bucle():
    d = Diagrama(280)
    d.nota("El modelo solo ve de cada herramienta: nombre, descripción y argumentos", 620, 44,
           560, CIAN)
    d.nodo("tarea", 130, 140, "Tarea", w=140)
    d.nodo("modelo", 440, 140, "Modelo", "decide la acción", "llm", w=190, h=66)
    d.nodo("herramientas", 790, 140, "Herramientas", "funciones de Python", "herramienta",
           w=230, h=66)
    d.nodo("final", 440, 244, "Respuesta final", w=190, h=46)
    d.flecha("tarea", "modelo")
    d.flecha("modelo", "herramientas", d=-14, etiqueta="petición")
    d.flecha("herramientas", "modelo", d=14, etiqueta="resultado")
    d.baja("modelo", "final", etiqueta="no pide más")
    return d


# --- Notebook 3: MCP y multimodal ----------------------------------------------------------


def mcp():
    d = Diagrama(250)
    d.nodo("agente", 150, 126, "Tu agente", "cliente MCP", "llm", w=180, h=64)
    d.nodo("servidor", 470, 126, "Servidor MCP", "calculadora de crédito", "control", w=220,
           h=64)
    for clave, y, nombre, sub in (("h", 52, "Herramientas", "funciones que el agente llama"),
                                  ("r", 126, "Recursos", "datos para leer"),
                                  ("p", 200, "Prompts", "instrucciones listas")):
        d.nodo(clave, 800, y, nombre, sub, "herramienta", w=240)
        d.flecha("servidor", clave)
    d.flecha("agente", "servidor", d=-12, etiqueta="pide")
    d.flecha("servidor", "agente", d=12, etiqueta="responde")
    d.texto("Un protocolo estándar: cualquier agente usa el servidor sin reescribirlo.", 310,
            226, 12, GRIS)
    return d


def multimodal():
    d = Diagrama(250)
    for clave, y, nombre, sub in (("t", 52, "Texto", "la pregunta"),
                                  ("i", 126, "Imagen", "el plano"),
                                  ("p", 200, "PDF", "el reglamento")):
        d.nodo(clave, 140, y, nombre, sub, w=170)
    d.nodo("mensaje", 420, 126, "Un mensaje", "una lista de bloques", "control", w=190, h=64)
    d.nodo("modelo", 660, 126, "Modelo", "lee todo junto", "llm", w=160, h=64)
    d.nodo("respuesta", 860, 126, "Respuesta", w=130)
    for clave in "tip":
        d.flecha(clave, "mensaje")
    d.flecha("mensaje", "modelo")
    d.flecha("modelo", "respuesta")
    return d


# --- El proyecto: las tablas de la base ------------------------------------------------------------------------


FILA_TABLA, CABEZA_TABLA = 22, 36


def _tabla(d, x0, y0, w, nombre, columnas, sello=None, color=TINTA):
    """Una tabla con sus columnas: (llave, columna, tipo). Devuelve la altura de cada columna."""
    alto = CABEZA_TABLA + FILA_TABLA * len(columnas) + 8
    d._redonda(x0, y0, x0 + w, y0 + alto, "#132c38", GRIS_LINEA, radio=8)
    d.ax.plot([x0, x0 + w], [y0 + CABEZA_TABLA, y0 + CABEZA_TABLA], color=GRIS_LINEA, lw=1.2 * PT)
    d.texto(nombre, x0 + 14, y0 + CABEZA_TABLA / 2, 14, TINTA, NOMBRE, "left")
    if sello:
        ancho = 5.2 * len(sello) + 12
        d._redonda(x0 + w - 8 - ancho, y0 - 7, x0 + w - 8, y0 + 7, color, color, radio=3, grosor=1)
        d.texto(sello.upper(), x0 + w - 8 - ancho / 2, y0, 8.5, OSCURO, MONO)
    filas = {}
    for i, (llave, columna, tipo) in enumerate(columnas):
        y = y0 + CABEZA_TABLA + 4 + FILA_TABLA * i + FILA_TABLA / 2
        if llave:
            d.texto(llave, x0 + 14, y, 9.5, ORO if llave == "PK" else CIAN, MONO, "left")
        d.texto(columna, x0 + 42, y, 11.5, TINTA, MONO, "left")
        d.texto(tipo, x0 + w - 14, y, 11, GRIS, alinear="right")
        filas[columna] = y
    return filas


def tablas():
    d = Diagrama(250, leyenda=False)
    _tabla(d, 120, 30, 320, "apartamentos", (
        ("PK", "codigo", "texto"), ("", "barrio", "texto"),
        ("", "precio", "pesos de venta"), ("", "alcobas", "número"), ("", "mascotas", "1 si las admite"),
        ("", "parqueadero", "1 si tiene")),
        "la lee recomendar", TINTA)
    _tabla(d, 540, 30, 300, "visitas", (
        ("PK", "id", "número"), ("", "codigo", "texto"), ("", "cliente", "texto"),
        ("", "fecha", "texto"), ("", "hora", "texto")),
        "la escribe agendar", LILA)
    return d


# --- Notebook 3: LangGraph ------------------------------------------------------------------


def grafo_minimo():
    d = Diagrama(210)
    d.nota("El estado viaja por todos los nodos, y cada nodo devuelve solo lo que cambia", 480, 44,
           620, CIAN)
    d.fila(140, (("inicio", "Inicio", None, "io"), ("saludar", "Saludar", "un nodo", "control"),
                 ("despedir", "Despedir", "otro nodo", "control"), ("fin", "Fin", None, "io")),
           x0=140, x1=820, w=160)
    d.texto("arista", 253, 124, 10.5, GRIS, MONO)
    return d


def publicar():
    d = Diagrama(260)
    d.fila(90, (("bienvenida", "Bienvenida", "dice qué datos dar", "control"),
                ("recibir", "Recibir", "el dueño responde", "humano"),
                ("decidir", "¿Falta algo?", "la arista revisa", "llm"),
                ("publicar", "Publicar", "escribe el anuncio", "llm"),
                ("fin", "Anuncio", None, "io")), x0=100, x1=860, w=160)
    d.nodo("pedir", 480, 210, "Pedir", "el modelo pregunta", "llm", w=160)
    d.baja("decidir", "pedir", color=CORAL, etiqueta="sí")
    d.ruta(d.punto("pedir", "l"), (290, 210), d.punto("recibir", "b"), color=LILA)
    d.texto("no", 575, 76, 10.5, GRIS, MONO, fondo=FONDO)
    d.texto("Después de pedir, se vuelve a recibir.", 590, 210, 12, GRIS, alinear="left")
    return d


def agente_grafo():
    d = Diagrama(230)
    d.fila(90, (("inicio", "Inicio", None, "io"), ("modelo", "Modelo", "¿pide algo?", "llm"),
                ("fin", "Fin", None, "io")), x0=140, x1=820, w=170, h=60)
    d.nodo("herramientas", 480, 186, "Herramientas", None, "herramienta", w=190, h=42)
    d.baja("modelo", "herramientas", d=30, etiqueta="sí")
    d.baja("herramientas", "modelo", d=-30)
    d.texto("no", 650, 76, 10.5, GRIS, MONO, fondo=FONDO)
    return d


# --- Notebook 4: los diez patrones ---------------------------------------------------------

FILA6 = {"x0": 85, "x1": 875, "w": 132}  # seis cajas en fila


def _abanico(d, origen, ramas, destino, x, w=210):
    """Tres cajas en columna entre `origen` y `destino`, con sus flechas."""
    for clave, y, nombre, sub in ramas:
        d.nodo(clave, x, y, nombre, sub, "llm", w=w)
        d.flecha(origen, clave)
        d.flecha(clave, destino)


def router():
    d = Diagrama(290)
    d.nodo("mensaje", 100, 126, "Mensaje", w=130)
    d.nodo("clasificar", 320, 126, "Clasificar", "elige el destino", "control", w=180, h=62)
    d.nodo("fin", 870, 126, "Respuesta", w=130)
    d.flecha("mensaje", "clasificar")
    _abanico(d, "clasificar", (("c", 52, "Compra", "crédito y escrituras"),
                               ("a", 126, "Arriendo", "requisitos y contrato"),
                               ("r", 200, "Reclamo", "registra el caso")), "fin", 620)
    d.nodo("persona", 620, 266, "Persona", "si no encaja", "humano", w=210, h=46)
    x, y = d.punto("clasificar", "b")
    d.ruta((x, y), (x, 266), d.punto("persona", "l"), color=LILA, punteada=True,
           etiqueta="otro")
    return d


def guardrail_entrada():
    d = Diagrama(250)
    d.fila(80, (("entrada", "Entrada", "del cliente", "io"),
                ("validar", "Validar", "con código", "guardrail"),
                ("clasificar", "Clasificar", "con un modelo", "guardrail"),
                ("separar", "Separar", "datos, no órdenes", "guardrail"),
                ("agente", "Agente", None, "llm")), **FILA6)
    d.nodo("bloquear", 380, 200, "Bloquear", "respuesta segura", "bloqueo", w=300)
    for clave in ("validar", "clasificar"):
        x, y = d.punto(clave, "b")
        d.ruta((x, y), (x, 173), color=CORAL, punteada=True)
    return d


def guardrail_salida():
    d = Diagrama(250)
    d.fila(80, (("modelo", "Modelo", "redacta", "llm"),
                ("revisar", "Revisar", "sin teléfonos", "guardrail"),
                ("cliente", "Cliente", None, "io")), x0=180, x1=780, w=170)
    d.nodo("reintentar", 400, 200, "Reintentar con el error", "máximo 3 intentos", "bloqueo",
           w=300)
    d.nodo("segura", 720, 200, "Respuesta segura", "si se acaban", "control", w=170)
    x, y = d.punto("revisar", "b")
    d.ruta((x, y), (x, 173), color=CORAL, punteada=True)
    xm, ym = d.punto("modelo", "b")
    d.ruta(d.punto("reintentar", "l"), (xm, 200), (xm, ym), color=CORAL, punteada=True,
           etiqueta="feedback")
    d.flecha("reintentar", "segura")
    return d


def secuencial():
    d = Diagrama(230)
    d.fila(80, (("aviso", "Aviso", None, "io"), ("extraer", "Extraer", "los datos", "llm"),
                ("gate", "Gate", "¿están todos?", "guardrail"),
                ("redactar", "Redactar", "50 palabras", "llm"), ("anuncio", "Anuncio", None, "io")),
           **FILA6)
    d.nodo("abortar", 480, 192, "Abortar", "no se redacta nada", "bloqueo", w=190)
    d.baja("gate", "abortar", color=CORAL, etiqueta="faltan datos")
    d.texto("El gate es código, no un modelo.", 760, 192, 12, GRIS)
    return d


def paralelo():
    d = Diagrama(250)
    d.nodo("hoja", 100, 126, "Hoja de vida", w=150)
    d.nodo("juntar", 650, 126, "Juntar", "suma los informes", "control", w=180, h=62)
    d.nodo("mejoras", 870, 126, "Mejoras", w=130)
    _abanico(d, "hoja", (("te", 52, "Técnico", "proyectos y habilidades"),
                         ("re", 126, "Redacción", "ortografía"),
                         ("fo", 200, "Formato", "orden y largo")), "juntar", 380)
    d.flecha("juntar", "mejoras")
    return d


def orquestador():
    d = Diagrama(270)
    d.nodo("pedido", 85, 126, "Pedido", w=120)
    d.nodo("planear", 285, 126, "Orquestador", "divide el pedido", "llm", w=190, h=62)
    d.nodo("sintetizar", 820, 126, "Respuestas", w=150)
    d.flecha("pedido", "planear")
    _abanico(d, "planear", (("w1", 52, "Worker", "subtarea 1"),
                            ("w2", 126, "Worker", "subtarea 2"),
                            ("w3", 200, "Worker", "subtarea 3")), "sintetizar", 555)
    d.texto("Send lanza un worker por subtarea, todos a la vez.", 480, 252, 12, GRIS)
    return d


def bucle_critico():
    d = Diagrama(230)
    d.fila(80, (("tema", "Ficha", None, "io"), ("escribir", "Generar", "el anuncio", "llm"),
                ("criticar", "Evaluar", "con la rúbrica", "control"),
                ("fin", "Anuncio", None, "io")), x0=110, x1=850, w=180, h=60)
    xc, yc = d.punto("criticar", "b")
    xe, ye = d.punto("escribir", "b")
    d.ruta((xc, yc), (xc, 172), (xe, 172), (xe, ye), color=CORAL, punteada=True,
           etiqueta="qué cambiar, máximo 4 vueltas")
    d.texto("aprobado", 721, 40, 10.5, VERDE, MONO)
    return d


def bucle_agentico():
    d = Diagrama(280)
    d.nota("El sistema controla: qué herramientas hay, sus permisos y cuántos pasos (5)", 560, 40,
           620)
    d.nodo("tarea", 120, 140, "Pregunta", w=140)
    d.nodo("modelo", 420, 140, "Modelo", "decide la acción", "llm", w=190, h=66)
    d.nodo("herramientas", 780, 140, "Herramientas", "buscar apartamentos",
           "herramienta", w=260, h=66)
    d.nodo("final", 420, 246, "Respuesta", w=190, h=46)
    d.flecha("tarea", "modelo")
    d.flecha("modelo", "herramientas", d=-14, etiqueta="acción")
    d.flecha("herramientas", "modelo", d=14, etiqueta="resultado")
    d.baja("modelo", "final", etiqueta="no pide más")
    return d


def humano():
    d = Diagrama(250)
    d.nodo("agente", 110, 80, "Agente", "propone la acción", "llm", w=170, h=60)
    d.nodo("riesgo", 340, 80, "¿Riesgo?", "agendar es alto", "control", w=180, h=60)
    d.nodo("ejecutar", 610, 80, "Ejecutar", "la herramienta", "herramienta", w=170)
    d.nodo("resultado", 860, 80, "Resultado", w=130)
    d.nodo("persona", 610, 200, "Persona", "aprueba o rechaza", "humano", w=230, h=60)
    d.flecha("agente", "riesgo")
    d.flecha("riesgo", "ejecutar", etiqueta="bajo")
    d.flecha("ejecutar", "resultado")
    x, y = d.punto("riesgo", "b")
    d.ruta((x, y), (x, 200), d.punto("persona", "l"), color=LILA, etiqueta="alto")
    d.baja("persona", "ejecutar", color=LILA, etiqueta="aprueba")
    return d


def memoria_largo_plazo():
    d = Diagrama(230)
    d.nodo("corto", 150, 90, "Corto plazo", "el historial", "herramienta", w=220, h=62)
    d.nodo("agente", 480, 90, "Agente", None, "llm", w=170, h=62)
    d.nodo("largo", 810, 90, "Largo plazo", "una ficha por cliente", "herramienta", w=220, h=62)
    d.flecha("corto", "agente", etiqueta="contexto")
    d.flecha("largo", "agente", etiqueta="recupera")
    xa, ya = d.punto("agente", "b")
    xl, yl = d.punto("largo", "b")
    d.ruta((xa, ya), (xa, 190), (xl, 190), (xl, yl), etiqueta="anota lo que dura")
    return d


# --- El proyecto: la app de proyecto_practica/ ----------------------------------------------

# Como las arquitecturas de ADK: carriles por etapa, una franja por ruta y un sello en cada tarjeta.
CARRIL, CARRIL_BORDE = "#112935", "#24404e"
TINTES = {"a": ("#13303c", "#2a5866"), "b": ("#2a2a31", "#5b3d3b"), "salida": ("#12302c", "#2c5b50")}
SELLOS = {"llm": CIAN, "control": TINTA, "guardrail": CORAL, "humano": LILA, "herramienta": GRIS_LINEA,
          "io": VERDE}


def _carril(d, x0, y0, x1, y1, titulo, tinte=None):
    relleno, borde = TINTES[tinte] if tinte else (CARRIL, CARRIL_BORDE)
    d._redonda(x0, y0, x1, y1, relleno, borde, radio=8, grosor=1.2)
    d.texto(titulo.upper(), x0 + 10, y0 + 15, 9.5, GRIS, MONO, "left")


def _tarjeta(d, clave, x, y, nombre, sub, tipo, sello, w=140, h=50):
    """Una caja con su sello arriba a la derecha, como las de ADK."""
    d.nodo(clave, x, y, nombre, sub, tipo, w=w, h=h)
    ancho = 5.2 * len(sello) + 12
    x1, arriba = x + w / 2 - 8, y - h / 2
    d._redonda(x1 - ancho, arriba - 7, x1, arriba + 7, SELLOS[tipo], SELLOS[tipo], radio=3, grosor=1)
    d.texto(sello.upper(), x1 - ancho / 2, arriba, 8.5, OSCURO, MONO)


def proyecto():
    d = Diagrama(624)
    # Los carriles: entrada, router, las tres rutas en franjas y las salidas
    _carril(d, 14, 14, 140, 620, "Entrada")
    _carril(d, 148, 14, 280, 620, "Router")
    _carril(d, 288, 14, 806, 262, "Ruta A: Recomendar (encuesta en loop)", "a")
    _carril(d, 288, 270, 806, 470, "Ruta B: Agendar", "b")
    _carril(d, 288, 478, 806, 620, "Ruta C: Ver un apartamento", "a")
    _carril(d, 814, 14, 946, 620, "Salidas", "salida")
    _tarjeta(d, "cliente", 77, 317, "Cliente", "un mensaje", "io", "chat", w=106)
    _tarjeta(d, "router", 214, 317, "Router", "elige 1 de 3", "control", "router", w=112)
    # Ruta A
    d.base("base_a", 547, 72)
    _tarjeta(d, "encuesta", 380, 145, "Encuesta", "llena lo que sabe", "llm", "loop")
    _tarjeta(d, "buscar", 547, 145, "Buscar", "cuenta condiciones", "control", "código")
    _tarjeta(d, "responder", 714, 145, "Responder", "frase y fichas", "llm", "modelo")
    _tarjeta(d, "preguntar", 380, 228, "Preguntar", "el cliente responde", "humano", "interrupt", h=46)
    # Ruta B
    d.base("base_b", 670, 304)
    _tarjeta(d, "sacar", 420, 380, "Sacar", "número, fecha y hora", "llm", "extraer")
    _tarjeta(d, "opciones", 670, 380, "Opciones", "reglas y fechas libres", "control", "interrupt")
    # Ruta C
    d.base("base_c", 670, 520)
    _tarjeta(d, "numeros", 420, 584, "Sacar", "los números", "llm", "extraer", h=46)
    _tarjeta(d, "fichas", 670, 584, "Fichas", "datos y foto", "control", "código", h=46)
    # Salidas
    _tarjeta(d, "recomendacion", 880, 145, "Recomienda", "fichas y fotos", "io", "salida a", w=116)
    _tarjeta(d, "visita", 880, 380, "Visita", "programada", "io", "salida b", w=116)
    _tarjeta(d, "sin_visita", 880, 442, "Sin visita", "no se guarda", "io", "salida b", w=116, h=44)
    _tarjeta(d, "ficha", 880, 584, "Ficha", "con su foto", "io", "salida c", w=116, h=46)
    # Las flechas
    d.flecha("cliente", "router")
    # El router se abre en el hueco entre carriles, para no cruzar Preguntar ni los títulos
    xr, yr = d.punto("router", "r")
    d.ruta((xr, yr), (284, yr), (284, 145), d.punto("encuesta", "l"))
    d.ruta((284, yr), (284, 380), d.punto("sacar", "l"))
    d.ruta((284, 380), (284, 584), d.punto("numeros", "l"))
    d.flecha("numeros", "fichas")
    d.flecha("fichas", "ficha")
    d.flecha("encuesta", "buscar")
    d.flecha("buscar", "responder")
    d.flecha("responder", "recomendacion")
    # Cada nodo que lee la base la tiene encima
    for base, nodo, dice in (("base_a", "buscar", "filas"), ("base_b", "opciones", "fechas"),
                             ("base_c", "fichas", "fila")):
        d.baja(base, nodo)
        x, y0 = d.punto(base, "b")
        d.texto(dice, x - 8, (y0 + d.punto(nodo, "t")[1]) / 2, 10.5, GRIS, MONO, "right")
    d.ruta(d.punto("encuesta", "b", -30), d.punto("preguntar", "t", -30), color=CORAL)
    d.texto("falta", 344, 186, 10.5, CORAL, MONO, "right")
    d.ruta(d.punto("preguntar", "t", 30), d.punto("encuesta", "b", 30), color=LILA)
    d.texto("hasta tener lo mínimo, máximo 3 veces", 465, 228, 11, GRIS, alinear="left")
    d.flecha("sacar", "opciones")
    d.flecha("opciones", "visita")
    # En Opciones el cliente puede cancelar
    xo, yo = d.punto("opciones", "b")
    d.ruta((xo, yo), (xo, 442), d.punto("sin_visita", "l"), color=CORAL, punteada=True)
    d.texto("cancelar o sin fecha", xo - 10, 430, 10.5, CORAL, MONO, "right")
    return d


DIAGRAMAS = {
    "mensajes": mensajes, "temperatura": temperatura, "limite_tokens": limite_tokens,
    "salida_estructurada": salida_estructurada, "cache": cache,
    "bucle": bucle, "mcp": mcp, "multimodal": multimodal,
    "grafo_minimo": grafo_minimo, "publicar": publicar, "agente_grafo": agente_grafo,
    "tablas": tablas, "router": router, "guardrail_entrada": guardrail_entrada,
    "guardrail_salida": guardrail_salida, "secuencial": secuencial, "paralelo": paralelo,
    "orquestador": orquestador, "bucle_critico": bucle_critico, "bucle_agentico": bucle_agentico,
    "humano": humano, "memoria_largo_plazo": memoria_largo_plazo, "proyecto": proyecto,
}


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, dibujar in DIAGRAMAS.items():
        dibujar().guardar(nombre)
        print(f"practica/assets/diagramas/{nombre}.png")


if __name__ == "__main__":
    main()
