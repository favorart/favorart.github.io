---
title: "vcd-writer: VCD toʻlqin diagrammasi fayllari uchun C++20 kutubxonasi"
summary: "pyvcd kutubxonasining tashqi bogʻliqliklarsiz C++20 porti: Value Change Dump fayllarini (IEEE 1364-2005) har bir qiymat oʻzgarishida xotira ajratmasdan yozadi."
kind: Kutubxona · C++20
---

Value Change Dump (VCD) — apparat simulyatorlari signallarning vaqt oʻtishi bilan qanday oʻzgarishini yozib boradigan matnli format; GTKWave kabi koʻruvchi dasturlar uni toʻlqin diagrammalari koʻrinishida chizadi. **vcd-writer** bunday fayllarni C++ kodidan yozadi: simulyator, emulyator yoki test stendi oʻzgaruvchilarni ichma-ich joylashgan sohalarda (scope) roʻyxatdan oʻtkazadi va ularning oʻzgarishlarini xabar qilib turadi, kutubxona esa istalgan toʻlqin diagrammasi koʻruvchisi ocha oladigan VCD faylini hosil qiladi.

Loyiha 2017-yilda Python kutubxonasi [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd)ning porti sifatida boshlandi va 2026-yilda zamonaviy kutubxonaga aylantirildi.

## Ichida nima bor

- **Standart bandma-band tekshirilgan.** IEEE 1364-2005 standarti (§18.2) boʻyicha toʻrt holatli VCD: sarlavha (`$date`, `$version`, `$timescale`, `$comment`), ichma-ich sohalar, oʻzgaruvchilarning barcha 18 turi, skalyar, vektor, haqiqiy son va satr qiymatlari, `$dumpvars`, `$dumpoff` / `$dumpon`. README faylida nima qoʻllab-quvvatlanishi va nima qoʻllab-quvvatlanmasligi jadvali bor.
- **Har bir oʻzgarishda xotira ajratilmaydi.** Qiymatlar 64 KiB hajmli chiqish buferiga yoziladi; benchmark repozitoriyning oʻzida.
- **Yon taʼsirsiz validatsiya.** Nomlar, oʻlchamlar, qiymatlar va sana har qanday holat oʻzgarishidan oldin tekshiriladi, shuning uchun muvaffaqiyatsiz chaqiruv faylda iz qoldirmaydi; oʻtmishdagi vaqt belgisi istisno chiqaradi.
- **Deterministik natija.** Fayl barcha platformalarda baytma-bayt bir xil chiqadi.
- **Toza interfeys.** Writer obyektining holati pimpl ortiga yashirilgan; uchinchi tomon bogʻliqliklari yoʻq.

## Muhandislik

- GoogleTest, AddressSanitizer va UndefinedBehaviorSanitizer bilan Linux, Windows va macOS uchun CI.
- CIdan oʻtgan har bir kommit semantik versiya tegi va oldindan yigʻilgan kutubxonalar bilan GitHub Release oladi.
- CMake loyihasiga bitta `CPMAddPackage` chaqiruvi bilan ulanadi.
- README faylida u pyvcd va cpp-vcd-tracer bilan imkoniyatlar boʻyicha birma-bir solishtirilgan.

## Bu nima uchun muhim

Kichik kutubxona butun muhandislik siklini koʻrsatish uchun qulay maydon: sinchiklab oʻqilgan standart, notoʻgʻri ishlatish qiyin boʻlgan API, oʻlchangan unumdorlik va qoʻlda bajariladigan qadamlarsiz reliz jarayoni.
