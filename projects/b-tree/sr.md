---
title: "b-tree: key-value skladište na B-stablu u C-u"
summary: "Key-value skladište na disku, napisano od nule u C-u: B-stablo nad stranicama fiksne veličine, ključevi i vrednosti proizvoljne dužine, LRU keš stranica i žurnal."
kind: Mehanizam za skladištenje · C
---

Mala ugrađena baza podataka, napisana 2015. za kurs sistemskog programiranja u Tehnosferi (Mail.Ru Group i MGU „M. V. Lomonosov“). Zadatak je bio da se od nule napravi sloj za skladištenje kakav prave baze podataka imaju ispod haube: key-value skladište sa interfejsom nalik na `dbopen` (`put`, `get`, `delete`, `sync`, `close`), koje svoje podatke drži u jednom fajlu.

## Kako radi

- **B-stablo nad stranicama.** Fajl je podeljen na stranice fiksne veličine (podrazumevano 4 KB); svaki čvor stabla je jedna stranica. Ključevi i vrednosti mogu biti proizvoljne dužine.
- **Mapa slobodnog prostora.** Servisne stranice čuvaju bitmapu slobodnih stranica, pa se obrisane stranice ponovo koriste.
- **LRU keš.** Nedavno korišćene stranice ostaju u memoriji (podrazumevano 16 MB); izmenjene („prljave“) stranice se zapisuju nazad pri izbacivanju iz keša.
- **Žurnal.** Izmene se prvo upisuju u log, pa se baza može oporaviti posle pada.
- **Konfiguracija.** Veličina fajla, veličina stranice i veličina keša zadaju se pri kreiranju baze.

## Zašto je to važno

Projekat dotiče ključna pitanja svakog mehanizma za skladištenje: raspored podataka na stranicama, deljenje i spajanje čvorova, keširanje i trajnost. To je direktan put od udžbeničkog B-stabla do toga kako su napravljeni SQLite ili InnoDB.
