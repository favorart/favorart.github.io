---
tagline: "C tilida jurnalli, diskdagi B-daraxtli kalit-qiymat ombori"
summary: "Sof C tilida yozilgan, bitta faylda saqlanadigan kalit-qiymat ombori: B-daraxt sahifalari, LRU kesh va nazorat yigʻindili jurnal. Nosozlikdan keyin tiklash bola jarayonni oʻldirish orqali tekshiriladi; eng yomon holatlar oʻlchangan."
kind: "Saqlash dvigateli · C"
---

2015-yilda Texnosferada (Mail.Ru Group va M. V. Lomonosov nomidagi MDU) berilgan C API ortida yozgan va 2026-yilda oxiriga yetkazgan oʻrnatiladigan kalit-qiymat omborim. Fayldagi har bir sahifa — B-daraxt tuguni. Kesh barcha oʻzgartirilgan sahifalarni birdaniga yozadi, shuning uchun faylda doim izchil daraxt turadi, jarayon nosozligidan keyin jurnalni qayta bajarish esa barcha tasdiqlangan oʻzgarishlarni qaytaradi. Toʻla sahifani qoʻshish nuqtasida boʻlish ketma-ket qoʻshishda sahifalarning 68% toʻlishini saqlab qoladi.

## Qanday ishlaydi

- **Sahifalar ustidagi B-daraxt.** Qatʼiy oʻlchamli sahifalar (standart boʻyicha 4 KB); oʻzgaruvchan uzunlikdagi kalit va qiymatlar bevosita tugunlarda saqlanadi, har bir yozuv sahifaning 1/8 qismigacha. Toʻla sahifalar pastga tushish chogʻida bir oʻtishda boʻlinadi; oʻchirishda yetarlicha toʻlmagan sahifalar qoʻshnisi bilan birlashtiriladi yoki undan yozuvlar oladi.
- **Boʻsh joy xaritasi.** Xizmat sahifalarida boʻsh sahifalarning bit xaritasi saqlanadi, shuning uchun oʻchirilgan sahifalar qayta ishlatiladi.
- **LRU kesh.** Yaqinda ishlatilgan sahifalar xotirada qoladi (standart boʻyicha 16 MB); oʻzgartirilgan («iflos») sahifa keshdan chiqarilayotganda barcha shunday sahifalar diskka yoziladi va `fsync` chaqiriladi.
- **Jurnal.** Har bir oʻzgarish avval nazorat yigʻindili yozuvlardan iborat jurnalga tushadi; baza ochilganda oxirgi nazorat nuqtasidan keyingi yozuvlar qayta bajariladi, nosozlik tufayli uzilib qolgan yozuv esa eʼtiborga olinmaydi.
- **Diagnostika.** `db_check` daraxtni tekshiradi, `db_stats` uning shakli va toʻlishi haqida hisobot beradi, `db_trace` amallarni toʻrt darajada qayd etadi.

## Muhandislik

- Sof C99 va POSIX, bogʻliqliklarsiz, Make bilan yigʻiladi.
- cmocka testlari: modullarning birlik testlari, etalon model bilan solishtiriladigan tasodifiy amallar, bola jarayonda nosozlikdan keyin tiklash va eng yomon yuklama holatlari; ularning barchasi AddressSanitizer va UndefinedBehaviorSanitizer ostida ham ishga tushiriladi.
- READMEdagi benchmark: daraxt keshga sigʻganda soniyasiga taxminan 186 ming tasodifiy qoʻshish va 594 ming qidiruv.
- Linux (gcc va clang, oddiy va sanitayzerlar bilan) va macOS uchun CI; `master`ga yuborilgan va CIdan oʻtgan har bir push versiya tegi va GitHub Release oladi.

## Cheklovlar

Jurnal elektr taʼminoti uzilishidan emas, jarayon nosozligidan himoya qiladi; baza bilan bir vaqtda faqat bitta jarayon ishlaydi; bu B+-daraxt emas, B-daraxt.
