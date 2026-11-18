#!/usr/bin/env python3
"""Weekly analytics report from the GoatCounter API, as Markdown (in Russian, for the author).

    GOATCOUNTER_API_TOKEN=... python tools/weekly_report.py [--site favorart] [--end 2026-11-16] > report.md

The week is the last full Monday-Sunday (UTC) before --end (default: today), compared with the week before.
The token is a GoatCounter API key with read access to statistics; keep it in the GitHub secret
GOATCOUNTER_API_TOKEN, never in the repo. Used by .github/workflows/weekly-report.yml.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request

READ_EVENTS = ("read-50", "read-90", "time-1m", "time-3m")


def fail(msg):
    sys.exit("weekly_report: " + msg)


class API:
    def __init__(self, site, token):
        self.base = "https://%s.goatcounter.com/api/v0/" % site
        self.token = token

    def get(self, path, **params):
        url = self.base + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + self.token,
                                                   "Content-Type": "application/json"})
        for attempt in range(5):
            time.sleep(0.3)  # the API allows 4 requests per second
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 4:
                    time.sleep(2)
                    continue
                fail("%s -> HTTP %d: %s" % (path, e.code, e.read()[:300].decode("utf-8", "replace")))


def week(end):
    """[start, end) of the last full Monday-Sunday week before the day `end`."""
    monday = end - dt.timedelta(days=end.weekday())
    return monday - dt.timedelta(days=7), monday


def rng(start, end):
    return {"start": start.strftime("%Y-%m-%dT00:00:00Z"), "end": end.strftime("%Y-%m-%dT00:00:00Z")}


def hits(api, r):
    out, exclude = [], []
    while True:
        params = dict(r, limit=100)
        if exclude:
            params["exclude_paths"] = ",".join(exclude)
        d = api.get("stats/hits", **params)
        out += d.get("hits") or []
        if not d.get("more"):
            return out
        exclude = [str(h["path_id"]) for h in out]


def stats(api, page, r, limit=10):
    return api.get("stats/" + page, limit=limit, **r).get("stats") or []


def delta(now, before):
    if not before:
        return "новое" if now else ""
    d = now - before
    return "%+d" % d if d else "="


def table(head, rows):
    if not rows:
        return "_нет данных_\n"
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=os.environ.get("GOATCOUNTER_CODE", "favorart"))
    ap.add_argument("--end", help="YYYY-MM-DD, default today (UTC)")
    a = ap.parse_args()
    token = os.environ.get("GOATCOUNTER_API_TOKEN", "")
    if not token:
        fail("GOATCOUNTER_API_TOKEN is not set")
    api = API(a.site, token)
    today = dt.date.fromisoformat(a.end) if a.end else dt.datetime.now(dt.timezone.utc).date()
    start, end = week(today)
    cur, prev = rng(start, end), rng(start - dt.timedelta(days=7), start)

    tot, tot_prev = api.get("stats/total", **cur), api.get("stats/total", **prev)
    h, h_prev = hits(api, cur), hits(api, prev)
    prev_count = {(x["path"], x["event"]): x["count"] for x in h_prev}
    pages = [x for x in h if not x["event"]]
    events = [x for x in h if x["event"]]

    def ev(prefix):
        return [x for x in events if x["path"].startswith(prefix)]

    last_day = end - dt.timedelta(days=1)
    md = ["Неделя **%s – %s** (UTC), сравнение с предыдущей. Дашборд: https://%s.goatcounter.com\n"
          % (start.strftime("%d.%m"), last_day.strftime("%d.%m.%Y"), a.site)]

    visitors = tot.get("total", 0) - tot.get("total_events", 0)
    visitors_prev = tot_prev.get("total", 0) - tot_prev.get("total_events", 0)
    contact = sum(x["count"] for x in ev("click/contact"))
    sent = sum(x["count"] for x in ev("form/contact-sent"))
    md.append("## Коротко\n")
    md.append(table(["Что", "Неделя", "Было"], [
        ["Посетители (визиты страниц)", visitors, visitors_prev],
        ["Клики «Связаться»", contact, sum(c for (p, e), c in prev_count.items() if e and p.startswith("click/contact"))],
        ["**Отправлено через форму**", sent, sum(c for (p, e), c in prev_count.items() if e and p.startswith("form/contact-sent"))],
        ["Переходы наружу (LinkedIn, GitHub…)", sum(x["count"] for x in ev("out/")),
         sum(c for (p, e), c in prev_count.items() if e and p.startswith("out/"))],
    ]))

    md.append("\n## Страницы\n")
    md.append(table(["Страница", "Визиты", "Δ"],
                    [[x["path"], x["count"], delta(x["count"], prev_count.get((x["path"], False), 0))]
                     for x in sorted(pages, key=lambda x: -x["count"])[:15]]))

    # reading: one row per page, columns = read events
    reading = {}
    for x in events:
        for name in READ_EVENTS:
            if x["path"].startswith(name + "/"):
                reading.setdefault("/" + x["path"][len(name) + 1:], {})[name] = x["count"]
    visits = {x["path"]: x["count"] for x in pages}
    md.append("\n## Дочитывание\n")
    md.append("Сколько визитов прокрутили страницу до половины / почти до конца и сколько пробыли на ней ≥ 1 и ≥ 3 минут "
              "(вкладка видна). Страницы на один экран не учитываются.\n\n")
    md.append(table(["Страница", "Визиты", "50%", "90%", "≥1 мин", "≥3 мин"],
                    [[p, visits.get(p, ""), *[r.get(n, "") for n in READ_EVENTS]]
                     for p, r in sorted(reading.items(), key=lambda kv: -sum(kv[1].values()))[:15]]))

    md.append("\n## Клики\n")
    clicks = [x for x in events if not any(x["path"].startswith(n + "/") for n in READ_EVENTS)]
    md.append(table(["Событие", "Раз", "Δ", "Последний текст ссылки / страница"],
                    [[x["path"], x["count"], delta(x["count"], prev_count.get((x["path"], True), 0)), x.get("title", "")]
                     for x in sorted(clicks, key=lambda x: -x["count"])[:20]]))

    for title, page, head in (("Страны и регионы", "locations", "Где"),
                              ("Источники", "toprefs", "Откуда"),
                              ("Кампании (utm_campaign)", "campaigns", "Кампания"),
                              ("Языки браузера", "languages", "Язык"),
                              ("Экраны", "sizes", "Размер")):
        s, s_prev = stats(api, page, cur), stats(api, page, prev, limit=100)
        before = {x["name"]: x["count"] for x in s_prev}
        md.append("\n## %s\n" % title)
        md.append(table([head, "Визиты", "Δ"], [[x["name"] or "(нет данных)", x["count"],
                                                  delta(x["count"], before.get(x["name"], 0))] for x in s]))

    md.append("\n_Источник «(нет данных)» — переходы без реферера (приложение LinkedIn, lnkd.in). Ставь в постах "
              "ссылки с `?ref=linkedin&utm_campaign=<пост>`._\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
