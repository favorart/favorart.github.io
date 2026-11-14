---
title: "AVX-512ga oʻtish hisoblashlarni tezlashtirmadi"
summary: "NeoMLning eng qaynoq sikllarini AVX2dan AVX-512ga qayta yozish nega yutuq bermadi: Intel chastota «litsenziyalari», oʻtish narxi va Lemir qoidasi."
source: posts/2026-11-avx512-frequency/index.md
source_lang: ru
source_hash: 8b5e3da9
translated: 2026-11-14
translator: Claude
reviewed:            # date of the independent review; the build ignores the file until it is set
---
2023-yilda men ABBYYda NeoML ustida ishlardim. Bu open-source ML-freymvork boʻlib, Windows serverlarida neyrotarmoqlarning jangovar inferensi aynan unda ishlardi. Kod imkon qadar koʻchma boʻlishi kerak edi, shuning uchun kompilyatorga SSE/SSE2dan yuqori vektorlashtirishga ruxsat berilmagan.

Bir kuni eng qaynoq joylarni aniq Xeon protsessorlari uchun nuqtaviy tezlashtirishga qaror qilishdi. Konvolyutsiyalar, matritsa koʻpaytmasi va vektor funksiyalari AVX2 va FMAda qoʻlda qayta yozildi, konvolyutsiyalarning bir qismi uchun esa xbyak orqali JIT qilindi. Yutuq yaqqol edi.

Men jamoaga kelganimda vazifa mantiqiy eshitilardi: AVX2 yaxshi yutuq bergan ekan, oʻsha tor joylarni AVX-512da qayta yozamiz — vektor 2 baravar keng. Tezroq boʻladi, toʻgʻrimi?

Qayta yozdim va oʻlchadim. Notoʻgʻri: hech qanday yutuq boʻlmadi.

Sababi Intel chastota «litsenziyalari»da. Xeon yadrosi (Skylake-SP / Cascade Lake) vektor instruksiyalarini bajarayotganda pasaytirilgan chastota shiftiga oʻtadi: oddiy kod uchun L0, ogʻir AVX2 uchun L1, ogʻir AVX-512 uchun L2. Koʻp yadrolarda zich AVX-512 ishlaganda chastota yoʻqotilishi ~40% gacha yetadi. Bizda keng instruksiyalar uzun sikllarda uzluksiz oqim boʻlib borardi va vektor kengligidan olingan yutuqni pastroq chastota yeb qoʻyardi.

Ehtimol, kompilyatorga instruksiyalarni kerakli joylarga oʻzi qoʻshishiga, yaʼni «ozginadan aralashtirishga» ruxsat berish mumkindir, lekin bu ham tekin emas. Boshqa litsenziyaga oʻtish 10–20 mks yarim quvvatda ishlash bilan toʻlanadi, avvalgi chastota esa faqat ~2 ms dan keyin qaytadi. Bitta tasodifiy ogʻir instruksiya shu yadrodagi qolgan barcha kodni sekinlashtiradi, bu yadroda esa, aytgancha, protsessorning 2 ta giper-oqimi ishlaydi. Eʼtiborlisi, GCC va Clang hatto AVX-512 yoqilgan boʻlsa ham sukut boʻyicha 256-bitli vektorlarni afzal koʻradi (-mprefer-vector-width=256) — aynan shu sababdan.

Bunday qoidalar qayerdan kelgan? Gap energiya va issiqlikda. Bir taktdagi 512-bitli FMA skalyar kodga qaraganda bir necha baravar koʻp tranzistorni almashtiradi. Energiya butun kristall boʻylab emas, vektor bloklarining kichik zonasida ajraladi va u yerda qaynoq nuqta hosil boʻladi. Tok keskin oshadi, kuchlanish tushib ketadi va keng bloklar barqaror ishlashi uchun chip kuchlanishni koʻtarishi kerak boʻladi. Quvvat (TDP), tok va harorat chegaralaridan chiqib ketmaslik uchun protsessor qizib ketishni kutmasdan, chastotani oldindan pasaytiradi. Oʻtish narxi ham shundan: kuchlanish koʻtarilayotgan va oddiy rejimda tejash uchun tokdan uzib qoʻyilgan vektor registrlarining yuqori yarmlari yoqilayotgan paytda yadro yarim quvvatda ishlaydi.

Shunga oʻxshash holatni jamoamiz avval ham koʻrgan edi: AVX-512li protsessorlarda tezkor AVX-konvolyutsiyamizni avval oʻchirib qoʻyishdi, keyin esa butunlay olib tashlashdi.

Bundan nimani oʻrgandim:

- Daniel Lemir qoidasi: AVX-512 oʻzini oqlaydi, agar bir taktdagi yutuq 2x dan sezilarli darajada katta boʻlsa.
- Yangi protsessorlarda jarima, ehtimol, kamroq boʻladi, shuning uchun javob temirga bogʻliq. Chastota, xotira va yuklama xarakteri hal qiladi.
- Avval oʻlchovlar, keyin xulosalar.

Oʻqish uchun:

- [Cloudflare Blog: On the dangers of Intel's frequency scaling](https://blog.cloudflare.com/on-the-dangers-of-intels-frequency-scaling/)
- [Travis Downs, Performance Matters: Gathering Intel on Intel AVX-512 Transitions](https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html)
- [Daniel Lemire's blog: AVX-512: when and how to use these new instructions](https://lemire.me/blog/2018/09/07/avx-512-when-and-how-to-use-these-new-instructions)

![Post rasmi](cover.jpg)
