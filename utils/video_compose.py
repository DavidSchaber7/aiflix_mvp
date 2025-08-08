import os
try:
    # MoviePy v2 (neuer Importpfad)
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_V2 = True
except ImportError:
    # Fallback: MoviePy v1
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_V2 = False

# ---- Helfer für v1/v2 Kompatibilität ----
def _with_duration(clip, seconds):
    return clip.with_duration(seconds) if MOVIEPY_V2 else clip.set_duration(seconds)

def _with_audio(clip, audio_clip):
    return clip.with_audio(audio_clip) if MOVIEPY_V2 else clip.set_audio(audio_clip)

# Non-Image -> PNG-Platzhalter erzeugen
def _ensure_image(path, idx):
    valid_ext = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
    ext = os.path.splitext(path)[1].lower()
    if os.path.exists(path) and ext in valid_ext:
        return path
    from PIL import Image, ImageDraw
    out = f"assets/images/scene_{idx:02d}_autoplaceholder.png"
    img = Image.new("RGB", (1280, 720), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    d.text((40, 40), f"Auto-Platzhalter für: {os.path.basename(path)}", fill=(220, 220, 220))
    img.save(out)
    return out

def compose_video(script_text: str, images: list, voice_file: str | None, fps=24, seconds_per_image=12):
    os.makedirs("assets/out", exist_ok=True)

    if not images:
        from PIL import Image, ImageDraw
        os.makedirs("assets/images", exist_ok=True)
        placeholder = "assets/images/scene_00.png"
        img = Image.new("RGB", (1280, 720), color=(20, 20, 20))
        d = ImageDraw.Draw(img)
        d.text((50, 50), "AIflix Platzhalter – keine Szenen erkannt", fill=(200, 200, 200))
        img.save(placeholder)
        images = [placeholder]

    # Absichern, dass alles Bilddateien sind
    safe_images = [_ensure_image(p, idx) for idx, p in enumerate(images, start=1)]

    # Clips mit Dauer (v2: with_duration, v1: set_duration)
    clips = [_with_duration(ImageClip(p), seconds_per_image) for p in safe_images]
    video = concatenate_videoclips(clips, method="compose")

    # Optional Voiceover
    if voice_file and os.path.exists(voice_file):
        narration = AudioFileClip(voice_file)
        # Falls Audio länger ist: letzte Szene duplizieren, bis es passt
        while video.duration + 0.1 < narration.duration:
            clips.append(clips[-1].copy())
            video = concatenate_videoclips(clips, method="compose")
        # v2: with_audio, v1: set_audio
        video = _with_audio(video, narration)
    else:
        print("ℹ️ Kein Voiceover vorhanden – rendere Video ohne Ton.")

    out_path = "assets/out/episode.mp4"
    video.write_videofile(out_path, fps=fps, codec="libx264", audio_codec="aac")
    return out_path
