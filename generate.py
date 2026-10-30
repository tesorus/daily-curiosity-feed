"""Generate five AI-curated RSS headlines from public source feeds."""
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import feedparser
from openai import OpenAI

now = datetime.now(timezone.utc)
sources = json.loads(Path("sources.json").read_text(encoding="utf-8"))
candidates, seen = [], set()
for source in sources:
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:20]:
            url = entry.get("link", "")
            title = re.sub(r"<[^>]*>", "", entry.get("title", "")).strip()
            if not url.startswith("http") or not title or url in seen:
                continue
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            date = datetime.fromtimestamp(time.mktime(published), timezone.utc) if published else now
            if date < now - timedelta(days=5):
                continue
            seen.add(url)
            candidates.append({"url": url, "title": title[:200], "category": source["category"], "date": date.isoformat()})
    except Exception as exc:
        print(f"Skipping {source['url']}: {exc}")
if len(candidates) < 5:
    raise RuntimeError("Fewer than five current candidates; preserving previous feed")
candidates.sort(key=lambda x: x["date"], reverse=True)
candidates = candidates[:80]

response = OpenAI().responses.create(
    model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    instructions=(
        "Tu sélectionnes cinq articles pour une revue quotidienne en français. "
        "Le lecteur aime le développement logiciel, l'IA, les mathématiques, la science, "
        "l'économie, la géopolitique, la Suisse, l'énergie solaire et les découvertes insolites. "
        "Privilégie la pertinence, la variété et la nouveauté. "
        "Tu ne connais que les titres et métadonnées: n'invente pas le contenu des articles. "
        "Retourne uniquement un JSON: "
        "{\"picks\":[{\"url\":\"URL exacte fournie\",\"summary\":\"une phrase prudente en français\"}]}. "
        "Exactement cinq URLs distinctes, prises dans la liste."
    ),
    input=json.dumps(candidates, ensure_ascii=False),
)
raw = response.output_text.strip()
if raw.startswith("```"):
    raw = re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", raw).strip()
picks = json.loads(raw)["picks"]
by_url = {c["url"]: c for c in candidates}
chosen, selected = [], set()
for pick in picks:
    url = pick.get("url")
    if url in by_url and url not in selected:
        selected.add(url)
        chosen.append({**by_url[url], "summary": str(pick.get("summary", ""))[:500]})
if len(chosen) != 5:
    raise RuntimeError("Invalid selection; preserving previous feed")

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
for tag, value in [
    ("title", "Ma revue quotidienne — cinq découvertes"),
    ("link", "https://tesorus.github.io/daily-curiosity-feed/"),
    ("description", "Cinq actualités choisies chaque matin selon mes centres d'intérêt."),
    ("language", "fr-FR"),
    ("lastBuildDate", format_datetime(now)),
]:
    ET.SubElement(channel, tag).text = value
for article in chosen:
    item = ET.SubElement(channel, "item")
    for tag, value in [
        ("title", article["title"]),
        ("link", article["url"]),
        ("guid", article["url"]),
        ("description", article["summary"] + " — " + article["category"]),
        ("category", article["category"]),
        ("pubDate", format_datetime(now)),
    ]:
        ET.SubElement(item, tag).text = value
Path("docs").mkdir(exist_ok=True)
ET.indent(rss, space="  ")
ET.ElementTree(rss).write("docs/feed.xml", encoding="utf-8", xml_declaration=True)
Path("docs/.nojekyll").touch()
Path("docs/index.html").write_text(
    '<!doctype html><html lang="fr"><meta charset="utf-8">'
    '<title>Ma revue quotidienne</title><h1>Ma revue quotidienne</h1>'
    '<p><a href="feed.xml">Consulter le flux RSS</a></p></html>',
    encoding="utf-8",
)
print("Published five items")
