import os, json, requests, re, tempfile
from dotenv import load_dotenv

load_dotenv()
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "").strip()
VOICE_ID_ENV = os.getenv("ELEVEN_VOICE_ID", "").strip()

ELEVEN_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"
HEADERS_JSON = {"xi-api-key": ELEVEN_API_KEY, "accept":"audio/mpeg", "content-type":"application/json"}
HEADERS_GET  = {"xi-api-key": ELEVEN_API_KEY}

def _pick_voice_id():
    if VOICE_ID_ENV:
        return VOICE_ID_ENV
    r = requests.get("https://api.elevenlabs.io/v1/voices", headers=HEADERS_GET, timeout=30)
    r.raise_for_status()
    data = r.json()
    voices = data.get("voices", [])
    if not voices:
        raise RuntimeError("Keine ElevenLabs-Stimmen im Account gefunden.")
    return voices[0]["voice_id"]

def _split_text(text, max_len=1800):
    # Kompakt machen + in satznahe Chunks teilen
    text = re.sub(r"\s+", " ", text).strip()
    parts, cur = [], ""
    for sent in re.split(r"(?<=[\.!\?\n])\s+", text):
        if len(cur) + len(sent) + 1 <= max_len:
            cur = f"{cur} {sent}".strip()
        else:
            if cur: parts.append(cur)
            cur = sent
    if cur: parts.append(cur)
    return [p for p in parts if p]

def _shorten_for_tts(full_script: str, hard_cap=6000):
    """Versuch: nur Erzähler + wichtige Zeilen, dann hart kürzen."""
    lines = [l.strip() for l in full_script.splitlines() if l.strip()]
    picked = []
    for l in lines:
        if l.lower().startswith(("erzähler", "narrator", "szene", "scene", "int.", "ext.")):
            picked.append(l)
        elif ":" in l and len(l) < 160:  # kurze Dialogzeilen bevorzugen
            picked.append(l)
        if sum(len(x) for x in picked) > hard_cap:
            break
    text = " ".join(picked) or full_script
    # hart kürzen, falls immer noch zu lang
    return text[:hard_cap]

def extract_voice_script(full_script: str) -> str:
    return _shorten_for_tts(full_script, hard_cap=6000)

def generate_voice(script_text: str, out_path="assets/audio/voice.mp3") -> str | None:
    if not ELEVEN_API_KEY:
        print("⚠️ ELEVEN_API_KEY fehlt – überspringe Voice.")
        return None

    os.makedirs("assets/audio", exist_ok=True)

    try:
        voice_id = _pick_voice_id()
    except Exception as e:
        print(f"⚠️ Konnte Voice-ID nicht ermitteln: {e}. Rendere ohne Voice.")
        return None

    text = extract_voice_script(script_text)
    chunks = _split_text(text, max_len=1800)

    tmp_files = []
    try:
        for i, chunk in enumerate(chunks, 1):
            payload = {
                "text": chunk,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
            }
            url = f"{ELEVEN_TTS_URL}/{voice_id}"
            r = requests.post(url, headers=HEADERS_JSON, data=json.dumps(payload), timeout=300)

            # **Robustes Fehlerhandling**: bei 400/401/402/429 -> ohne Voice weitermachen
            if r.status_code in (400, 401, 402, 429):
                print(f"ℹ️ ElevenLabs Problem (HTTP {r.status_code}): {r.text[:200]}")
                print("→ Rendere Episode ohne Voiceover.")
                return None

            r.raise_for_status()  # andere Fehler normal melden

            # chunk speichern
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{i:02d}.mp3")
            tmp.write(r.content)
            tmp.flush(); tmp.close()
            tmp_files.append(tmp.name)

        # Chunks zu einer Datei zusammenfügen
        try:
            from moviepy import AudioFileClip  # v2
            from moviepy import concatenate_audioclips
        except Exception:
            from moviepy.editor import AudioFileClip, concatenate_audioclips  # v1

        clips = [AudioFileClip(p) for p in tmp_files]
        final = concatenate_audioclips(clips) if len(clips) > 1 else clips[0]
        final.write_audiofile(out_path, codec="libmp3lame", fps=44100, bitrate="192k")
        for c in clips:
            c.close()
        return out_path
    finally:
        for p in tmp_files:
            try: os.remove(p)
            except: pass
