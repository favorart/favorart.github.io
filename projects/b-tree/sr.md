---
title: "b-tree: key-value skladište na B-stablu u C-u"
summary: "Key-value skladište na disku, napisano od nule u C-u: B-stablo nad stranicama fiksne veličine, ključevi i vrednosti promenljive dužine, LRU keš stranica i žurnal sa unapred upisanim izmenama (write-ahead) za oporavak posle pada."
kind: Mehanizam za skladištenje · C
---

Mala ugrađena baza podataka, napisana 2015. kao kursni projekat u Tehnosferi (Mail.Ru Group i MGU „M. V. Lomonosov“). Zadatak je bio da se od nule napravi sloj za skladištenje kakav prave baze podataka imaju ispod haube: key-value skladište iza zadatog C API-ja (`dbcreate`, `dbopen`, umetanje, pretraga, brisanje, upis na disk, zatvaranje), koje svoje podatke drži u jednom fajlu. Godine 2026. projekat je vraćen u život: nedovršeni brisanje i oporavak iz žurnala su završeni, a sve je pokriveno testovima.

## Kako radi

- **B-stablo nad stranicama.** Fajl je podeljen na stranice fiksne veličine (podrazumevano 4 KB); svaki čvor stabla je jedna stranica. Ključevi i vrednosti promenljive dužine čuvaju se direktno u čvorovima, do 1/8 stranice po zapisu.
- **Deljenje i balansiranje.** Pune stranice se dele unapred, pri silasku, u jednom prolazu; pri sekvencijalnom umetanju stranica se deli u tački umetanja, pa stranice ostaju dobro popunjene. Pri brisanju se nedovoljno popunjena stranica spaja sa susednom ili od nje pozajmljuje zapise.
- **Mapa slobodnog prostora.** Servisne stranice čuvaju bitmapu slobodnih stranica, pa se obrisane stranice ponovo koriste.
- **LRU keš.** Nedavno korišćene stranice ostaju u memoriji (podrazumevano 16 MB); izmenjene („prljave“) stranice se zapisuju nazad pri izbacivanju iz keša — sve odjednom, pa fajl uvek sadrži konzistentno stablo.
- **Žurnal.** Svaka izmena se prvo upisuje u žurnal unapred (write-ahead), a svaki zapis ima kontrolnu sumu; pri otvaranju se ponovo primenjuju zapisi posle poslednje kontrolne tačke, a zapis prekinut padom se odbacuje.
- **Konfiguracija.** Veličina fajla, veličina stranice i veličina keša zadaju se pri kreiranju baze.

## Inženjerska strana

- Čist C99 i POSIX, bez zavisnosti, gradi se Make-om; Windows nije podržan.
- Testovi na cmocka-i: jedinični testovi modula, nasumične operacije proverene prema referentnom modelu, oporavak posle pada u procesu-detetu i najgori scenariji opterećenja; pokreću se i pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om.
- CI na Linux-u (gcc i clang, običan build i sa sanitizerima) i macOS-u; benčmark se pokreće na svaki push na `master`.
- Svaki push na `master` koji prođe CI dobija oznaku verzije i GitHub Release sa bibliotekom za Linux i macOS.

## Zašto je to važno

Projekat dotiče ključna pitanja svakog mehanizma za skladištenje: raspored podataka na stranicama, deljenje i spajanje čvorova, keširanje i trajnost. To je direktan put od udžbeničkog B-stabla do toga kako su napravljeni SQLite ili InnoDB.
