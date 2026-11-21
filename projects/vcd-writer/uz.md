---
tagline: "VCD fayllari uchun tez, bogʻliqliksiz C++20 kutubxona"
summary: "VCD toʻlqin diagrammasi fayllarini yozadigan C++20 kutubxonasi: qiymatning har bir oʻzgarishida xotira ajratilmaydi, natija esa har qanday OTda baytma-bayt bir xil. Sanitayzerlar bilan oʻtkazilgan tekshiruv 18 ta yashil test sezmagan dinamik xotira buzilishini topdi."
kind: "Kutubxona · C++20"
---

Value Change Dump (VCD) — apparat simulyatorlari signallarning vaqt oʻtishi bilan qanday oʻzgarishini yozib boradigan matnli format; GTKWave va boshqa koʻruvchi dasturlar uni toʻlqin diagrammalari koʻrinishida chizadi. 2017-yilda Python kutubxonasi [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd)ni C++ga koʻchirdim. 2026-yilda uni AddressSanitizer va UndefinedBehaviorSanitizer ostida ishga tushirib, dinamik xotirada bufer toʻlib ketishi, null koʻrsatkichni dereferensiya qilish, istisno chiqaradigan destruktor va yaroqsiz VCD natijasini topdim — bularning barchasi 18 ta muvaffaqiyatli test ortida yashiringan edi, chunki testlar solishtiradigan etalon fayl notoʻgʻri natijani mustahkamlab qoʻygan edi. Tuzatishlardan soʻng kutubxonada 39 ta test bor, eng koʻp chaqiriladigan kod qismini qayta yozish esa `change()`ni [2–5 baravar tezlashtirdi](https://github.com/favorart/vcd-writer/pull/10).

## Ichida nima bor

- **Standart bandma-band.** IEEE 1364-2005 standarti (§18.2) boʻyicha toʻrt holatli VCD: sarlavha, ichma-ich sohalar, oʻzgaruvchilarning barcha 18 turi, skalyar, vektor va haqiqiy son qiymatlari, `$dumpvars`, `$dumpoff` / `$dumpon`; satr qiymatlari — GTKWave kengaytmasi sifatida. README faylida nima qoʻllab-quvvatlanishi va nima qoʻllab-quvvatlanmasligi jadvali bor.
- **Har bir oʻzgarishda xotira ajratilmaydi.** Qiymatlar 64 KiB hajmli buferga formatlanadi va bitta chaqiruv bilan yoziladi; benchmark repozitoriyning oʻzida.
- **Yon taʼsirsiz validatsiya.** Nomlar, oʻlchamlar, qiymatlar va sana har qanday holat oʻzgarishidan oldin tekshiriladi, shuning uchun muvaffaqiyatsiz chaqiruv faylda iz qoldirmaydi; oʻtmishdagi vaqt belgisi istisno chiqaradi.
- **Kichik interfeys ortida deterministik natija.** Fayl barcha platformalarda baytma-bayt bir xil chiqadi; ichki holat pimpl ortiga yashirilgan, uchinchi tomon bogʻliqliklari yoʻq.

## Muhandislik

- Linux, Windows va macOS uchun CI: GoogleTest va etalon fayl bilan baytma-bayt solishtirish; alohida vazifa hammasini sanitayzerlar ostida ishga tushiradi.
- CIdan oʻtgan har bir kommit semantik versiya tegi va oldindan yigʻilgan kutubxonalar bilan GitHub Release oladi.
- CMake loyihasiga `CPMAddPackage` orqali ulanadi; README faylida u pyvcd va cpp-vcd-tracer bilan imkoniyatlar boʻyicha birma-bir solishtirilgan.
