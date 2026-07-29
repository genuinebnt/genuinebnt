"""Renders the focus grid as a card SVG per theme.

GitHub strips CSS from markdown, so the editor's card recipe cannot be applied
to the README directly — but an SVG is its own document and keeps its styling.
Values mirror frontend/styles/_tokens.scss ($themes.dark / $themes.light) and
the .ts-settings-card idiom: surface fill, 1px border, --radius corners, and an
accent edge standing in for the :hover / .ts-selected border-colour shift.

Webfonts cannot load inside an <img>-embedded SVG, so the type stack is limited
to fonts the viewer already has.
"""

CARDS = [
    ("storage engines", "LSM trees, B+ trees, WAL, MVCC, compaction"),
    ("consensus", "Raft, replication, partition tolerance"),
    ("query processing", "planning, execution, columnar &amp; vectorized"),
    ("data platforms", "warehouse internals, pipelines, cloud-native OLAP"),
    ("systems craft", "async runtimes, observability, backpressure"),
    ("security", "bug bounty on Bugcrowd, reversing with IDA Pro &amp; Ghidra"),
]

THEMES = {
    "dark": dict(surface="#13161b", border="#232830", text="#e2e6ee", muted="#6b7280", acc="#00d4a4"),
    "light": dict(surface="#ffffff", border="#e4e8ee", text="#1a1e25", muted="#5b6573", acc="#008f6f"),
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

COLS, CARD_W, CARD_H, GAP, RADIUS = 2, 432, 78, 14, 6
PAD_X, PAD_Y = 14, 26
WIDTH = COLS * CARD_W + (COLS - 1) * GAP
ROWS = (len(CARDS) + COLS - 1) // COLS
HEIGHT = ROWS * CARD_H + (ROWS - 1) * GAP


def render(theme: str) -> str:
    t = THEMES[theme]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="focus areas">',
        "<style>",
        f".card {{ fill: {t['surface']}; stroke: {t['border']}; stroke-width: 1; }}",
        f".edge {{ fill: {t['acc']}; }}",
        f".title {{ font: 500 13px {MONO}; fill: {t['text']}; }}",
        f".desc  {{ font: 400 11.5px {MONO}; fill: {t['muted']}; }}",
        "</style>",
    ]

    for i, (title, desc) in enumerate(CARDS):
        x = (i % COLS) * (CARD_W + GAP)
        y = (i // COLS) * (CARD_H + GAP)
        parts += [
            f'<g transform="translate({x},{y})">',
            f'<rect class="card" x="0.5" y="0.5" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="{RADIUS}"/>',
            # Stands in for the accent border the cards take when selected.
            f'<rect class="edge" x="1" y="{CARD_H / 2 - 14}" width="2" height="28" rx="1"/>',
            f'<text class="title" x="{PAD_X}" y="{PAD_Y}">{title}</text>',
            f'<text class="desc" x="{PAD_X}" y="{PAD_Y + 22}">{desc}</text>',
            "</g>",
        ]

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    import pathlib

    out = pathlib.Path("profile-repo/assets")
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        path = out / f"focus-{theme}.svg"
        path.write_text(render(theme))
        print(f"wrote {path} ({path.stat().st_size} bytes)")
