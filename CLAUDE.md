# Notes for Claude

- How the site is built and how to add content: see `README.md`. When copying a LinkedIn post, follow
  "Rules for copying a post" there — in particular, bring in the continuation from the author's comments.
- The site is in 5 languages (`i18n/<lang>.yml`, `content/home.<lang>.html`, `content/cv.<lang>.html`).
  Any new UI string or CV/home change must be made in all of them; translations get an independent review.
- Never put a personal email address into the repo or commits; commit as
  `9784285+favorart@users.noreply.github.com`.
- A push to `main` deploys the live site.
