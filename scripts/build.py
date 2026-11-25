"""Builds the sticker-board GitHub profile: every SVG in assets/ plus README.md.

Run locally:   python scripts/build.py --fixture      (sample data, for layout checks only)
In the Action: python scripts/build.py                (real data from the GitHub API)

Every SVG is drawn in four versions: light / dark, desktop / phone.
Fonts (Fredoka, DM Mono, both SIL OFL) are subset and embedded so GitHub renders them exactly.
"""
import argparse, base64, datetime as dt, io, json, math, os, random, sys, urllib.request
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
from fontTools import subset as ftsubset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"
PROFILE = json.loads((ROOT / "profile.json").read_text())

# ------------------------------------------------------------------ theme
THEMES = {
    "light": dict(
        bg="#fbf6ee", card="#ffffff", text="#22201c", muted="#66615a", line="#22201c", dot="#e2d9c8",
        blue="#cfe6ff", green="#d6f2dc", peach="#ffe1b8", lilac="#e7defc", pink="#ffd3cf", teal="#cdeff0",
        pop="#ff6a3d", go="#2fbf71", goink="#1d814b", screen="#1e1f33", onscreen="#efedff", onmuted="#b4b1d6",
        cell0="#ece7dd", cells=["#c8eed5", "#8fdcac", "#45c27c", "#23985a"], area="#ffdcd0",
    ),
    "dark": dict(
        bg="#15172b", card="#1f2240", text="#f3f1ff", muted="#bdbcd8", line="#07081a", dot="#272b4c",
        blue="#264a7d", green="#215c3c", peach="#7a4d1e", lilac="#4b3b7c", pink="#7a3040", teal="#1e5b5d",
        pop="#ff6a3d", go="#2fbf71", goink="#86e3ae", screen="#0f1025", onscreen="#efedff", onmuted="#a9a6cf",
        cell0="#2a2e50", cells=["#1f5a3a", "#2a8150", "#38a866", "#56d690"], area="#4a2633",
    ),
}
DESKTOP, PHONE = 960, 480

# ------------------------------------------------------------------ fonts
FONT_FILES = {("F", 500): "Fredoka-500", ("F", 600): "Fredoka-600", ("F", 700): "Fredoka-700",
              ("M", 400): "DMMono-400", ("M", 500): "DMMono-500"}
FAMILY = {"F": "Fredoka", "M": "DM Mono"}
_fonts, _metrics = {}, {}


def _font(key):
    if key not in _fonts:
        f = TTFont(FONTS / f"{FONT_FILES[key]}.ttf")
        _fonts[key] = f
        _metrics[key] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    return _fonts[key]


def measure(text, size, fam="F", wt=None):
    wt = wt or (600 if fam == "F" else 400)
    _font((fam, wt))
    cmap, hmtx, upm = _metrics[(fam, wt)]
    total = 0
    for ch in text:
        g = cmap.get(ord(ch))
        total += hmtx[g][0] if g in hmtx else upm * 0.55
    return total / upm * size


def embed_font(key, chars):
    opts = ftsubset.Options()
    opts.flavor = "woff"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    font = TTFont(FONTS / f"{FONT_FILES[key]}.ttf")
    sub = ftsubset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    fam, wt = key
    return f"@font-face{{font-family:'{FAMILY[fam]}';font-weight:{wt};src:url(data:font/woff;base64,{b64}) format('woff');}}"


def wrap(text, width, size, fam="F", wt=500):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(trial, size, fam, wt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ svg canvas
class SVG:
    def __init__(self, w, h, theme):
        self.w, self.h, self.t = w, h, THEMES[theme]
        self.els, self.used, self.css = [], defaultdict(set), []

    def add(self, s):
        self.els.append(s)

    def text(self, x, y, s, size, fam="F", wt=None, fill=None, anchor="start", extra=""):
        wt = wt or (600 if fam == "F" else 400)
        self.used[(fam, wt)].update(s)
        fill = fill or self.t["text"]
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY[fam]}" font-weight="{wt}" '
                 f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>')

    def sticker(self, x, y, w, h, fill, r=16, shadow=6, stroke=3, shadow_fill=None, extra=""):
        sf = shadow_fill or self.t["line"]
        if shadow:
            self.add(f'<rect x="{x+shadow:.1f}" y="{y+shadow:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{sf}" {extra}/>')
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" '
                 f'stroke="{self.t["line"]}" stroke-width="{stroke}" {extra}/>')

    def panel(self, pad=4):
        """Cream board with a dot grid, like a cutting mat the stickers sit on."""
        t = self.t
        self.add(f'<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
                 f'<circle cx="2" cy="2" r="1.6" fill="{t["dot"]}"/></pattern></defs>')
        self.add(f'<rect x="{pad}" y="{pad}" width="{self.w-2*pad}" height="{self.h-2*pad}" rx="24" fill="{t["bg"]}" '
                 f'stroke="{t["line"]}" stroke-width="2.5"/>')
        self.add(f'<rect x="{pad}" y="{pad}" width="{self.w-2*pad}" height="{self.h-2*pad}" rx="24" fill="url(#dots)"/>')

    def render(self, alt=""):
        fonts = "".join(embed_font(k, v) for k, v in self.used.items() if v)
        css = fonts + "".join(self.css)
        title = f"<title>{escape(alt)}</title>" if alt else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img">{title}<style>{css}</style>'
                + "".join(self.els) + "</svg>\n")


def fmt(n):
    return f"{n:,}"


def write(name, svg_by_variant):
    for variant, svg in svg_by_variant.items():
        (ASSETS / f"{name}-{variant}.svg").write_text(svg)


def variants(fn, *args, phone=True, **kw):
    out = {}
    for theme in ("light", "dark"):
        out[theme] = fn(DESKTOP, theme, *args, **kw)
        if phone:
            out[f"phone-{theme}"] = fn(PHONE, theme, *args, **kw)
    return out


# ------------------------------------------------------------------ icons (24x24, drawn here)
def icon(svg, kind, x, y, s=24, color=None):
    c, ink = color or svg.t["pop"], svg.t["line"]
    k = s / 24
    g = f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})" stroke="{ink}" stroke-width="1.8" stroke-linejoin="round">'
    shapes = {
        "calendar": f'<rect x="2" y="4" width="20" height="18" rx="3" fill="{c}"/><path d="M2 9h20" fill="none"/>'
                    f'<path d="M7 2v4M17 2v4" fill="none" stroke-linecap="round"/>',
        "flame": f'<path d="M12 2c1 4 6 6 6 12a6 6 0 0 1-12 0c0-3 2-5 3-6 0 2 1 3 2 3 0-4 1-6 1-9z" fill="{c}"/>',
        "trophy": f'<path d="M7 3h10v6a5 5 0 0 1-10 0z" fill="{c}"/><path d="M7 5H3v2a4 4 0 0 0 4 4M17 5h4v2a4 4 0 0 1-4 4" fill="none"/>'
                  f'<path d="M12 14v4M8 21h8l-1-3H9z" fill="{c}"/>',
        "bars": f'<rect x="3" y="12" width="5" height="10" rx="1" fill="{c}"/><rect x="10" y="6" width="5" height="16" rx="1" fill="{c}"/>'
                f'<rect x="17" y="2" width="5" height="20" rx="1" fill="{c}"/>',
        "folder": f'<path d="M2 6a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2z" fill="{c}"/>',
        "star": f'<path d="M12 2l3 6.5 7 .8-5.2 4.8 1.5 7L12 17.6 5.7 21.1l1.5-7L2 9.3l7-.8z" fill="{c}"/>',
        "bolt": f'<path d="M13 2L4 14h7l-1 8 9-12h-7z" fill="{c}"/>',
        "arrow": f'<path d="M7 17L17 7M9 7h8v8" fill="none" stroke-width="3" stroke-linecap="round"/>',
    }
    svg.add(g + shapes[kind] + "</g>")


def app_glyph(svg, kind, x, y, s):
    """Glyphs for the project tiles, drawn for these projects."""
    t, ink, c = svg.t, svg.t["line"], svg.t["onscreen"]
    k = s / 64
    g = f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})">'
    shapes = {
        "circle": f'<circle cx="32" cy="32" r="18" fill="none" stroke="{c}" stroke-width="5" stroke-dasharray="7 6" stroke-linecap="round"/>'
                  f'<circle cx="32" cy="32" r="6" fill="{t["pop"]}"/>',
        "cross": f'<path d="M26 12h12v14h14v12H38v14H26V38H12V26h14z" fill="{t["go"]}"/>',
        "nodes": f'<path d="M18 46L32 18L46 46Z" fill="none" stroke="{c}" stroke-width="4"/>'
                 f'<circle cx="32" cy="18" r="7" fill="{t["pop"]}"/><circle cx="18" cy="46" r="7" fill="{c}"/>'
                 f'<circle cx="46" cy="46" r="7" fill="{c}"/>',
        "car": f'<path d="M10 40l4-12a6 6 0 0 1 6-4h24a6 6 0 0 1 6 4l4 12v6H10z" fill="{t["pop"]}"/>'
               f'<circle cx="21" cy="46" r="6" fill="{c}"/><circle cx="43" cy="46" r="6" fill="{c}"/>',
    }
    svg.add(g + shapes[kind] + "</g>")


# ------------------------------------------------------------------ 1. hero
def hero(W, theme):
    phone = W == PHONE
    P = PROFILE
    H = 360 if phone else 262
    s = SVG(W, H, theme)
    t = s.t
    s.panel()
    lx, ly, ls = (28, 30, 74) if phone else (44, 46, 104)
    s.sticker(lx, ly, ls, ls, t["card"], r=20, shadow=8, stroke=4, shadow_fill=t["pop"])
    s.text(lx + ls / 2, ly + ls * 0.76, P["name"][0], int(ls * 0.74), wt=700, anchor="middle")
    # sticker, slightly rotated, top right
    st = P["sticker"]
    sw = measure(st, 17, wt=700) + 32
    sx, sy = W - sw - (30 if phone else 48), (34 if phone else 44)
    s.add(f'<g transform="rotate(-6 {sx+sw/2:.1f} {sy+21})">')
    s.sticker(sx, sy, sw, 42, t["pop"], r=12, shadow=5)
    s.text(sx + sw / 2, sy + 28, st, 17, wt=700, fill="#22201c", anchor="middle")
    s.add("</g>")
    # title with highlighted name
    size = 40 if phone else 56
    tx, ty = (28, 158) if phone else (184, 112)
    pre = "Hi, I'm "
    pw = measure(pre, size, wt=700)
    nw = measure(P["name"], size, wt=700)
    s.add(f'<rect x="{tx+pw-8:.1f}" y="{ty-size*0.86:.1f}" width="{nw+16:.1f}" height="{size*1.12:.1f}" rx="10" fill="{t["pink"]}"/>')
    s.text(tx, ty, pre, size, wt=700)
    s.text(tx + pw, ty, P["name"], size, wt=700)
    # tagline
    tsize = 16 if phone else 19
    lines = wrap(P["tagline"], W - tx - 36, tsize, wt=500)
    y = ty + (36 if phone else 44)
    for ln in lines:
        s.text(tx + 2, y, ln, tsize, wt=500, fill=t["muted"])
        y += tsize * 1.45
    # pills (wrap to new row when out of room)
    px, py = tx + 2, y + 2
    colors = ["blue", "peach", "lilac", "pink"]
    for i, label in enumerate(P["pills"]):
        pw2 = measure(label, 15, wt=600) + 28
        if px + pw2 > W - 30:
            px, py = tx + 2, py + 46
        s.sticker(px, py, pw2, 34, t[colors[i % 4]], r=10, shadow=4, stroke=2.5)
        s.text(px + pw2 / 2, py + 23, label, 15, wt=600, anchor="middle")
        px += pw2 + 14
    return s.render(f"Hi, I'm {P['name']}. {P['tagline']}")


# ------------------------------------------------------------------ 2. link badges
def badge(theme, label, color):
    w = measure(label, 16, wt=600) + 36
    s = SVG(int(w + 8), 44, theme)
    fill = s.t[color]
    s.sticker(2, 2, w, 36, fill, r=10, shadow=4, stroke=2.5)
    s.text(2 + w / 2, 26, label, 16, wt=600, anchor="middle")
    return s.render(label)


# ------------------------------------------------------------------ 3. github stats board
def stats_board(W, theme, d):
    phone = W == PHONE
    big = [
        ("calendar", fmt(d["last_year"]), ["contributions in", "the last year"], "blue"),
        ("flame", f'{d["cur_streak"]} day' + ("" if d["cur_streak"] == 1 else "s"),
         ["current streak" + (",", "")[d["cur_streak"] == 0], (f'since {d["cur_since"]}' if d["cur_streak"] else "starts today")], "green"),
        ("trophy", f'{d["long_streak"]} day' + ("" if d["long_streak"] == 1 else "s"), ["longest streak", "ever"], "peach"),
        ("bars", fmt(d["all_time"]), ["contributions", f'since {d["since_year"]}'], "lilac"),
    ]
    small = [
        ("folder", str(d["repos"]), "public repos", "teal"),
        ("star", str(d["stars"]), "stars earned", "pink"),
        ("bolt", str(PROFILE["hackathon_builds"]["value"]), "hackathon builds", "green"),
    ]
    m, gap = (24, 16) if phone else (40, 20)
    cols = 2 if phone else 4
    bw = (W - 2 * m - gap * (cols - 1)) / cols
    bh = 112 if phone else 118
    rows_big = math.ceil(len(big) / cols)
    sh = 58 if phone else 64
    y0 = 96 if phone else 92
    small_y = y0 + rows_big * (bh + gap) + 6
    H = int(small_y + (len(small) * (sh + gap) if phone else sh + gap) + 24)
    s = SVG(W, H, theme)
    t = s.t
    s.panel()
    s.text(m, 60 if phone else 62, "On GitHub", 26 if phone else 30, wt=700)
    s.text(W - m, 60 if phone else 62, f'redrawn every night · {d["today_label"]}', 12 if phone else 14,
           fam="M", fill=t["muted"], anchor="end")
    for i, (ic, num, label, col) in enumerate(big):
        x = m + (i % cols) * (bw + gap)
        y = y0 + (i // cols) * (bh + gap)
        s.sticker(x, y, bw, bh, t[col], r=18, shadow=6)
        nsize = 30 if phone else 36
        while measure(num, nsize, wt=700) > bw - 60 and nsize > 18:
            nsize -= 2
        s.text(x + 20, y + (52 if phone else 58), num, nsize, wt=700)
        for j, ln in enumerate(label):
            s.text(x + 20, y + (78 if phone else 84) + j * 18, ln, 13 if phone else 15, fam="M")
        icon(s, ic, x + bw - 42, y + 16, 24)
    sw = W - 2 * m if phone else (W - 2 * m - gap * 2) / 3
    for i, (ic, num, label, col) in enumerate(small):
        x = m if phone else m + i * (sw + gap)
        y = small_y + (i * (sh + gap) if phone else 0)
        s.sticker(x, y, sw, sh, t[col], r=18, shadow=6)
        icon(s, ic, x + 20, y + sh / 2 - 12, 24)
        nsize = 26 if phone else 28
        s.text(x + 56, y + sh / 2 + 10, num, nsize, wt=700)
        s.text(x + 64 + measure(num, nsize, wt=700), y + sh / 2 + 6, label, 13 if phone else 15, fam="M")
    alt = (f'On GitHub: {fmt(d["last_year"])} contributions in the last year, a {d["cur_streak"]}-day current streak, '
           f'longest streak {d["long_streak"]} days, {fmt(d["all_time"])} contributions since {d["since_year"]}, '
           f'{d["repos"]} public repos, {d["stars"]} stars earned.')
    return s.render(alt), alt


# ------------------------------------------------------------------ 4. heatmap
def levels(counts):
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return lambda c: 0
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)]
    return lambda c: 0 if c == 0 else 1 + sum(c > v for v in q)


def weeks_of(days):
    """Group (date, count) days into Sunday-start weeks, like GitHub."""
    weeks, cur = [], []
    for d, c in days:
        wd = (d.weekday() + 1) % 7  # Sunday = 0
        if wd == 0 and cur:
            weeks.append(cur)
            cur = []
        cur.append((d, c, wd))
    if cur:
        weeks.append(cur)
    return weeks


def heatmap(W, theme, days, title_num, title_rest, numbers=True):
    phone = W == PHONE
    m, inner = (14, 16) if phone else (24, 26)
    weeks = weeks_of(days)
    gx = W - 2 * (m + inner)
    step = gx / len(weeks)
    cell = step * 0.86
    show_nums = numbers and cell >= 22
    H = int(m + 76 + 24 + 7 * step + 60 + m)
    s = SVG(W, H, theme)
    t = s.t
    s.panel()
    cx0, cy0 = m + 6, m + 6
    s.sticker(cx0, cy0, W - 2 * m - 18, H - 2 * m - 18, t["card"], r=18, shadow=6)
    x0, y0 = m + inner, m + 54
    s.text(x0, y0, title_num, 22 if phone else 24, wt=700)
    s.text(x0 + measure(title_num, 22 if phone else 24, wt=700) + 10, y0, title_rest, 14 if phone else 16, fam="M")
    lv = levels([c for _, c in days])
    gy = y0 + 34
    last_month = None
    for wi, wk in enumerate(weeks):
        for d, c, wd in wk:
            if d.day <= 7 and wd == 0 or (wi == 0 and last_month is None):
                if d.month != last_month and (wi < len(weeks) - 2 or wi == 0):
                    s.text(x0 + wi * step, gy - 4, d.strftime("%b"), 12 if phone else 14, fam="M", fill=t["muted"])
                last_month = d.month
            x = x0 + wi * step
            y = gy + 6 + wd * step
            L = lv(c)
            fill = t["cell0"] if L == 0 else t["cells"][L - 1]
            s.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{max(2, cell*0.18):.1f}" fill="{fill}"/>')
            if show_nums:
                col = "#ffffff" if L >= 3 else (t["muted"] if c == 0 else t["text"])
                size = 11 if c < 100 else 10
                s.text(x + cell / 2, y + cell / 2 + 4, str(c), size, fam="M", wt=500 if c else 400, fill=col, anchor="middle",
                       extra='font-style="italic" opacity="0.7"' if c == 0 else "")
    fy = gy + 6 + 7 * step + 30
    s.text(x0, fy, "contributions per day", 12 if phone else 13, fam="M", fill=t["muted"])
    lxe = W - m - inner
    s.text(lxe, fy, "More", 12 if phone else 13, fam="M", fill=t["muted"], anchor="end")
    bx = lxe - measure("More", 13, "M", 400) - 10 - 5 * 16
    for i, col in enumerate([t["cell0"]] + t["cells"]):
        s.add(f'<rect x="{bx + i*16:.1f}" y="{fy-11}" width="12" height="12" rx="3" fill="{col}"/>')
    s.text(bx - 8, fy, "Less", 12 if phone else 13, fam="M", fill=t["muted"], anchor="end")
    return s.render(f"{title_num} {title_rest}")


# ------------------------------------------------------------------ 5. 30-day line
def nice_step(mx):
    if mx <= 0:
        return 1
    raw = mx / 4
    p = 10 ** math.floor(math.log10(raw))
    for k in (1, 2, 5, 10):
        if raw <= k * p:
            return k * p
    return 10 * p


def line30(W, theme, days):
    phone = W == PHONE
    m, inner = (14, 16) if phone else (24, 26)
    H = 330 if phone else 380
    s = SVG(W, H, theme)
    t = s.t
    s.panel()
    s.sticker(m + 6, m + 6, W - 2 * m - 18, H - 2 * m - 18, t["card"], r=18, shadow=6)
    total = sum(c for _, c in days)
    x0, y0 = m + inner, m + 54
    s.text(x0, y0, fmt(total), 22 if phone else 24, wt=700)
    s.text(x0 + measure(fmt(total), 22 if phone else 24, wt=700) + 10, y0, "contributions in the last 30 days", 13 if phone else 16, fam="M")
    left, right = x0 + (34 if phone else 40), W - m - inner - 12
    top, bottom = y0 + 34, H - m - (64 if phone else 70)
    mx = max(c for _, c in days) if days else 0
    st = nice_step(mx)
    ymax = max(st * 4, mx) if mx else 4
    def Y(v): return bottom - (v / ymax) * (bottom - top)
    ticks = list(range(0, int(ymax) + 1, int(st))) if mx else [0, 1, 2, 3, 4]
    if mx and mx not in ticks:
        ticks.append(mx)
    for v in ticks:
        yy = Y(v)
        s.add(f'<line x1="{left}" y1="{yy:.1f}" x2="{right}" y2="{yy:.1f}" stroke="{t["muted"]}" stroke-opacity="0.35" stroke-dasharray="5 5"/>')
        s.text(left - 10, yy + 4, str(v), 11 if phone else 13, fam="M", fill=t["muted"], anchor="end")
    n = len(days)
    xs = [left + i * (right - left) / max(1, n - 1) for i in range(n)]
    ys = [Y(c) for _, c in days]
    # Catmull-Rom to cubic Bezier, clamped so the curve never dips below zero
    def path(pts):
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(len(pts) - 1):
            p0 = pts[max(0, i - 1)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(len(pts) - 1, i + 2)]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(bottom, p1[1] + (p2[1] - p0[1]) / 6))
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(bottom, p2[1] - (p3[1] - p1[1]) / 6))
            d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
        return d
    pts = list(zip(xs, ys))
    if n >= 2:
        curve = path(pts)
        s.add(f'<path d="{curve} L{xs[-1]:.1f},{bottom:.1f} L{xs[0]:.1f},{bottom:.1f}Z" fill="{t["area"]}" opacity="0.85"/>')
        s.add(f'<path d="{curve}" fill="none" stroke="{t["line"]}" stroke-width="5" transform="translate(2,3)" stroke-linecap="round"/>')
        s.add(f'<path d="{curve}" fill="none" stroke="{t["pop"]}" stroke-width="4" stroke-linecap="round"/>')
    for x, y in pts:
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 if phone else 5}" fill="{t["pop"]}" stroke="{t["line"]}" stroke-width="2"/>')
    every = 3 if phone else 1
    prev_month = None
    for i, ((d, _), x) in enumerate(zip(days, xs)):
        if i % every == 0 or i == n - 1:
            s.text(x, bottom + 22, str(d.day), 11 if phone else 13, fam="M", fill=t["muted"], anchor="middle")
        if d.month != prev_month:
            s.text(x, bottom + 42, d.strftime("%b"), 11 if phone else 13, fam="M", fill=t["muted"], anchor="middle")
            prev_month = d.month
    return s.render(f"{fmt(total)} contributions in the last 30 days"), total


# ------------------------------------------------------------------ 6. whoami terminal
def whoami(W, theme):
    phone = W == PHONE
    P = PROFILE["whoami"]
    m = 14 if phone else 24
    fs, lh = (13, 22) if phone else (17, 28)
    tx = m + (20 if phone else 34)
    maxw = W - tx - m - 24
    lines = [("cmd", "whoami")]
    for ln in wrap(P["id"], maxw, fs, "M", 500):
        lines.append(("id", ln))
    for ln in wrap(P["about"], maxw, fs, "M", 400):
        lines.append(("out", ln))
    lines += [("gap", ""), ("cmd", "cat now.txt")]
    for item in P["now"]:
        for j, ln in enumerate(wrap(item, maxw - fs * 1.6, fs, "M", 400)):
            lines.append(("now" if j == 0 else "nowc", ln))
    lines += [("gap", ""), ("cursor", "")]
    H = int(m + 70 + len(lines) * lh + 30 + m)
    s = SVG(W, H, theme)
    t = s.t
    s.panel()
    s.sticker(m + 6, m + 6, W - 2 * m - 18, H - 2 * m - 18, t["screen"], r=18, shadow=6)
    for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        s.add(f'<circle cx="{m + 32 + i*20}" cy="{m + 34}" r="6" fill="{col}"/>')
    s.text(W / 2, m + 39, f'{P["host"]}: ~', 12 if phone else 14, fam="M", fill=t["onmuted"], anchor="middle")
    s.css.append("@keyframes blink{50%{opacity:0}}.cur{animation:blink 1.1s steps(1) infinite}")
    y = m + 78
    for kind, ln in lines:
        if kind == "cmd":
            s.text(tx, y, "$", fs, fam="M", wt=500, fill=t["pop"])
            s.text(tx + fs * 1.3, y, ln, fs, fam="M", wt=500, fill=t["onscreen"])
        elif kind == "id":
            s.text(tx, y, ln, fs, fam="M", wt=500, fill=t["onscreen"])
        elif kind == "out":
            s.text(tx, y, ln, fs, fam="M", fill=t["onmuted"])
        elif kind in ("now", "nowc"):
            if kind == "now":
                s.text(tx, y, "→", fs, fam="M", fill=t["go"])
            s.text(tx + fs * 1.6, y, ln, fs, fam="M", fill=t["onmuted"])
        elif kind == "cursor":
            s.text(tx, y, "$", fs, fam="M", wt=500, fill=t["pop"])
            s.add(f'<rect class="cur" x="{tx + fs*1.3:.1f}" y="{y - fs*0.85:.1f}" width="{fs*0.6:.1f}" height="{fs*1.05:.1f}" fill="{t["onscreen"]}"/>')
        y += lh
    alt = f'whoami: {P["id"]}. {P["about"]} Now: ' + "; ".join(P["now"]) + "."
    return s.render(alt), alt


# ------------------------------------------------------------------ 7. section label
def label(W, theme, text, tag):
    phone = W == PHONE
    s = SVG(W, 76, theme)
    t = s.t
    size = 24 if phone else 28
    lw = measure(text, size, wt=700) + 36
    s.add(f'<g transform="rotate(-2 {20+lw/2:.1f} 38)">')
    s.sticker(16, 14, lw, 48, t["peach"], r=14, shadow=5)
    s.text(16 + lw / 2, 46, text, size, wt=700, anchor="middle")
    s.add("</g>")
    tw = measure(tag, 14, "M", 400) + 24
    s.add(f'<rect x="{lw + 40:.1f}" y="24" width="{tw:.1f}" height="30" rx="8" fill="{t["card"]}" stroke="{t["line"]}" stroke-width="2"/>')
    s.text(lw + 40 + tw / 2, 44, tag, 14, fam="M", anchor="middle")
    return s.render(text)


# ------------------------------------------------------------------ 8. project cards
def app_card(W, theme, app, force_h=0):
    """Desktop: 470 wide (shown at 49%). Phone: a compact 240-wide card that stays readable at half a phone screen."""
    phone = W == PHONE
    if phone:
        k = dict(cw=240, pad=16, icon=44, name=20, pill=10, pillh=20, about=14, alh=19, tag=11, tagh=21, stat=11, arrow=26)
    else:
        k = dict(cw=470, pad=28, icon=66, name=28, pill=12, pillh=24, about=17, alh=25, tag=13, tagh=26, stat=14, arrow=36)
    cw, pad = k["cw"], k["pad"]
    inner = cw - 2 * pad - 14
    ab_lines = wrap(app["about"], inner, k["about"], wt=500)
    # lay tags out in rows
    rows, row, rx = [], [], 0
    for tag in app["tags"]:
        tw = measure(tag, k["tag"], "M", 400) + (12 if phone else 18)
        if row and rx + tw > inner:
            rows.append(row); row, rx = [], 0
        row.append((tag, tw)); rx += tw + 6
    rows.append(row)
    st_lines = wrap(app["stats"], inner, k["stat"], "M", 400)
    top = pad + k["icon"] + (18 if phone else 22)
    H = int(top + len(ab_lines) * k["alh"] + 10 + len(rows) * (k["tagh"] + 6) + 14 + len(st_lines) * (k["stat"] + 6) + pad + 10)
    H = max(H, force_h)
    s = SVG(cw, H, theme)
    t = s.t
    s.sticker(4, 4, cw - 14, H - 14, t[app["color"]], r=18 if phone else 20, shadow=5 if phone else 7)
    ix = iy = pad
    s.sticker(ix, iy, k["icon"], k["icon"], t["screen"], r=12 if phone else 16, shadow=3 if phone else 4, stroke=2.5 if phone else 3)
    app_glyph(s, app["icon"], ix + 1, iy + 1, k["icon"] - 2)
    nx = ix + k["icon"] + (12 if phone else 16)
    s.text(nx, iy + (18 if phone else 30), app["name"], k["name"], wt=700)
    pw = measure(app["status"], k["pill"], "M", 500) + (12 if phone else 20)
    py = iy + (24 if phone else 40)
    s.add(f'<rect x="{nx:.1f}" y="{py}" width="{pw:.1f}" height="{k["pillh"]}" rx="{6 if phone else 8}" fill="{t["go"]}" stroke="{t["line"]}" stroke-width="2"/>')
    s.text(nx + pw / 2, py + k["pillh"] * 0.68, app["status"], k["pill"], fam="M", wt=500, fill="#0f2a1a", anchor="middle")
    a = k["arrow"]
    ax = cw - pad - a - 6
    s.sticker(ax, pad - 2, a, a, t["pop"], r=7 if phone else 9, shadow=2.5 if phone else 3, stroke=2 if phone else 2.5)
    icon(s, "arrow", ax + a * 0.17, pad - 2 + a * 0.17, a * 0.66)
    y = top + k["about"]
    for ln in ab_lines:
        s.text(pad, y, ln, k["about"], wt=500)
        y += k["alh"]
    ty = y - k["about"] + 12
    for row in rows:
        tx = pad
        for tag, tw in row:
            s.add(f'<rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="{k["tagh"]}" rx="6" fill="{t["card"]}" stroke="{t["line"]}" stroke-width="{1.6 if phone else 2}"/>')
            s.text(tx + tw / 2, ty + k["tagh"] * 0.69, tag, k["tag"], fam="M", anchor="middle")
            tx += tw + 6
        ty += k["tagh"] + 6
    y = ty + 14 + k["stat"]
    for ln in st_lines:
        s.text(pad, y, ln, k["stat"], fam="M", fill=t["muted"])
        y += k["stat"] + 6
    alt = f'{app["name"]}: {app["about"]} {app["status"]}. {app["stats"]}.'
    return s.render(alt), alt, H


# ------------------------------------------------------------------ data
def gql(token, query, variables):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read())
    if "errors" in out:
        raise RuntimeError(out["errors"])
    return out["data"]


CAL = "contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }"


def fetch_real(user, token):
    base = gql(token, """query($u:String!){ user(login:$u){ createdAt
        repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false){ totalCount nodes{ stargazerCount } }
        contributionsCollection{ %s } } }""" % CAL, {"u": user})["user"]
    created = dt.date.fromisoformat(base["createdAt"][:10])
    today = dt.date.today()
    years = {}
    for yr in range(created.year, today.year + 1):
        frm = dt.datetime(yr, 1, 1).isoformat() + "Z"
        to = dt.datetime(yr, 12, 31, 23, 59, 59).isoformat() + "Z"
        cal = gql(token, "query($u:String!,$f:DateTime!,$t:DateTime!){ user(login:$u){ contributionsCollection(from:$f,to:$t){ %s } } }" % CAL,
                  {"u": user, "f": frm, "t": to})["user"]["contributionsCollection"]["contributionCalendar"]
        years[yr] = cal
    def flat(cal):
        return [(dt.date.fromisoformat(d["date"]), d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    return dict(
        created=created,
        repos=base["repositories"]["totalCount"],
        stars=sum(n["stargazerCount"] for n in base["repositories"]["nodes"]),
        last_year_days=flat(base["contributionsCollection"]["contributionCalendar"]),
        last_year=base["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        years={y: (c["totalContributions"], [d for d in flat(c) if d[0] <= today]) for y, c in years.items()},
    )


def fetch_fixture():
    """Sample data for checking the layout locally. Never shipped."""
    rnd = random.Random(7)
    today = dt.date.today()
    days = []
    for i in range(365 * 3, -1, -1):
        d = today - dt.timedelta(days=i)
        busy = 0.35 + 0.5 * (i < 200)
        days.append((d, rnd.choice([0, 0, 1, 2, 3, 5, 8, 12, 20]) if rnd.random() < busy else 0))
    created = today - dt.timedelta(days=365 * 3)
    years = {}
    for d, c in days:
        years.setdefault(d.year, [0, []])
        years[d.year][0] += c
        years[d.year][1].append((d, c))
    ly = [x for x in days if x[0] > today - dt.timedelta(days=365)]
    return dict(created=created, repos=21, stars=9, last_year_days=ly, last_year=sum(c for _, c in ly),
                years={y: (v[0], v[1]) for y, v in years.items()})


def summarize(data):
    today = dt.date.today()
    alld = sorted({d: c for y in data["years"].values() for d, c in y[1]}.items())
    longest = run = 0
    for _, c in alld:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    counts = dict(alld)
    cur, day = 0, today
    if counts.get(day, 0) == 0:
        day -= dt.timedelta(days=1)
    while counts.get(day, 0) > 0:
        cur += 1
        day -= dt.timedelta(days=1)
    since = (day + dt.timedelta(days=1)).strftime("%-d %b") if cur else ""
    return dict(last_year=data["last_year"], cur_streak=cur, cur_since=since, long_streak=longest,
                all_time=sum(v[0] for v in data["years"].values()), since_year=data["created"].year,
                repos=data["repos"], stars=data["stars"], today_label=today.strftime("%-d %b %Y"))


# ------------------------------------------------------------------ README
def pic(name, alt, width="100%", phone=True, href=None):
    src = []
    if phone:
        src.append(f'<source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="assets/{name}-phone-dark.svg">')
        src.append(f'<source media="(max-width: 600px)" srcset="assets/{name}-phone-light.svg">')
    src.append(f'<source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">')
    p = f'<picture>{"".join(src)}<img src="assets/{name}-light.svg" width="{width}" alt="{escape(alt)}"></picture>'
    return f'<a href="{href}">{p}</a>' if href else p


def badge_pic(slug, label, url):
    return (f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/badge-{slug}-dark.svg">'
            f'<img src="assets/badge-{slug}-light.svg" height="44" alt="{escape(label)}"></picture></a>')


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", action="store_true", help="use sample data (layout checks only)")
    ap.add_argument("--out", default=None, help="write assets here instead of assets/")
    a = ap.parse_args()
    global ASSETS
    if a.out:
        ASSETS = Path(a.out)
    ASSETS.mkdir(parents=True, exist_ok=True)

    if a.fixture:
        data = fetch_fixture()
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Set GH_TOKEN (the Action does this for you), or run with --fixture for a layout preview.")
        data = fetch_real(PROFILE["user"], token)
    d = summarize(data)
    today = dt.date.today()
    P = PROFILE

    write("hero", variants(hero))
    for ln in P["links"]:
        slug = ln["label"].lower()
        write(f"badge-{slug}", {th: badge(th, ln["label"], ln["color"]) for th in ("light", "dark")})

    stats = {}
    for th in ("light", "dark"):
        for w, key in ((DESKTOP, th), (PHONE, f"phone-{th}")):
            stats[key], stats_alt = stats_board(w, th, d)
    write("github", stats)

    ly = data["last_year_days"]
    six = [x for x in ly if x[0] > today - dt.timedelta(days=182)]
    six_total = sum(c for _, c in six)
    graphs = {"graph-6m": (six, fmt(six_total), "contributions in the last 6 months")}
    graphs["graph-12m"] = (ly, fmt(data["last_year"]), "contributions in the last 12 months")
    for yr, (tot, ds) in data["years"].items():
        graphs[f"graph-{yr}"] = (ds, fmt(tot), f"contribution{'s' if tot != 1 else ''} in {yr}")
    for name, (ds, num, rest) in graphs.items():
        out = {}
        for th in ("light", "dark"):
            out[th] = heatmap(DESKTOP, th, ds, num, rest)
            pds = ds if name != "graph-6m" else [x for x in ds if x[0] > today - dt.timedelta(days=91)]
            out[f"phone-{th}"] = heatmap(PHONE, th, pds, num, rest)
        write(name, out)

    last30 = [x for x in ly if x[0] > today - dt.timedelta(days=30)]
    lines = {}
    for th in ("light", "dark"):
        for w, key in ((DESKTOP, th), (PHONE, f"phone-{th}")):
            lines[key], total30 = line30(w, th, last30)
    write("line-30d", lines)

    who = {}
    for th in ("light", "dark"):
        for w, key in ((DESKTOP, th), (PHONE, f"phone-{th}")):
            who[key], who_alt = whoami(w, th)
    write("whoami", who)

    write("label-ship", variants(label, "What I ship", f'{len(P["apps"])} things I built'))
    app_alts = {}
    tallest = {w: max(app_card(w, "light", app)[2] for app in P["apps"]) for w in (DESKTOP, PHONE)}
    for app in P["apps"]:
        out = {}
        for th in ("light", "dark"):
            for w, key in ((DESKTOP, th), (PHONE, f"phone-{th}")):
                out[key], app_alts[app["slug"]], _ = app_card(w, th, app, force_h=tallest[w])
        write(f'app-{app["slug"]}', out)

    # ---------------- README
    R = [pic("hero", f"Hi, I'm {P['name']}. {P['tagline']}", href=P["home"]), "",
         '<p align="center">', *[badge_pic(l["label"].lower(), l["label"], l["url"]) for l in P["links"]], "</p>", "",
         pic("github", stats_alt), "",
         pic("graph-6m", f"{fmt(six_total)} contributions in the last 6 months"), ""]
    R += ["<details><summary>Last 12 months: " + fmt(data["last_year"]) + " contributions</summary>", "",
          pic("graph-12m", f'{fmt(data["last_year"])} contributions in the last 12 months'), "", "</details>", ""]
    for yr in sorted(data["years"], reverse=True):
        tot = data["years"][yr][0]
        word = "contribution" if tot == 1 else "contributions"
        R += [f"<details><summary>{yr}: {fmt(tot)} {word}</summary>", "",
              pic(f"graph-{yr}", f"{fmt(tot)} {word} in {yr}"), "", "</details>", ""]
    R += [pic("line-30d", f"{fmt(total30)} contributions in the last 30 days"), "",
          pic("whoami", who_alt), "",
          pic("label-ship", "What I ship"), "",
          '<p align="center">']
    for app in P["apps"]:
        R.append(pic(f'app-{app["slug"]}', app_alts[app["slug"]], width="49%", href=app["url"]))
    R += ["</p>", "",
          '<p align="center"><sub>more builds: ' + " · ".join(f'<a href="{m["url"]}">{escape(m["label"])}</a>' for m in P["more"]) + "</sub></p>", "",
          '<p align="center"><picture><source media="(prefers-color-scheme: dark)" '
          'srcset="https://raw.githubusercontent.com/farazkabbo/farazkabbo/output/github-snake-dark.svg">'
          '<img src="https://raw.githubusercontent.com/farazkabbo/farazkabbo/output/github-snake.svg" width="100%" '
          'alt="Contribution graph being eaten by a snake"></picture></p>', "",
          f'<p align="center"><sub>Drawn as a sticker board · numbers redrawn every night by a GitHub Action · '
          f'<a href="{P["home"]}">farazkabbo.github.io/Portfolio</a></sub></p>', ""]
    readme_path = (ASSETS.parent / "README.md") if a.out else ROOT / "README.md"
    readme_path.write_text("\n".join(R))
    print(f"built {len(list(ASSETS.glob('*.svg')))} SVGs and {readme_path.name}")


if __name__ == "__main__":
    main()
