"""Add a content-hash version to assets/style.css and assets/site.js links in every HTML page,
so browsers fetch the new file after each deploy (cache busting).
Run from the site root before deploying:  python3 tools/stamp_assets.py
(tools/build_content.py runs it automatically.)"""
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_css():
    css = re.sub(r"/\*.*?\*/", "", open(os.path.join(ROOT, "assets/style.css"), encoding="utf-8").read(), flags=re.S)
    depth = 0
    for line_no, line in enumerate(css.split("\n"), 1):
        depth += line.count("{") - line.count("}")
        if depth < 0: raise SystemExit(f"style.css: extra '}}' around line {line_no}")
    if depth != 0: raise SystemExit(f"style.css: {depth} unclosed '{{' — fix before deploying")


def stamp():
    check_css()
    tags = {}
    for name in ("style.css", "site.js"):
        data = open(os.path.join(ROOT, "assets", name), "rb").read()
        tags[name] = hashlib.sha1(data).hexdigest()[:8]
    tags["explorer.js"] = hashlib.sha1(open(os.path.join(ROOT, "explorer", "explorer.js"), "rb").read()).hexdigest()[:8]
    art = os.path.join(ROOT, "data", "artikel.json")
    if os.path.exists(art):
        tags["artikel.json"] = hashlib.sha1(open(art, "rb").read()).hexdigest()[:8]
    n = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("content", "tools", "data")]
        for f in files:
            if not f.endswith(".html"): continue
            p = os.path.join(root, f); s = open(p, encoding="utf-8").read()
            new = s
            for name, tag in tags.items():
                if name == "explorer.js":
                    new = re.sub(r'(src="explorer\.js)(\?v=[0-9a-f]+)?"', r'\1?v=%s"' % tag, new); continue
                folder = "data" if name.endswith(".json") else "assets"
                new = re.sub(r'(%s/%s)(\?v=[0-9a-f]+)?"' % (folder, re.escape(name)), r'\1?v=%s"' % tag, new)
            if new != s: open(p, "w", encoding="utf-8").write(new); n += 1
    print(f"stamped {n} pages: {tags}")


if __name__ == "__main__":
    stamp()
