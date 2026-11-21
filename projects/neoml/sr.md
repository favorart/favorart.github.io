---
tagline: "Doprinos ABBYY-jevom frejmvorku otvorenog koda za ML u C++-u"
summary: "Više od sto prihvaćenih pull request-ova u ABBYY-jev ML frejmvork u C++-u, 2022–2024: OpenMP zamenjen sopstvenim thread pool-om, preuređeno memorijsko jezgro, višenitni inferens nad zajedničkim težinama, uvoz ONNX modela."
kind: "Doprinos otvorenom kodu · C++"
---

[NeoML](https://github.com/neoml-lib/neoml) je ABBYY-jev frejmvork otvorenog koda za duboko učenje i klasično mašinsko učenje: napisan je u C++-u, radi na CPU-u, CUDA-i, Metal-u i Vulkan-u, ima interfejs za Python i uvoz ONNX modela. Od kraja 2022. do 2024, u okviru posla u ABBYY-ju, u njega sam spojio više od sto pull request-ova. Najveći delovi: izbacivanje OpenMP-a iz celog frejmvorka u korist sopstvenog thread pool-a, preuređenje memorijskog jezgra i inferens u mnogo niti koje dele jednu kopiju težina.

## Glavni pravci rada

- **OpenMP napolje, sopstveni thread pool unutra.** CPU matematičko jezgro i klasični algoritmi (gradient boosting, SVM, k-means, optimizatori) prešli su na sopstveni thread pool frejmvorka, tako da biblioteka sama upravlja svojim nitima i radi isto na svim platformama; samo je poslednji pull request obrisao skoro dve hiljade linija.
- **Memorija.** Refaktorisano memorijsko jezgro i stek alokatori, ograničenja memorije, statistika vršne potrošnje memorije, pulovi bafera po niti sa pragom u bajtovima, prenos podataka između niti i štedljiviji slojevi (uključujući LoRA).
- **Inferens.** Distribuirani inferens: kopije mreže u više niti dele težine umesto da ih dupliraju.
- **Brzina.** Unazadni prolaz konvolucije sa manje memorije i manje transponovanja, manje CUDA sinhronizacija, mikrooptimizacije u kernelima pooling-a; množenje matrica preko MKL JIT-a u nekim slojevima (kasnije delimično povučeno).
- **CUDA jezgro.** Ispravke u kernelima redukcije i podrazumevanim vrednostima, izbegavanje NaN vrednosti u LSTM-u na GPU-u.
- **Modeli i ONNX.** Transformer enkoder sa prednormalizacijom, odsecanje gradijenta; u NeoOnnx-u — dvosmerni LSTM, 1D transponovana konvolucija, fuzija operacija normalizacije sloja (layer normalization) i optimizator grafa.
- **Build i kvalitet.** Kompaktan build za Android/iOS, kroskompajliranje za macOS, Visual Studio 2022, CodeQL, novi testovi i čistiji javni hederi.

Svaka izmena je prošla pregled koda i morala je da sačuva stabilan javni API na svim podržanim platformama.
