#!/usr/bin/env python3
"""Generate 3 SVG cover options (1200x630) for an article or course.

Usage: python tools/make_covers.py [--plain-only] [--lang xx --author "Name"] <out_dir> <motif> "<title>" ["<kicker>"]
  --lang xx  writes only the titled covers, as cover-N.xx.svg: the version of a cover for the xx pages
             (the site picks it by language; text-free twins are shared by all languages)
  motif: pi | robot | tree | cpp | cpu | code | wave | net | btree | heap
Writes <out_dir>/cover-1.svg, cover-2.svg, cover-3.svg (with the title: for cards and lists)
and cover-1-plain.svg ... cover-3-plain.svg (illustration only: above the title on the article page;
the site picks the -plain twin of the chosen cover automatically). --plain-only writes just the latter.
  1 "paper"     light background, motif on the right (no accent stripes on any variant)
  2 "night"     dark background, large faint motif behind the title
  3 "blueprint" accent background with a grid, white line-art
  4 "pastel"    (motif pi only) peach-lavender gradient, fading rows of digits, a big π in a glass circle;
                it has no title, so cover-4-plain.svg is the same picture
"""
import math
import os
import sys
from xml.sax.saxutils import escape

W, H = 1200, 630
PI = ("31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
      "82148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964")


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    lines.append(cur)
    return lines


def title_block(title, x, y, size, color, width, bottom=500):
    """Title lines from baseline y; a long title gets smaller (and wider lines) so the last baseline stays
    above `bottom`."""
    out = []
    while size > 30 and y + (len(wrap(title, width)) - 1) * size * 1.12 > bottom:
        size -= 4
        width = int(width * 1.1) + 1
    for i, line in enumerate(wrap(title, width)):
        out.append('<text x="%d" y="%d" font-family="\'Source Serif 4\', Georgia, serif" font-weight="600" '
                   'font-size="%d" fill="%s">%s</text>' % (x, y + i * size * 1.12, size, color, escape(line)))
    return "\n".join(out)


def kicker_text(text, x, y, color):
    return ('<text x="%d" y="%d" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="22" '
            'letter-spacing="2" fill="%s">%s</text>' % (x, y, color, escape(text.upper())))


# ---------------------------------------------------------------- motifs
# each motif draws inside the box (x, y, w, h) with stroke colour s and highlight colour a

def m_pi(x, y, w, h, s, a):
    cols, rows = 14, 9
    dx, dy = w / cols, h / rows
    out, k = [], 0
    hl = set(range(4 * cols + 3, 4 * cols + 9))  # a highlighted run, like a found birthday
    for r in range(rows):
        for c in range(cols):
            d = PI[k % len(PI)]
            cx, cy = x + c * dx + dx / 2, y + r * dy + dy * .7
            if k in hl:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" opacity=".18"/>'
                           % (cx - dx / 2 + 2, cy - dy * .72, dx - 4, dy * .95, a))
            out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="\'JetBrains Mono\', Consolas, monospace" '
                       'font-size="%d" fill="%s" opacity="%s">%s</text>'
                       % (cx, cy, int(dy * .55), a if k in hl else s, "1" if k in hl else ".55", d))
            k += 1
    return "\n".join(out)


def m_robot(x, y, w, h, s, a):
    rel = [(.18, .92), (.30, .38), (.66, .18), (.84, .46)]  # base, elbow, wrist, gripper
    pts = [(x + w * u, y + h * v) for u, v in rel]
    bx, by = pts[0]
    out = ['<rect x="%.1f" y="%.1f" width="120" height="18" rx="4" fill="%s" opacity=".5"/>' % (bx - 60, by + 6, s)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="16" stroke-linecap="round"/>'
                   % (x1, y1, x2, y2, s))
    for px, py in pts:
        out.append('<circle cx="%.1f" cy="%.1f" r="13" fill="none" stroke="%s" stroke-width="5"/>' % (px, py, a))
    ex, ey = pts[-1]
    tx, ty = x + w * .9, y + h * .85
    out.append('<path d="M%.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="4" stroke-dasharray="10 10"/>'
               % (ex, ey, ex - w * .2, (ey + ty) / 2, tx, ty, a))
    out.append('<circle cx="%.1f" cy="%.1f" r="22" fill="none" stroke="%s" stroke-width="4"/>' % (tx, ty, a))
    out.append('<path d="M%.1f %.1fh60M%.1f %.1fv60" stroke="%s" stroke-width="4"/>' % (tx - 30, ty, tx, ty - 30, a))
    return "\n".join(out)


def m_tree(x, y, w, h, s, a):
    nodes = {"stmt": (.5, .08), "if": (.25, .38), "=": (.75, .38), "cond": (.12, .7), "then": (.38, .7),
             "x": (.62, .7), "+": (.88, .7), "a": (.8, .97), "1": (.96, .97)}
    edges = [("stmt", "if"), ("stmt", "="), ("if", "cond"), ("if", "then"), ("=", "x"), ("=", "+"), ("+", "a"), ("+", "1")]
    P = {k: (x + w * u, y + h * v * .9) for k, (u, v) in nodes.items()}
    out = []
    for p, c in edges:
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4" opacity=".7"/>'
                   % (P[p] + P[c] + (s,)))
    for k, (cx, cy) in P.items():
        hl = k in ("if", "=")
        out.append('<rect x="%.1f" y="%.1f" width="96" height="48" rx="12" fill="%s" stroke="%s" stroke-width="4"/>'
                   % (cx - 48, cy - 24, a if hl else "none", a if hl else s))
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="\'JetBrains Mono\', Consolas, monospace" '
                   'font-size="22" fill="%s">%s</text>' % (cx, cy + 8, "#ffffff" if hl else s, escape(k)))
    return "\n".join(out)


def m_code(x, y, w, h, s, a, lines=None):
    lines = lines or ["template <typename T>", "class Pool {", "  alignas(64) T* data_;", "  size_t size_;",
                      "public:", "  T& operator[](size_t i)", "    noexcept { return data_[i]; }", "};"]
    out, lh = [], h / (len(lines) + .5)
    for i, ln in enumerate(lines):
        out.append('<text x="%.1f" y="%.1f" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="%d" '
                   'fill="%s" xml:space="preserve">%s</text>'
                   % (x, y + lh * (i + 1), int(lh * .62), a if i in (0, 5) else s, escape(ln)))
    return "\n".join(out)


def m_cpp(x, y, w, h, s, a):
    return m_code(x, y, w, h, s, a)


def m_cpu(x, y, w, h, s, a):
    out = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="18" fill="none" stroke="%s" stroke-width="5"/>'
           % (x, y, w, h, s)]
    pad, cw, ch = 24, (w - 24 * 5) / 4, (h * .55 - 24 * 3) / 2
    for r in range(2):
        for c in range(4):
            cx, cy = x + pad + c * (cw + pad), y + pad + r * (ch + pad)
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" opacity="%s"/>'
                       % (cx, cy, cw, ch, a, ".85" if (r, c) == (0, 1) else ".25"))
            out.append('<text x="%.1f" y="%.1f" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="18" fill="%s">L1</text>'
                       % (cx + 10, cy + 26, s))
    ly = y + h * .55 + 6
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="none" stroke="%s" stroke-width="4"/>'
               % (x + pad, ly, w - 2 * pad, h * .18, a))
    out.append('<text x="%.1f" y="%.1f" font-family="\'JetBrains Mono\', Consolas, monospace" font-size="22" fill="%s">%s</text>'
               % (x + pad + 14, ly + h * .11, s, escape(CACHE_LABEL.get(LANG, "L3 cache"))))
    for i in range(10):  # pins
        px = x + 30 + i * (w - 60) / 9
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5"/>' % (px, y + h, px, y + h + 22, s))
    return "\n".join(out)


def cover_pastel_pi(motif, title, kicker, plain=False, dark=False):
    """The pi tile of design mockup A, scaled to 1200x630 (digits run off the left edge).
    dark=True: the same picture for the dark theme (written as cover-4-dark.svg)."""
    mono = "'JetBrains Mono', Consolas, 'Courier New', monospace"
    g1, g2, ink, glass, ring = ("#3a2433", "#2b2142", "#b6a6f5", ".08", ".35") if dark else ("#ffd6c9", "#d9d2ff", "#7a5fa8", ".35", ".7")
    rows = [("3.14159 26535 89793", ".35"), ("23846 26433 83279", ".25"), ("50288 41971 69399", ".15")]
    body = ['<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % (g1, g2),
            '<rect width="1200" height="630" fill="url(#pg)"/>',
            '<circle cx="890" cy="190" r="257" fill="#ffffff" opacity="%s"/>' % glass,
            '<circle cx="890" cy="190" r="154" fill="none" stroke="#ffffff" stroke-width="3" opacity="%s"/>' % ring]
    for i, (row, op) in enumerate(rows):
        body.append('<text x="-14" y="%d" font-family="%s" font-size="75" fill="%s" opacity="%s">%s</text>'
                    % (154 + i * 103, mono, ink, op, row))
    body.append('<text x="806" y="257" font-family="Georgia, \'Times New Roman\', serif" font-size="206" fill="#ffffff" opacity=".9">π</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n%s\n</svg>\n'
            % (W, H, W, H, "\n".join(body)))


MONO = "'JetBrains Mono', Consolas, monospace"


def m_wave(x, y, w, h, s, a):
    """Digital waveforms as in a VCD viewer: a clock, two single-bit signals and an 8-bit bus."""
    out, rows, step = [], 4, w / 12
    rh = h / rows
    bits = {"clk": [i % 2 for i in range(12)], "en": [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            "rdy": [0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0]}
    for r, (name, seq) in enumerate(bits.items()):
        hi, lo = y + r * rh + rh * .2, y + r * rh + rh * .7
        pts, prev = [], None
        for i, b in enumerate(seq):
            yy = hi if b else lo
            if prev is not None and prev != yy:
                pts.append((x + i * step, prev))
            pts.append((x + i * step, yy))
            prev = yy
        pts.append((x + w, prev))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4" stroke-linejoin="round"/>'
                   % (" ".join("%.1f,%.1f" % p for p in pts), a if name == "clk" else s))
    by0, by1, edges = y + 3 * rh + rh * .2, y + 3 * rh + rh * .7, [0, 3, 7, 10, 12]
    vals = ["0a", "1f", "c3", "ff"]
    for k in range(len(edges) - 1):
        x0, x1 = x + edges[k] * step, x + edges[k + 1] * step
        d = 10
        out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" '
                   'stroke="%s" stroke-width="4"/>' % (x0 + d, by0, x1 - d, by0, x1, (by0 + by1) / 2, x1 - d, by1,
                                                     x0 + d, by1, x0, (by0 + by1) / 2, s))
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="%s" font-size="24" fill="%s">%s</text>'
                   % ((x0 + x1) / 2, (by0 + by1) / 2 + 8, MONO, a if k == 2 else s, vals[k]))
    return "\n".join(out)


def m_net(x, y, w, h, s, a):
    """A small fully connected neural network: 3 - 5 - 4 - 2."""
    layers = [3, 5, 4, 2]
    P = [[(x + w * (li + .5) / len(layers), y + h * (ni + .5) / n) for ni in range(n)] for li, n in enumerate(layers)]
    out = []
    for li in range(len(layers) - 1):
        for p in P[li]:
            for q in P[li + 1]:
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" opacity=".45"/>'
                           % (p + q + (s,)))
    for li, col in enumerate(P):
        for ni, (cx, cy) in enumerate(col):
            hl = (li, ni) in ((1, 2), (2, 1), (3, 0))
            out.append('<circle cx="%.1f" cy="%.1f" r="24" fill="%s" stroke="%s" stroke-width="4"/>'
                       % (cx, cy, a if hl else "none", a if hl else s))
    return "\n".join(out)


def m_btree(x, y, w, h, s, a):
    """A B-tree: a root with two keys, three children with up to three keys each."""
    kw, kh = 56, 50
    nodes = [((.5, .1), ["40", "80"], True), ((.15, .62), ["12", "25", "31"], False),
             ((.5, .62), ["47", "63"], False), ((.85, .62), ["85", "91", "97"], False)]
    out, boxes = [], []
    for (u, v), keys, root in nodes:
        nw = kw * len(keys)
        bx, by = x + w * u - nw / 2, y + h * v
        boxes.append((bx, by, nw))
        for i, k in enumerate(keys):
            out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="4"/>'
                       % (bx + i * kw, by, kw, kh, a if root else "none", a if root else s))
            out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-family="%s" font-size="22" fill="%s">%s</text>'
                       % (bx + i * kw + kw / 2, by + kh / 2 + 8, MONO, "#ffffff" if root else s, k))
    rx, ry, rw = boxes[0]
    for i, (cx, cy, cw) in enumerate(boxes[1:]):
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4" opacity=".7"/>'
                   % (rx + i * kw, ry + kh, cx + cw / 2, cy, s))
    # leaf pages on disk under the children
    for cx, cy, cw in boxes[1:]:
        for j in range(3):
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="10" rx="3" fill="%s" opacity="%s"/>'
                       % (cx, cy + kh + 22 + j * 18, cw, s, ".5" if j == 0 else ".25"))
    return "\n".join(out)


def m_heap(x, y, w, h, s, a):
    """A memory arena before and after defragmentation: used blocks (accent) and free gaps."""
    before = [(.0, .14, 1), (.14, .1, 0), (.24, .2, 1), (.44, .16, 0), (.6, .12, 1), (.72, .08, 0), (.8, .2, 1)]
    after = [(.0, .14, 1), (.14, .2, 1), (.34, .12, 1), (.46, .2, 1), (.66, .34, 0)]
    out, bh = [], h * .22
    for row, blocks in ((y + h * .08, before), (y + h * .62, after)):
        for u, du, used in blocks:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" stroke="%s" '
                       'stroke-width="4" opacity="%s"/>' % (x + w * u + 3, row, w * du - 6, bh, a if used else "none",
                                                           a if used else s, ".9" if used else ".6"))
    mx, top, bot = x + w * .5, y + h * .08 + bh + 16, y + h * .62 - 16
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4" stroke-dasharray="10 8"/>'
               % (mx, top, mx, bot - 14, s))
    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (mx - 14, bot - 18, mx + 14, bot - 18, mx, bot, s))
    return "\n".join(out)


MOTIFS = {"pi": m_pi, "robot": m_robot, "tree": m_tree, "cpp": m_cpp, "cpu": m_cpu, "code": m_code,
          "wave": m_wave, "net": m_net, "btree": m_btree, "heap": m_heap}


def svg(body, bg):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n'
            '<rect width="%d" height="%d" fill="%s"/>\n%s\n</svg>\n' % (W, H, W, H, W, H, bg, body))


def cover_paper(motif, title, kicker, plain=False):
    if plain:
        body = [motif(330, 100, 540, 430, "#5d6470", "#004f90")]
        return svg("\n".join(body), "#fbfaf7")
    body = [motif(700, 120, 430, 390, "#5d6470", "#004f90"),
            kicker_text(kicker, 72, 120, "#004f90"),
            title_block(title, 72, 210, 60, "#1c1f24", 18),
            '<text x="72" y="560" font-family="Inter, Arial, sans-serif" font-size="24" fill="#5d6470">%s · favorart.github.io</text>' % escape(AUTHOR) + '']
    return svg("\n".join(body), "#fbfaf7")


def cover_night(motif, title, kicker, plain=False):
    if plain:
        body = ['<g opacity=".75">%s</g>' % motif(300, 70, 600, 490, "#9aa3ae", "#6aaef0")]
        return svg("\n".join(body), "#111418")
    body = ['<g opacity=".35">%s</g>' % motif(560, 40, 600, 520, "#9aa3ae", "#6aaef0"),
            '<rect x="0" y="0" width="1200" height="630" fill="url(#fade)"/>',
            kicker_text(kicker, 72, 360, "#6aaef0"),
            title_block(title, 72, 440, 52, "#e7e9ec", 30)]
    defs = ('<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#111418"/>'
            '<stop offset=".55" stop-color="#111418" stop-opacity=".6"/><stop offset="1" stop-color="#111418" stop-opacity="0"/>'
            '</linearGradient></defs>')
    return svg(defs + "\n" + "\n".join(body), "#111418")


def cover_blueprint(motif, title, kicker, plain=False):
    grid = []
    for gx in range(0, W + 1, 40):
        grid.append('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="#ffffff" stroke-opacity="%s"/>' % (gx, gx, H, ".16" if gx % 200 == 0 else ".06"))
    for gy in range(0, H + 1, 40):
        grid.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#ffffff" stroke-opacity="%s"/>' % (gy, W, gy, ".16" if gy % 200 == 0 else ".06"))
    if plain:
        body = ["\n".join(grid), motif(340, 130, 520, 380, "#ffffff", "#9fd0ff"),
                '<rect x="60" y="60" width="1080" height="510" fill="none" stroke="#ffffff" stroke-opacity=".5" stroke-width="2"/>']
        return svg("\n".join(body), "#004f90")
    body = ["\n".join(grid),
            motif(640, 200, 480, 360, "#ffffff", "#9fd0ff"),
            '<rect x="60" y="60" width="1080" height="510" fill="none" stroke="#ffffff" stroke-opacity=".5" stroke-width="2"/>',
            kicker_text(kicker, 100, 130, "#9fd0ff"),
            title_block(title, 100, 205, 46, "#ffffff", 22)]
    return svg("\n".join(body), "#004f90")


AUTHOR = "Kirill Golikov"
LANG = "en"
CACHE_LABEL = {"en": "L3 cache", "es": "caché L3", "ru": "кэш L3", "sr": "L3 keš", "uz": "L3 kesh"}


def main():
    global AUTHOR, LANG
    argv, lang = sys.argv[1:], None
    for opt in ("--lang", "--author"):
        if opt in argv:
            k = argv.index(opt)
            val = argv[k + 1]
            del argv[k:k + 2]
            if opt == "--lang":
                lang = LANG = val
            else:
                AUTHOR = val
    args = [a for a in argv if a != "--plain-only"]
    plain_only = len(args) != len(argv)
    if len(args) < 3:
        sys.exit(__doc__)
    out_dir, motif_name, title = args[0], args[1], args[2]
    kicker = args[3] if len(args) > 3 else "Kirill Golikov"
    motif = MOTIFS[motif_name]
    os.makedirs(out_dir, exist_ok=True)
    styles = [cover_paper, cover_night, cover_blueprint] + ([cover_pastel_pi] if motif_name == "pi" else [])
    for n, fn in enumerate(styles, 1):
        variants = [("-plain", True)] if plain_only else [("", False), ("-plain", True)]
        if lang:
            variants = [("." + lang, False)]
        for suffix, plain in variants:
            with open(os.path.join(out_dir, "cover-%d%s.svg" % (n, suffix)), "w", encoding="utf-8", newline="\n") as f:
                f.write(fn(motif, title, kicker, plain))
    k = len(styles)
    if motif_name == "pi":  # dark-theme twin of the pastel style
        for suffix, plain in variants:
            with open(os.path.join(out_dir, "cover-4-dark%s.svg" % suffix), "w", encoding="utf-8", newline="\n") as f:
                f.write(cover_pastel_pi(motif, title, kicker, plain, dark=True))
    print("wrote %s covers to %s" % ("%d text-free" % k if plain_only else "%d + %d text-free" % (k, k), out_dir))


if __name__ == "__main__":
    main()
