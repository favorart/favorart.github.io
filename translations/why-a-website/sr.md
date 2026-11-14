---
title: "Čemu ti sajt?"
summary: "Žena me je pitala čemu mi sajt. Za dve večeri sa Claude-om napravio sam ga i našao odgovor: sto sitnih „ne“ i raščišćavanje u glavi."
source: posts/2026-11-why-a-website/index.md
source_lang: ru
source_hash: 79974efc
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-15
---

– podrugljivo je upitala žena.

Odgovora nisam imao. Imao sam fajl sa biografijom u YAML-u, profil na LinkedIn-u i nejasno hoću nešto lepo, a ne napravljeno na brzu ruku. Posle dve večeri sajt je bio gotov, a i odgovor.

## Nisam znao šta hoću

Došao sam kod Claude-a bez projektnog zadatka. Imao sam samo predstavu o sajtu: topao i savremen, sa sunčanim akcentom.

Claude je postavljao pitanja, a onda nudio varijante: tri mokapa sajta, uz svaku pasus opisa. U jednoj su mi se dopali raspored i navigacija, u drugoj stil, u trećoj animacija. Izabrao sam pastelnu pozadinu i zaobljene uglove, blago sunčano raspoloženje, meni na svakoj stranici i primetno uvećanje slika kad se pređe mišem.

![Jedan od tri mokapa: pastelna pozadina i sunce u centru](img/cmp-a-full.png)

Sunce u centru nije ostalo slučajno. Pre dvadeset šest vekova persijski car Kuruš stvorio je najveće carstvo koje je svet do tada video. Grci su ga zvali Kiros, Kir, i na sluh je to bilo skoro isto kao njihova reč „kirios“, gospodar. Caru je pristajalo. A nešto više od šest stotina godina kasnije Plutarh je zapisao da je Kir dobio ime po suncu, jer Persijanci tako i zovu sunce. Lingvisti Plutarhu ne veruju. A meni se dopada: caru sam skoro imenjak. Tako da u centru sajta sijam ja lično.

## Kako izgleda staklo?

Claude mi je prvo ponudio ono što obično nudi: strogi minimalizam, tamni inženjerski stil u duhu terminala i časopisni prelom sa krupnim naslovima. A ja sam hteo sajt koji ne odaje moj AI slop. Zagledao sam se duboko u sebe i izrekao: staklo, savremene površine, poluprozirne i mat, sa odsjajem.

Zatim smo se dugo mučili sa efektima i pozadinama. Sunce je čas zaslepljivalo i pritiskalo sve oko sebe, čas potpuno nestajalo.

![Sunce: četiri pokušaja](img/anim/10-sun.en.gif)

Ni sa reakcijom na miša nije išlo odmah. Hteo sam baš ono zumiranje slike iz trećeg mokapa.

![1. Odbijeno: kartica se podiže](img/anim/01-lift.en.gif)

![2. Prihvaćeno: slika se uvećava unutar nepomične kartice](img/anim/02-zoom.en.gif)

Zumiranje smo izabrali, ali ja ga nisam video i dvaput sam se žalio da uvećanja kod mene jednostavno nema. Claude je dvaput proveravao stilove, i sve je bilo na mestu. Ispostavilo se da su mi u Windows-u isključeni efekti animacije. Pregledač je pošteno prenosio sajtu molbu da se ne pomera, i sajt se pošteno nije pomerao. Moj sopstveni Windows zabranjivao je da mi se prikaže ono što sam naručio. Sada za one poput mene postoji tiha verzija, gde se slika uvećava malčice i brzo.

![Tiha verzija: malčice i brzo](img/anim/02b-quiet.en.gif)

Najviše muke bilo je sa samim staklom.

![3. Odbijeno: staklo odlazi u stranu](img/anim/03-slide.en.gif)

![4. Korak: staklo se topi celo](img/anim/04-fade.en.gif)

![5. Odbijeno: dijagonala klizi preko slike](img/anim/05-sweep.en.gif)

![6. Korak: dijagonala bledi](img/anim/06-diagfade.en.gif)

Gde će proći dijagonala i koliko je zamućena, rečima se ne može objasniti. Zato je Claude napravio posebnu demo stranicu, gde se devet varijanti kreće istovremeno. Pokrivaju 30, 20 ili 10 procenata slike, a granica im je oštra, srednja ili široka. Gledaš i upreš prstom u onu pravu.

Izabrao sam. A onda shvatio da sam sve vreme hteo obrnuto.

![7. Skoro: providan ugao, ali ne taj](img/anim/07-peekTL.en.gif)

![8. Prihvaćeno: ugao dole desno, kad se pređe mišem staklo se topi celo](img/anim/08-peekBR.en.gif)

## Od linkova do dugmadi

Kako ćemo isticati linkove, i to smo rešili tek iz trećeg pokušaja.

![Linkovi: podvlačenje, marker, pojavljivanje](img/anim/09-links.en.gif)

Ikonica na kartici pregledača – ceo sajt u malom kvadratiću, sa onim istim suncem. Sada nas sunce dočekuje i u pozadini, i na kartici, i u logotipu stranice.

![Ikonica sajta: od narandžastog kvadrata do sunca iza slova](img/favicon-evolution.svg)

Dugme ispod odeljka na početnoj stranici isprva je govorilo samo „Svi tekstovi“ i krilo se, sitno, u uglu. Nije bilo jasno da se iza njega krije još mnogo toga. Sada upadljivo poziva unutra i piše „Svih 12 tekstova“, koliko ih stvarno ima.

Ispod svakog teksta su dva jednaka dugmeta, ali je upadljivo samo „Pošaljite komentar“. Ono poziva onoga ko je dočitao do kraja i skoro se odlučio da napiše nešto. Put nazad do spiska naći će i sam.

## Šta je urađeno ispod haube? I mene zanima!

Tekstovi iz mojih repozitorijuma ne kopiraju se na sajt. Ispravio sam README u repozitorijumu, i ispravila se stranica. Druge verzije nema, pa nema ni šta da se razilazi.

![Kako se sajt sklapa](img/build-scheme.en.png)

Sajt govori engleski, španski, ruski, srpski i uzbečki. Ko je čitao moju biografiju, u ovom skupu prepoznaće mapu.

## Head of Slop Review

Ispod mog imena na početnoj stranici redom se smenjuju šaljive uloge. Jednu sam pošteno maznuo od kolege: šef odeljenja za proveru AI slopa. Ona i opisuje moj posao najtačnije.

Potpis na dnu svake stranice Claude je smislio sam: sajt je napravio Claude dok je čovek birao pastelne boje. Iz njega sam precrtao jednu reč, i to je, rekao bih, moj najveći doprinos tekstovima na sajtu.

Sto sitnih „ne“ – i ispao je sajt kojim sam zadovoljan. Svako je ponešto razjasnilo, ne toliko u sajtu koliko u meni. Šta hoću, saznavao sam odbijajući.

Sitnice poput nijanse sunca ili providnosti panela video sam čim osvežim stranicu: nova verzija se objavljuje sama za minut-dva. Za krupne odluke Claude je pravio demo stranice, gde su sve varijante vidljive odjednom. To me i oduševljava najviše. Osećaj se pretvara u varijantu, varijanta – u odluku, i eto, ta odluka već radi na sajtu.

## Pa čemu mi sajt?

Dok sam ga pravio, shvatio sam koliko toga imam da kažem.

Tekstovi koji su godinama ležali po raznim repozitorijumima. Postovi koji su živeli na LinkedIn-u iza zida prijave. Obeleživači „dočitaću kasnije“, linkovi „trebalo bi to srediti“, nedovršene misli. Sajt me je naterao da sve to rasporedim po policama. Nešto je leglo na stranicu. Nešto sam najzad bacio. Davno otvorena pitanja su se zatvorila.

Sajt se pokazao ne kao izlog, nego kao raščišćavanje u glavi.

Baš sam oduševljen! I'm excited, ¡estoy emocionado! Ja sam kao dete sa novom igračkom. Da sam takvu imao u detinjstvu, nikad i ni za šta na svetu ne bih izašao iz kuće!
