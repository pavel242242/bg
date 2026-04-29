#!/usr/bin/env bash
# Spustí hru "Přihořívá hoří":
#  1. instaluje závislosti (uv sync)
#  2. zjistí LAN IP, ať máš link pro mobil
#  3. nastartuje server bound na 0.0.0.0:8765

set -euo pipefail

# Skript běží ze svého adresáře (experiments/word-guess-game).
cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v uv >/dev/null 2>&1; then
  echo "❌  uv není nainstalovaný."
  echo "    macOS / Linux:  curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "    macOS Homebrew: brew install uv"
  exit 1
fi

echo "📦  uv sync …"
uv sync --quiet

# Best-effort pokus zjistit LAN IP, ať se zobrazí mobilní URL.
detect_ip() {
  if command -v ipconfig >/dev/null 2>&1; then           # macOS
    ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null
  elif command -v hostname >/dev/null 2>&1; then         # Linux
    hostname -I 2>/dev/null | awk '{print $1}'
  fi
}
LAN_IP="$(detect_ip || true)"
PORT="${PORT:-8765}"

echo
echo "🔥  Server startuje na 0.0.0.0:${PORT}"
echo "    Lokálně:   http://127.0.0.1:${PORT}"
if [[ -n "${LAN_IP:-}" ]]; then
  echo "    Z mobilu:  http://${LAN_IP}:${PORT}    (mobil i tenhle počítač musí být na stejné WiFi)"
else
  echo "    Z mobilu:  zjisti svojí LAN IP ručně (ifconfig / ip addr)"
fi
echo
echo "    Ctrl-C ukončí server."
echo

exec uv run uvicorn backend.main:app --host 0.0.0.0 --port "${PORT}"
