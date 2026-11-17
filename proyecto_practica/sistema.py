"""El asistente: un grafo de LangGraph con un router y dos rutas.

- Recomendar: una encuesta que pregunta en loop hasta tener lo mínimo. Después el código busca y
  el modelo ofrece el apartamento que cumple todo o los más cercanos.
- Agendar: el modelo saca los datos de la visita. Opciones siempre muestra las reglas de horario
  y las fechas libres para que el cliente elija, y Confirmar (human in the loop) le pregunta si
  está seguro antes de guardar: puede agendar, volver a Opciones por otra fecha o cancelar.

El checkpointer guarda el historial de cada chat, así que «ese» o «el primero» se entienden.
"""
import re
from datetime import date
from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from datos import DIAS, buscar, fechas_libres, guardar_visita, legible, problemas_de_la_visita

load_dotenv()

modelo = init_chat_model("google_genai:gemini-3.6-flash")


class Estado(MessagesState):
    ruta: str              # recomendar o agendar
    encuesta: dict         # lo que el cliente quiere del lugar
    preguntas: int         # cuántas veces le hemos preguntado en esta encuesta
    visita: dict | None    # los datos de la visita que pidió el cliente
    eleccion: dict | None  # la fecha que eligió entre las opciones
    otra_fecha: bool       # en Confirmar pidió ver otra fecha


EMOJIS = re.compile(r" ?[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+")  # los rangos de emojis


def responder(texto: str) -> dict:
    """Lo que devuelve un nodo para agregar la respuesta al chat. Sin emojis: si el modelo
    los pone, se quitan aquí."""
    return {"messages": [AIMessage(EMOJIS.sub("", texto).strip())]}


def unir(partes: list[str]) -> str:
    """["a", "b", "c"] -> "a, b y c"."""
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " y " + partes[-1]


# Router

class Ruta(BaseModel):
    ruta: Literal["recomendar", "agendar"] = Field(
        description="recomendar: busca apartamento o responde a la encuesta (negocio, presupuesto, "
                    "alcobas, barrio, mascotas, parqueadero). agendar: quiere visitar un apartamento.")


def router(estado: Estado):
    decision = modelo.with_structured_output(Ruta).invoke([
        SystemMessage("Clasifica el último mensaje del cliente de una inmobiliaria."),
        *estado["messages"][-6:],
    ])
    return {"ruta": decision.ruta, "preguntas": 0, "visita": None, "eleccion": None, "otra_fecha": False}


def elegir_ruta(estado: Estado):
    return "encuesta" if estado["ruta"] == "recomendar" else "agendar"


# Recomendar

class Encuesta(BaseModel):
    negocio: Literal["venta", "arriendo"] | None = Field(description="venta si quiere comprar")
    presupuesto: int | None = Field(description="Lo máximo que puede pagar en pesos: el precio si compra, "
                                                "el canon si arrienda. 400 millones = 400000000")
    alcobas: int | None = Field(description="Cuántas alcobas necesita como mínimo")
    barrio: str | None = Field(description="Barrio que prefiere")
    mascotas: bool | None = Field(description="true si tiene mascotas, false si no")
    parqueadero: bool | None = Field(description="true si necesita parqueadero, false si no")


MINIMO = {  # sin estos datos no se busca, y así se preguntan
    "negocio": "si quieres comprar o arrendar",
    "presupuesto": "hasta cuánto puedes pagar",
    "alcobas": "cuántas alcobas necesitas",
}
OPCIONALES = "Si quieres, dime también el barrio, si tienes mascotas y si necesitas parqueadero."
MAX_PREGUNTAS = 3  # el loop no puede ser infinito

LLENAR_ENCUESTA = ("Llena la encuesta con lo que ha dicho el cliente en la conversación. "
                   "Si no lo dijo, déjalo vacío.")
RECOMENDAR_EXACTOS = ("Eres asesor de la Inmobiliaria Señor Gato. Estos apartamentos cumplen todo lo "
                      "que pidió el cliente. Recomiéndalos en máximo 80 palabras, con su código. ")
RECOMENDAR_CERCANOS = ("Eres asesor de la Inmobiliaria Señor Gato. Ningún apartamento cumple todo lo "
                       "que pidió el cliente. Díselo y ofrécele estos, que son los que cumplen más "
                       "condiciones, con su código y lo que le falta a cada uno. Máximo 100 palabras. ")
OFRECER_VISITA = ("Cierra ofreciendo una visita en una de sus fechas_de_visita, tal cual están escritas: "
                  "no inventes otras. No uses emojis.")


def faltan(estado: Estado) -> list[str]:
    """Los datos mínimos que el cliente todavía no ha dicho."""
    return [dato for dato in MINIMO if estado["encuesta"][dato] is None]


def encuesta(estado: Estado):
    """El modelo llena la encuesta con lo que el cliente ha dicho en la conversación."""
    respuestas = modelo.with_structured_output(Encuesta).invoke([
        SystemMessage(LLENAR_ENCUESTA),
        *estado["messages"][-12:],
    ])
    return {"encuesta": respuestas.model_dump()}


def encuesta_completa(estado: Estado):
    """La arista del loop: si falta lo mínimo y quedan preguntas, se vuelve a preguntar."""
    if faltan(estado) and estado["preguntas"] < MAX_PREGUNTAS:
        return "preguntar"
    return "recomendar"


def preguntar(estado: Estado):
    """El grafo se detiene hasta que el cliente responde. Después vuelve a la encuesta."""
    pregunta = f"Para recomendarte bien, cuéntame {unir([MINIMO[dato] for dato in faltan(estado)])}."
    if estado["preguntas"] == 0:
        pregunta += " " + OPCIONALES

    respuesta = interrupt({"pregunta": pregunta})

    return {
        "messages": [AIMessage(pregunta), HumanMessage(respuesta)],
        "preguntas": estado["preguntas"] + 1,
    }


def recomendar(estado: Estado):
    if faltan(estado):  # se acabaron las preguntas y sigue faltando lo mínimo
        return responder("Sin eso no puedo buscarte apartamento todavía. Cuando lo tengas, escríbeme y seguimos.")

    opciones = buscar(estado["encuesta"])
    for apartamento in opciones:
        apartamento["fechas_de_visita"] = [legible(fecha, hora) for fecha, hora in fechas_libres(apartamento["codigo"], 2)]
    exactos = [apartamento for apartamento in opciones if not apartamento["le_falta"]]

    if exactos:
        instruccion, apartamentos = RECOMENDAR_EXACTOS, exactos
    else:
        instruccion, apartamentos = RECOMENDAR_CERCANOS, opciones
    respuesta = modelo.invoke([SystemMessage(instruccion + OFRECER_VISITA), HumanMessage(str(apartamentos))])
    return responder(respuesta.text)


# Agendar

class Visita(BaseModel):
    codigo: str | None = Field(description="Código SG-XXX del apartamento")
    fecha: date | None = Field(description="Fecha que pidió, si la dijo")
    hora: str | None = Field(description="Hora en formato HH:MM, de 24 horas, si la dijo")
    nombre: str | None = Field(description="Nombre del cliente, si lo dijo")


REGLAS_DE_VISITA = ("Las visitas son de lunes a sábado, entre las 8:00 y las 18:00, y se piden con "
                    "al menos 24 horas de anticipación.")


def agendar(estado: Estado):
    """El modelo saca los datos de la visita que pide el cliente."""
    hoy = date.today()
    visita = modelo.with_structured_output(Visita).invoke([
        SystemMessage(f"Hoy es {DIAS[hoy.weekday()]} {hoy.isoformat()}. Saca los datos de la visita "
                      "que pide el cliente. Si falta uno, déjalo vacío."),
        *estado["messages"][-6:],
    ])
    return {"visita": visita.model_dump(mode="json")}


def opciones(estado: Estado):
    """Siempre muestra las reglas y las fechas libres, y el cliente elige una. Si la fecha que
    pidió cumple las reglas, va de primera. El grafo se detiene hasta que elige."""
    visita = dict(estado["visita"])
    if not fechas_libres(visita["codigo"] or ""):  # no dijo el apartamento: se le pregunta
        respuesta = interrupt({"pregunta": "¿Qué apartamento quieres visitar? Dime su código, por ejemplo SG-101."})
        codigo = re.search(r"SG-\d{3}", respuesta.upper())
        visita["codigo"] = codigo.group() if codigo else None
    libres = fechas_libres(visita["codigo"]) if visita["codigo"] else []
    if not libres:
        return {"visita": visita, "eleccion": None}

    mensaje = REGLAS_DE_VISITA
    if visita["fecha"] and visita["hora"]:
        pedida = (date.fromisoformat(visita["fecha"]), visita["hora"])
        problemas = problemas_de_la_visita(visita["codigo"], *pedida)
        if problemas:
            mensaje = f"La fecha que pediste no se puede: {' '.join(problemas)} {mensaje}"
        else:
            libres = [pedida] + [libre for libre in libres if libre != pedida]

    eleccion = interrupt({
        "mensaje": f"{mensaje} Estas son las fechas para el {visita['codigo']}:",
        "opciones": [{"etiqueta": legible(fecha, hora), "fecha": fecha.isoformat(), "hora": hora}
                     for fecha, hora in libres],
    })
    if "fecha" not in eleccion:  # eligió «Cancelar»
        eleccion = None
    return {"visita": visita, "eleccion": eleccion}


CANCELADA = "Listo, no agendé nada. Cuando quieras, buscamos otra fecha."


def confirmar(estado: Estado):
    """Human in the loop: antes de guardar, el cliente elige entre agendar, ver otra fecha o cancelar."""
    visita, eleccion = estado["visita"], estado["eleccion"]
    if not eleccion:  # no hubo apartamento o no eligió fecha
        return {**responder(CANCELADA), "otra_fecha": False}
    nombre = visita["nombre"] or "Cliente"

    decision = interrupt({"confirmar": f"Visita al {visita['codigo']} el {eleccion['etiqueta']}, a nombre de {nombre}."})

    if decision == "otra":  # vuelve a Opciones, sin poner de primera la fecha que pidió
        return {"otra_fecha": True, "visita": {**visita, "fecha": None, "hora": None}}
    if decision != "si":
        return {**responder(CANCELADA), "otra_fecha": False}
    numero = guardar_visita(visita["codigo"], nombre, date.fromisoformat(eleccion["fecha"]), eleccion["hora"])
    return {**responder(f"**Tu visita ya está programada.** {visita['codigo']}, el {eleccion['etiqueta']}, a "
                        f"nombre de {nombre}. Número de solicitud: {numero}."), "otra_fecha": False}


def decidio(estado: Estado):
    """La arista de Confirmar: si pidió otra fecha, vuelve a Opciones."""
    return "opciones" if estado["otra_fecha"] else END


# El grafo

grafo = StateGraph(Estado)

grafo.add_node("router", router)
grafo.add_node("encuesta", encuesta)
grafo.add_node("preguntar", preguntar)
grafo.add_node("recomendar", recomendar)
grafo.add_node("agendar", agendar)
grafo.add_node("opciones", opciones)
grafo.add_node("confirmar", confirmar)

grafo.add_edge(START, "router")
grafo.add_conditional_edges("router", elegir_ruta, ["encuesta", "agendar"])

grafo.add_conditional_edges("encuesta", encuesta_completa, ["preguntar", "recomendar"])
grafo.add_edge("preguntar", "encuesta")  # el loop
grafo.add_edge("recomendar", END)

grafo.add_edge("agendar", "opciones")
grafo.add_edge("opciones", "confirmar")
grafo.add_conditional_edges("confirmar", decidio, ["opciones", END])

sistema = grafo.compile(checkpointer=InMemorySaver())
