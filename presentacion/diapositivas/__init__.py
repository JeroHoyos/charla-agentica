from manim import UP, FadeIn, FadeOut

from comun.componentes import cursor_esquina

from . import (
    ai_engineer,
    analogias,
    anatomia,
    casos_de_uso,
    dominios,
    enfoque,
    entorno,
    formacion,
    fundamentos,
    gracias,
    observar,
    patron,
    portada,
    practica,
    pregunta,
    pronto_iniciamos,
    que_es_un_agente,
    siguiente_token,
    stack_ai,
)


class SlideBase:
    def indicador(self):
        if getattr(self, "_indicador", None) is None:
            self._indicador = cursor_esquina()
        return self._indicador

    def next_slide(self, *args, indicador=True, **kwargs):
        if not indicador:
            super().next_slide(*args, **kwargs)
            return
        cursor = self.indicador()
        self.play(FadeIn(cursor, shift=UP * 0.1), run_time=0.3)
        super().next_slide(*args, **kwargs)
        self.remove(cursor)

    def iniciar_slide(self):
        # El marco (fondo, rótulo, logo y puntos) se queda; lo demás se va.
        fijos = self.marco.fijos
        resto = [m for m in self.mobjects if m not in fijos]
        for m in resto:
            m.clear_updaters()

        if resto:
            self.play(*[FadeOut(m) for m in resto], run_time=0.5)


def _slide(construir):
    def metodo(self):
        self.iniciar_slide()
        construir(self)
        self.wait(0.3)
        self.next_slide()

    return metodo


def _slide_en_loop(construir):
    """Para las diapositivas que terminan en un loop: `construir` ya muestra el indicador y
    abre el loop; aquí solo se cierra, sin pausa de más que rompa la vuelta."""

    def metodo(self):
        self.iniciar_slide()
        construir(self)
        self.next_slide(indicador=False)
        self.remove(self.indicador())

    return metodo


# Cada clase sigue el orden de main.py: después de los fundamentos, una por notebook. Cada
# concepto abre con su analogía (analogias.py) y, si es un patrón, sigue su ficha (patron.py).


class SlidesInicio:
    slide_portada = _slide_en_loop(portada.construir)
    slide_pronto_iniciamos = _slide(pronto_iniciamos.construir)
    slide_pregunta = _slide(pregunta.construir)
    slide_que_es_un_agente = _slide(que_es_un_agente.construir)
    slide_dominios = _slide(dominios.construir)
    # La misma práctica cierra cada bloque, con el número del bloque; la del notebook va aparte.
    slide_practica_1 = _slide(practica.construir)
    slide_practica_2 = _slide(practica.construir)
    slide_practica_3 = _slide_en_loop(practica.construir_en_loop)
    slide_practica_4 = _slide_en_loop(practica.construir_en_loop)


class SlidesFundamentos:
    slide_seccion_1 = _slide_en_loop(fundamentos.construir)
    slide_ai_engineer = _slide(ai_engineer.construir)
    slide_enfoque = _slide(enfoque.construir)
    slide_siguiente_token = _slide_en_loop(siguiente_token.construir)
    slide_casos_de_uso = _slide(casos_de_uso.construir)
    slide_stack_ai = _slide(stack_ai.construir)


class SlidesAnatomia:
    slide_seccion_2 = _slide(anatomia.construir)
    slide_system_prompt = _slide(analogias.manual)
    slide_cache = _slide(analogias.cache)
    slide_tools = _slide(analogias.aparatos)


class SlidesInteracciones:
    slide_seccion_3 = _slide_en_loop(entorno.construir)
    slide_mcp = _slide(analogias.acople)
    slide_multimodal = _slide(analogias.multimodal)
    slide_langgraph = _slide(analogias.grafo)


class SlidesPatrones:
    # Las diez fichas de la guía de Commit Academy, seguidas y sin analogías.
    slide_seccion_4 = _slide_en_loop(formacion.construir)
    slide_patron_router = _slide(patron.ficha("router"))
    slide_patron_guardrail_entrada = _slide(patron.ficha("guardrail_entrada"))
    slide_patron_guardrail_salida = _slide(patron.ficha("guardrail_salida"))
    slide_patron_cadena = _slide(patron.ficha("cadena"))
    slide_patron_paralelo = _slide(patron.ficha("paralelo"))
    slide_patron_orquestador = _slide(patron.ficha("orquestador"))
    slide_patron_evaluador = _slide(patron.ficha("evaluador"))
    slide_patron_bucle = _slide(patron.ficha("bucle"))
    slide_patron_humano = _slide(patron.ficha("humano"))
    slide_patron_memoria = _slide(patron.ficha("memoria"))


class SlidesProyecto:
    slide_proyecto = _slide_en_loop(observar.construir)


class SlidesCierre:
    slide_gracias = _slide_en_loop(gracias.construir)
