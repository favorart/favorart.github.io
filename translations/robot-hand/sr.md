---
title: "Kretanje robotske ruke od tačke do tačke sa diskretnim upravljanjem"
summary: "Algoritmi učenja za pozicioniranje robotske ruke sa diskretnim upravljanjem – pokušaji i greške umesto poznatog modela."
source: favorart/robot-hand@master:README.md
source_lang: en
source_hash: ad3388a2
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
# Sistem kretanja od tačke do tačke za robota sa diskretnim upravljanjem

Kiril Golikov

MGU „M. V. Lomonosov“

2016

Ključne reči: robotika, robotska ruka, manipulator, pozicioniranje, kretanje od tačke do tačke, gradijentni spust, mašinsko učenje


## APSTRAKT

U ovom radu predstavljen je algoritam pozicioniranja robotske ruke sa diskretnim upravljanjem. 
Cilj rada je dokaz koncepta pozicioniranja manipulatora 
korišćenjem „beskonačne“ memorije, bez ikakvog prethodnog znanja o matematičkim principima kretanja ruke. 
Rezultat rada su algoritam kretanja od tačke do tačke sa nekoliko faza učenja, 
baza podataka pokreta i podesivi 2D model manipulatora sa vizuelizacijom.


## UVOD

Ovo istraživanje potvrđuje mogućnost da se robot-manipulator pozicionira sa velikom preciznošću unutar određene ograničene oblasti radnog prostora robota
bez ikakvih analitičkih modela dinamike manipulatora. Pošto je robotika danas
popularna oblast nauke i tehnike u naglom razvoju, svakog meseca pojavljuje se mnoštvo
različitih uređaja. Proizvođači žele da sa tim uređajima izvedu eksperimente i puste ih u rad
što je pre moguće. Aktuelnost ovog rada je u tome što umesto
ručnih analitičkih proračuna nudi način da robot sam automatski nauči
da upravlja svojim „udovima“ kroz sopstveno korišćenje, uz pomoć baze podataka pokreta robota.


## BIOLOŠKE PREMISE

Efikasni pokreti ljudskih udova rezultat su složenih paralelnih izračunavanja koja se odvijaju u mozgu, 
kičmenoj moždini i duž čitavog puta kroz nervna vlakna sve do uda koji se kreće. 
Štaviše, pokret koristi celokupno nagomilano bogato iskustvo prethodnih pokreta čoveka. 
Fiziolozi svojim istraživanjima potvrđuju da naš um zapravo ne izračunava plan i izvođenje sledećeg pokreta od nule. 
On pre sakuplja iz memorije podatke o pokretima koji odgovaraju datom slučaju i, koristeći te pokrete kao blokove, sklapa sledeći pokret mehanički, bez razmišljanja [9]. 
Ljudski mozak pritom u realnom vremenu prima povratne informacije od nerava i čulnih receptora i koriguje upravljanje koje mišići izvršavaju. 

Nikoga ne čudi što mala deca mogu da promaše igračku koja visi iznad krevetca, a ponekad čak i da započnu pokret u pogrešnom smeru. 
Isto se dešava i u robotici: algoritam učenja, poput mozga bebe, ne zna ništa o sebi i istražuje strukturu i stanje sopstvenog organizma pokrećući svoje udove. 
Fiziolozi primećuju da tek posle duge faze učenja beba može da uskladi vizuelna očekivanja sa stvarnim pokretima.


## U ČEMU JE SLOŽENOST?

Dinamika robota utvrđuje zakone kretanja, koji su predstavljeni sistemima diferencijalnih jednačina 
i povezuju pogonske sile aktuatora sa silom inercije, gravitacijom, 
trenjem i ostalim silama koje deluju na segmente manipulatora. 
Iako su formule mehanike i metode rešavanja sistema diferencijalnih jednačina dobro proučene, 
teškoća u konstruisanju adekvatnog modela je određivanje vrednosti mnoštva parametara jednačina. 
Potrebno je sprovesti proračune i eksperimente na svakom robotu pojedinačno. 
Taj put je mukotrpan i skup; njegova realizacija zahteva kvalifikovanog stručnjaka.

Kada je dinamika robota nepoznata, svaki pokret se izrođava u mnoštvo promašaja i korektivnih okretanja. 
Taj efekat ne samo da usporava fazu izvršavanja, već može dovesti i do sudara i oštećenja samog robota i predmeta kojima manipuliše. 
Pravilna realizacija pronalaženja putanje i pozicioniranja manipulatora daje pokretu izvesnu „eleganciju“: 
glatkoću i brzinu u dostizanju zahtevanog položaja i odsustvo promašaja. 
Udovi moraju da se kreću prirodno, ne samo u smislu sličnosti sa izgledom pokreta ljudske ruke, 
već i u smislu efikasnosti i koordinacije pri izvođenju operacija. 
Potrebno je stvoriti takav algoritam koji pre pokreta omogućava robotu da zamisli kuda treba pomeriti ud 
i kako da deluje od samog početka, tako da odstupanje na kraju pokreta pozicioniranja bude u okviru zadate preciznosti.

Isprobavajući se, manipulator može da shvati opšti princip svog funkcionisanja. 
Imajući određeni skup putanja koji pokriva ceo radni prostor robota, 
može da izvodi zaključke o novim putanjama. Rešenje je iterativno precizirati model manipulatora pri svakom njegovom radu. 
Kada se prikupi uzorak trening pokreta dovoljnog obima i kvaliteta, pojaviće se i metod upravljanja rukom.


## POSTAVKA PROBLEMA

Neka robot-manipulator deluje u svom radnom prostoru bez prepreka i neka ima dva rotaciona zgloba: rame i lakat. 
Pneumatski motor obezbeđuje pomeranje hvataljke robota po ploči. 
Zaseban pneumatski cilindar pokreće svoj zglob: otvara ga ili zatvara u skladu sa šemom ventila. 
Kao da postoje dva para uparenih mišića-antagonista.

**Problem** glasi: *pri nepoznatom fizičkom modelu dinamike manipulatora obezbediti optimalno vreme pronalaženja skupova takvih upravljačkih dejstava*
*koja centar hvataljke prevode u sve zadate tačke unutar neke podoblasti radnog prostora robota sa unapred zadatom tačnošću (= 1,5 mm)*. 
**Meta** je takva podoblast radnog prostora robota koja sadrži sve zadate tačke.

U ovom radu konstruiše se diskretni model robota. „Posebnost diskretnih modela je diskretno vreme u kom se odvija funkcionisanje“ [7]. 
Postoje upravljačka dejstva minimalnog trajanja takva da kraće signale manipulator ne bi „osetio“ ni kada bi ih primio. 
Osim toga, robot deluje u kontinualnom prostoru, ali može da izvede samo konačan broj pokreta. 
Fiksirajmo minimalnu zahtevanu preciznost i podelimo prostor na oblasti u direktnoj zavisnosti od te preciznosti. 
Smatrajmo da se karakteristična tačka hvataljke manipulatora uvek nalazi tačno u centru jedne od tih oblasti. 
Dok se ruka kreće, hvataljka se pomera iz centra jedne oblasti u centar druge.

U ovom radu modelni zadatak pozicioniranja manipulatora je igra go.

Meta robota je kvadratna tabla za igru sa stranicom od 30 cm (sl. 1). 
Mesta za postavljanje kamenova čine pravilnu rešetku 18x18 unutar mete, ukupno 324 tačke. 
Hvataljka mora da pogodi te određene tačke. 
Meta se u celosti nalazi u onom delu radnog prostora gde manipulator može da dosegne svako njeno teme.

![1](https://github.com/favorart/robot-hand/assets/9784285/ebe578bc-36b1-4662-adf0-91ab48409501)

Svaki pokret izvodi se iz **jedne početne tačke**.

**Opšte upravljanje modelom robota** je $𝑣⃗(𝑡) = (𝑣_1(𝑡), 𝑣_2(𝑡), 𝑣_3(𝑡), 𝑣_4(𝑡))$,
vektor binarnih koordinata, gde je svaka koordinata signal odgovarajućem mišiću u svakom trenutku diskretnog vremena $t$.

**Mišić ruke deluje** sve vreme dok prima „jedinicu“ i dok je u dozvoljenom stanju. 
Stanje mišića je *dozvoljeno* kada:

* maksimalni (minimalni) ugao otvaranja (zatvaranja) nije dostignut;
* upareni mišić-antagonist nije aktivan;
* nije stigao signal za trenutno zaustavljanje.

Ako se signal promenio sa „jedinice“ na „nulu“, mišić prekida dejstvo, 
ali robotska ruka nastavlja da se kreće po inerciji. Kada se dostigne stanje mirovanja, 
robot to signalizira, posle čega se može utvrditi krajnja tačka pokreta.

Manipulator ima **povratnu spregu**, tj. ruka prati sopstveni položaj, i ta informacija je u svakom trenutku tačna.

Virtuelni manipulator modeluje pokrete i proverava ispravnost algoritma; 
on pomera hvataljku po ravni u skladu sa kombinacijom zakona kretanja svih aktivnih mišića.

**Zakon kretanja** (*kadriranje*) uparenog mišića je vrednost pomeraja tekućeg ugla zgloba u svakom kadru diskretnog vremena. 
Zakon kretanja ostvaruje nelinearne promene brzine tokom delovanja mišića i simulira inerciju.

![2](https://github.com/favorart/robot-hand/assets/9784285/20a7ddbc-2cd0-41d6-ad75-fde4e98f2ce1)

Zakoni kretanja mišića sa različitim konstrukcijama pogona i režimima rada motora prikazani su na slici 2. 
Na slici 2 rastući grafici prikazuju promene ugla tokom rada motora (dok prima „jedinicu“); 
opadajući grafici predstavljaju inerciju.

**Putanja pokreta** robotske ruke je uređeni skup tačaka koje je hvataljka posetila u svakom kadru diskretnog vremena 
tokom izvođenja pokreta od početka do kraja. 
Putanju karakteriše njena *krajnja tačka*. Putanje sa istim krajnjim tačkama su ekvivalentne.

**Gradijentni spust** koristi nekoliko putanja čije su krajnje tačke najbliže ciljnoj tački. 
Upravljačka dejstva tih putanja razlikuju se međusobno. 
Trajanje upravljanja sledećeg pokreta može se malo varirati u granicama razlika u upravljanju navedenih putanja. 
Tako će se ovaj pokret pomeriti duž prave linije ka cilju. Tada bi zaustavljanje ovog pokreta trebalo da bude bliže ciljnoj tački. 
Koristeći Tejlorovu teoremu, algoritam pozicioniranja može da dostigne ciljnu tačku iz dovoljno bliske tačke, uzastopno pomerajući putanju sa najbližom krajnjom tačkom
duž prave linije ka cilju.

**Tejlorova teorema**: ako racionalna funkcija $f(x)$ ima izvod u tački $a$, onda ona ima linearnu aproksimaciju u tački $a$:

$$ 𝑓(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) + h_1(𝑥 − 𝑎) \tag{1}$$

gde je $h_1(𝑥)$ greška aproksimacije i $\lim_{𝑥 \to a}{h_1(𝑥)}=0$.

$$ 𝑃_1(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) \tag{2}$$

gde je $𝑃_1(𝑥)$ linearna aproksimacija funkcije $𝑓(𝑥)$ u tački $a$. 
Grafik $y=P_1(𝑥)$ je tangenta na grafik funkcije $𝑓(𝑥)$ u tački $𝑥=a$ [10].


## ALGORITAM POZICIONIRANJA

Algoritam se sastoji od tri faze učenja, posle kojih pozicioniranje postaje tačno.

U **prvoj fazi učenja** ceo radni prostor ruke pokriva se pokretima 
iz početne tačke sa nekim dovoljno velikim korakom pokrivanja.

Pritom krajnje tačke neće biti na jednakim međusobnim rastojanjima, 
jer robot ne zna tačne funkcije ubrzanja svojih mišića. 
Algoritam pokušava da održi približno jednake razmake između krajnjih tačaka pokreta, 
oslanjajući se na to da funkcija ubrzanja monotono ne opada. 
Pokrivanje se izvodi nezavisnim promenama trajanja rada svakog mišića robota.

Sve izvedene putanje upisuju se u bazu podataka. 
Na osnovu tih podataka izvodi se prva aproksimacija zavisnosti položaja hvataljke od upravljačkih vrednosti. 
Osim toga, određuju se granične konfiguracije ruke, 
tj. granice upravljanja koje ne izvode centar hvataljke izvan mete.

**Druga faza učenja** je pokrivanje mete putanjama
sa manjim korakom pokrivanja, gušće nego u prvoj fazi.

**Treća faza učenja** je izbor iz baze podataka putanja sa krajnjim tačkama u nekoj okolini ciljne tačke. 
Kompozicija upravljanja tih tačaka daje upravljanje za takve uzastopne pokrete da se svaki sledeći pokret zaustavlja bliže ciljnoj tački.

Dobro obučen robot može da postavi ruku na zadato mesto sa propisanom tačnošću bez ijednog promašaja.


## TREĆA FAZA UČENJA

1. Ako u okolini ciljne tačke nema oslonih putanja, algoritam se završava greškom.
2. Dok konvergira ka ciljnoj tački, radi uprosečeni algoritam gradijentnog spusta.
3. Ako se konvergencija gradijenta prekine, tj. algoritam se nalazi u jednom od lokalnih minimuma 2D funkcije 
koji se razlikuje od ciljne tačke, koristi se jedan od „algoritama-primesa“ da bi se „iskočilo iz jame“ 
i nastavio proces konvergencije gradijenta.
4. Ako je „algoritam-primesa“ uspeo, tj. pronađena je tačka bliža cilju od lokalnog minimuma, 
algoritam se vraća na uprosečeni gradijentni spust (korak 2), a u suprotnom koristi se drugi „algoritam-primesa“ (korak 3).
5. Ako „algoritam-primesa“ nije uspeo, tj. algoritam je i dalje u lokalnom minimumu, prelazi se na osnovni algoritam gradijentnog spusta.
6. Dok konvergira ka ciljnoj tački, radi osnovni algoritam gradijentnog spusta.
7. Ako se konvergencija gradijenta prekine, koristi se iscrpna pretraga svih pravaca sve do trenutka kada se cilj dostigne.
8. Ako iscrpna pretraga nije uspela, znači da je najbliža tačka predaleko od ciljne. 
U tom slučaju uslovi Tejlorove teoreme ne važe. Izlaz iz algoritma.
9. Umesto cilja izabrati nasumičnu tačku u kvadratnoj okolini (srazmernoj tačnosti) ciljne tačke. 
Izvršiti opisani algoritam za novu tačku. Ako je ta tačka bila bliža postojećim tačkama, 
algoritam će konvergirati ka njoj. Po načinu izbora, nova tačka je takođe blizu cilja. 
Sada ponoviti algoritam od te nove tačke do ciljne tačke. 
Ili će konvergirati i uspeti, ili će trebati probati drugu tačku. 

Praksa je pokazala da je za pogađanje svake fiksirane ciljne tačke dovoljno nekoliko puta (< 15) izabrati novu tačku, 
pri čemu je svaki treći pokušaj provera same ciljne tačke.


## REZULTATI

**Složenost** algoritma je ukupan broj pokreta robota dovoljan da se pogodi svaka ciljna tačka.

**Metod procene vremena**: rame prelazi ceo svoj put za 700 taktova diskretnog vremena, a lakat za 550 taktova. 
Neka jedan takt bude jedna milisekunda (1 ms). Daleko od toga da svaki pokret zahteva potpuno otvaranje ili zatvaranje zgloba. 
Jedan pokret ruke traje oko pola sekunde, a isto toliko je potrebno da se ruka vrati u početnu tačku. 
Dakle, za pomeranje hvataljke tamo i nazad troši se u proseku *jedna sekunda*.

Rezultati rada opisanog algoritma sa različitim parametrima dati su u tabelama 1–4. 
U tim tabelama navedeni su rezultati složenosti i vremena učenja za modele sa različitim zakonima kretanja:

### **MotionLaw**: *ContinuousAcceleration & ContinuousDeceleration*

Tabela 1

| Faza   | Složenost    | Korak pokrivanja | Prosečan br. pokreta | Pogođenih ciljnih tačaka | Vreme       |
|:------:|:------------:|:----------------:|:--------------------:|:------------------------:|:-----------:|
| 1      | 1359 pokreta | 18,75 mm         | 1                    | 1,8%                     | 23 minuta
| 2      | -            | -                | -                    | -                        | -
| 3      | 6796 pokreta | -                | 21                   | 100%                     | 114 minuta
| Ukupno | 8155 pokreta |                  |                      | 100%                     | 2,17 sati

Tabela 2

| Faza   | Složenost    | Korak pokrivanja | Prosečan br. pokreta | Pogođenih ciljnih tačaka | Vreme       |
|:------:|:------------:|:----------------:|:--------------------:|:------------------------:|:-----------:|
| 1      | 1359 pokreta | 18,75 mm         | 1                    | 1,8%                     | 23 minuta
| 2      | 4288 pokreta | 5,625 mm         | 1                    | 28,7%                    | 72 minuta
| 3      | 2973 pokreta | -                | 10                   | 100%                     | 50 minuta
| Ukupno | 8620 pokreta |                  |                      | 100%                     | 2,25 sati

### **MotionLaw**: *ContinuousSlowAcceleration & ContinuousDeceleration*

Tabela 3

| Faza   | Složenost    | Korak pokrivanja | Prosečan br. pokreta | Pogođenih ciljnih tačaka | Vreme       |
|:------:|:------------:|:----------------:|:--------------------:|:------------------------:|:-----------:|
| 1      | 1455 pokreta | 18,75 mm         | 1                    | 0,3%                     | 25 minuta
| 2      | -            | -                | -                    | -                        | -
| 3      | 4563 pokreta | -                | 14                   | 100%                     | 77 minuta
| Ukupno | 6018 pokreta |                  |                      | 100%                     | 1,42 sata

Tabela 4

| Faza   | Složenost    | Korak pokrivanja | Prosečan br. pokreta | Pogođenih ciljnih tačaka | Vreme       |
|:------:|:------------:|:----------------:|:--------------------:|:------------------------:|:-----------:|
| 1      | 1455 pokreta | 18,75 mm         | 1                    | 0,3%                     | 25 minuta
| 2      | 4217 pokreta | 5,625 mm         | 1                    | 23,1%                    | 71 minut
| 3      | 2973 pokreta | -                | 5                    | 100%                     | 28 minuta
| Ukupno | 8645 pokreta |                  |                      | 100%                     | 2,7 sati

* **Prosečan br. pokreta** je prosečan broj pokreta potreban da se dostigne jedna ciljna tačka.


## ZAKLJUČAK

Da bi se dokazao koncept, konstruisan je 2D model manipulatora sa diskretnim upravljanjem koji omogućava simulaciju različitih izvedbi uređaja, 
napravljena je baza podataka pokreta koje izvodi model robota i isprogramiran je algoritam pozicioniranja. 
Rad je pokazao da je za pozicioniranje robota dovoljno koristiti unapred naučene putanje.

Rezultat rada je i ukupna procena vremena procesa učenja, broja pokreta potrebnih da se meta pokrije sa propisanom tačnošću, 
kao i procena minimalnog obima baze podataka dovoljnog za precizno pozicioniranje. 
Algoritam učenja uspeva da pogodi sve zadate tačke sa u proseku manje od 15 pokreta. 
Celokupno učenje algoritma zahteva približno 2,5 sata.


## VELIKI CILJ

Zadatak se ne svodi na efikasno upravljanje konkretnim robotom. 
Želja je da se većina rezultata učenja jednog robota može iskoristiti za ubrzano učenje drugih sličnih manipulatora. 
(U praksi, manipulatori iste vrste, čak i proizvedeni istom tehnologijom na istoj mašini, ne mogu imati apsolutno identično pozicioniranje 
zbog sitnih razlika u naleganju i montaži, koje ne utiču na njihovu pouzdanost.) 
Želja je da baza podataka jednog robota sadrži iskustvo koje su akumulirali drugi.


## LITERATURA

1. Russell S., Norvig P. - Artificial Intelligence: A Modern Approach. – 2nd ed. – New Jersey: Prentice Hall, 2003. – 985 c. – ISBN 0-13-790395-2.
2. ГОСТ 25686-85 Манипуляторы, автооператоры и пром. роботы. Термины и определения // М:ИПК Издательство стандартов, 1988. – 6 с. 10
3. ГОСТ 26050-89 Роботы промышленные. Общие технические требования // М:ИПК Издательство стандартов, 1995. – 16 с.
4. Андре П., Кофман Ж.-М., Лот Ф., Тайар Ж.П. - Конструирование роботов / пер. с фр. – М.: Мир, 1986. — 360 с., ил.
5. Бурдаков С.Ф. и др. - Проектирование манипуляторов промышленных роботов и роботизированных комплексов: Учеб. пособие для студ. вузов, обучающихся по спец. «Робототехнические системы» — М.: Высш. шк.,1986. — 264 с.: ил.
6. Василенко Н.В., Никитин К.Д., Пономарёв В.П., Смолин А.Ю. - Основы Робототехники / Под ред. Никитина К.Д. – Томск: "Радио и связь" МГП «РАСКО», 1993. — ISBN 5-88276-044-5.
7. Кудрявцев В.Б., Алешин С.В., Подколзин А.С. - Введение в теорию автоматов – М.: Наука. Гл. ред. физ.-мат. лит., 1985. – 320 с.
8. Никифоров С.О., Мархадаев Б.Е., Сумкин А.Г. - Экстремальные свойства стационарных движений двухшарнирного манипулятора // Изд. СО АН СССР, 1985. - №6. – Вып. .3. Сер. техн. наук,- 99 с.
9. Физиология человека: Учебник / Под ред. Покровского В.М., Коротько Г.Ф. - 2-е изд., перераб. и доп. - М.:Медицина, 2003. – 656 с.. ил. – (Учеб.лит. Для студ. мед. вузов). — ISBN 5-225-04729-7.
10. [Linear approximation - Wikipedia](https://en.wikipedia.org/wiki/Linear_approximation){: hreflang=en }
11. [Ильва Эллнеби. Моторные движения](http://www.childneurologyinfo.com/sensory-text-breaking3.php){: hreflang=en }
12. [Тарабарин В.Б. Конспект лекций по курсу ТММ](http://www.tmm-umk.bmstu.ru/lectures){: hreflang=ru }
13. [Golikov K.A. - Learning algorithm of systems with discrete control](http://intsysjournal.ru/pdfs/23-1/Golikov.pdf){: hreflang=ru }
14. [Golikov K.A. - Learning systems with descrete control](http://intsysjournal.ru/pdfs/22-4/Golikov.pdf){: hreflang=ru }


### IZVORNI KOD

[Izvorni kod na C++ dostupan je na GitHub-u](https://github.com/favorart/robot-hand/){: hreflang=en }
