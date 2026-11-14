---
title: "allocator: alokator memorije sa defragmentacijom"
summary: "Alokator memorije u C++-u nad fiksnom arenom koji ume sam sebe da defragmentuje, uparen sa pametnim pokazivačem koji ostaje ispravan kada se blokovi pomeraju."
kind: Alokator memorije · C++
---

Kursni projekat iz 2015. (Tehnosfera, Mail.Ru Group i MGU „M. V. Lomonosov“): alokator memorije koji sam upravlja jednom fiksnom arenom umesto da poziva sistemski `malloc`.

## Kako radi

- **Bez dodatne memorije.** Alokator izdaje blokove iz unapred alociranog bafera, a njegova sopstvena evidencija — dvostruko povezana lista deskriptora blokova — živi u istom baferu, zbijena od njegovog kraja bez praznina. Alokacija i oslobađanje imaju složenost O(1).
- **Defragmentacija.** Posle mnogo alokacija i oslobađanja slobodan prostor se raspadne na sitne komade. Alokator primiče žive blokove jedan uz drugi, tako da slobodan prostor ponovo postane jedna neprekidna oblast; blok se može i realocirati na veću veličinu.
- **Pametni pokazivač.** Pomeranje blokova bi pokvarilo obične pokazivače, pa korisnik radi preko klase `Pointer`, koja upućuje na deskriptor bloka i ažurira se kada se blok pomeri.
- **Testovi.** U repozitorijumu je test-program za alokaciju, oslobađanje, realokaciju i defragmentaciju.

## Zašto je to važno

Sopstveni alokatori su jedan od glavnih alata za rad na performansama u C++-u: manje sistemskih poziva, bolja lokalnost podataka i predvidljiva potrošnja memorije. Ovaj projekat pokazuje mehaniku koja stoji iza toga — i cenu pomeranja objekata u memoriji.
