"""Generates the SVG assets for the GitHub profile README.
Edit the data below and run: python3 build.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent.parent / "assets"
OUT.mkdir(exist_ok=True)

FONT = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"
BG, PANEL, LINE = "#0b0f14", "#0f151c", "#1f2a36"
TEXT, DIM, FAINT = "#d6dde6", "#7d8a99", "#3a4756"
GREEN, AMBER, BLUE, VIOLET = "#7ee787", "#e3b341", "#79c0ff", "#c297ff"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, style="", frame=True):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">
<style>
text {{ fill: {TEXT}; }}
.dim {{ fill: {DIM}; }} .faint {{ fill: {FAINT}; }}
.g {{ fill: {GREEN}; }} .a {{ fill: {AMBER}; }} .b {{ fill: {BLUE}; }} .v {{ fill: {VIOLET}; }}
{style}
</style>
{f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{LINE}"/>' if frame else ""}
{body}
</svg>
'''


def section_rule(y, left, right, w):
    return (f'<text x="28" y="{y}" font-size="11" letter-spacing="2" class="dim">{esc(left)}</text>'
            f'<line x1="{28 + len(left) * 8.8 + 14}" y1="{y - 4}" x2="{w - 28 - len(right) * 8.8 - 14}" y2="{y - 4}" stroke="{LINE}"/>'
            f'<text x="{w - 28}" y="{y}" font-size="11" letter-spacing="2" text-anchor="end" class="faint">{esc(right)}</text>')


# ---------------------------------------------------------------- 01 header
def header():
    W, H = 840, 250
    rows = [
        ("role", "AI & software engineer · co-founder, Clarus"),
        ("focus", "RAG · AI agents · APIs · data pipelines"),
        ("status", "open to spring/fall 2027 internships · new grad"),
        ("style", "measure first · ship it · keep a log"),
    ]
    body = [section_rule(34, "01  RUN LOG", "faraz.kabbo", W)]
    body.append(f'<text x="28" y="84" font-size="30" font-weight="700">Mohammed Faraz Kabbo</text>')
    body.append(f'<text x="28" y="110" font-size="13" class="dim">York University · Toronto, Canada · building AI that holds up in production</text>')
    body.append(f'<line x1="28" y1="130" x2="{W-28}" y2="130" stroke="{LINE}"/>')
    y = 158
    for k, v in rows:
        body.append(f'<text x="28" y="{y}" font-size="11" letter-spacing="2" class="dim">{k.upper()}</text>')
        body.append(f'<text x="130" y="{y}" font-size="13">{esc(v)}</text>')
        y += 24
    # live status pill
    body.append(f'<circle class="pulse" cx="{W-120}" cy="80" r="4" fill="{GREEN}"/>')
    body.append(f'<text x="{W-108}" y="84" font-size="12" class="g">status: ok</text>')
    style = ".pulse { animation: p 2.4s ease-in-out infinite; } @keyframes p { 0%,100% { opacity: 1 } 50% { opacity: .25 } }"
    return svg(W, H, "\n".join(body), style)


# ---------------------------------------------------------------- 02 trace
def trace():
    W = 840
    # months since Jan 2023
    def m(y, mo):
        return (y - 2023) * 12 + (mo - 1)
    X0, X1 = 250, W - 40
    M0, M1 = m(2023, 1), m(2027, 6)
    px = lambda mm: X0 + (mm - M0) / (M1 - M0) * (X1 - X0)
    NOW = m(2026, 9)

    # (name, start, end or None for instant, colour, note, open_ended)
    spans = [
        ("york.bsc_cs",           m(2023, 1), m(2027, 5), DIM,    "",                True),
        ("spurhacks.vroomi",      m(2025, 6), None,       AMBER,  "win",             False),
        ("gov.software_dev",      m(2025, 9), m(2026, 5), BLUE,   "co-op · 8 mo",    False),
        ("hackthevalley.mimicoo", m(2025, 10), None,      AMBER,  "win",             False),
        ("hackcanada.clarus",     m(2026, 3), None,       AMBER,  "2 awards",        False),
        ("genai_genesis.numen",   m(2026, 3), None,       VIOLET, "build",           False),
        ("gov.ai_engineer",       m(2026, 5), m(2026, 8), BLUE,   "co-op · 4 mo",    False),
        ("clarus.cofounder",      m(2026, 3), NOW,        GREEN,  "funded · NSU",    True),
    ]
    top, row = 92, 26
    H = top + row * len(spans) + 44
    body = [section_rule(34, "02  TRACE", "career.span", W)]
    body.append(f'<text x="28" y="62" font-size="12" class="dim">every milestone as a span · amber = hackathon · blue = co-op · green = live</text>')

    # year grid
    for yr in range(2023, 2028):
        x = px(m(yr, 1))
        body.append(f'<line x1="{x:.1f}" y1="{top-14}" x2="{x:.1f}" y2="{H-36}" stroke="{LINE}" stroke-dasharray="2 4"/>')
        body.append(f'<text x="{x:.1f}" y="{H-18}" font-size="11" text-anchor="middle" class="faint">{yr}</text>')

    for i, (name, s, e, col, note, open_end) in enumerate(spans):
        y = top + i * row
        body.append(f'<text x="28" y="{y+4}" font-size="12" class="dim">{esc(name)}</text>')
        delay = 0.15 * i
        if e is None:
            cx = px(s)
            body.append(f'<g class="in" style="animation-delay:{delay:.2f}s"><path d="M{cx:.1f} {y-6} L{cx+6:.1f} {y} L{cx:.1f} {y+6} L{cx-6:.1f} {y} Z" fill="{col}"/></g>')
            body.append(f'<text x="{cx+14:.1f}" y="{y+4}" font-size="11" class="in" style="fill:{col}; animation-delay:{delay:.2f}s">{esc(note)}</text>')
        else:
            x1, x2 = px(s), px(e)
            body.append(f'<rect class="grow" style="animation-delay:{delay:.2f}s; transform-origin:{x1:.1f}px {y}px" x="{x1:.1f}" y="{y-5}" width="{x2-x1:.1f}" height="10" rx="2" fill="{col}" fill-opacity="{0.35 if col == DIM else 0.9}"/>')
            if open_end:
                body.append(f'<line x1="{x2:.1f}" y1="{y}" x2="{min(x2+22, X1):.1f}" y2="{y}" stroke="{col}" stroke-dasharray="2 3"/>')
            if note:
                lx = x2 + (28 if open_end else 10)
                anchor = "start"
                if lx + len(note) * 7 > W - 20:
                    lx, anchor = x1 - 10, "end"
                body.append(f'<text x="{lx:.1f}" y="{y+4}" font-size="11" text-anchor="{anchor}" class="in" style="fill:{col}; animation-delay:{delay:.2f}s">{esc(note)}</text>')

    nx = px(NOW)
    body.append(f'<line x1="{nx:.1f}" y1="{top-18}" x2="{nx:.1f}" y2="{H-36}" stroke="{GREEN}" stroke-width="1"/>')
    body.append(f'<text x="{nx:.1f}" y="{top-22}" font-size="10" text-anchor="middle" class="g">now</text>')

    style = (".grow { transform: scaleX(0); animation: g .9s cubic-bezier(.2,.7,.2,1) forwards; } "
             "@keyframes g { to { transform: scaleX(1) } } "
             ".in { opacity: 0; animation: f .5s ease-out forwards; } @keyframes f { to { opacity: 1 } }")
    return svg(W, H, "\n".join(body), style)


# ---------------------------------------------------------------- 03 build cards
def card(num, num_col, metric, name, what, stack, event):
    W, H = 268, 232
    b = [
        f'<text x="22" y="64" font-size="44" font-weight="700" style="fill:{num_col}">{esc(num)}</text>',
        f'<text x="22" y="88" font-size="11" class="dim">{esc(metric)}</text>',
        f'<line x1="22" y1="108" x2="{W-22}" y2="108" stroke="{LINE}"/>',
        f'<text x="22" y="138" font-size="17" font-weight="700" letter-spacing="1">{esc(name)}</text>',
        f'<text x="22" y="160" font-size="12" class="dim">{esc(what)}</text>',
        f'<text x="22" y="186" font-size="11">{esc(stack)}</text>',
        f'<text x="22" y="210" font-size="10" class="faint">{esc(event)}</text>',
    ]
    return svg(W, H, "\n".join(b))


def builds_header():
    W, H = 840, 70
    body = [section_rule(34, "03  BUILDS", "one number each", W),
            f'<text x="28" y="56" font-size="12" class="dim">three of 13 hackathon builds · the rest are on devpost</text>']
    return svg(W, H, "\n".join(body), frame=False)


files = {
    "header.svg": header(),
    "trace.svg": trace(),
    "builds.svg": builds_header(),
    "card-clarus.svg": card("0", GREEN, "manual handoffs across 5 systems", "CLARUS",
                            "AI healthcare workflow agent", "Python · FastAPI · agents",
                            "Hack Canada 2026 · 2 awards · funded"),
    "card-numen.svg": card("60%+", VIOLET, "questions answered, no human needed", "NUMEN",
                           "multi-agent team knowledge", "Gemini · hybrid search",
                           "GenAI Genesis 2026"),
    "card-mimicoo.svg": card("85%", AMBER, "classifier accuracy", "MIMICOO",
                             "infant babble analysis", "Python · ML · FastAPI",
                             "HackTheValley 2025 · winner"),
}
for n, s in files.items():
    (OUT / n).write_text(s)
print("wrote", ", ".join(files))
