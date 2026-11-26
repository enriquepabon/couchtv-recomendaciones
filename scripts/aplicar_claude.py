#!/usr/bin/env python3
"""Lee la respuesta de Claude (JSON) por la entrada estándar, la valida y la escribe en
recomendaciones.json e historial.json con "fuente": "claude". Sale con 1 si no sirve: así el
respaldo del día se queda como está.
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from respaldo import HIST, KEEP_DAYS, MESSAGES, PLATFORMS, RECS, UA, cut, message_card  # noqa: E402

URL_RE = re.compile(r"^https://[^\s'\"<>\\`$]+$")


def image_ok(url):
    if not URL_RE.match(url or ""):
        return False
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
            return r.status == 200 and r.headers.get_content_type().startswith("image/")
    except Exception:
        return False


def main():
    raw = sys.stdin.read()
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        print("Claude no devolvió JSON", file=sys.stderr)
        return 1
    try:
        answer = json.loads(raw[start:end + 1])
    except ValueError as e:
        print(f"JSON inválido: {e}", file=sys.stderr)
        return 1

    today = dt.datetime.now(ZoneInfo("America/Bogota")).date().isoformat()
    recs = json.loads(RECS.read_text()) if RECS.exists() else {"cards": []}
    before = {c.get("app"): c for c in recs.get("cards", [])}
    cards, entry, new = [], {"fecha": today, "fuente": "claude"}, 0
    # el mensaje del día de cada persona; si Claude no trae uno que quepa, el del respaldo de hoy
    for who, _, _ in MESSAGES:
        text = answer.get("mensaje_" + who)
        text = " ".join(text.split()) if isinstance(text, str) else ""
        if 0 < len(text) <= 40:
            cards.append(message_card(who, text))
            entry["mensaje_" + who] = text
            new += 1
        else:
            cards += [c for c in recs.get("cards", []) if c.get("who") == [who] and c.get("tipo") == "mensaje"]
            print(f"mensaje_{who}: sin un mensaje válido, se deja el anterior", file=sys.stderr)
    for subtitle, key, app, _ in PLATFORMS:
        pick = answer.get(key)
        if isinstance(pick, dict) and isinstance(pick.get("title"), str) and image_ok(pick.get("image")):
            card = {"subtitle": subtitle, "title": cut(pick["title"], 40),
                    "value": cut(pick.get("value") or "", 24), "image": pick["image"], "app": app}
            if not card["value"]:
                del card["value"]
            cards.append(card)
            entry[key] = card["title"]
            if pick.get("por_que"):
                entry[key + "_por_que"] = cut(pick["por_que"], 200)
            new += 1
        elif app in before:
            cards.append(before[app])
            print(f"{key}: sin una elección válida, se deja la anterior", file=sys.stderr)
    # noticias: dos por persona, con su "who"; si Claude no trae nada válido, las que ya estaban
    for field, who, label in (("noticias_ia", "kike", "IA"), ("noticias_mundo", "ehilin", "Mundo")):
        items = []
        for n in answer.get(field) or [] if isinstance(answer.get(field), list) else []:
            if not isinstance(n, dict) or not isinstance(n.get("title"), str) or not n["title"].strip():
                continue
            link = n.get("url") if isinstance(n.get("url"), str) else ""
            if not (URL_RE.match(link) and len(link) <= 1000):
                continue
            source = " ".join(str(n.get("fuente") or "").split())
            items.append({"subtitle": cut(f"{label} · {source}" if source else label, 60),
                          "title": cut(n["title"], 40), "url": link, "who": [who], "tipo": "noticia"})
            if len(items) >= 2:
                break
        if items:
            entry[field] = [i["title"] for i in items]
            new += 1
        else:
            items = [c for c in recs.get("cards", []) if c.get("who") == [who] and c.get("url")]
            print(f"{field}: sin noticias válidas, se dejan las anteriores", file=sys.stderr)
        cards += items
    if new == 0:
        print("Ninguna elección válida", file=sys.stderr)
        return 1

    RECS.write_text(json.dumps({"fecha": today, "fuente": "claude", "cards": cards},
                               indent=2, ensure_ascii=False) + "\n")
    hist = json.loads(HIST.read_text()) if HIST.exists() else []
    keep_from = (dt.date.fromisoformat(today) - dt.timedelta(days=KEEP_DAYS)).isoformat()
    hist = [h for h in hist if h.get("fecha", "") >= keep_from and h.get("fecha") != today]
    HIST.write_text(json.dumps(hist + [entry], indent=2, ensure_ascii=False) + "\n")
    for _, key, _, _ in PLATFORMS:
        if key in entry:
            print(f"{key}: {entry[key]} — {entry.get(key + '_por_que', '')}")
    for who, _, _ in MESSAGES:
        if "mensaje_" + who in entry:
            print(f"mensaje_{who}: {entry['mensaje_' + who]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
