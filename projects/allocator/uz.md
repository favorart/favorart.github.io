---
title: "allocator: defragmentatsiya qila oladigan xotira allokatori"
summary: "Qatʼiy arena ustida ishlaydigan va oʻzini oʻzi defragmentatsiya qila oladigan C++ xotira allokatori hamda bloklar koʻchganda ham yaroqli qoladigan aqlli koʻrsatkich."
kind: Xotira allokatori · C++
---

2015-yilgi kurs loyihasi (Texnosfera, Mail.Ru Group va M. V. Lomonosov nomidagi MDU): tizimning `malloc` funksiyasini chaqirish oʻrniga bitta qatʼiy arenani oʻzi boshqaradigan xotira allokatori.

## Qanday ishlaydi

- **Ortiqcha xotirasiz.** Allokator oldindan ajratilgan buferdan bloklar beradi, oʻzining hisob maʼlumotlari esa — blok deskriptorlarining ikki tomonlama bogʻlangan roʻyxati — xuddi shu buferda, uning oxiridan boshlab boʻshliqlarsiz joylashadi. Ajratish va boʻshatish O(1) vaqt oladi.
- **Defragmentatsiya.** Koʻplab ajratish va boʻshatishlardan soʻng boʻsh joy mayda boʻlaklarga parchalanib ketadi. Allokator band bloklarni bir-biriga surib joylashtiradi va boʻsh joy yana bitta uzluksiz sohaga aylanadi; blokni kattaroq oʻlchamda qayta ajratish ham mumkin.
- **Aqlli koʻrsatkich.** Bloklarni koʻchirish oddiy koʻrsatkichlarni buzib qoʻyadi, shuning uchun foydalanuvchi blok deskriptoriga murojaat qiladigan va blok koʻchganda toʻgʻrilanadigan `Pointer` klassi orqali ishlaydi.
- **Testlar.** Repozitoriyda ajratish, boʻshatish, qayta ajratish va defragmentatsiyani tekshiradigan test dasturi bor.

## Bu nima uchun muhim

Maxsus allokatorlar C++da unumdorlik ustida ishlashning asosiy vositalaridan biri: tizim chaqiruvlari kamroq, maʼlumotlar lokalligi yaxshiroq, xotira sarfi esa oldindan aytib boʻladigan. Bu loyiha shularning ichki mexanikasini — va obyektlarni xotirada koʻchirishning narxini koʻrsatadi.
