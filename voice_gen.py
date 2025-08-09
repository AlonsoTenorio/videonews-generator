import os
import json
from dotenv import load_dotenv
from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

PROYECTO = config["nombre_proyecto"]
VOICE_DIR = f"{PROYECTO}/VOICE"
SLIDES_PATH = f"{PROYECTO}/slides.json"
os.makedirs(VOICE_DIR, exist_ok=True)

with open(f"{PROYECTO}/slides.json", "r", encoding="utf-8") as f:
    slides = json.load(f)

VOICE_ID = "iDEmt5MnqUotdwCIVplo"
MODEL_ID = "eleven_multilingual_v2"

for i, slide in enumerate(slides, start=1):
    texto = slide["chunk"]
    nombre_archivo = slide["nombre_audio"]
    ruta_salida = os.path.join(VOICE_DIR, nombre_archivo)

    audio_stream = client.text_to_speech.convert(
        text=texto,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        output_format="mp3_44100_128",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.5,
            style=0.5,
            use_speaker_boost=True
        )
    )

    save(audio_stream, ruta_salida)


from mutagen.mp3 import MP3

FPS = 30

with open(SLIDES_PATH, "r", encoding="utf-8") as f:
    slides = json.load(f)

for slide in slides:
    nombre_audio = slide["nombre_audio"]
    ruta_audio = os.path.join(VOICE_DIR, nombre_audio)

    # Obtener duración del .mp3
    audio = MP3(ruta_audio)
    duracion_segundos = audio.info.length
    duracion_frames = int(duracion_segundos * FPS)

    # Guardar en el slide
    slide["duracion_segundos"] = round(duracion_segundos, 2)
    slide["duracion_frames"] = duracion_frames

with open(SLIDES_PATH, "w", encoding="utf-8") as f:
    json.dump(slides, f, indent=2, ensure_ascii=False)

print(f"✅ Voices")