import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

WIDTH = 1080
HEIGHT = 1350
SAFE_MARGIN_X = 64          
SAFE_MARGIN_BOTTOM = 72     
BOX_PADDING_X = 32
BOX_PADDING_Y = 20
BOX_MAX_HEIGHT_RATIO = 0.35 
BOX_BG = (0, 0, 0, 180)     
TEXT_FILL = (255, 255, 255, 255)
START_FONT_SIZE = 64        
MIN_FONT_SIZE = 36
LINE_SPACING_RATIO = 0.12   

CANDIDATE_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def load_font(size: int) -> ImageFont.FreeTypeFont:
    for fp in CANDIDATE_FONTS:
        p = Path(fp)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except Exception:
                continue
    return ImageFont.load_default()

def fit_text_to_box(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int) -> tuple[ImageFont.ImageFont, list[str]]:
    """Reduce el font-size hasta que el bloque entre en el recuadro (max_w x max_h)."""
    size = START_FONT_SIZE
    while size >= MIN_FONT_SIZE:
        font = load_font(size)
        avg_char_w = draw.textlength("M", font=font) or 1
        max_chars = max(8, int(max_w / avg_char_w))
        wrapped = textwrap.wrap(text, width=max_chars)

        line_h = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
        line_spacing = int(line_h * LINE_SPACING_RATIO)
        total_h = len(wrapped) * line_h + (len(wrapped) - 1) * line_spacing

        w_max = 0
        for line in wrapped:
            w = draw.textlength(line, font=font)
            if w > w_max:
                w_max = w
        if w_max <= max_w and total_h <= max_h:
            return font, wrapped
        size -= 2

    font = load_font(MIN_FONT_SIZE)
    wrapped = textwrap.wrap(text, width= max(8, int(max_w / (draw.textlength("M", font=font) or 1))))
    return font, wrapped

def main():
    ROOT = Path(__file__).resolve().parent
    CONFIG_PATH = ROOT / "config.json"
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"No se encontró config.json en {CONFIG_PATH}")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    proyecto = config.get("nombre_proyecto")
    if not proyecto:
        raise ValueError("config.json debe incluir 'nombre_proyecto'")

    PROJ_DIR = ROOT / proyecto
    SLIDES_PATH = PROJ_DIR / "slides.json"
    if not SLIDES_PATH.exists():
        raise FileNotFoundError(f"No se encontró slides.json en {SLIDES_PATH}")

    slides = json.loads(SLIDES_PATH.read_text(encoding="utf-8"))
    subs_dir = PROJ_DIR / "SUBS"
    subs_dir.mkdir(parents=True, exist_ok=True)

    for idx, slide in enumerate(slides, start=1):
        text_screen = (slide.get("texto_pantalla") or "").strip()
        if not text_screen:
            text_screen = ""

        im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)

        max_box_h = int(HEIGHT * BOX_MAX_HEIGHT_RATIO)
        max_box_w = WIDTH - 2 * SAFE_MARGIN_X

        font, lines = fit_text_to_box(draw, text_screen, max_box_w - 2*BOX_PADDING_X, max_box_h - 2*BOX_PADDING_Y)
        line_h = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
        line_spacing = int(line_h * LINE_SPACING_RATIO)
        text_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
        text_w = max((draw.textlength(line, font=font) for line in lines), default=0)

        box_w = min(max_box_w, int(text_w) + 2*BOX_PADDING_X)
        box_h = min(max_box_h, int(text_h) + 2*BOX_PADDING_Y)
        box_left = (WIDTH - box_w) // 2
        box_top = HEIGHT - SAFE_MARGIN_BOTTOM - box_h

        draw.rectangle([box_left, box_top, box_left + box_w, box_top + box_h], fill=BOX_BG)

        y = box_top + BOX_PADDING_Y
        for line in lines:
            w = draw.textlength(line, font=font)
            x = box_left + (box_w - w) // 2
            draw.text((x, y), line, font=font, fill=TEXT_FILL)
            y += line_h + line_spacing

        out_path = subs_dir / f"sub_{idx:04d}.png"
        im.save(out_path, format="PNG")

    print(f"✅ Subs")

if __name__ == "__main__":
    main()
