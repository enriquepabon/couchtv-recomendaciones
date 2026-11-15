#!/bin/bash
# Claude en el Mac: reemplaza la recomendación de respaldo del día por una elegida con criterio.
# launchd lo llama a las 6:30 y cada hora; sale enseguida si Claude ya eligió las de hoy, así que
# corre una sola vez al día, la primera vez que el Mac está prendido después de las 6:30.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
unset ANTHROPIC_API_KEY   # usa el plan de Claude, nunca una clave de pago

today=$(TZ=America/Bogota date +%F)
if [ "$(TZ=America/Bogota date +%H%M)" -lt 0630 ] && [ -z "${FORZAR:-}" ]; then exit 0; fi
git pull -q --rebase origin main || { echo "$(date): git pull falló"; exit 0; }
done_today=$(python3 -c "import json;d=json.load(open('recomendaciones.json'));print(d.get('fecha')=='$today' and d.get('fuente')=='claude')")
if [ "$done_today" = True ] && [ -z "${FORZAR:-}" ]; then exit 0; fi

echo "$(date): eligiendo las de $today"
recent=$(python3 -c "
import json,datetime as dt
h=json.load(open('historial.json'));since=(dt.date.fromisoformat('$today')-dt.timedelta(days=14)).isoformat()
print('; '.join(sorted({x[k] for x in h if x.get('fecha','')>=since for k in ('netflix','prime','youtube') if x.get(k)})) or 'nada todavía')")
prompt=$(sed -e "s|{FECHA}|$today|" -e "s|{RECIENTES}|${recent//|/-}|" scripts/prompt-claude.md)

answer=$(claude -p "$prompt" --model sonnet --allowedTools "WebSearch" "WebFetch" "Bash(curl:*)" 2>>"$HOME/Library/Logs/couchtv-recomendaciones.err") \
  || { echo "$(date): claude falló"; exit 0; }
if ! printf '%s' "$answer" | python3 scripts/aplicar_claude.py; then
  echo "$(date): la respuesta no sirvió, se queda el respaldo"; git checkout -q -- recomendaciones.json historial.json; exit 0
fi

git add recomendaciones.json historial.json
git -c user.name="Claude (Mac)" -c user.email="enriquepabon@users.noreply.github.com" \
  commit -q -m "Recomendaciones de Claude del $today"
git push -q origin HEAD:main || { echo "$(date): git push falló"; exit 0; }
echo "$(date): listo"
