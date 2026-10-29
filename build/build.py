#!/usr/bin/env python3
"""Builds public/ from build/content/*.html  (same system as marketing-raleigh.com).

Each content file starts with "key: value" lines, then a line "---", then the page body HTML.
Keys: path, title, description, kind (home|page|study|plain), eyebrow, h1, sub,
      date, updated, excerpt, file_no (shown on the folder tab), crumb (parent label|/url/),
      noindex (1), topic (e.g. Real estate)

A .js file with the same name as a content file is inlined as that page's script.
Placeholders in bodies: {{STUDIES}} (all studies as index cards), {{RECENT_STUDIES}} (latest 3).

Run:  python3 build/build.py
"""
import html, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "build" / "content"
PUBLIC = ROOT / "public"
SITE = "https://wakecountyinfo.com"
BRAND = "Wake County Info"
TAGLINE = "Data studies · Wake County, NC"
CSS_V = "1"

NAV = [
    ("/#studies", "Studies"),
    ("/#sources", "Data sources"),
    ("/#about", "About"),
]

FONTS = ("https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700"
         "&amp;family=Special+Elite&amp;family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&amp;display=swap")

MARK = ('<svg class="mark" viewBox="0 0 40 32" width="40" height="32" aria-hidden="true">'
        '<path d="M2 6a2 2 0 0 1 2-2h11l4 4h17a2 2 0 0 1 2 2v18a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2z" fill="#E2C98B" stroke="#7A5C1E" stroke-width="1.5"/>'
        '<rect x="7" y="13" width="26" height="2" fill="#7A5C1E" opacity=".5"/><rect x="7" y="18" width="18" height="2" fill="#7A5C1E" opacity=".5"/></svg>')


def parse(fp):
    raw = fp.read_text(encoding="utf-8")
    head, body = raw.split("\n---\n", 1)
    meta = {}
    for line in head.strip().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    meta["body"] = body.strip()
    meta.setdefault("kind", "page")
    return meta


def esc(s):
    return html.escape(s, quote=True)


def nav(path):
    out = []
    for url, label in NAV:
        cur = ' aria-current="page"' if path == url else ""
        out.append(f'<a href="{url}"{cur}>{label}</a>')
    return "".join(out)


def faq_schema(body):
    items = re.findall(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", body, re.S)
    if not items:
        return None
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
        for q, a in items]}


ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": BRAND,
    "url": SITE + "/",
    "description": "Independent data studies about Wake County, North Carolina, built from public records.",
    "areaServed": {"@type": "AdministrativeArea", "name": "Wake County, North Carolina"},
}


def schema(m):
    url = SITE + m["path"]
    graph = []
    k = m["kind"]
    if k == "home":
        graph.append(ORG)
        graph.append({"@type": "WebSite", "@id": SITE + "/#site", "name": BRAND, "url": SITE + "/",
                      "publisher": {"@id": SITE + "/#org"}})
    elif k == "study":
        graph.append({"@type": "Article", "headline": m["h1_plain"], "description": m["description"],
                      "url": url, "datePublished": m.get("date"), "dateModified": m.get("updated", m.get("date")),
                      "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"},
                      "about": {"@type": "AdministrativeArea", "name": "Wake County, North Carolina"},
                      "mainEntityOfPage": url})
        graph.append(ORG)
    else:
        graph.append({"@type": "WebPage", "name": m["title"], "url": url, "description": m["description"]})
    f = faq_schema(m["body"])
    if f:
        graph.append(f)
    crumb = m.get("crumb")
    if crumb and m["path"] != "/":
        label, curl = [x.strip() for x in crumb.split("|")]
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": label, "item": SITE + curl},
            {"@type": "ListItem", "position": 3, "name": m["h1_plain"], "item": url}]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def fmt_date(d):
    y, mo, da = map(int, d.split("-"))
    return date(y, mo, da).strftime("%B %-d, %Y")


def page(m):
    path, title, desc, k = m["path"], m["title"], m["description"], m["kind"]
    h1 = m.get("h1", title)
    robots = "noindex, follow" if m.get("noindex") == "1" else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    crumbs = ""
    if m.get("crumb"):
        label, curl = [x.strip() for x in m["crumb"].split("|")]
        crumbs = f'<p class="crumbs"><a href="/">Home</a> › <a href="{curl}">{esc(label)}</a></p>'
    tab = f'<span class="tab">{esc(m.get("file_no", "FILE"))}</span>'

    if k in ("home", "page") and m.get("eyebrow"):
        cls = "hero" if k == "home" else "hero hero-page"
        hero = (f'<section class="{cls}"><div class="wrap"><div class="folder">{tab}<div class="sheet">{crumbs}'
                f'<p class="stamp">{esc(m["eyebrow"])}</p><h1>{h1}</h1><p class="sub">{m.get("sub", "")}</p>'
                f'</div></div></div></section>')
        inner = f'<div class="wrap narrow entry">{m["body"]}'
    elif k == "study":
        hero = ""
        meta_line = (f'<p class="meta"><span class="field">Topic</span> {esc(m.get("topic", "Real estate"))}'
                     f' <span class="field">Filed</span> <time datetime="{m["date"]}">{fmt_date(m["date"])}</time></p>')
        inner = (f'<article class="wrap narrow entry"><header class="entry-head">{crumbs}{meta_line}<h1>{h1}</h1>'
                 f'<p class="lead">{m.get("sub", "")}</p></header>{m["body"]}')
    else:
        hero = ""
        inner = f'<div class="wrap narrow entry"><header class="entry-head">{crumbs}<h1>{h1}</h1></header>{m["body"]}'

    close = "</article>" if k == "study" else "</div>"
    main = hero + inner + close
    canonical = SITE + path

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{'article' if k == 'study' else 'website'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F4EEDF">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{BRAND} studies" href="/feed/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={CSS_V}">
<script type="application/ld+json">{schema(m)}</script>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">{MARK}<span><strong>{BRAND}</strong><small>{TAGLINE}</small></span></a>
    <nav class="site-nav" aria-label="Main">{nav(path)}</nav>
  </div>
</header>
<main id="content">
{main}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div>
      <strong>{BRAND}</strong>
      <p>Independent data studies about Wake County, North Carolina, built from public records.</p>
    </div>
    <div>
      <p class="label">Index</p>
      <p><a href="/#studies">Studies</a><br><a href="/#sources">Data sources</a><br><a href="/#about">About</a></p>
    </div>
    <p class="fine">© {date.today().year} {BRAND} · Raleigh, North Carolina · Not affiliated with Wake County Government.</p>
  </div>
</footer>
{m.get('script', '')}
</body></html>
"""


def write(path, text):
    out = PUBLIC / path.strip("/") / "index.html" if path != "/" else PUBLIC / "index.html"
    if path == "/404/":
        out = PUBLIC / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")


def card(m):
    return (f'<article class="card"><a href="{m["path"]}"><span class="card-tab">{esc(m.get("file_no", "FILE"))}</span>'
            f'<div class="card-body"><time datetime="{m["date"]}">{fmt_date(m["date"])}</time><h3>{m["h1_plain"]}</h3>'
            f'<p>{esc(m.get("excerpt", m["description"]))}</p></div></a></article>')


def main():
    pages = []
    for fp in sorted(CONTENT.rglob("*.html")):
        m = parse(fp)
        scr = fp.with_suffix(".js")
        if scr.exists():
            m["script"] = "<script>\n" + scr.read_text(encoding="utf-8").strip() + "\n</script>"
        m["h1_plain"] = re.sub(r"<[^>]+>", "", m.get("h1", m["title"]))
        pages.append(m)

    studies = sorted([p for p in pages if p["kind"] == "study"], key=lambda p: p["date"], reverse=True)
    empty = '<p class="empty">No studies filed yet. The first ones are in progress.</p>'
    grid = ('<div class="grid">' + "".join(card(p) for p in studies) + "</div>") if studies else empty
    grid3 = ('<div class="grid">' + "".join(card(p) for p in studies[:3]) + "</div>") if studies else empty
    for p in pages:
        p["body"] = p["body"].replace("{{STUDIES}}", grid).replace("{{RECENT_STUDIES}}", grid3)

    seen = set()
    for p in pages:
        if p["path"] in seen:
            sys.exit("duplicate path " + p["path"])
        seen.add(p["path"])
        write(p["path"], page(p))

    # sitemap (indexable pages only)
    today = date.today().isoformat()
    urls = [p for p in pages if p.get("noindex") != "1" and p["path"] != "/404/"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in sorted(urls, key=lambda p: p["path"]):
        sm.append(f'<url><loc>{SITE}{p["path"]}</loc><lastmod>{p.get("updated", p.get("date", today))}</lastmod></url>')
    sm.append("</urlset>")
    (PUBLIC / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

    # rss (studies)
    items = "".join(
        f"<item><title>{esc(p['h1_plain'])}</title><link>{SITE}{p['path']}</link><guid>{SITE}{p['path']}</guid>"
        f"<pubDate>{date.fromisoformat(p['date']).strftime('%a, %d %b %Y')} 12:00:00 -0400</pubDate>"
        f"<description>{esc(p['description'])}</description></item>" for p in studies)
    rss = (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{BRAND} studies</title>'
           f'<link>{SITE}/</link><description>Data studies about Wake County, NC</description>{items}</channel></rss>\n')
    (PUBLIC / "feed").mkdir(exist_ok=True)
    (PUBLIC / "feed" / "rss.xml").write_text(rss, encoding="utf-8")
    print(f"built {len(pages)} pages, {len(studies)} studies")


if __name__ == "__main__":
    main()
