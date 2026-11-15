---
title: "allocator: alokator memorije sa defragmentacijom"
summary: "Alokator memorije u C++17 nad fiksnom arenom koji ume sam sebe da defragmentuje, uparen sa pametnim pokazivačem koji ostaje ispravan kada se blokovi pomeraju."
kind: Alokator memorije · C++
---

Kursni projekat iz 2015. (Tehnosfera, Mail.Ru Group i MGU „M. V. Lomonosov“): alokator memorije koji sam upravlja jednom fiksnom arenom umesto da poziva sistemski `malloc`. Godine 2026. kod je prošao reviziju: greške su ispravljene, a projekat je dobio prave testove, CI i izdanja.

## Kako radi

- **Bez dodatne memorije.** Alokator izdaje blokove iz unapred alociranog bafera, a njegova sopstvena evidencija — dvostruko povezana lista deskriptora blokova, sortirana po adresama — živi u istom baferu, zbijena od njegovog kraja bez praznina. Alokacija prolazi kroz listu do prvog odgovarajućeg prostora, O(broj blokova); oslobađanje ima složenost O(1).
- **Defragmentacija.** Posle mnogo alokacija i oslobađanja slobodan prostor se raspadne na sitne komade. `defrag()` u jednom prolazu primiče žive blokove jedan uz drugi, tako da slobodan prostor ponovo postane jedna neprekidna oblast; `realloc()` povećava ili smanjuje blok na mestu kad ima prostora.
- **Pametni pokazivač.** Pomeranje blokova bi pokvarilo obične pokazivače, pa korisnik radi preko klase `Pointer`. Ona pamti mesto deskriptora i jedinstveni indeks bloka i ponovo pronalazi blok kada se pomeri; pokazivač na oslobođeni blok vraća `nullptr`.

## Inženjerska strana

- Revizija iz 2026. pokrenula je stare testove pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om i pronašla deset grešaka — od upisa van bafera do pokazivača koji je pronalazio tuđi blok; svaka ispravka ima regresioni test.
- GoogleTest testovi pokrivaju ceo javni API, a nasumični stres-test poredi svaki živi blok sa modelom bajt po bajt.
- CI gradi projekat GCC-om i Clang-om na Linux-u (i pod sanitizerima), MSVC-om na Windows-u i Apple Clang-om na macOS-u; upozorenja se tretiraju kao greške.
- README sadrži benčmark u poređenju sa `malloc`/`free` koji pošteno pokazuje cenu: alokacija prolazi kroz listu i mnogo je sporija od `malloc`-a, dok je sabijanje jedan prolaz `memmove`-a.
- Svaki push na `master` koji prođe CI dobija oznaku verzije i GitHub Release sa fajlom zaglavlja i statičkom bibliotekom za Linux, Windows i macOS.

## Zašto je to važno

Sopstveni alokatori su jedan od glavnih alata za rad na performansama u C++-u: manje sistemskih poziva, bolja lokalnost podataka i predvidljiva potrošnja memorije. Ovaj projekat pokazuje mehaniku koja stoji iza toga — i cenu pomeranja objekata u memoriji.
