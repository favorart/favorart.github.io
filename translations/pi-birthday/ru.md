---
title: "День рождения в цифрах числа π"
summary: "Небольшое GUI-приложение на Python/Tkinter, которое ищет дату рождения среди 3 миллиардов знаков π, — позже переделанное для веба."
source: favorart/pi-birthday@main:article.md
source_lang: en
source_hash: 926233cf
translated: 2026-11-14
translator: Kirill Golikov (author), adapted by Claude
reviewed: 2026-11-14
---

# Графическое приложение на Python

[English](article.md){: hreflang=en } · **Русский**

_Статья 2018 года о первой, десктопной версии (Python 2.7 + Tkinter). Исходная публикация: [ВКонтакте](https://vk.ru/@33453621-pi-gui-python). Полный код — [legacy/pi.py](legacy/pi.py), запустить его сегодня можно скриптом [legacy/run.sh](legacy/run.sh)._

Время от времени встаёт передо мной вопрос о написании небольших оконных приложений. Обычно приложения пишу на C++. Но в своё время вместо Qt изучал WindowsAPI, т.к. окна всегда нужны были для Windows, считаю, что нативный интерфейс всегда лучший. Хочется, чтобы всё смотрелось органично. WinAPI позволяет сделать всё, что может Windows, но много чего приходится писать в коде самому, всегда нужны какие-то плюшки и свистульки.

На WinAPI нельзя мышкой накидать контролы интерфейса, в студии нет дизайнера для этого слоя **:(** (не считая хитрых обходных путей с диалогами вместо форм). Есть, конечно, уровни повыше — MFC и WPF. Но первый имеет очень странную и непростую организацию классов, в которой очень не хочется детально разбираться. А второй прекрасен всем, кроме того, что это C#, т.е. желая писать на C++, нужно использовать managed code и вызывать функции .NET framework.

Бог с ним, со всем этим… Чаще всего проще написать любое приложение на python.

Давайте разберёмся, так ли это.

### Tkinter

**Tkinter** – это пакет python, предназначенный для работы с библиотекой Tk, написанной на языке программирования Tcl. Этот пакет просто преобразовывает код python в команды на Tcl.

### Виджет

**Виджет** (**widget**) – элементы интерфейса (Control в терминологии WinAPI) объекты, порожденные встроенными классами.

-   `Button` – кнопка
-   `Entry` – однострочное текстовое поле ввода
-   `Frame` — группа виджетов
-   `Label` – область на окне, в которой может располагаться картинка или статичный текст
-   `Text` – многострочное поле ввода

и др.

Любой граф.интерфейс работает в парадигме событийно-ориентированного программирования, т.е. та или иная часть программного кода начинает выполняться лишь тогда, когда случается то или иное событие.

```c
// цикл обработки событий в WinAPI - самая главная функция оконного приложения
LRESULT CALLBACK WndProc(HWND hWnd, UINT messg, WPARAM wParam, LPARAM lParam)
{
    switch (messg)
    {
    case WM_PAINT: //нарисовать окно
      onWindowPaint(hWnd);
      break;
    case WM_DESTROY: //уничтожить окно нажатием на крестик
      PostQuitMessage(0);
      break;
    case WM_ERASEBKGND: //какие-нибудь ещё события
      return 1;
    }
    return DefWindowProc(hWnd, messg, wParam, lParam); //обработка событий по умолчанию самой ОС
}
```

### События

События бывают разными, их может вызывать: таймер, пользователь, система, сами виджеты и пр. Событий очень много, для каждого есть обработчик по умолчанию или пустой. При получении события происходит срабатывание определенной части кода программы. Обычно своя логика в программу добавляется в обработчиках событий.

Минимальное приложение выглядит так:

```python
try:
    import tkinter as tk    # >= python 3.0
except ImportError:
    import Tkinter as tk    # >= python 2.7

root = tk.Tk()  # создаём главное окно
root.mainloop() # запускаем цикл получения и обработки событий
```

В функции `mainloop()` написан бесконечный цикл. Код, написанный после этой функции, выполнится только после выключения приложения. Выход из цикла происходит, например, по событию нажатия на крестик.

Общий план создания GUI-программы:

-   Создать главное окно.
-   Создать доп. окна и виджеты, выполнить их конфигурацию, добавить виджеты на главное или другие окна.
-   Определить интересующие события и их обработчики — то: куда будет вставлен пользовательский код, и как будет реагировать программа.
-   Запустить цикл обработки событий.

### Конфигурация виджетов

Создадим первый виджет — статичный текст в окне, менять который пользователь не сможет

```python
tk.Label(root, text="This label")
```

Но текст можно изменять программно, если вместо параметра `text`, подключить строковую переменную, меняя её значение тут же будет меняться и текст на `Label`

```python
lb_text = tk.StringVar()
lb_text.set("1")
tk.Label(root, textvariable=lb_text, width=10, font=dFont, anchor=tk.NW)
```

Исходник: [legacy/pi.py, стр. 227–230](legacy/pi.py#L227-L230)

Параметр `font` меняет вид шрифта, я заранее подготовил более крупный читаемый шрифт интерфейса:

```python
import tkFont
dFont = tkFont.Font(family="Arial", size=30)
```

Исходник: [legacy/pi.py, стр. 211](legacy/pi.py#L211)

Параметр `anchor` определяет выравнивание у виджета — в нашем случае это NORTH-WEST, т.е. текст прижимается к верхнему левому краю виджета.

Устанавливать свойства объектов не обязательно при их создании.

Обратите внимание, что первым аргументом указывается "хозяин", "мастер" – место, где располагается виджет. В данном случае его можно было не указывать, т.к. по умолчанию это `root`. Однако виджеты не обязательно располагаются прямо на главном окне (`root`), они могут размещаться и в других виджетах.

### Пользовательские обработчики событий

У функций — обработчиков событий, которые вызываются при наступлении события должен быть один параметр. Обычно его называют `event` (событие).

С помощью метода `bind` можно связать обработчик с событием библиотеки Tk:

```python
def bt_find_click(event):
    pass

root.bind('<Return>', bt_find_click)
```

Исходник: [legacy/pi.py, стр. 210](legacy/pi.py#L210)

Ему передается имя события и вызываемая функция. Событие со всеми его параметрами будет передано в функцию и присвоено аргументу `event`. В данном случае событием является нажатие на клавишу Enter, что обозначается строкой `'<Return>'`.

### Расположение виджетов в окне

Хотя я отчаянно бежал от WinAPI за графическим редактором интерфейса. У Tkinter из коробки его тоже не оказалось **:(** Сжав зубы, я начал читать, как же разработчики без него живут и, на своё удивление, они вышли из положения довольно удобно и элегантно.

### Упаковщики

\[Источник: [Хабр](https://habr.com/post/133337/)\]

**1 pack()** — это функция, так называемый упаковщик, или менеджер расположения. Он отвечает за то, как виджеты будут располагаться на главном окне. Для каждого виджета нужно вызвать метод упаковщика, иначе он не будет отображён. Всего упаковщиков три:

pack автоматически размещает виджеты в родительском окне. Имеет параметры:

side – с какого бока добавлять очередной элемент,

fill – растягивать ли его в каком-то направлении до границ окна,

expand – замостить ли весь родительский объект данным виджетом.

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

**2 grid()** размещает виджеты на сетке. Основные параметры:

row/column – строка/столбец в сетке,

rowspan/columnspan – сколько строк/столбцов занимает виджет.

sticky — как растягивать виджет вместе с увеличением ячейки, в которой он находится: к каким краям ячейки NWSE приклеивать виджет.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').grid(row = 1, column = 1)
Button(root, text = '2').grid(row = 1, column = 2)
Button(root, text = '__3__').grid(row = 2, column = 1, columnspan = 2)
root.mainloop()
```

<img width="137" height="94" alt="2-grid" src="https://github.com/user-attachments/assets/1da19342-4b45-406e-ae00-fb29dfd5bc18" />

**3 place()** позволяет размещать виджеты в указанных координатах с указанными размерами. Основные параметры: x, y, width, height.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').place(x = 10, y = 10, width = 30)
Button(root, text = '2').place(x = 45, y = 20, height = 15)
Button(root, text = '__3__').place(x = 20, y = 40)
root.mainloop()
```

<img width="139" height="139" alt="3-place" src="https://github.com/user-attachments/assets/f6ecb75e-e579-4d53-a7a9-653519d72954" />

Пока Вы не вызвали какой-то упаковщик для виджета, логично, что он не отображается.

### Постановка задачи

Теперь о примере, реализацию которого я хочу Вам рассказать.

Существует гипотеза о том, что число π — [нормальное](http://www.etudes.ru/ru/sketches/normal-number-pi), т.е., что в нём можно найти любую наперёд заданную последовательность цифр конечной длины.

Чтобы удивить детей и взрослых на [фестивале науки](http://www.festivalnauki.ru) подглядели вот такой [аттракцион](http://www.etudes.ru/ru/sketches/normal-number-pi/): _вводишь дату своего рождения, а программа говорит, на каком символе в строке π её можно найти_.

Соответственно, нужно было посчитать π с точностью до достаточно много знаков, пройтись по всем датам от 1го года Н.Э. до 9999 года Н.Э., и найти их ближайшие смещения в строке π.

### Подсчёт π

Готовая программка по подсчёту π была найдена в [интернетах](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354). На ней было подсчитано 3 миллиарда знаков после запятой. Получился текстовый файл размером почти 3 Гб.

Далее оказалось, что python 2.7, на котором я обычно пишу программки, [не дружит](https://ozymaxx.github.io/blog/2018/05/29/python-strftime){: hreflang=en } с датами до 1900 года. Для перечисления дат была взята библиотека [arrow](http://arrow.readthedocs.io){: hreflang=en }, которая прекрасно справилась:

```python
start_date = arrow.Arrow(0001, 1, 1), end_date = arrow.Arrow(9999, 12, 30)
with open('dates.txt', 'w') as dates:
        for single_date in arrow.Arrow.range('day', start_date, end_date):
            print >>dates, single_date.format(fmt='DDMMYYYY')
```

Был сгенерирован файл со всеми возможными датами с четырёхзначным положительным годом, с учётом високосных и пр.

Далее нужно было записать даты ключами в словарь, пройтись по всем подстрокам π, и значениями в этот словарь записать — смещения, относительно десятичной точки, первых появлений каждой даты.

Оказалось, что python 2.7 также имеет ограничения по величине значения итератора [оператора](https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large){: hreflang=en } `range()`, код вышел таким:

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

_Эти подготовительные скрипты в `legacy/` не вошли; в веб-версии их заменяет [tools/build_index.py](tools/build_index.py)._

Всё, подготовительный этап пройден.

Дело осталось за малым — графический интерфейс.

### Графический интерфейс

План интерфейса следующий:

<img width="807" height="579" alt="plan" src="https://github.com/user-attachments/assets/a718d644-af95-4aa8-8da3-48d56f8265bd" />

1.  Зафиксировать минимальный размер окна.
2.  Валидируемый ввод даты, чтобы нельзя было ввести некорректную дату.
3.  Научиться позиционировать текст на `Label`, чтобы он переносился по символам, кроме того, выводилось бы ровно столько текста, сколько помещается на экране.
4.  Оперативная подгрузка из файла и отображение нужной области числа π.
5.  Нужно уметь подсвечивать найденную подстроку среди всех символов.
6.  Размещение объектов. Поместить заголовок из трёх нерастяжимых объектов, а также остальные растяжимые объекты под ними.
7.  Оптимизация работы приложения.

Начнём с простого.

### Минимальный размер окна

```python
root.geometry("1280x640") # размер окна по умолчанию при старте приложения
root.minsize(680, 340)    # минимальный размер окна, чтобы виджеты не схлопывались в точку
```

Исходник: [legacy/pi.py, стр. 206–207](legacy/pi.py#L206-L207)

### Валидация ввода

Для ввода даты был выбран виджет `Entry` (аналог Textbox из WinAPI). Логику ввода только даты Н.Э. решил реализовать самостоятельно через валидацию вводимых символов на лету.

Иллюстрация [общей схемы валидации](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en } текстового ввода пользователя в любой виджет библиотеки Tk выглядит следующим образом:

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

Таким образом, из этого всего, мне нужен был только параметр `'%P'` — _совокупный новый ввод_. Если он целиком, при вводе очередного символа, не является датой, то оставляем то, что было введено до последнего символа, иначе добавляем символ к содержимому `Entry`.

Для полной даты используем ту же самую arrow. Итоговый виджет `DateEntry`: [legacy/pi.py, стр. 34–89](legacy/pi.py#L34-L89).

### Настройка виджета числа π

Изначально я планировал использовать статический текст для размещения числа Пи. Он хорошо подходит для тех случаев, когда нужно ограничить пользователей в возможностях выделения, копирования и изменения отображённого текста.

Из коробки `Label` не умеет переносить текст на новые строки посимвольно. Был найден [способ](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps){: hreflang=en } переносить по буквам — длина принудительного переноса устанавливалась равной ширине виджета:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
# ...
lbt = WrappingLabel(root, textvariable=lbt_text, font=dFont, anchor=tk.NW, justify=tk.LEFT)
```

justify — прижимаем многострочный текст к левому краю `Label`.

Далее нужно было уменьшать предлагаемый к отображению текст в соответствии с объёмом, который можно отобразить на экране.

Для этого я начал писать новый велосипед с перехватыванием события изменения размеров главного окна:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', self.fit)         # перехват события вставки и изменения текста
        self.font = tkFont.nametofont(self["font"])                   # получение шрифта виджета
        self.font_height = self.font.metrics('linespace')             # высота шрифта в пикселях

    def fit(self, event):
        # ширину виджета в символах получаем из события
        max_width = event.width
        # число строк, влезает по высоте, с учётом шрифта
        max_height = event.height / self.font_height
        # изменённый текст
        text = lbt_text.get()
        # текущая ширина текста в символах
        actual_width = self.font.measure(text)
        # уменьшаем текст, пока он полностью не влезет в виджет
        while (actual_width > (max_width * max_height) and len(text) > 1):
            text = text[:-1]
            actual_width = font.measure(text + "...")
        # запоминаем полученный результат
        lbt_text.set(text + '...')
        # продолжаем переносить по-символьно внутри виджета
        return self.config(wraplength=self.winfo_width())

last_event_H, last_event_W = 0, 0 # старые размеры lbt - высота и ширина

def sizing(event):
    ''' Main window size changing Event handler '''
    global last_event_H, last_event_W
    if (event.width == last_event_W and event.height == last_event_H):
        return # если размер не изменился
    last_event_H, last_event_W = event.height, event.width
    # вызываем событие вручную, для подгонки вставленного текста
    lbt.event_generate("<Configure>", when="now",
                       width=lbt.winfo_width(), height=lbt.winfo_height())
# ...
root.bind("<Configure>", sizing) # соединяем пользовательский обработчик с событием
```

В итоге, пришлось отказаться от виджета `Label`. В первую очередь из-за невозможности подкрашивания найденной подстроки из коробки. Пришлось бы создавать динамический `Label` поверх статического, вычислять координаты положения подстроки в окне, располагать там новый `Label` с новым цветом…

Ох…

### Виджет Text для числа π

Более мощный виджет `Text` с возможностями форматирования областей текста и более тонкой настройкой.

Благодаря [путеводной нити всех программистов и единственному светлому лучику](http://stackoverflow.com){: hreflang=en } во тьме и разочаровании всего сущего, где мне подсказали [статью](https://stackoverflow.com/questions/40992931/python-easiest-way-to-define-multiple-global-variables){: hreflang=en } с аналогичным кейсом, к решению которого я приступил в предыдущем параграфе, а также [документации](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en } к Tkinter, моя мечта осуществилась:

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

Исходник: [legacy/pi.py, стр. 101–134](legacy/pi.py#L101-L134), создание виджета — [стр. 248](legacy/pi.py#L248)

Идея осталась та же с перехватом события изменения текста, улучшилась её реализация. Несколько пунктов.

1.  Вместо while по всем буквам начиная с последней — бинарный поиск.

```python
if (actual_width  > max_width * max_height):
    # the original text won't fit. Keep shrinking until it does
    ilast = bisect.bisect_left(KeyList(text, key=lambda x,i:
                                       self.font.measure(text[:i]+ '...')),
                                       max_width * max_height)
```

Исходник: [legacy/pi.py, стр. 117–121](legacy/pi.py#L117-L121)

Т.к. бинарный поиск не имеет параметра `предикат` вычисления ключа, по которому нужно сортировать, пришлось написать `обёртку`.

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

Исходник: [legacy/pi.py, стр. 91–99](legacy/pi.py#L91-L99)

Вместо буквы — подставляет поиску длину от начала до неё самой.

2\. Вместо точной высоты шрифта подобрал коэффициент, из-за переносов на новые строки — ширина умноженная на высоту — всё же не точный размер.

```python
self.font_height = 46.8   # вместо self.font.metrics('linespace')
```

Исходник: [legacy/pi.py, стр. 107](legacy/pi.py#L107)

Коэффициент максимально близко располагает конец текста к концу виджета, но, конечно, иногда ошибается:

<img width="1071" height="105" alt="font_height" src="https://github.com/user-attachments/assets/c2254737-5e6c-4251-9eeb-fe905d76fc0d" />

3\. `Text` умеет переносить побуквенно сам.

```python
wrap=tk.CHAR
```

4\. `Text` умеет подсвечивать собственные подстроки. Подсветка найденной подстроки в красный цвет:

```python
self.tag_add("highlight", "1."+str(index), "1."+str(index+8))
self.tag_config("highlight", background=frame["bg"], foreground="red")
```

Исходник: [legacy/pi.py, стр. 130–131](legacy/pi.py#L130-L131)

5\. Запрещаем любую модификацию этого виджета:

```python
lb3.config(state=tk.DISABLED)
```

Исходник: [legacy/pi.py, стр. 255](legacy/pi.py#L255)

Чтобы `Text` не выделялся, как и `Label`, задний фон — `background` — делаем таким же, как цвет главного окна:

```python
bg=frame["bg"]
```

Добавляем некоторые начальные данные в `Text` при старте программы:

```python
LONG_ARRAY = read_pi(1,2500)
lb3.insert(tk.END, LONG_ARRAY)
```

Исходник: [legacy/pi.py, стр. 204](legacy/pi.py#L204) и [стр. 254](legacy/pi.py#L254)

Заменяем данные на нужные в обработчике события:

```python
self.delete(1.0, tk.END)   # сначала удаляю старые данные, начиная с 0го символа 1й строки,
self.insert(tk.END, text)  # затем вставляю новые данные в строку в конец текста
```

Исходник: [legacy/pi.py, стр. 125–126](legacy/pi.py#L125-L126)

Как можно видеть, данные добавляются не так, как в `Label`, можно добавлять построчно, указывая в какую строку записывать. Я не стал с этим запариваться, работаю лишь с одной строкой.

В кои-то веки что-то было сделано встроенными средствами, что уже является _большой победой_.

Код поиска в базе дат, выполняющийся по клику на кнопку «Найти» или по нажатию Enter, выполнен следующим образом:

```python
def bt_find_click(event=None):
    global LONG_ARRAY, FN_LOG_DATES, DB
    global lb_first_text, lb_last_no_text, lb_found_no_text, lb3
    # размещаем в Тексте хоть сколько-то символов Пи
    first, last = 1, 2500
    # получаем введённую дату
    ddate = tb_date.get()
    if (not DB.has_key(ddate)): # если дата не введена пользователем
        lb_found_no_text.set("--")
    else:
        # получаем смещение этой даты относительно десятичной точки
        index = int(DB[ddate])
        # получаем число отображённых символов в текущий момент в Тексте
        last = int(lb_last_no_text.get()) - int(lb_first_text.get())
        # вычисляем случайное положение найденной подстроки для отображения в окне
        last_of = random.randint(9, 100) if (last > 100) else 9
        offset = random.randint(10, last - last_of)
        # вычисляем начало и конец отображаемого фрагмента числа Пи
        first = (index - offset) if (index > offset) else 1
        last = index + last
        # отображаем смещение найденной даты в соответствующем для этого виджете
        lb_found_no_text.set(str(index))
    # отображаем новые границы показанного фрагмента Пи в нужных виджетах
    lb_first_text.set(str(first))
    lb_last_no_text.set(str(last))
    # считываем нужный фрагмент Пи из файла
    LONG_ARRAY = read_pi(first, last-first)

    lb3.config(state=tk.NORMAL)        # разрешаем редактирование Текста
    lb3.event_generate("<Configure>",             # здесь мы собственноручно вызываем событие
                       when="now",                # прямо сейчас
                       width=lb3.winfo_width(),   # и задаём параметры аргумента Event, а именно
                       height=lb3.winfo_height()) # актуальную ширину и высоту самого виджета
    lb3.config(state=tk.DISABLED)      # запрещаем редактирование
```

Исходник: [legacy/pi.py, стр. 136–162](legacy/pi.py#L136-L162)

Как можно видеть, чтобы модифицировать теперь `Text` даже программно нужно возвращать его сначала в нормальное состояние, менять содержимое, а потом снова отключать возможность модификации.

Случайное смещение добавлено для того, чтобы явно выделить: для новой даты подсвеченное совпадение является правильным и находится в другом (возможно далёком) фрагменте числа Пи.

Своего рода оптимизацией является то, что подгружается только маленький нужный фрагмент числа Пи. Но при этом считывание происходит быстро и не вызывает задержек в интерфейсе. Хранить в памяти весь огромный файл Пи и считывать его во время старта программы было бы сильным расточительством.

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

Исходник: [legacy/pi.py, стр. 164–173](legacy/pi.py#L164-L173)

### Размещение объектов

Изначально, думал, делать программу с помощью первого самого простого упаковщика — `pack()`. Согласно плану для этого нужно было объединить объекты в группы, чтобы правильно растянуть основной `Text` в размер окна.

Во-первых, выделил в группу `Frame` головную часть из трёх объектов окна: приглашение, ввод-даты и кнопку — `win_header`.

```python
# ...
win_header = tk.Frame(root, padx=10, pady=2)
# padx и pady - задал отступы для расположения элементов внутри группы
win_header.pack(side=tk.TOP, fill=tk.X)
# добавить группу на главное окно со стороны верха (TOP)
# растянуть по горизонтали (Х) на всю ширину окна
# добавляем в группу Приглашение слева
lb_invite = tk.Label(win_header, text="Input your birth date", font=dFont,
                     anchor=tk.NW, width=20)
lb_invite.pack(side=tk.LEFT)
# добавляем в группу Entry сразу за Приглашением слева
lb_date = DateEntry(win_header, font=dFont)
lb_date.pack(side=tk.LEFT)
# кнопку прикрепляем справа
bt_find = tk.Button(win_header, text="Find", font=dFont, command=bt_find_click, pady=2)
bt_find.pack(side=tk.RIGHT)
# ...
```

Во-вторых, потребовались группы: основной части `win_body` и внутри неё группа левой колонки `winbl` с тремя номерами символов: первого показанного, начала найденной подстроки с датой и последнего показанного.

```python
# ...
win_body = tk.Frame(root)
win_body.pack(side=tk.TOP, fill=tk.BOTH)
# растягиваем группу в оба направления: вертикальное и горизонтальное
# слева добавляем группу - колонку с номерами символов
winbl = tk.Frame(win_body, width=10)
winbl.pack(side=tk.LEFT, fill=tk.BOTH)
# задаём виджет для номера первого показанного символа
lb_first_no = tk.Label(winbl, textvariable=lb_first_no_text, font=dFont, anchor=tk.NW, width=10)
lb_first_no.pack(side=tk.TOP, fill=tk.X)
# задаём виджет для номера символа начала найденной подстроки
lb_found_no = tk.Label(winbl, textvariable=lb_found_no_text, font=dFont, anchor=tk.NW, width=10)
# задаём виджет для номера последнего показанного символа
lb_last_no = tk.Label(winbl, textvariable=lb_last_no_text, font=dFont, anchor=tk.NW, width=10)
lb_last_no.pack(side=tk.BOTTOM, fill=tk.X)
# задаём основной виджет для отображённого фрагмента числа Пи
lb_digits = WrappingLabel(win_body, textvariable=lb_digits_text, font=dFont,
                          anchor=tk.NW, justify=tk.LEFT)
lb_digits.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
# Растягиваем (expand) этот виджет на всё свободное место в группе,
# а саму группу растягиваем (fill), на всё свободное место в окне
# ...
```

_Эта версия на `pack()` в итоговый код не вошла._

Но позднее распробовал упаковщик grid() и сделал всё с помощью него.

### Табличный упаковщик

Создал группу `frame` для всех виджетов главного окна, в которой наметил виртуальных 11 столбцов и 7 строк.

Прикинул так — приглашение, ввод-даты и кнопка должны находиться в первой строке, при том приглашение должно занимать 4 столбца, ввод-даты идти прямо за ним и занимать 3 столбца, а кнопка должна быть справа и занимать 2 столбца. Разрешил расширяться (sticky) вместе с ячейками, которые они занимают, во всех направлениях.

```python
frame = tk.Frame(root)
tk.Grid.rowconfigure(root, 0, weight=1)
tk.Grid.columnconfigure(root, 0, weight=1)
frame.grid(row=0, column=0, sticky=tk.NSEW)
# Приглашение
lb_invite = tk.Label(frame, text="Input your birth date", font=dFont, anchor=tk.NW)
lb_invite.grid(column=0, row=0, columnspan=4, sticky=tk.NSEW, pady=0, padx=10)
# Ввод-даты
tb_date = DateEntry(frame, font=dFont)
tb_date.grid(column=4, row=0, columnspan=3, sticky=tk.NSEW, pady=10)
# Кнопка
bt_find = tk.Button(frame, text="Find", font=dFont, command=bt_find_click)
bt_find.grid(column=8, row=0, columnspan=2, sticky=tk.NSEW, pady=0)
```

Исходник: [legacy/pi.py, стр. 213–224](legacy/pi.py#L213-L224)

Остальные элементы расставил по аналогии. Как видно, `Text` — `lbt` занимает больше всего места:

```python
# задаём виджет для номера первого показанного символа
lb_first = tk.Label(frame, textvariable=lb_first_text, width=10)
lb_first.grid(column=0, row=2, sticky=tk.NSEW)
# задаём виджет для номера символа начала найденной подстроки
lb_found_no = tk.Label(frame, textvariable=lb_found_no_text)
lb_found_no.grid(column=0, row=4, sticky=tk.NSEW)
# задаём виджет для номера последнего показанного символа
lb_last_no = tk.Label(frame, textvariable=lb_last_no_text)
lb_last_no.grid(column=0, row=6, sticky=tk.NSEW)
# задаём основной виджет для отображённого фрагмента числа Пи
lbt = WrappingLabel(frame)
lbt.grid(column=1, row=1, columnspan=9, rowspan=5, sticky=tk.NSEW)
```

Исходник: [legacy/pi.py, стр. 225–249](legacy/pi.py#L225-L249)

В самом конце установил веса ячеек, чем больше вес, тем сильнее она будет изменять свой размер при масштабировании главного окна.

```python
for y in range(1,11): tk.Grid.columnconfigure(frame, y, weight=1)
for x in range(2,6): tk.Grid.rowconfigure(frame, x, weight=1)
```

Исходник: [legacy/pi.py, стр. 250–253](legacy/pi.py#L250-L253)

### Оптимизация работы программы

Когда всё было написано и отлажено, лёгкое тестирование выявило, что старт программы происходил непростительно долго. Всё это из-за чтения текстового файла.

Хотя удалось избавиться от необходимости считывания файла Пи. Избежать полного считывания базы дат из файла не получится. Она представляет собой таблицу с двумя столбцами — подстрока даты — таб — число-смещение.

Стало быть надо понять — как её считать быстро. Простой эксперимент:

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

Замеры времени проводились timeit - стандартными средствами python.

Результаты следующие:

```
readfile 6.3322045118 secs.
csv file 4.1212712648 secs.
pd  file 4.4932071859 secs.
pd csvrd 350.0057260714 secs.
loadtxt  41.6930684601 secs.
```

Оставляем csv. Всё равно долго. Итоговый `read_db`: [legacy/pi.py, стр. 189–193](legacy/pi.py#L189-L193).

Тогда я подкатил тяжёлую артиллерию — многопоточность — считывание текстового файла с датами в фоне, пока загружается форма.

```python
# определяем поток, который будет читать текстовый файл
class Worker(threading.Thread):
    ''' thread to read the dates DB from the text file '''
    def run(self):
        global DB
        DB = read_db()
WORKER = Worker() # создаём экземпляр этого потока, который считывает БД из файла
```

Исходник: [legacy/pi.py, стр. 27–32](legacy/pi.py#L27-L32)

Для такого случая, что при программировании окон довольно частый — когда хотят, чтобы форма не зависала при производстве сложных вычислений, у библиотеки Tk есть специальные функции. Нас интересует `after()`, которая умеет вызывать через 10 миллисекунд работы цикла событий нашу функцию, здесь `listen_for_result()`.

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

Исходник: [legacy/pi.py, стр. 195–200](legacy/pi.py#L195-L200) и [стр. 208–209](legacy/pi.py#L208-L209)

Которая пробует завершить поток, если он закончил работу, и если ещё нет, снова ставит Tk на ожидание на 10 миллисекунд.

Таким образом, параллельно загрузке окна, что тоже тяжеловесная операция происходит загрузка немаленького текстового файла. _Победа_.

Осталось одно «но»: если пользователь ввёл дату раньше, чем считался файл - что очень маловероятно, но всё же, ждём, пока закончится работа потока, потом производим поиск в готовой БД:

```python
def bt_find_click(event=None):
    # ...
    if WORKER.is_alive():
        WORKER.join()
    # ...
```

Исходник: [legacy/pi.py, стр. 140–141](legacy/pi.py#L140-L141)

### Полный исходный текст программы

Полный код — в [legacy/pi.py](legacy/pi.py).

<img width="1080" height="557" alt="interface" src="https://github.com/user-attachments/assets/81283f68-b27a-4b1d-8242-a384d49153bd" />

### Локализация

Вместо статичных строк, строки считываются из файла конфигурации: [legacy/pi.py, стр. 175–187](legacy/pi.py#L175-L187).

<img width="1080" height="565" alt="localize" src="https://github.com/user-attachments/assets/36be95e5-22fa-42e1-982e-cf63ec3ea86a" />

### Исполняемый файл

Осталось скомпилировать в .exe — это делается с помощью консольной команды (если у Вас на компьютере стоит anaconda):

```
pyinstaller --onefile pi.py --noconsole
```

noconsole — Tk запускается из консоли, то перед запуском формы показывается терминал, который нам не нужен, убираем его данным параметром.

### Использованная литература:

-   [Stack Overflow: How to get the widget's current x and y coordinates](https://stackoverflow.com/questions/30257574/how-to-get-the-widgets-current-x-and-y-coordinates){: hreflang=en }
-   [Python docs: ttk — Tk themed widgets](https://docs.python.org/2.7/library/ttk.html#label-options){: hreflang=en }
-   [Tcl/Tk manual: event](https://www.tcl.tk/man/tcl/TkCmd/event.htm){: hreflang=en }
-   [Stack Overflow: Make the Tkinter Text widget read-only](https://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only){: hreflang=en }
-   [effbot: The Tkinter Text widget](http://effbot.org/tkinterbook/text.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Text](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Button](https://www.tutorialspoint.com/python/tk_button.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Entry](https://www.tutorialspoint.com/python/tk_entry.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Frame](https://www.tutorialspoint.com/python/tk_frame.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter Label](https://www.tutorialspoint.com/python/tk_label.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter pack()](https://www.tutorialspoint.com/python/tk_pack.htm){: hreflang=en }
-   [Tutorialspoint: Tkinter grid()](https://www.tutorialspoint.com/python/tk_grid.htm){: hreflang=en }
-   [Stack Overflow: How many characters fit in an expanding Tkinter label](https://stackoverflow.com/questions/52062162/python-tkinter-how-to-count-the-quantity-of-characters-can-be-shown-in-expandi/52066664#52066664){: hreflang=en }
-   [ZetCode: Tkinter layout management](http://zetcode.com/gui/tkinter/layout/){: hreflang=en }
-   [Stack Overflow: Current widget size in Tkinter](https://stackoverflow.com/questions/3950687/how-to-find-out-the-current-widget-size-in-tkinter){: hreflang=en }
-   [Stack Overflow: Interactively validating Entry content in Tkinter](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en }
-   [effbot: The Tkinter Label widget](http://effbot.org/tkinterbook/label.htm){: hreflang=en }
-   [Reddit r/learnpython: Text that wraps automatically](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps/){: hreflang=en }
-   [Stack Overflow: Tkinter Entry validation not working](https://stackoverflow.com/questions/25936958/tkinter-entry-validation-not-working){: hreflang=en }
-   [effbot: Tkinter variable classes](http://effbot.org/tkinterbook/variable.htm){: hreflang=en }
-   [NMT Tkinter reference: Entry validation](http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/entry-validation.html){: hreflang=en }
-   [Stack Overflow: Tkinter Entry formatted for a date](https://stackoverflow.com/questions/13242970/tkinter-entry-box-formatted-for-date){: hreflang=en }
-   [Stack Overflow: Three dots at the end of a Tkinter label](https://stackoverflow.com/questions/51143777/display-three-dots-in-the-end-of-a-tkinter-label-text){: hreflang=en }
-   [Stack Overflow: bisect on a list of tuples by the first value](https://stackoverflow.com/questions/42146482/using-bisect-on-list-of-tuples-but-compare-using-first-value-only){: hreflang=en }
-   [effbot: Tkinter events and bindings](http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm){: hreflang=en }
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
-   [CyberForum: QBasic thread](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354)
