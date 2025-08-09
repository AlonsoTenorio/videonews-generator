# Generador de Video con IA – Formato Videonoticia

Este proyecto crea **videos en formato videonoticia** a partir de dos inputs:
- **Nombre del video** (para fines de clasificación y organización).
- **Guion** (contenido base del video).

A partir de este guion, el flujo automatizado realiza los siguientes pasos:

## Flujo de trabajo

1. **División semántica del guion**  
   Utiliza **LangChain** para segmentar el texto en *chunks* o “slides” de forma inteligente, manteniendo la coherencia narrativa.  

2. **Generación de texto para apoyo gráfico**  
   Con **OpenAI (LLM)**, cada chunk se adapta a un formato conciso y visual, pensado para mostrarse en pantalla como refuerzo informativo.

3. **Generación de imágenes**  
   Cada chunk se convierte en una imagen generada por IA (**OpenAI DALL·E**), coherente con el contenido del guion.

4. **Generación de voz**  
   Se sintetiza la narración de cada chunk usando **ElevenLabs**, logrando voces naturales y con buena entonación.

5. **Ensamblaje en XML para edición profesional**  
   Todos los elementos generados (imágenes, voz, subtítulos) se organizan en un archivo **XML compatible** con softwares como **Adobe Premiere** o **Final Cut Pro**, facilitando la edición final.  

---

💡 **Nota:**  
Esta es una **versión inicial** con múltiples oportunidades de mejora.  
Por ejemplo: actualmente, el texto de apoyo gráfico se exporta como imagen, pero podría generarse directamente como **texto en el XML**, generando la codificación y decodificación del mismo permitiendo que el software de edición lo interprete.  

---

## Requisitos previos

- Python 3.11 o superior  
- Claves API de:
  - OpenAI
  - ElevenLabs

---

## Instalación

```bash
git clone https://github.com/AlonsoTenorio/videonews-generator.git
cd videonews-generator
pip install -r requirements.txt
```

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto con este contenido:

```
OPENAI_API_KEY=tu_clave_openai
ELEVENLABS_API_KEY=tu_clave_elevenlabs
```

---

## Uso

1. Inicia la app Flask:
```bash
python app.py
```
2. Abre en el navegador:
```
http://127.0.0.1:5000/
```
3. Ingresa el nombre del video y el guion.

---

## Salida

Estructura generada:
```
video_<nombre>_<fecha>/
├── IMGS/
├── VOICE/
├── slides.json
└── video.xml (importar a tu software de edición de video)
```