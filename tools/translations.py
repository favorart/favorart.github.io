#!/usr/bin/env python3
"""Versioned translation cache for articles and posts (see "Translations" in README.md).

    python tools/translations.py status [--offline]      what is up to date / outdated / missing / unreviewed
    python tools/translations.py source <slug>           print the original (Markdown) and its version hash
    python tools/translations.py new <slug> <lang>       create translations/<section>/<slug>/<lang>.<hash>.md
    python tools/translations.py prune                   delete versions superseded by a reviewed current one

A translation file is valid for one version of the original: its name and `source_hash` carry
build.source_hash() of the original text it was made from. When the original changes, the build keeps showing
the newest reviewed version with an "original updated" note until a translation of the new version is added.
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def items(offline=False):
    langs = build.load_languages()
    build.LANGS.update(langs)
    all_items = build.load_posts() + build.load_external(offline)
    return [i for i in all_items if build.translatable(i)], langs


def find(slug, offline=False):
    its, langs = items(offline)
    for i in its:
        if i["slug"] == slug:
            return i, langs
    build.fail("no translatable item with slug '%s' (posts and articles in Writing)" % slug)


def state(item, lang):
    cur = build.source_hash(item["source_md"])
    files = build.translation_files(item, lang)
    reviewed = [f for f in files if build.read_translation(f)[0].get("reviewed")]
    if any(f.endswith(".%s.md" % cur) for f in reviewed):
        return "ok"
    if any(f.endswith(".%s.md" % cur) for f in files):
        return "unreviewed"
    if reviewed:
        return "outdated"
    return "missing"


def cmd_status(args):
    its, langs = items(args.offline)
    codes = list(langs)
    print("%-36s %-4s %s" % ("item", "orig", "  ".join("%-10s" % c for c in codes)))
    totals = {}
    for i in its:
        cells = []
        for c in codes:
            st = "original" if c == i["lang"] else state(i, c)
            totals[st] = totals.get(st, 0) + 1
            cells.append("%-10s" % st)
        print("%-36s %-4s %s" % ((i["section"] + "/" + i["slug"])[:36], i["lang"], "  ".join(cells)))
    print("\n" + ", ".join("%s: %d" % kv for kv in sorted(totals.items())))


def cmd_source(args):
    i, _ = find(args.slug, args.offline)
    print("section: %s\nslug: %s\nsource: %s\nsource_lang: %s\nsource_hash: %s\ntitle: %s\nsummary: %s\n---" % (
        i["section"], i["slug"], i["source_ref"], i["lang"], build.source_hash(i["source_md"]),
        build.loc(i["title"], build.LANGS[build.DEFAULT_LANG]) if isinstance(i["title"], dict) else i["title"],
        build.loc(i["summary"], build.LANGS[build.DEFAULT_LANG]) if isinstance(i["summary"], dict) else i["summary"]))
    print(i["source_md"])


def cmd_new(args):
    i, langs = find(args.slug, args.offline)
    if args.lang not in langs:
        build.fail("unknown language '%s' (have: %s)" % (args.lang, ", ".join(langs)))
    if args.lang == i["lang"]:
        build.fail("'%s' is already in %s" % (args.slug, args.lang))
    h = build.source_hash(i["source_md"])
    d = os.path.join(build.ROOT, "translations", i["section"], i["slug"])
    path = os.path.join(d, "%s.%s.md" % (args.lang, h))
    if os.path.exists(path):
        build.fail("%s already exists" % os.path.relpath(path, build.ROOT))
    os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("---\n"
                "title: \"\"\n"
                "summary: \"\"\n"
                "source: %s\n"
                "source_lang: %s\n"
                "source_hash: %s\n"
                "translated: %s\n"
                "translator: Claude\n"
                "reviewed:            # date of the independent review; the build ignores the file until it is set\n"
                "---\n\n" % (i["source_ref"], i["lang"], h, dt.date.today().isoformat()))
    print(os.path.relpath(path, build.ROOT))


def cmd_prune(args):
    its, langs = items(args.offline)
    removed = 0
    for i in its:
        cur = build.source_hash(i["source_md"])
        for c in langs:
            files = build.translation_files(i, c)
            current_ok = [f for f in files if f.endswith(".%s.md" % cur) and build.read_translation(f)[0].get("reviewed")]
            if not current_ok:
                continue
            for f in files:
                if f not in current_ok:
                    os.remove(f)
                    removed += 1
                    print("removed", os.path.relpath(f, build.ROOT))
    print("%d superseded version(s) removed (they stay in git history)" % removed)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip external articles (no network)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    p = sub.add_parser("source"); p.add_argument("slug")
    p = sub.add_parser("new"); p.add_argument("slug"); p.add_argument("lang")
    sub.add_parser("prune")
    args = ap.parse_args()
    {"status": cmd_status, "source": cmd_source, "new": cmd_new, "prune": cmd_prune}[args.cmd](args)


if __name__ == "__main__":
    main()
