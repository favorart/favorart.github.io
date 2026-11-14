---
title: "Interpreter sa podesivom sintaksom"
summary: "Diplomski projekat sa osnovnih studija – višeplatformski interpreter čije se ključne reči i gramatika mogu podešavati."
source: favorart/IPL@master:docs/ru/README.md
source_lang: ru
source_hash: b2ca507e
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
# Interpreter za interpretirani programski jezik sa podesivom sintaksom

[Golikov Kiril Anatoljevič](https://github.com/favorart)

Mentor: [Alisejčik Pavel Aleksandrovič](http://intsys.msu.ru/staff/aliseychik/){: hreflang=ru }

MGU „M. V. Lomonosov“

Mehaničko-matematički fakultet

Katedra MaTIS

2013

UDK: 004.432.2

*Ključne reči:* IPL, interpretirani programski jezik, podesiva sintaksa, 
interpreter, prirodni jezik, leksički analizator, sinonimi, regularne reči.


## Apstrakt

Projekat interpretiranog programskog jezika koji olakšava razumevanje formalnog matematičkog algoritma, 
a razvoj novog algoritma čini efikasnijim, 
zahvaljujući pojednostavljenju sintakse i približavanju leksičkih oblika programskog jezika onima koji su korisniku prirodni. 
Aktuelnost teme: velika složenost izvornog koda softvera u praksi.


## Uvod

U radu se razmatra prototip programskog jezika koji pojednostavljuje komunikaciju naručioca sa programerom. 
Iako su načini te komunikacije odavno uhodani, na primer, postoje šeme, UML dijagrami i dr., oni nisu idealni – ima prostora za napredak. 
Cilj ovog rada je olakšavanje čitanja složenog izvornog koda programa, približavanjem programskog jezika prirodnom jeziku. 
Ideja rada je da se obezbedi interfejs za interakciju čoveka sa računarom bez specijalnih znakova “}_$<<;”, 
tj. da računar govori jezikom čoveka, a ne obrnuto. 
Smatram da treba težiti tome da svako može da reši svakodnevni programski zadatak 
jednostavno izdajući komande na maternjem jeziku, i da za to ne bude potrebno tehničko znanje.

Ideja podrazumeva programski jezik čiji bi kod čitaocu delovao razumljivo i prirodno, 
bez potrebe za dodatnom dokumentacijom i komentarima 
(na kraju je ispalo da pisanjem koda treba da se bavi profesionalac koji razume principe funkcionisanja sintakse). 
Jezik je dobio naziv – *interpretirani programski jezik* ili IPL.

Jezik ostvaruje sledeće ciljeve i zadatke:

*	*Cilj – algoritam*: nema potrebe za navođenjem iscrpnih detalja koji otežavaju razumevanje algoritma. Visok nivo apstrakcije.
*	*Kod se predstavlja kao formalni matematički tekst*; tekstu se takav izgled daje rečima za redosled i sumiranje, kao i mogućnošću korišćenja ugnežđenih numerisanih tačaka i podtačaka.
*	*Kod razumljiv na prvi pogled*. Interpreter omogućava izmenu registrovanih reči i operacija u skladu sa navikama i sklonostima pisca pri pisanju i čitaoca pri čitanju.
*	*Kod se može lokalizovati, a sintaksa prilagoditi lokalizaciji*. Izmene izgleda koda sve do mogućnosti pisanja programa na maternjem jeziku (nejasne konstrukcije mogu postati jasnije u kontekstu). Jezik podstiče pravilna, razvijena imena podrškom ustaljenih sintagmi prirodnog jezika.
*	*Kod je nalik interfejsu*. Naručilac bi po analogiji mogao i sam da ispravi kod.
*	*Kod radi ono što treba da radi i ne radi ništa što ne treba*. Naručilac se može i sam uveriti da li projekat programa zadovoljava njegove zahteve ili ne.

Osobine jezika IPL:

*	leksički analizator koji uzima u obzir sintagme u imenima; 
*	promenljiva azbuka i skup regularnih reči; 
*	sintaksa jezika podesiva prema sklonostima korisnika; 
*	jednostavna i razumljiva semantika; 
*	inteligentni tipovi za skladištenje podataka; 
*	ugrađena sredstva za optimizaciju izvršavanja.

IPL nas približava rešavanju sledećih zadataka:

*	udobno i brzo upoznavanje novog programera sa izvornim kodom;
*	olakšano održavanje softverskih proizvoda;
*	poverenje korisnika u program;
*	bolje međusobno razumevanje programera i naručioca.

Rad se sastoji od uvoda, u kom je data analiza osnovnih ideja i formulisan cilj rada; 
tri dela: demonstracije podesive sintakse jezika, funkcionisanja i implementacije interpretera IPL; 
i zaključka, u kom su sumirani rezultati rada na projektu.

**Listing 1.1.**

![1](https://github.com/favorart/IPL/assets/9784285/09371315-ff99-499d-b85c-f48d39dc301b)

_____________________

## 1. Podesiva sintaksa

Ideja stvaranja interpretiranog programskog jezika bila je da se korisnicima omogući da definišu sintaksu 
prema svojim sklonostima i navikama (listing 1.1). 
Blokovi deklaracije promenljivih mogu se nalaziti bilo gde u programu. U listingu 1.2 prikazane su varijante sintakse:

**Listing 1.2.**

![2](https://github.com/favorart/IPL/assets/9784285/805a65af-e821-4e13-b60d-33deb87c962a)

*Aritmetički izrazi*. Pri pisanju koda sa podešavanjem bez eksplicitnih separatora, 
izrazi se logički razdvajaju u skladu sa intuitivnim razumevanjem. 
Algebarski izraz se smatra završenim ako zaredom slede elementi koji nisu operatori jezika: 

$$ a=1+2 \hspace{10pt} [;] \hspace{10pt} b=2+4 $$

U `interpreter.Syntax` postoje podešavanja (listing 1.3) koja zadaju varijacije pisanja jezičkih konstrukcija. 

**Listing 1.3.**

![3](https://github.com/favorart/IPL/assets/9784285/70704cd9-32fc-41fc-bca1-c6f9d7ea21c9)


## 2. Funkcionisanje

Interpretacija se sastoji od tri faze:

*Leksička analiza* - izdvajanje atoma iz teksta i sastavljanje liste atomskih reči, 
uz preskakanje neregistrovanih simbola i komentara.

*Sintaksna analiza* - izdvajanje izraza iz liste atoma i 
pretvaranje aritmetičkih izraza u poljsku notaciju uz uvažavanje prioriteta operacija, 
podudarnosti tipova i dostupnosti funkcija.

*Izvršavanje* metodom rekurzivnog spusta po listi; 
povratne vrednosti funkcija koriste se kao parametri funkcija više u rekurziji.

*Čitanje i upisivanje prekompajliranog bajtkoda*. 
Pri pokretanju skripte interpreter proverava da li u tekućem folderu postoje gotove prekompajlirane datoteke. 
Ako postoje, interpreter preskače faze leksičke i sintaksne analize koda, 
kao i konfigurisanje sintakse, i prelazi neposredno na izvršavanje. 
Tako se postiže veća brzina.


### 2.1. Prekompajliranje u bajtkod

Programer piše IPL skriptu u tekstualnoj datoteci u skladu sa svojom konfiguracijom interpretera 
i dobija datoteku `.ipl` (interpreted pre-compiled). 
Pri izvršavanju datoteke u memoriji interpretera stvara se prekompajlirana verzija izvornog koda programa, 
razumljiva samo interpreteru.
Prekompajliranje stvara tri datoteke sa podacima i datoteku sa bajtkodom:

		<script name>.ipc.constants.dat
		<script name>.ipc.variables.dat
		<script name>.<conf>.ipc.reg_words.dat
		<script name>.ipc

Pri stvaranju bajtkoda odbacuju se svi blokovi deklaracije promenljivih, 
i stvara se posebna heš-tabela namenjena čuvanju početnih vrednosti promenljivih – 
ona se upisuje u `variables.dat`.

Na početku čitanja porede se heševi `{1}` u datoteci bajtkoda i u izvornoj datoteci programa koji se izvršava. 
Dalje se datoteka sastoji od trojki četvorobajtnih brojeva koje određuju kod. 
Prva trojka je lista najvišeg nivoa, koja sadrži sve izraze i blokove koda. 
Zatim slede njeni elementi itd. – program se rekurzivno ugnežđuje (tabela 2.1).

**Tabela 2.1.**

| zaglavlje datoteke [32 bajta]                 |
|:---------------------------------------------:|
| sha256 heš-suma datoteke sa izvršnom skriptom |

| tip atoma                     | pomeraj u tabeli    | pomeraj u lancu       |                   |
|:-----------------------------:|:-------------------:|:---------------------:|:------------------|
|u kojoj heš-tabeli se traži    |od početka heš-tabele|na elementu heš-tabele |
| [ sizeof (int) ]              | [ sizeof (int) ]    | [ sizeof (int) ]      |
| PreComp                       | 0                   | broj elemenata        |izraz jezika (lista)
| Constant                      | 476                 | 0                     |vrednost konstante
| Variable                      | 165                 | 0                     |promenljiva jezika
| RegWord                       | 634                 | 2                     |regularna reč jezika
| ...                           | ...                 | ...                   |


### 2.2. Faza leksičke analize

Kao što je rečeno, radi veće preglednosti algoritma IPL koristi sinonime regularnih reči i identifikatore 
sastavljene od nekoliko *rečnih sastavnica* (tako ćemo zvati reči prirodnog jezika, da bismo izbegli zabunu), 
a neprirodni prefiksi i simboli nisu dozvoljeni. Zbog toga je mehanizam leksičke analize interpretera 
napisan tako da mora da pogađa na osnovu redosleda reči u izrazu jezika i iz konteksta. 
Analiza teksta odvija se u dve etape: najpre se bajtovi datoteke na disku 
(`TODO: unicode još nije implementiran, rad sa stringovima odvija se u ASCII-ju`) 
grupišu u proste sastavnice reči, koje se svode na *normalizovani oblik*. 
Njihova lista prosleđuje se etapi iznad, gde se od njih, ako ih ima dovoljno, konstruišu *atomi* jezika, 
a u suprotnom se ponovo poziva analizator prvog nivoa. 
Rezultat leksičke analize je sekvencijalna lista atoma (sl. 2.1):

**Sl. 2.1.** `ipl_list_pmv list_of_atoms`

![2 1](https://github.com/favorart/IPL/assets/9784285/5bf1d652-95df-426b-90d2-7b09e57d59d4)

Analizator se podešava pomoću *konfiguracionih datoteka*. 
Svi simboli zadaju se u datoteci podešavanja azbuke 
(`<conf>_charset.txt`, gde `<conf>` zadaje korisnik, na primer `eng` ili `rus`). 
U njoj se simboli dele na 5 disjunktnih klasa: slova, znaci, cifre, simbol navodnika i simbol decimalne tačke. 
Simbole zadaje korisnik i mogu biti proizvoljni – interpreter ne zavisi od konkretnih slova i znakova.

Druga konfiguraciona datoteka je datoteka regularnih reči (`<conf>.txt`). 
Izgleda ovako: jedinstveni identifikator značenja reči (dobijen iz `reg.word.id.txt`), 
iza njega, odvojeni zarezima, slede sinonimi koji označavaju tu regularnu reč, a na kraju neobavezni objašnjavajući komentar. 
Regularne reči su analizatoru poznate tokom izvršavanja.
 Sinonime sinhronizuje sintaksni analizator.


### 2.3. Faza sintaksne analize

Zadaci sintaksnog analizatora su: 

1. korektna obrada varijacija izvornog koda i njihovo svođenje na jedinstven bajtkod;
2. preraspoređivanje instrukcija u skladu sa prioritetima.

Na taj način, izvršilac se bavi samo sekvencijalnim izvršavanjem instrukcija. 

Zadatak (1) je trivijalan i sastoji se u sukcesivnom traženju od leksičkog analizatora sledeće porcije atoma, 
nakon čijeg dobijanja se proverava značenje reči; ako sledeća reč nije dozvoljena, prijavljuje se odgovarajuća greška. 

Zadatak (2) sastoji se u izdvajanju izraza iz liste atoma i pretvaranju aritmetičkih operacija 
u *prefiksnu poljsku notaciju pomoću programskog steka* `{3}`. 
Ovde sintaksni analizator prevodi izraz iz infiksne u prefiksnu notaciju, tj. $(1+2)$ u $(+,1,2)$.

Osim toga, ako tokom rada sintaksni analizator naiđe na predugačke redove i duboka ugnežđenja, 
izdaje upozorenja da su konstrukcije koje je programer napisao možda previše zamršene 
i da će korisniku biti teško da razume taj deo algoritma. 
Na slici 2.2 prikazan je primer uspešno završene faze sintaksne analize u interpreteru IPL za operaciju grananja.

**Sl. 2.2.** Operator grananja u IPL-u.

![2 2](https://github.com/favorart/IPL/assets/9784285/430e7237-9c07-415f-a2d7-78b3b91fec57)

Ukratko, *sintaksa* IPL-a ima sledeće osobine:

*	deklaracija promenljivih vrši se u posebnom bloku;
*	postoji nekoliko alternativnih sintaksi za metode objekata i petlje;
*	u blokovima koda mogu se navesti tačke koje razjašnjavaju strukturu bloka i obezbeđuju stroži smer pogleda;
*	direktiva `resulted`, koja omogućava da bilo koji blok koda vrati rezultat.

U jeziku IPL ne postoje dve vrste *zagrada* uobičajene za programere: *funkcijske* i *strukturne*. 
To je urađeno radi ostvarenja paradigme u kojoj bilo koji blok koda može vratiti vrednost, izjednačavajući se sa izrazom. 
Blok koda može se koristiti čak i unutar parametara funkcije, ako vraća vrednost i ne otežava razumevanje programa.


### 2.4. Faza izvršavanja

Interpreter metodom *rekurzivnog spusta* `{2}` izvršava bajtkod 
prikazan na slici 2.2, koji predstavlja ugnežđene liste atoma. 
Pri izvršavanju instrukcija program se *sažima* – 
izraz koji se obrađuje izvlači se iz liste, a umesto njega upisuje se rezultat ($1+2 \to 3$). 
U strukturi izvršioca izvučeni elementi se ne brišu, 
već se premeštaju iz izraza koji se izvršava u izraz koji ih čuva. 
Na taj način prekompajlirani bajtkod, čija je ispravnost proverena izvršavanjem, 
ostaje dostupan za upis u datoteku ili za korišćenje u petljama i funkcijama. 
Program se završava kada u listi instrukcija za izvršavanje ne ostane nijedan element [1].


## 3. Implementacija

Cigle od kojih se sastoji interpreter jesu strukture `myvar` (listing 3.1); u zavisnosti od vrednosti u njima, 
atomski element jezika može biti znak, regularna reč, konstanta, promenljiva, pa čak i ceo izraz. 
Šta je atom, pokazuju polja enumeratora.

**Listing 3.1.**

![3 1](https://github.com/favorart/IPL/assets/9784285/46fa5a6f-91e1-4ca1-b326-d95c5cc8e87b)

Podaci interpretera čuvaju se u strukturi pod nazivom *tabela imena* (`names_table`). 
Interpreter počinje njenom inicijalizacijom, a završava njenim čišćenjem. 
Tabela čuva podatke potrebne u različitim etapama izvršavanja skripte. 
Na primer, u etapama formiranja leksema i sintakse, kao i važne podatke 
koji su uvek potrebni – rečnike promenljivih, konstanti, regularnih reči i izraza.

Tako se dinamička memorija na ovaj ili onaj način upisuje u ovaj registar, 
čime se garantuje da će sva alocirana memorija biti blagovremeno i u potpunosti oslobođena. 
Tako se rešava problem sakupljanja smeća.


## 4. Tipizacija

U jeziku IPL odlučeno je da se ne koristi *implicitna tipizacija*, 
jer je teško razlikovati implicitnu deklaraciju promenljive od reference na nju i teško je pratiti oblast važenja promenljive u tekstu programa. 
Ali se pritom ne odustaje od *dinamičke tipizacije* [5], da se programer ne bi ograničavao krutom statičkom tipizacijom, 
čime se pružaju pogodnosti interpretiranog jezika, a istovremeno zadržava mogućnost hvatanja grešaka vezanih za tipove podataka. 
Izabrana je *mešovita tipizacija*, tj. pri stvaranju promenljive mora se eksplicitno navesti njen tip, ali postoji mogućnost da se taj tip promeni kad zatreba.

Ugrađeni tipovi jezika prikazani su u tabeli 3.1.

**Tabela 3.1.**

| tip podataka             | opseg vrednosti
|:-------------------------|:-----------------------------------:|
| ceo broj                 | od -2 147 483 647 do 2 147 483 647
| broj u pokretnom zarezu  | 1E-37 do 1E+37
| string                   | niz ASCII znakova
| funkcija                 |
| kontejner                | lista ili niz
| rečnik                   | dinamički analog strukture

IPL podržava modularno programiranje korišćenjem funkcija u posebnim datotekama. 
Sve funkcije su globalne, sve promenljive su lokalne. 
Promenljive se prosleđuju funkciji po vrednosti. 
Implementacija funkcije unutar strukture `myvar` je ceo mali interpreter: 
ima sopstvenu datoteku skripte, sopstveni leksički analizator, sopstveni prekompajlirani kod. 
Deklaracija funkcije je potrebna ako se njena definicija nalazi u drugoj datoteci. 
Ako ime datoteke nije navedeno u deklaraciji, datoteka će se tražiti 
po imenu identičnom imenu funkcije + ekstenzija `.ipl` u podrazumevanom folderu. 

Nemoguće je zamisliti savremeni programski jezik bez *nabrojivih tipova podataka*: 
rečnika i kontejnera. 
Ovi tipovi su ugrađeni u jezgro i imaju uobičajene metode korišćenja. 
Posebnost IPL kontejnera, koji može da čuva elemente bilo kog tipa jedan za drugim, 
jeste to što, u zavisnosti od toga koliko često korisnik koristi određene operacije, 
kontejner sam odlučuje o načinu čuvanja elemenata 
(tip čuvanja može se zadati i unapred) – to može biti dvostruko povezana lista ili kontinualni niz.

Kao što je poznato, niz je efikasan za čitanje sa nasumičnim pristupom, ali neefikasan za nasumično upisivanje. 
Kod liste je obrnuto: umetanje je laka operacija, a za indeksiranje u sredinu treba proći kroz polovinu elemenata. 
Ako se operacije nepogodne za konkretan način čuvanja izvode sistematski, 
ima smisla preći na drugi način čuvanja, uprkos troškovima restrukturiranja. 
Kontejner prati ukupan broj, kao i dužinu serija uzastopnih umetanja i pristupa po adresama. 
Pri svakoj radnji povećavaju se ili smanjuju brojači unutar konkretne instance kontejnera. 
Granične vrednosti odabrane su eksperimentalno.

Tip podataka rečnik (`joint`) je skup parova `key:value`, 
gde su `key` i `value` neki tipovi podataka. 
Vrednost `value` može se dobiti za konstantno vreme po vrednosti `key` iz rečnika, ako je tamo ima. 
U suprotnom biće vraćen ‘otkaz’. 
Rečnici zasnovani na heš-tabelama {4} koriste se kao analog korisničkih tipova (`struct` u jeziku C). 
Takav put je raširen među interpretiranim jezicima, 
jer omogućava da se struktura unije definiše dinamički tokom izvršavanja programa. 


## Zaključak

U ovom radu predstavljeni su rezultati istraživačkog rada na stvaranju interpretera jezika IPL. 
Na primeru teksta u listingu 4.1 demonstriraju se čitljivost koda i mnoge mogućnosti jezika. 
Kao što ste se mogli uveriti iz predstavljenog izvornog koda na IPL-u, 
on nas približava još jedan korak korišćenju prirodnog jezika u programiranju.

**Listing 4.1.** Problem ranca

![4 1](https://github.com/favorart/IPL/assets/9784285/ee554a40-3c85-4684-b2ec-129a0da78021)

_____________________

**Listing 4.2.** Program složenosti $O(n^2)$

![4 2](https://github.com/favorart/IPL/assets/9784285/80204cf2-5f07-492f-9add-cc38e3709e2b)

_____________________

**Listing 4.3.** Program na uzbečkom jeziku

![4 3](https://github.com/favorart/IPL/assets/9784285/8e0f53e5-8e0a-47e4-9c01-8c3bd6e48849)

_____________________

## Spisak korišćene literature

* [1]	Шилдт Г. Язык С для профессиональных программистов. / Born to Code in C. – Osborne, 1989
* [2]	Керниган Б., Ритчи Д. Язык программирования С. / The C Programming Language. – Prentice Hall, 1988
* [3]	[Пример написания простого интерпретатора](http://rsdn.ru/forum/alg/5018812.all){: hreflang=ru }
* [4]	[Сам себе интерпретатор](http://coderszone.info/339-sam-sebe-interpretator.html){: hreflang=ru }
* [5]	[Динамическая типизация данных](http://ru.wikipedia.org/wiki/Динамическая_типизация){: hreflang=ru }


### Korišćeni algoritmi

*	{1}	[Metod izračunavanja SHA256 heš-sume datoteke (Ch. Devine, 2003)](http://patux.net/crypto_programs/hash/sha-2/sha256.c.html){: hreflang=en }
*	{2}	[Metod rekurzivnog spusta](http://en.wikipedia.org/wiki/Recursive_descent_parser){: hreflang=en }
*	{3}	[Konstruisanje prefiksne poljske notacije metodom programskog steka](http://algolist.manual.ru/maths/misc/revpn.php){: hreflang=ru }
*	{4}	Konstruisanje heš-tabela
*	Heš-adresa jednaka ostatku pri deljenju prostim brojem (A. Dumey, 1956)
*	Metod lanaca (H. P. Luhn, 1953)
*	Metod otvorenog adresiranja (probanja) (A. P. Jeršov, 1953), (u stranoj literaturi – G. Amdahl, 1957)
*	{5}	Sortiranja
*	Brzo sortiranje (C. Hoare, 1960), implementacija iz <stdlib.h>
*	Algoritam sortiranja spajanjem za liste (Džon fon Nojman, 1945)
