
#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate || .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env || true
echo "✅ Umgebung erstellt. Bitte trage deine API-Keys in .env ein."
