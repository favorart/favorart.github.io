---
title: "Prelazak na AVX-512 nije ubrzao računanje"
summary: "Zašto prepisivanje najtoplijih petlji u NeoML-u sa AVX2 na AVX-512 nije donelo ubrzanje: Intelove frekvencijske „licence“, cena prebacivanja i Lemirovo pravilo."
source: posts/2026-11-avx512-frequency/index.md
source_lang: ru
source_hash: 8b5e3da9
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
Godine 2023. radio sam u ABBYY-ju na NeoML-u. To je open-source ML okvir na kom se na Windows serverima vrteo produkcioni inferens neuronskih mreža. Kod je bio maksimalno prenosiv, pa je kompajleru bila dozvoljena vektorizacija najviše do SSE/SSE2.

Jednog dana odlučeno je da se ciljano ubrzaju najtoplija mesta za konkretne Xeon procesore. Konvolucije, množenje matrica i vektorske funkcije ručno su prepisane na AVX2 i FMA, a za deo konvolucija napravljen je JIT preko xbyak-a. Ubrzanje je bilo očigledno.

Kad sam došao u tim, zadatak je zvučao logično: pošto je AVX2 dao dobro ubrzanje, prepišimo ista uska grla na AVX-512, vektor je dvostruko širi. Biće brže, zar ne?

Prepisao sam i izmerio. Ne: ubrzanja nije bilo.

Razlog su Intelove frekvencijske „licence“. Kada jezgro Xeona (Skylake-SP / Cascade Lake) izvršava vektorske instrukcije, prelazi na niži plafon frekvencije: L0 za običan kod, L1 za teške AVX2, L2 za teške AVX-512. Pri gustom AVX-512 kodu na mnogo jezgara gubitak frekvencije dostiže ~40%. Kod nas su široke instrukcije išle u neprekidnom nizu u dugim petljama, i dobitak od širine vektora pojela je niža frekvencija.

Verovatno se kompajleru može dozvoliti da sam ubacuje instrukcije na pravim mestima, tj. da ih „umešava pomalo“, ali ni to nije besplatno. Prelazak na drugu licencu košta 10–20 µs rada upola snage, a prethodna frekvencija vraća se tek posle ~2 ms. Jedna slučajna teška instrukcija usporava sav ostali kod na tom jezgru, na kom, uzgred, rade dve hiper-niti procesora. Indikativno je da GCC i Clang čak i sa uključenim AVX-512 podrazumevano biraju 256-bitne vektore (-mprefer-vector-width=256) upravo zbog toga.

Odakle takva pravila? Sve je stvar energije i toplote. 512-bitni FMA po taktu prebacuje višestruko više tranzistora nego skalarni kod. Energija se ne oslobađa po celom čipu, već u maloj zoni vektorskih jedinica, i tu nastaje vruća tačka. Struja naglo raste, napon propada, i čip mora da podigne napon da bi široke jedinice radile stabilno. Da ne bi prešao granice snage (TDP), struje i temperature, procesor unapred smanjuje frekvenciju, ne čekajući pregrevanje. Otuda i cena prelaska: dok se podiže napon i uključuju gornje polovine vektorskih registara, koje su u običnom režimu bez napajanja radi uštede, jezgro radi upola snage.

Nešto slično naš tim je video i ranije: na procesorima sa AVX-512 našu brzu AVX konvoluciju prvo su isključili, a zatim je potpuno izbacili.

Šta sam iz toga izvukao:

- Pravilo Danijela Lemira: AVX-512 se isplati ako je dobitak po taktu primetno veći od 2x.
- Na novim procesorima kazna će verovatno biti manja, pa odgovor zavisi od hardvera. Odlučuju frekvencija, memorija i priroda opterećenja.
- Prvo merenja, pa onda zaključci.

Za dalje čitanje:

- [Cloudflare Blog: On the dangers of Intel's frequency scaling](https://blog.cloudflare.com/on-the-dangers-of-intels-frequency-scaling/)
- [Travis Downs, Performance Matters: Gathering Intel on Intel AVX-512 Transitions](https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html)
- [Daniel Lemire's blog: AVX-512: when and how to use these new instructions](https://lemire.me/blog/2018/09/07/avx-512-when-and-how-to-use-these-new-instructions)

![Slika iz posta](cover.jpg)
