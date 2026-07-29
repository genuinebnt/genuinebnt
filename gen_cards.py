"""Renders the README's sections as SVG, styled from genuinebasil.dev's own CSS.

GitHub strips CSS from markdown, so an SVG is the only way to reuse the site's
component styles. Every value below is lifted from frontend/styles — the theme
maps in _tokens.scss ($themes.dark / $themes.light, $topics) and the component
rules in _components.scss / _home.scss:

  .card           surface fill, 1px border, 2px accent LEFT border, --radius, 16px pad
  .card h3        mono 14px/500, --acc          .card p      12.5px, --muted, lh 1.6
  .home-proj-row  3px topic bar, 12px 14px pad  .hpr-name    mono 13px/500
  .hpr-desc       12px --muted lh 1.55          .hpr-chip    mono 10px, pill, --surface2
  .eyebrow        mono 11px --acc, .12em, upper
  .section-label  mono 10px --faint, .15em, upper
  .divider5       3px bar: warn / purple / blue / acc / faint
  h1              30px/500, -0.025em           .lead        15px --muted lh 1.75

Each section carries its own label and rule so the README needs no markdown
headings, which GitHub would render in its own sans and defeat the point.

Webfonts cannot load inside an <img>-embedded SVG, so the stacks below are
limited to fonts the viewer already has.
"""

from html import escape

THEMES = {
    "dark": dict(bg="#0d0f12", surface="#13161b", surface2="#1a1e25", border="#232830",
                 border2="#2e3540", text="#e2e6ee", muted="#6b7280", faint="#3a4050",
                 acc="#00d4a4", blue="#60a5fa", purple="#a78bfa", warn="#f59e0b"),
    "light": dict(bg="#f6f7f9", surface="#ffffff", surface2="#f0f2f5", border="#e4e8ee",
                  border2="#d3dae3", text="#1a1e25", muted="#5b6573", faint="#9aa4b2",
                  acc="#008f6f", blue="#2563eb", purple="#7c3aed", warn="#c2740a"),
}

# $topics — fixed hex, deliberately not theme-dependent (a topic's colour is its
# own identity). See _tokens.scss:91 and _home.scss's .t-* rules.
TOPICS = {"rust": "#f0703c", "distributed": "#4a90e8", "systems": "#9270e0"}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"

W = 880
RADIUS = 6


def wrap(text, width_px, size, mono=False):
    """Greedy wrap using an average advance width — SVG has no text metrics."""
    per_char = size * (0.6 if mono else 0.515)
    limit = max(1, int(width_px / per_char))
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if len(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def head(width, height, label):
    # No background rect anywhere: the SVGs sit directly on GitHub's canvas.
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">')


def styles(t, extra=""):
    return f"""<style>
.card {{ fill: {t['surface']}; stroke: {t['border']}; stroke-width: 1; }}
.acc-edge {{ fill: {t['acc']}; }}
.eyebrow {{ font: 500 11px {MONO}; fill: {t['acc']}; letter-spacing: 1.32px; }}
.seclabel {{ font: 400 10px {MONO}; fill: {t['faint']}; letter-spacing: 1.5px; }}
.rule {{ stroke: {t['border']}; stroke-width: 1; }}
.h1 {{ font: 500 30px {SANS}; fill: {t['text']}; letter-spacing: -0.75px; }}
.h1acc {{ font: 500 30px {SANS}; fill: {t['acc']}; letter-spacing: -0.75px; }}
.lead {{ font: 400 15px {SANS}; fill: {t['muted']}; }}
.cardtitle {{ font: 500 14px {MONO}; fill: {t['acc']}; }}
.cardbody {{ font: 400 12.5px {SANS}; fill: {t['muted']}; }}
.name {{ font: 500 13px {MONO}; fill: {t['text']}; }}
.desc {{ font: 400 12px {SANS}; fill: {t['muted']}; }}
.chip {{ fill: {t['surface2']}; stroke: {t['border']}; stroke-width: 1; }}
.chiptext {{ font: 400 10px {MONO}; fill: {t['muted']}; }}
.pill {{ fill: {t['surface']}; stroke: {t['border']}; stroke-width: 1; }}
.pilltext {{ font: 400 11px {MONO}; fill: {t['muted']}; }}
.pillstrong {{ font: 500 11px {MONO}; fill: {t['text']}; }}
{extra}</style>"""


def section_label(text, y, width=W):
    """.section-label + the hairline the site pairs it with."""
    return (f'<text class="seclabel" x="0" y="{y}">{escape(text.upper())}</text>'
            f'<line class="rule" x1="0" y1="{y + 12}" x2="{width}" y2="{y + 12}"/>')


def divider5(t, y, width=W):
    """.divider5 — warn / purple / blue / acc / faint, 3px tall, 2px radius."""
    cols = [t["warn"], t["purple"], t["blue"], t["acc"], t["faint"]]
    seg = width / len(cols)
    out = [f'<g><clipPath id="d5"><rect x="0" y="{y}" width="{width}" height="3" rx="2"/></clipPath>',
           '<g clip-path="url(#d5)">']
    for i, c in enumerate(cols):
        out.append(f'<rect x="{i * seg:.1f}" y="{y}" width="{seg:.1f}" height="3" fill="{c}"/>')
    out.append("</g></g>")
    return "".join(out)


def chips(items, x, y, t):
    """.hpr-chip row — mono 10px in a 100px-radius pill."""
    out, cx = [], x
    for item in items:
        w = len(item) * 6 + 16
        out.append(f'<rect class="chip" x="{cx}" y="{y}" width="{w}" height="17" rx="8.5"/>')
        out.append(f'<text class="chiptext" x="{cx + 8}" y="{y + 12}">{escape(item)}</text>')
        cx += w + 5
    return "".join(out)


# ── sections ────────────────────────────────────────────────────────────────

def hero(t):
    h = 268
    p = [head(W, h, "Genuine Basil — Rust, distributed systems, database internals"), styles(t),
         
         '<text class="eyebrow" x="0" y="26">GENUINE BASIL · SYSTEMS ENGINEER</text>',
         '<text class="h1" x="0" y="66">I build the layer <tspan class="h1acc">underneath</tspan> the application.</text>']
    lead = ("Storage engines, consensus protocols, job queues, request tracing. Deliberately close to "
            "database and distributed infrastructure: the way I understand how systems like Postgres, "
            "CockroachDB and Snowflake work is by building smaller versions of the same problems myself.")
    y = 96
    for line in wrap(lead, 620, 15):
        p.append(f'<text class="lead" x="0" y="{y}">{escape(line)}</text>')
        y += 26
    y += 6
    pills = [("Rust", ""), ("distributed systems", ""), ("database internals", ""), ("genuinebasil.dev", "")]
    px = 0
    for label, _ in pills:
        w = len(label) * 6.6 + 24
        p.append(f'<rect class="pill" x="{px}" y="{y}" width="{w:.0f}" height="24" rx="12"/>')
        p.append(f'<text class="pilltext" x="{px + 12}" y="{y + 16}">{escape(label)}</text>')
        px += w + 8
    p.append(divider5(t, y + 38))
    p.append("</svg>")
    return "\n".join(p)


PROJECTS = [
    ("db-labs", "rust", "Rust · storage & recovery",
     "A database, written from the disk up. An LSM-tree storage engine — write-ahead log, SSTables, "
     "bloom filters, leveled compaction — plus a Raft-backed key-value store exercised under chaos testing.",
     ["WAL", "MVCC", "B+ tree", "compaction", "recovery"]),
    ("gossip-glomers", "distributed", "Rust · consensus & fault tolerance",
     "Distributed systems that survive the network. Fly.io's challenge set, solved and written up one at "
     "a time — efficient broadcast under partition, a grow-only counter, a replicated log.",
     ["Raft", "replication", "partitions", "linearizability"]),
]


def work(t):
    row_h, gap, top = 108, 10, 30
    h = top + len(PROJECTS) * row_h + (len(PROJECTS) - 1) * gap
    p = [head(W, h, "current work"), styles(t),
         section_label("current work", 10)]
    y = top
    for name, topic, meta, desc, tags in PROJECTS:
        bar = TOPICS[topic]
        p.append(f'<g transform="translate(0,{y})">')
        # .home-proj-row — 3px topic bar clipped to the rounded shell.
        p.append(f'<clipPath id="c{name}"><rect x="0" y="0" width="{W}" height="{row_h}" rx="{RADIUS}"/></clipPath>')
        p.append(f'<rect class="card" x="0.5" y="0.5" width="{W - 1}" height="{row_h - 1}" rx="{RADIUS}"/>')
        p.append(f'<g clip-path="url(#c{name})"><rect x="0" y="0" width="3" height="{row_h}" fill="{bar}"/></g>')
        p.append(f'<text class="name" x="18" y="26">{escape(name)}</text>')
        p.append(f'<text class="chiptext" x="{18 + len(name) * 8 + 14}" y="26">{escape(meta)}</text>')
        ty = 48
        for line in wrap(desc, W - 60, 12):
            p.append(f'<text class="desc" x="18" y="{ty}">{escape(line)}</text>')
            ty += 19
        p.append(chips(tags, 18, row_h - 30, t))
        p.append("</g>")
        y += row_h + gap
    p.append("</svg>")
    return "\n".join(p)


FOCUS = [
    ("storage engines", "LSM trees, B+ trees, WAL, MVCC, compaction"),
    ("consensus", "Raft, replication, partition tolerance"),
    ("query processing", "planning, execution, columnar & vectorized"),
    ("data platforms", "warehouse internals, pipelines, cloud-native OLAP"),
    ("systems craft", "async runtimes, observability, backpressure"),
    ("security", "bug bounty on Bugcrowd, reversing with IDA Pro & Ghidra"),
]


def focus(t):
    cols, cw, ch, gap, top = 2, 435, 72, 10, 30
    rows = (len(FOCUS) + cols - 1) // cols
    h = top + rows * ch + (rows - 1) * gap
    p = [head(W, h, "focus areas"), styles(t),
         section_label("focus", 10)]
    for i, (title, desc) in enumerate(FOCUS):
        x = (i % cols) * (cw + gap)
        y = top + (i // cols) * (ch + gap)
        p.append(f'<g transform="translate({x},{y})">')
        p.append(f'<clipPath id="f{i}"><rect x="0" y="0" width="{cw}" height="{ch}" rx="{RADIUS}"/></clipPath>')
        p.append(f'<rect class="card" x="0.5" y="0.5" width="{cw - 1}" height="{ch - 1}" rx="{RADIUS}"/>')
        # .card's 2px accent left border — full height, not an inset marker.
        p.append(f'<g clip-path="url(#f{i})"><rect class="acc-edge" x="0" y="0" width="2" height="{ch}"/></g>')
        p.append(f'<text class="cardtitle" x="16" y="28">{escape(title)}</text>')
        dy = 48
        for line in wrap(desc, cw - 32, 12.5):
            p.append(f'<text class="cardbody" x="16" y="{dy}">{escape(line)}</text>')
            dy += 18
        p.append("</g>")
    p.append("</svg>")
    return "\n".join(p)


STATUS = [("BUILDING", "a database engine"), ("SOLVING", "distributed systems"), ("WRITING", "genuinebasil.dev")]


def status(t):
    cols, gap = 3, 10
    cw = (W - (cols - 1) * gap) / cols
    h = 64
    p = [head(W, h, "current status"), styles(t)]
    for i, (label, value) in enumerate(STATUS):
        x = i * (cw + gap)
        p.append(f'<g transform="translate({x:.1f},0)">')
        p.append(f'<rect class="card" x="0.5" y="0.5" width="{cw - 1:.1f}" height="{h - 1}" rx="{RADIUS}"/>')
        p.append(f'<text class="eyebrow" x="16" y="26">{escape(label)}</text>')
        p.append(f'<text class="name" x="16" y="48">{escape(value)}</text>')
        p.append("</g>")
    p.append("</svg>")
    return "\n".join(p)


def label_only(text):
    """A standalone .section-label + rule, for sections whose body is not an SVG."""
    def build(t):
        return "\n".join([head(W, 22, text), styles(t), section_label(text, 10), "</svg>"])
    return build


if __name__ == "__main__":
    import pathlib

    out = pathlib.Path("profile-repo/assets")
    out.mkdir(parents=True, exist_ok=True)
    for theme, t in THEMES.items():
        sections = [("hero", hero), ("status", status), ("work", work), ("focus", focus),
                    ("label-stack", label_only("working set")), ("label-activity", label_only("activity"))]
        for name, fn in sections:
            path = out / f"{name}-{theme}.svg"
            path.write_text(fn(t))
            print(f"  {path}  {path.stat().st_size}B")
