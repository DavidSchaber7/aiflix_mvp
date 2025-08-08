import os, base64, re, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Erlaubte Sizes laut API: "1024x1024", "1536x1024", "1024x1536", "auto"
IMG_SIZE = "1536x1024"  # 16:9-ähnlich (Landscape). Alternativ: "auto"

def _scene_prompts_from_script(script_text: str, max_scenes=8):
    lines = [l.strip() for l in script_text.splitlines() if l.strip()]
    scenes = []
    for l in lines:
        if re.match(r"^(Szene|Scene|Szenenbild)\b", l, flags=re.IGNORECASE):
            scenes.append(l)
    if not scenes:
        # Fallback: nimm markante Absätze
        scenes = [l for l in lines if len(l) > 40][:max_scenes]
    return scenes[:max_scenes]

# ... oben unverändert ...

def generate_images(script_text: str):
    os.makedirs("assets/images", exist_ok=True)
    prompts = _scene_prompts_from_script(script_text)

    image_paths = []
    for i, p in enumerate(prompts, start=1):
        try:
            img = client.images.generate(
                model="gpt-image-1",
                prompt=f"Szenenbild für: {p}. Filmischer Stil, 16:9-Anmutung, hochauflösend, kinoreif.",
                size=IMG_SIZE,
                n=1
            )
            b64 = img.data[0].b64_json
            path = f"assets/images/scene_{i:02d}.png"
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
            image_paths.append(path)
        except Exception as e:
            # PNG-Platzhalter statt .txt erzeugen
            from PIL import Image, ImageDraw
            path = f"assets/images/scene_{i:02d}_placeholder.png"
            img = Image.new("RGB", (1280, 720), color=(25, 25, 25))
            d = ImageDraw.Draw(img)
            d.text((40, 40), f"Platzhalter: {str(e)[:70]}...", fill=(220, 220, 220))
            d.text((40, 100), f"Prompt: {p[:70]}...", fill=(180, 180, 180))
            img.save(path)
            image_paths.append(path)

    # Falls gar nichts erzeugt wurde, einen Platzhalter erzeugen
    if not image_paths:
        from PIL import Image, ImageDraw
        path = "assets/images/scene_00_placeholder.png"
        img = Image.new("RGB", (1280, 720), color=(25, 25, 25))
        d = ImageDraw.Draw(img)
        d.text((40, 40), "Keine Szenen generiert", fill=(220, 220, 220))
        img.save(path)
        image_paths = [path]

    return image_paths

