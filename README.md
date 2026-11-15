# Recomendaciones del día para couch-tv

`recomendaciones.json` tiene una recomendación diaria para Netflix, Prime Video y YouTube en Colombia,
en el formato de las tarjetas propias de [couch-tv](https://github.com/Seagey/couch-tv)
(`home.custom_cards`, docs/TV-HOME.md, "Custom cards"). Una tarea programada de Claude lo actualiza
cada mañana a las 6:00 (hora de Colombia).

Límites del formato: como máximo 8 tarjetas; `title` hasta 40 caracteres, `value` hasta 24,
`subtitle` hasta 60; `image` solo `https://`; `app` es el paquete Android de la app que abre OK.
