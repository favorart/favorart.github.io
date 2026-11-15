---
title: "allocator: defragmentatsiya qila oladigan xotira allokatori"
summary: "Qatʼiy arena ustida ishlaydigan va oʻzini oʻzi defragmentatsiya qila oladigan C++17 xotira allokatori hamda bloklar koʻchganda ham yaroqli qoladigan aqlli koʻrsatkich."
kind: Xotira allokatori · C++
---

2015-yilgi kurs loyihasi (Texnosfera, Mail.Ru Group va M. V. Lomonosov nomidagi MDU): tizimning `malloc` funksiyasini chaqirish oʻrniga bitta fiksirlangan arenani oʻzi boshqaradigan xotira allokatori. 2026-yilda kod qayta koʻrib chiqildi: xatolar tuzatildi, loyihada haqiqiy testlar, CI va relizlar paydo boʻldi.

## Qanday ishlaydi

- **Ortiqcha xotirasiz.** Allokator oldindan ajratilgan buferdan bloklar beradi, oʻzining hisob maʼlumotlari esa — manzil boʻyicha tartiblangan blok deskriptorlarining ikki tomonlama bogʻlangan roʻyxati — xuddi shu buferda, uning oxiridan boshlab boʻshliqlarsiz joylashadi. Ajratish roʻyxat boʻylab yurib, birinchi mos joyni qidiradi — O(bloklar soni); boʻshatish O(1) vaqt oladi.
- **Defragmentatsiya.** Koʻplab ajratish va boʻshatishlardan soʻng boʻsh joy mayda boʻlaklarga parchalanib ketadi. `defrag()` band bloklarni bir oʻtishda bir-biriga surib joylashtiradi va boʻsh joy yana bitta uzluksiz sohaga aylanadi; joy yetsa, `realloc()` blokni oʻz joyida kattalashtiradi yoki kichraytiradi.
- **Aqlli koʻrsatkich.** Bloklarni koʻchirish oddiy koʻrsatkichlarni buzib qoʻyadi, shuning uchun foydalanuvchi `Pointer` klassi orqali ishlaydi. U deskriptor joyini va blokning yagona indeksini eslab qoladi va blok koʻchgandan keyin uni qayta topadi; boʻshatilgan blokka koʻrsatkich `nullptr` qaytaradi.

## Muhandislik

- 2026-yilgi koʻrib chiqishda eski testlar AddressSanitizer va UndefinedBehaviorSanitizer ostida ishga tushirildi va oʻnta xato topildi — buferdan tashqariga yozishdan tortib boshqa birovning blokini topadigan koʻrsatkichgacha; har bir tuzatish uchun regressiya testi bor.
- GoogleTest testlari butun ommaviy APIni qamrab oladi, tasodifiy stress-test esa har bir band blokni model bilan baytma-bayt solishtiradi.
- CI loyihani Linuxda GCC va Clang bilan (sanitayzerlar ostida ham), Windowsda MSVC bilan va macOSda Apple Clang bilan yigʻadi; ogohlantirishlar xato deb hisoblanadi.
- READMEda `malloc`/`free` bilan taqqoslovchi benchmark bor va u narxni ochiq koʻrsatadi: ajratish roʻyxat boʻylab yuradi va `malloc`dan ancha sekin, siqish esa bitta `memmove` oʻtishidan iborat.
- `master`ga yuborilgan va CIdan oʻtgan har bir push versiya tegi hamda Linux, Windows va macOS uchun sarlavha fayli va statik kutubxona bilan GitHub Release oladi.

## Bu nima uchun muhim

Maxsus allokatorlar C++da unumdorlik ustida ishlashning asosiy vositalaridan biri: tizim chaqiruvlari kamroq, maʼlumotlar lokalligi yaxshiroq, xotira sarfi esa oldindan aytib boʻladigan. Bu loyiha shularning ichki mexanikasini — va obyektlarni xotirada koʻchirishning narxini koʻrsatadi.
