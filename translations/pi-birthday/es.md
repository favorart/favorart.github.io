---
title: "Tu cumpleaños en las cifras de π"
summary: "Una pequeña aplicación gráfica en Python/Tkinter que encuentra tu fecha de nacimiento entre 3000 millones de cifras de π, luego rehecha para la web."
source: favorart/pi-birthday@main:docs/article.md
source_lang: en
source_hash: aa96f51d
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---
# Una aplicación gráfica en Python

**Español** · [English](article.md){: hreflang=en } · [Русский](article.ru.md){: hreflang=ru }

_Artículo de 2018 sobre la primera versión, de escritorio (Python 2.7 + Tkinter), traducido del ruso. Publicación original: [VK](https://vk.ru/@33453621-pi-gui-python){: hreflang=ru }. Código completo: [legacy/pi.py](../legacy/pi.py); para ejecutarlo hoy, usen [legacy/run.sh](../legacy/run.sh)._

_La continuación de 2026, una versión web que no guarda ni una cifra de π: [π lo guarda todo, así que no tuve que guardar π](/es/writing/pi-stores-everything/)._

De vez en cuando me toca escribir una pequeña aplicación con ventanas. Normalmente escribo aplicaciones en C++. En su día, en lugar de Qt aprendí la API de Windows, porque mis ventanas siempre eran para Windows, y creo que la interfaz nativa siempre es la mejor. Quiero que todo se vea orgánico. WinAPI permite hacer todo lo que puede hacer Windows, pero hay mucho que escribir a mano, y siempre hacen falta algunos adornos.

Con WinAPI no se pueden arrastrar los controles con el ratón: Visual Studio no tiene diseñador para esa capa **:(** (salvo apaños enrevesados usando diálogos en lugar de formularios). Hay niveles más altos, claro: MFC y WPF. Pero el primero tiene una organización de clases muy rara y complicada en la que no me apetece nada meterme. Y el segundo es estupendo en todo, salvo en que es C#: si se quiere escribir en C++, hay que usar código administrado y llamar a funciones de .NET Framework.

En fin… La mayoría de las veces es más fácil escribir cualquier aplicación en Python.

Veamos si es verdad.

### Tkinter

**Tkinter** es un paquete de Python para trabajar con la biblioteca Tk, escrita en el lenguaje de programación Tcl. El paquete simplemente traduce el código Python a comandos Tcl.

### Widgets

Un **widget** es un elemento de la interfaz (un Control en términos de WinAPI): un objeto creado a partir de las clases integradas.

-   `Button`: un botón
-   `Entry`: un campo de texto de una línea
-   `Frame`: un grupo de widgets
-   `Label`: una zona de la ventana que puede contener una imagen o texto estático
-   `Text`: un campo de texto de varias líneas

y otros.

Toda GUI sigue el paradigma de la programación orientada a eventos: un fragmento de código concreto solo se ejecuta cuando ocurre un evento determinado.

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

### Eventos

Hay eventos de muchos tipos: los puede disparar un temporizador, el usuario, el sistema, los propios widgets, etc. Hay muchísimos eventos, y cada uno tiene un manejador por defecto o vacío. Cuando llega un evento, se ejecuta una parte concreta del programa. Normalmente, la lógica propia se coloca en los manejadores de eventos.

Una aplicación mínima se ve así:

```python
try:
    import tkinter as tk    # >= python 3.0
except ImportError:
    import Tkinter as tk    # >= python 2.7

root = tk.Tk()  # create the main window
root.mainloop() # start the loop that receives and handles events
```

`mainloop()` contiene un bucle infinito. El código escrito después de esta llamada solo se ejecuta cuando la aplicación se cierra. Del bucle se sale, por ejemplo, con el evento de pulsar el botón de cerrar.

El plan general de un programa con GUI:

-   Crear la ventana principal.
-   Crear las ventanas y widgets adicionales, configurarlos y añadir los widgets a la ventana principal o a otras ventanas.
-   Definir los eventos que interesan y sus manejadores, es decir, dónde va el código del usuario y cómo reacciona el programa.
-   Arrancar el bucle de eventos.

### Configurar los widgets

Creemos el primer widget, un texto estático en la ventana que el usuario no puede cambiar:

```python
tk.Label(root, text="This label")
```

Desde el código, en cambio, el texto sí se puede cambiar: en lugar del parámetro `text`, se le asocia una variable de cadena, y al cambiar su valor cambia al instante el texto del `Label`:

```python
lb_text = tk.StringVar()
lb_text.set("1")
tk.Label(root, textvariable=lb_text, width=10, font=dFont, anchor=tk.NW)
```

Fuente: [legacy/pi.py, líneas 227–230](../legacy/pi.py#L227-L230)

El parámetro `font` cambia la fuente; preparé de antemano una fuente de interfaz más grande y legible:

```python
import tkFont
dFont = tkFont.Font(family="Arial", size=30)
```

Fuente: [legacy/pi.py, línea 211](../legacy/pi.py#L211)

El parámetro `anchor` fija la alineación del widget; aquí es NORTH-WEST, es decir, el texto se pega a la esquina superior izquierda del widget.

Las propiedades no tienen por qué fijarse al crear el objeto.

Fíjense en que el primer argumento es el «propietario», el «master»: el lugar donde vive el widget. Aquí se podría omitir, porque por defecto es `root`. Pero los widgets no tienen por qué estar directamente en la ventana principal (`root`); también se pueden colocar dentro de otros widgets.

### Manejadores de eventos propios

Las funciones manejadoras de eventos, que se llaman cuando ocurre un evento, deben recibir un parámetro. Normalmente se llama `event`.

El método `bind` conecta un manejador con un evento de Tk:

```python
def bt_find_click(event):
    pass

root.bind('<Return>', bt_find_click)
```

Fuente: [legacy/pi.py, línea 210](../legacy/pi.py#L210)

Recibe el nombre del evento y la función a la que hay que llamar. El evento, con todos sus parámetros, se pasa a la función como argumento `event`. Aquí el evento es pulsar la tecla Enter, que se escribe como la cadena `'<Return>'`.

### Colocar los widgets

Había huido desesperado de WinAPI en busca de un diseñador visual de interfaces. Resultó que Tkinter tampoco trae uno de serie **:(** Apretando los dientes, me puse a leer cómo viven los desarrolladores sin él y, para mi sorpresa, han resuelto el problema de forma bastante cómoda y elegante.

### Gestores de geometría

\[Fuente: [Habr](https://habr.com/post/133337/){: hreflang=ru }\]

**1 pack()** es una función que se llama empaquetador o gestor de geometría. Decide cómo se disponen los widgets en la ventana principal. Hay que llamar al empaquetador para cada widget; si no, el widget no se muestra. Hay tres empaquetadores en total:

pack coloca los widgets en la ventana padre automáticamente. Sus parámetros:

side: desde qué lado se añade el siguiente elemento,

fill: si se estira hasta los bordes de la ventana en alguna dirección,

expand: si el widget debe ocupar todo el padre.

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

**2 grid()** coloca los widgets en una cuadrícula. Parámetros principales:

row/column: la fila/columna de la cuadrícula,

rowspan/columnspan: cuántas filas/columnas ocupa el widget,

sticky: cómo se estira el widget cuando crece su celda, es decir, a qué bordes de la celda (N, W, S, E) se pega.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').grid(row = 1, column = 1)
Button(root, text = '2').grid(row = 1, column = 2)
Button(root, text = '__3__').grid(row = 2, column = 1, columnspan = 2)
root.mainloop()
```

<img width="137" height="94" alt="2-grid" src="https://github.com/user-attachments/assets/1da19342-4b45-406e-ae00-fb29dfd5bc18" />

**3 place()** coloca los widgets en unas coordenadas y con unos tamaños dados. Parámetros principales: x, y, width, height.

```python
from Tkinter import *
root = Tk()
Button(root, text = '1').place(x = 10, y = 10, width = 30)
Button(root, text = '2').place(x = 45, y = 20, height = 15)
Button(root, text = '__3__').place(x = 20, y = 40)
root.mainloop()
```

<img width="139" height="139" alt="3-place" src="https://github.com/user-attachments/assets/f6ecb75e-e579-4d53-a7a9-653519d72954" />

Mientras no se llame a un empaquetador para un widget, este, naturalmente, no se muestra.

### La tarea

Ahora, sobre el ejemplo cuya implementación les quiero contar.

Existe la hipótesis de que π es un [número normal](http://www.etudes.ru/ru/sketches/normal-number-pi){: hreflang=ru }, es decir, que en él se puede encontrar cualquier secuencia finita de cifras.

Para asombrar a niños y mayores en un [festival de ciencia](http://www.festivalnauki.ru){: hreflang=ru }, tomamos prestada esta [atracción](http://www.etudes.ru/ru/sketches/normal-number-pi/){: hreflang=ru }: _introduces tu fecha de nacimiento y el programa te dice en qué cifra de π se encuentra_.

Así que tuvimos que calcular π con bastantes cifras, recorrer todas las fechas desde el año 1 d. C. hasta el 9999 d. C. y encontrar su primera posición en las cifras de π.

### Calcular π

Encontramos [en internet](http://www.cyberforum.ru/qbasic/thread1923079.html#post10542354){: hreflang=ru } un programa ya hecho para calcular π. Calculó 3000 millones de cifras decimales. El resultado fue un archivo de texto de casi 3 GB.

Luego resultó que Python 2.7, en el que suelo escribir programas pequeños, [no se lleva bien](https://ozymaxx.github.io/blog/2018/05/29/python-strftime){: hreflang=en } con las fechas anteriores a 1900. Para enumerar las fechas usé la biblioteca [arrow](http://arrow.readthedocs.io){: hreflang=en }, que lo resolvió a la perfección:

```python
start_date = arrow.Arrow(0001, 1, 1), end_date = arrow.Arrow(9999, 12, 30)
with open('dates.txt', 'w') as dates:
        for single_date in arrow.Arrow.range('day', start_date, end_date):
            print >>dates, single_date.format(fmt='DDMMYYYY')
```

Esto generó un archivo con todas las fechas posibles con año positivo de cuatro cifras, teniendo en cuenta los años bisiestos y demás.

Después, las fechas tenían que convertirse en claves de un diccionario; luego había que recorrer todas las subcadenas de π y guardar como valores las posiciones (respecto a la coma decimal) de la primera aparición de cada fecha.

Resultó que Python 2.7 también limita el valor del iterador del operador [`range()`](https://stackoverflow.com/questions/39470012/python-overflow-error-iter-index-too-large){: hreflang=en }, así que el código quedó así:

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

_Estos scripts de preparación no están en `legacy/`; en la versión web los sustituye [tools/build_index.py](../tools/build_index.py)._

Listo, la etapa de preparación está terminada.

Solo queda una minucia: la interfaz gráfica.

### La interfaz gráfica

El plan de la interfaz:

<img width="807" height="579" alt="plan de la interfaz" src="img/plan-en.png" />

1.  Fijar el tamaño mínimo de la ventana.
2.  Entrada de fecha validada, para que no se pueda introducir una fecha no válida.
3.  Aprender a colocar el texto en un `Label` de modo que salte de línea por caracteres y muestre exactamente tanto texto como quepa en pantalla.
4.  Cargar sobre la marcha la parte necesaria de π desde el archivo y mostrarla.
5.  Resaltar la subcadena encontrada entre todos los caracteres.
6.  Disposición: una cabecera de tres objetos que no se estiran, y debajo el resto de objetos, que sí se estiran.
7.  Optimizar la aplicación.

Empecemos por lo sencillo.

### Tamaño mínimo de la ventana

```python
root.geometry("1280x640") # default window size at startup
root.minsize(680, 340)    # minimum window size, so widgets don't collapse into a dot
```

Fuente: [legacy/pi.py, líneas 206–207](../legacy/pi.py#L206-L207)

### Validación de la entrada

Para introducir la fecha elegí el widget `Entry` (el equivalente del Textbox de WinAPI). Decidí implementar yo mismo la entrada de «solo fechas d. C.» validando los caracteres sobre la marcha.

Una ilustración del [esquema general de validación](https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter){: hreflang=en } de la entrada de texto del usuario en cualquier widget de Tk:

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

De todo esto solo me hacía falta el parámetro `'%P'`: _toda la entrada nueva_. Si, después de escribir el siguiente carácter, el conjunto no es (el principio de) una fecha, nos quedamos con lo escrito antes de ese carácter; si lo es, el carácter se añade al `Entry`.

Para la fecha completa usamos la misma biblioteca arrow. El widget `DateEntry` resultante: [legacy/pi.py, líneas 34–89](../legacy/pi.py#L34-L89).

### Configurar el widget de π

Al principio pensaba usar texto estático para mostrar π. Va bien cuando hay que impedir que los usuarios seleccionen, copien o cambien el texto mostrado.

De serie, `Label` no sabe partir el texto en líneas carácter a carácter. Encontré una [forma](https://www.reddit.com/r/learnpython/comments/6dndqz/how_would_you_make_text_that_automatically_wraps){: hreflang=en } de partirlo por letras: la longitud de salto forzado se iguala a la anchura del widget:

```python
class WrappingLabel(tk.Label):
    ''' a type of Label that automatically adjusts the wrap to the size '''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
# ...
lbt = WrappingLabel(root, textvariable=lbt_text, font=dFont, anchor=tk.NW, justify=tk.LEFT)
```

justify: alinear el texto de varias líneas al borde izquierdo del `Label`.

Después había que recortar el texto mostrado a la cantidad que cabe en pantalla.

Para eso me puse a reinventar otra rueda, interceptando el evento de cambio de tamaño de la ventana principal:

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

Al final tuve que renunciar al widget `Label`, sobre todo porque de serie no sabe colorear la subcadena encontrada. Habría tenido que crear un `Label` dinámico encima del estático, calcular las coordenadas de la subcadena en la ventana y colocar ahí un `Label` nuevo con otro color…

Uf…

### El widget Text para π

`Text` es un widget más potente, con formato para regiones del texto y un control más fino.

Gracias al [hilo conductor de todos los programadores y único rayo de luz](http://stackoverflow.com){: hreflang=en } en la oscuridad y la decepción de todas las cosas, donde me señalaron un [post](https://stackoverflow.com/questions/40992931/python-easiest-way-to-define-multiple-global-variables){: hreflang=en } con un caso parecido al que había empezado en el apartado anterior, y a la [documentación](https://www.tutorialspoint.com/python/tk_text.htm){: hreflang=en } de Tkinter, mi sueño se hizo realidad:

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

Fuente: [legacy/pi.py, líneas 101–134](../legacy/pi.py#L101-L134); creación del widget: [línea 248](../legacy/pi.py#L248)

La idea siguió siendo la misma, interceptar el evento de cambio del texto, pero la implementación mejoró. Algunos puntos.

1.  Búsqueda binaria en lugar de un bucle while por todas las letras empezando por la última.

```python
if (actual_width  > max_width * max_height):
    # the original text won't fit. Keep shrinking until it does
    ilast = bisect.bisect_left(KeyList(text, key=lambda x,i:
                                       self.font.measure(text[:i]+ '...')),
                                       max_width * max_height)
```

Fuente: [legacy/pi.py, líneas 117–121](../legacy/pi.py#L117-L121)

Como `bisect` no tiene un parámetro key para el valor por el que comparar, tuve que escribir un envoltorio:

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

Fuente: [legacy/pi.py, líneas 91–99](../legacy/pi.py#L91-L99)

En lugar de una letra, le da a la búsqueda la anchura del texto desde el principio hasta esa letra.

2\. En lugar de la altura exacta de la fuente, elegí un coeficiente: por los saltos de línea, la anchura multiplicada por la altura sigue sin ser el tamaño exacto.

```python
self.font_height = 46.8   # instead of self.font.metrics('linespace')
```

Fuente: [legacy/pi.py, línea 107](../legacy/pi.py#L107)

El coeficiente lleva el final del texto lo más cerca posible del final del widget, pero, claro, a veces falla:

<img width="1071" height="105" alt="altura de la fuente" src="https://github.com/user-attachments/assets/c2254737-5e6c-4251-9eeb-fe905d76fc0d" />

3\. `Text` sabe partir las líneas por caracteres él solo.

```python
wrap=tk.CHAR
```

4\. `Text` sabe resaltar sus propias subcadenas. Resaltamos en rojo la subcadena encontrada:

```python
self.tag_add("highlight", "1."+str(index), "1."+str(index+8))
self.tag_config("highlight", background=frame["bg"], foreground="red")
```

Fuente: [legacy/pi.py, líneas 130–131](../legacy/pi.py#L130-L131)

5\. Prohibimos cualquier modificación del widget:

```python
lb3.config(state=tk.DISABLED)
```

Fuente: [legacy/pi.py, línea 255](../legacy/pi.py#L255)

Para que el `Text` no destaque, igual que un `Label`, su `background` se iguala al color de la ventana principal:

```python
bg=frame["bg"]
```

Añadimos algunos datos iniciales al `Text` al arrancar:

```python
LONG_ARRAY = read_pi(1,2500)
lb3.insert(tk.END, LONG_ARRAY)
```

Fuente: [legacy/pi.py, línea 204](../legacy/pi.py#L204) y [línea 254](../legacy/pi.py#L254)

En el manejador de eventos sustituimos los datos por los que hacen falta:

```python
self.delete(1.0, tk.END)   # first delete the old data, starting from char 0 of line 1,
self.insert(tk.END, text)  # then insert the new data at the end of the text
```

Fuente: [legacy/pi.py, líneas 125–126](../legacy/pi.py#L125-L126)

Como ven, los datos se añaden de otra forma que en un `Label`: se pueden añadir línea a línea, indicando en qué línea escribir. No me compliqué con eso y trabajo con una sola línea.

Por una vez, algo se hizo con las herramientas integradas, y eso ya es una _gran victoria_.

El código que busca en la base de datos de fechas, que se ejecuta al pulsar el botón «Find» o la tecla Enter:

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

Fuente: [legacy/pi.py, líneas 136–162](../legacy/pi.py#L136-L162)

Como ven, ahora, para modificar el `Text`, incluso desde el código, primero hay que devolverlo al estado normal, cambiar el contenido y luego volver a desactivar la modificación.

El desplazamiento aleatorio deja claro que, para una fecha nueva, la coincidencia resaltada es correcta y está en otro fragmento (quizá lejano) de π.

Una especie de optimización es que solo se carga el pequeño fragmento de π que hace falta. La lectura es rápida y no provoca retrasos en la interfaz. Tener todo el enorme archivo de π en memoria y leerlo al arrancar sería un gran derroche.

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

Fuente: [legacy/pi.py, líneas 164–173](../legacy/pi.py#L164-L173)

### Disposición

Al principio pensé en montar el programa con el primer empaquetador, el más sencillo: `pack()`. Según el plan, eso exigía agrupar los objetos para que el `Text` principal se estirara bien según el tamaño de la ventana.

Primero metí la cabecera de tres objetos (el rótulo, la entrada de fecha y el botón) en un grupo `Frame`, `win_header`.

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

Segundo, necesitaba grupos para la parte principal, `win_body`, y dentro de ella la columna izquierda `winbl` con tres números de carácter: el primero mostrado, el inicio de la fecha encontrada y el último mostrado.

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

_Esta versión con `pack()` no llegó al código final._

Pero más tarde aprendí a manejar el empaquetador grid() y lo hice todo con él.

### El empaquetador grid

Creé un grupo `frame` para todos los widgets de la ventana principal y tracé en él una cuadrícula virtual de 11 columnas y 7 filas.

Mi razonamiento: el rótulo, la entrada de fecha y el botón van en la primera fila; el rótulo ocupa 4 columnas, la entrada de fecha va justo detrás y ocupa 3, y el botón está a la derecha y ocupa 2. Les dejé estirarse (sticky) en todas las direcciones junto con sus celdas.

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

Fuente: [legacy/pi.py, líneas 213–224](../legacy/pi.py#L213-L224)

Los demás elementos se colocaron igual. Como ven, el `Text` (`lbt`) es el que más espacio ocupa:

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

Fuente: [legacy/pi.py, líneas 225–249](../legacy/pi.py#L225-L249)

Al final de todo fijé los pesos de las celdas: cuanto mayor es el peso, más cambia de tamaño la celda al escalar la ventana principal.

```python
for y in range(1,11): tk.Grid.columnconfigure(frame, y, weight=1)
for x in range(2,6): tk.Grid.rowconfigure(frame, x, weight=1)
```

Fuente: [legacy/pi.py, líneas 250–253](../legacy/pi.py#L250-L253)

### Optimizar el programa

Cuando todo estuvo escrito y depurado, unas pruebas ligeras mostraron que el programa arrancaba con una lentitud imperdonable. Todo por leer un archivo de texto.

La lectura del archivo de π sí logré evitarla. Pero leer toda la base de datos de fechas desde su archivo es inevitable. Es una tabla de dos columnas: la cadena de la fecha, un tabulador y la posición.

Así que había que averiguar cómo leerla rápido. Un experimento sencillo:

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

Los tiempos se midieron con timeit, la herramienta estándar de Python.

Los resultados:

```
readfile 6.3322045118 secs.
csv file 4.1212712648 secs.
pd  file 4.4932071859 secs.
pd csvrd 350.0057260714 secs.
loadtxt  41.6930684601 secs.
```

Gana csv. Sigue siendo lento. El `read_db` final: [legacy/pi.py, líneas 189–193](../legacy/pi.py#L189-L193).

Así que saqué la artillería pesada, el multihilo: leer el archivo de texto de fechas en segundo plano mientras se carga el formulario.

```python
# a thread that reads the text file
class Worker(threading.Thread):
    ''' thread to read the dates DB from the text file '''
    def run(self):
        global DB
        DB = read_db()
WORKER = Worker() # an instance of the thread that reads the DB from the file
```

Fuente: [legacy/pi.py, líneas 27–32](../legacy/pi.py#L27-L32)

Para este caso, bastante habitual en la programación de GUI (mantener el formulario receptivo durante cálculos pesados), Tk tiene funciones especiales. Nos hace falta `after()`, que llama a nuestra función, aquí `listen_for_result()`, al cabo de 10 milisegundos del bucle de eventos.

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

Fuente: [legacy/pi.py, líneas 195–200](../legacy/pi.py#L195-L200) y [líneas 208–209](../legacy/pi.py#L208-L209)

Intenta unirse al hilo si ya ha terminado y, si no, le pide a Tk que espere otros 10 milisegundos.

Así, el pesado archivo de texto se carga en paralelo con la ventana, que también es una operación pesada. _Victoria_.

Queda un inconveniente: si el usuario introduce una fecha antes de que se haya leído el archivo (muy improbable, pero aun así), esperamos a que termine el hilo y luego buscamos en la base de datos ya lista:

```python
def bt_find_click(event=None):
    # ...
    if WORKER.is_alive():
        WORKER.join()
    # ...
```

Fuente: [legacy/pi.py, líneas 140–141](../legacy/pi.py#L140-L141)

### Código fuente completo

El código completo está en [legacy/pi.py](../legacy/pi.py).

<img width="1080" height="557" alt="interfaz" src="img/interface-en.jpg" />

### Localización

En lugar de cadenas fijas en el código, las cadenas se leen de un archivo de configuración: [legacy/pi.py, líneas 175–187](../legacy/pi.py#L175-L187).

<img width="1080" height="565" alt="localización" src="https://github.com/user-attachments/assets/36be95e5-22fa-42e1-982e-cf63ec3ea86a" />

### Ejecutable

Solo queda generar un .exe, que se hace con un comando de consola (si tienen Anaconda instalado):

```
pyinstaller --onefile pi.py --noconsole
```

noconsole: Tk se lanza desde una consola, así que antes del formulario aparece una terminal; no la necesitamos, y esta opción la quita.

### Ocho años después

En 2026 el programa se mudó al navegador, y resultó que el sitio no necesitaba para nada el archivo de 3 GB con las cifras de π. Cómo pasó, lo cuento en la nueva nota: [π lo guarda todo, así que no tuve que guardar π](/es/writing/pi-stores-everything/).

### Referencias

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
