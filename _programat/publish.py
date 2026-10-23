"""Publică o cronică programată din rubrica Cultură pe aequus.news.

Rulare din rădăcina repo-ului (pe main actualizat):
    python3 _programat/publish.py strainul
    python3 _programat/publish.py filantropica
Idempotent: dacă un pas a fost deja făcut, îl sare.
"""
import json, os, re, shutil, sys

KIT = os.path.dirname(os.path.abspath(__file__))
SLUGS = {"strainul": "strainul-daca-nu-plangi", "filantropica": "filantropica-de-cine-radem"}
NAV_FILES = ["index.html", "global.html", "iran.html", "ucraina.html", "ue.html", "arhiva.html", "despre.html"]
CSS_LINE = ".flux-cultura .cat-chip { background: #110c18; border-color: #8e6bbf; }"


def rd(p):
    return open(p, encoding="utf-8").read()


def wr(p, s):
    open(p, "w", encoding="utf-8").write(s)


def insert_before(path, marker_regex, block, skip_if):
    s = rd(path)
    if skip_if in s:
        print(f"  {path}: deja există, sar")
        return
    m = re.search(marker_regex, s, re.M)
    if not m:
        sys.exit(f"EROARE: n-am găsit locul de inserare în {path}")
    wr(path, s[: m.start()] + block + s[m.start():])
    print(f"  {path}: inserat")


def common():
    if not os.path.exists("cultura.html"):
        shutil.copy(f"{KIT}/common/cultura.html", "cultura.html")
        print("  cultura.html: creat")
    for f in NAV_FILES:
        s = rd(f)
        if 'href="/cultura.html"' in s:
            continue
        s2 = re.sub(r'^(\s*)<a href="/despre.html">Despre</a>',
                    r'\1<a href="/cultura.html">Cultură</a>\n\1<a href="/despre.html">Despre</a>', s, count=1, flags=re.M)
        if s2 != s:
            wr(f, s2)
            print(f"  {f}: meniu + Cultură")
    for c in ["css/style.css", "style.css"]:
        if os.path.exists(c) and CSS_LINE not in rd(c):
            wr(c, rd(c).rstrip("\n") + "\n" + CSS_LINE + "\n")
            print(f"  {c}: stil Cultură")


def publish(key):
    slug = SLUGS[key]
    d = f"{KIT}/{key}"
    b = json.load(open(f"{d}/blocks.json", encoding="utf-8"))
    common()
    for f in [f"{slug}.html", f"card-{slug}.svg", f"card-{slug}.png"]:
        shutil.copy(f"{d}/{f}", f"articles/{f}")
    insert_before("index.html", r"^    <!-- FEATURED", b["index"], f'<!-- FEATURED — {"Străinul" if key=="strainul" else "Filantropica"} (Cultură')
    insert_before("arhiva.html", r'^\s*<article class="article-card', b["arhiva"], f'<h3 class="article-title"><a href="/articles/{slug}.html"')
    insert_before("sitemap.xml", r"^  <url>\n    <loc>https://aequus.news/articles/", b["sitemap"], f"/articles/{slug}.html</loc>")
    if "sitemap_cultura" in b:
        insert_before("sitemap.xml", r"^  <url>\n    <loc>https://aequus.news/articles/", b["sitemap_cultura"], "aequus.news/cultura.html</loc>")
    if "cultura" in b:
        insert_before("cultura.html", r'^    <article class="featured-article flux-cultura">', b["cultura"], f'<h2 class="article-title"><a href="/articles/{slug}.html"')
    if key == "filantropica":
        p = "articles/strainul-daca-nu-plangi.html"
        s = rd(p)
        link = '<a href="/articles/filantropica-de-cine-radem.html">Filantropica: de cine râdem, de fapt?</a> · '
        if link not in s:
            wr(p, s.replace('Vezi și: <a href="/cultura.html">', "Vezi și: " + link + '<a href="/cultura.html">', 1))
            print(f"  {p}: legătură spre Filantropica")
    print("Gata:", slug)


if __name__ == "__main__":
    publish(sys.argv[1])
