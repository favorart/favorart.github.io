"""Layout check of the built site in a headless browser, for every language, phone/tablet/desktop width and theme.

    python tools/layout_check.py _site            # after python build.py; exit code 1 on any problem
    python tools/layout_check.py _site --all      # every page, not only one page of each kind
    python tools/layout_check.py _site --json out.json

Fails on:
  overflow  the page scrolls sideways
  target    a control outside running text smaller than 40x40 px at phone width (WCAG 2.5.8 + our 40px rule)
  wrap      a single-line element (date, menu item, button, language) broken over two lines
  hanging   a short word (preposition, conjunction, article; 5 languages) left at the end of a line
Needs: pip install playwright && python -m playwright install chromium (CI), or Google Chrome with --chrome.
"""
import argparse
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build import SHORT_WORDS  # noqa: E402  the same lists the build binds with non-breaking spaces

WIDTHS = [375, 768, 1280]
THEMES = ["light", "dark"]
# single-line elements; the article's end buttons are exempt: on a phone a long call to action ("LinkedIn sahifasida
# izoh qoldirish") may take two lines of a full-width button
WRAP = ".when span:first-child, .snav a, .mnav a, .btn:not(.foot-actions .btn), .lang a, .langdd a, .crumbs a, .filters a, .k-date"

JS = r"""
(args) => {
  const res = {overflow: 0, target: [], wrap: [], hanging: []};
  const W = innerWidth;
  res.overflow = Math.max(0, document.documentElement.scrollWidth - W);
  const vis = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && !el.closest('[hidden], details:not([open]) > div'); };
  const label = el => el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : '') +
    ' "' + (el.textContent || el.value || '').trim().replace(/\s+/g, ' ').slice(0, 40) + '"';
  if (W <= 640) {
    document.querySelectorAll('a, button, summary, input:not([type=hidden]), textarea, select').forEach(el => {
      if (!vis(el) || el.matches('.stretch')) return;  // .stretch covers a whole card
      // exempt: links inside running text and inside headings (the text around them makes them easy to hit)
      if (el.tagName === 'A' && getComputedStyle(el).display === 'inline' && el.closest('p, li, td, h1, h2, h3, h4, .prose, .byline')) return;
      const r = el.getBoundingClientRect();
      if (r.height < 40 || r.width < 40) res.target.push(label(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
    });
  }
  document.querySelectorAll(args.wrap).forEach(el => {
    if (!vis(el)) return;
    // lines of text = clusters of text-box bottoms more than half a font size apart (mixed fonts shift tops a little)
    const fs = parseFloat(getComputedStyle(el).fontSize), bottoms = [], tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let tn;
    while ((tn = tw.nextNode())) { if (!tn.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tn);
      for (const q of rg.getClientRects()) if (q.width > 1) bottoms.push(q.bottom); }
    bottoms.sort((x, y) => x - y);
    let lines = bottoms.length ? 1 : 0;
    for (let i = 1; i < bottoms.length; i++) if (bottoms[i] - bottoms[i - 1] > fs * .5) lines++;
    if (lines > 1) res.wrap.push(label(el));
  });
  const set = new Set(args.short);
  const walker = document.createTreeWalker(document.querySelector('main') || document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const p = n.parentElement; if (!p || p.closest('pre, code, script, style, .sr-only, [hidden]') || !vis(p)) continue;
    const t = n.textContent, re = /(^|[\s(«"„])([^\s\d.,;:!?()«»"„“”—–-]{1,5})[ ]/g; let m;
    while ((m = re.exec(t))) {
      const w = m[2]; if (!set.has(w.toLowerCase())) continue;
      const a = m.index + m[1].length, b = a + w.length; if (b + 1 >= t.length) continue;
      const r1 = document.createRange(); r1.setStart(n, a); r1.setEnd(n, b);
      const r2 = document.createRange(); r2.setStart(n, b + 1); r2.setEnd(n, b + 2);
      const q1 = r1.getBoundingClientRect(), q2 = r2.getBoundingClientRect();
      if (q1.height && q2.height && q2.top > q1.bottom - 2) res.hanging.push(w + ' | ' + t.slice(Math.max(0, a - 25), b + 25).replace(/\s+/g, ' '));
    }
  }
  return res;
}
"""


def pages_to_check(site, check_all):
    """Language prefixes (from i18n/) and paths: home, section indexes, CV and the first item page of each section."""
    import yaml
    i18n = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "i18n")
    langs = sorted(str(yaml.safe_load(open(os.path.join(i18n, f), encoding="utf-8")).get("prefix") or "")
                   for f in os.listdir(i18n) if f.endswith(".yml"))
    paths = ["/", "/writing/", "/projects/", "/courses/", "/cv/"]
    for sec in ("writing", "projects", "courses"):
        items = sorted(d for d in os.listdir(os.path.join(site, sec))
                       if d != "covers" and os.path.isfile(os.path.join(site, sec, d, "index.html")))
        paths += ["/%s/%s/" % (sec, d) for d in (items if check_all else items[:1])]
    return langs, paths


def serve(site):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=site)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--all", action="store_true", help="every item page, not one per section")
    ap.add_argument("--chrome", action="store_true", help="use installed Google Chrome instead of Playwright's Chromium")
    ap.add_argument("--json", help="write all findings to this file")
    a = ap.parse_args()
    site = os.path.abspath(a.site)
    langs, paths = pages_to_check(site, a.all)
    srv, base = serve(site)
    found, renders = [], 0
    with sync_playwright() as p:
        kw = {"channel": "chrome", "args": ["--headless=new"]} if a.chrome else {}
        br = p.chromium.launch(**kw)
        for theme in THEMES:
            for w in WIDTHS:
                ctx = br.new_context(viewport={"width": w, "height": 900}, color_scheme=theme)
                pg = ctx.new_page()
                pg.route("**/*", lambda r: r.abort() if not r.request.url.startswith(base) and
                         "fonts.g" not in r.request.url else r.continue_())  # no analytics/external calls
                for lang in langs:
                    code = lang.strip("/") or "en"
                    for path in paths:
                        url = base + lang + path
                        resp = pg.goto(url, wait_until="networkidle")
                        renders += 1
                        if not resp or resp.status != 200:
                            found.append({"url": lang + path, "w": w, "theme": theme, "kind": "http",
                                          "what": str(resp.status if resp else "no response")})
                            continue
                        pg.evaluate("document.fonts.ready")
                        r = pg.evaluate(JS, {"short": SHORT_WORDS.get(code, []), "wrap": WRAP})
                        where = {"url": lang + path, "w": w, "theme": theme}
                        if r["overflow"]:
                            found.append(dict(where, kind="overflow", what="%dpx wider than the screen" % r["overflow"]))
                        for k in ("target", "wrap", "hanging"):
                            found += [dict(where, kind=k, what=x) for x in r[k]]
                ctx.close()
        br.close()
    srv.shutdown()
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(found, f, ensure_ascii=False, indent=1)
    # one line per distinct problem, with how many renders show it and one example
    groups = {}
    for f in found:
        groups.setdefault((f["kind"], f["what"]), []).append(f)
    for (kind, what), fs in sorted(groups.items()):
        ex = fs[0]
        print("%-8s %s  [%d×, e.g. %s @%d %s]" % (kind, what, len(fs), ex["url"], ex["w"], ex["theme"]))
    print("layout: %d renders (%d languages × %d pages × %d widths × %d themes), %d problems"
          % (renders, len(langs), len(paths), len(WIDTHS), len(THEMES), len(found)))
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
