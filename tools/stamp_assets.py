"""Add a content-hash version to assets/style.css and assets/site.js links in every HTML page,
so browsers fetch the new file after each deploy (cache busting).
Run from the site root before deploying:  python3 tools/stamp_assets.py
(tools/build_content.py runs it automatically.)"""
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stamp():
    tags = {}
    for name in ("style.css", "site.js"):
        data = open(os.path.join(ROOT, "assets", name), "rb").read()
        tags[name] = hashlib.sha1(data).hexdigest()[:8]
    n = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("content", "tools", "data")]
        for f in files:
            if not f.endswith(".html"): continue
            p = os.path.join(root, f); s = open(p, encoding="utf-8").read()
            new = s
            for name, tag in tags.items():
                new = re.sub(r'(assets/%s)(\?v=[0-9a-f]+)?"' % re.escape(name), r'\1?v=%s"' % tag, new)
            if new != s: open(p, "w", encoding="utf-8").write(new); n += 1
    print(f"stamped {n} pages: {tags}")


if __name__ == "__main__":
    stamp()
