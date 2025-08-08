from dotenv import load_dotenv
from utils.story_gen import generate_script
from utils.image_gen import generate_images
from utils.voice_gen import generate_voice
from utils.video_compose import compose_video

def main():
    load_dotenv()
    wish = input("🎬 Was möchtest du sehen?\n> ").strip()
    if not wish:
        print("Bitte gib einen Wunsch ein.")
        return

    print("📖 Skript (GPT-5)…")
    script = generate_script(wish)

    print("🖼️ Szenenbilder…")
    images = generate_images(script)

    print("🎤 Voiceover…")
    voice = generate_voice(script)

    print("🎞️ Video rendern…")
    out = compose_video(script, images, voice)

    print(f"✅ Fertig: {out}")

if __name__ == "__main__":
    main()