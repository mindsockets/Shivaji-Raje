#!/usr/bin/env python3
"""Stamp the common site shell into every page.

One source of truth for the header (menu bar), the story pager, the
"mark as read" slot and the footer. Each block lives between marker
comments, e.g. <!-- shell:header --> ... <!-- /shell:header -->, so the
script can be re-run safely after editing the menu here.

    python3 tools/build_shell.py          # rewrite pages in place
    python3 tools/build_shell.py --check  # exit 1 if any page is stale
"""
import html, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MENU = [  # (key, href, label)
    ("nights", "index.html#nights", "30 Nights"),
    ("saints", "saints.html", "Saints"),
    ("cast", "cast.html", "Cast"),
    ("tree", "family-tree.html", "Family tree"),
    ("forts", "forts.html", "Forts"),
    ("map", "map.html", "Map"),
    ("sayings", "sayings-sheet.html", "Sayings"),
    ("relics", "relics.html", "Relics"),
    ("trip", "trip-companion.html", "📍 Trip map"),
]
REF_PAGES = {"cast.html": "cast", "family-tree.html": "tree", "forts.html": "forts", "map.html": "map",
             "sayings-sheet.html": "sayings", "relics.html": "relics", "saints.html": "saints"}
NIGHTS = ["The Land That Waited", "Birth at Shivneri", "Jijabai's Lap", "The Mavla Brotherhood", "The Oath at Raireshwar",
          "The First Fort — Torna", "Freeing Father Shahaji", "Javali", "The Giant Approaches", "Pratapgad & Afzal Khan",
          "Panhala & Shiva Kashid", "Pavan Khind & Baji Prabhu", "Night Raid on the Lal Mahal", "The Surat Raid",
          "Purandar & Murarbaji", "Agra — The Cage & the Escape", "Sinhagad & Tanaji", "Salher", "Nesari & Prataprao",
          "Bahirji Naik & Ganimi Kava", "Raigad & Hirkani", "The Coronation", "Rajmata Jijabai Departs", "Master of the Sea",
          "The Southern Campaign", "The Just King", "The Saints", "The Last Days", "The Dream That Didn't Die",
          "The Memory Garland"]
ACTS = [(1, 6, "Act I"), (7, 12, "Act II"), (13, 16, "Act III"), (17, 23, "Act IV"), (24, 30, "Act V")]
SAINTS = [("saint-varkari", "The Road to Pandharpur"), ("saint-tukaram", "Sant Tukaram"), ("saint-ramdas", "Samarth Ramdas"),
          ("saint-mauni-baba", "Mauni Baba"), ("saint-sufi", "Shared Faith")]

e = html.escape


def header(current):
    links = "\n".join(
        f'      <a href="{h}"' + (' aria-current="page"' if k == current else "") + f">{e(l)}</a>"
        for k, h, l in MENU)
    return f"""<!-- shell:header -->
<nav class="sitebar" aria-label="Site">
  <div class="sb-in">
    <a class="sb-brand" href="index.html"><span class="sb-moon" aria-hidden="true">☾</span>A Story a Night</a>
    <div class="sb-links">
{links}
    </div>
    <a class="sb-prog" href="index.html#progress"><span class="sb-ring" aria-hidden="true"></span><span data-sb-count>My progress</span></a>
  </div>
</nav>
<!-- /shell:header -->"""


def footer():
    col = lambda title, items: (f'    <div><h2>{title}</h2><ul>' +
                                "".join(f'<li><a href="{h}">{e(l)}</a></li>' for h, l in items) + "</ul></div>")
    return f"""<!-- shell:footer -->
<div class="sitefoot" role="contentinfo">
  <div class="sf-in">
{col("Read", [("index.html#nights", "The 30 nights"), ("day-01.html", "Begin with Night 1"), ("saints.html", "Saint stories"), ("index.html#progress", "Your progress")])}
{col("Who & where", [("cast.html", "The Cast"), ("family-tree.html", "The Family Tree"), ("forts.html", "The Forts"), ("map.html", "The Map")])}
{col("Collect & visit", [("sayings-sheet.html", "The Sayings"), ("relics.html", "The Relics"), ("trip-companion.html", "Trip map")])}
    <div class="sf-progress"><h2>Your reading</h2><div data-foot-progress><p>Your progress is saved only in this browser.</p></div>
      <button type="button" data-reset>Clear my progress</button></div>
    <div class="sf-about"><b>A Story a Night · छत्रपती शिवाजी महाराज</b><span>Fact first, legend always labelled.</span></div>
  </div>
</div>
<!-- /shell:footer -->"""


def pager_night(n):
    act = next(a for a in ACTS if a[0] <= n <= a[1])[2]
    prev = (f'<a class="pg-prev" href="day-{n-1:02d}.html" rel="prev">‹ Night {n-1}</a>' if n > 1
            else '<a class="pg-prev" href="index.html#nights">‹ All nights</a>')
    nxt = (f'<a class="pg-next" href="day-{n+1:02d}.html" rel="next">Night {n+1} ›</a>' if n < 30
           else '<a class="pg-next" href="saints.html">Bonus: the saints ›</a>')
    return f"""<!-- shell:pager -->
<nav class="pager" aria-label="Nights">
  {prev}
  <span class="pg-pos">{act} · Night {n} of 30<span class="pg-read">✓ read</span></span>
  {nxt}
</nav>
<!-- /shell:pager -->"""


def pager_saint(i):
    prev = (f'<a class="pg-prev" href="{SAINTS[i-1][0]}.html" rel="prev">‹ {e(SAINTS[i-1][1])}</a>' if i > 0
            else '<a class="pg-prev" href="saints.html">‹ All saints</a>')
    nxt = (f'<a class="pg-next" href="{SAINTS[i+1][0]}.html" rel="next">{e(SAINTS[i+1][1])} ›</a>' if i < len(SAINTS) - 1
           else '<a class="pg-next" href="saints.html">All saints ›</a>')
    return f"""<!-- shell:pager -->
<nav class="pager" aria-label="Saint stories">
  {prev}
  <span class="pg-pos">Saint story {i+1} of {len(SAINTS)}<span class="pg-read">✓ read</span></span>
  {nxt}
</nav>
<!-- /shell:pager -->"""


def foot_night(n):
    nxt = (f'Next → <a href="day-{n+1:02d}.html">Night {n+1} · {e(NIGHTS[n])}</a>' if n < 30
           else 'Bonus → <a href="saints.html">Stories of the saints</a>')
    return f"""<!-- shell:next -->
    <div class="foot">
      <span><a href="index.html#nights">🏠 All nights</a> · <a href="family-tree.html">🌳 Who's who</a> · <a href="trip-companion.html">📍 Trip map</a></span>
      <span class="next">{nxt}</span>
    </div>
    <!-- /shell:next -->"""


def foot_saint(i):
    nxt = (f'Next → <a href="{SAINTS[i+1][0]}.html">{e(SAINTS[i+1][1])}</a>' if i < len(SAINTS) - 1
           else 'Back → <a href="saints.html">All saints</a>')
    return f"""<!-- shell:next -->
    <div class="foot">
      <span><a href="saints.html">🪷 All saints</a> · <a href="index.html#nights">🏠 All nights</a> · <a href="trip-companion.html">📍 Trip map</a></span>
      <span class="next">{nxt}</span>
    </div>
    <!-- /shell:next -->"""


READMARK = "<!-- shell:readmark -->\n    <div class=\"readmark\" data-readmark></div>\n    <!-- /shell:readmark -->"


def put(s, name, block, migrate=None):
    """Replace the marked block; on first run, call migrate(s, block) to place it."""
    pat = re.compile(r"<!-- shell:%s -->.*?<!-- /shell:%s -->" % (name, name), re.S)
    if pat.search(s):
        return pat.sub(lambda m: block, s, count=1)
    if migrate is None:
        raise SystemExit(f"no marker for {name}")
    out = migrate(s, block)
    if out == s:
        raise SystemExit(f"could not place {name}")
    return out


def sub1(pattern, repl, s, flags=re.S):
    out, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"pattern not found: {pattern[:60]}")
    return out


def ensure_assets(s, is_fragment):
    if 'href="shell.css"' not in s:
        m = re.search(r'<link rel="stylesheet" href="(?:day|site)\.css">', s)
        if m:
            s = s[:m.end()] + '\n<link rel="stylesheet" href="shell.css">' + s[m.end():]
        else:  # trip companion: own inline styles
            s = s.replace("</head>", '<link rel="stylesheet" href="shell.css">\n</head>', 1)
    if 'src="shell.js"' not in s:
        if "</body>" in s:
            s = s.replace("</body>", '<script src="shell.js" defer></script>\n</body>', 1)
        else:
            s = s.rstrip("\n") + '\n<script src="shell.js" defer></script>\n'
    return s


def build(name, s):
    if re.fullmatch(r"day-\d\d\.html", name):
        n = int(name[4:6])
        s = put(s, "header", header("nights"), lambda s, b: sub1(r'<nav class="daynav">', b + "\n" + '<nav class="daynav">', s))
        s = put(s, "pager", pager_night(n), lambda s, b: sub1(r'<nav class="daynav">.*?</nav>', b, s))
        s = put(s, "readmark", READMARK, lambda s, b: sub1(r'(?=<div class="moon-note">)', b + "\n    ", s))
        s = put(s, "next", foot_night(n), lambda s, b: sub1(r'[ \t]*<div class="foot">.*?</div>', b, s))
        s = put(s, "footer", footer(), lambda s, b: sub1(r'</main>', "</main>\n" + b, s))
        return ensure_assets(s, True)
    if name.startswith("saint-"):
        i = [k for k, _ in SAINTS].index(name[:-5])
        s = put(s, "header", header("saints"), lambda s, b: sub1(r'<nav class="daynav">', b + "\n" + '<nav class="daynav">', s))
        s = put(s, "pager", pager_saint(i), lambda s, b: sub1(r'<nav class="daynav">.*?</nav>', b, s))
        s = put(s, "readmark", READMARK, lambda s, b: sub1(r'(?=<div class="moon-note">)', b + "\n    ", s))
        s = put(s, "next", foot_saint(i), lambda s, b: sub1(r'[ \t]*<div class="foot">.*?</div>', b, s))
        s = put(s, "footer", footer(), lambda s, b: sub1(r'</main>', "</main>\n" + b, s))
        return ensure_assets(s, True)
    if name in REF_PAGES:
        s = put(s, "header", header(REF_PAGES[name]), lambda s, b: sub1(r'<nav class="topnav">.*?</nav>', b, s))
        s = put(s, "footer", footer(), lambda s, b: sub1(r'[ \t]*<footer>.*?</footer>\s*(</div>\s*)?</main>',
                                                         ("</div>\n" if "family-tree" in name else "") + "</main>\n" + b, s)
                if "<footer>" in s else sub1(r'</main>', "</main>\n" + b, s))
        return ensure_assets(s, False)
    if name == "index.html":
        s = put(s, "header", header("nights"), lambda s, b: sub1(r'<body>\n', "<body>\n" + b + "\n", s))
        s = put(s, "footer", footer(), lambda s, b: sub1(r'[ \t]*<footer>.*?</footer>\s*</main>', "</main>\n" + b, s))
        return ensure_assets(s, False)
    if name == "trip-companion.html":
        s = put(s, "header", header("trip"), lambda s, b: sub1(r'<body>\n', "<body>\n" + b + "\n", s))
        return ensure_assets(s, False)
    if name == "404.html":
        s = put(s, "header", header(None), lambda s, b: sub1(r'<body>\n', "<body>\n" + b + "\n", s))
        s = put(s, "footer", footer(), lambda s, b: sub1(r'</main>', "</main>\n" + b, s))
        return ensure_assets(s, False)
    return None


def main():
    check = "--check" in sys.argv
    stale = []
    for p in sorted(ROOT.glob("*.html")):
        s = p.read_text(encoding="utf-8")
        out = build(p.name, s)
        if out is None:
            print("skipped", p.name); continue
        if out != s:
            stale.append(p.name)
            if not check:
                p.write_text(out, encoding="utf-8")
    print(("stale: " if check else "updated: ") + (", ".join(stale) or "none"))
    if check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
