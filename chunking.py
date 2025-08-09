from datetime import date
import os
from dotenv import load_dotenv
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

NOMBRE = "pokemon"
GUION = """
En un mundo donde miles de series intentan robarse tu corazón... solo una ha logrado atraparlos a todos.
Primero, hablemos de impacto cultural: Más de 25 años en pantalla. Videojuegos, películas, cartas coleccionables, peluches, cereales... hasta calcetines con Snorlax.
¿Conoces a alguien que no haya cantado "Tengo que atraparlos" a todo pulmón? Yo tampoco.
Segundo: la historia. Un joven llamado Ash Ketchum, con más perseverancia que cualquier protagonista en la historia del anime. Veinticinco años persiguiendo su sueño. Y cuando finalmente ganó la Liga Mundial... medio planeta lloró.
Tercero: las batallas. No es solo pelear. Es estrategia, amistad, adrenalina y la eterna duda existencial de por qué un ataque de tipo planta afecta a una roca.
Pero lo que hace que Pokémon sea la mejor serie jamás creada… es el corazón. Nos enseñó sobre la amistad, la perseverancia, el respeto por la naturaleza y la emoción de seguir explorando.
Porque en un mundo lleno de opciones… ¡solo una serie lo atrapó todo! Pokémon.
"""

_env_nombre = os.getenv("NOMBRE")
_env_guion  = os.getenv("GUION")
if _env_nombre and _env_nombre.strip():
    NOMBRE = _env_nombre.strip()
if _env_guion and _env_guion.strip():
    GUION = _env_guion

FECHA = date.today().isoformat()
PROYECTO = f"video_{NOMBRE}_{FECHA}"


def splitter_script(texto, chunk_size=200, chunk_overlap=20):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", ",", " "]
    )
    return splitter.split_text(texto)

chunks = splitter_script(GUION)


prompt_template = PromptTemplate(
    input_variables=["chunk"],
    template="""
Tu tarea es generar un párrafo atractivo y breve, como si fuera para TikTok o una videonoticia viral.
Debe ser distinto al texto original, pero basado en su contenido.
No emojis nunca.
No repitas el texto literal.
No más de 120 caracteres.

Texto base:
"{chunk}"

Título para pantalla:
"""
)


prompt_visual = PromptTemplate(
    input_variables=["chunk"],
    template="""
Tu tarea es convertir el siguiente texto narrado en un prompt para generar una imagen con inteligencia artificial.
Describe claramente la escena, personajes, entorno y estilo. No repitas el texto literal.
Incluye detalles como edad, ambiente, iluminación, emociones, ropa, si aplica.

Texto:
"{chunk}"

Prompt visual:
"""
)

llm = ChatOpenAI(
    temperature=0.8,
    model="gpt-4",
    openai_api_key=openai_api_key
)

chain = prompt_template | llm
chain_visual = prompt_visual | llm

resultado_slides = []

for i, chunk in enumerate(chunks):
    titulo_pantalla = chain.invoke({"chunk": chunk}).content.strip()
    prompt_imagen = chain_visual.invoke({"chunk": chunk}).content.strip()

    slide_data = {
        "slide": i + 1,
        "chunk": chunk,
        "texto_pantalla": titulo_pantalla,
        "prompt_imagen": prompt_imagen,
        "nombre_audio": f"chunk_voice{i+1:02d}.mp3",
        "nombre_imagen": f"img_{i:02d}.jpg"
    }

    resultado_slides.append(slide_data)

os.makedirs(PROYECTO, exist_ok=True)

with open(f"{PROYECTO}/slides.json", "w", encoding="utf-8") as f:
    json.dump(resultado_slides, f, ensure_ascii=False, indent=4)

with open("config.json", "w", encoding="utf-8") as f:
    json.dump({"nombre_proyecto": PROYECTO}, f, indent=4)

print(f"✅ Chunking")