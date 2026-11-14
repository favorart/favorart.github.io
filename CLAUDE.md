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

## Every commit that adds or changes a post or an article

Articles and posts (Writing) are translated into every site language other than their own; translations are a
cache keyed by the version of the original (`translations/<section>/<slug>/<lang>.<hash>.md`, see README →
Translations). Before committing such a change:

1. Run `python tools/translations.py status`. It lists every post/article × language as `ok`, `missing`,
   `outdated` (the original changed since the translation) or `unreviewed`. Check **all** items, not only the
   one being added — an edit to an external repo can make an older translation outdated.
2. For every `missing` / `outdated` / `unreviewed` cell:
   - `python tools/translations.py source <slug>` prints the original and its hash;
   - `python tools/translations.py new <slug> <lang>` creates the file for the current version; fill in `title`,
     `summary` and the translated Markdown body. For an outdated one, update the previous version's text
     rather than translating from scratch (keep what is still right).
   - Translate per `docs/translation-glossary.md`, one agent per language, native-level, keeping Markdown,
     links, images and code untouched.
3. Independent review: a separate agent that did not translate compares each new file with the original
   (accuracy, omissions, grammar, glossary terms, typography, Markdown intact), fixes clear errors and only then
   sets `reviewed: <date>`. Unreviewed files are never published.
4. `python build.py` (must print `0 outdated, 0 missing` unless the author agreed otherwise) and
   `python tools/check_links.py _site`.
5. Commit the original change and its translations **in the same commit**. Old versions may be removed with
   `python tools/translations.py prune` (git keeps them).

Courses, papers (abstracts only) and the CV/home pages are not part of this cache: courses are not translated,
papers carry their own RU/EN abstracts, CV/home are translated by hand in `content/`.
