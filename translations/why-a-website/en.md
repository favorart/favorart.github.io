---
title: "Why do you need a website?"
summary: "My wife asked why I needed a website. In two evenings with Claude I built one and found the answer: a hundred small \"no\"s and a tidy-up in my head."
source: posts/2026-11-why-a-website/index.md
source_lang: ru
source_hash: 79974efc
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---

— my wife asked mockingly.

I had no answer. I had a CV in a YAML file, a LinkedIn profile and a vague wish for something beautiful, not something slapped together. Two evenings later the site was done, and so was the answer.

## I didn't know what I wanted

I came to Claude without a spec. All I had was a rough idea of the site: warm and modern, with a sunny accent.

Claude asked questions and then offered options: three site mockups, each with a paragraph of description. In one I liked the layout and navigation, in another the style, in the third the animation. I picked a pastel background and rounded corners, a soft sunny mood, a menu on every page and a noticeable image zoom on mouse hover.

![One of the three mockups: a pastel background and the sun in the center](img/cmp-a-full.png)

The sun in the center stayed for a reason. Twenty-six centuries ago the Persian king Kurush built the largest empire the world had yet seen. The Greeks called him Kyros, Cyrus, and to their ears it sounded almost like their word "kyrios", lord. It suited a king. Then, six hundred-odd years later, Plutarch wrote that Cyrus was named after the sun, since that's what the Persians call the sun. Linguists don't believe Plutarch. But I like him: the king and I almost share a name. So at the center of the site, the one shining is me.

## What does glass look like?

At first Claude offered me what it usually offers: strict minimalism, a dark engineering terminal style and a magazine layout with big headlines. But I wanted a site that doesn't give away my AI slop. I looked deep inside myself and pronounced: glass, modern surfaces, translucent and frosted, with a glint.

Then we struggled with effects and backgrounds for a long time. The sun either blinded you and overpowered everything around it, or vanished altogether.

![The sun: four attempts](img/anim/10-sun.en.gif)

The mouse response didn't come together right away either. I wanted that exact zoom into the image from the third mockup.

![1. Rejected: the card lifts](img/anim/01-lift.en.gif)

![2. Accepted: the image zooms inside a still card](img/anim/02-zoom.en.gif)

We chose the zoom, but I couldn't see it, and twice I complained that I simply wasn't getting any zoom. Twice Claude checked the styles, and everything was in place. It turned out I had animation effects turned off in Windows. The browser honestly passed on the request to do without motion, and the site honestly didn't move. My own Windows was forbidding me to see what I had ordered. Now, for people like me, there's a quiet version where the image zooms just a little and quickly.

![The quiet version: just a little and quickly](img/anim/02b-quiet.en.gif)

The glass itself was the hardest to get right.

![3. Rejected: the glass slides away](img/anim/03-slide.en.gif)

![4. A step: the glass fades out entirely](img/anim/04-fade.en.gif)

![5. Rejected: the diagonal sweeps across](img/anim/05-sweep.en.gif)

![6. A step: the diagonal as a fade](img/anim/06-diagfade.en.gif)

Where the diagonal runs and how blurred it is can't be explained in words. So Claude built a separate test-bench page where nine variants move at once. They cover 30, 20 or 10 percent of the image, and their edge is sharp, medium or wide. You look and jab a finger at the one you want.

I chose. And then I realized that all along I had wanted the opposite.

![7. Almost: a transparent corner, but the wrong one](img/anim/07-peekTL.en.gif)

![8. Accepted: the bottom-right corner, and on hover the glass fades out entirely](img/anim/08-peekBR.en.gif)

## From links to buttons

How to highlight links was also settled only on the third try.

![Links: underline, marker, reveal](img/anim/09-links.en.gif)

The tab icon is the whole site in a tiny square, with that same sun. Now the sun greets us in the background, on the tab and in the page logo.

![The site icon: from an orange square to the sun behind the letters](img/favicon-evolution.svg)

The button under a section on the home page used to say just "All writing" and hid, small, in a corner. It wasn't clear that a lot more was hiding behind it. Now it brightly invites you in and reads "All 12 articles", matching the actual count.

Under every article there are two identical buttons, but only "Send feedback" is bright. It calls out to whoever has read to the end and has almost made up their mind to write. They'll find the way back to the list on their own.

## What's under the hood? I'm curious myself!

Articles from my repositories aren't copied to the site. I fix a README in a repository, and the page fixes itself. There's no second version, so there's nothing to drift apart.

![How the site is built](img/build-scheme.en.png)

The site speaks English, Spanish, Russian, Serbian and Uzbek. Anyone who has read my CV will recognize a map in that set.

## Head of Slop Review

Under my name on the home page, joke roles take turns. One I honestly stole from a colleague: head of the AI slop review department. It describes my job most accurately of all.

Claude came up with the footer line on every page by itself: the site was made by Claude while the human picked pastel colors. I crossed one word out of it, and that is probably my biggest contribution to the site's copy.

A hundred small "no"s — and I got a site I'm happy with. Each one clarified something not so much in the site as in me. I found out what I wanted by rejecting things.

Small things like the shade of the sun or the transparency of the panels I saw just by refreshing the page: a new version deploys itself in a minute or two. For big decisions Claude built test benches where all the variants are visible at once. That's what amazes me most. A feeling turns into a variant, a variant into a decision, and there that decision is, already working on the site.

## So why do I need a website?

While I was building it, I realized how much I have to say.

Articles that had been lying around in different repositories for years. Posts that lived on LinkedIn behind a login wall. "Read later" bookmarks, "should write this up" links, half-finished thoughts. The site made me put all of it in its place. Some of it went onto a page. Some of it I finally threw away. Questions that had been open for ages got closed.

The site turned out to be not a shop window, but a tidy-up in my head.

I'm so inspired! Я очень вдохновлён, ¡estoy emocionado! I'm like a kid with a new toy. If I'd had one like this as a child, I would never, ever have left the house!
