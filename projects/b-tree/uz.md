---
title: "b-tree: C tilida B-daraxtga asoslangan kalit-qiymat ombori"
summary: "C tilida noldan yozilgan, diskda saqlanadigan kalit-qiymat ombori: qatʼiy oʻlchamli sahifalar ustidagi B-daraxt, oʻzgaruvchan uzunlikdagi kalit va qiymatlar, LRU sahifa keshi va nosozlikdan keyin tiklash imkonini beradigan oldindan yoziladigan jurnal."
kind: Saqlash dvigateli · C
---

2015-yilda Texnosferada (Mail.Ru Group va M. V. Lomonosov nomidagi MDU) kurs loyihasi sifatida yozilgan kichik oʻrnatiladigan (embedded) maʼlumotlar bazasi. Vazifa haqiqiy maʼlumotlar bazalarining ostida yotgan saqlash qatlamini noldan qurish edi: berilgan C API (`dbcreate`, `dbopen`, qoʻshish, qidirish, oʻchirish, diskka yozish, yopish) ortidagi va maʼlumotlarini bitta faylda saqlaydigan kalit-qiymat ombori. 2026-yilda loyiha qayta jonlantirildi: chala qolgan oʻchirish va jurnaldan tiklash oxiriga yetkazildi, hammasi testlar bilan qamrab olindi.

## Qanday ishlaydi

- **Sahifalar ustidagi B-daraxt.** Fayl qatʼiy oʻlchamli sahifalarga boʻlinadi (standart boʻyicha 4 KB); daraxtning har bir tuguni — bitta sahifa. Oʻzgaruvchan uzunlikdagi kalit va qiymatlar bevosita tugunlarda saqlanadi, har bir yozuv sahifaning 1/8 qismigacha.
- **Boʻlish va muvozanatlash.** Toʻla sahifalar pastga tushish chogʻida, bir oʻtishda oldindan boʻlinadi; ketma-ket qoʻshishda sahifa qoʻshish nuqtasida boʻlinadi, shuning uchun sahifalar yaxshi toʻlgan holda qoladi. Oʻchirishda yetarlicha toʻlmagan sahifa qoʻshnisi bilan birlashtiriladi yoki undan yozuvlar oladi.
- **Boʻsh joy xaritasi.** Xizmat sahifalarida boʻsh sahifalarning bit xaritasi (bitmap) saqlanadi, shuning uchun oʻchirilgan sahifalar qayta ishlatiladi.
- **LRU kesh.** Yaqinda ishlatilgan sahifalar xotirada qoladi (standart boʻyicha 16 MB); oʻzgartirilgan («iflos») sahifalar keshdan chiqarilayotganda diskka qayta yoziladi — barchasi birdaniga, shuning uchun faylda doim izchil daraxt turadi.
- **Jurnal.** Har bir oʻzgarish avval nazorat yigʻindilari bilan oldindan yoziladigan jurnalga tushadi; baza ochilganda oxirgi nazorat nuqtasidan keyingi yozuvlar qayta bajariladi, nosozlik tufayli uzilib qolgan yozuv esa tashlab yuboriladi.
- **Sozlash.** Fayl hajmi, sahifa oʻlchami va kesh hajmi baza yaratilayotganda belgilanadi.

## Muhandislik

- Sof C99 va POSIX, bogʻliqliklarsiz, Make bilan yigʻiladi; Windows qoʻllab-quvvatlanmaydi.
- cmocka testlari: modullarning birlik testlari, etalon model bilan solishtiriladigan tasodifiy amallar, bola jarayonda nosozlikdan keyin tiklash va eng yomon yuklama holatlari; ular AddressSanitizer va UndefinedBehaviorSanitizer ostida ham ishga tushiriladi.
- Linux (gcc va clang, oddiy va sanitayzerlar bilan) va macOS uchun CI; benchmark `master`ga har bir push qilinganda ishlaydi.
- `master`ga yuborilgan va CIdan oʻtgan har bir push versiya tegi hamda Linux va macOS uchun kutubxona bilan GitHub Release oladi.

## Bu nima uchun muhim

Loyiha har qanday saqlash dvigatelining asosiy masalalariga bevosita taalluqli: sahifalar tuzilishi, tugunlarni boʻlish va birlashtirish, keshlash va mustahkamlik (durability). Bu darslikdagi B-daraxtdan SQLite yoki InnoDB qanday qurilganigacha toʻgʻridan-toʻgʻri yoʻl.
