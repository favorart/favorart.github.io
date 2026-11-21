---
tagline: "Oʻzini defragmentatsiya qiladigan allokator va aqlli koʻrsatkich"
summary: "Qoʻshimcha xotirasiz C++17 allokatori: defrag() 6,4 GB/s tezlikda siqadi, Pointer esa koʻchgan bloklarni kuzatib boradi. Oʻlchangan narx: alloc() mallocdan taxminan 140 baravar sekinroq."
kind: "Xotira allokatori · C++"
---

2015-yilgi kurs loyihasi (Texnosfera, Mail.Ru Group va M. V. Lomonosov nomidagi MDU): bitta qatʼiy bufer ustida ishlaydigan va oʻz hisob maʼlumotlarini shu buferning ichida saqlaydigan allokator — maʼlumotlar boshidan, blok deskriptorlari esa oxiridan oʻsadi. `defrag()` bloklarni koʻchirgani uchun foydalanuvchi oʻz blokini yagona indeks boʻyicha qayta topadigan `Pointer` bilan ishlaydi. 2026-yilda sanitayzerlar va kodni koʻrib chiqish unda 13 ta xato topdi — buferdan tashqariga yozishdan tortib boshqa birovning blokini topadigan koʻrsatkichgacha; har bir tuzatish uchun regressiya testi bor.

## Qanday ishlaydi

- **Qoʻshimcha xotirasiz.** Deskriptorlar manzil boʻyicha tartiblangan ikki tomonlama bogʻlangan roʻyxatni tashkil qiladi va buferning oxirida boʻshliqlarsiz joylashadi. Ajratish birinchi mos joyni qidirib roʻyxat boʻylab yuradi — O(bloklar soni); boʻshatish O(1) vaqt oladi.
- **Defragmentatsiya.** `defrag()` band bloklarni bir oʻtishda bir-biriga surib joylashtiradi va boʻsh joy yana bitta sohaga aylanadi; joy yetsa, `realloc()` blokni oʻz joyida kattalashtiradi yoki kichraytiradi.
- **Aqlli koʻrsatkich.** `Pointer` deskriptor joyini va blokning indeksini eslab qoladi va blok koʻchgandan keyin uni qayta topadi; boʻshatilgan blokka koʻrsatkich `nullptr` qaytaradi.
- **Oʻz-oʻzini tekshirish.** `check()` arenaning barcha invariantlarini tekshiradi, `dump()` uning xaritasini chiqaradi.

## Oʻlchangan narx

READMEdagi benchmark buni halol koʻrsatadi: ajratish roʻyxat boʻylab yurgani uchun 4,6 µs vaqt oladi, `malloc` esa 33 ns; siqish band maʼlumotlar boʻyicha 6,4 GB/s tezlikda ishlaydi, joyi keshlangan `Pointer`ni dereferensiya qilish esa 2,3 ns vaqt oladi.

## Muhandislik

- Butun ommaviy APIni qamrab oluvchi GoogleTest toʻplamlari, har bir band blokni model bilan baytma-bayt solishtiradigan tasodifiy stress-test va libFuzzer maqsadi; stress-testlar va fazzer har bir amaldan keyin `check()`ni chaqiradi.
- Linuxda GCC va Clang bilan (AddressSanitizer va UndefinedBehaviorSanitizer ostida ham), Windowsda MSVC bilan va macOSda Apple Clang bilan CI, ogohlantirishlar xato deb hisoblanadi; `master`ga yuborilgan va CIdan muvaffaqiyatli oʻtgan har bir push versiya tegi va GitHub Release oladi.
