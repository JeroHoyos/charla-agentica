"""La base de datos y las reglas.

La base es SQLite, que viene con Python. Cada vez que arranca, `inmobiliaria.sql` la vuelve a
crear en `inmobiliaria.db`.

Todo lo que se puede revisar con código se revisa aquí, sin modelo: qué condiciones cumple cada
apartamento y las reglas de una visita.
"""
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).parent
BASE = AQUI / "inmobiliaria.db"


def conectar():
    conexion = sqlite3.connect(BASE)
    conexion.row_factory = sqlite3.Row  # cada fila se puede leer como un diccionario
    return conexion


with conectar() as conexion:
    conexion.executescript((AQUI / "inmobiliaria.sql").read_text(encoding="utf-8"))


def filas(consulta: str, *parametros) -> list[dict]:
    """Corre una consulta y devuelve cada fila como un diccionario."""
    with conectar() as conexion:
        return [dict(fila) for fila in conexion.execute(consulta, parametros)]


# Recomendar

def condiciones(apartamento: dict, encuesta: dict) -> dict[str, bool]:
    """Revisa cada cosa que pidió el cliente. Lo que no dijo (barrio, mascotas o parqueadero)
    no se revisa."""
    revision = {
        "presupuesto": apartamento["precio"] <= encuesta["presupuesto"],
        "alcobas": apartamento["alcobas"] >= encuesta["alcobas"],
        "barrio": apartamento["barrio"].lower() == (encuesta["barrio"] or "").lower(),
        "mascotas": apartamento["mascotas"] or not encuesta["mascotas"],
        "parqueadero": apartamento["parqueadero"] or not encuesta["parqueadero"],
    }
    return {condicion: cumple for condicion, cumple in revision.items() if encuesta[condicion] is not None}


def buscar(encuesta: dict, cuantos: int = 3) -> list[dict]:
    """Los apartamentos, del que cumple más condiciones al que cumple menos. Si empatan, va
    primero el más barato. Cada uno dice qué le falta."""
    apartamentos = filas("SELECT * FROM apartamentos WHERE negocio = ?", encuesta["negocio"])
    for apartamento in apartamentos:
        revision = condiciones(apartamento, encuesta)
        apartamento["le_falta"] = [condicion for condicion, cumple in revision.items() if not cumple]

    apartamentos.sort(key=lambda apartamento: (len(apartamento["le_falta"]), apartamento["precio"]))
    return apartamentos[:cuantos]


# Agendar

def problemas_de_la_visita(codigo: str, fecha: date, hora: str) -> list[str]:
    """Las reglas de una visita. Devuelve la lista vacía si las cumple todas."""
    cuando = datetime.combine(fecha, datetime.strptime(hora, "%H:%M").time())

    problemas = []
    if not filas("SELECT 1 FROM apartamentos WHERE codigo = ?", codigo):
        problemas.append(f"El {codigo} no existe.")
    if cuando < datetime.now() + timedelta(hours=24):
        problemas.append("Las visitas se piden con al menos 24 horas de anticipación.")
    if fecha.weekday() == 6:
        problemas.append("No hay visitas los domingos.")
    if not 8 <= cuando.hour < 18:
        problemas.append("Las visitas son entre las 8:00 y las 18:00.")
    if filas("SELECT 1 FROM visitas WHERE codigo = ? AND fecha = ? AND hora = ?", codigo, fecha.isoformat(), hora):
        problemas.append("Ese horario ya está ocupado.")
    return problemas


HORAS_DE_VISITA = ("09:00", "11:00", "15:00", "17:00")
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre")


def legible(fecha: date, hora: str) -> str:
    """date(2026, 11, 21), "10:00" -> "sábado 21 de noviembre a las 10:00"."""
    return f"{DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]} a las {hora}"


def fechas_libres(codigo: str, cuantas: int = 3) -> list[tuple[date, str]]:
    """Los próximos horarios en que se puede visitar el apartamento: cumplen las reglas y no
    están ocupados. Así el modelo ofrece fechas que sí sirven, en vez de inventarlas."""
    if not filas("SELECT 1 FROM apartamentos WHERE codigo = ?", codigo):
        return []
    libres = []
    dia = date.today()
    while len(libres) < cuantas:
        dia += timedelta(days=1)
        for hora in HORAS_DE_VISITA:
            if len(libres) < cuantas and not problemas_de_la_visita(codigo, dia, hora):
                libres.append((dia, hora))
    return libres


def guardar_visita(codigo: str, cliente: str, fecha: date, hora: str) -> int:
    """La única escritura en la base. Solo se llama después de que el cliente confirma."""
    with conectar() as conexion:
        cursor = conexion.execute(
            "INSERT INTO visitas (codigo, cliente, fecha, hora) VALUES (?, ?, ?, ?)",
            (codigo, cliente, fecha.isoformat(), hora),
        )
    return cursor.lastrowid


if __name__ == "__main__":
    ejemplo = {"negocio": "venta", "presupuesto": 350_000_000, "alcobas": 3,
               "barrio": "Laureles", "mascotas": True, "parqueadero": True}
    for apartamento in buscar(ejemplo):
        print(apartamento["codigo"], apartamento["barrio"], "le falta:", apartamento["le_falta"])
    print(problemas_de_la_visita("SG-101", date.today(), "20:00"))
    print([legible(fecha, hora) for fecha, hora in fechas_libres("SG-101")])
