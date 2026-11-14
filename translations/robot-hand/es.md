---
title: "Movimiento punto a punto de un brazo robótico con control discreto"
summary: "Algoritmos de aprendizaje para posicionar un brazo robótico con control discreto: ensayo y error en lugar de un modelo conocido."
source: favorart/robot-hand@master:README.md
source_lang: en
source_hash: ad3388a2
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
# Sistema de movimiento punto a punto para un robot con control discreto

Kirill Golikov

Universidad Estatal de Moscú (MSU)

2016

Palabras clave: robótica, brazo robótico, manipulador, posicionamiento, movimiento punto a punto, descenso de gradiente, aprendizaje automático


## RESUMEN

En este trabajo se presenta un algoritmo de posicionamiento de un brazo robótico con control discreto.
El objetivo del trabajo es una prueba de concepto del posicionamiento de un manipulador
mediante una memoria «infinita», sin ningún conocimiento previo de los principios matemáticos del movimiento del brazo.
El resultado del trabajo es un algoritmo de movimiento punto a punto con varias etapas de aprendizaje,
una base de datos de movimientos y un modelo 2D configurable del manipulador con visualización.


## INTRODUCCIÓN

Este estudio comprueba que es posible posicionar un robot manipulador con alta precisión dentro de una zona acotada de su espacio de trabajo
sin ningún modelo analítico de la dinámica del manipulador. Como la robótica es hoy
una rama de la ciencia y la técnica popular y en pleno auge, cada mes aparece
una gran cantidad de dispositivos nuevos. Los fabricantes quieren experimentar con ellos y ponerlos
en funcionamiento lo antes posible. La actualidad de este trabajo radica en que, en lugar
de cálculos analíticos manuales, propone que el robot aprenda automáticamente por sí mismo a
controlar sus «extremidades» a base de usarlas, apoyándose en una base de datos de sus movimientos.


## PREMISAS BIOLÓGICAS

Los movimientos eficaces de las extremidades de una persona son el resultado de complejos cálculos paralelos que se producen en el cerebro,
en la médula espinal y a lo largo de todo el recorrido de los nervios hasta la extremidad que se mueve.
Además, cada movimiento aprovecha toda la gran experiencia acumulada de movimientos anteriores de la persona.
Los fisiólogos confirman con sus investigaciones que nuestra mente, en realidad, no calcula desde cero el plan y la ejecución del siguiente movimiento.
Más bien reúne en la memoria los datos de movimientos que encajan con el caso actual y, usándolos como bloques, construye el siguiente movimiento de forma mecánica, sin pensar [9].
Aun así, el cerebro humano recibe en tiempo real la retroalimentación de los nervios y los receptores sensoriales y corrige el control que ejecutan los músculos.

A nadie le sorprende que los niños pequeños no acierten con el juguete que cuelga sobre la cuna, y que a veces incluso empiecen el movimiento en la dirección equivocada.
En robótica ocurre lo mismo: el algoritmo de aprendizaje, como el cerebro de un bebé, no sabe nada de sí mismo y explora la estructura y el estado de su propio organismo moviendo sus extremidades.
Los fisiólogos señalan que solo tras una larga etapa de aprendizaje el bebé es capaz de coordinar lo que espera ver con los movimientos reales.


## ¿DÓNDE ESTÁ LA DIFICULTAD?

La dinámica de robots establece las leyes del movimiento, que se expresan mediante sistemas de ecuaciones diferenciales
y relacionan las fuerzas motrices de los accionamientos con las fuerzas de inercia, la gravedad,
el rozamiento y las demás fuerzas aplicadas a los segmentos del manipulador.
Aunque las fórmulas de la mecánica y los métodos de resolución de sistemas de ecuaciones diferenciales están bien estudiados,
la dificultad para construir un modelo adecuado está en hallar los valores de los numerosos parámetros de las ecuaciones.
Hay que hacer cálculos y experimentos con cada robot por separado.
Es un camino laborioso y caro, y requiere un especialista cualificado.

Cuando la dinámica del robot es desconocida, cada movimiento degenera en una multitud de fallos y giros de corrección.
Esto no solo ralentiza la fase de ejecución, sino que también puede provocar colisiones y daños en el propio robot y en los objetos que manipula.
Una buena implementación de la búsqueda de trayectorias y del posicionamiento del manipulador le da cierta «elegancia» al movimiento:
suavidad y rapidez al alcanzar la posición requerida, y ausencia de fallos.
Las extremidades deben moverse con naturalidad, no solo en el sentido de parecerse a los movimientos de un brazo humano,
sino también en el de la eficacia y la coordinación de las operaciones que realizan.
Hay que crear un algoritmo que, antes de moverse, permita al robot imaginar adónde debe desplazar su extremidad
y cómo actuar desde el principio para que la desviación al final del movimiento de posicionamiento quede dentro de la precisión establecida.

Probando el manipulador, se puede entender el principio general de su funcionamiento.
Con un conjunto de trayectorias que cubra todo el espacio de trabajo del robot,
se pueden sacar conclusiones sobre trayectorias nuevas. La solución es ir precisando iterativamente el modelo del manipulador con cada una de sus operaciones.
Cuando se acumule una muestra de movimientos de entrenamiento suficiente en volumen y calidad, aparecerá el método para controlar el brazo.


## PLANTEAMIENTO DEL PROBLEMA

Supongamos que el robot manipulador actúa en un espacio de trabajo sin obstáculos y tiene dos articulaciones de rotación: hombro y codo.
Un accionamiento neumático desplaza la pinza del robot sobre una placa.
Cada articulación la mueve su propio cilindro neumático, que la abre o la cierra según el esquema de válvulas,
como si hubiera dos pares de músculos antagonistas.

El **problema** es: *con un modelo físico desconocido de la dinámica del manipulador, encontrar en un tiempo óptimo los conjuntos de acciones de control*
*que lleven el centro de la pinza a todos los puntos definidos dentro de una subregión del espacio de trabajo del robot con una precisión prefijada (= 1,5 mm)*.
El **objetivo** (*target*) es esa subregión del espacio de trabajo del robot que contiene todos los puntos definidos.

En este trabajo se construye un modelo discreto del robot. «La particularidad de los modelos discretos es el tiempo discreto en el que se produce su funcionamiento» [7].
Existen acciones de control de duración mínima tales que el manipulador no «notaría» señales más cortas aunque las recibiera.
Además, el robot opera en un espacio continuo, pero solo puede realizar un número finito de movimientos.
Fijemos la precisión mínima requerida y dividamos el espacio en regiones en función directa de esa precisión.
Consideremos que el punto característico de la pinza del manipulador está siempre exactamente en el centro de una de esas regiones.
Mientras el brazo se mueve, la pinza pasa del centro de una región al de otra.

En este trabajo, la tarea modelo de posicionamiento del manipulador es el juego del go.

El objetivo del robot es el tablero de juego, un cuadrado de 30 cm de lado (fig. 1).
Las posiciones de las piedras forman una retícula regular de 18x18 dentro del objetivo, 324 puntos en total.
La pinza debe acertar en esos puntos concretos.
El objetivo está situado por completo en una zona del espacio de trabajo en la que el manipulador alcanza cada uno de sus vértices.

![1](https://github.com/favorart/robot-hand/assets/9784285/ebe578bc-36b1-4662-adf0-91ab48409501)

Todos los movimientos parten de **un único punto de origen**.

**El control general del modelo del robot** es $𝑣⃗(𝑡) = (𝑣_1(𝑡), 𝑣_2(𝑡), 𝑣_3(𝑡), 𝑣_4(𝑡))$,
un vector de coordenadas binarias en el que cada coordenada es la señal al músculo correspondiente en cada instante del tiempo discreto $t$.

El **músculo** del brazo **actúa** todo el tiempo mientras recibe un «uno» y está en un estado admisible.
El estado del músculo es *admisible* cuando:

* no se ha alcanzado el ángulo máximo (mínimo) de apertura (cierre);
* el músculo antagonista de su par no está activo;
* no ha llegado la señal de parada inmediata.

Si la señal cambia de «uno» a «cero», el músculo deja de actuar,
pero el brazo robótico sigue moviéndose por inercia. Cuando alcanza el estado de reposo,
el robot lo señala, y entonces se puede conocer el punto final del movimiento.

El manipulador tiene **retroalimentación**: el brazo observa su propia posición, y esa información es correcta en todo momento.

Un manipulador virtual modela los movimientos y comprueba la corrección del algoritmo:
desplaza la pinza por el plano según la combinación de las leyes de movimiento de todos los músculos activos.

La **ley de movimiento** (*framing*) de un par de músculos es el valor en que se desplaza el ángulo actual de la articulación en cada fotograma del tiempo discreto.
La ley de movimiento reproduce los cambios no lineales de velocidad durante la actuación del músculo y simula la inercia.

![2](https://github.com/favorart/robot-hand/assets/9784285/20a7ddbc-2cd0-41d6-ad75-fde4e98f2ce1)

En la figura 2 se muestran las leyes de movimiento de músculos con distintos diseños de accionamiento y regímenes de trabajo del motor.
En la figura 2, las curvas crecientes muestran la variación del ángulo durante el funcionamiento del motor (mientras recibe un «uno»);
las curvas decrecientes representan la inercia.

**La trayectoria del movimiento** de un brazo robótico es el conjunto ordenado de puntos por los que ha pasado la pinza en cada fotograma del tiempo discreto
mientras se ejecuta el movimiento de principio a fin.
La trayectoria se caracteriza por su *punto final*. Las trayectorias con el mismo punto final son equivalentes.

**El descenso de gradiente** utiliza varias trayectorias cuyos puntos finales son los más cercanos al punto buscado.
Las acciones de control de esas trayectorias difieren entre sí.
La duración del control del siguiente movimiento puede variarse ligeramente dentro de los límites de las diferencias de control de dichas trayectorias.
Así, el movimiento se desplazará en línea recta hacia el punto buscado, y su parada quedará más cerca de él.
Gracias al teorema de Taylor, el algoritmo de posicionamiento puede alcanzar el punto buscado desde un punto lo bastante cercano, desplazando sucesivamente la trayectoria con el punto final más próximo
en línea recta hasta que termine en el punto buscado.

**Teorema de Taylor**: si la función real $f(x)$ tiene derivada en el punto $a$, entonces admite una aproximación lineal en el punto $a$:

$$ 𝑓(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) + h_1(𝑥 − 𝑎) \tag{1}$$

donde $h_1(𝑥)$ es el error de aproximación y $\lim_{𝑥 \to a}{h_1(𝑥)}=0$.

$$ 𝑃_1(𝑥) = 𝑓(𝑎) + 𝑓'(𝑎)(𝑥 − 𝑎) \tag{2}$$

donde $𝑃_1(𝑥)$ es la aproximación lineal de la función $𝑓(𝑥)$ en el punto $a$.
La gráfica $y=P_1(𝑥)$ es la recta tangente a la gráfica de la función $𝑓(𝑥)$ en el punto $𝑥=a$ [10].


## ALGORITMO DE POSICIONAMIENTO

El algoritmo consta de tres etapas de aprendizaje, tras las cuales el posicionamiento pasa a ser preciso.

En **la primera etapa de aprendizaje**, todo el espacio de trabajo del brazo se cubre con movimientos
desde el punto de origen con un paso de cobertura suficientemente grande.

Los puntos finales no quedarán a la misma distancia unos de otros,
porque el robot no conoce las funciones de aceleración exactas de sus músculos.
El algoritmo intenta mantener intervalos más o menos iguales entre los puntos finales de los movimientos,
basándose en que la función de aceleración no es monótona decreciente.
La cobertura se realiza variando de forma independiente la duración del trabajo de cada músculo del robot.

Todas las trayectorias realizadas se guardan en la base de datos.
A partir de esos datos se obtiene una primera aproximación de la dependencia entre la posición de la pinza y los valores de control.
Además, se determinan los límites de configuración del brazo,
es decir, los umbrales de control que no sacan el centro de la pinza del objetivo.

**La segunda etapa de aprendizaje** consiste en cubrir el objetivo con trayectorias
con un paso de cobertura menor, de forma más densa que en la primera etapa.

**La tercera etapa de aprendizaje** consiste en seleccionar en la base de datos las trayectorias cuyos puntos finales están en un entorno del punto buscado.
La composición de los controles de esos puntos da el control para una serie de movimientos sucesivos, cada uno de los cuales se detiene más cerca del punto buscado.

Un robot bien entrenado puede posicionar el brazo en una ubicación dada con la precisión prescrita sin ningún fallo.


## LA TERCERA ETAPA DE APRENDIZAJE

1. Si no hay trayectorias de apoyo en un entorno del punto buscado, se termina con un error.
2. Mientras haya convergencia hacia el punto buscado, funciona el algoritmo promediado de descenso de gradiente.
3. Si la convergencia del gradiente se interrumpe, es decir, se ha caído en uno de los mínimos locales de la función 2D
distinto del punto buscado, se aplica uno de los «algoritmos-perturbación» para «salir del hoyo»
y continuar el proceso de convergencia del gradiente.
4. Si el «algoritmo-perturbación» funciona, es decir, se ha encontrado un punto más cercano al objetivo que el mínimo local,
se vuelve al algoritmo promediado de descenso de gradiente (paso 2); si no, se aplica otro «algoritmo-perturbación» (paso 3).
5. Si ningún «algoritmo-perturbación» funciona, es decir, se sigue en el mínimo local, se pasa al algoritmo básico de descenso de gradiente.
6. Mientras haya convergencia hacia el punto buscado, funciona el algoritmo básico de descenso de gradiente.
7. Si la convergencia del gradiente se interrumpe, se aplica la búsqueda exhaustiva en todas las direcciones hasta alcanzar el objetivo.
8. Si la búsqueda exhaustiva no tiene éxito, el punto más cercano está demasiado lejos del buscado.
En ese caso no se cumplen las condiciones del teorema de Taylor. Se sale del algoritmo.
9. En lugar del punto buscado, se elige un punto aleatorio en un entorno cuadrado (comparable a la precisión) del punto buscado.
Se ejecuta el algoritmo descrito para el nuevo punto. Si este punto está más cerca de los puntos existentes,
el algoritmo convergerá hacia él. Por la forma en que se ha elegido, el nuevo punto también está cerca del objetivo.
Ahora se repite el algoritmo desde este nuevo punto hasta el punto buscado.
O bien convergerá con éxito, o bien habrá que probar con otro punto.

La práctica ha demostrado que, para acertar en cada punto buscado fijado, basta con elegir un nuevo punto unas pocas veces (< 15),
y en cada tercer intento se vuelve a probar el propio punto buscado.


## RESULTADOS

La **complejidad** del algoritmo es el número total de movimientos del robot necesarios para acertar en cada punto buscado.

**Método de estimación del tiempo**: el hombro recorre toda su trayectoria en 700 ciclos de tiempo discreto, y el codo, en 550.
Supongamos que un ciclo dura un milisegundo (1 ms). No todos los movimientos requieren abrir o cerrar del todo una articulación.
Un movimiento del brazo dura aproximadamente medio segundo, y otro tanto hace falta para devolver el brazo al punto de origen.
Así, llevar la pinza a un punto y traerla de vuelta cuesta de media *un segundo*.

Los resultados del algoritmo descrito con distintos parámetros se recogen en las tablas 1–4.
En ellas se dan la complejidad y el tiempo de aprendizaje para modelos con distintas leyes de movimiento:

### **MotionLaw**: *ContinuousAcceleration & ContinuousDeceleration*

Tabla 1

| Etapa | Complejidad | Paso de cobertura | N.º medio de movimientos | Aciertos en puntos buscados | Tiempo |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1359 movimientos | 18,75 mm      | 1             | 1,8 %           | 23 minutos
| 2     | -          | -             | -             | -               | -
| 3     | 6796 movimientos | -             | 21            | 100 %           | 114 minutos
| Total | 8155 movimientos |               |               | 100 %           | 2,17 horas

Tabla 2

| Etapa | Complejidad | Paso de cobertura | N.º medio de movimientos | Aciertos en puntos buscados | Tiempo |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1359 movimientos | 18,75 mm      | 1             | 1,8 %           | 23 minutos
| 2     | 4288 movimientos | 5,625 mm      | 1             | 28,7 %          | 72 minutos
| 3     | 2973 movimientos | -             | 10            | 100 %           | 50 minutos
| Total | 8620 movimientos |               |               | 100 %           | 2,25 horas

### **MotionLaw**: *ContinuousSlowAcceleration & ContinuousDeceleration*

Tabla 3

| Etapa | Complejidad | Paso de cobertura | N.º medio de movimientos | Aciertos en puntos buscados | Tiempo |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1455 movimientos | 18,75 mm      | 1             | 0,3 %           | 25 minutos
| 2     | -          | -             | -             | -               | -
| 3     | 4563 movimientos | -             | 14            | 100 %           | 77 minutos
| Total | 6018 movimientos |               |               | 100 %           | 1,42 horas

Tabla 4

| Etapa | Complejidad | Paso de cobertura | N.º medio de movimientos | Aciertos en puntos buscados | Tiempo |
|:-----:|:----------:|:-------------:|:-------------:|:---------------:|:-----------:|
| 1     | 1455 movimientos | 18,75 mm      | 1             | 0,3 %           | 25 minutos
| 2     | 4217 movimientos | 5,625 mm      | 1             | 23,1 %          | 71 minutos
| 3     | 2973 movimientos | -             | 5             | 100 %           | 28 minutos
| Total | 8645 movimientos |               |               | 100 %           | 2,7 horas

* **N.º medio de movimientos** es la cantidad media de movimientos necesarios para alcanzar un punto buscado.


## CONCLUSIÓN

Como prueba de concepto se construyó un modelo 2D del manipulador con control discreto que permite simular distintas implementaciones de dispositivos,
se creó la base de datos de los movimientos realizados por el modelo del robot y se programó el algoritmo de posicionamiento.
El trabajo ha demostrado que basta con usar trayectorias aprendidas previamente para posicionar el robot.

El resultado del trabajo incluye además una estimación del tiempo total del proceso de aprendizaje, del número de movimientos necesarios para cubrir el objetivo con la precisión prescrita
y del volumen mínimo de la base de datos suficiente para un posicionamiento preciso.
El algoritmo de aprendizaje logra alcanzar todos los puntos dados en menos de 15 movimientos de media.
El aprendizaje completo del algoritmo requiere unas 2,5 horas.


## EL GRAN OBJETIVO

La tarea no se limita a controlar con eficacia un robot concreto.
Se quiere poder aprovechar la mayor parte de los resultados del aprendizaje de un robot para acelerar el aprendizaje de otros manipuladores similares.
(En la práctica, ni siquiera manipuladores del mismo tipo, fabricados con la misma tecnología y en la misma máquina, tienen un posicionamiento absolutamente idéntico,
debido a pequeñas diferencias de ajuste y montaje que no afectan a su fiabilidad).
Se quiere que la base de datos de un robot incluya la experiencia acumulada por otros.


## REFERENCIAS

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
11. [Ильва Эллнеби. Моторные движения](http://www.childneurologyinfo.com/sensory-text-breaking3.php){: hreflang=ru }
12. [Тарабарин В.Б. Конспект лекций по курсу ТММ](http://www.tmm-umk.bmstu.ru/lectures){: hreflang=ru }
13. [Golikov K.A. - Learning algorithm of systems with discrete control](http://intsysjournal.ru/pdfs/23-1/Golikov.pdf){: hreflang=ru }
14. [Golikov K.A. - Learning systems with descrete control](http://intsysjournal.ru/pdfs/22-4/Golikov.pdf){: hreflang=ru }


### CÓDIGO FUENTE

[El código fuente en C++ está disponible en GitHub](https://github.com/favorart/robot-hand/){: hreflang=en }
