---
tagline: "Key-value skladište u C-u: B-stablo na disku i žurnal"
summary: "Key-value skladište u jednom fajlu, u čistom C-u: stranice B-stabla, LRU keš i žurnal sa kontrolnim sumama. Oporavak posle pada testira se ubijanjem procesa-deteta; najgori scenariji su izmereni."
kind: "Mehanizam za skladištenje · C"
---

Ugrađeno key-value skladište koje sam napisao 2015. u Tehnosferi (Mail.Ru Group i MGU „M. V. Lomonosov“) iza zadatog C API-ja, a završio 2026. Svaka stranica fajla je čvor B-stabla. Keš zapisuje sve izmenjene („prljave“) stranice odjednom, pa fajl uvek sadrži konzistentno stablo, a ponovna primena žurnala posle pada procesa vraća svaku potvrđenu izmenu. Zato što se puna stranica deli u tački umetanja, stranice su pri sekvencijalnom umetanju popunjene 68%.

## Kako radi

- **B-stablo nad stranicama.** Stranice fiksne veličine (podrazumevano 4 KB); ključevi i vrednosti promenljive dužine čuvaju se direktno u čvorovima, do 1/8 stranice po zapisu. Pune stranice se dele unapred, pri silasku, u jednom prolazu; pri brisanju se nedovoljno popunjene stranice spajaju sa susednom ili od nje pozajmljuju zapise.
- **Mapa slobodnog prostora.** Servisne stranice čuvaju bitmapu slobodnih stranica, pa se obrisane stranice ponovo koriste.
- **LRU keš.** Nedavno korišćene stranice ostaju u memoriji (podrazumevano 16 MB); izbacivanje prljave stranice zapisuje sve prljave stranice i poziva `fsync`.
- **Žurnal.** Svaka izmena se prvo upisuje u žurnal čiji zapisi imaju kontrolne sume; pri otvaranju se ponovo primenjuju zapisi posle poslednje kontrolne tačke, a zapis prekinut padom se zanemaruje.
- **Dijagnostika.** `db_check` proverava stablo, `db_stats` prikazuje njegov oblik i popunjenost, `db_trace` beleži operacije na četiri nivoa.

## Inženjerska strana

- Čist C99 i POSIX, bez zavisnosti, gradi se Make-om.
- Testovi na cmocka-i: jedinični testovi modula, nasumične operacije proverene prema referentnom modelu, oporavak posle pada u procesu-detetu i najgori scenariji opterećenja; svi se pokreću i pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om.
- Benčmark u README-u: kada stablo stane u keš, oko 186 hiljada nasumičnih umetanja i 594 hiljade pretraga u sekundi.
- CI na Linux-u (gcc i clang, običan build i sa sanitizerima) i macOS-u; svaki push na `master` koji prođe CI dobija oznaku verzije i GitHub Release.

## Ograničenja

Žurnal štiti od pada procesa, ali ne i od nestanka struje; bazu u jednom trenutku koristi samo jedan proces; ovo je B-stablo, a ne B+-stablo.
