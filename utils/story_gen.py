import logging
import os
from openai import BadRequestError

from utils import config

SYSTEM = """Du bist ein preisgekrönter Serienautor.
Erzeuge ein vollständiges Episoden-Drehbuch für 20–40 Minuten.
Struktur:
1) Titel
2) Genre
3) Logline (2 Sätze)
4) Beat-Sheet (Akte & Wendepunkte)
5) Szenenliste (5–8 Szenen, je mit Ort, Zeit, Figuren)
6) Ausgeschriebene Dialoge (mit Sprecherrollen)
7) Erzählertext / Regieanweisungen
Sprache: Deutsch. Filmisch, präzise, produktionstauglich.
"""

def generate_script(user_wish: str) -> str:
    """Create a full episode script from the viewer's wish via OpenAI."""
    prompt = f"""Wunsch des Zuschauers:
{user_wish}

Erzeuge das vollständige Skript gemäß der Struktur. Länge der finalen Episode: 20–40 Minuten."""
    models = ["gpt-5", "gpt-5-chat-latest"]  # Fallback, falls das erste Modell Parameter nicht akzeptiert
    last_err = None
    client = config.get_openai_client()
    for m in models:
        try:
            resp = client.responses.create(
                model=m,
                input=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                # WICHTIG: KEIN temperature hier – einige Modelle erlauben das nicht
                max_output_tokens=6000
            )
            text = resp.output_text
            os.makedirs("assets/scripts", exist_ok=True)
            with open("assets/scripts/script.txt", "w", encoding="utf-8") as f:
                f.write(text)
            return text
        except BadRequestError as e:
            last_err = e
            continue
    # Wenn beide Modelle fehlschlagen:
    if last_err:
        raise last_err
    raise RuntimeError("Unbekannter Fehler beim Generieren des Skripts.")

