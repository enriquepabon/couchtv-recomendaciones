Elige UNA recomendación de hoy ({FECHA}) para Netflix, UNA para Prime Video y UNA para YouTube,
para una pareja adulta en Barranquilla, Colombia, que las verá en el TV de la sala.

No repitas nada de lo recomendado estos días: {RECIENTES}

Netflix y Prime Video:
- Lo más popular en Colombia hoy, de la API pública de JustWatch (sin clave):
  curl -s https://apis.justwatch.com/graphql -H 'content-type: application/json' -d '{"query":"query($c: Country!, $p: [String!]){ popularTitles(country:$c, first:20, filter:{packages:$p}){ edges{ node{ objectType content(country:$c, language:\"es\"){ title originalReleaseYear posterUrl shortDescription genres{ translation(language:\"es\") } } } } } }","variables":{"c":"CO","p":["nfx"]}}'
  (cambia "nfx" por "prv" para Prime Video). La portada es https://images.justwatch.com + posterUrl,
  con {profile} → s332 y {format} → jpg.
- Busca además en internet estrenos y recomendaciones de esta semana para Colombia
  ("estrenos Netflix Colombia esta semana", "qué ver en Prime Video hoy", reseñas recientes).
  Prefiere un estreno reciente o algo muy comentado y bien valorado; si no, algo popular de JustWatch.
- Nada infantil para niños pequeños ni explícitamente para adultos. Varía: no siempre serie, no
  siempre el número 1.

YouTube:
- Tendencias de Colombia: https://kworb.net/youtube/trending/co.html (los enlaces son
  https://youtu.be/<id>). Si falla, busca "tendencias YouTube Colombia hoy".
- Elige algo que valga la pena en el TV: música oficial, un documental, un programa, algo del día.
  Nada de gameplays para niños (Minecraft, Roblox...), clickbait ni contenido ofensivo.
- La portada es https://i.ytimg.com/vi/<id>/hqdefault.jpg.

Comprueba con curl que cada portada responde 200.

Noticias (de las últimas 24 a 48 horas, en español; busca en internet):
- noticias_ia: las 2 noticias de inteligencia artificial más relevantes para Kike, que construye
  herramientas con IA (agentes, Claude, automatización) en una empresa en Colombia: lanzamientos de
  modelos y herramientas, cambios en Anthropic, OpenAI o Google, y cómo se usa la IA en las
  empresas. Nada de notas genéricas tipo "la IA cambiará el mundo".
- noticias_mundo: las 2 noticias del mundo más importantes del día para Ehilin: lo que de verdad
  pasa en el mundo (y en Colombia si es grande), no farándula ni chismes.
- Para cada una: un titular tuyo, claro y corto (máximo 40 caracteres), el nombre del medio y el
  enlace https a la nota original (no a un buscador ni a Google News).

Responde SOLO con este JSON, sin texto antes ni después y sin bloque de código:
{"netflix": {"title": "...", "value": "Serie · Drama", "image": "https://...", "por_que": "..."},
 "prime": {"title": "...", "value": "Película · Comedia", "image": "https://...", "por_que": "..."},
 "youtube": {"title": "...", "value": "Tendencia en Colombia", "image": "https://i.ytimg.com/vi/<id>/hqdefault.jpg", "por_que": "..."},
 "noticias_ia": [{"title": "...", "fuente": "...", "url": "https://..."}, {...}],
 "noticias_mundo": [{"title": "...", "fuente": "...", "url": "https://..."}, {...}]}

- title: el título en español como sale en Colombia, máximo 40 caracteres (acórtalo con sentido).
- value: máximo 24 caracteres ("Serie · <género>", "Película · <género>", o algo corto para YouTube).
- por_que: una frase corta de por qué lo elegiste (va al historial, no al TV).
- Si para una plataforma no encuentras nada confiable, pon null en vez del objeto.
