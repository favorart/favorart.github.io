---
title: "Vaš rođendan u ciframa broja π"
summary: "Mala GUI aplikacija u Python-u/Tkinter-u koja pronalazi vaš datum rođenja među 3 milijarde cifara broja π – kasnije prepravljena za veb."
source: favorart/pi-birthday@main:docs/article.md
source_lang: en
source_hash: aa96f51d
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---
# Grafička aplikacija u Python-u

**Srpski** · [English](article.md){: hreflang=en } · [Русский](article.ru.md){: hreflang=ru }

_Članak iz 2018. o prvoj, desktop verziji (Python 2.7 + Tkinter), prvobitno napisan na ruskom. Originalna objava: [VK](https://vk.ru/@33453621-pi-gui-python){: hreflang=ru }. Ceo kod: [legacy/pi.py](../legacy/pi.py); da biste ga danas pokrenuli, koristite [legacy/run.sh](../legacy/run.sh)._

_Nastavak iz 2026. – veb verzija koja ne čuva nijednu cifru broja π: [π čuva sve, pa ja nisam morao da čuvam π](/sr/writing/pi-stores-everything/)._

S vremena na vreme treba da napišem neku malu aplikaciju sa prozorima. Aplikacije obično pišem u C++-u. Nekada sam umesto Qt-a naučio Windows API, jer su moji prozori uvek bili za Windows, a smatram da je nativni interfejs uvek najbolji. Želim da sve izgleda prirodno. WinAPI omogućava da uradiš sve što Windows može, ali mnogo toga mora da se piše ručno, a uvek treba nekih ukrasa i dodataka.

U WinAPI-ju ne možeš mišem da prevlačiš kontrole; Visual Studio nema dizajner za taj sloj **:(** (osim lukavih zaobilaznica sa dijalozima umesto formi). Postoje, naravno, i viši nivoi – MFC i WPF. Ali prvi ima veoma čudnu i zamršenu organizaciju klasa u koju zaista ne želim da se zavlačim. A drugi je odličan u svemu, osim što je C#: ako hoćeš da pišeš u C++-u, moraš da koristiš upravljani kod i pozivaš funkcije .NET framework-a.

Pa dobro… Najčešće je lakše bilo koju aplikaciju napisati u Python-u.

Hajde da vidimo da li je to tačno.

### Tkinter

**Tkinter** je Python paket za rad sa bibliotekom Tk, napisanom u programskom jeziku Tcl. Paket jednostavno prevodi Python kod u Tcl komande.

### Vidžeti

**Vidžet** je element interfejsa (Control u terminologiji WinAPI-ja): objekat napravljen od ugrađenih klasa.

-   `Button` – dugme
-   `Entry` – jednolinijsko polje za unos teksta
-   `Frame` – grupa vidžeta
-   `Label` – oblast prozora koja može da sadrži sliku ili statički tekst
-   `Text` – višelinijsko polje za unos teksta

i drugi.

Svaki GUI sledi paradigmu programiranja vođenog događajima: određeni deo koda izvršava se tek kada se desi određeni događaj.

```c
// the event loop in WinAPI - the most important function of a windowed application
LRESULT CALLBACK WndProc(HWND hWnd, UINT messg, WPARAM wParam, LPARAM lParam)
{
    switch (messg)
    {
    case WM_PAINT: // paint the window
      onWindowPaint(hWnd);
      break;
    case WM_DESTROY: // destroy the window when the close button is clicked
      PostQuitMessage(0);
      break;
    case WM_ERASEBKGND: // some other events
      return 1;
    }
    return DefWindowProc(hWnd, messg, wParam, lParam); // default handling by the OS itself
}
```

### Događaji

Događaji su raznih vrsta: može ih pokrenuti tajmer, korisnik, sistem, sami vidžeti itd. Događaja ima mnogo, i svaki ima podrazumevani ili prazan rukovalac. Kada događaj stigne, izvršava se određeni deo programa. Sopstvena logika obično ide u rukovaoce događajima.

Minimalna aplikacija izgleda ovako:

```python
try:
    import tkinter as tk    # >= python 3.0
except ImportError:
    import Tkinter as tk    # >= python 2.7

root = tk.Tk()  # create the main window
root.mainloop() # start the loop that receives and handles events
```

`mainloop()` sadrži beskonačnu petlju. Kod napisan posle ovog poziva izvršava se tek kada se aplikacija zatvori. Iz petlje se izlazi, na primer, na događaj klika na dugme za zatvaranje.

Opšti plan GUI programa:

-   Napraviti glavni prozor.
-   Napraviti dodatne prozore i vidžete, podesiti ih i dodati vidžete u glavni ili druge prozore.
-   Odrediti događaje od interesa i njihove rukovaoce – tj. gde ide korisnički kod i kako program reaguje.
-   Pokrenuti petlju događaja.

### Podešavanje vidžeta

Napravimo prvi vidžet – statički tekst u prozoru koji korisnik ne može da menja:

```python
tk.Label(root, text="This label")
```

Tekst se ipak može menjati iz koda: umesto parametra `text` poveže se string promenljiva – promena njene vrednosti odmah menja tekst na `Label`-u:

```python
lb_text = tk.StringVar()
lb_text.set("1")
tk.Label(root, textvariable=lb_text, width=10, font=dFont, anchor=tk.NW)
```

Izvor: [legacy/pi.py, redovi 227–230](../legacy/pi.py#L227-L230)

Parametar `font` menja font; unapred sam pripremio veći, čitljiviji font za interfejs:

```python
import tkFont
dFont = tkFont.Font(family="Arial", size=30)
```

Izvor: [legacy/pi.py, red 211](../legacy/pi.py#L211)

Parametar `anchor` određuje poravnanje vidžeta – ovde je to NORTH-WEST, tj. tekst se lepi za gornji levi ugao vidžeta.

Svojstva ne moraju da se zadaju pri stvaranju objekta.

Obratite pažnju da je prvi argument „vlasnik“, „master“ – mesto gde vidžet živi. Ovde bi mogao da se izostavi, jer je podrazumevano `root`. Ali vidžeti ne moraju da stoje direktno na glavnom prozoru (`root`); mogu se smestiti i unutar drugih vidžeta.

### Sopstveni rukovaoci događajima

Funkcije za rukovanje događajima, koje se pozivaju kada se događaj desi, moraju da primaju jedan parametar. Obično se zove `event`.

Metod `bind` povezuje rukovalac sa Tk događajem:

```python
def bt_find_click(event):
    pass

root.bind('<Return>', bt_find_click)
```

Izvor: [legacy/pi.py, red 210](../legacy/pi.py#L210)

Prima ime događaja i funkciju koju treba pozvati. Događaj sa svim svojim parametrima prosleđuje se funkciji kao argument `event`. Ovde je događaj pritisak na taster Enter, zapisan kao string `'<Return>'`.

### Raspoređivanje vidžeta

Očajnički sam pobegao od WinAPI-ja u potrazi za vizuelnim dizajnerom interfejsa. Ispostavilo se da ni Tkinter nema takav ugrađen **:(** Stisnuvši zube, počeo sam da čitam kako programeri žive bez njega i, na moje iznenađenje, rešili su taj problem prilično zgodno i elegantno.

### Menadžeri geometrije

\[Izvor: [Habr](https://habr.com/post/133337/){: hreflang=ru }\]

**1 pack()** je funkcija koja se zove paker, ili menadžer geometrije. Ona odlučuje kako su vidžeti raspoređeni u glavnom prozoru. Paker mora da se pozove za svaki vidžet, inače se vidžet ne prikazuje. Ukupno postoje tri pakera:

pack raspoređuje vidžete u roditeljskom prozoru automatski. Njegovi parametri:

side – sa koje strane se dodaje sledeći element,

fill – da li ga razvući do ivica prozora u nekom pravcu,

expand – da li vidžet treba da ispuni ceo roditeljski element.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').pack(side = 'left')
Button(root, text = '2').pack(side = 'top')
Button(root, text = '3').pack(side = 'right')
Button(root, text = '4').pack(side = 'bottom')
Button(root, text = '5').pack(fill = 'both')
root.mainloop()
```

<img width="134" height="116" alt="1-pack" src="https://github.com/user-attachments/assets/8067aec6-e630-430c-a5fb-5b8891f5f66d" />

**2 grid()** raspoređuje vidžete po mreži. Glavni parametri:

row/column – red/kolona u mreži,

rowspan/columnspan – koliko redova/kolona vidžet zauzima,

sticky – kako se vidžet razvlači kada mu ćelija raste: za koje ivice ćelije (N, W, S, E) se lepi.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').grid(row = 1, column = 1)
Button(root, text = '2').grid(row = 1, column = 2)
Button(root, text = '__3__').grid(row = 2, column = 1, columnspan = 2)
root.mainloop()
```

<img width="137" height="94" alt="2-grid" src="https://github.com/user-attachments/assets/1da19342-4b45-406e-ae00-fb29dfd5bc18" />

**3 place()** postavlja vidžete na zadate koordinate sa zadatim dimenzijama. Glavni parametri: x, y, width, height.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').place(x = 10, y = 10, width = 30)
Button(root, text = '2').place(x = 45, y = 20, height = 15)
Button(root, text = '__3__').place(x = 20, y = 40)
root.mainloop()
```

<img width="139" height="139" alt="3-place" src="https://github.com/user-attachments/assets/f6ecb75e-e579-4d53-a7a9-653519d72954" />

Dok za vidžet ne pozovete paker, on se, naravno, ne prikazuje.

### Zadatak

Sada o primeru o čijoj implementaciji želim da vam pričam.

Postoji hipoteza da je π [normalan broj](http://www.etudes.ru/ru/sketches/normal-number-pi){: hreflang=ru }, tj. da se u njemu može naći bilo koji zadati konačan niz cifara.

Da bismo zadivili decu i odrasle na [festivalu nauke](http://www.festivalnauki.ru){: hreflang=ru }, pozajmili smo ovu [atrakciju](http://www.etudes.ru/ru/sketches/normal-number-pi/){: hreflang=ru }: _unesete svoj datum rođenja, a program vam kaže na kojoj cifri broja π se on može naći_.

Dakle, morali smo da izračunamo π na prilično mnogo cifara, prođemo kroz sve datume od 1. do 9999. godine nove ere i nađemo njihove prve pozicije u ciframa broja π.

### Računanje broja π

Gotov program za računanje broja π pronađen je [na internetu](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354){: hreflang=ru }. Izračunao je 3 milijarde cifara posle decimalnog zareza. Rezultat je bila tekstualna datoteka od skoro 3 GB.

Zatim se ispostavilo da se Python 2.7, u kom obično pišem male programe, [ne slaže](https://ozymaxx.github.io/blog/2018/05/29/python-strftime){: hreflang=en } sa datumima pre 1900. Za nabrajanje datuma uzeo sam biblioteku [arrow](http://arrow.readthedocs.io){: hreflang=en }, koja je to savršeno odradila:

```python
start_date = arrow.Arrow(0001, 1, 1), end_date = arrow.Arrow(9999, 12, 30)
with open('dates.txt', 'w') as dates:
        for single_date in arrow.Arrow.range('day', start_date, end_date):
            print >>dates, single_date.format(fmt='DDMMYYYY')
```

Tako je generisana datoteka sa svim mogućim datumima sa četvorocifrenom pozitivnom godinom, uz uvažavanje prestupnih godina i slično.

Dalje je trebalo da datumi postanu ključevi rečnika; zatim proći kroz sve podstringove broja π i kao vrednosti sačuvati pozicije (u odnosu na decimalni zarez) prvog pojavljivanja svakog datuma.

Ispostavilo se da Python 2.7 ograničava i vrednost iteratora operatora [`range()`](https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large){: hreflang=en }, pa je kod ispao ovakav:

```python
def window(seq, n=2):
    ''' Returns a sliding window (of width n) over data from the iterable
        s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ... '''
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def fill_db(db, PI, beg, end, count):
    ''' Put all shifts of dates sub-strings in PI into dictionary db '''
    for i, block in enumerate(window(PI[beg:end],8)):
        s = ''.join(block)
        ddate = "%s.%s.%s" % (s[:2],s[2:4],s[4:])
        if (db.has_key(ddate)):
            if (db[ddate] == ""): count -= 1
            db[ddate] = i+beg
            if (count == 0): break
        if (not (i % 5000000)):
            print '.',

count = len(db)
fill_db(db, PI, 0, 1000000000, count)
fill_db(db, PI, 1000000000, 2000000000, count)
fill_db(db, PI, 2000000000, 3000000000, count)
print
```

_Ove pripremne skripte nisu u `legacy/`; u veb verziji zamenjuje ih [tools/build_index.py](../tools/build_index.py)._

To je to, faza pripreme je završena.

Ostala je sitnica – grafički interfejs.

### Grafički interfejs

Plan interfejsa:

<img width="807" height="579" alt="plan" src="img/plan-en.png" />

1.  Fiksirati minimalnu veličinu prozora.
2.  Unos datuma sa validacijom, da se ne bi mogao uneti nevažeći datum.
3.  Naučiti da se tekst na `Label`-u raspoređuje tako da se prelama po znakovima i prikazuje tačno onoliko teksta koliko staje na ekran.
4.  Učitavati potreban deo broja π iz datoteke u hodu i prikazivati ga.
5.  Istaći pronađeni podstring među svim znakovima.
6.  Raspored: zaglavlje od tri objekta koji se ne razvlače, a ispod njih ostali objekti koji se razvlače.
7.  Optimizovati aplikaciju.

Počnimo od jednostavnih stvari.

### Minimalna veličina prozora

```python
root.geometry("1280x640") # default window size at startup
root.minsize(680, 340)    # minimum window size, so widgets don't collapse into a dot
```

Izvor: [legacy/pi.py, redovi 206–207](../legacy/pi.py#L206-L207)

### Validacija unosa

Za unos datuma izabrao sam vidžet `Entry` (analog WinAPI Textbox-a). Odlučio sam da unos „samo datuma nove ere“ implementiram sam, validacijom znakova u hodu.

Ilustracija [opšte šeme validacije](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en } korisničkog unosa teksta u bilo koji Tk vidžet:

```python
class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        vcmd = (self.register(self.onValidate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.text = tk.Text(self, height=10, width=40)
        self.entry.pack(side="top", fill="x")
        self.text.pack(side="bottom", fill="both", expand=True)

    def onValidate(self, d, i, P, s, S, v, V, W):
        self.text.delete("1.0", "end")
        self.text.insert("end","OnValidate:\n")
        self.text.insert("end","d='%s'\n" % d)
        self.text.insert("end","i='%s'\n" % i)
        self.text.insert("end","P='%s'\n" % P)
        self.text.insert("end","s='%s'\n" % s)
        self.text.insert("end","S='%s'\n" % S)
        self.text.insert("end","v='%s'\n" % v)
        self.text.insert("end","V='%s'\n" % V)
        self.text.insert("end","W='%s'\n" % W)

        # Disallow anything but lowercase letters
        if S == S.lower():
            return True
        else:
            self.bell()
            return False
# ...
Example(root).pack(fill="both", expand=True)
```

Od svega toga bio mi je potreban samo parametar `'%P'` – _ceo novi unos_. Ako posle kucanja sledećeg znaka unos u celini nije (početak) datuma, zadržavamo ono što je bilo otkucano pre tog znaka; u suprotnom se znak dodaje u `Entry`.

Za potpun datum koristimo istu biblioteku arrow. Dobijeni vidžet `DateEntry`: [legacy/pi.py, redovi 34–89](../legacy/pi.py#L34-L89).

### Podešavanje vidžeta za π

Isprva sam planirao da za prikaz broja π koristim statički tekst. On dobro odgovara kada korisnike treba sprečiti da selektuju, kopiraju ili menjaju prikazani tekst.

`Label` ne ume sam da prelama tekst u nove redove znak po znak. Pronašao sam [način](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps){: hreflang=en } da se prelama po slovima – prinudna dužina prelamanja postavlja se na širinu vidžeta:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
# ...
lbt = WrappingLabel(root, textvariable=lbt_text, font=dFont, anchor=tk.NW, justify=tk.LEFT)
```

justify – poravnanje višelinijskog teksta uz levu ivicu `Label`-a.

Zatim je tekst za prikaz trebalo skratiti na količinu koja staje na ekran.

Za to sam počeo da izmišljam još jedan točak, presrećući događaj promene veličine glavnog prozora:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', self.fit)         # intercept the text insert/change event
        self.font = tkFont.nametofont(self["font"])                   # the widget's font
        self.font_height = self.font.metrics('linespace')             # font height in pixels

    def fit(self, event):
        # widget width from the event
        max_width = event.width
        # number of lines that fit vertically, given the font
        max_height = event.height / self.font_height
        # the changed text
        text = lbt_text.get()
        # current text width
        actual_width = self.font.measure(text)
        # shrink the text until it fits into the widget entirely
        while (actual_width > (max_width * max_height) and len(text) > 1):
            text = text[:-1]
            actual_width = font.measure(text + "...")
        # remember the result
        lbt_text.set(text + '...')
        # keep wrapping by characters inside the widget
        return self.config(wraplength=self.winfo_width())

last_event_H, last_event_W = 0, 0 # previous lbt size - height and width

def sizing(event):
    ''' Main window size changing Event handler '''
    global last_event_H, last_event_W
    if (event.width == last_event_W and event.height == last_event_H):
        return # the size has not changed
    last_event_H, last_event_W = event.height, event.width
    # fire the event manually to fit the inserted text
    lbt.event_generate("<Configure>", when="now",
                       width=lbt.winfo_width(), height=lbt.winfo_height())
# ...
root.bind("<Configure>", sizing) # connect the custom handler to the event
```

Na kraju sam morao da odustanem od vidžeta `Label` – pre svega zato što sam ne ume da oboji pronađeni podstring. Morao bih da napravim dinamički `Label` preko statičkog, izračunam koordinate podstringa u prozoru i tamo postavim novi `Label` u novoj boji…

Uf…

### Vidžet Text za π

`Text` je moćniji vidžet, sa formatiranjem delova teksta i finijom kontrolom.

Zahvaljujući [putevodnoj niti svih programera i jedinom zraku svetlosti](http://stackoverflow.com){: hreflang=en } u tami i razočaranju svega postojećeg, gde su me uputili na [objavu](https://stackoverflow.com/questions/40992931/python-easiest-way-to-define-multiple-global-variables){: hreflang=en } sa sličnim slučajem kao onaj koji sam započeo u prethodnom odeljku, i na [dokumentaciju](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en } Tkinter-a, moj san se ostvario:

```python
class WrappingLabel(tk.Text):
    ''' a type of Text that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Text.__init__(self, master, **kwargs)
        self.bind('<Configure>', self.onFit)
        self.font = tkFont.nametofont(self["font"])
        self.font_height = 46.8 # self.font.metrics('linespace')

    def onFit(self, event):
        global LONG_ARRAY, lb_first_text, lb_last_no_text, lb_found_no_text
        max_width = event.width
        max_height = event.height / self.font_height # rough n_lines
        text = LONG_ARRAY
        last = int(lb_last_no_text.get())
        first = int(lb_first_text.get())-1
        actual_width = self.font.measure(text)
        if (actual_width  > max_width * max_height):
            # the original text won't fit. Keep shrinking until it does
            ilast = bisect.bisect_left(KeyList(text, key=lambda x,i:
                                               self.font.measure(text[:i]+ '...')),
                                               max_width * max_height)
            last = (first + ilast) if (ilast > 0) else last
            text = text[:last-first] + '...'
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)
        self.insert(tk.END, text)
        if (lb_found_no_text.get().isdigit()):
            index = (int(lb_found_no_text.get()) - first - 1)
            self.tag_delete("highlight")
            self.tag_add("highlight", "1."+str(index), "1."+str(index+8))
            self.tag_config("highlight", background=frame["bg"], foreground="red")
        self.config(state=tk.DISABLED)
        lb_last_no_text.set(str(last))
        return True
# ...
lbt = WrappingLabel(frame, font=dFont, wrap=tk.CHAR, bg=frame["bg"], fg='black')
```

Izvor: [legacy/pi.py, redovi 101–134](../legacy/pi.py#L101-L134); stvaranje vidžeta – [red 248](../legacy/pi.py#L248)

Ideja je ostala ista – presretanje događaja promene teksta – ali je implementacija poboljšana. Nekoliko tačaka.

1.  Binarna pretraga umesto while petlje kroz sva slova počev od poslednjeg.

```python
if (actual_width  > max_width * max_height):
    # the original text won't fit. Keep shrinking until it does
    ilast = bisect.bisect_left(KeyList(text, key=lambda x,i:
                                       self.font.measure(text[:i]+ '...')),
                                       max_width * max_height)
```

Izvor: [legacy/pi.py, redovi 117–121](../legacy/pi.py#L117-L121)

Pošto `bisect` nema parametar key za vrednost po kojoj se poredi, morao sam da napišem omotač:

```python
class KeyList(object):
    ''' bisect doesn't accept a key function, so we build the key into our sequence '''
    def __init__(self, l, key):
        self.l = l
        self.key = key
    def __len__(self):
        return len(self.l)
    def __getitem__(self, index):
        return self.key(self.l[index], index)
```

Izvor: [legacy/pi.py, redovi 91–99](../legacy/pi.py#L91-L99)

Umesto slova, on pretrazi daje širinu teksta od početka do tog slova.

2\. Umesto tačne visine fonta izabrao sam koeficijent: zbog prelamanja redova, širina pomnožena visinom ionako nije tačna veličina.

```python
self.font_height = 46.8   # instead of self.font.metrics('linespace')
```

Izvor: [legacy/pi.py, red 107](../legacy/pi.py#L107)

Koeficijent postavlja kraj teksta što bliže kraju vidžeta, ali se, naravno, ponekad promaši:

<img width="1071" height="105" alt="font_height" src="https://github.com/user-attachments/assets/c2254737-5e6c-4251-9eeb-fe905d76fc0d" />

3\. `Text` ume sam da prelama po znakovima.

```python
wrap=tk.CHAR
```

4\. `Text` ume da ističe sopstvene podstringove. Isticanje pronađenog podstringa crvenom bojom:

```python
self.tag_add("highlight", "1."+str(index), "1."+str(index+8))
self.tag_config("highlight", background=frame["bg"], foreground="red")
```

Izvor: [legacy/pi.py, redovi 130–131](../legacy/pi.py#L130-L131)

5\. Zabraniti svaku izmenu vidžeta:

```python
lb3.config(state=tk.DISABLED)
```

Izvor: [legacy/pi.py, red 255](../legacy/pi.py#L255)

Da se `Text` ne bi isticao, baš kao `Label`, njegov `background` postavlja se na boju glavnog prozora:

```python
bg=frame["bg"]
```

Dodajmo neke početne podatke u `Text` pri pokretanju:

```python
LONG_ARRAY = read_pi(1,2500)
lb3.insert(tk.END, LONG_ARRAY)
```

Izvor: [legacy/pi.py, red 204](../legacy/pi.py#L204) i [red 254](../legacy/pi.py#L254)

U rukovaocu događajem zamenimo podatke potrebnim:

```python
self.delete(1.0, tk.END)   # first delete the old data, starting from char 0 of line 1,
self.insert(tk.END, text)  # then insert the new data at the end of the text
```

Izvor: [legacy/pi.py, redovi 125–126](../legacy/pi.py#L125-L126)

Kao što vidite, podaci se dodaju drugačije nego u `Label`-u: mogu se dodavati red po red, uz navođenje u koji red se piše. Nisam se time zamarao i radim samo sa jednim redom.

Bar jednom je nešto urađeno ugrađenim alatima, što je već _velika pobeda_.

Kod koji pretražuje bazu datuma, a pokreće se klikom na dugme „Find“ ili pritiskom na Enter:

```python
def bt_find_click(event=None):
    global LONG_ARRAY, FN_LOG_DATES, DB
    global lb_first_text, lb_last_no_text, lb_found_no_text, lb3
    # show at least some digits of Pi in the Text
    first, last = 1, 2500
    # get the entered date
    ddate = tb_date.get()
    if (not DB.has_key(ddate)): # if the user has not entered a date
        lb_found_no_text.set("--")
    else:
        # offset of this date relative to the decimal point
        index = int(DB[ddate])
        # number of characters currently shown in the Text
        last = int(lb_last_no_text.get()) - int(lb_first_text.get())
        # random position of the found substring on screen
        last_of = random.randint(9, 100) if (last > 100) else 9
        offset = random.randint(10, last - last_of)
        # start and end of the shown fragment of Pi
        first = (index - offset) if (index > offset) else 1
        last = index + last
        # show the offset of the found date in its widget
        lb_found_no_text.set(str(index))
    # show the new bounds of the fragment in their widgets
    lb_first_text.set(str(first))
    lb_last_no_text.set(str(last))
    # read the needed fragment of Pi from the file
    LONG_ARRAY = read_pi(first, last-first)

    lb3.config(state=tk.NORMAL)        # allow editing the Text
    lb3.event_generate("<Configure>",             # fire the event ourselves
                       when="now",                # right now
                       width=lb3.winfo_width(),   # and set the Event arguments, namely
                       height=lb3.winfo_height()) # the current width and height of the widget
    lb3.config(state=tk.DISABLED)      # forbid editing
```

Izvor: [legacy/pi.py, redovi 136–162](../legacy/pi.py#L136-L162)

Kao što vidite, da bi se `Text` sada izmenio, čak i iz koda, najpre ga treba vratiti u normalno stanje, promeniti sadržaj, a zatim ponovo zabraniti izmene.

Nasumični pomeraj čini očiglednim da je za novi datum istaknuto podudaranje tačno i da se nalazi u drugom (možda dalekom) fragmentu broja π.

Svojevrsna optimizacija je to što se učitava samo mali potrebni fragment broja π. Čitanje je brzo i ne izaziva zastoje u interfejsu. Držati celu ogromnu datoteku sa brojem π u memoriji i čitati je pri pokretanju bilo bi veoma rasipno.

```python
def read_pi(first,last):
    global FN_PI_STRING
    with open(FN_PI_STRING, 'r') as f_pi:
        if (first == 1):
            f_pi.seek(1)
            PI = "3."+f_pi.read(last)
        else:
            f_pi.seek(first)
            PI = f_pi.read(last)
    return PI
```

Izvor: [legacy/pi.py, redovi 164–173](../legacy/pi.py#L164-L173)

### Raspored

Isprva sam mislio da program sklopim pomoću prvog i najjednostavnijeg pakera – `pack()`. Prema planu, to je zahtevalo grupisanje objekata tako da se glavni `Text` pravilno razvlači prema veličini prozora.

Prvo sam zaglavlje od tri objekta – poziv na unos, unos datuma i dugme – smestio u grupu `Frame`, `win_header`.

```python
# ...
win_header = tk.Frame(root, padx=10, pady=2)
# padx and pady - padding for the elements inside the group
win_header.pack(side=tk.TOP, fill=tk.X)
# add the group to the main window from the top (TOP)
# stretch horizontally (X) across the whole window width
# add the Prompt to the group on the left
lb_invite = tk.Label(win_header, text="Input your birth date", font=dFont,
                     anchor=tk.NW, width=20)
lb_invite.pack(side=tk.LEFT)
# add the Entry to the group right after the Prompt
lb_date = DateEntry(win_header, font=dFont)
lb_date.pack(side=tk.LEFT)
# attach the button on the right
bt_find = tk.Button(win_header, text="Find", font=dFont, command=bt_find_click, pady=2)
bt_find.pack(side=tk.RIGHT)
# ...
```

Drugo, bile su mi potrebne grupe za glavni deo, `win_body`, i u njemu leva kolona `winbl` sa tri broja znakova: prvi prikazani, početak pronađenog datuma i poslednji prikazani.

```python
# ...
win_body = tk.Frame(root)
win_body.pack(side=tk.TOP, fill=tk.BOTH)
# stretch the group in both directions: vertical and horizontal
# on the left add a group - the column with character numbers
winbl = tk.Frame(win_body, width=10)
winbl.pack(side=tk.LEFT, fill=tk.BOTH)
# widget for the number of the first shown character
lb_first_no = tk.Label(winbl, textvariable=lb_first_no_text, font=dFont, anchor=tk.NW, width=10)
lb_first_no.pack(side=tk.TOP, fill=tk.X)
# widget for the number of the character where the found substring starts
lb_found_no = tk.Label(winbl, textvariable=lb_found_no_text, font=dFont, anchor=tk.NW, width=10)
# widget for the number of the last shown character
lb_last_no = tk.Label(winbl, textvariable=lb_last_no_text, font=dFont, anchor=tk.NW, width=10)
lb_last_no.pack(side=tk.BOTTOM, fill=tk.X)
# the main widget for the shown fragment of Pi
lb_digits = WrappingLabel(win_body, textvariable=lb_digits_text, font=dFont,
                          anchor=tk.NW, justify=tk.LEFT)
lb_digits.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
# Expand this widget over all free space in the group,
# and fill the group itself over all free space in the window
# ...
```

_Ova verzija sa `pack()` nije ušla u konačni kod._

Ali kasnije sam savladao paker grid() i sve uradio njime.

### Paker grid

Napravio sam grupu `frame` za sve vidžete glavnog prozora i u njoj postavio virtuelnu mrežu od 11 kolona i 7 redova.

Moje razmišljanje: poziv na unos, unos datuma i dugme idu u prvi red; poziv zauzima 4 kolone, unos datuma dolazi odmah posle njega i zauzima 3 kolone, a dugme je desno i zauzima 2 kolone. Dozvolio sam im da se razvlače (sticky) u svim pravcima zajedno sa svojim ćelijama.

```python
frame = tk.Frame(root)
tk.Grid.rowconfigure(root, 0, weight=1)
tk.Grid.columnconfigure(root, 0, weight=1)
frame.grid(row=0, column=0, sticky=tk.NSEW)
# Prompt
lb_invite = tk.Label(frame, text="Input your birth date", font=dFont, anchor=tk.NW)
lb_invite.grid(column=0, row=0, columnspan=4, sticky=tk.NSEW, pady=0, padx=10)
# Date input
tb_date = DateEntry(frame, font=dFont)
tb_date.grid(column=4, row=0, columnspan=3, sticky=tk.NSEW, pady=10)
# Button
bt_find = tk.Button(frame, text="Find", font=dFont, command=bt_find_click)
bt_find.grid(column=8, row=0, columnspan=2, sticky=tk.NSEW, pady=0)
```

Izvor: [legacy/pi.py, redovi 213–224](../legacy/pi.py#L213-L224)

Ostali elementi postavljeni su na isti način. Kao što vidite, `Text` – `lbt` – zauzima najviše prostora:

```python
# widget for the number of the first shown character
lb_first = tk.Label(frame, textvariable=lb_first_text, width=10)
lb_first.grid(column=0, row=2, sticky=tk.NSEW)
# widget for the number of the character where the found substring starts
lb_found_no = tk.Label(frame, textvariable=lb_found_no_text)
lb_found_no.grid(column=0, row=4, sticky=tk.NSEW)
# widget for the number of the last shown character
lb_last_no = tk.Label(frame, textvariable=lb_last_no_text)
lb_last_no.grid(column=0, row=6, sticky=tk.NSEW)
# the main widget for the shown fragment of Pi
lbt = WrappingLabel(frame)
lbt.grid(column=1, row=1, columnspan=9, rowspan=5, sticky=tk.NSEW)
```

Izvor: [legacy/pi.py, redovi 225–249](../legacy/pi.py#L225-L249)

Na samom kraju postavio sam težine ćelija: što je težina veća, to se ćelija više menja pri skaliranju glavnog prozora.

```python
for y in range(1,11): tk.Grid.columnconfigure(frame, y, weight=1)
for x in range(2,6): tk.Grid.rowconfigure(frame, x, weight=1)
```

Izvor: [legacy/pi.py, redovi 250–253](../legacy/pi.py#L250-L253)

### Optimizacija programa

Kada je sve bilo napisano i debagovano, površno testiranje je pokazalo da se program pokreće neoprostivo sporo. Sve zbog čitanja tekstualne datoteke.

Čitanje datoteke sa brojem π uspeo sam da izbegnem. Ali čitanje cele baze datuma iz njene datoteke ne može se izbeći. To je tabela sa dve kolone: string datuma, tabulator i pomeraj.

Dakle, morao sam da otkrijem kako da je pročitam brzo. Jednostavan eksperiment:

```python
from timeit import default_timer as timer

def read_db():
    global FN_DB_DATES

    t = timer()
    db = {}
    with open(FN_DB_DATES, 'r') as f:
        pairs = [ line.split('\t') for line in f ]
        db = { k:v for k,v in pairs }
    elapsed = timer() - t
    print "{} {:.10f} secs.".format("readfile", elapsed)

    db1 = {}
    t = timer()
    with open(FN_DB_DATES, mode='r') as infile:
        db1 = dict(row[:2] for row in csv.reader(infile, delimiter="\t"))
    elapsed = timer() - t
    print "{} {:.10f} secs.".format("csv file", elapsed)

    t = timer()
    db2 = pd.read_csv(FN_DB_DATES, header=None, delimiter="\t",
                      dtype={'a':str,'b':str}).set_index(0).squeeze().to_dict()
    elapsed = timer() - t
    print "{} {:.10f} secs.".format("pd  file", elapsed)

    t = timer()
    db3 = {row[0] : row[1] for row in pd.read_csv(FN_DB_DATES).iterrows()}
    elapsed = timer() - t
    print "{} {:.10f} secs.".format("pd csvrd", elapsed)

    t = timer()
    db4 = { k:v for k,v in loadtxt(FN_DB_DATES, delimiter="\t",
                                   dtype={'names': ('date', 'offset'), 'formats': ('S','S')}) }
    elapsed = timer() - t
    print "{} {:.10f} secs.".format("loadtxt ", elapsed)
    return db
```

Vremena su merena pomoću timeit, standardnog Python alata.

Rezultati:

```
readfile 6.3322045118 secs.
csv file 4.1212712648 secs.
pd  file 4.4932071859 secs.
pd csvrd 350.0057260714 secs.
loadtxt  41.6930684601 secs.
```

Pobeđuje csv. I dalje sporo. Konačni `read_db`: [legacy/pi.py, redovi 189–193](../legacy/pi.py#L189-L193).

Zato sam uveo tešku artiljeriju – višenitnost: čitati tekstualnu datoteku sa datumima u pozadini dok se forma učitava.

```python
# a thread that reads the text file
class Worker(threading.Thread):
    ''' thread to read the dates DB from the text file '''
    def run(self):
        global DB
        DB = read_db()
WORKER = Worker() # an instance of the thread that reads the DB from the file
```

Izvor: [legacy/pi.py, redovi 27–32](../legacy/pi.py#L27-L32)

Za ovaj slučaj, prilično čest u GUI programiranju – da forma ostane responzivna tokom teških izračunavanja – Tk ima posebne funkcije. Potrebna nam je `after()`, koja poziva našu funkciju, ovde `listen_for_result()`, posle 10 milisekundi petlje događaja.

```python
def listen_for_result():
    """ Check if there is something load """
    global WORKER, root
    WORKER.join(1)
    if WORKER.is_alive():
        root.after(10, listen_for_result)

if __name__ == '__main__':
    # ...
    WORKER.start()
    root.after(10, listen_for_result)
    # ...
    root.mainloop()
```

Izvor: [legacy/pi.py, redovi 195–200](../legacy/pi.py#L195-L200) i [redovi 208–209](../legacy/pi.py#L208-L209)

Ona pokušava da pridruži nit ako je završila, a ako nije, zakazuje da Tk sačeka još 10 milisekundi.

Tako se glomazna tekstualna datoteka učitava paralelno sa prozorom, što je takođe teška operacija. _Pobeda_.

Ostaje jedna kvaka: ako korisnik unese datum pre nego što je datoteka pročitana – veoma malo verovatno, ali ipak – čekamo da nit završi, pa onda pretražujemo gotovu bazu:

```python
def bt_find_click(event=None):
    # ...
    if WORKER.is_alive():
        WORKER.join()
    # ...
```

Izvor: [legacy/pi.py, redovi 140–141](../legacy/pi.py#L140-L141)

### Ceo izvorni kod

Ceo kod je u [legacy/pi.py](../legacy/pi.py).

<img width="1080" height="557" alt="interface" src="img/interface-en.jpg" />

### Lokalizacija

Umesto stringova upisanih direktno u kod, stringovi se čitaju iz konfiguracione datoteke: [legacy/pi.py, redovi 175–187](../legacy/pi.py#L175-L187).

<img width="1080" height="565" alt="localize" src="https://github.com/user-attachments/assets/36be95e5-22fa-42e1-982e-cf63ec3ea86a" />

### Izvršna datoteka

Ostaje još da se napravi .exe – to se radi konzolnom komandom (ako imate instaliranu Anacondu):

```
pyinstaller --onefile pi.py --noconsole
```

noconsole – Tk se pokreće iz konzole, pa se pre forme pojavljuje terminal; ne treba nam, a ova opcija ga uklanja.

### Osam godina kasnije

Godine 2026. program se preselio u pregledač, a ispostavilo se da sajtu fajl od 3 GB sa ciframa broja π uopšte nije potreban. Kako je do toga došlo, pišem u novom zapisu: [π čuva sve, pa ja nisam morao da čuvam π](/sr/writing/pi-stores-everything/).

### Reference

-   [Stack Overflow: How to get the widget's current x and y coordinates](https://stackoverflow.com/questions/30257574/how-to-get-the-widgets-current-x-and-y-coordinates){: hreflang=en }
-   [Python docs: ttk — Tk themed widgets](https://docs.python.org/2.7/library/ttk.html#label-options){: hreflang=en }
-   [Tcl/Tk manual: event](https://www.tcl-lang.org/man/tcl8.6/TkCmd/event.htm){: hreflang=en }
-   [Stack Overflow: Make the Tkinter Text widget read-only](https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only){: hreflang=en }
-   [effbot: The Tkinter Text widget](https://web.archive.org/web/20201112033110/http://effbot.org/tkinterbook/text.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Text](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Button](https://www.tutorialspoint.com/python/tk_button.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Entry](https://www.tutorialspoint.com/python/tk_entry.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Frame](https://www.tutorialspoint.com/python/tk_frame.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Label](https://www.tutorialspoint.com/python/tk_label.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter pack()](https://www.tutorialspoint.com/python/tk_pack.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter grid()](https://www.tutorialspoint.com/python/tk_grid.htm){: hreflang=en }
-   [Stack Overflow: How many characters fit in an expanding Tkinter label](https://stackoverflow.com/questions/52062162/python-tkinter-how-to-count-the-quantity-of-characters-can-be-shown-in-expandi/52066664#52066664){: hreflang=en }
-   [ZetCode: Tkinter layout management](https://web.archive.org/web/20190415112347/http://zetcode.com/gui/tkinter/layout/){: hreflang=en }
-   [Stack Overflow: Current widget size in Tkinter](https://stackoverflow.com/questions/3950687/how-to-find-out-the-current-widget-size-in-tkinter){: hreflang=en }
-   [Stack Overflow: Interactively validating Entry content in Tkinter](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en }
-   [effbot: The Tkinter Label widget](https://web.archive.org/web/20201112020335/http://effbot.org/tkinterbook/label.htm){: hreflang=en }
-   [Reddit r/learnpython: Text that wraps automatically](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps/){: hreflang=en }
-   [Stack Overflow: Tkinter Entry validation not working](https://stackoverflow.com/questions/25936958/tkinter-entry-validation-not-working){: hreflang=en }
-   [effbot: Tkinter variable classes](https://web.archive.org/web/20230716211314/https://effbot.org/tkinterbook/variable.htm){: hreflang=en }
-   [NMT Tkinter reference: Entry validation](https://tkdocs.com/shipman/entry-validation.html){: hreflang=en }
-   [Stack Overflow: Tkinter Entry formatted for a date](https://stackoverflow.com/questions/13242970/tkinter-entry-box-formatted-for-date){: hreflang=en }
-   [Stack Overflow: Three dots at the end of a Tkinter label](https://stackoverflow.com/questions/51143777/display-three-dots-in-the-end-of-a-tkinter-label-text){: hreflang=en }
-   [Stack Overflow: bisect on a list of tuples by the first value](https://stackoverflow.com/questions/42146482/using-bisect-on-list-of-tuples-but-compare-using-first-value-only){: hreflang=en }
-   [effbot: Tkinter events and bindings](https://web.archive.org/web/20230528034914/https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm){: hreflang=en }
-   [Stack Overflow: Measure the height of a string in Tkinter](https://stackoverflow.com/questions/48726956/measure-the-height-of-a-string-in-tkinter-python){: hreflang=en }
-   [Stack Overflow: Invoke an event in the Tkinter main loop](https://stackoverflow.com/questions/270648/tkinter-invoke-event-in-main-loop){: hreflang=en }
-   [Arrow: better dates & times for Python](https://arrow.readthedocs.io/en/latest/#arrow.arrow.Arrow){: hreflang=en }
-   [Python docs: bisect — array bisection algorithm](https://docs.python.org/2/library/bisect.html){: hreflang=en }
-   [Tutorialspoint: Python file seek()](https://www.tutorialspoint.com/python/file_seek.htm){: hreflang=en }
-   [Stack Overflow: datetime to a date-only string](https://stackoverflow.com/questions/10624937/convert-datetime-object-to-a-string-of-date-only-in-python){: hreflang=en }
-   [Stack Overflow: Loop over a range of dates](https://stackoverflow.com/questions/14288498/creating-a-loop-for-two-dates/14288620){: hreflang=en }
-   [Stack Overflow: OverflowError: iter index too large](https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large){: hreflang=en }
-   [Multithreading with Tkinter](https://scorython.wordpress.com/2016/06/27/multithreading-with-tkinter/){: hreflang=en }
-   [Stack Overflow: Run in the background independently of the Tk front end](https://stackoverflow.com/questions/42589372/pythontkinter-how-to-run-in-background-independant-of-tk-frontend){: hreflang=en }
-   [Python docs: threading — higher-level threading interface](https://docs.python.org/2/library/threading.html){: hreflang=en }
-   [CyberForum: QBasic thread](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354){: hreflang=ru }
