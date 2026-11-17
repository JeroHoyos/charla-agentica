"""Las prácticas del taller: un bloque por notebook de `practica/` (del 1 al 4) y el proyecto,
la app de `proyecto_practica/`. La diapositiva de cada práctica muestra las partes de aquí."""


# Prácticas: bloque, notebook de `practica/`, título, objetivo y las partes del notebook. Hay
# una por cada `self.slide_practica_N()` de main.py, en el mismo orden; si cambias una parte en
# el notebook, cámbiala también aquí.
PRACTICAS = (
    ("llamada", "01_fundamentos", "Fundamentos",
     "Conectar un modelo y ver qué cambia al mover sus parámetros", (
         "Conectar el modelo", "Mensajes", "Temperatura", "Límite de tokens y razonamiento",
         "Salida estructurada")),
    ("anatomia", "02_anatomia_agente", "System prompt, caché y herramientas",
     "Las piezas que convierten un modelo en un agente", (
         "El system prompt", "El system prompt y la caché", "Herramientas")),
    ("interacciones", "03_interacciones", "MCP, multimodal, estado y LangGraph",
     "Herramientas de afuera, imágenes, lo que el agente sabe y el flujo como grafo", (
         "MCP", "Multimodal", "LangGraph")),
    ("patrones", "04_patrones", "Diez patrones",
     "El modelo decide lo que requiere razonamiento, el código lo que requiere garantías", (
         "Router", "Guardrails de entrada", "Guardrails de salida", "Prompt chaining",
         "Paralelización", "Orquestador y workers", "Evaluador-optimizador", "Bucle agéntico",
         "Human in the loop", "Memoria")),
    ("proyecto", "proyecto_practica/", "Mini proyecto",
     "Un asistente con SQL, en un chat con Chainlit", (
         "Los datos", "Recomendar", "Agendar", "El chat")),
)


