#!/bin/bash
# Claude en el Mac: reemplaza la recomendación de respaldo del día por una elegida con criterio.
# launchd lo llama a las 6:30 y cada hora; sale enseguida si Claude ya eligió las de hoy, así que
# corre una sola vez al día, la primera vez que el Mac está prendido después de las 6:30.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
unset ANTHROPIC_API_KEY   # usa el plan de Claude, nunca una clave de pago
# un token de larga duración (claude setup-token), para no depender de la sesión del CLI, que vence
TOKEN_FILE="$HOME/.config/couchtv-recomendaciones/claude-token"
if [ -s "$TOKEN_FILE" ]; then export CLAUDE_CODE_OAUTH_TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"; fi

today=$(TZ=America/Bogota date +%F)
if [ "$(TZ=America/Bogota date +%H%M)" -lt 0630 ] && [ -z "${FORZAR:-}" ]; then exit 0; fi
git pull -q --rebase origin main || { echo "$(date): git pull falló"; exit 0; }
done_today=$(python3 -c "import json;d=json.load(open('recomendaciones.json'));print(d.get('fecha')=='$today' and d.get('fuente')=='claude')")
if [ "$done_today" = True ] && [ -z "${FORZAR:-}" ]; then exit 0; fi

echo "$(date): eligiendo las de $today"
prompt=$(python3 - "$today" <<'PY'
import datetime as dt, json, sys
today = sys.argv[1]
h = json.load(open("historial.json"))
def since(days): return (dt.date.fromisoformat(today) - dt.timedelta(days=days)).isoformat()
recent = sorted({x[k] for x in h if x.get("fecha", "") >= since(14) for k in ("netflix", "prime", "youtube") if x.get(k)})
notes = [x[k] for x in h if x.get("fecha", "") >= since(30) for k in ("mensaje_ehilin", "mensaje_kike") if x.get(k)]
text = open("scripts/prompt-claude.md").read()
print(text.replace("{FECHA}", today).replace("{RECIENTES}", "; ".join(recent) or "nada todavía")
          .replace("{MENSAJES}", "; ".join(notes) or "ninguno todavía"))
PY
)

answer=$(claude -p "$prompt" --model sonnet --allowedTools "WebSearch" "WebFetch" "Bash(curl:*)" </dev/null 2>>"$HOME/Library/Logs/couchtv-recomendaciones.err") \
  || { echo "$(date): claude falló"; exit 0; }
if ! printf '%s' "$answer" | python3 scripts/aplicar_claude.py; then
  echo "$(date): la respuesta no sirvió, se queda el respaldo"; git checkout -q -- recomendaciones.json historial.json; exit 0
fi

git add recomendaciones.json historial.json
git -c user.name="Claude (Mac)" -c user.email="enriquepabon@users.noreply.github.com" \
  commit -q -m "Recomendaciones de Claude del $today"
git push -q origin HEAD:main || { echo "$(date): git push falló"; exit 0; }
echo "$(date): listo"
