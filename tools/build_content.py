"""Build the Artikel and Kebijakan sections of connectingnusantara.com.

Sources (edit these):
  content/artikel/<slug>.md   one file per article (front matter + Markdown)
  content/kebijakan.json      list of regulations for /kebijakan/

Run from the site root:  python3 tools/build_content.py
Writes: artikel/index.html, artikel/<slug>/index.html, kebijakan/index.html,
        data/artikel.json, data/kebijakan.json, feed.xml
Needs only the Python standard library.
"""
import html, json, os, re, shutil
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.connectingnusantara.com"
CATEGORIES = ["Kabar", "Konsep", "Data & Statistik", "Regulasi", "Aksesibilitas"]
MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

esc = lambda s: html.escape(str(s or ""), quote=True)


def fmt_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def page(title, desc, base, page_id, body, extra_head=""):
    return f"""<!doctype html>
<html lang="id" data-base="{base}" data-page="{page_id}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="Connecting Nusantara" href="{base}feed.xml">
{extra_head}</head>
<body>
<main>
{body}
</main>
<script src="{base}assets/site.js"></script>
</body>
</html>
"""


# ---------- tiny Markdown ----------
LIST_MARK = re.compile(r"^(- |\* |\d+\. )")

def inline(t):
    t = esc(t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", t)
    return t


def markdown(md):
    out, lst = [], None
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = block.strip().split("\n")
        if all(re.match(r"^(- |\* |\d+\. )", l) for l in lines):
            tag = "ol" if re.match(r"^\d+\. ", lines[0]) else "ul"
            items = "".join("<li>" + inline(LIST_MARK.sub("", l)) + "</li>" for l in lines)
            out.append(f"<{tag}>{items}</{tag}>")
        elif m := re.match(r"^(#{2,4}) (.*)", lines[0]):
            out.append(f"<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>")
            if len(lines) > 1: out.append(f"<p>{inline(' '.join(lines[1:]))}</p>")
        elif re.match(r"^!\[[^\]]*\]\([^)]+\)$", block.strip()):
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", block.strip())
            out.append(f'<figure><img src="{esc(m.group(2))}" alt="{esc(m.group(1))}" loading="lazy"><figcaption>{esc(m.group(1))}</figcaption></figure>')
        elif block.startswith("> "):
            out.append(f"<blockquote>{inline(' '.join(l[2:] for l in lines))}</blockquote>")
        else:
            out.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


def read_article(path):
    raw = open(path, encoding="utf-8").read()
    _, fm, body = raw.split("---", 2)
    meta = {}
    for line in fm.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1); meta[k.strip()] = v.strip()
    meta["slug"] = os.path.basename(path)[:-3]
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["body"] = body.strip()
    words = len(re.findall(r"\w+", body))
    meta["minutes"] = max(1, round(words / 200))
    if meta.get("category") not in CATEGORIES:
        raise SystemExit(f"{path}: category must be one of {CATEGORIES}")
    return meta


def article_card(a, base):
    hero = f'<img src="{base}{esc(a["hero"])}" alt="" loading="lazy">' if a.get("hero") else f'<div class="ph" aria-hidden="true">{esc(a["category"])}</div>'
    lang = ' <span class="tag">EN</span>' if a.get("lang") == "en" else ""
    return f"""<a class="card post-card" href="{base}artikel/{a['slug']}/" data-cat="{esc(a['category'])}">
  <div class="thumb">{hero}</div>
  <div class="post-body"><div class="small muted"><span class="cat">{esc(a['category'])}</span> · {fmt_date(a['date'])}{lang}</div>
  <h3>{esc(a['title'])}</h3><p class="small muted">{esc(a.get('summary'))}</p></div></a>"""


def build():
    arts = sorted((read_article(os.path.join(ROOT, "content/artikel", f))
                   for f in os.listdir(os.path.join(ROOT, "content/artikel")) if f.endswith(".md")),
                  key=lambda a: a["date"], reverse=True)

    # clean old generated article folders
    adir = os.path.join(ROOT, "artikel"); os.makedirs(adir, exist_ok=True)
    for d in os.listdir(adir):
        if os.path.isdir(os.path.join(adir, d)): shutil.rmtree(os.path.join(adir, d))

    for i, a in enumerate(arts):
        base = "../../"
        hero = f'<img class="post-hero" src="{base}{esc(a["hero"])}" alt="">' if a.get("hero") else ""
        tags = "".join(f'<span class="tag">{esc(t)}</span> ' for t in a["tags"])
        newer = arts[i - 1] if i > 0 else None
        older = arts[i + 1] if i + 1 < len(arts) else None
        nav = '<nav class="post-nav">' + (
            f'<a href="{base}artikel/{older["slug"]}/">← {esc(older["title"])}</a>' if older else "<span></span>") + (
            f'<a href="{base}artikel/{newer["slug"]}/">{esc(newer["title"])} →</a>' if newer else "<span></span>") + "</nav>"
        note = (f'<p class="small muted">Artikel ini dipindahkan dari situs Connecting Nusantara sebelumnya.</p>'
                if a.get("migrated_from") else "")
        body = f"""<article class="wrap post">
  <p class="eyebrow"><a href="{base}artikel/">Artikel</a> · {esc(a['category'])}</p>
  <h1>{esc(a['title'])}</h1>
  <p class="small muted">{fmt_date(a['date'])} · {a['minutes']} menit baca</p>
  {hero}
  <div class="prose" lang="{esc(a.get('lang', 'id'))}">
{markdown(a['body'])}
  </div>
  <p>{tags}</p>
  {note}
  {nav}
</article>"""
        os.makedirs(os.path.join(adir, a["slug"]), exist_ok=True)
        open(os.path.join(adir, a["slug"], "index.html"), "w", encoding="utf-8").write(
            page(f"{a['title']} · Connecting Nusantara", a.get("summary", ""), base, "artikel/", body))

    # listing
    chips = '<button class="chip active" data-f="">Semua</button>' + "".join(
        f'<button class="chip" data-f="{esc(c)}">{esc(c)}</button>' for c in CATEGORIES if any(a["category"] == c for a in arts))
    body = f"""<div class="wrap">
  <p class="eyebrow">Artikel</p>
  <h1>Artikel, analisis, dan kabar</h1>
  <p class="muted" style="max-width:760px">Tulisan tentang kesenjangan digital di Indonesia: konsep, data, regulasi, dan perkembangan terbaru dari Connecting Nusantara.
    Ikuti lewat <a href="../feed.xml">RSS</a>.</p>
  <div class="chips" role="group" aria-label="Filter kategori">{chips}</div>
  <div class="grid post-grid">
{''.join(article_card(a, '../') for a in arts)}
  </div>
</div>
<script>
function applyCat(f) {{
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('active', x.dataset.f === f));
  document.querySelectorAll('.post-card').forEach(c => c.hidden = !!f && c.dataset.cat !== f);
}}
document.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () => {{ applyCat(b.dataset.f); history.replaceState(null, '', b.dataset.f ? '#' + encodeURIComponent(b.dataset.f) : location.pathname); }}));
const h = decodeURIComponent(location.hash.slice(1)); if (h && document.querySelector(`.chip[data-f="${{CSS.escape(h)}}"]`)) applyCat(h);
</script>"""
    open(os.path.join(adir, "index.html"), "w", encoding="utf-8").write(
        page("Artikel · Connecting Nusantara", "Artikel, analisis kebijakan, dan kabar terbaru tentang kesenjangan digital di Indonesia.", "../", "artikel/", body))

    # kebijakan
    kb = json.load(open(os.path.join(ROOT, "content/kebijakan.json"), encoding="utf-8"))
    by_slug = {a["slug"]: a for a in arts}
    cat_name = {c["id"]: c["name"] for c in kb["categories"]}
    items = sorted(kb["items"], key=lambda it: -it["year"])

    def review_links(it):
        revs = [by_slug[x] for x in it.get("articles", []) if x in by_slug]
        if not revs: return ""
        links = "".join(f'<li><a href="../artikel/{r["slug"]}/">{esc(r["title"])}</a></li>' for r in revs)
        return f'<div class="pol-reviews"><span>Ulasan kami</span><ul>{links}</ul></div>'

    cards = "".join(f"""<article class="pol-card" data-cat="{esc(it['category'])}">
  <div class="pol-top"><span class="pol-cat">{esc(cat_name.get(it['category'], ''))}</span><span class="pol-year">{it['year']}</span></div>
  <h3>{esc(it['short'])}</h3>
  <p class="pol-num">{esc(it['number'])} · <span class="pol-status">{esc(it['status'])}</span></p>
  <p class="pol-meaning"><strong>Apa artinya:</strong> {esc(it['meaning'])}</p>
  {review_links(it)}
</article>""" for it in items)

    chips = '<button class="chip active" data-f="">Semua</button>' + "".join(
        f'<button class="chip" data-f="{esc(c["id"])}">{esc(c["name"])}</button>' for c in kb["categories"])

    years = sorted({it["year"] for it in items})
    y0, y1 = years[0], years[-1]
    dots = "".join(
        f'<span class="tl-dot" style="left:{(y - y0) / max(1, y1 - y0) * 100:.1f}%" title="{esc(", ".join(i["short"] for i in items if i["year"] == y))}">'
        f'<span class="tl-n">{sum(1 for i in items if i["year"] == y)}</span><span class="tl-y">{y}</span></span>' for y in years)

    body = f"""<div class="wrap">
  <h1>Kebijakan digital Indonesia</h1>
  <p class="lead muted" style="max-width:720px;font-size:1.08rem">Aturan yang menentukan siapa bisa terhubung, berapa biayanya,
    dan bagaimana data kita dilindungi, dijelaskan dalam bahasa sehari-hari.</p>
  <p class="small" style="margin:-6px 0 36px"><a href="../artikel/#Regulasi">Semua ulasan kebijakan di Artikel ›</a></p>
  <section>
    <div class="section-head" style="align-items:center"><h2 style="margin:0">Daftar regulasi</h2>
      <div class="chips" role="group" aria-label="Filter topik" style="margin:0">{chips}</div></div>
    <div class="pol-grid">{cards}</div>
  </section>
  <section>
    <h2>Linimasa</h2>
    <p class="muted small" style="margin-top:-4px">Regulasi dalam daftar ini menurut tahun terbit.</p>
    <div class="timeline" role="img" aria-label="Linimasa regulasi {y0}–{y1}">{dots}</div>
  </section>
  <p class="small muted">Teks resmi setiap regulasi tersedia di <a href="https://peraturan.go.id">peraturan.go.id</a> dan JDIH kementerian terkait.
    Ringkasan di halaman ini adalah penjelasan umum, bukan nasihat hukum.</p>
</div>
<script>
document.querySelectorAll('.chip').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('active', x === b));
  document.querySelectorAll('.pol-card').forEach(c => c.hidden = !!b.dataset.f && c.dataset.cat !== b.dataset.f);
}}));
</script>"""
    os.makedirs(os.path.join(ROOT, "kebijakan"), exist_ok=True)
    open(os.path.join(ROOT, "kebijakan/index.html"), "w", encoding="utf-8").write(
        page("Kebijakan · Connecting Nusantara", "Regulasi digital Indonesia dijelaskan dalam bahasa sehari-hari: telekomunikasi, internet, data pribadi, dan pemerintahan digital.", "../", "kebijakan/", body))

    # data for the home page + feed
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    json.dump([{k: a.get(k) for k in ("slug", "title", "date", "category", "lang", "summary", "hero")} for a in arts],
              open(os.path.join(ROOT, "data/artikel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(kb, open(os.path.join(ROOT, "data/kebijakan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    items = "".join(f"""<item><title>{esc(a['title'])}</title><link>{SITE}/artikel/{a['slug']}/</link><guid>{SITE}/artikel/{a['slug']}/</guid>
<pubDate>{format_datetime(datetime.fromisoformat(a['date']).replace(tzinfo=timezone.utc))}</pubDate><category>{esc(a['category'])}</category><description>{esc(a.get('summary'))}</description></item>
""" for a in arts[:20])
    open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8").write(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Connecting Nusantara</title><link>{SITE}/</link>
<description>Kesenjangan dan kesetaraan digital di Indonesia: data, kebijakan, dan analisis.</description><language>id</language>
{items}</channel></rss>
""")
    print(f"built {len(arts)} articles, {len(kb['items'])} regulations")


if __name__ == "__main__":
    build()
    import stamp_assets; stamp_assets.stamp()
