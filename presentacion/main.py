from manim_slides import Slide

from comun.estilo import FONDO_PORTADA
from comun.marco import Marco
from diapositivas import (
    SlideBase,
    SlidesAnatomia,
    SlidesCierre,
    SlidesFundamentos,
    SlidesInicio,
    SlidesInteracciones,
    SlidesPatrones,
    SlidesProyecto,
)


class presentacion(
    SlidesInicio,
    SlidesFundamentos,
    SlidesAnatomia,
    SlidesInteracciones,
    SlidesPatrones,
    SlidesProyecto,
    SlidesCierre,
    SlideBase,
    Slide,
):
    def construct(self):
        self.marco = Marco(self, FONDO_PORTADA)

        # Inicio
        self.slide_pronto_iniciamos()
        self.slide_portada()
        self.slide_pregunta()
        self.slide_que_es_un_agente()
        self.slide_dominios()

        # Fundamentos
        self.slide_seccion_1()
        self.slide_ai_engineer()
        self.slide_enfoque()
        self.slide_siguiente_token()
        self.slide_casos_de_uso()
        self.slide_stack_ai()
        self.slide_practica_1()


        # Anatomía de un agente
        self.slide_seccion_2()
        self.slide_system_prompt()
        self.slide_cache()
        self.slide_tools()
        self.slide_practica_2()

        # interacciones
        self.slide_seccion_3()
        self.slide_mcp()
        self.slide_multimodal()
        self.slide_langgraph()
        self.slide_practica_3()

        # Patrones agénticos
        self.slide_seccion_4()
        self.slide_patron_router()
        self.slide_patron_guardrail_entrada()
        self.slide_patron_guardrail_salida()
        self.slide_patron_cadena()
        self.slide_patron_paralelo()
        self.slide_patron_orquestador()
        self.slide_patron_evaluador()
        self.slide_patron_bucle()
        self.slide_patron_humano()
        self.slide_patron_memoria()
        self.slide_practica_4()

        # PROYECTO EJEMPLo

        # Cierre
        self.slide_proyecto()
        self.slide_gracias()
