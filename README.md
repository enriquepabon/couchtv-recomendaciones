# Recomendaciones del día para couch-tv

`recomendaciones.json` tiene una recomendación diaria para Netflix, Prime Video y YouTube en Colombia,
en el formato de las tarjetas propias de [couch-tv](https://github.com/Seagey/couch-tv)
(`home.custom_cards`, docs/TV-HOME.md, "Custom cards"). Una tarea programada de Claude lo actualiza
cada mañana a las 6:00 (hora de Colombia).

Límites del formato: como máximo 12 tarjetas (8 en couch-tv sin el cambio local que sube el límite); `title` hasta 40 caracteres, `value` hasta 24,
`subtitle` hasta 60; `image` solo `https://`; `app` es el paquete Android de la app que abre OK.

## Cómo se actualiza

- **6:00 a.m., GitHub Actions** (`.github/workflows/respaldo.yml`, `scripts/respaldo.py`): sin IA,
  lo más popular del día en Colombia (JustWatch para Netflix y Prime Video, tendencias de kworb.net
  para YouTube), sin repetir lo de las últimas dos semanas. Corre aunque ningún computador esté prendido.
- **Después, Claude en el Mac** (cuando está prendido): busca en internet y reemplaza las del día por
  unas elegidas con criterio (`"fuente": "claude"`). Si ya lo hizo, el respaldo no las toca.

Cada persona ve su **mensaje del día** escrito con letra caligráfica encima de su fila (tarjetas con
`"who"`, `"tipo": "mensaje"` y `"style": "note"`, que couch-tv dibuja como texto, no como tarjeta): para
Ehilin uno amoroso de Enrique, para Kike una afirmación para manifestar éxito. Claude los escribe
cada día; el respaldo toma uno de `mensajes.json` sin repetir los de los últimos 30 días. Después
vienen las tres plataformas y las noticias de cada uno (`"tipo": "noticia"`).

Si Claude falla con "OAuth session expired", la sesión del CLI venció: `claude auth login`, o mejor,
un token de un año con `claude setup-token` guardado en `~/.config/couchtv-recomendaciones/claude-token`
(permiso 600), que `scripts/claude-diario.sh` usa si existe.

`historial.json` guarda lo recomendado los últimos 30 días.
