import argparse
import logging

from utils import config
from utils.story_gen import generate_script
from utils.image_gen import generate_images
from utils.voice_gen import generate_voice
from utils.video_compose import compose_video

def main():
    parser = argparse.ArgumentParser(description="Erzeuge eine AIflix Episode")
    parser.add_argument("--wish", help="Nutzerwunsch für die Episode")
    args = parser.parse_args()

    wish = args.wish or input("🎬 Was möchtest du sehen?\n> ").strip()
    if not wish:
        logging.error("Bitte gib einen Wunsch ein.")
        return

    logging.info("📖 Skript (GPT-5)…")
    script = generate_script(wish)

    logging.info("🖼️ Szenenbilder…")
    images = generate_images(script)

    logging.info("🎤 Voiceover…")
    voice = generate_voice(script)

    logging.info("🎞️ Video rendern…")
    out = compose_video(script, images, voice)

    logging.info(f"✅ Fertig: {out}")

if __name__ == "__main__":
    main()
