"""El chat de Chainlit.

    uv run chainlit run app.py -w
"""
import chainlit as cl
from langchain.messages import HumanMessage
from langgraph.types import Command

from sistema import sistema

ESPERA = 600          # segundos que el chat espera una respuesta
AUTOR = "Asistente"   # su avatar es public/avatars/asistente.png
# Cuando no elige fecha. No puede ser None ni {}: LangGraph no reanuda el grafo con esos valores.
NINGUNA = {"ninguna": True}


BIENVENIDA = """¡Hola! Soy el asistente de la **Inmobiliaria Señor Gato**.

Te puedo ayudar con tres cosas:

- **Recomendarte un apartamento.** Cuéntame tu presupuesto y qué comodidades necesitas.
- **Obtener más información de un apartamento.** Dime su número, por ejemplo *muéstrame el 101*.
- **Agendar una visita.** Dime el número del apartamento, el día, la hora y tu nombre.

Por ejemplo: *Quiero comprar un apartamento. ¿Qué me recomiendas?*"""


@cl.on_chat_start
async def bienvenida():
    await cl.Message(content=BIENVENIDA, author=AUTOR).send()


async def preguntar_al_cliente(pregunta: str) -> str:
    """La encuesta: el chat muestra la pregunta y espera lo que el cliente escriba."""
    respuesta = await cl.AskUserMessage(content=pregunta, author=AUTOR, timeout=ESPERA).send()
    return respuesta["output"] if respuesta else ""


async def elegir_fecha(pedido: dict) -> dict:
    """Opciones: las reglas y las fechas libres, un botón por fecha y uno para cancelar."""
    botones = [
        cl.Action(name="fecha", label=opcion["boton"], tooltip=opcion["etiqueta"], icon="calendar", payload=opcion)
        for opcion in pedido["opciones"]
    ]
    botones.append(cl.Action(name="cancelar", label="Cancelar", icon="x", payload=NINGUNA))
    respuesta = await cl.AskActionMessage(content=pedido["mensaje"], actions=botones,
                                          author=AUTOR, timeout=ESPERA).send()
    return respuesta["payload"] if respuesta else NINGUNA


@cl.on_message
async def responder(mensaje: cl.Message):
    config = {
        "configurable": {"thread_id": cl.context.session.id},  # un historial por chat
        "callbacks": [cl.LangchainCallbackHandler()],         # muestra cada paso del grafo
    }
    salida = await sistema.ainvoke({"messages": [HumanMessage(mensaje.content)]}, config)

    # El grafo se detiene (interrupt) cuando espera al cliente: una respuesta o una fecha
    while "__interrupt__" in salida:
        pedido = salida["__interrupt__"][0].value
        if "opciones" in pedido:
            respuesta = await elegir_fecha(pedido)
        else:
            respuesta = await preguntar_al_cliente(pedido["pregunta"])
        salida = await sistema.ainvoke(Command(resume=respuesta), config)

    # La respuesta es markdown: las fichas, los listados y las fotos van en el mismo texto
    await cl.Message(content=salida["messages"][-1].text, author=AUTOR).send()

