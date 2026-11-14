---
title: "Diskret boshqaruvli robot-qoʻlning nuqtadan nuqtaga harakati"
summary: "Diskret boshqaruvli robot-qoʻlni pozitsiyalash uchun oʻqitish algoritmlari — maʼlum model oʻrniga sinov va xatolar."
source: favorart/robot-hand@master:README.md
source_lang: en
source_hash: ad3388a2
translated: 2026-11-14
translator: Claude
reviewed:            # date of the independent review; the build ignores the file until it is set
---
# Diskret boshqaruvli robot uchun nuqtadan nuqtaga trayektoriya rejimi tizimi

Golikov Kirill

M. V. Lomonosov nomidagi MDU

2016

Kalit soʻzlar: robototexnika, robot-qoʻl, manipulyator, pozitsiyalash, trayektoriya rejimi, gradiyent tushish, mashinali oʻqitish


## ANNOTATSIYA

Ushbu ishda diskret boshqaruvli robot-qoʻlni pozitsiyalash algoritmi taqdim etilgan.
Ishning maqsadi — qoʻl harakatining matematik qonuniyatlari haqida oldindan hech qanday bilimsiz,
«cheksiz» xotiradan foydalanib manipulyatorni pozitsiyalash konsepsiyasining isboti (proof of concept).
Ish natijasi — bir necha oʻqitish bosqichiga ega nuqtadan nuqtaga trayektoriya rejimi algoritmi,
harakatlar maʼlumotlar bazasi va vizualizatsiyali sozlanadigan 2D manipulyator modeli.


## KIRISH

Ushbu tadqiqot manipulyator dinamikasining hech qanday analitik modellarisiz robot-manipulyatorni uning ish fazosining maʼlum chegaralangan sohasida yuqori aniqlik bilan pozitsiyalash mumkinligini tasdiqlaydi.
Robototexnika bugun fan va texnikaning ommabop va jadal rivojlanayotgan sohasi boʻlgani sababli,
har oy turli-tuman qurilmalar paydo boʻlmoqda. Ishlab chiqaruvchilar bu qurilmalar bilan tajribalar oʻtkazib,
ularni imkon qadar tezroq foydalanishga topshirishni xohlaydi. Ushbu ishning dolzarbligi shundaki, u qoʻlda bajariladigan
analitik hisob-kitoblar oʻrniga robotning harakatlar maʼlumotlar bazasidan foydalanib, oʻz-oʻzini ishlatish orqali
«qoʻl-oyoqlarini» boshqarishni avtomatik oʻrganish usulini taklif qiladi.


## BIOLOGIK ASOSLAR

Odamlarning qoʻl-oyoqlari bilan bajaradigan samarali harakatlari ularning miyasida, orqa miyasida va harakatlanayotgan aʼzogacha boʻlgan butun nerv yoʻli boʻylab kechadigan murakkab parallel hisoblashlar natijasidir.
Bundan tashqari, harakat insonning avvalgi harakatlaridan yigʻilgan ulkan tajribaning barchasidan foydalanadi.
Fiziologlar oʻz tadqiqotlari bilan tasdiqlaydiki, ongimiz aslida navbatdagi harakatning rejasi va bajarilishini noldan hisoblamaydi.
U koʻproq xotiramizdagi joriy holatga mos harakatlar maʼlumotlarini yigʻadi va bu harakatlardan bloklar sifatida foydalanib, navbatdagi harakatni mexanik tarzda, oʻylamasdan quradi [9].
Shu bilan birga inson miyasi nervlar va sezgi retseptorlaridan keladigan teskari aloqani real vaqtda qayd etib, mushaklar bajarayotgan boshqaruvni tuzatib boradi.

Kichik bolalar karavot ustida osilgan oʻyinchoqqa yetmay yoki undan oshib ketishi, baʼzan esa harakatni hatto notoʻgʻri yoʻnalishda boshlashi hech kimni ajablantirmaydi.
Robototexnikada ham xuddi shunday kuzatiladi: oʻqitish algoritmi chaqaloq miyasi kabi oʻzi haqida hech narsa bilmaydi va oʻz qoʻl-oyoqlarini harakatlantirib, organizmining tuzilishi va holatini oʻrganadi.
Fiziologlarning taʼkidlashicha, faqat uzoq oʻrganish bosqichidan keyingina chaqaloq koʻrish orqali kutganlarini haqiqiy harakatlar bilan muvofiqlashtira oladi.


## MURAKKABLIK NIMADA?

Robot dinamikasi differensial tenglamalar tizimlari koʻrinishida ifodalanadigan harakat qonunlarini belgilaydi,
ular yuritmalarning faol kuchlarini inersiya kuchi, ogʻirlik kuchi,
ishqalanish va manipulyator boʻgʻinlariga qoʻyilgan boshqa kuchlar bilan bogʻlaydi.
Mexanika formulalari va differensial tenglamalar tizimlarini yechish usullari yaxshi oʻrganilgan boʻlishiga qaramay,
adekvat modelni qurishdagi murakkablik tenglamalarning turli-tuman parametrlari qiymatlarini topishdadir.
Har bir robot uchun alohida hisob-kitoblar oʻtkazish va tajribalar qilish kerak.
Bu yoʻl mehnattalab va qimmat; uni amalga oshirish malakali mutaxassisni talab qiladi.

Robot dinamikasi nomaʼlum boʻlgan sharoitda har bir harakat koʻplab xatolar va tuzatuvchi burilishlarga aylanib ketadi.
Bu effekt bajarilish bosqichini sekinlashtirishdan tashqari, toʻqnashuvlarga va robotning oʻzi hamda manipulyatsiya qilinayotgan obyektlarning shikastlanishiga ham olib kelishi mumkin.
Yoʻl topish va manipulyatorni pozitsiyalashning toʻgʻri amalga oshirilishi harakatga qandaydir «nafislik» bagʻishlaydi:
kerakli holatga silliq va tez yetib borish hamda xatolarning yoʻqligi.
Qoʻl-oyoqlar nafaqat tashqi koʻrinishi inson qoʻli harakatlariga oʻxshashligi nuqtayi nazaridan,
balki operatsiyalarni bajarish samaradorligi va muvofiqligi nuqtayi nazaridan ham tabiiy harakatlanishi kerak.
Shunday algoritm yaratish zarurki, u robotga harakatdan oldin oʻz aʼzosini qayerga siljitish kerakligini
va pozitsiyalash harakati oxiridagi ogʻish belgilangan aniqlik doirasida boʻlishi uchun boshidanoq qanday harakat qilishni tasavvur qilish imkonini bersin.

Manipulyator oʻzini sinab koʻrib, oʻz ishining umumiy tamoyilini tushunib olishi mumkin.
Robotning butun ish fazosini qamrab oluvchi maʼlum trayektoriyalar toʻplamiga ega boʻlib,
u yangi trayektoriyalar haqida xulosa chiqarishi mumkin. Yechim — manipulyator modelini uning har bir ishi orqali iterativ aniqlashtirib borish.
Hajmi va sifati boʻyicha yetarli oʻquv harakatlari tanlanmasi yigʻilgach, qoʻlni boshqarish usuli paydo boʻladi.


## MASALANING QOʻYILISHI

Robot-manipulator toʻsiqlarsiz ish fazosida harakat qilsin va ikkita aylanma boʻgʻinga ega boʻlsin: yelka va tirsak.
Pnevmatik dvigatel robot ushlagichining tekislik boʻylab harakatlanishini taʼminlaydi.
Har bir boʻgʻinga alohida pnevmatik silindr taʼsir qiladi: klapanlar sxemasiga muvofiq uni ochadi yoki yopadi.
Goʻyo ikki juft juftlashgan antagonist-mushak bordek.

**Masala** shundan iborat: *manipulyator dinamikasining fizik modeli nomaʼlum boʻlgan sharoitda shunday boshqaruv taʼsirlari toʻplamlarini topishning optimal vaqtini taʼminlash,*
*ular ushlagich markazini robot ish fazosining qandaydir kichik sohasi ichidagi barcha belgilangan nuqtalarga oldindan berilgan aniqlik (= 1.5 mm) bilan olib borsin*.
**Nishon** — robot ish fazosi ichidagi barcha belgilangan nuqtalarni oʻz ichiga olgan shunday kichik soha.

Ushbu ishda robotning diskret modeli quriladi. «Diskret modellarning oʻziga xos xususiyati — ishlash amalga oshiriladigan diskret vaqt» [7].
Shunday minimal davomiylikdagi boshqaruv taʼsirlari mavjudki, undan qisqaroq signallar kelgan taqdirda ham manipulyator ularni «sezmaydi».
Bundan tashqari, robot uzluksiz fazoda ishlaydi, lekin faqat chekli sondagi harakatlarni bajara oladi.
Talab qilinadigan minimal aniqlikni belgilab olamiz va fazoni shu aniqlikka bevosita bogʻliq ravishda sohalarga boʻlamiz.
Manipulyator ushlagichining xarakterli nuqtasi har doim aynan shu sohalardan birining markazida turadi deb hisoblaymiz.
Qoʻl harakatlanayotganda ushlagich bir sohaning markazidan boshqasiga siljib boradi.

Ushbu ishda manipulyatorni pozitsiyalashning modelli masalasi — «Go» oʻyini.

Robot nishoni — tomoni 30 sm boʻlgan kvadrat shaklidagi oʻyin maydoni (1-rasm).
Toshlar joylashadigan oʻrinlar nishon ichidagi 18x18 tekis panjara, jami 324 nuqta.
Ushlagich aynan shu ajratilgan nuqtalarga tushishi kerak.
Nishon toʻliq ish fazosining manipulyator uning har bir uchiga yeta oladigan joyida joylashgan.

![1](https://github.com/favorart/robot-hand/assets/9784285/ebe578bc-36b1-4662-adf0-91ab48409501)

Har bir harakat **bitta boshlangʻich nuqtadan** bajariladi.

**Robot modelining umumiy boshqaruvi** — $𝑣⃗(𝑡) = (𝑣_1(𝑡), 𝑣_2(𝑡), 𝑣_3(𝑡), 𝑣_4(𝑡))$,
ikkilik koordinatalar vektori, bunda har bir koordinata diskret vaqtning har bir $t$ momentida tegishli mushakka beriladigan signal.

Qoʻlning **mushagi** «bir» olayotgan va joiz holatda turgan butun vaqt davomida **ishlaydi**.
Mushak holati *joiz*, agar:

* ochilish (yopilish)ning maksimal (minimal) burchagiga yetilmagan boʻlsa;
* juft antagonist-mushak faol boʻlmasa;
* zudlik bilan toʻxtash signali kelmagan boʻlsa.

Agar signal «bir»dan «nol»ga oʻzgarsa, mushak harakatni tormozlaydi,
lekin robot-qoʻl inersiya boʻyicha harakatlanishda davom etadi. Tinch holatga erishilganda
robot bu haqda signal beradi, shundan keyin harakatning yakuniy nuqtasini aniqlash mumkin.

Manipulyatorda **teskari aloqa** bor, yaʼni qoʻl oʻz holatini kuzatib boradi va bu maʼlumot har bir vaqtda toʻgʻri.

Virtual manipulyator harakatlarni modellashtiradi va algoritmning toʻgʻriligini tekshiradi;
u ushlagichni barcha faol mushaklar harakat qonunlarining kombinatsiyasiga muvofiq tekislik boʻylab siljitadi.

Juft mushakning **harakat qonuni** (*kadrlash*) — diskret vaqtning har bir kadrida boʻgʻin joriy burchagining siljish qiymati.
Harakat qonuni mushak ishlayotgan vaqtda tezlikning nochiziqli oʻzgarishlarini amalga oshiradi va inersiyani simulyatsiya qiladi.

![2](https://github.com/favorart/robot-hand/assets/9784285/20a7ddbc-2cd0-41d6-ad75-fde4e98f2ce1)

Turli yuritma konstruksiyalari va dvigatellarning turli ish rejimlariga ega mushaklarning harakat qonunlari 2-rasmda koʻrsatilgan.
2-rasmda oʻsuvchi grafiklar dvigatel ishlayotgan vaqtda («bir» olinayotganda) burchak oʻzgarishlarini koʻrsatadi;
kamayuvchi grafiklar inersiyani ifodalaydi.

Robot-qoʻlning **harakat trayektoriyasi** — harakat boshidan oxirigacha bajarilayotganda
ushlagich diskret vaqtning har bir kadrida boʻlib oʻtgan nuqtalarning tartiblangan toʻplami.
Trayektoriya oʻzining *yakuniy nuqtasi* bilan tavsiflanadi. Yakuniy nuqtalari bir xil boʻlgan trayektoriyalar ekvivalent.

**Gradiyent tushish** yakuniy nuqtalari maqsad nuqtasiga eng yaqin boʻlgan bir nechta trayektoriyadan foydalanadi.
Bu trayektoriyalarning boshqaruv taʼsirlari bir-biridan farq qiladi.
Navbatdagi harakatning boshqaruv davomiyligini koʻrsatilgan trayektoriyalar boshqaruvlari orasidagi farqlar chegarasida biroz oʻzgartirish mumkin.
Shunday qilib, bu harakat maqsad tomon toʻgʻri chiziq boʻylab siljiydi. Demak, bu harakatning toʻxtash nuqtasi maqsad nuqtasiga yaqinroq boʻlishi kerak.
Teylor teoremasidan foydalanib, pozitsiyalash algoritmi yetarlicha yaqin nuqtadan maqsad nuqtasiga, oxirgi nuqtasi eng yaqin boʻlgan trayektoriyani
maqsaddagi yakun tomon toʻgʻri chiziq boʻylab ketma-ket siljitib, yetib borishi mumkin.

**Teylor teoremasi**: agar $f(х)$ ratsional funksiya $a$ nuqtada hosilaga ega boʻlsa, u holda u $a$ nuqtada chiziqli approksimatsiyaga ega:

$$ 𝑓(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) + h_1(𝑥 − 𝑎) \tag{1}$$

bu yerda $h_1(𝑥)$ — approksimatsiya xatoligi va $\lim_{𝑥 \to a}{h_1(𝑥)}=0$.

$$ 𝑃_1(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) \tag{2}$$

bu yerda $𝑃_1(𝑥)$ — $𝑓(𝑥)$ funksiyaning $a$ nuqtadagi chiziqli approksimatsiyasi.
$y=P_1(𝑥)$ grafigi $𝑓(𝑥)$ funksiya grafigiga $𝑥=a$ nuqtada oʻtkazilgan urinma chiziqdir [10].


## POZITSIYALASH ALGORITMI

Algoritm uchta oʻqitish bosqichidan iborat, shundan soʻng pozitsiyalash aniq boʻladi.

**Birinchi oʻqitish bosqichida** qoʻlning butun ish fazosi boshlangʻich nuqtadan
yetarlicha katta qamrash qadami bilan harakatlar orqali qamrab olinadi.

Bunda yakuniy nuqtalar bir-biridan bir xil masofada joylashmaydi,
chunki robot oʻz mushaklarining aniq tezlanish funksiyalarini bilmaydi.
Algoritm harakatlarning yakuniy nuqtalari orasida taxminan teng oraliqlarni saqlashga harakat qiladi,
uning urinishlari tezlanish funksiyasi monoton kamaymasligiga asoslanadi.
Qamrash har bir robot mushagining ishlash davomiyligini mustaqil oʻzgartirish orqali amalga oshiriladi.

Bajarilgan barcha trayektoriyalar maʼlumotlar bazasiga yozib boriladi.
Bu maʼlumotlar yordamida ushlagich holatining boshqaruv qiymatlariga bogʻliqligining birinchi yaqinlashuvi chiqariladi.
Bundan tashqari, qoʻl konfiguratsiyasining chegaralari aniqlanadi;
bu boshqaruv chegaralari ushlagich markazini nishondan chiqarib yubormaydi.

**Ikkinchi oʻqitish bosqichi** — nishonni birinchi bosqichdagiga qaraganda
kichikroq qamrash qadami bilan, zichroq trayektoriyalar orqali qamrab olish.

**Uchinchi oʻqitish bosqichi** — maʼlumotlar bazasidan yakuniy nuqtalari maqsad nuqtasining qandaydir atrofida boʻlgan trayektoriyalarni tanlash.
Nuqtalar boshqaruvlarining kompozitsiyasi shunday ketma-ket harakatlar uchun boshqaruv hosil qiladiki, har bir navbatdagi harakat maqsad nuqtasida toʻxtashga yaqinroq boʻladi.

Yaxshi oʻqitilgan robot oʻz qoʻlini berilgan joyga belgilangan aniqlik bilan hech qanday xatosiz pozitsiyalay oladi.


## UCHINCHI OʻQITISH BOSQICHI

1. Agar maqsad nuqtasi atrofida tayanch trayektoriyalar boʻlmasa, algoritm xato bilan chiqadi.
2. Maqsad nuqtasiga yaqinlashib borilayotgan paytda gradiyent tushishning oʻrtachalangan algoritmi ishlaydi.
3. Agar gradiyent boʻyicha yaqinlashish uzilib qolsa, yaʼni u 2D funksiyaning maqsad nuqtasidan farqli lokal minimumlaridan birida turgan boʻlsa,
«chuqurdan sakrab chiqish» va gradiyent boʻyicha yaqinlashish jarayonini davom ettirish uchun «aralashma-algoritm»lardan biri qoʻllaniladi.
4. Agar «aralashma-algoritm» muvaffaqiyatli boʻlsa, yaʼni maqsadga lokal minimumdan koʻra yaqinroq nuqta topilsa,
yana gradiyent tushishning oʻrtachalangan algoritmiga qaytiladi (2-qadam), aks holda boshqa «aralashma-algoritm» qoʻllaniladi (3-qadam).
5. Agar «aralashma-algoritm» muvaffaqiyatsiz boʻlsa, yaʼni lokal minimumda qolishda davom etsa, gradiyent tushishning asosiy algoritmiga oʻtiladi.
6. Maqsad nuqtasiga yaqinlashib borilayotgan paytda gradiyent tushishning asosiy algoritmi ishlaydi.
7. Agar gradiyent boʻyicha yaqinlashish uzilib qolsa, maqsadga erishilgunga qadar barcha yoʻnalishlarni toʻliq saralab chiqish qoʻllaniladi.
8. Agar toʻliq saralash muvaffaqiyatsiz boʻlsa, demak, eng yaqin nuqta maqsad nuqtasidan juda uzoqda.
Bu holda Teylor teoremasining shartlari bajarilmaydi. Algoritmdan chiqiladi.
9. Maqsad oʻrniga maqsad nuqtasining kvadrat atrofidan (aniqlik bilan solishtirsa boʻladigan) tasodifiy nuqta tanlanadi.
Tavsiflangan algoritm yangi nuqta uchun bajariladi. Agar bu nuqta mavjud nuqtalarga yaqinroq boʻlsa,
algoritm unga yaqinlashadi. Yangi nuqtaning tanlanishiga koʻra, u maqsadga ham yaqin.
Endi algoritm shu yangi nuqtadan maqsad nuqtasiga qarab takrorlanadi.
Yo yaqinlashib, muvaffaqiyatga erishiladi, yo boshqa nuqtani sinab koʻrish kerak boʻladi.

Amaliyot shuni koʻrsatdiki, har bir belgilangan maqsad nuqtasiga tushish uchun yangi nuqtani bir necha marta (< 15) tanlash kifoya,
bunda har uchinchi urinish — maqsad nuqtasining oʻzini tekshirish.


## NATIJALAR

Algoritmning **murakkabligi** — robotning har bir maqsad nuqtasiga tushishi uchun yetarli boʻlgan harakatlarining umumiy soni.

**Vaqtni baholash usuli**: yelka oʻzining butun yoʻlini diskret vaqtning 700 taktida, tirsak esa 550 taktida bosib oʻtadi.
Bir takt bir millisekund (1 ms) boʻlsin. Har bir harakat boʻgʻinning toʻliq ochilishi yoki yopilishini talab qilishidan yiroq.
Qoʻlning bitta harakati taxminan yarim soniyada bajariladi, qoʻlni boshlangʻich nuqtaga qaytarish uchun ham yana shuncha vaqt kerak.
Shunday qilib, ushlagichni borib-kelishiga oʻrtacha *bir soniya* vaqt sarflanadi.

Tavsiflangan algoritmning turli parametrlar bilan ishlash natijalari 1–4-jadvallarda keltirilgan.
Bu jadvallarda turli harakat qonunlariga ega modellar uchun murakkablik va oʻqitish vaqti natijalari berilgan:

### **MotionLaw**: *ContinuousAcceleration & ContinuousDeceleration*

1-jadval

| Bosqich | Murakkablik | Qamrash qadami | Oʻrt. harakatlar soni | Maqsad nuqtalariga tushish | Vaqt        |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1359 harakat | 18.75 mm      | 1             | 1.8%            | 23 daqiqa
| 2     | -          | -             | -             | -               | -
| 3     | 6796 harakat | -             | 21            | 100%            | 114 daqiqa
| Jami | 8155 harakat |               |               | 100%            | 2.17 soat

2-jadval

| Bosqich | Murakkablik | Qamrash qadami | Oʻrt. harakatlar soni | Maqsad nuqtalariga tushish | Vaqt        |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1359 harakat | 18.75 mm      | 1             | 1.8%            | 23 daqiqa
| 2     | 4288 harakat | 5.625 mm      | 1             | 28.7%           | 72 daqiqa
| 3     | 2973 harakat | -             | 10            | 100%            | 50 daqiqa
| Jami | 8620 harakat |               |               | 100%            | 2.25 soat

### **MotionLaw**: *ContinuousSlowAcceleration & ContinuousDeceleration*

3-jadval

| Bosqich | Murakkablik | Qamrash qadami | Oʻrt. harakatlar soni | Maqsad nuqtalariga tushish | Vaqt        |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1455 harakat | 18.75 mm      | 1             | 0.3%            | 25 daqiqa
| 2     | -          | -             | -             | -               | -
| 3     | 4563 harakat | -             | 14            | 100%            | 77 daqiqa
| Jami | 6018 harakat |               |               | 100%            | 1.42 soat

4-jadval

| Bosqich | Murakkablik | Qamrash qadami | Oʻrt. harakatlar soni | Maqsad nuqtalariga tushish | Vaqt        |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1455 harakat | 18.75 mm      | 1             | 0.3%            | 25 daqiqa
| 2     | 4217 harakat | 5.625 mm      | 1             | 23.1%           | 71 daqiqa
| 3     | 2973 harakat | -             | 5             | 100%            | 28 daqiqa
| Jami | 8645 harakat |               |               | 100%            | 2.7 soat

* **Oʻrt. harakatlar soni** — bitta maqsad nuqtasiga tushish uchun zarur boʻlgan harakatlarning oʻrtacha soni.


## XULOSA

Konsepsiyani isbotlash uchun qurilmalarning turli xil amalga oshirilishlarini simulyatsiya qilish imkonini beruvchi diskret boshqaruvli manipulyatorning 2D modeli qurildi,
shuningdek, robot modeli bajargan harakatlar maʼlumotlar bazasi yaratildi va pozitsiyalash algoritmi dasturlashtirildi.
Ushbu ish robotni pozitsiyalash uchun oldindan oʻrganilgan trayektoriyalardan foydalanish kifoya ekanini koʻrsatdi.

Ishning natijasi, shuningdek, oʻqitish jarayonining umumiy vaqtini baholash, nishonni belgilangan aniqlik bilan qamrab olish uchun zarur harakatlar soni,
hamda aniq pozitsiyalash uchun yetarli boʻlgan maʼlumotlar bazasining minimal hajmini baholashdir.
Oʻqitish algoritmi barcha berilgan nuqtalarga oʻrtacha 15 tadan kam harakat bilan tushishga muvaffaq boʻldi.
Algoritmni toʻliq oʻqitish taxminan 2.5 soat talab qiladi.


## KATTA MAQSAD

Vazifa muayyan robotni samarali boshqarish bilan cheklanib qolmaydi.
Bir robotni oʻqitish natijalarining katta qismidan boshqa shunga oʻxshash manipulyatorlarni tezroq oʻqitish uchun foydalana olish istaladi.
(Amalda bir xil turdagi, hatto bitta texnologiya boʻyicha bitta dastgohda tayyorlangan manipulyatorlar ham pozitsiyalashda mutlaq bir xil boʻla olmaydi,
chunki ularning ishonchliligiga taʼsir qilmaydigan moslash va yigʻishdagi nozik farqlar mavjud.)
Bir robotning maʼlumotlar bazasiga boshqalar toʻplagan tajribani ham kiritish istaladi.


## ADABIYOTLAR

1. Russell S., Norvig P. - Artificial Intelligence: A Modern Approach. – 2nd ed. – New Jersey: Prentice Hall, 2003. – 985 c. – ISBN 0-13-790395-2.
2. ГОСТ 25686-85 Манипуляторы, автооператоры и пром. роботы. Термины и определения // М:ИПК Издательство стандартов, 1988. – 6 с. 10
3. ГОСТ 26050-89 Роботы промышленные. Общие технические требования // М:ИПК Издательство стандартов, 1995. – 16 с.
4. Андре П., Кофман Ж.-М., Лот Ф., Тайар Ж.П. - Конструирование роботов / пер. с фр. – М.: Мир, 1986. — 360 с., ил.
5. Бурдаков С.Ф. и др. - Проектирование манипуляторов промышленных роботов и роботизированных комплексов: Учеб. пособие для студ. вузов, обучающихся по спец. «Робототехнические системы» — М.: Высш. шк.,1986. — 264 с.: ил.
6. Василенко Н.В., Никитин К.Д., Пономарёв В.П., Смолин А.Ю. - Основы Робототехники / Под ред. Никитина К.Д. – Томск: "Радио и связь" МГП «РАСКО», 1993. — ISBN 5-88276-044-5.
7. Кудрявцев В.Б., Алешин С.В., Подколзин А.С. - Введение в теорию автоматов – М.: Наука. Гл. ред. физ.-мат. лит., 1985. – 320 с.
8. Никифоров С.О., Мархадаев Б.Е., Сумкин А.Г. - Экстремальные свойства стационарных движений двухшарнирного манипулятора // Изд. СО АН СССР, 1985. - №6. – Вып. .3. Сер. техн. наук,- 99 с.
9. Физиология человека: Учебник / Под ред. Покровского В.М., Коротько Г.Ф. - 2-е изд., перераб. и доп. - М.:Медицина, 2003. – 656 с.. ил. – (Учеб.лит. Для студ. мед. вузов). — ISBN 5-225-04729-7.
10. [Linear approximation - Wikipedia](https://en.wikipedia.org/wiki/Linear_approximation)
11. [Ильва Эллнеби. Моторные движения](http://www.childneurologyinfo.com/sensory-text-breaking3.php)
12. [Тарабарин В.Б. Конспект лекций по курсу ТММ](http://www.tmm-umk.bmstu.ru/lectures)
13. [Golikov K.A. - Learning algorithm of systems with discrete control](http://intsysjournal.ru/pdfs/23-1/Golikov.pdf)
14. [Golikov K.A. - Learning systems with descrete control](http://intsysjournal.ru/pdfs/22-4/Golikov.pdf)


### MANBA KODI

[C++dagi manba kodi GitHubda mavjud](https://github.com/favorart/robot-hand/)
