---
title: "Qanday qilib 1 ta float videokartadagi oʻqitishni sekinlashtira oladi?"
summary: "Sinxron cudaMemcpy bilan GPUga uzatilgan bitta skalyar butun oʻqitish konveyerini toʻxtatib qoʻyadi. Nega shunday boʻladi va NeoMLda sonni qiymat boʻyicha uzatib, toʻxtashlarsiz qanday ishlash mumkin."
source: posts/2026-11-gpu-waits-for-a-float/index.md
source_lang: ru
source_hash: f24792e0
translated: 2026-11-15
translator: Claude
reviewed: 2026-11-15
---
Qanday qilib 1 ta float videokartadagi oʻqitishni sekinlashtira oladi?

Kuchli videokartani serverga matritsalar, konvolyutsiyalar va gradiyentlar shamoldek uchsin deb qoʻyishadi. Ulkan matritsalardagi hisoblashlar toʻxtab, nimanidir kutib tursa, alam qiladi. Bu muammoni men ABBYYning ochiq ML-kutubxonasi NeoMLda tuzatganman (u haqda [oldingi postda](/uz/writing/avx512-frequency/) yozgan edim).

Videokarta — oʻz xotirasiga ega alohida mini-kompyuter, u dasturning RAM-xotirasini koʻrmaydi: hisoblash uchun kerak boʻlgan hamma narsa unga shina orqali olib kelinadi.

Neyrotarmoqlarni oʻqitishda protsessorning oʻzi deyarli hisoblamaydi — u videokarta uchun vazifalarni navbatga qoʻyadi. Bir-ikki mikrosekundda qoʻydi-yu, natijani kutmasdan oldinga yugurdi. GPU vazifalarni qatʼiy tartib bilan bajaradi. Agar bittasi natijani karta xotirasiga yozsa, keyingisi esa uni oʻqisa, kutadigan narsa yoʻq: u boshlanganda maʼlumotlar allaqachon joyida boʻladi. Sogʻlom dasturda CPU ancha oldinga ketib qoladi, videokartaning vazifalar navbati esa boʻshamaydi.

Endi vazifaga CPUdan bitta son kerak boʻlsin, atigi 4 bayt. Shina tezligining bunga aloqasi yoʻq: ular undan bir zumda oʻtib ketadi. Qimmati — reysning oʻzi.

CUDAdagi asosiy nusxalash funksiyasi cudaMemcpy sinxron: avval GPU oldinroq qoʻyilgan hamma narsani bajarib boʻlishini kutadi va shundan keyingina nusxalaydi. Tartib muhim: kartadagi yacheykani navbatdagi vazifalar hali oʻqishi mumkin va ularga eski qiymat kerak.

Keyin — reys almashtirish. Baytlarni shina orqali videokartaning alohida bloki — DMA tashiydi. U ularni faqat mahkamlangan (pinned) RAM-xotiradan ola biladi — OT diskka chiqarib tashlamaydigan va joyidan siljitmaydigan xotiradan. Shuning uchun drayver sonni oʻzining mahkamlangan buferiga koʻchiradi va son faqat u yerdan kartaga yoʻl oladi.

Jami: GPU navbatni tugatguncha CPU turib qoladi, keyin 2 ta uzatish, keyin CPU navbatni qaytadan toʻldirguncha GPU boʻsh turadi. NVIDIAda shunday oʻlchov bor: vazifa 2,9 mks davomida bajariladi. CPU kutmasa, bir vazifaga 3,8 mks chiqadi. Har biridan keyin kutsa — 9,6. 2,5 baravar sekinroq, bunda hali nusxalash hisobga olinmagan.

Kutmaslik mumkin: cudaMemcpyAsync nusxalashni navbatga yana bitta vazifa sifatida qoʻyadi. Lekin unda son albatta mahkamlangan RAM-xotirada turishi va navbat unga yetib kelguncha oʻzgarmasligi shart. Bunday xotirani ajratish uzoq vaqt oladi, u OTdan tortib olinadi, shuning uchun har bir son uchun yangi bufer olib boʻlmaydi. Yacheykalar puli va ulardan qaysi birini GPU allaqachon oʻqiganini hisobga olib borish kerak. 4 bayt uchun butun boshli quyi tizim.

NeoMLda bunday quyi tizim yoʻq edi. Deyarli barcha metodlar skalyarlarni karta xotirasidagi manzil orqali qabul qilardi, u yerga ularni esa cudaMemcpy joylardi. Yoʻqotish funksiyasidagi mashina epsiloni, MobileNet bloklaridagi ReLU chegarasi, optimizatordagi gradiyent chegaralari, istalgan koeffitsiyent — hammasi konveyerni toʻliq toʻxtatib, kartaga yoʻl olardi. Oʻqitishning har bir qadamida.

Aylanma yoʻl topildi: vazifa argumentlari qiymat boʻyicha, ishga tushirish buyrugʻi ichida uzatiladi. Son navbatga qoʻyilayotgan paytda buyruqqa yozib qoʻyiladi — na bufer, na reys. Koeffitsiyent qayerdan kelmasin — dastur xotirasidan qiymat boʻyicha yoki videokarta xotirasidan manzil boʻyicha, — vazifa boshlanganda u maʼlum boʻladi. Hech qanday holatda toʻxtash boʻlmaydi.

Videokartaga kutmaslikka yordam beradigan [PR](https://github.com/neoml-lib/neoml/pull/1070){: hreflang=en } esa 2024-yildan beri oʻzi navbatini kutib yotibdi.

Sizga kodingiz nimani kutayotganini qidirishga toʻgʻri kelganmi?

\#CUDA #GPU #ML #unumdorlik

Oʻqish uchun:

* NVIDIA, CUDA Runtime API: API synchronization behavior — qaysi nusxalash navbatni kutadi, qaysi biri kutmaydi https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html
* NVIDIA, How to Optimize Data Transfers in CUDA C/C++ — mahkamlangan xotira va mayda uzatishlar narxi https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/
* NVIDIA, Getting Started with CUDA Graphs — 2,9 / 3,8 / 9,6 mks raqamlari qayerdan olingan https://developer.nvidia.com/blog/cuda-graphs/
* PyTorch Performance Tuning Guide https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html

![Post rasmi](cover.jpg)
