# Notes for Claude

- How the site is built and how to add content: see `README.md`. When copying a LinkedIn post, follow
  "Rules for copying a post" there — in particular, bring in the continuation from the author's comments.
- The site is in 5 languages (`i18n/<lang>.yml`, `content/home.<lang>.html`, `content/cv.<lang>.html`).
  Any new UI string or CV/home change must be made in all of them; translations get an independent review.
- Terms already decided (content types, job titles, names): `docs/translation-glossary.md`. Use them; add new
  decisions there.
- Never put a personal email address into the repo or commits; commit as
  `9784285+favorart@users.noreply.github.com`.
- A push to `main` deploys the live site.
- Projects (`projects/<slug>/<lang>.md`) are written per language, not translated at build time: a change to
  `en.md` is made in every language file in the same commit, with an independent review (README → Add a project).

## Links and images (details: README → Links)

- A link leads to the reader's language if that page exists, then to this site, then to English; in translations
  link `/<lang>/writing/<slug>/` for pages of this site. Language badges only on standalone links (lists, tables,
  own line), never inside running text or on links named after their language.
- Images in translations come from the English version; text on an image in another language → make an English
  copy in the source repo.
- Before a release of link-heavy changes run `python tools/check_link_langs.py _site --wiki` and
  `python tools/check_web_links.py _site`; a dead link → new address or Wayback copy, in the original and in
  every translation.
- Pushing to an external source repo (pi-birthday, IPL, robot-hand…) only after showing the author the edits.

## Every commit that adds or changes a post or an article

Articles, posts and paper abstracts (Writing) are translated into every site language other than their own;
one file per text and language, `translations/<slug>/<lang>.md`, updated in place — its `source_hash` says
which version of the original it matches (see README → Translations). Never keep several versions of a file:
history is git's job. Before committing such a change:

1. Run `python tools/translations.py status`. It lists every post/article × language as `ok`, `missing`,
   `outdated` (the original changed since the translation) or `unreviewed`. Check **all** items, not only the
   one being added — an edit to an external repo can make an older translation outdated.
2. For every `missing` / `outdated` / `unreviewed` cell:
   - `python tools/translations.py source <slug>` prints the original and its hash;
   - `python tools/translations.py new <slug> <lang>` creates the file (fill in `title`, `summary` and the
     translated Markdown body), or for an outdated one re-stamps it in place for the current original —
     then edit its text to match the changes (keep what is still right, don't retranslate from scratch).
   - Translate per `docs/translation-glossary.md`, one agent per language, native-level, keeping Markdown,
     links, images and code untouched.
3. Independent review: a separate agent that did not translate compares each new file with the original
   (accuracy, omissions, grammar, glossary terms, typography, Markdown intact), fixes clear errors and only then
   sets `reviewed: <date>`. Unreviewed files are never published.
4. `python build.py` (must print `0 outdated, 0 missing` unless the author agreed otherwise) and
   `python tools/check_links.py _site`.
5. Commit the original change and its translations **in the same commit**.

Papers: one abstract per page, in the page's language. The file body is the abstract, plus `keywords` in front
matter; the English abstract comes from
the journal (`abstract_en` in sources.yml) and is not translated. Courses are not translated (lectures are in
Russian). CV/home are translated by hand in `content/`.

Covers with text (SVG made by `tools/make_covers.py`) exist per language: `cover-N.<lang>.svg` next to
`cover-N.svg` (`--lang xx --author "Name"`); the build picks the one for the page's language.
