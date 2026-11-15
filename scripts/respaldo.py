#!/usr/bin/env python3
"""Recomendación de respaldo, sin IA: una por plataforma para hoy (hora de Colombia).

Netflix y Prime Video: lo más popular en Colombia según la API pública de JustWatch.
YouTube: las tendencias de Colombia en kworb.net, sin gameplays ni clickbait.
No repite lo de los últimos 14 días (historial.json). Si una fuente falla, deja la tarjeta que
ya estaba para esa plataforma. Si Claude ya escribió las de hoy, no las toca.

Solo usa la biblioteca estándar de Python, para correr igual en GitHub Actions y en el Mac.
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
RECS, HIST = ROOT / "recomendaciones.json", ROOT / "historial.json"
UA = {"User-Agent": "Mozilla/5.0 (couchtv-recomendaciones)"}
JW = "https://apis.justwatch.com/graphql"
KWORB = "https://kworb.net/youtube/trending/co.html"
NO_REPEAT_DAYS, KEEP_DAYS = 14, 30

# subtitle, la llave en historial.json, el paquete que abre OK, el paquete de JustWatch
PLATFORMS = [("Hoy en Netflix", "netflix", "com.netflix.ninja", "nfx"),
             ("Hoy en Prime Video", "prime", "com.amazon.amazonvideo.livingroom", "prv"),
             ("Hoy en YouTube", "youtube", "com.google.android.youtube.tv", None)]
SKIP_GENRES = {"Infantil", "Kids & Family"}
SKIP_VIDEO = re.compile(r"minecraft|roblox|fortnite|free ?fire|gta|gameplay|#shorts|brawl|"
                        r"among us|banban|\bmods?\b|vs\b|reto|challenge|1.000.000|millonario",
                        re.I)

QUERY = """query($c: Country!, $p: [String!]){ popularTitles(country:$c, first:25,
 filter:{packages:$p}){ edges{ node{ objectType content(country:$c, language:"es"){
 title posterUrl genres{ translation(language:"es") } } } } } }"""


def fetch(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(UA, **({"content-type": "application/json"} if data else {}))
    with urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def cut(text, most):
    text = " ".join(str(text).split())
    return text if len(text) <= most else text[: most - 1].rstrip(" ,.-·:") + "…"


def image_ok(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def streaming(package, recent):
    data = json.loads(fetch(JW, {"query": QUERY, "variables": {"c": "CO", "p": [package]}}))
    for edge in data["data"]["popularTitles"]["edges"]:
        node, c = edge["node"], edge["node"]["content"]
        genres = [g["translation"] for g in c.get("genres") or [] if g.get("translation")]
        if not c.get("title") or not c.get("posterUrl") or c["title"] in recent:
            continue
        if SKIP_GENRES & set(genres):
            continue
        image = "https://images.justwatch.com" + c["posterUrl"].replace("{profile}", "s332").replace("{format}", "jpg")
        if not image_ok(image):
            continue
        kind = "Serie" if node["objectType"] == "SHOW" else "Película"
        fits = [g for g in genres if len(f"{kind} · {g}") <= 24]
        value = f"{kind} · {fits[0]}" if fits else kind
        return {"title": cut(c["title"], 40), "value": cut(value, 24), "image": image}
    return None


def youtube(recent):
    page = fetch(KWORB)
    for vid, title in re.findall(r'href="https://youtu\.be/([\w-]{11})"[^>]*>([^<]+)</a>', page):
        title = html.unescape(title).strip()
        title = re.sub(r"\s*[\(\[](letra|lyrics?|video oficial|official (music )?video|"
                       r"audio oficial|official audio|visualizer|en vivo)[^\)\]]*[\)\]]", "", title, flags=re.I).strip()
        if title in recent or cut(title, 40) in recent or SKIP_VIDEO.search(title):
            continue
        image = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        if image_ok(image):
            return {"title": cut(title, 40), "value": "Tendencia en Colombia", "image": image}
    return None


def main():
    today = dt.datetime.now(ZoneInfo("America/Bogota")).date()
    recs = json.loads(RECS.read_text()) if RECS.exists() else {"cards": []}
    hist = json.loads(HIST.read_text()) if HIST.exists() else []
    if recs.get("fecha") == today.isoformat() and recs.get("fuente") == "claude":
        print("Claude ya eligió las de hoy; no cambio nada.")
        return 0
    since = (today - dt.timedelta(days=NO_REPEAT_DAYS)).isoformat()
    recent = {h.get(k) for h in hist if h.get("fecha", "") >= since for k in ("netflix", "prime", "youtube")}
    before = {c.get("app"): c for c in recs.get("cards", [])}

    cards, picked, kept = [], {"fecha": today.isoformat(), "fuente": "respaldo"}, []
    for subtitle, key, app, package in PLATFORMS:
        try:
            got = streaming(package, recent) if package else youtube(recent)
        except Exception as e:
            print(f"{key}: la fuente falló ({e})", file=sys.stderr)
            got = None
        if got:
            cards.append(dict(subtitle=subtitle, **got, app=app))
            picked[key] = got["title"]
        elif app in before:
            cards.append(before[app])
            kept.append(key)
        print(f"{key}: {got['title'] if got else 'sin cambio'}")

    RECS.write_text(json.dumps({"fecha": today.isoformat(), "fuente": "respaldo", "cards": cards},
                               indent=2, ensure_ascii=False) + "\n")
    keep_from = (today - dt.timedelta(days=KEEP_DAYS)).isoformat()
    hist = [h for h in hist if h.get("fecha", "") >= keep_from and h.get("fecha") != today.isoformat()]
    HIST.write_text(json.dumps(hist + [picked], indent=2, ensure_ascii=False) + "\n")
    if kept:
        print("se dejó la tarjeta anterior para: " + ", ".join(kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
