---
title: "b-tree: C tilida B-daraxtga asoslangan kalit-qiymat ombori"
summary: "C tilida noldan yozilgan, diskda saqlanadigan kalit-qiymat ombori: qatʼiy oʻlchamli sahifalar ustidagi B-daraxt, istalgan uzunlikdagi kalit va qiymatlar, LRU sahifa keshi va jurnal."
kind: Saqlash dvigateli · C
---

2015-yilda Texnosferada (Mail.Ru Group va M. V. Lomonosov nomidagi MDU) tizimli dasturlash kursi uchun yozilgan kichik oʻrnatiladigan (embedded) maʼlumotlar bazasi. Vazifa haqiqiy maʼlumotlar bazalarining ostida yotgan saqlash qatlamini noldan qurish edi: `dbopen`ga oʻxshash interfeysli (`put`, `get`, `delete`, `sync`, `close`) va maʼlumotlarini bitta faylda saqlaydigan kalit-qiymat ombori.

## Qanday ishlaydi

- **Sahifalar ustidagi B-daraxt.** Fayl qatʼiy oʻlchamli sahifalarga boʻlinadi (standart boʻyicha 4 KB); daraxtning har bir tuguni — bitta sahifa. Kalitlar va qiymatlar istalgan uzunlikda boʻlishi mumkin.
- **Boʻsh joy xaritasi.** Xizmat sahifalarida boʻsh sahifalarning bit xaritasi (bitmap) saqlanadi, shuning uchun oʻchirilgan sahifalar qayta ishlatiladi.
- **LRU kesh.** Yaqinda ishlatilgan sahifalar xotirada qoladi (standart boʻyicha 16 MB); oʻzgartirilgan («iflos») sahifalar keshdan chiqarilayotganda diskka qayta yoziladi.
- **Jurnal.** Oʻzgarishlar avval jurnalga yoziladi, shuning uchun nosozlikdan keyin bazani tiklash mumkin.
- **Sozlash.** Fayl hajmi, sahifa oʻlchami va kesh hajmi baza yaratilayotganda belgilanadi.

## Bu nima uchun muhim

Loyiha har qanday saqlash dvigatelining asosiy masalalariga bevosita taalluqli: sahifalar tuzilishi, tugunlarni boʻlish va birlashtirish, keshlash va mustahkamlik (durability). Bu darslikdagi B-daraxtdan SQLite yoki InnoDB qanday qurilganigacha toʻgʻridan-toʻgʻri yoʻl.
