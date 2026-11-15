---
title: "Kako jedan float može da uspori obuku na grafičkoj kartici?"
summary: "Jedan skalar, poslat na GPU sinhronim pozivom cudaMemcpy, zaustavlja ceo pajplajn obuke. Zašto se to dešava i kako u NeoML-u izbeći zastoje tako što se broj prosledi po vrednosti."
source: posts/2026-11-gpu-waits-for-a-float/index.md
source_lang: ru
source_hash: 104d94b0
translated: 2026-11-15
translator: Claude
reviewed: 2026-11-15
---
Kako jedan float može da uspori obuku na grafičkoj kartici?

Moćnu grafičku karticu stavljaju u server da bi matrice, konvolucije i gradijenti leteli. Šteta je kad računanje nad ogromnim matricama stoji i čeka. Taj problem sam rešavao u NeoML-u, ABBYY-jevoj ML biblioteci otvorenog koda (o njoj je bio [prethodni post](/sr/writing/avx512-frequency/)).

Grafička kartica je zaseban mini-računar sa sopstvenom memorijom, i RAM memoriju programa ne vidi: sve što joj treba za računanje doprema joj se preko magistrale.

Pri obuci neuronskih mreža procesor sam gotovo ništa ne računa — on stavlja zadatke u red grafičke kartice. Stavi zadatak za par mikrosekundi i juri dalje, ne čeka rezultat. GPU izvršava zadatke strogo po redu. Ako jedan upisuje rezultat u memoriju kartice, a sledeći ga čita, nema šta da se čeka: kad sledeći krene, podaci su već tu. U zdravom programu CPU odmakne daleko napred, a red zadataka grafičke kartice nikad se ne isprazni.

Sad neka zadatku treba broj sa CPU-a, svega 4 bajta. Brzina magistrale tu nije bitna: ona ih prenese u trenu. Skupa je sama vožnja.

Osnovna funkcija za kopiranje u CUDA-i, cudaMemcpy, sinhrona je: prvo čeka da GPU izvrši sve što je ranije stavljeno u red, pa tek onda kopira. Redosled je važan: ćeliju na kartici možda još čitaju zadaci iz reda, i njima treba stara vrednost.

Zatim presedanje. Bajtove preko magistrale vozi poseban blok grafičke kartice, DMA. On ume da ih preuzme samo iz zaključane (pinned) RAM memorije — one koju OS neće izbaciti na disk niti premestiti. Zato drajver prebacuje broj u svoj zaključani bafer, i tek odatle on putuje na karticu.

Ukupno: CPU stoji dok GPU ne završi red, zatim 2 prenosa, zatim GPU stoji prazan dok CPU ponovo puni red. NVIDIA ima merenje: zadatak se računa 2,9 µs. Ako CPU ne čeka, ispada 3,8 µs po zadatku. Ako čeka posle svakog — 9,6. To je 2,5 puta sporije, i to još bez kopiranja.

Može i bez čekanja: cudaMemcpyAsync stavlja kopiranje u red kao još jedan zadatak. Ali tada broj mora da stoji u zaključanoj RAM memoriji i da se ne menja dok red ne dođe do njega. Alociranje takve memorije traje dugo, a oduzima se od OS-a, pa svež bafer za svaki broj ne dolazi u obzir. Treba pul ćelija i evidencija o tome koju je GPU već pročitao. Ceo podsistem zbog 4 bajta.

U NeoML-u ga nije bilo. Gotovo sve metode primale su skalare kao adresu u memoriji kartice, a tamo ih je stavljao cudaMemcpy. Mašinski epsilon u funkciji gubitka, prag ReLU-a u blokovima MobileNet-a, granice gradijenta u optimizatoru, bilo koji koeficijent — putovali su na karticu uz potpuno zaustavljanje pajplajna. Na svakom koraku obuke.

Našao se zaobilazni put: argumenti zadatka prosleđuju se po vrednosti, unutar same komande pokretanja. Broj se upisuje u komandu u trenutku stavljanja u red — nema ni bafera ni vožnje. Odakle god da koeficijent stigne — iz memorije programa po vrednosti ili iz memorije grafičke kartice po adresi — poznat je kad zadatak krene. Zastoja nema ni u jednom slučaju.

[PR](https://github.com/neoml-lib/neoml/pull/1070){: hreflang=en } koji pomaže grafičkoj kartici da ne čeka i sam od 2024. godine čeka svoj red.

A da li ste vi ikad tražili šta to vaš kod čeka?

\#CUDA #GPU #ML #performanse

Za dalje čitanje:

* [NVIDIA, CUDA Runtime API: API synchronization behavior](https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html) — koje kopiranje čeka red, a koje ne
* [NVIDIA, How to Optimize Data Transfers in CUDA C/C++](https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/) — zaključana memorija i cena sitnih prenosa
* [NVIDIA, Getting Started with CUDA Graphs](https://developer.nvidia.com/blog/cuda-graphs/) — odakle brojke 2,9 / 3,8 / 9,6 µs
* [PyTorch Performance Tuning Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

![Slika iz posta](cover.jpg)
