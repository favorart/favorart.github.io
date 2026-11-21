---
title: "Diskret boshqaruvli tizimlarni oʻqitish algoritmi"
summary: "Tezis: robot pnevmoyuritmasining tasodifiy jarayon sifatidagi modeli hamda mexanizm dreyfini ish jarayonida kompensatsiya qilib, pozitsiyalash aniqligini saqlaydigan algoritm."
source: sources.yml papers/lomonosov-2020-learning-algorithm
source_lang: ru
source_hash: 5018b640
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---
Ish joyiga bir marta oʻrnatilgan robot uzluksiz pozitsiyalash harakatlarini bajaradi, vaqt oʻtishi bilan esa uning mexanizmida va atrof-muhitda aniqlikka taʼsir qiluvchi oʻzgarishlar yuz beradi. Robot muskulining (pnevmoyuritmasining) tasodifiy jarayonning additiv-multiplikativ shaklidagi modeli taklif etilgan: tezlik va tezlanishga cheklovlar qoʻyilgan deterministik tashkil etuvchi, yuqori chastotali soʻnuvchi tebranishlar, past chastotali sekin dreyf va anomal qiymatlar. Oʻqitish algoritmi anomal qiymatlarni filtrlaydi, nostoxastik parametrlarni tanlaydi va stoxastik parametrlarni kuzatib boradi, talab qilinadigan pozitsiyalash aniqligini saqlash uchun muskul ishining bir nechta ssenariysi oʻrtasida ish jarayonida almashinadi. Robot diskret holatli va diskret vaqtli bir jinsli boʻlmagan Markov qaror qabul qilish jarayoni bilan tavsiflangan; oʻqitish uchun natijani yaxshilaydigan birinchi topilgan qoʻshni yechimga oʻtadigan tushish usulining (hill climbing) bir varianti qoʻllaniladi.
