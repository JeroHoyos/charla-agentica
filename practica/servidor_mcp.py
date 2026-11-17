"""Servidor MCP de la Inmobiliaria Señor Gato: la calculadora de crédito.

No hay que correrlo a mano: lo arranca el notebook 03."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("senor_gato")

TASA_ANUAL = 12.0  # % efectivo anual de referencia


@mcp.tool()
def cuota_credito(precio: int, cuota_inicial_pct: float = 30, anios: int = 20) -> dict:
    """Calcula la cuota mensual de un crédito hipotecario en pesos colombianos."""
    prestamo = precio * (1 - cuota_inicial_pct / 100)
    tasa_mes = (1 + TASA_ANUAL / 100) ** (1 / 12) - 1
    meses = anios * 12
    cuota = prestamo * tasa_mes / (1 - (1 + tasa_mes) ** -meses)
    return {"cuota_inicial": round(precio - prestamo), "prestamo": round(prestamo),
            "cuota_mensual": round(cuota), "meses": meses, "tasa_anual_pct": TASA_ANUAL}


@mcp.tool()
def gastos_de_cierre(precio: int) -> dict:
    """Estima en pesos los gastos de notaría, registro y beneficencia de una compra."""
    return {"minimo": round(precio * 0.015), "maximo": round(precio * 0.02)}


@mcp.resource("senor-gato://tasas")
def tasas() -> str:
    """Tasas de crédito hipotecario de los bancos aliados."""
    return ("Banco Nutibara: 11,8 % E.A.\n"
            "Banco La Montaña: 12,4 % E.A.\n"
            "Cooperativa Gatuna: 11,2 % E.A.")


@mcp.prompt()
def asesor_financiero(cliente: str) -> str:
    """Instrucciones para el asesor financiero de la inmobiliaria."""
    return f"""Eres el asesor financiero de la Inmobiliaria Señor Gato y atiendes a {cliente}.
    - Haz las cuentas con tus herramientas, nunca de memoria.
    - Escribe los valores en pesos con puntos de miles, por ejemplo $2.816.000.
    - Responde en pocas líneas."""


if __name__ == "__main__":
    mcp.run()
