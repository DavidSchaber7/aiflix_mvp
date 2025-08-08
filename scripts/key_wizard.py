
"""
Interaktiver Key-Wizard.
- Fragt Keys ab
- Schreibt .env
- Optional: Test-Endpunkte aufrufen (OpenAI / ElevenLabs)
"""
import os, sys, json, requests

ENV_PATH = ".env"

def prompt(msg):
    try:
        return input(msg).strip()
    except KeyboardInterrupt:
        print("\nAbbruch."); sys.exit(1)

def write_env(values: dict):
    lines = []
    if os.path.exists(ENV_PATH):
        # Preserve existing non-empty
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            existing = f.read().splitlines()
        keep = [l for l in existing if l and not l.startswith(("OPENAI_API_KEY=","ELEVEN_API_KEY=","ELEVEN_VOICE_ID="))]
        lines.extend(keep)
    for k,v in values.items():
        lines.append(f"{k}={v}")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✅ .env aktualisiert → {ENV_PATH}")

def test_openai(key: str):
    print("🔎 Teste OpenAI…")
    try:
        headers = {"Authorization": f"Bearer {key}", "Content-Type":"application/json"}
        # Lightweight list models
        r = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=20)
        if r.status_code == 200:
            print("✅ OpenAI-Key scheint gültig.")
        else:
            print(f"⚠️ OpenAI-Test fehlgeschlagen: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"⚠️ OpenAI-Test Fehler: {e}")

def test_eleven(key: str, voice_id: str):
    print("🔎 Teste ElevenLabs…")
    try:
        headers = {"xi-api-key": key}
        r = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=20)
        if r.status_code == 200:
            print("✅ ElevenLabs-Key scheint gültig.")
        else:
            print(f"⚠️ ElevenLabs-Test fehlgeschlagen: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"⚠️ ElevenLabs-Test Fehler: {e}")

def main():
    print("=== AIflix Key Wizard ===")
    openai_key = prompt("OpenAI API Key (sk-...): ")
    eleven_key = prompt("ElevenLabs API Key (eleven_...): ")
    voice_id = prompt("ElevenLabs Voice ID (z.B. 21m00Tcm4TlvDq8ikWAM) [Enter = Standard]: ") or "21m00Tcm4TlvDq8ikWAM"
    write_env({"OPENAI_API_KEY":openai_key, "ELEVEN_API_KEY":eleven_key, "ELEVEN_VOICE_ID":voice_id})

    test = prompt("Keys testen? (j/n): ").lower()
    if test.startswith("j"):
        if openai_key:
            test_openai(openai_key)
        if eleven_key:
            test_eleven(eleven_key, voice_id)

if __name__ == "__main__":
    main()
