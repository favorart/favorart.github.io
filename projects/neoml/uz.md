---
title: "NeoML: ABBYYning mashinali oʻqitish freymvorkiga qoʻshgan hissam"
summary: "ABBYYning chuqur oʻqitish va klassik ML uchun ochiq kodli C++ freymvorki NeoMLga yuzdan ortiq qabul qilingan pull request: unumdorlik, xotira, CUDA va ONNX importi."
kind: Ochiq kodga hissa · C++
---

[NeoML](https://github.com/neoml-lib/neoml) — ABBYYning ochiq kodli mashinali oʻqitish freymvorki: neyron tarmoqlar va klassik algoritmlar, C++ tilida yozilgan, CPU, CUDA, Metal va Vulkan ustida ishlaydi, Python bindinglari va ONNX modellarini import qilish imkoniyati bor. 2022–2024-yillarda ABBYYdagi ishim doirasida unga yuzdan ortiq pull requestim qabul qilindi.

## Ishning asosiy yoʻnalishlari

- **OpenMP oʻrniga — oʻz oqimlar puli.** CPU hisoblash dvigateli va klassik algoritmlarni (gradient boosting, SVM, k-means, optimizatorlar) OpenMPdan freymvorkning oʻz oqimlar puliga (thread pool) koʻchirdim: endi kutubxona oʻz oqimlarini oʻzi boshqaradi va barcha platformalarda bir xil ishlaydi.
- **Xotira.** Xotira dvigateli va stek allokatorlarini refaktoring qildim, xotira limitlari, eng yuqori xotira sarfi statistikasi, har bir oqim uchun alohida bufer pullari va oqimlar oʻrtasida maʼlumot uzatishni qoʻshdim, qatlamlarning (jumladan, LoRA qatlamlarining) xotira sarfini kamaytirdim.
- **Tezlik.** Konvolyutsiyaning tezroq teskari oʻtishi (backward pass), MKL JIT matritsa koʻpaytmasi, L1/L2 kesh oʻlchamlariga moslangan matritsa koʻpaytirgich, CUDA sinxronizatsiyalarini kamaytirish, pooling yadrolarida mikrooptimallashtirishlar.
- **CUDA dvigateli.** Reduksiya yadrolari, umumiy buferni initsializatsiya qilish va standart qiymatlardagi xatolarni tuzatish.
- **Modellar.** Pre-normalizatsiyali transformer enkoderi, gradientni kesish (gradient clipping), taqsimlangan inferens; NeoOnnxda — ikki yoʻnalishli LSTM, 1D transponirlangan konvolyutsiya, qatlam normalizatsiyasini qoʻshni amallar bilan birlashtirish (layer-normalization fusion) va graf optimizatori.
- **Yigʻish va sifat.** Android va iOS uchun ixcham yigʻma, macOS uchun kross-kompilyatsiya, Visual Studio 2022ga oʻtish, CodeQL tekshiruvlari, yangi testlar va tozaroq ommaviy sarlavha fayllari.

## Bu nima uchun muhim

Bu boshqa jamoalar va tashqi foydalanuvchilar oʻz ishini quradigan, real ishlatiladigan kod: har bir oʻzgarish kod reviewidan oʻtgan, API barqarorligini saqlashi va barcha qoʻllab-quvvatlanadigan platformalarda ishlashi shart edi.
