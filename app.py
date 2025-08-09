import os
import subprocess
import sys
from pathlib import Path
from flask import Flask, request, render_template_string

BASE_DIR = Path(__file__).resolve().parent

HTML_FORM = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Generador de Video</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
      .card { max-width: 900px; margin: 0 auto; padding: 24px; border: 1px solid #ddd; border-radius: 12px; }
      label { display:block; font-weight:600; margin: 12px 0 6px; }
      input[type=text], textarea { width: 100%; box-sizing: border-box; padding: 12px; border: 1px solid #ccc; border-radius: 8px; }
      textarea { min-height: 220px; }
      button { margin-top: 16px; padding: 12px 16px; border: 0; border-radius: 10px; background: black; color: white; font-weight: 700; }
      pre { background: #0b1020; color: #cfe3ff; padding: 16px; border-radius: 10px; overflow:auto; }
      .small { color:#666; font-size: 12px; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Generador de Video</h1>
      <form method="POST" action="/run">
        <label for="nombre">Nombre del proyecto</label>
        <input type="text" id="nombre" name="nombre" placeholder="Agrega el título de tu video SIN ESPACIOS" required>

        <label for="guion">Guion / Script</label>
        <textarea id="guion" name="guion" placeholder="Pega aquí tu guion..." required></textarea>

        <button type="submit">Generar video</button>
      </form>
      {% if log %}
      <h2>Resultado</h2>
      <pre>{{ log }}</pre>
      {% if output_path %}
        <p>XML generado: <strong>{{ output_path }}</strong></p>
        <p class="small">Importa el XML en tu programa de edición</p>
      {% endif %}
      {% endif %}
    </div>
  </body>
</html>
"""

app = Flask(__name__)

def run_cmd(cmd, env=None):
    """Run a command and return (rc, stdout+stderr)."""
    try:
        out = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        combined = (out.stdout or "") + ("\n" + out.stderr if out.stderr else "")
        return out.returncode, combined
    except Exception as e:
        return 1, f"[EXCEPTION] {e}"

def find_generated_xml(project_name: str) -> str | None:
    out = (BASE_DIR / project_name / f"{project_name}.xml")
    if out.exists():
        return str(out)
    return None

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_FORM, log=None, output_path=None)

@app.route("/run", methods=["POST"])
def run_pipeline():
    nombre = (request.form.get("nombre") or "").strip()
    guion = (request.form.get("guion") or "").strip()

    if not nombre or not guion:
        return render_template_string(HTML_FORM, log="ERROR: nombre y guion son requeridos.", output_path=None)

    env = os.environ.copy()
    env["NOMBRE"] = nombre
    env["GUION"] = guion

    log = []
    def step(title, cmd, env=None):
        rc, out = run_cmd(cmd, env=env)
        log.append(f"$ {' '.join(cmd)}\n{out}\n[exit {rc}]")
        return rc

    # 1) chunking.py
    rc = step("chunking", [sys.executable, "chunking.py"], env=env)
    if rc != 0:
        return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=None)

    # Read config.json to locate project folder name (created by chunking.py)
    cfg_path = BASE_DIR / "config.json"
    project_name = None
    if cfg_path.exists():
        try:
            import json
            project_name = json.loads(cfg_path.read_text(encoding="utf-8")).get("nombre_proyecto")
        except Exception as e:
            log.append(f"ERROR leyendo config.json: {e}")
    else:
        log.append("WARNING: no se encontró config.json tras chunking.py")

    # 2) image_gen.py
    if (BASE_DIR / "image_gen.py").exists():
        rc = step("image_gen", [sys.executable, "image_gen.py"])
        if rc != 0:
            return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=None)
    else:
        log.append("WARNING: image_gen.py no encontrado, se omite.")

    # 3) voice_gen.py
    if (BASE_DIR / "voice_gen.py").exists():
        rc = step("voice_gen", [sys.executable, "voice_gen.py"])
        if rc != 0:
            return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=None)
    else:
        log.append("WARNING: voice_gen.py no encontrado, se omite.")

    # 4) subtitle_gen.py
    if (BASE_DIR / "subtitle_gen.py").exists():
        rc = step("subtitle_gen", [sys.executable, "subtitle_gen.py"])
        if rc != 0:
            return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=None)
    else:
        log.append("WARNING: subtitle_gen.py no encontrado, se omite.")

    # 5) generate_xml.py
    if (BASE_DIR / "generate_xml.py").exists():
        rc = step("generate_xml", [sys.executable, "generate_xml.py"])
        if rc != 0:
            return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=None)
    else:
        log.append("WARNING: generate_xml.py no encontrado, se omite.")

    xml_path = find_generated_xml(project_name) if project_name else None
    return render_template_string(HTML_FORM, log="\n\n".join(log), output_path=xml_path or "(desconocido)")

if __name__ == "__main__":
    # For local testing: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)