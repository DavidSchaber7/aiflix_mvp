
# AIflix MVP (GPT‑5 Edition)

**Ziel:** Vollautomatisches Generieren einer 20–40-minütigen Episode aus einem Nutzerwunsch.
Aktuell: MVP (Skript → Bilder → Voice → Slideshow-Video).

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# API-Keys in .env eintragen
```

**FFmpeg installieren** (für Video-Export):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: https://www.gyan.dev/ffmpeg/builds/

## 2) Start

```bash
python main.py
```

## 3) API Keys
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io
- (später) Nebius Object Storage: https://nebius.com/

## 4) Hinweise
- Dieses MVP nutzt vorerst eine Slideshow. Für echte KI-Videoclips integriere später Runway/Veo/Pika.
- Stimmen pro Figur, Lipsync, Untertitel & Musik sind als nächste Schritte vorgesehen.

## 5) Sicherheit
- Halte deine API-Keys strikt geheim (nicht commiten). Verwende `.env`.
