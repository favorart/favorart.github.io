---
title: "Sozlanadigan sintaksisli interpretator"
summary: "Bakalavrlik loyihasi — kalit soʻzlari va grammatikasini sozlash mumkin boʻlgan kross-platformali interpretator."
source: favorart/IPL@master:docs/ru/README.md
source_lang: ru
source_hash: 5b3a6762
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---
# Sozlanadigan sintaksisli interpretatsiya qilinadigan dasturlash tili uchun interpretator

[Golikov Kirill Anatolyevich](https://github.com/favorart)

Ilmiy rahbar: [Aliseychik Pavel Aleksandrovich](http://intsys.msu.ru/staff/aliseychik/){: hreflang=ru }

M. V. Lomonosov nomidagi MDU

Mexanika-matematika fakulteti

MaTIS kafedrasi

2013

UDK: 004.432.2

*Kalit soʻzlar:* IPL, interpretatsiya qilinadigan dasturlash tili, sozlanadigan sintaksis,
interpretator, tabiiy til, leksik analizator, sinonimlar, muntazam soʻzlar.


## Annotatsiya

Sintaksisni soddalashtirish va dasturlash tilining leksik shakllarini foydalanuvchi uchun tabiiy shakllarga yaqinlashtirish hisobiga
formal matematik algoritmni tushunishni osonlashtiradigan, yangi algoritm ishlab chiqishni esa samaraliroq qiladigan
interpretatsiya qilinadigan dasturlash tili loyihasi.
Mavzuning dolzarbligi: amaliyotda dasturiy taʼminot dastlabki kodlarining yuqori murakkabligi.


## Kirish

Maqolada buyurtmachining dasturchi bilan muloqotini soddalashtiradigan dasturlash tili prototipi koʻrib chiqiladi.
Bu muloqot usullari allaqachon ishlab chiqilgan boʻlsa-da, masalan, sxemalar, UML-diagrammalar va boshqalar bor, ular mukammal emas, rivojlanish uchun joy bor.
Ushbu ishning maqsadi — dasturlash tilini tabiiy tilga yaqinlashtirish orqali dasturlarning murakkab dastlabki kodlarini oʻqishni osonlashtirish.
Ishning gʻoyasi inson va kompyuter oʻzaro taʼsiri uchun “}_$<<;” kabi maxsus belgilarsiz interfeys taqdim etishdan iborat,
yaʼni kompyuter odam tilida gapirsin, aksincha emas.
Menimcha, har kim maishiy dasturiy vazifani shunchaki ona tilida buyruqlar berib hal qila olishiga
va buning uchun texnik bilimlar talab qilinmasligiga intilish kerak.

Gʻoya kodi oʻquvchiga tushunarli va tabiiy tuyuladigan,
qoʻshimcha hujjatlar va izohlarni talab qilmaydigan dasturlash tilini nazarda tutadi
(natijada kod yozish bilan baribir sintaksisning ishlash tamoyillarini tushunadigan professional shugʻullanishi kerak boʻlib chiqdi).
Til *interpretatsiya qilinadigan dasturlash tili* yoki IPL deb nomlandi.

Til quyidagi maqsad va vazifalarni amalga oshiradi:

*	*Maqsad — algoritm*: algoritmni tushunishni qiyinlashtiradigan barcha mayda tafsilotlarni aniqlashtirishga ehtiyoj yoʻq. Abstraksiyaning yuqori darajasi.
*	*Kod formal matematik matn sifatida taqdim etiladi*: matnga ketma-ketlik va xulosa soʻzlari hamda ichma-ich raqamlangan bandlar va kichik bandlardan foydalanish imkoniyati orqali shunday koʻrinish beriladi.
*	*Bir qarashda tushunarli kod*. Interpretator roʻyxatga olingan soʻzlar va amallarni yozayotgan muallif va oʻqiyotgan kitobxonning odatlari hamda afzalliklariga muvofiq oʻzgartirish imkonini beradi.
*	*Kodni lokalizatsiya qilish va sintaksisni lokalizatsiyaga moslashtirish mumkin*. Kodlarning tashqi koʻrinishini oʻzgartirish, hatto dasturlarni ona tilida yozish imkoniyatigacha (tushunarsiz konstruksiyalar kontekstda tushunarliroq boʻlishi mumkin). Til tabiiy tildagi turgʻun soʻz birikmalarini qoʻllab-quvvatlash orqali toʻgʻri va batafsil nomlarni ragʻbatlantiradi.
*	*Kod interfeysning bir koʻrinishidir*. Buyurtmachi oʻxshatish orqali kodni oʻzi tuzatib qoʻya olardi.
*	*Kod qilishi kerak boʻlgan ishni qiladi va qilmasligi kerak boʻlgan hech narsani qilmaydi*. Buyurtmachi dastur loyihasi uning talablariga javob berish-bermasligiga oʻzi ishonch hosil qila oladi.

IPL tilining xususiyatlari:

*	nomlardagi soʻz birikmalarini hisobga oluvchi leksik analizator;
*	oʻzgartiriladigan alifbo va muntazam soʻzlar toʻplami;
*	foydalanuvchi afzalliklariga moslashtiriladigan til sintaksisi;
*	sodda va tushunarli semantika;
*	maʼlumotlarni saqlashning intellektual turlari;
*	bajarilishni optimallashtirishning oʻrnatilgan vositalari.

IPL bizni quyidagi vazifalarni hal qilishga yaqinlashtiradi:

*	yangi dasturchi tomonidan dastlabki kodlarni qulay va tez oʻrganish;
*	dasturiy mahsulotlarni qoʻllab-quvvatlashni osonlashtirish;
*	foydalanuvchining dasturga ishonchi;
*	dasturchi va buyurtmachi oʻrtasidagi oʻzaro tushunishni yaxshilash.

Maqola asosiy gʻoyalar tahlil qilingan va ishning maqsadi shakllantirilgan kirishdan;
uch qismdan: tilning sozlanadigan sintaksisi namoyishi, IPL interpretatorining ishlashi va amalga oshirilishi;
hamda loyiha ustidagi ish yakunlangan xulosadan iborat.

**1.1-listing.**

![1](https://github.com/favorart/IPL/assets/9784285/09371315-ff99-499d-b85c-f48d39dc301b)

_____________________

## 1. Sozlanadigan sintaksis

Interpretatsiya qilinadigan dasturlash tilini yaratish gʻoyasi foydalanuvchilarga sintaksisni
oʻz afzalliklari va odatlaridan kelib chiqib belgilash imkoniyatini berish edi (1.1-listing).
Oʻzgaruvchilarni eʼlon qilish bloklari dasturning istalgan joyida boʻlishi mumkin. 1.2-listingda sintaksis variantlari koʻrsatilgan:

**1.2-listing.**

![2](https://github.com/favorart/IPL/assets/9784285/805a65af-e821-4e13-b60d-33deb87c962a)

*Arifmetik ifodalar*. Kod aniq ajratgichlarsiz sozlama bilan yozilganda
ifodalarning mantiqiy ajralishi intuitiv tushunishga muvofiq sodir boʻladi.
Agar ketma-ket til operatorlari boʻlmagan elementlar kelsa, algebraik ifoda tugallangan hisoblanadi:

$$ a=1+2 \hspace{10pt} [;] \hspace{10pt} b=2+4 $$

`interpreter.Syntax`da til konstruksiyalarini yozish variantlarini belgilaydigan sozlamalar bor (1.3-listing).

**1.3-listing.**

![3](https://github.com/favorart/IPL/assets/9784285/70704cd9-32fc-41fc-bca1-c6f9d7ea21c9)


## 2. Ishlash tamoyili

Interpretatsiya uch fazadan iborat:

*Leksik tahlil* - roʻyxatga olinmagan belgilar va izohlarni tashlab oʻtib,
matndan atomlarni ajratish va atomar soʻzlar roʻyxatini tuzish.

*Sintaktik tahlil* - atomlar roʻyxatidan ifodalarni ajratish va
amallar ustuvorligi, turlar mosligi va funksiyalarning mavjudligini hisobga olib, arifmetik ifodalarni polyak notatsiyasiga oʻgirish.

*Bajarish* roʻyxat boʻylab rekursiv tushish usuli bilan amalga oshiriladi,
funksiyalarning qaytargan qiymatlari rekursiya boʻyicha yuqoridagi funksiyalarning parametrlari sifatida ishlatiladi.

*Oldindan kompilyatsiya qilingan bayt-kodni oʻqish va yozish*.
Skript ishga tushirilganda interpretator joriy papkada tayyor oldindan kompilyatsiya qilingan fayllar bor-yoʻqligini tekshiradi.
Muvaffaqiyatli boʻlsa, interpretator kodni leksik va sintaktik tahlil qilish,
shuningdek, sintaksisni konfiguratsiya qilish fazalarini tashlab oʻtib, toʻgʻridan-toʻgʻri bajarishga oʻtadi.
Shu tariqa tezkorlik oshadi.


### 2.1. Bayt-kodga oldindan kompilyatsiya

Dasturchi IPL skriptini oʻz interpretator konfiguratsiyasiga muvofiq matnli faylda yozadi
va `.ipl` (interpreted pre-compiled) faylini oladi.
Fayl bajarilganda interpretator xotirasida dastur dastlabki kodlarining faqat interpretatorga tushunarli boʻlgan
oldindan kompilyatsiya qilingan versiyasi yaratiladi.
Oldindan kompilyatsiya maʼlumotlar bilan uchta fayl va bayt-kodli fayl yaratadi:

		<script name>.ipc.constants.dat
		<script name>.ipc.variables.dat
		<script name>.<conf>.ipc.reg_words.dat
		<script name>.ipc

Bayt-kod yaratilayotganda oʻzgaruvchilarni eʼlon qilishning barcha bloklari tashlab yuboriladi
va aynan oʻzgaruvchilarning boshlangʻich qiymatlarini saqlash uchun alohida xesh-jadval yaratiladi —
u `variables.dat` fayliga yoziladi.

Oʻqish boshida bayt-kod fayli va bajarilayotgan dastur dastlabki faylining `{1}` xeshlari solishtiriladi.
Keyin fayl kodni belgilaydigan toʻrt baytli sonlar uchliklaridan iborat boʻladi.
Eng birinchi uchlik — barcha ifodalar va kod bloklarini saqlaydigan yuqori darajadagi roʻyxat.
Keyin uning elementlari va hokazo — dastur rekursiv ravishda ichma-ich joylashadi (2.1-jadval).

**2.1-jadval.**

| fayl sarlavhasi [32 bayt]                    |
|:---------------------------------------------:|
| bajariladigan skriptli faylning sha256 xesh-summasi |

| atom turi                     | jadvaldagi siljish  | zanjirdagi siljish    |                   |
|:-----------------------------:|:-------------------:|:---------------------:|:------------------|
|qaysi xesh-jadvalda qidiriladi|xesh-jadval boshidan|xesh-jadval elementida|
| [ sizeof (int) ]              | [ sizeof (int) ]    | [ sizeof (int) ]      |
| PreComp                       | 0                   | elementlar soni       |til ifodasi (roʻyxat)
| Constant                      | 476                 | 0                     |konstanta qiymati
| Variable                      | 165                 | 0                     |til oʻzgaruvchisi
| RegWord                       | 634                 | 2                     |tilning muntazam soʻzi
| ...                           | ...                 | ...                   |


### 2.2. Leksik tahlil fazasi

Yuqorida aytilganidek, algoritm yaqqolroq boʻlishi uchun IPLda muntazam soʻzlarning sinonimlari va
bir nechta *soʻz-tarkibiy qismlar*dan (chalkashlikning oldini olish uchun tabiiy til soʻzlarini shunday ataymiz) iborat identifikatorlar ishlatiladi,
shuningdek, notabiiy prefikslar va belgilarga yoʻl qoʻyilmaydi. Shu sababli interpretatorning leksik tahlil mexanizmi
til ifodasidagi soʻzlar tartibi va kontekstdan taxmin qilish zaruratini hisobga olgan holda yozilgan.
Matn tahlili ikki bosqichda boradi: avval diskdagi fayl baytlari
(`TODO: unicode hozircha amalga oshirilmagan, satrlar bilan ishlash ASCIIda bajariladi`)
soʻzlarning oddiy tarkibiy qismlariga guruhlanadi va ular *normallashtirilgan koʻrinishga* keltiriladi.
Ularning roʻyxati yuqoriroq bosqichga uzatiladi, u yerda, agar yetarli boʻlsa, ulardan til *atomlari* quriladi,
aks holda birinchi darajali analizator yana chaqiriladi.
Leksik tahlil natijasi — atomlarning ketma-ket roʻyxati (2.1-rasm):

**2.1-rasm.** `ipl_list_pmv list_of_atoms`

![2 1](https://github.com/favorart/IPL/assets/9784285/5bf1d652-95df-426b-90d2-7b09e57d59d4)

Analizator *konfiguratsiya fayllari* orqali sozlanib ishlaydi.
Barcha belgilar alifbo sozlamalari faylida beriladi
(`<conf>_charset.txt`, bu yerda `<conf>` foydalanuvchi tomonidan beriladi, masalan, `eng` yoki `rus`).
Unda belgilar 5 ta kesishmaydigan sinfga boʻlinadi: harflar, ishoralar, raqamlar, qoʻshtirnoq belgisi va oʻnlik nuqta belgisi.
Belgilarni foydalanuvchi beradi va ular ixtiyoriy boʻlishi mumkin — interpretator aniq harflar va ishoralarga bogʻliq emas.

Yana bir konfiguratsiya fayli — muntazam soʻzlar fayli (`<conf>.txt`).
U quyidagicha koʻrinadi: soʻz maʼnosining yagona identifikatori (`reg.word.id.txt`dan olingan),
undan keyin vergul bilan shu muntazam soʻzni bildiruvchi sinonimlar, oxirida esa ixtiyoriy tushuntirish izohi.
Muntazam soʻzlar analizatorga bajarilish vaqtida maʼlum boʻladi.
 Sinonimlar sintaktik analizator tomonidan sinxronlanadi.


### 2.3. Sintaktik tahlil fazasi

Sintaktik analizatorning vazifalari:

1. dastlabki kodlar variantlarini toʻgʻri qayta ishlash va ularni yagona bayt-kodga keltirish;
2. instruksiyalarni ustuvorliklarga muvofiq qayta tartiblash.

Shunday qilib, ijrochi faqat instruksiyalarni ketma-ket bajarish bilan shugʻullanadi.

(1) vazifa oddiy boʻlib, leksik analizatordan navbatdagi atomlar ulushini ketma-ket soʻrashdan iborat;
uni olgandan keyin soʻzlar maʼnosi tekshiriladi, agar navbatdagi soʻz yaroqsiz boʻlsa, tegishli xato chiqariladi.

(2) vazifa atomlar roʻyxatidan ifodalarni ajratish va arifmetik amallarni
*dasturiy stek yordamida toʻgʻri polyak notatsiyasiga* `{3}` oʻgirishdan iborat.
Bu yerda sintaktik analizator ifodani infixdan prefix notatsiyaga oʻtkazadi, yaʼni $(1+2)$ ni $(+,1,2)$ ga.

Bundan tashqari, agar ish jarayonida sintaktik analizator haddan tashqari uzun satrlar va chuqur ichma-ichliklarni topsa,
u dasturchi yozgan konstruksiyalar juda chalkash boʻlishi mumkinligi
va foydalanuvchiga algoritmning bu qismini tushunish qiyin boʻlishi haqida ogohlantirishlar beradi.
2.2-rasmda IPL interpretatorida tarmoqlanish amali uchun sintaktik tahlil fazasi muvaffaqiyatli yakunlanganiga misol keltirilgan.

**2.2-rasm.** IPLdagi tarmoqlanish operatori.

![2 2](https://github.com/favorart/IPL/assets/9784285/430e7237-9c07-415f-a2d7-78b3b91fec57)

Natijada IPL *sintaksisi* quyidagi xususiyatlarga ega:

*	oʻzgaruvchilarni eʼlon qilish alohida blokda amalga oshiriladi;
*	obyekt metodlari va sikllar sintaksisining bir nechta muqobil variantlari bor;
*	kod bloklarida blok tuzilishini oydinlashtiradigan va nigohning qatʼiyroq yoʻnalishini taʼminlaydigan bandlarni koʻrsatish mumkin;
*	istalgan kod blokiga natija qaytarish imkonini beruvchi `resulted` direktivasi.

IPL tilida dasturchi uchun odatiy boʻlgan ikki turdagi *qavslar* — *funksional* va *strukturaviy* qavslar yoʻq.
Bu istalgan kod bloki ifodaga tenglashib, qiymat qaytara oladigan paradigmani amalga oshirish maqsadida qilingan.
Kod blokini hatto funksiya parametrlari ichida ham ishlatish mumkin, agar u qiymat qaytarsa va dasturni tushunishni qiyinlashtirmasa.


### 2.4. Bajarish fazasi

Interpretator *rekursiv tushish* `{2}` usuli bilan 2.2-rasmda koʻrsatilgan,
ichma-ich atomlar roʻyxatlaridan iborat bayt-kodni bajaradi.
Instruksiyalar bajarilganda dastur *qisqaradi* —
qayta ishlanayotgan ifoda roʻyxatdan olinadi va uning oʻrniga natija yoziladi ($1+2 \to 3$).
Ijrochi tuzilmasida olinadigan elementlar oʻchirilmaydi,
balki bajarilayotgan ifodadan saqlovchi ifodaga koʻchiriladi.
Shu tariqa bajarish orqali toʻgʻriligi tekshirilgan oldindan kompilyatsiya qilingan bayt-kod
faylga yozish yoki sikllar va funksiyalarda foydalanish uchun ochiq qoladi.
Bajariladigan instruksiyalar roʻyxatida element qolmaganda dastur tugaydi [1].


## 3. Amalga oshirish

Interpretatorni tashkil etuvchi gʻishtchalar — `myvar` tuzilmalari (3.1-listing); ulardagi qiymatlarga qarab
tilning atomar elementi ishora, muntazam soʻz, konstanta, oʻzgaruvchi va hatto butun bir ifoda boʻlishi mumkin.
Atom nima ekanini sanoq maydonlari koʻrsatadi.

**3.1-listing.**

![3 1](https://github.com/favorart/IPL/assets/9784285/46fa5a6f-91e1-4ca1-b326-d95c5cc8e87b)

Interpretator maʼlumotlari *nomlar jadvali* (`names_table`) deb ataladigan tuzilmada saqlanadi.
Interpretator ishini uni ishga tushirishdan boshlaydi va uni tozalash bilan tugatadi.
Jadval skript bajarilishining turli bosqichlarida kerak boʻladigan maʼlumotlarni saqlaydi.
Masalan, leksemalar va sintaksisni shakllantirish bosqichlarida, shuningdek, har doim kerak boʻladigan muhim maʼlumotlarni —
oʻzgaruvchilar, konstantalar, muntazam soʻzlar va ifodalar lugʻatlarini.

Shunday qilib, dinamik xotira u yoki bu tarzda shu reyestrga kiritiladi,
bu esa ajratilgan barcha xotira oʻz vaqtida va toʻliq tozalanishini kafolatlaydi.
Axlat yigʻish muammosi shu tariqa hal qilinadi.


## 4. Turlash

IPL tilida *noaniq turlash*dan foydalanmaslikka qaror qilindi,
chunki oʻzgaruvchining noaniq eʼlon qilinishini unga havoladan ajratish qiyin va dastur matnida oʻzgaruvchining koʻrinish sohasini kuzatish mushkul.
Lekin shu bilan birga, dasturchini qatʼiy statik turlash bilan cheklamaslik,
interpretatsiya qilinadigan til qulayliklarini taqdim etish va maʼlumotlar turlari bilan bogʻliq xatolarni ushlash imkoniyatiga ega boʻlish uchun *dinamik turlash*dan [5] voz kechilmadi.
*Aralash turlash* tanlandi, yaʼni oʻzgaruvchi yaratilganda uning turini aniq koʻrsatish kerak, lekin kerak boʻlganda bu turni oʻzgartirish imkoniyati bor.

Tilning oʻrnatilgan turlari 3.1-jadvalda keltirilgan.

**3.1-jadval.**

| maʼlumot turi            | qiymatlar diapazoni
|:-------------------------|:-----------------------------------:|
| butun son                | -2 147 483 647 dan 2 147 483 647 gacha
| suzuvchi nuqtali son     | 1E-37 dan 1E+37 gacha
| satr                     | ASCII belgilar ketma-ketligi
| funksiya                 |
| konteyner                | roʻyxat yoki massiv
| lugʻat                   | tuzilmaning dinamik analogi

IPL alohida fayllardagi funksiyalardan foydalangan holda modulli dasturlashni qoʻllab-quvvatlaydi.
Barcha funksiyalar — global, barcha oʻzgaruvchilar — lokal.
Oʻzgaruvchilar funksiyaga qiymat boʻyicha uzatiladi.
`myvar` tuzilmasi ichidagi funksiyaning amalga oshirilishi — bu butun bir kichik interpretator:
uning oʻz skript fayli, oʻz leksik analizatori, oʻz oldindan kompilyatsiya qilingan kodi bor.
Funksiyani tavsiflash, agar uning taʼrifi boshqa faylda boʻlsa, zarur.
Agar tavsifda fayl nomi koʻrsatilmagan boʻlsa, fayl sukut boʻyicha papkada
funksiya nomi bilan bir xil nom + `.ipl` fayl kengaytmasi boʻyicha qidiriladi.

Zamonaviy dasturlash tilini *sanab oʻtiladigan maʼlumot turlari*siz —
lugʻatlar va konteynerlarsiz tasavvur qilib boʻlmaydi.
Bu turlar yadroga oʻrnatilgan va odatiy foydalanish metodlariga ega.
Istalgan turdagi elementlarni ketma-ket saqlay oladigan IPL konteynerining xususiyati shundaki,
foydalanuvchi muayyan amallardan qanchalik tez-tez foydalanishiga qarab,
konteyner elementlarni saqlash usulini oʻzi tanlaydi
(konteyner uchun saqlash turini boshidanoq koʻrsatish mumkin) — bu ikki tomonlama bogʻlangan roʻyxat yoki uzluksiz massiv boʻlishi mumkin.

Maʼlumki, massiv tasodifiy kirish rejimida oʻqish uchun samarali, lekin tasodifiy yozish uchun samarasiz.
Roʻyxatda esa aksincha: qoʻshish — yengil amal, oʻrtadagi elementga indeks boʻyicha murojaat qilish uchun esa elementlarning yarmini aylanib chiqish kerak.
Agar muayyan saqlash usuli uchun noqulay amallar muntazam bajarilsa,
qayta shakllantirish xarajatlariga qaramay, boshqa saqlash usuliga oʻtish mantiqan toʻgʻri.
Konteyner umumiy sonni, shuningdek, ketma-ket qoʻshishlar va manzil boʻyicha murojaatlar seriyalarining uzunligini kuzatib boradi.
Har bir navbatdagi amalda muayyan konteyner nusxasi ichidagi hisoblagichlar oshadi yoki kamayadi.
Chegaraviy qiymatlar tajriba yoʻli bilan tanlangan.

Lugʻat maʼlumot turi (`joint`) — `key:value` juftliklari toʻplami,
bu yerda `key` va `value` — qandaydir maʼlumot turlari.
`value` qiymatini, agar u lugʻatda boʻlsa, `key` qiymati boʻyicha konstant vaqtda olish mumkin.
Aks holda ‘rad’ qaytariladi.
Xesh-jadvallar {4} asosidagi lugʻatlar foydalanuvchi turlarining (C tilidagi `struct`) analogi sifatida ishlatiladi.
Bu yoʻl interpretatsiya qilinadigan tillar orasida keng tarqalgan,
chunki birlashma tuzilmasini dastur bajarilishi davomida dinamik ravishda aniqlash imkonini beradi.


## Xulosa

Ushbu maqolada IPL tili interpretatorini yaratish boʻyicha tadqiqot ishining natijalari taqdim etildi.
4.1-listingdagi matn misolida kodning oʻqilishi osonligi va tilning koʻplab imkoniyatlari namoyish etiladi.
Keltirilgan IPL dastlabki kodlaridan ishonch hosil qilganingizdek,
u bizni dasturlashda tabiiy tildan foydalanishga yana bir qadam yaqinlashtiradi.

**4.1-listing.** Ryukzak masalasi

![4 1](https://github.com/favorart/IPL/assets/9784285/ee554a40-3c85-4684-b2ec-129a0da78021)

_____________________

**4.2-listing.** Murakkablik tartibi $O(n^2)$ boʻlgan dastur

![4 2](https://github.com/favorart/IPL/assets/9784285/80204cf2-5f07-492f-9add-cc38e3709e2b)

_____________________

**4.3-listing.** Oʻzbek tilidagi dastur

![4 3](https://github.com/favorart/IPL/assets/9784285/8e0f53e5-8e0a-47e4-9c01-8c3bd6e48849)

_____________________

## Foydalanilgan adabiyotlar roʻyxati

* [1]	Шилдт Г. Язык С для профессиональных программистов. / Born to Code in C. – Osborne, 1989
* [2]	Керниган Б., Ритчи Д. Язык программирования С. / The C Programming Language. – Prentice Hall, 1988
* [3]	[Пример написания простого интерпретатора](http://rsdn.ru/forum/alg/5018812.all){: hreflang=ru }
* [4]	[Сам себе интерпретатор](http://coderszone.info/339-sam-sebe-interpretator.html){: hreflang=ru }
* [5]	[Динамическая типизация данных](http://ru.wikipedia.org/wiki/Динамическая_типизация){: hreflang=ru }


### Foydalanilgan algoritmlar

*	{1}	[Fayl xesh-summasini SHA256 bilan hisoblash usuli (Ch. Devine, 2003)](http://patux.net/crypto_programs/hash/sha-2/sha256.c.html){: hreflang=en }
*	{2}	[Rekursiv tushish usuli](http://en.wikipedia.org/wiki/Recursive_descent_parser){: hreflang=en }
*	{3}	[Dasturiy stek usuli bilan toʻgʻri polyak notatsiyasini qurish](http://algolist.manual.ru/maths/misc/revpn.php){: hreflang=ru }
*	{4}	Xesh-jadvallarni qurish
*	Xesh-manzil tub songa boʻlishdagi qoldiqqa teng (A. Dumey, 1956)
*	Zanjirlar usuli (H. P. Luhn, 1953)
*	Ochiq adreslash (zondlash) usuli (A. P. Yershov, 1953), (xorijiy adabiyotda — G. Amdahl, 1957)
*	{5}	Saralashlar
*	Tezkor saralash (C. Hoare, 1960), <stdlib.h> kutubxonasidagi amalga oshirish
*	Roʻyxatlar uchun birlashtirib saralash algoritmi (J. fon Neyman, 1945)
