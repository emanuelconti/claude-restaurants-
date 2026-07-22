#!/usr/bin/env bash
# Avvio guidato di Sowld: prima volta configura tutto da solo,
# le volte dopo chiede solo cosa cercare.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Prima configurazione, un attimo..."
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

if ! grep -q "^ANTHROPIC_API_KEY=.\+" .env 2>/dev/null; then
  echo ""
  echo "Serve la tua chiave Anthropic (una volta sola)."
  echo "Prendila su https://console.anthropic.com/ -> API Keys -> Create Key"
  read -rp "Incollala qui e premi invio: " key
  if grep -q "^ANTHROPIC_API_KEY=" .env; then
    sed -i.bak "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=${key}|" .env && rm -f .env.bak
  else
    echo "ANTHROPIC_API_KEY=${key}" >> .env
  fi
fi

echo ""
read -rp "Cosa cerchi? (es. \"bici da corsa\"): " query
read -rp "In che città? (es. \"Barcellona\"): " city

.venv/bin/python -m sowld "$query" "$city"
