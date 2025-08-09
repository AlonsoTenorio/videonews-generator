import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

with open("config.json", "r") as f:
    config = json.load(f)

PROYECTO = config["nombre_proyecto"]
IMGS_DIR = os.path.join(PROYECTO, "IMGS")
os.makedirs(IMGS_DIR, exist_ok=True)

client = OpenAI(api_key=openai_api_key)

with open(os.path.join(PROYECTO, "slides.json"), "r", encoding="utf-8") as f:
    slides = json.load(f)

def reparar_jpg_para_premiere(path):
    try:
        with Image.open(path) as img:
            rgb_img = img.convert("RGB")  # Asegura el modo correcto
            rgb_img.save(path, "JPEG", quality=95)  # Reescribe con compresión estándar
    except Exception as e:
        print(f"Error al recodificar {path}: {e}")

def generar_imagen(prompt, ruta_guardado):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1
    )
    
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    
    nombre_temporal = "temp_image.jpg"
    with open(nombre_temporal, 'wb') as handler:
        handler.write(img_data)

    reparar_jpg_para_premiere(nombre_temporal)
    os.rename(nombre_temporal, ruta_guardado)



for i, slide in enumerate(slides):
    prompt = slide["prompt_imagen"]
    nombre_archivo = f"img_{i:02d}.jpg"
    ruta_guardado = os.path.join(IMGS_DIR, nombre_archivo)
    
    generar_imagen(prompt, ruta_guardado)

print(f"✅ Images")