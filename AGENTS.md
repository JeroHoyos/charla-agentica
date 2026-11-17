# AGENTS.md

Taller «De Prompts a Agentes»: dos horas, para estudiantes de sistemas que programan en Python.
Enseña patrones y arquitectura de agentes con LangChain. Diapositivas animadas con Manim Slides y
notebooks de práctica.

## Dónde está cada cosa

| Ruta | Qué es |
| --- | --- |
| `presentacion/main.py` | El orden de las diapositivas. |
| `presentacion/diapositivas/__init__.py` | El registro: `slide_x = _slide(modulo.construir)`. |
| `presentacion/diapositivas/analogias.py` | Las analogías: una escena de la oficina por concepto. |
| `presentacion/diapositivas/patron.py` | La ficha de cada patrón: título y diagrama. |
| `presentacion/comun/escena.py` | Las piezas de las analogías: cuarto, personas, robot, muebles, rótulos y `analogia()`. |
| `presentacion/comun/tres_d.py` | Las figuras en 3D hechas de cajas: el robot de la portada y las personas. |
| `presentacion/comun/temario.py` | Las prácticas: las partes de cada notebook que muestra su diapositiva. |
| `presentacion/comun/componentes.py` | Texto, cajas, diagramas e íconos. Busca aquí antes de dibujar algo. |
| `practica/` | Los notebooks (00 a 04), `servidor_mcp.py` y `datos/` (el plano e `inmobiliaria.sql`, en SQLite). Solo Gemini. |
| `proyecto_practica/` | El proyecto: un grafo de LangGraph (recomendar con una encuesta y agendar) y un chat de Chainlit. Solo SQL. |
| `herramientas/diagramas.py` | Dibuja los diagramas de los notebooks en `practica/assets/diagramas/`, con los colores de las diapositivas. |
| `herramientas/apartamentos.py` | Dibuja la fachada y el plano de cada apartamento del proyecto en `proyecto_practica/public/apartamentos/`. |

## El temario sigue a los notebooks

Después de los fundamentos hay **un bloque por notebook** (del 1 al 4), con su mismo número, su
mismo orden y sus mismos temas. Si cambia un notebook, cambia su bloque en `temario.py`
(las partes de `PRACTICAS`) y en `main.py`.

- Los notebooks no llevan ejercicio de «Tu turno» (se quitó a pedido). La diapositiva de cada
  práctica muestra las partes del notebook.
- Cada concepto del notebook lleva su diagrama (cajas y flechas, como los de la guía de
  patrones) al final del texto de su parte. Se dibujan en `herramientas/diagramas.py`: una
  función por diagrama, y una línea `<img>` en el `.ipynb`. Los notebooks se editan a mano: no hay
  código que los genere ni que los sobrescriba (se quitó a pedido).
- No hay RAG ni vector store: se quitó a pedido. SQL solo se ve en el proyecto (las consultas
  las escribe el código, no el modelo). En el notebook 4 las herramientas son funciones de Python sobre los datos.
- Solo queda lo que se usa (pedido así): lo que no está en `main.py` se borra, sin dejarlo
  comentado. Las imágenes de `assets/` son solo las que carga alguna diapositiva.

## Reglas de las diapositivas

- **Nada de código en pantalla.** Ni Python, ni terminales, ni JSON, ni nombres de funciones. El
  código vive en los notebooks.
- **Poco texto.** Una frase de cierre por diapositiva, con una parte resaltada, y rótulos cortos.
- **Sin «·» como separador.** Usa comas, dos puntos o el layout.
- **Cada concepto abre con su analogía**, en tres tiempos: primero el problema que había
  (animado, con la frase en coral), después la escena que lo arregla y al final los rótulos pasan
  a ser los del concepto. Casi todo ocurre en una oficina; el system prompt va en un teatro, el
  prompt caching en un control de trenes, la memoria en hilos donde se cuelgan los mensajes,
  las tools en una cabina con tubos hacia unas máquinas y MCP en una estación espacial con
  naves que se acoplan (pedido así); LangChain y LangGraph, en el mapa de un videojuego (la
  cadena solo va hacia adelante; el grafo trae desvíos, carriles, banderas y una barrera, y al
  final el mapa entero cabe en una parada de otro). Esas seis van sin las frases ni los rótulos de abajo (pedido así),
  con una pausa por paso y con figuras que se mueven (`_en_teatro()` en `analogias.py`).
- **El robot de la portada es siempre el modelo.** Las personas son clientes, empleados o quien
  revisa. Quien revisa con reglas lleva gorra. Robots y personas van en 3D (`robot()`,
  `persona()`); un robot detrás de un escritorio va antes que él en la lista de la escena.
  Los robots pequeños que hacen un trabajo (peritos, oficiales, puestos, quien evalúa) llevan
  su oficio, no solo un color: ingeniero, analista, abogado, redactor, discriminador, asesor o
  revisor (`OFICIOS` en `tres_d.py`).
- **El bloque 4 son los diez patrones de la guía**, una ficha tras otra y sin analogías (pedido
  así, por ahora): el título, el diagrama de la guía en grande (sin
  el caso de la inmobiliaria), sin frases debajo ni contador (pedido así). El bloque de RAG se
  quitó, con su notebook.
- **Una idea por pausa.** Si una diapositiva necesita subtítulo, tabla de varias columnas o más
  de una tarjeta de texto, sobra algo: quítalo o pártela con pausas, como `arquitectura.py`, que
  agrega una capa y una frase por pausa.
- `material/` tiene las fuentes: la guía de patrones de Commit Academy y el resumen en video de
  «AI Engineering» de Chip Huyen (evaluar, las cinco capas).
- **Ejemplos:** la Inmobiliaria Señor Gato sale en una sola diapositiva, `observar.py` (pedido
  así): presenta el caso y sus problemas y termina en «Pasando al código». Las demás van sin
  ella. Los notebooks de `practica/` la usan.
- **Indicador:** el logo de Aperture abajo a la derecha aparece cuando la diapositiva espera la
  flecha. No va en otro lugar.
- Ninguna función pasa de complejidad cognitiva 10 (`uvx complexipy .` en `presentacion/`).

## Diseño

Toda la charla va en fondo oscuro, como la portada y «pronto iniciamos». La composición es la
de las guías de Commit Academy (`material/`). En `estilo.py` los nombres dicen para qué sirve
cada color: `TINTA` es el texto (claro) y `OSCURO` lo que se escribe sobre un relleno de color.

- **Cabecera:** el nombre de la charla en mono a la izquierda y una raya gris de lado a lado.
  Sin la píldora del bloque a la derecha (se quitó a pedido). La pone `Marco`.
- **Títulos** gruesos y a la izquierda (`titulo()`, `titular()`, Archivo Black). Texto en Lexend.
  JetBrains Mono solo para rótulos en mayúsculas y etiquetas (`mono()`, `rotulo()`, `chip()`).
- **Diagramas:** el modelo va en cian lleno, el control en blanco, los guardrails en coral y
  las personas en lila; la entrada y la salida, solo con borde. La tarjeta lleva su leyenda (`leyenda()`).
- **Sin cajas de «IDEA»** (se quitaron a pedido): ninguna diapositiva lleva la franja con ese
  sello. El problema de las analogías va en una nota oscura con el canto coral.
- **Portada, «pronto iniciamos» y cierre** van sin cabecera ni formas de fondo.
- **Vistos buenos y equis** se dibujan con `marca()`: las fuentes no traen esos signos.

## Agregar una analogía

1. En `analogias.py`, escribe `_escena()`: devuelve lo que ya está en el cuarto, la función que
   anima el problema (y devuelve lo que hay que quitar) y la función que anima la solución.
2. Arma la diapositiva con `analogia(bloque, lección, pregunta, pista, _escena, rótulos, problema,
   frase, definición)`.
3. Regístrala en `diapositivas/__init__.py` y llámala en `main.py`.

## Verificar

No hay tests de las diapositivas: se renderizan y se miran sus fotogramas, con la skill `slides`.
Los notebooks se corren de principio a fin con `nbclient` desde `practica/`.
