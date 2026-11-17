"""El asistente: un grafo de LangGraph con un router y tres rutas.

- Recomendar: una encuesta que pregunta en loop hasta tener lo mínimo. Después el código busca
  los apartamentos y el modelo los presenta con una frase. Las fichas las arma el código.
- Ver: el modelo saca los números de los apartamentos que pide el cliente y el código muestra
  la ficha y la foto de cada uno.
- Agendar: el modelo saca los datos de la visita. Opciones muestra las reglas de horario y las
  fechas libres para que el cliente elija, y Confirmar le pregunta si está seguro antes de
  guardar: puede agendar, volver a Opciones por otra fecha o cancelar.

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

from datos import (
    DIAS,
    buscar,
    corta,
    fechas_libres,
    guardar_visita,
    legible,
    por_dia,
    problemas_de_la_visita,
    un_apartamento,
)

load_dotenv()

modelo = init_chat_model("google_genai:gemini-3.6-flash")


class Estado(MessagesState):
    ruta: str              # recomendar, ver o agendar
    encuesta: dict         # lo que el cliente quiere del apartamento
    preguntas: int         # cuántas veces le hemos preguntado en esta encuesta
    visita: dict | None    # los datos de la visita que pidió el cliente
    eleccion: dict | None  # la fecha que eligió entre las opciones
    otra_fecha: bool       # en Confirmar pidió ver otra fecha


EMOJIS = re.compile(r" ?[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+")


def responder(texto: str) -> dict:
    """Lo que devuelve un nodo para agregar la respuesta al chat. Si el modelo puso emojis,
    se quitan aquí."""
    return {"messages": [AIMessage(EMOJIS.sub("", texto).strip())]}


def unir(partes: list[str]) -> str:
    """["a", "b", "c"] -> "a, b y c"."""
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " y " + partes[-1]


def listado(lineas: list[str]) -> str:
    """["a", "b"] -> "- a\\n- b", un listado en markdown."""
    return "\n".join(f"- {linea}" for linea in lineas)


# Router

class Ruta(BaseModel):
    ruta: Literal["recomendar", "ver", "agendar"] = Field(
        description="recomendar: busca apartamento o responde a la encuesta (presupuesto, alcobas, "
                    "barrio, mascotas, parqueadero). "
                    "ver: pregunta por apartamentos que ya conoce (muéstrame el 101, cuánto vale el primero). "
                    "agendar: quiere visitar un apartamento.")


def router(estado: Estado):
    decision = modelo.with_structured_output(Ruta).invoke([
        SystemMessage("Clasifica el último mensaje del cliente de una inmobiliaria."),
        *estado["messages"][-6:],
    ])
    return {"ruta": decision.ruta, "preguntas": 0, "visita": None, "eleccion": None, "otra_fecha": False}


def elegir_ruta(estado: Estado):
    """La arista del router: el nombre de la ruta lleva al primer nodo de esa ruta."""
    primer_nodo = {"recomendar": "encuesta", "ver": "ver", "agendar": "agendar"}
    return primer_nodo[estado["ruta"]]


# Las fichas: los datos de cada apartamento los escribe el código, no el modelo

FOTOS = "/public/apartamentos"  # Chainlit sirve la carpeta public/ en esa ruta

NO_CUMPLE = {
    "presupuesto": "se pasa de tu presupuesto",
    "alcobas": "tiene menos alcobas de las que pediste",
    "barrio": "queda en otro barrio",
    "mascotas": "no admite mascotas",
    "parqueadero": "no tiene parqueadero",
}


def millones(pesos: int) -> str:
    """295000000 -> "295 millones"."""
    return f"{pesos / 1_000_000:,.0f} millones".replace(",", ".")


def si_o_no(valor) -> str:
    return "sí" if valor else "no"


def ficha(apartamento: dict) -> str:
    """El apartamento en un listado y su foto, en markdown."""
    codigo = apartamento["codigo"]
    datos = [
        f"**Barrio:** {apartamento['barrio']}",
        f"**Precio:** {millones(apartamento['precio'])}",
        f"**Alcobas:** {apartamento['alcobas']}",
        f"**Mascotas:** {si_o_no(apartamento['mascotas'])}",
        f"**Parqueadero:** {si_o_no(apartamento['parqueadero'])}",
    ]
    le_falta = apartamento.get("le_falta", [])
    if le_falta:
        datos.append(f"**Ojo:** {unir([NO_CUMPLE[condicion] for condicion in le_falta])}")

    foto = f"![Apartamento {codigo}]({FOTOS}/{codigo}.png)"
    return f"### Apartamento {codigo}\n{listado(datos)}\n\n{foto}"


# Recomendar

class Encuesta(BaseModel):
    presupuesto: int | None = Field(description="Lo máximo que puede pagar por el apartamento, en pesos. "
                                                "400 millones = 400000000")
    alcobas: int | None = Field(description="Cuántas alcobas necesita como mínimo")
    barrio: str | None = Field(description="Barrio que prefiere")
    mascotas: bool | None = Field(description="true si tiene mascotas, false si no")
    parqueadero: bool | None = Field(description="true si necesita parqueadero, false si no")


MINIMO = {  # sin estos datos no se busca, y así se preguntan
    "presupuesto": "Hasta cuánto puedes pagar",
    "alcobas": "Cuántas alcobas necesitas",
}
OPCIONALES = ["El barrio", "Si tienes mascotas", "Si necesitas parqueadero"]
MAX_PREGUNTAS = 3  # el loop no puede ser infinito

LLENAR_ENCUESTA = ("Llena la encuesta con lo que ha dicho el cliente en la conversación. "
                   "Si no lo dijo, déjalo vacío.")
ASESOR = "Eres asesor de la Inmobiliaria Señor Gato. "
EXACTOS = "Estos apartamentos cumplen todo lo que pidió el cliente. "
CERCANOS = "Ningún apartamento cumple todo lo que pidió el cliente. Estos son los que cumplen más condiciones. "
PRESENTAR = ("Escribe una o dos frases para presentarlos al cliente, de tú y en máximo 40 palabras. "
             "No repitas sus datos ni sus números: el chat muestra debajo la ficha y la foto de cada uno. "
             "No uses emojis.")


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
    pregunta = "Para recomendarte bien, cuéntame:\n\n" + listado([MINIMO[dato] for dato in faltan(estado)])
    if estado["preguntas"] == 0:
        pregunta += "\n\nSi quieres, dime también:\n\n" + listado(OPCIONALES)

    respuesta = interrupt({"pregunta": pregunta})

    return {
        "messages": [AIMessage(pregunta), HumanMessage(respuesta)],
        "preguntas": estado["preguntas"] + 1,
    }


def que_sigue(codigo: str) -> str:
    """El cierre de la recomendación: ver el apartamento o agendar la visita."""
    fecha, hora = fechas_libres(codigo, 1)[0]
    opciones = [
        f"**Ver un apartamento:** escribe *muéstrame el {codigo}*",
        f"**Agendar la visita:** escribe *quiero visitar el {codigo}*. "
        f"La próxima fecha libre es el {legible(fecha, hora)}.",
    ]
    return "**¿Qué quieres hacer ahora?**\n\n" + listado(opciones)


def recomendar(estado: Estado):
    if faltan(estado):  # se acabaron las preguntas y sigue faltando lo mínimo
        return responder("Sin eso no puedo buscarte apartamento todavía. Cuando lo tengas, escríbeme y seguimos.")

    opciones = buscar(estado["encuesta"])
    exactos = [apartamento for apartamento in opciones if not apartamento["le_falta"]]
    apartamentos = exactos or opciones
    contexto = EXACTOS if exactos else CERCANOS

    presentacion = modelo.invoke([
        SystemMessage(ASESOR + contexto + PRESENTAR),
        HumanMessage(str(apartamentos)),
    ]).text

    partes = [presentacion, *map(ficha, apartamentos), que_sigue(apartamentos[0]["codigo"])]
    return responder("\n\n".join(partes))


# Ver

class Codigos(BaseModel):
    codigos: list[str] = Field(description="Los números de los apartamentos que pide ver el cliente, "
                                           "de tres cifras, por ejemplo 101")


SACAR_CODIGOS = ("Saca los números de los apartamentos que el cliente quiere ver. Si dice «el primero» "
                 "o «ese», habla de la última lista que le mostró el asistente.")


def ver(estado: Estado):
    """El modelo saca los números (también de «el primero» o «la de 406») y el código arma las fichas."""
    pedido = modelo.with_structured_output(Codigos).invoke([
        SystemMessage(SACAR_CODIGOS),
        *estado["messages"][-6:],
    ])
    apartamentos = [un_apartamento(codigo.strip()) for codigo in pedido.codigos]
    apartamentos = [apartamento for apartamento in apartamentos if apartamento]  # los que existen
    if not apartamentos:
        return responder("No encontré ese apartamento. Dime su número, por ejemplo 101.")

    codigo = apartamentos[0]["codigo"]
    visitar = f"**¿Quieres visitarlo?** Escribe *quiero visitar el {codigo}* y te muestro las fechas libres."
    return responder("\n\n".join([*map(ficha, apartamentos), visitar]))


# Agendar

class Visita(BaseModel):
    codigo: str | None = Field(description="Número del apartamento, de tres cifras, por ejemplo 101")
    fecha: date | None = Field(description="Fecha que pidió, si la dijo")
    hora: str | None = Field(description="Hora en formato HH:MM, de 24 horas, si la dijo")
    nombre: str | None = Field(description="Nombre del cliente, si lo dijo")


REGLAS_DE_VISITA = ("Las visitas son de lunes a sábado, entre las 8:00 y las 18:00, y se piden con "
                    "al menos 24 horas de anticipación.")
CANCELADA = "Listo, no agendé nada. Cuando quieras, buscamos otra fecha."


def agendar(estado: Estado):
    """El modelo saca los datos de la visita que pide el cliente."""
    hoy = date.today()
    visita = modelo.with_structured_output(Visita).invoke([
        SystemMessage(f"Hoy es {DIAS[hoy.weekday()]} {hoy.isoformat()}. Saca los datos de la visita "
                      "que pide el cliente. Si falta uno, déjalo vacío."),
        *estado["messages"][-6:],
    ])
    return {"visita": visita.model_dump(mode="json")}


def preguntar_apartamento() -> str | None:
    """Si el cliente no dijo qué apartamento quiere visitar, el grafo se detiene y se lo pregunta."""
    respuesta = interrupt({"pregunta": "¿Qué apartamento quieres visitar? Dime su número, por ejemplo 101."})
    numero = re.search(r"\b\d{3}\b", respuesta)
    return numero.group() if numero else None


def opciones(estado: Estado):
    """Muestra las reglas y las fechas libres, y el cliente elige una. Si la fecha que pidió cumple
    las reglas, va de primera. El grafo se detiene hasta que elige."""
    visita = dict(estado["visita"])
    if not un_apartamento(visita["codigo"] or ""):
        visita["codigo"] = preguntar_apartamento()
    libres = fechas_libres(visita["codigo"]) if visita["codigo"] else []
    if not libres:
        return {"visita": visita, "eleccion": None}

    mensaje = REGLAS_DE_VISITA
    if visita["fecha"] and visita["hora"]:
        pedida = (date.fromisoformat(visita["fecha"]), visita["hora"])
        problemas = problemas_de_la_visita(visita["codigo"], *pedida)
        if problemas:
            mensaje = f"**La fecha que pediste no se puede:**\n\n{listado(problemas)}\n\n{mensaje}"
        else:
            libres = [pedida] + [libre for libre in libres if libre != pedida]

    mensaje += f"\n\n**Fechas libres para el apartamento {visita['codigo']}:**\n\n{por_dia(libres)}\n\nElige una:"
    botones = [{"etiqueta": legible(fecha, hora), "boton": corta(fecha, hora),
                "fecha": fecha.isoformat(), "hora": hora}
               for fecha, hora in libres]

    eleccion = interrupt({"mensaje": mensaje, "opciones": botones})

    if "fecha" not in eleccion:  # eligió «Cancelar»
        eleccion = None
    return {"visita": visita, "eleccion": eleccion}


def confirmar(estado: Estado):
    """Antes de guardar, el cliente elige entre agendar, ver otra fecha o cancelar."""
    visita, eleccion = estado["visita"], estado["eleccion"]
    if not eleccion:  # no hubo apartamento o no eligió fecha
        return {**responder(CANCELADA), "otra_fecha": False}
    nombre = visita["nombre"] or "Cliente"
    resumen = f"Visita al apartamento {visita['codigo']} el {eleccion['etiqueta']}, a nombre de {nombre}."

    decision = interrupt({"confirmar": resumen})

    if decision == "otra":  # vuelve a Opciones, sin poner de primera la fecha que pidió
        return {"otra_fecha": True, "visita": {**visita, "fecha": None, "hora": None}}
    if decision != "si":
        return {**responder(CANCELADA), "otra_fecha": False}

    numero = guardar_visita(visita["codigo"], nombre, date.fromisoformat(eleccion["fecha"]), eleccion["hora"])
    detalle = listado([
        f"**Apartamento:** {visita['codigo']}",
        f"**Fecha:** {eleccion['etiqueta']}",
        f"**A nombre de:** {nombre}",
        f"**Número de solicitud:** {numero}",
    ])
    return {**responder(f"### Tu visita ya está programada\n{detalle}"), "otra_fecha": False}


def decidio(estado: Estado):
    """La arista de Confirmar: si pidió otra fecha, vuelve a Opciones."""
    return "opciones" if estado["otra_fecha"] else END


# El grafo

grafo = StateGraph(Estado)

grafo.add_node("router", router)
grafo.add_node("encuesta", encuesta)
grafo.add_node("preguntar", preguntar)
grafo.add_node("recomendar", recomendar)
grafo.add_node("ver", ver)
grafo.add_node("agendar", agendar)
grafo.add_node("opciones", opciones)
grafo.add_node("confirmar", confirmar)

grafo.add_edge(START, "router")
grafo.add_conditional_edges("router", elegir_ruta, ["encuesta", "ver", "agendar"])

# Ruta A: recomendar
grafo.add_conditional_edges("encuesta", encuesta_completa, ["preguntar", "recomendar"])
grafo.add_edge("preguntar", "encuesta")  # el loop
grafo.add_edge("recomendar", END)

# Ruta B: agendar
grafo.add_edge("agendar", "opciones")
grafo.add_edge("opciones", "confirmar")
grafo.add_conditional_edges("confirmar", decidio, ["opciones", END])

# Ruta C: ver
grafo.add_edge("ver", END)

sistema = grafo.compile(checkpointer=InMemorySaver())
