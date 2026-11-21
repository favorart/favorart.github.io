---
tagline: "Alokator koji se sam defragmentuje i prati premeštene blokove"
summary: "Alokator u C++17 bez dodatne memorije: defrag() sabija podatke brzinom od 6,4 GB/s, a Pointer prati premeštene blokove. Izmerena cena: alloc() je oko 140 puta sporiji od malloc-a."
kind: "Alokator memorije · C++"
---

Kursni projekat iz 2015. (Tehnosfera, Mail.Ru Group i MGU „M. V. Lomonosov“): alokator nad jednim fiksnim baferom koji sopstvenu evidenciju drži u tom istom baferu — podaci rastu od početka, deskriptori blokova od kraja. Pošto `defrag()` pomera blokove, korisnik drži `Pointer` koji svoj blok ponovo pronalazi po jedinstvenom indeksu. Godine 2026. sanitizeri i pregled koda pronašli su u njemu 13 grešaka, od upisa van bafera do pokazivača koji je pronalazio tuđi blok; svaka ispravka ima regresioni test.

## Kako radi

- **Bez dodatne memorije.** Deskriptori čine dvostruko povezanu listu sortiranu po adresama, zbijenu na kraju bafera bez praznina. Alokacija traži prvi odgovarajući prostor (first fit) i prolazi kroz listu, O(broj blokova); oslobađanje ima složenost O(1).
- **Defragmentacija.** `defrag()` u jednom prolazu primiče žive blokove jedan uz drugi, tako da slobodan prostor ponovo postane jedna oblast; `realloc()` povećava ili smanjuje blok na mestu kad ima prostora.
- **Pametni pokazivač.** `Pointer` pamti mesto deskriptora i indeks bloka i ponovo pronalazi blok kada se pomeri; pokazivač na oslobođeni blok vraća `nullptr`.
- **Samoprovere.** `check()` proverava svaku invarijantu arene, `dump()` ispisuje njenu mapu.

## Izmerena cena

Benčmark u README-u to pošteno pokazuje: alokacija traje 4,6 µs naspram 33 ns za `malloc`, jer prolazi kroz listu; sabijanje radi brzinom od 6,4 GB/s živih podataka, a dereferenciranje `Pointer`-a sa keširanim mestom deskriptora košta 2,3 ns.

## Inženjerska strana

- GoogleTest testovi nad celim javnim API-jem, nasumični stres-test koji svaki živi blok poredi sa modelom bajt po bajt i cilj za libFuzzer; stres-testovi i fuzzer pozivaju `check()` posle svake operacije.
- CI gradi projekat GCC-om i Clang-om na Linux-u (i pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om), MSVC-om na Windows-u i Apple Clang-om na macOS-u, upozorenja se tretiraju kao greške; svaki zeleni push na `master` dobija oznaku verzije i GitHub Release.
