---
title: "Every calendar date hides in three billion digits of π"
summary: "A site where you can find your birthday among three billion digits of π, and a detective story about the technical puzzles I ran into along the way."
source: posts/2026-11-pi-every-date/index.md
source_lang: ru
source_hash: 94cc7054
translated: 2026-11-19
translator: Claude
reviewed: 2026-11-19
---
I computed three billion digits of π, and every single calendar date is hiding in there.

At which digit does your birthday begin? You can find out [on the site](https://favorart.github.io/pi-birthday/).

π most likely contains every finite sequence of digits. So far this is only a mathematical conjecture.

But how can you get a hands-on feel for it? I put the site online so that anyone can try. While building it, I ran into a lot of technical problems. I found them so intriguing that I wrote a whole detective story about them.

A sequence of 8 digits, DDMMYYYY, turns up on average once every 100 million digits. How many digits do you need for each of the 3.65 million calendar dates to show up? Why was converting a big number to a string in CPython declared a vulnerability? How did numpy get through 1.7 billion digits in a minute and a half? When was Jesus born, and why did we need a year zero?

[Full article](/writing/pi-stores-everything/)

Which date would you check on the site first?

\#Python #Math #Algorithms #numpy #Pi

![Image from the post](cover.jpg)
