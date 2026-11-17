# /// script
# dependencies = ["matplotlib"]
# ///
"""Dibuja cada apartamento de `proyecto_practica/inmobiliaria.sql` como una caricatura: la
fachada a la izquierda y el plano a la derecha. Sale de los datos de su fila: las alcobas, si
tiene parqueadero (un carro), si admite mascotas (un gato) y si es venta o arriendo (el letrero).

Uso: uv run herramientas/apartamentos.py"""

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon, Rectangle

RAIZ = Path(__file__).parent.parent
PROYECTO = RAIZ / "proyecto_practica"
SALIDA = PROYECTO / "public" / "apartamentos"
FUENTES = RAIZ / "presentacion" / "assets" / "fonts"
NOMBRE = FontProperties(fname=str(FUENTES / "Lexend-SemiBold.ttf"))
TEXTO = FontProperties(fname=str(FUENTES / "Lexend-Regular.ttf"))

TRAZO = "#2b2d42"
CIELO, PASTO, PAPEL = "#cdeffd", "#9bd770", "#fffaf0"
VIDRIO, PUERTA, TECHO = "#9fd8f5", "#a0522d", "#e2725b"
# Un color de fachada por barrio
FACHADAS = {"Laureles": "#f6c177", "El Poblado": "#c7a6f2", "Envigado": "#8fd3c1",
            "Sabaneta": "#f7a3a3", "Belén": "#f2d06b", "Robledo": "#9cc5f0"}
PISOS = {"Laureles": 5, "El Poblado": 8, "Envigado": 6, "Sabaneta": 7, "Belén": 5, "Robledo": 4}


def caja(ax, x, y, w, h, relleno, radio=6, grosor=3, **kw):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radio}",
                                fc=relleno, ec=TRAZO, lw=grosor, **kw))


def texto(ax, contenido, x, y, tam=14, fuente=TEXTO, color=TRAZO, **kw):
    ax.text(x, y, contenido, fontsize=tam, fontproperties=fuente, color=color,
            ha="center", va="center", **kw)


# La fachada

def nube(ax, x, y):
    for dx, dy, r in ((0, 0, 18), (22, 6, 22), (46, 0, 17)):
        ax.add_patch(Circle((x + dx, y + dy), r, fc="white", ec="none"))


def arbol(ax, x, y):
    ax.add_patch(Rectangle((x - 6, y), 12, 40, fc=PUERTA, ec=TRAZO, lw=3))
    ax.add_patch(Circle((x, y + 62), 34, fc="#5cb85c", ec=TRAZO, lw=3))


def carro(ax, x, y):
    caja(ax, x, y + 12, 96, 30, "#e63946", radio=10)
    caja(ax, x + 18, y + 36, 56, 24, "#e63946", radio=10)
    ax.add_patch(Rectangle((x + 26, y + 42), 18, 13, fc=VIDRIO, ec=TRAZO, lw=2))
    ax.add_patch(Rectangle((x + 50, y + 42), 18, 13, fc=VIDRIO, ec=TRAZO, lw=2))
    for rx in (x + 22, x + 74):
        ax.add_patch(Circle((rx, y + 12), 11, fc=TRAZO, ec=TRAZO))
        ax.add_patch(Circle((rx, y + 12), 4, fc="#dddddd", ec="none"))


def gato(ax, x, y):
    ax.add_patch(Ellipse((x, y + 18), 40, 34, fc="#ff9f43", ec=TRAZO, lw=3))
    ax.add_patch(Circle((x, y + 46), 16, fc="#ff9f43", ec=TRAZO, lw=3))
    for lado in (-1, 1):
        ax.add_patch(Polygon([(x + lado * 14, y + 52), (x + lado * 6, y + 60), (x + lado * 15, y + 68)],
                             fc="#ff9f43", ec=TRAZO, lw=3))
        ax.add_patch(Circle((x + lado * 6, y + 48), 2.6, fc=TRAZO))
    ax.plot([x + 18, x + 34, x + 30], [y + 10, y + 20, y + 34], color=TRAZO, lw=3, solid_capstyle="round")


def letrero(ax, apto, x, y):
    ax.add_patch(Rectangle((x + 77, 70), 6, y - 70, fc=PUERTA, ec="none"))  # el poste: el carro lo tapa
    caja(ax, x, y, 160, 62, "white", radio=8)
    negocio = "SE VENDE" if apto["negocio"] == "venta" else "SE ARRIENDA"
    texto(ax, negocio, x + 80, y + 42, 13, NOMBRE, "#d62828")
    precio = (f"{apto['precio'] / 1_000_000:,.0f} millones" if apto["negocio"] == "venta"
              else f"{apto['precio']:,} al mes").replace(",", ".")
    texto(ax, precio, x + 80, y + 18, 12)


def fachada(ax, apto):
    ax.add_patch(Rectangle((0, 0), 560, 520, fc=CIELO, ec="none"))
    ax.add_patch(Circle((500, 450), 34, fc="#ffd166", ec="none"))
    nube(ax, 50, 430)
    nube(ax, 300, 440)
    ax.add_patch(Rectangle((0, 0), 560, 70, fc=PASTO, ec="none"))

    pisos = PISOS.get(apto["barrio"], 5)
    alto_piso = min(52, 330 / pisos)
    x0, ancho, base = 150, 230, 70
    alto = pisos * alto_piso + 30
    caja(ax, x0, base, ancho, alto, FACHADAS.get(apto["barrio"], "#f6c177"), radio=4)
    ax.add_patch(Polygon([(x0 - 14, base + alto), (x0 + ancho + 14, base + alto),
                          (x0 + ancho - 10, base + alto + 26), (x0 + 10, base + alto + 26)],
                         fc=TECHO, ec=TRAZO, lw=3))
    for piso in range(1, pisos):
        for col in range(3):
            caja(ax, x0 + 22 + col * 70, base + 18 + piso * alto_piso, 46, alto_piso * 0.55, VIDRIO, radio=3, grosor=2.5)
    caja(ax, x0 + ancho / 2 - 24, base, 48, alto_piso * 0.9, PUERTA, radio=4)
    ax.add_patch(Circle((x0 + ancho / 2 + 14, base + alto_piso * 0.45), 3, fc="#ffd166", ec=TRAZO, lw=1.5))

    arbol(ax, 70, 70)
    letrero(ax, apto, 392, 200)
    if apto["parqueadero"]:
        carro(ax, 410, 52)
    if apto["mascotas"]:
        gato(ax, 110, 48)
    texto(ax, "FACHADA", 280, 495, 13, NOMBRE)


# El plano

def cama(ax, x, y, w, h):
    caja(ax, x, y, w, h, "#ffffff", radio=4, grosor=2.5)
    caja(ax, x + 4, y + h - 18, w - 8, 14, "#ffc8dd", radio=4, grosor=2)


def cuarto(ax, x, y, w, h, nombre, relleno):
    ax.add_patch(Rectangle((x, y), w, h, fc=relleno, ec=TRAZO, lw=5))
    texto(ax, nombre, x + w / 2, y + 16, 12, NOMBRE)


def plano(ax, apto):
    ax.add_patch(Rectangle((0, 0), 560, 520, fc=PAPEL, ec="none"))
    x0, y0, ancho, alto = 30, 40, 500, 420
    alcobas = apto["alcobas"]

    # Arriba, una fila de alcobas
    alto_alcoba = 170
    w = ancho / alcobas
    for i in range(alcobas):
        x = x0 + i * w
        cuarto(ax, x, y0 + alto - alto_alcoba, w, alto_alcoba, f"Alcoba {i + 1}", "#fde2e4")
        cama(ax, x + w / 2 - 34, y0 + alto - 120, 68, 90)

    # Abajo: sala, cocina y baño
    abajo = alto - alto_alcoba
    w_sala, w_cocina = ancho * 0.52, ancho * 0.26
    cuarto(ax, x0, y0, w_sala, abajo, "Sala comedor", "#e9f5db")
    caja(ax, x0 + 30, y0 + 120, 130, 40, "#90be6d", radio=10, grosor=2.5)  # sofá
    ax.add_patch(Circle((x0 + w_sala - 60, y0 + 140), 30, fc="#ddb892", ec=TRAZO, lw=2.5))  # mesa

    cuarto(ax, x0 + w_sala, y0, w_cocina, abajo, "Cocina", "#fff1c1")
    for i in range(2):
        for j in range(2):
            ax.add_patch(Circle((x0 + w_sala + 38 + i * 32, y0 + 130 + j * 32), 11, fc="white", ec=TRAZO, lw=2.5))

    x_bano = x0 + w_sala + w_cocina
    cuarto(ax, x_bano, y0, ancho - w_sala - w_cocina, abajo, "Baño", "#d7f0ff")
    ax.add_patch(Ellipse((x_bano + 62, y0 + 140), 34, 44, fc="white", ec=TRAZO, lw=2.5))

    texto(ax, "PLANO", 280, 495, 13, NOMBRE)


def dibujar(apto):
    fig = plt.figure(figsize=(11.2, 5.6), dpi=110)
    fig.patch.set_facecolor("white")
    for i, panel in enumerate((fachada, plano)):
        ax = fig.add_axes([0.01 + i * 0.5, 0.02, 0.48, 0.86])
        ax.set_xlim(0, 560)
        ax.set_ylim(0, 520)
        ax.axis("off")
        panel(ax, apto)
        ax.add_patch(FancyBboxPatch((0, 0), 560, 520, boxstyle="round,pad=0,rounding_size=18",
                                    fc="none", ec=TRAZO, lw=4))
    detalles = [f"{apto['alcobas']} alcoba{'s' if apto['alcobas'] > 1 else ''}",
                "parqueadero" if apto["parqueadero"] else "sin parqueadero",
                "admite mascotas" if apto["mascotas"] else "sin mascotas"]
    fig.text(0.02, 0.94, f"{apto['codigo']}, {apto['barrio']}", fontsize=22, fontproperties=NOMBRE, color=TRAZO)
    fig.text(0.98, 0.94, ", ".join(detalles), fontsize=14, fontproperties=TEXTO, color=TRAZO, ha="right")
    fig.savefig(SALIDA / f"{apto['codigo']}.png")
    plt.close(fig)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    base = sqlite3.connect(":memory:")
    base.row_factory = sqlite3.Row
    base.executescript((PROYECTO / "inmobiliaria.sql").read_text(encoding="utf-8"))
    for fila in base.execute("SELECT * FROM apartamentos"):
        dibujar(dict(fila))
        print(f"proyecto_practica/public/apartamentos/{fila['codigo']}.png")


if __name__ == "__main__":
    main()
