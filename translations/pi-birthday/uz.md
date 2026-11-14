---
title: "Tugʻilgan kuningiz π raqamlari ichida"
summary: "Tugʻilgan sanangizni π sonining 3 milliard raqami orasidan topadigan Python/Tkinterdagi kichik GUI-ilova — keyinchalik veb uchun qayta yaratilgan."
source: favorart/pi-birthday@main:article.md
source_lang: en
source_hash: 926233cf
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
# Pythonda GUI-ilova

**English** · [Русский](article.ru.md){: hreflang=ru }

_Birinchi, desktop versiyasi (Python 2.7 + Tkinter) haqidagi 2018-yilgi maqola, rus tilidan tarjima. Asl nashr: [vk.ru/@33453621-pi-gui-python](https://vk.ru/@33453621-pi-gui-python){: hreflang=ru }. Toʻliq kod: [legacy/pi.py](legacy/pi.py); uni bugun ishga tushirish uchun [legacy/run.sh](legacy/run.sh)dan foydalaning._

Vaqti-vaqti bilan menga kichik oynali ilova yozish kerak boʻlib qoladi. Odatda ilovalarni C++da yozaman. Bir paytlar Qt oʻrniga Windows APIni oʻrgangandim, chunki oynalarim doim Windows uchun boʻlardi, va men nativ interfeys har doim eng yaxshisi deb hisoblayman. Hammasi organik koʻrinishini xohlayman. WinAPI Windows qila oladigan hamma narsani qilishga imkon beradi, lekin koʻp narsani qoʻlda yozishga toʻgʻri keladi, qandaydir qoʻngʻiroqchalar va hushtakchalar esa doim kerak boʻladi.

WinAPIda boshqaruv elementlarini sichqoncha bilan sudrab joylashtirib boʻlmaydi; Visual Studioda bu qatlam uchun dizayner yoʻq **:(** (formalar oʻrniga dialoglardan foydalanadigan ayyorona aylanma yoʻllarni hisobga olmaganda). Albatta, yuqoriroq darajalar ham bor — MFC va WPF. Lekin birinchisida klasslar juda gʻalati va murakkab tashkil etilgan, unga sira kirishgim kelmaydi. Ikkinchisi esa hamma jihatdan ajoyib, faqat u C#: agar C++da yozmoqchi boʻlsangiz, managed koddan foydalanishingiz va .NET framework funksiyalarini chaqirishingiz kerak.

Mayli… Koʻpincha istalgan ilovani Pythonda yozish osonroq.

Keling, shu rostmi, koʻramiz.

### Tkinter

**Tkinter** — Tcl dasturlash tilida yozilgan Tk kutubxonasi bilan ishlash uchun Python paketi. Paket shunchaki Python kodini Tcl buyruqlariga oʻgiradi.

### Vidjetlar

**Vidjet** — interfeys elementi (WinAPI atamalarida Control): oʻrnatilgan klasslardan yaratilgan obyekt.

-   `Button` – tugma
-   `Entry` – bir qatorli matn kiritish maydoni
-   `Frame` – vidjetlar guruhi
-   `Label` – oynaning rasm yoki statik matn joylashadigan sohasi
-   `Text` – koʻp qatorli matn kiritish maydoni

va boshqalar.

Har qanday GUI hodisalarga yoʻnaltirilgan dasturlash paradigmasiga amal qiladi: muayyan kod qismi faqat maʼlum hodisa yuz berganda ishlaydi.

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

### Hodisalar

Hodisalar turli xil boʻladi: ularni taymer, foydalanuvchi, tizim, vidjetlarning oʻzi va hokazolar keltirib chiqarishi mumkin. Hodisalar juda koʻp va har birining sukut boʻyicha yoki boʻsh ishlovchisi bor. Hodisa kelganda dasturning maʼlum qismi ishlaydi. Odatda oʻz mantigʻingiz hodisa ishlovchilariga yoziladi.

Minimal ilova quyidagicha koʻrinadi:

```python
try:
    import tkinter as tk    # >= python 3.0
except ImportError:
    import Tkinter as tk    # >= python 2.7

root = tk.Tk()  # create the main window
root.mainloop() # start the loop that receives and handles events
```

`mainloop()` ichida cheksiz sikl bor. Bu chaqiruvdan keyin yozilgan kod faqat ilova yopilgandan keyin ishlaydi. Sikl, masalan, yopish tugmasi bosilishi hodisasida tugaydi.

GUI-dasturning umumiy rejasi:

-   Asosiy oynani yaratish.
-   Qoʻshimcha oynalar va vidjetlarni yaratish, ularni sozlash va vidjetlarni asosiy yoki boshqa oynalarga qoʻshish.
-   Qiziqtirgan hodisalar va ularning ishlovchilarini belgilash — yaʼni foydalanuvchi kodi qayerga yozilishi va dastur qanday javob berishini.
-   Hodisalar siklini ishga tushirish.

### Vidjetlarni sozlash

Birinchi vidjetni yaratamiz — oynadagi foydalanuvchi oʻzgartira olmaydigan statik matn:

```python
tk.Label(root, text="This label")
```

Lekin matnni koddan oʻzgartirish mumkin: `text` parametri oʻrniga satrli oʻzgaruvchi ulanadi — uning qiymatini oʻzgartirish `Label`dagi matnni darhol oʻzgartiradi:

```python
lb_text = tk.StringVar()
lb_text.set("1")
tk.Label(root, textvariable=lb_text, width=10, font=dFont, anchor=tk.NW)
```

Manba: [legacy/pi.py, 227–230-qatorlar](legacy/pi.py#L227-L230)

`font` parametri shriftni oʻzgartiradi; men oldindan kattaroq, oʻqish oson interfeys shriftini tayyorlab qoʻydim:

```python
import tkFont
dFont = tkFont.Font(family="Arial", size=30)
```

Manba: [legacy/pi.py, 211-qator](legacy/pi.py#L211)

`anchor` parametri vidjetning tekislanishini belgilaydi — bu yerda u NORTH-WEST, yaʼni matn vidjetning yuqori chap burchagiga yopishadi.

Xossalarni obyekt yaratilayotganda belgilash shart emas.

Eʼtibor bering, birinchi argument — "egasi", "master" — vidjet yashaydigan joy. Bu yerda uni tushirib qoldirish mumkin edi, chunki sukut boʻyicha u `root`. Lekin vidjetlar toʻgʻridan-toʻgʻri asosiy oynada (`root`) turishi shart emas, ularni boshqa vidjetlar ichiga ham joylashtirish mumkin.

### Oʻz hodisa ishlovchilarimiz

Hodisa yuz berganda chaqiriladigan hodisa ishlovchi funksiyalari bitta parametr qabul qilishi kerak. Odatda u `event` deb ataladi.

`bind` metodi ishlovchini Tk hodisasiga ulaydi:

```python
def bt_find_click(event):
    pass

root.bind('<Return>', bt_find_click)
```

Manba: [legacy/pi.py, 210-qator](legacy/pi.py#L210)

U hodisa nomini va chaqiriladigan funksiyani qabul qiladi. Hodisa barcha parametrlari bilan funksiyaga `event` argumenti sifatida uzatiladi. Bu yerda hodisa — Enter tugmasini bosish, u `'<Return>'` satri bilan yoziladi.

### Vidjetlarni joylashtirish

Vizual interfeys dizaynerini izlab WinAPIdan jon holatda qochgan edim. Maʼlum boʻldiki, Tkinterda ham u tayyor holda yoʻq ekan **:(** Tishimni tishimga qoʻyib, dasturchilar usiz qanday yashashi haqida oʻqiy boshladim va, ajablanarlisi, ular bu muammoni ancha qulay va nafis hal qilishgan ekan.

### Geometriya menejerlari

\[Manba: [habr.com/post/133337](https://habr.com/post/133337/){: hreflang=ru }\]

**1 pack()** — joylashtiruvchi (packer) yoki geometriya menejeri deb ataladigan funksiya. U vidjetlar asosiy oynada qanday joylashishini hal qiladi. Joylashtiruvchini har bir vidjet uchun chaqirish kerak, aks holda vidjet koʻrinmaydi. Jami uchta joylashtiruvchi bor:

pack vidjetlarni ota oynaga avtomatik joylashtiradi. Uning parametrlari:

side – navbatdagi elementni qaysi tomondan qoʻshish,

fill – uni biror yoʻnalishda oyna chetlarigacha choʻzish-choʻzmaslik,

expand – vidjet butun ota elementni toʻldirishi kerakmi.

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

**2 grid()** vidjetlarni toʻrga joylashtiradi. Asosiy parametrlari:

row/column – toʻrdagi qator/ustun,

rowspan/columnspan – vidjet nechta qator/ustunni egallashi,

sticky – katakcha kattalashganda vidjet qanday choʻziladi: katakchaning qaysi chetlariga (N, W, S, E) yopishadi.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').grid(row = 1, column = 1)
Button(root, text = '2').grid(row = 1, column = 2)
Button(root, text = '__3__').grid(row = 2, column = 1, columnspan = 2)
root.mainloop()
```

<img width="137" height="94" alt="2-grid" src="https://github.com/user-attachments/assets/1da19342-4b45-406e-ae00-fb29dfd5bc18" />

**3 place()** vidjetlarni berilgan koordinatalarga berilgan oʻlchamlarda qoʻyadi. Asosiy parametrlari: x, y, width, height.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').place(x = 10, y = 10, width = 30)
Button(root, text = '2').place(x = 45, y = 20, height = 15)
Button(root, text = '__3__').place(x = 20, y = 40)
root.mainloop()
```

<img width="139" height="139" alt="3-place" src="https://github.com/user-attachments/assets/f6ecb75e-e579-4d53-a7a9-653519d72954" />

Vidjet uchun joylashtiruvchi chaqirilmaguncha u, tabiiyki, koʻrinmaydi.

### Vazifa

Endi amalga oshirilishi haqida aytib bermoqchi boʻlgan misol haqida.

π [normal son](http://www.etudes.ru/ru/sketches/normal-number-pi){: hreflang=ru } ekanligi, yaʼni unda istalgan berilgan chekli raqamlar ketma-ketligini topish mumkinligi haqida gipoteza bor.

[Fan festivali](http://www.festivalnauki.ru){: hreflang=ru }da bolalar va kattalarni hayratda qoldirish uchun biz bu [attraksionni](http://www.etudes.ru/ru/sketches/normal-number-pi/){: hreflang=ru } oʻzlashtirdik: _siz tugʻilgan sanangizni kiritasiz, dastur esa uni π sonining nechanchi raqamidan topish mumkinligini aytadi_.

Shunday qilib, π sonini ancha koʻp raqamgacha hisoblash, milodiy 1-yildan milodiy 9999-yilgacha boʻlgan barcha sanalarni aylanib chiqish va ularning π raqamlaridagi birinchi siljishlarini topish kerak edi.

### π sonini hisoblash

π sonini hisoblash uchun tayyor dastur [internetdan](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354){: hreflang=ru } topildi. U oʻnlik nuqtadan keyin 3 milliard raqamni hisobladi. Natijada qariyb 3 GBlik matnli fayl hosil boʻldi.

Keyin maʼlum boʻldiki, men odatda kichik dasturlarni yozadigan Python 2.7 1900-yilgacha boʻlgan sanalar bilan [chiqisha olmas ekan](https://ozymaxx.github.io/blog/2018/05/29/python-strftime){: hreflang=en }. Sanalarni sanab chiqish uchun [arrow](http://arrow.readthedocs.io){: hreflang=en } kutubxonasini oldim, u bu ishni aʼlo darajada uddaladi:

```python
start_date = arrow.Arrow(0001, 1, 1), end_date = arrow.Arrow(9999, 12, 30)
with open('dates.txt', 'w') as dates:
        for single_date in arrow.Arrow.range('day', start_date, end_date):
            print >>dates, single_date.format(fmt='DDMMYYYY')
```

Bu kabisa yillari va boshqalarni hisobga olgan holda, toʻrt xonali musbat yilli barcha mumkin boʻlgan sanalar faylini yaratdi.

Keyin sanalar lugʻat kalitlariga aylanishi kerak edi; soʻng π sonining barcha qism satrlarini aylanib chiqib, qiymat sifatida har bir sana birinchi uchragan joyning (oʻnlik nuqtaga nisbatan) siljishini saqlash kerak edi.

Maʼlum boʻlishicha, Python 2.7 [`range()`](https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large){: hreflang=en } operatorining iterator qiymatini ham cheklar ekan, shuning uchun kod quyidagicha chiqdi:

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

_Bu tayyorgarlik skriptlari `legacy/`da yoʻq; veb-versiyada ularning oʻrnini [tools/build_index.py](tools/build_index.py) egallaydi._

Tamom, tayyorgarlik bosqichi tugadi.

Bir arzimas narsa qoldi xolos — grafik interfeys.

### Grafik interfeys

Interfeys rejasi:

<img width="807" height="579" alt="reja" src="https://github.com/user-attachments/assets/a718d644-af95-4aa8-8da3-48d56f8265bd" />

1.  Oynaning minimal oʻlchamini belgilash.
2.  Notoʻgʻri sanani kiritib boʻlmasligi uchun tekshiriladigan sana kiritish.
3.  `Label`da matnni belgilar boʻyicha keyingi qatorga oʻtadigan va ekranga qancha sigʻsa, aynan shuncha matn koʻrsatiladigan qilib joylashtirishni oʻrganish.
4.  π sonining kerakli qismini fayldan yoʻl-yoʻlakay yuklab, koʻrsatish.
5.  Topilgan qism satrni barcha belgilar orasida ajratib koʻrsatish.
6.  Joylashuv: choʻzilmaydigan uchta obyektdan iborat sarlavha va ularning ostida qolgan choʻziluvchi obyektlar.
7.  Ilovani optimallashtirish.

Oddiy narsalardan boshlaymiz.

### Oynaning minimal oʻlchami

```python
root.geometry("1280x640") # default window size at startup
root.minsize(680, 340)    # minimum window size, so widgets don't collapse into a dot
```

Manba: [legacy/pi.py, 206–207-qatorlar](legacy/pi.py#L206-L207)

### Kiritishni tekshirish

Sanani kiritish uchun `Entry` vidjetini (WinAPIdagi Textbox analogi) tanladim. "Faqat milodiy sanalar" kiritilishini belgilarni yoʻl-yoʻlakay tekshirish orqali oʻzim amalga oshirishga qaror qildim.

Istalgan Tk vidjetiga foydalanuvchi matn kiritishini tekshirishning [umumiy sxemasi](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en } misoli:

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

Bularning hammasidan menga faqat `'%P'` parametri — _butun yangi kiritma_ kerak edi. Agar navbatdagi belgi terilgandan keyin u bir butun sifatida sana (yoki sana boshi) boʻlmasa, shu belgigacha terilgan narsani qoldiramiz; aks holda belgi `Entry`ga qoʻshiladi.

Toʻliq sana uchun oʻsha arrow kutubxonasidan foydalanamiz. Hosil boʻlgan `DateEntry` vidjeti: [legacy/pi.py, 34–89-qatorlar](legacy/pi.py#L34-L89).

### π vidjetini sozlash

Avvaliga π sonini koʻrsatish uchun statik matndan foydalanishni rejalashtirgandim. U foydalanuvchilarga koʻrsatilgan matnni belgilash, nusxalash yoki oʻzgartirishni taqiqlash kerak boʻlganda yaxshi mos keladi.

Tayyor holda `Label` matnni belgilar boʻyicha yangi qatorlarga koʻchira olmaydi. Harflar boʻyicha koʻchirishning [usulini](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps){: hreflang=en } topdim — majburiy koʻchirish uzunligi vidjet kengligiga tenglashtiriladi:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
# ...
lbt = WrappingLabel(root, textvariable=lbt_text, font=dFont, anchor=tk.NW, justify=tk.LEFT)
```

justify — koʻp qatorli matnni `Label`ning chap chetiga tekislash.

Keyin koʻrsatiladigan matnni ekranga sigʻadigan hajmgacha qisqartirish kerak edi.

Buning uchun asosiy oynaning oʻlchami oʻzgarishi hodisasini ushlab, yana bir velosiped ixtiro qila boshladim:

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

Oxir-oqibat `Label` vidjetidan voz kechishga toʻgʻri keldi — eng avvalo, u tayyor holda topilgan qism satrni boʻyay olmagani uchun. Statik `Label` ustida dinamik `Label` yaratishim, oynada qism satr koordinatalarini hisoblashim va u yerga yangi rangli yangi `Label` joylashtirishim kerak boʻlardi…

Uf…

### π uchun Text vidjeti

`Text` — matn sohalarini formatlash va nozikroq boshqaruvga ega kuchliroq vidjet.

Barcha narsalarning zulmati va hafsalasi pirligi ichida [barcha dasturchilarning yoʻlchi yulduzi va yagona nur shuʼlasi](http://stackoverflow.com){: hreflang=en } tufayli — u yerda meni oldingi boʻlimda boshlagan holatimga oʻxshash [postga](https://stackoverflow.com/questions/40992931/python-easiest-way-to-define-multiple-global-variables){: hreflang=en } va Tkinter [hujjatlariga](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en } yoʻnaltirishdi — orzuim roʻyobga chiqdi:

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

Manba: [legacy/pi.py, 101–134-qatorlar](legacy/pi.py#L101-L134); vidjetni yaratish — [248-qator](legacy/pi.py#L248)

Gʻoya oʻsha-oʻsha qoldi — matn oʻzgarishi hodisasini ushlash — lekin amalga oshirilishi yaxshilandi. Bir necha jihat.

1.  Oxirgisidan boshlab barcha harflar boʻylab while sikli oʻrniga ikkilik qidiruv.

```python
if (actual_width  > max_width * max_height):
    # the original text won't fit. Keep shrinking until it does
    ilast = bisect.bisect_left(KeyList(text, key=lambda x,i:
                                       self.font.measure(text[:i]+ '...')),
                                       max_width * max_height)
```

Manba: [legacy/pi.py, 117–121-qatorlar](legacy/pi.py#L117-L121)

`bisect`da solishtiriladigan qiymat uchun key parametri yoʻqligi sababli, oʻram yozishga toʻgʻri keldi:

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

Manba: [legacy/pi.py, 91–99-qatorlar](legacy/pi.py#L91-L99)

U qidiruvga harf oʻrniga matnning boshidan shu harfgacha boʻlgan kengligini beradi.

2\. Shriftning aniq balandligi oʻrniga koeffitsiyent tanladim: qatorlar koʻchishi tufayli kenglikni balandlikka koʻpaytirish baribir aniq oʻlchamni bermaydi.

```python
self.font_height = 46.8   # instead of self.font.metrics('linespace')
```

Manba: [legacy/pi.py, 107-qator](legacy/pi.py#L107)

Koeffitsiyent matn oxirini vidjet oxiriga imkon qadar yaqin qoʻyadi, lekin, albatta, baʼzan adashadi:

<img width="1071" height="105" alt="font_height" src="https://github.com/user-attachments/assets/c2254737-5e6c-4251-9eeb-fe905d76fc0d" />

3\. `Text` belgilar boʻyicha oʻzi koʻchira oladi.

```python
wrap=tk.CHAR
```

4\. `Text` oʻz qism satrlarini ajratib koʻrsata oladi. Topilgan qism satrni qizil rangda ajratib koʻrsatish:

```python
self.tag_add("highlight", "1."+str(index), "1."+str(index+8))
self.tag_config("highlight", background=frame["bg"], foreground="red")
```

Manba: [legacy/pi.py, 130–131-qatorlar](legacy/pi.py#L130-L131)

5\. Vidjetni har qanday oʻzgartirishni taqiqlash:

```python
lb3.config(state=tk.DISABLED)
```

Manba: [legacy/pi.py, 255-qator](legacy/pi.py#L255)

`Text` ajralib turmasligi uchun, xuddi `Label`dagidek, uning `background`i asosiy oyna rangiga oʻrnatiladi:

```python
bg=frame["bg"]
```

Ishga tushishda `Text`ga boshlangʻich maʼlumot qoʻshamiz:

```python
LONG_ARRAY = read_pi(1,2500)
lb3.insert(tk.END, LONG_ARRAY)
```

Manba: [legacy/pi.py, 204-qator](legacy/pi.py#L204) va [254-qator](legacy/pi.py#L254)

Hodisa ishlovchisida maʼlumotni keraklisiga almashtiramiz:

```python
self.delete(1.0, tk.END)   # first delete the old data, starting from char 0 of line 1,
self.insert(tk.END, text)  # then insert the new data at the end of the text
```

Manba: [legacy/pi.py, 125–126-qatorlar](legacy/pi.py#L125-L126)

Koʻrib turganingizdek, maʼlumot `Label`dagidan boshqacha qoʻshiladi: uni qatorma-qator, qaysi qatorga yozishni koʻrsatib qoʻshish mumkin. Men bu bilan ovora boʻlmadim va faqat bitta qator bilan ishlayman.

Bir marta boʻlsa ham nimadir oʻrnatilgan vositalar bilan qilindi, bu allaqachon _katta gʻalaba_.

"Find" tugmasini bosish yoki Enterni bosish orqali ishga tushadigan sanalar bazasidan qidiruv kodi:

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

Manba: [legacy/pi.py, 136–162-qatorlar](legacy/pi.py#L136-L162)

Koʻrib turganingizdek, endi `Text`ni hatto koddan oʻzgartirish uchun ham avval uni oddiy holatga qaytarish, tarkibni oʻzgartirish va keyin oʻzgartirishni yana taqiqlash kerak.

Tasodifiy siljish yangi sana uchun ajratib koʻrsatilgan moslik toʻgʻri ekanini va π sonining boshqa (ehtimol, uzoqdagi) fragmentida joylashganini yaqqol koʻrsatadi.

Oʻziga xos optimallashtirish shundaki, π sonining faqat kerakli kichik fragmenti yuklanadi. Oʻqish tez va interfeysda kechikishlarga olib kelmaydi. π sonining butun ulkan faylini xotirada saqlash va uni ishga tushishda oʻqish juda isrofgarchilik boʻlardi.

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

Manba: [legacy/pi.py, 164–173-qatorlar](legacy/pi.py#L164-L173)

### Joylashuv

Avvaliga dasturni birinchi va eng oddiy joylashtiruvchi — `pack()` bilan qurishni oʻyladim. Rejaga koʻra, buning uchun asosiy `Text` oyna oʻlchamiga toʻgʻri choʻzilishi uchun obyektlarni guruhlash kerak edi.

Birinchidan, uchta obyektdan iborat sarlavhani — taklif yozuvi, sana kiritish maydoni va tugmani — `Frame` guruhiga, `win_header`ga joyladim.

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

Ikkinchidan, asosiy qism uchun `win_body` guruhi va uning ichida uchta belgi raqami boʻlgan chap ustun `winbl` kerak edi: koʻrsatilgan birinchi belgi, topilgan sana boshi va koʻrsatilgan oxirgi belgi.

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

_Bu `pack()` versiyasi yakuniy kodga kirmadi._

Lekin keyinroq grid() joylashtiruvchisini oʻzlashtirib oldim va hammasini u bilan qildim.

### grid joylashtiruvchisi

Asosiy oynaning barcha vidjetlari uchun `frame` guruhini yaratdim va unda 11 ustun va 7 qatordan iborat virtual toʻr belgiladim.

Mulohazam shunday edi: taklif yozuvi, sana kiritish maydoni va tugma birinchi qatorga tushadi; taklif yozuvi 4 ustunni egallaydi, sana kiritish maydoni undan keyin keladi va 3 ustunni egallaydi, tugma esa oʻngda va 2 ustunni egallaydi. Ularga katakchalari bilan birga barcha yoʻnalishlarda choʻzilishga (sticky) ruxsat berdim.

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

Manba: [legacy/pi.py, 213–224-qatorlar](legacy/pi.py#L213-L224)

Qolgan elementlar ham xuddi shunday joylashtirildi. Koʻrib turganingizdek, eng koʻp joyni `Text` — `lbt` egallaydi:

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

Manba: [legacy/pi.py, 225–249-qatorlar](legacy/pi.py#L225-L249)

Eng oxirida katakchalar vaznlarini belgiladim: vazn qancha katta boʻlsa, asosiy oyna masshtablanganda katakcha shuncha koʻp oʻzgaradi.

```python
for y in range(1,11): tk.Grid.columnconfigure(frame, y, weight=1)
for x in range(2,6): tk.Grid.rowconfigure(frame, x, weight=1)
```

Manba: [legacy/pi.py, 250–253-qatorlar](legacy/pi.py#L250-L253)

### Dasturni optimallashtirish

Hammasi yozilib, debug qilingach, yengil sinov dastur kechirib boʻlmas darajada sekin ishga tushishini koʻrsatdi. Hammasi matnli faylni oʻqish tufayli.

π faylini oʻqishdan qochishga muvaffaq boʻldim. Lekin sanalar bazasini faylidan toʻliq oʻqishdan qochib boʻlmaydi. Bu ikki ustunli jadval: sana satri, tabulyatsiya va siljish.

Shunday qilib, uni qanday tez oʻqishni aniqlashim kerak edi. Oddiy tajriba:

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

Vaqt Pythonning standart vositasi timeit bilan oʻlchandi.

Natijalar:

```
readfile 6.3322045118 secs.
csv file 4.1212712648 secs.
pd  file 4.4932071859 secs.
pd csvrd 350.0057260714 secs.
loadtxt  41.6930684601 secs.
```

csv yutadi. Baribir sekin. Yakuniy `read_db`: [legacy/pi.py, 189–193-qatorlar](legacy/pi.py#L189-L193).

Shuning uchun ogʻir artilleriyani — koʻp oqimlilikni ishga soldim: forma yuklanayotganda sanalar matnli faylini fonda oʻqish.

```python
# a thread that reads the text file
class Worker(threading.Thread):
    ''' thread to read the dates DB from the text file '''
    def run(self):
        global DB
        DB = read_db()
WORKER = Worker() # an instance of the thread that reads the DB from the file
```

Manba: [legacy/pi.py, 27–32-qatorlar](legacy/pi.py#L27-L32)

GUI-dasturlashda ancha keng tarqalgan bu holat uchun — ogʻir hisoblashlar paytida formani javob beradigan holatda saqlash — Tkda maxsus funksiyalar bor. Bizga hodisalar siklining 10 millisekundidan keyin bizning funksiyamizni, bu yerda `listen_for_result()`ni, chaqiradigan `after()` kerak.

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

Manba: [legacy/pi.py, 195–200-qatorlar](legacy/pi.py#L195-L200) va [208–209-qatorlar](legacy/pi.py#L208-L209)

U oqim tugagan boʻlsa, unga qoʻshilishga (join) harakat qiladi, tugamagan boʻlsa, Tkga yana 10 millisekund kutishni rejalashtiradi.

Shunday qilib, salmoqli matnli fayl oyna bilan parallel yuklanadi, bu ham ogʻir amal. _Gʻalaba_.

Bitta nozik jihat qoladi: agar foydalanuvchi fayl oʻqilib boʻlinmasidan sana kiritsa — bu juda kam ehtimolli, lekin baribir — oqim tugashini kutamiz va keyin tayyor bazadan qidiramiz:

```python
def bt_find_click(event=None):
    # ...
    if WORKER.is_alive():
        WORKER.join()
    # ...
```

Manba: [legacy/pi.py, 140–141-qatorlar](legacy/pi.py#L140-L141)

### Toʻliq dastlabki kod

Toʻliq kod [legacy/pi.py](legacy/pi.py)da.

<img width="1080" height="557" alt="interfeys" src="https://github.com/user-attachments/assets/81283f68-b27a-4b1d-8242-a384d49153bd" />

### Lokalizatsiya

Kodga qattiq yozilgan satrlar oʻrniga satrlar konfiguratsiya faylidan oʻqiladi: [legacy/pi.py, 175–187-qatorlar](legacy/pi.py#L175-L187).

<img width="1080" height="565" alt="lokalizatsiya" src="https://github.com/user-attachments/assets/36be95e5-22fa-42e1-982e-cf63ec3ea86a" />

### Bajariladigan fayl

Faqat .exe yigʻish qoldi — bu konsol buyrugʻi bilan bajariladi (agar Anaconda oʻrnatilgan boʻlsa):

```
pyinstaller --onefile pi.py --noconsole
```

noconsole — Tk konsoldan ishga tushiriladi, shuning uchun formadan oldin terminal paydo boʻladi; u bizga kerak emas va bu bayroq uni olib tashlaydi.

### Havolalar

-   https://stackoverflow.com/questions/30257574/how-to-get-the-widgets-current-x-and-y-coordinates
-   https://docs.python.org/2.7/library/ttk.html#label-options
-   https://www.tcl.tk/man/tcl/TkCmd/event.htm
-   https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
-   http://effbot.org/tkinterbook/text.htm
-   https://www.tutorialspoint.com/python/tk\_text.htm
-   https://www.tutorialspoint.com/python/tk\_button.htm
-   https://www.tutorialspoint.com/python/tk\_entry.htm
-   https://www.tutorialspoint.com/python/tk\_frame.htm
-   https://www.tutorialspoint.com/python/tk\_label.htm
-   https://www.tutorialspoint.com/python/tk\_pack.htm
-   https://www.tutorialspoint.com/python/tk\_grid.htm
-   https://stackoverflow.com/questions/52062162/python-tkinter-how-to-count-the-quantity-of-characters-can-be-shown-in-expandi/52066664#52066664
-   http://zetcode.com/gui/tkinter/layout/
-   https://stackoverflow.com/questions/3950687/how-to-find-out-the-current-widget-size-in-tkinter
-   https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
-   http://effbot.org/tkinterbook/label.htm
-   https://www.reddit.com/r/learnpython/comments/6dndqz/how\_would\_you\_make\_text\_that\_automatically\_wraps/
-   https://stackoverflow.com/questions/25936958/tkinter-entry-validation-not-working
-   http://effbot.org/tkinterbook/variable.htm
-   http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/entry-validation.html
-   https://stackoverflow.com/questions/13242970/tkinter-entry-box-formatted-for-date
-   https://stackoverflow.com/questions/51143777/display-three-dots-in-the-end-of-a-tkinter-label-text
-   https://stackoverflow.com/questions/42146482/using-bisect-on-list-of-tuples-but-compare-using-first-value-only
-   http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
-   https://stackoverflow.com/questions/48726956/measure-the-height-of-a-string-in-tkinter-python
-   https://stackoverflow.com/questions/270648/tkinter-invoke-event-in-main-loop
-   https://arrow.readthedocs.io/en/latest/#arrow.arrow.Arrow
-   https://docs.python.org/2/library/bisect.html
-   https://www.tutorialspoint.com/python/file\_seek.htm
-   https://stackoverflow.com/questions/10624937/convert-datetime-object-to-a-string-of-date-only-in-python
-   https://stackoverflow.com/questions/14288498/creating-a-loop-for-two-dates/14288620
-   https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large
-   https://scorython.wordpress.com/2016/06/27/multithreading-with-tkinter/
-   https://stackoverflow.com/questions/42589372/pythontkinter-how-to-run-in-background-independant-of-tk-frontend
-   https://docs.python.org/2/library/threading.html
-   http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354
