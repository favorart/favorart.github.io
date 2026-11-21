---
tagline: "ABBYYning ochiq kodli C++ ML freymvorkiga qoʻshgan hissam"
summary: "2022–2024-yillarda ABBYYning C++ ML freymvorkiga yuzdan ortiq qabul qilingan pull request: OpenMP oʻrniga oʻz oqimlar puli, qayta ishlangan xotira dvigateli, umumiy vaznlar ustida koʻp oqimli inferens, ONNX importi."
kind: "Ochiq kodga hissa · C++"
---

[NeoML](https://github.com/neoml-lib/neoml) — ABBYYning chuqur oʻqitish va klassik mashinali oʻqitish uchun ochiq kodli freymvorki: C++ tilida yozilgan, CPU, CUDA, Metal va Vulkan ustida ishlaydi, Python bindinglari va ONNX modellarini import qilish imkoniyati bor. 2022-yil oxiridan 2024-yilgacha ABBYYdagi ishim doirasida unga yuzdan ortiq pull requestim qabul qilindi. Eng yirik ishlar: butun freymvorkda OpenMPdan voz kechib, oʻz oqimlar puliga oʻtish, xotira dvigatelini qayta ishlash va vaznlarning bitta nusxasidan birgalikda foydalanadigan koʻplab oqimlarda inferens.

## Ishning asosiy yoʻnalishlari

- **OpenMP oʻrniga — oʻz oqimlar puli.** CPU hisoblash dvigateli va klassik algoritmlar (gradient boosting, SVM, k-means, optimizatorlar) freymvorkning oʻz oqimlar puliga koʻchdi: endi kutubxona oʻz oqimlarini oʻzi boshqaradi va barcha platformalarda bir xil ishlaydi; birgina yakuniy pull request qariyb ikki ming qatorni oʻchirdi.
- **Xotira.** Refaktoring qilingan xotira dvigateli va stek allokatorlari, xotira limitlari, eng yuqori xotira sarfi statistikasi, baytlardagi chegaraga ega har bir oqimning bufer pullari, oqimlar oʻrtasida maʼlumot uzatish va xotirani kamroq sarflaydigan qatlamlar (jumladan, LoRA).
- **Inferens.** Taqsimlangan inferens: bir nechta oqimdagi tarmoq nusxalari vaznlarni takrorlash oʻrniga ulardan birgalikda foydalanadi.
- **Tezlik.** Kamroq xotira va kamroq transponirlash bilan ishlaydigan konvolyutsiyaning teskari oʻtishi, CUDA sinxronizatsiyalarini kamaytirish, pooling yadrolarida mikrooptimallashtirishlar; baʼzi qatlamlarda MKL JIT matritsa koʻpaytmasi (keyinroq qisman bekor qilingan).
- **CUDA dvigateli.** Reduksiya yadrolari va standart qiymatlardagi xatolarni tuzatish, GPUda LSTMni NaNdan himoyalash.
- **Modellar va ONNX.** Pre-normalizatsiyali transformer enkoderi, gradientni kesish; NeoOnnxda — ikki yoʻnalishli LSTM, 1D transponirlangan konvolyutsiya, qatlam normalizatsiyasini qoʻshni amallar bilan birlashtirish va graf optimizatori.
- **Yigʻish va sifat.** Android va iOS uchun ixcham yigʻma, macOS uchun kross-kompilyatsiya, Visual Studio 2022, CodeQL, yangi testlar va tozaroq ommaviy sarlavha fayllari.

Har bir oʻzgarish kodni koʻrib chiqishdan oʻtgan va barcha qoʻllab-quvvatlanadigan platformalarda ommaviy API barqarorligini saqlashi shart edi.
