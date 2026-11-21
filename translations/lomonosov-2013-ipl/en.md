---
title: "An Interpreted Programming Language with Customizable Syntax"
summary: "Talk abstract: an interpreted language with modifiable syntax whose code reads like a mathematical text in the programmer's language."
source: sources.yml papers/lomonosov-2013-ipl
source_lang: ru
source_hash: 611586e2
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---

We describe an interpreted programming language with modifiable syntax and an interpreter for it. The main feature of the language is that its source code comes as close as possible to formal (for example, mathematical) text in the programmer's language. To this end, we developed a lexical analyzer that is not limited to single-word names and operators, a parser with flexible configuration of syntax and semantics, a user-replaceable set of keywords (up to translating them into another language), code precompilation, and rethought enumerated types. Such a language makes programs easier to learn and maintain and facilitates mutual understanding between the programmer and the customer, who can read the code themselves and make sure the program does what it is supposed to do.
