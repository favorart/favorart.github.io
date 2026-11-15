---
title: "NeoML: doprinos ABBYY-jevom frejmvorku za mašinsko učenje"
summary: "Više od sto prihvaćenih pull request-ova u NeoML, ABBYY-jev frejmvork otvorenog koda u C++-u za duboko učenje i klasični ML: performanse, memorija, CUDA i uvoz ONNX modela."
kind: Doprinos otvorenom kodu · C++
---

[NeoML](https://github.com/neoml-lib/neoml) je ABBYY-jev frejmvork otvorenog koda za mašinsko učenje (neuronske mreže i klasični algoritmi): napisan je u C++-u, radi na CPU-u, CUDA-i, Metal-u i Vulkan-u, ima interfejs za Python i uvoz ONNX modela. Od 2022. do 2024, u okviru posla u ABBYY-ju, u njega je spojeno više od sto mojih pull request-ova.

## Glavni pravci rada

- **OpenMP napolje, sopstveni thread pool unutra.** CPU matematičko jezgro i klasične algoritme (gradient boosting, SVM, k-means, optimizatore) prebacio sam sa OpenMP-a na sopstveni thread pool frejmvorka, tako da biblioteka sama upravlja svojim nitima i radi isto na svim platformama.
- **Memorija.** Refaktorisao sam memorijsko jezgro i stek alokatore, dodao ograničenja memorije, statistiku vršne potrošnje memorije, prag u bajtovima za pulove bafera svake niti i prenos podataka između niti, i smanjio potrošnju memorije slojeva (uključujući LoRA slojeve).
- **Brzina.** Brži unazadni prolaz konvolucije, množenje matrica preko MKL JIT-a u nekim slojevima (kasnije delimično povučeno), manje CUDA sinhronizacija, mikrooptimizacije u kernelima pooling-a.
- **CUDA jezgro.** Ispravke u kernelima redukcije i podrazumevanim vrednostima, zaštita LSTM-a na GPU-u od NaN vrednosti i dodatne zaštitne inicijalizacije.
- **Modeli.** Transformer enkoder sa prednormalizacijom, odsecanje gradijenta, distribuirani inferens; u NeoOnnx-u — dvosmerni LSTM, 1D transponovana konvolucija, fuzija layer normalization operacije i optimizator grafa.
- **Build i kvalitet.** Kompaktan build za Android i iOS, kroskompajliranje za macOS, prelazak na Visual Studio 2022, CodeQL provere, novi testovi i čistiji javni hederi.

## Zašto je to važno

Ovo je produkcioni kod na koji se oslanjaju drugi timovi i spoljni korisnici: svaka izmena je prošla pregled koda, morala je da sačuva stabilan API i da radi na svim podržanim platformama.
