---
title: "Un intérprete con sintaxis configurable"
summary: "Proyecto de fin de grado: un intérprete multiplataforma cuyas palabras clave y gramática se pueden configurar."
source: favorart/IPL@master:docs/ru/README.md
source_lang: ru
source_hash: b2ca507e
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
# Intérprete para un lenguaje de programación interpretado con sintaxis configurable

[Kirill Anatólievich Golikov](https://github.com/favorart)

Director: [Pável Aleksándrovich Aliséichik](http://intsys.msu.ru/staff/aliseychik/){: hreflang=ru }

Universidad Estatal de Moscú (MSU)

Facultad de Mecánica y Matemáticas

Departamento de MaTIS (Teoría Matemática de Sistemas Inteligentes)

2013

CDU: 004.432.2

*Palabras clave:* IPL, lenguaje de programación interpretado, sintaxis configurable,
intérprete, lenguaje natural, analizador léxico, sinónimos, palabras reservadas.


## Resumen

Proyecto de un lenguaje de programación interpretado que facilita la comprensión de un algoritmo matemático formal
y hace más eficiente el desarrollo de algoritmos nuevos
gracias a una sintaxis simplificada y a unas formas léxicas más cercanas a las que le resultan naturales al usuario.
Actualidad del tema: la gran complejidad del código fuente del software en la práctica.


## Introducción

En el artículo se examina el prototipo de un lenguaje de programación que simplifica la comunicación entre el cliente y el programador.
Aunque las formas de esa comunicación están bien rodadas desde hace tiempo (hay esquemas, diagramas UML, etc.), no son ideales: hay margen de mejora.
El objetivo de este trabajo es facilitar la lectura de código fuente complejo acercando el lenguaje de programación al lenguaje natural.
La idea del trabajo es ofrecer una interfaz de interacción entre la persona y el ordenador sin símbolos especiales como “}_$<<;”,
es decir, conseguir que el ordenador hable el idioma de la persona, y no al revés.
Creo que hay que aspirar a que cualquiera pueda resolver una tarea de programación cotidiana
simplemente dando órdenes en su lengua materna, sin necesidad de conocimientos técnicos.

La idea supone un lenguaje de programación cuyo código le resulte al lector comprensible y natural,
sin necesidad de documentación ni comentarios adicionales
(en la práctica resultó que escribir el código sigue siendo cosa de un profesional que entienda cómo funciona la sintaxis).
El lenguaje recibió el nombre de *lenguaje de programación interpretado*, o IPL.

El lenguaje persigue los siguientes objetivos:

*	*El objetivo es el algoritmo*: no hace falta precisar detalles exhaustivos que dificultan entender el algoritmo. Alto nivel de abstracción.
*	*El código se presenta como un texto matemático formal*, con palabras de secuencia y de recapitulación que le dan ese aspecto, y con la posibilidad de usar apartados y subapartados numerados anidados.
*	*Código comprensible a primera vista*. El intérprete permite cambiar las palabras y operaciones registradas según los hábitos y preferencias de quien escribe y de quien lee.
*	*El código se puede localizar, y la sintaxis se adapta a la localización*. Se puede cambiar el aspecto del código hasta el punto de escribir programas en la lengua materna (las construcciones poco claras pueden entenderse mejor en contexto). El lenguaje fomenta nombres correctos y descriptivos, ya que admite expresiones fijas del lenguaje natural.
*	*El código es una especie de interfaz*. Por analogía, el propio cliente podría retocar el código.
*	*El código hace lo que debe hacer y no hace nada que no deba*. El cliente puede comprobar por sí mismo si el diseño del programa cumple o no sus requisitos.

Características del lenguaje IPL:

*	analizador léxico que admite nombres compuestos por varias palabras;
*	alfabeto y conjunto de palabras reservadas modificables;
*	sintaxis configurable según las preferencias del usuario;
*	semántica sencilla y clara;
*	tipos inteligentes de almacenamiento de datos;
*	herramientas integradas de optimización de la ejecución.

IPL nos acerca a la solución de los siguientes problemas:

*	que un programador nuevo pueda estudiar el código fuente de forma cómoda y rápida;
*	facilitar el mantenimiento de los productos de software;
*	la confianza del usuario en el programa;
*	mejorar el entendimiento mutuo entre el programador y el cliente.

El artículo consta de una introducción, en la que se analizan las ideas principales y se formula el objetivo del trabajo;
tres partes: demostración de la sintaxis configurable del lenguaje, funcionamiento e implementación del intérprete IPL;
y una conclusión, en la que se hace balance del trabajo en el proyecto.

**Listado 1.1.**

![1](https://github.com/favorart/IPL/assets/9784285/09371315-ff99-499d-b85c-f48d39dc301b)

_____________________

## 1. Sintaxis configurable

La idea de crear un lenguaje de programación interpretado era dar a los usuarios la posibilidad de definir la sintaxis
según sus preferencias y costumbres (listado 1.1).
Los bloques de declaración de variables pueden estar en cualquier parte del programa. En el listado 1.2 se muestran variantes de sintaxis:

**Listado 1.2.**

![2](https://github.com/favorart/IPL/assets/9784285/805a65af-e821-4e13-b60d-33deb87c962a)

*Expresiones aritméticas*. Al escribir código con una configuración sin separadores explícitos,
las expresiones se separan lógicamente de acuerdo con la intuición.
Una expresión algebraica se considera terminada si aparecen seguidos elementos que no son operadores del lenguaje:

$$ a=1+2 \hspace{10pt} [;] \hspace{10pt} b=2+4 $$

En `interpreter.Syntax` hay opciones (listado 1.3) que definen las variantes de escritura de las construcciones del lenguaje.

**Listado 1.3.**

![3](https://github.com/favorart/IPL/assets/9784285/70704cd9-32fc-41fc-bca1-c6f9d7ea21c9)


## 2. Funcionamiento

La interpretación consta de tres fases:

*Análisis léxico*: se extraen del texto los átomos y se compone una lista de palabras atómicas,
omitiendo los símbolos no registrados y los comentarios.

*Análisis sintáctico*: se extraen las expresiones de la lista de átomos y
se convierten las expresiones aritméticas a notación polaca teniendo en cuenta la precedencia de las operaciones,
la compatibilidad de tipos y la disponibilidad de las funciones.

*Ejecución* por descenso recursivo sobre la lista;
los valores de retorno de las funciones se usan como parámetros de las funciones de niveles superiores de la recursión.

*Lectura y escritura del bytecode precompilado*.
Al lanzar un script, el intérprete comprueba si en la carpeta actual hay archivos precompilados.
Si los hay, se salta las fases de análisis léxico y sintáctico del código,
así como la configuración de la sintaxis, y pasa directamente a la ejecución.
Así se gana velocidad.


### 2.1. Precompilación a bytecode

El programador escribe un script IPL en un archivo de texto de acuerdo con su configuración del intérprete
y obtiene un archivo `.ipl` (interpreted pre-compiled).
Al ejecutar el archivo, en la memoria del intérprete se crea una versión precompilada del código fuente del programa
que solo entiende el intérprete.
La precompilación crea tres archivos de datos y un archivo de bytecode:

		<script name>.ipc.constants.dat
		<script name>.ipc.variables.dat
		<script name>.<conf>.ipc.reg_words.dat
		<script name>.ipc

Al crear el bytecode se descartan todos los bloques de declaración de variables
y se crea una tabla hash aparte, específica para guardar los valores iniciales de las variables;
esta se escribe en `variables.dat`.

Al empezar la lectura se comparan los hashes `{1}` del archivo de bytecode y del código fuente del programa que se ejecuta.
A continuación, el archivo consta de ternas de números de cuatro bytes que definen el código.
La primera terna es la lista de nivel superior, que contiene todas las expresiones y bloques de código.
Después vienen sus elementos, y así se va anidando recursivamente el programa (tabla 2.1).

**Tabla 2.1.**

| cabecera del archivo [32 bytes]                     |
|:---------------------------------------------:|
| suma hash sha256 del archivo con el script ejecutable |

| tipo de átomo                 | desplazamiento en la tabla | desplazamiento en la cadena |          |
|:-----------------------------:|:-------------------:|:---------------------:|:------------------|
|en qué tabla hash se buscará   |desde el inicio de la tabla hash|en el elemento de la tabla hash|
| [ sizeof (int) ]              | [ sizeof (int) ]    | [ sizeof (int) ]      |
| PreComp                       | 0                   | número de elementos   |expresión del lenguaje (lista)
| Constant                      | 476                 | 0                     |valor de la constante
| Variable                      | 165                 | 0                     |variable del lenguaje
| RegWord                       | 634                 | 2                     |palabra reservada del lenguaje
| ...                           | ...                 | ...                   |


### 2.2. Fase de análisis léxico

Como se ha dicho, para que el algoritmo en IPL se lea mejor se usan sinónimos de las palabras reservadas e identificadores
formados por varias *palabras componentes* (así llamaremos a las palabras del lenguaje natural, para evitar confusiones),
y no se admiten prefijos ni símbolos poco naturales. Por eso el mecanismo de análisis léxico del intérprete
se escribió teniendo en cuenta que debe deducir las cosas por el orden de las palabras en la expresión y por el contexto.
El análisis del texto se hace en dos etapas: primero, los bytes del archivo en disco
(`TODO: unicode aún no está implementado; las cadenas se manejan en ASCII`)
se agrupan en componentes simples de palabras, que se llevan a una *forma normalizada*.
Su lista se pasa a la etapa superior, donde con ellos, si bastan, se construyen los *átomos* del lenguaje;
si no, se vuelve a llamar al analizador de primer nivel.
El resultado del análisis léxico es una lista secuencial de átomos (fig. 2.1):

**Fig. 2.1.** `ipl_list_pmv list_of_atoms`

![2 1](https://github.com/favorart/IPL/assets/9784285/5bf1d652-95df-426b-90d2-7b09e57d59d4)

El analizador se configura mediante *archivos de configuración*.
Todos los símbolos se definen en el archivo de configuración del alfabeto
(`<conf>_charset.txt`, donde `<conf>` lo define el usuario, por ejemplo, `eng` o `rus`).
En él, los símbolos se dividen en 5 clases disjuntas: letras, signos, dígitos, el símbolo de comillas y el símbolo del punto decimal.
Los símbolos los define el usuario y pueden ser arbitrarios: el intérprete no depende de letras ni signos concretos.

El otro archivo de configuración es el de palabras reservadas (`<conf>.txt`).
Su formato es el siguiente: un identificador único del significado de la palabra (tomado de `reg.word.id.txt`),
seguido, separados por comas, de los sinónimos que designan esa palabra reservada y, al final, un comentario explicativo opcional.
El analizador conoce las palabras reservadas durante la ejecución.
 El analizador sintáctico sincroniza los sinónimos.


### 2.3. Fase de análisis sintáctico

Las tareas del analizador sintáctico son:

1. procesar correctamente las variantes del código fuente y llevarlas a un bytecode único;
2. reordenar las instrucciones según la precedencia.

Así, el ejecutor solo se ocupa de ejecutar las instrucciones en orden.

La tarea (1) es trivial: consiste en pedirle sucesivamente al analizador léxico la siguiente porción de átomos;
una vez recibida, se comprueba el significado de las palabras y, si alguna no es admisible, se emite el error correspondiente.

La tarea (2) consiste en extraer las expresiones de la lista de átomos y convertir las operaciones aritméticas
a *notación polaca directa mediante una pila* `{3}`.
Aquí el analizador sintáctico pasa la expresión de notación infija a prefija, es decir, $(1+2)$ a $(+,1,2)$.

Además, si durante su trabajo el analizador sintáctico encuentra líneas demasiado largas o anidamientos demasiado profundos,
emite advertencias de que las construcciones escritas por el programador quizá sean demasiado enrevesadas
y al usuario le costará entender esa parte del algoritmo.
En la figura 2.2 se muestra un ejemplo de fase de análisis sintáctico completada con éxito en el intérprete IPL para una bifurcación.

**Fig. 2.2.** El operador de bifurcación en IPL.

![2 2](https://github.com/favorart/IPL/assets/9784285/430e7237-9c07-415f-a2d7-78b3b91fec57)

En resumen, la *sintaxis* de IPL tiene las siguientes características:

*	las variables se declaran en un bloque aparte;
*	hay varias alternativas de sintaxis para los métodos de objetos y para los bucles;
*	se pueden indicar apartados en los bloques de código, que aclaran la estructura del bloque y guían la vista de forma más estricta;
*	la directiva `resulted` permite que cualquier bloque de código devuelva un resultado.

En IPL no existen los dos tipos de *paréntesis* a los que está acostumbrado el programador: los *funcionales* y los *estructurales*.
Es así para implementar el paradigma en el que cualquier bloque de código puede devolver un valor, equiparándose a una expresión.
Un bloque de código puede usarse incluso dentro de los parámetros de una función, si devuelve un valor y no dificulta la comprensión del programa.


### 2.4. Fase de ejecución

El intérprete ejecuta por *descenso recursivo* `{2}` el bytecode
mostrado en la figura 2.2, que consiste en listas anidadas de átomos.
Al ejecutar las instrucciones, el programa *se colapsa*:
la expresión procesada se extrae de la lista y en su lugar se escribe el resultado ($1+2 \to 3$).
En la estructura del ejecutor los elementos extraídos no se eliminan,
sino que se trasladan de la expresión que se ejecuta a una expresión de respaldo.
Así, el bytecode precompilado, cuya corrección ha quedado comprobada al ejecutarse,
sigue disponible para escribirse en un archivo o usarse en bucles y funciones.
El programa termina cuando en la lista de instrucciones por ejecutar no quedan elementos [1].


## 3. Implementación

Los ladrillos de los que se compone el intérprete son las estructuras `myvar` (listado 3.1); según los valores que contengan,
un elemento atómico del lenguaje puede ser un signo, una palabra reservada, una constante, una variable o incluso una expresión entera.
Lo que es cada átomo lo indican los campos enumeradores.

**Listado 3.1.**

![3 1](https://github.com/favorart/IPL/assets/9784285/46fa5a6f-91e1-4ca1-b326-d95c5cc8e87b)

Los datos del intérprete se guardan en una estructura llamada *tabla de nombres* (`names_table`).
El intérprete arranca con su inicialización y termina con su limpieza.
La tabla guarda los datos necesarios en las distintas etapas de ejecución del script,
por ejemplo, en las de formación de lexemas y de sintaxis, así como datos importantes
que siempre hacen falta: los diccionarios de variables, constantes, palabras reservadas y expresiones.

Así, toda la memoria dinámica queda anotada de un modo u otro en este registro,
lo que garantiza que toda la memoria reservada se libere a tiempo y por completo.
Así se resuelve el problema de la recolección de basura.


## 4. Tipado

En IPL se decidió no usar *tipado implícito*,
ya que es difícil distinguir la declaración implícita de una variable de una referencia a ella y seguir el ámbito de la variable en el texto del programa.
Pero tampoco se quiso renunciar al *tipado dinámico* [5], para no atar al programador con un tipado estático rígido
y ofrecer las comodidades de un lenguaje interpretado, sin perder la posibilidad de detectar errores relacionados con los tipos de datos.
Se eligió un *tipado mixto*: al crear una variable hay que indicar su tipo explícitamente, pero ese tipo se puede cambiar cuando haga falta.

Los tipos integrados del lenguaje se presentan en la tabla 3.1.

**Tabla 3.1.**

| tipo de datos            | rango de valores
|:-------------------------|:-----------------------------------:|
| número entero            | de -2 147 483 647 a 2 147 483 647
| número de coma flotante  | de 1E-37 a 1E+37
| cadena                   | secuencia de caracteres ASCII
| función                  |
| contenedor               | lista o array
| diccionario              | análogo dinámico de una estructura

IPL admite programación modular con funciones en archivos separados.
Todas las funciones son globales y todas las variables, locales.
Las variables se pasan a las funciones por valor.
La implementación de una función dentro de la estructura `myvar` es todo un pequeño intérprete:
tiene su propio archivo de script, su propio analizador léxico y su propio código precompilado.
La declaración de una función es necesaria si su definición está en otro archivo.
Si la declaración no indica el nombre del archivo, este se buscará
por un nombre idéntico al de la función + la extensión `.ipl` en la carpeta por defecto.

Es imposible imaginar un lenguaje de programación moderno sin *tipos de datos enumerables*:
diccionarios y contenedores.
Estos tipos están integrados en el núcleo y se usan con los métodos habituales.
La particularidad del contenedor de IPL, que puede guardar elementos de cualquier tipo uno tras otro,
es que, según la frecuencia con que el usuario realiza ciertas operaciones,
el propio contenedor decide cómo almacenar los elementos
(también se puede indicar de entrada el tipo de almacenamiento del contenedor): como lista doblemente enlazada o como array contiguo.

Como es sabido, el array es eficiente para la lectura con acceso aleatorio, pero ineficiente para la escritura aleatoria.
Con la lista pasa lo contrario: insertar es una operación barata, pero para indexar un elemento del medio hay que recorrer la mitad de los elementos.
Si se realizan sistemáticamente operaciones poco adecuadas para un tipo de almacenamiento concreto,
tiene sentido pasar a otro, pese al coste de la reestructuración.
El contenedor lleva la cuenta del número total y de la longitud de las series de inserciones consecutivas y de accesos por dirección.
Con cada acción se incrementan o decrementan los contadores dentro de esa instancia concreta del contenedor.
Los valores umbral se eligieron de forma experimental.

El tipo de datos diccionario (`joint`) es un conjunto de pares `key:value`,
donde `key` y `value` son ciertos tipos de datos.
El valor `value` se puede obtener del diccionario en tiempo constante a partir de `key`, si está ahí.
En caso contrario, se devuelve un ‘rechazo’.
Los diccionarios basados en tablas hash {4} se usan como análogo de los tipos definidos por el usuario (`struct` en C).
Es un camino habitual en los lenguajes interpretados,
ya que permite definir la estructura de la agrupación dinámicamente durante la ejecución del programa.


## Conclusión

En este artículo se presentan los resultados del trabajo de investigación para crear el intérprete del lenguaje IPL.
Con el ejemplo del listado 4.1 se muestran la legibilidad del código y muchas de las posibilidades del lenguaje.
Como habrán podido comprobar con el código en IPL presentado,
el lenguaje nos acerca un paso más al uso del lenguaje natural en la programación.

**Listado 4.1.** El problema de la mochila

![4 1](https://github.com/favorart/IPL/assets/9784285/ee554a40-3c85-4684-b2ec-129a0da78021)

_____________________

**Listado 4.2.** Programa con complejidad $O(n^2)$

![4 2](https://github.com/favorart/IPL/assets/9784285/80204cf2-5f07-492f-9add-cc38e3709e2b)

_____________________

**Listado 4.3.** Programa en uzbeko

![4 3](https://github.com/favorart/IPL/assets/9784285/8e0f53e5-8e0a-47e4-9c01-8c3bd6e48849)

_____________________

## Bibliografía

* [1]	Шилдт Г. Язык С для профессиональных программистов. / Born to Code in C. – Osborne, 1989
* [2]	Керниган Б., Ритчи Д. Язык программирования С. / The C Programming Language. – Prentice Hall, 1988
* [3]	[Ejemplo de cómo escribir un intérprete sencillo](http://rsdn.ru/forum/alg/5018812.all){: hreflang=ru }
* [4]	[Tu propio intérprete](http://coderszone.info/339-sam-sebe-interpretator.html){: hreflang=ru }
* [5]	[Tipado dinámico (Wikipedia)](https://es.wikipedia.org/wiki/Tipado_dinámico)


### Algoritmos utilizados

*	{1}	[Cálculo de la suma hash SHA256 de un archivo (Ch. Devine, 2003)](http://patux.net/crypto_programs/hash/sha-2/sha256.c.html){: hreflang=en }
*	{2}	[Descenso recursivo](http://en.wikipedia.org/wiki/Recursive_descent_parser){: hreflang=en }
*	{3}	[Construcción de la notación polaca directa mediante una pila](http://algolist.manual.ru/maths/misc/revpn.php){: hreflang=ru }
*	{4}	Construcción de tablas hash
*	Dirección hash igual al resto de la división por un número primo (A. Dumey, 1956)
*	Encadenamiento (H. P. Luhn, 1953)
*	Direccionamiento abierto (sondeo) (A. P. Yershov, 1953), (en la literatura extranjera, G. Amdahl, 1957)
*	{5}	Ordenaciones
*	Quicksort (C. A. R. Hoare, 1960), implementación de <stdlib.h>
*	Ordenación por mezcla para listas (J. von Neumann, 1945)
