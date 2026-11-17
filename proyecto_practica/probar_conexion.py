"""Revisa que la base de datos y el modelo respondan antes de abrir el chat.

    uv run python probar_conexion.py
"""
from dotenv import load_dotenv

load_dotenv()


def probar(nombre, prueba):
    try:
        print(f"OK     {nombre}: {prueba()}")
    except Exception as error:  # noqa: BLE001 - queremos ver cualquier falla
        print(f"FALLA  {nombre}: {type(error).__name__}: {error}")


def base_de_datos():
    from datos import filas
    return filas("SELECT count(*) AS apartamentos FROM apartamentos")


def modelo():
    from langchain.chat_models import init_chat_model
    return init_chat_model("google_genai:gemini-3.6-flash").invoke("Responde solo: listo").text


if __name__ == "__main__":
    probar("Base de datos", base_de_datos)
    probar("Modelo", modelo)
