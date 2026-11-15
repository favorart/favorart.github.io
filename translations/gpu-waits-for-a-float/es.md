---
title: "¿Cómo puede un solo float frenar el entrenamiento en la GPU?"
summary: "Un solo escalar enviado a la GPU con un cudaMemcpy síncrono detiene todo el pipeline de entrenamiento. Por qué pasa y cómo en NeoML se evitan las paradas pasando el número por valor."
source: posts/2026-11-gpu-waits-for-a-float/index.md
source_lang: ru
source_hash: f24792e0
translated: 2026-11-15
translator: Claude
reviewed: 2026-11-15
---
¿Cómo puede un solo float frenar el entrenamiento en la GPU?

Una tarjeta gráfica potente se pone en el servidor para que las matrices, las convoluciones y los gradientes vuelen. Da rabia ver cómo los cálculos sobre matrices enormes se quedan parados esperando. Este problema lo arreglé en NeoML, la biblioteca de ML de código abierto de ABBYY (de ella hablé en el [post anterior](/es/writing/avx512-frequency/)).

La tarjeta gráfica es una minicomputadora aparte con su propia memoria, y la RAM del programa no la ve: todo lo que necesita para calcular se lo llevan por el bus.

Al entrenar redes neuronales, el procesador casi no calcula nada él mismo: va encolando tareas para la GPU. Encola una en un par de microsegundos y sigue adelante, sin esperar el resultado. La GPU ejecuta las tareas estrictamente en orden. Si una escribe su resultado en la memoria de la tarjeta y la siguiente lo lee, no hay nada que esperar: cuando esta arranca, los datos ya están ahí. En un programa sano, la CPU va muy por delante y la cola de tareas de la GPU nunca se vacía.

Ahora supongamos que una tarea necesita un número de la CPU, apenas 4 bytes. La velocidad del bus no tiene nada que ver: por ahí pasan en un instante. Lo caro es el viaje en sí.

La función básica de copia en CUDA, cudaMemcpy, es síncrona: primero espera a que la GPU termine todo lo encolado antes y solo entonces copia. El orden importa: las tareas de la cola todavía pueden estar leyendo esa celda en la tarjeta, y necesitan el valor anterior.

Luego viene el transbordo. Los bytes por el bus los lleva un bloque aparte de la tarjeta, el DMA. Y solo sabe recogerlos de la RAM fijada (pinned): la que el sistema operativo no va a paginar a disco ni a mover de sitio. Por eso el driver copia el número a su propio búfer fijado, y solo desde ahí viaja a la tarjeta.

En resumen: la CPU se queda parada mientras la GPU vacía la cola, luego 2 transferencias, luego la GPU se queda ociosa mientras la CPU vuelve a llenar la cola. NVIDIA tiene una medición: una tarea tarda 2,9 µs en calcularse. Si la CPU no espera, salen 3,8 µs por tarea. Si espera después de cada una, 9,6. Es 2,5 veces más lento, y eso sin contar la copia.

Se puede evitar la espera: cudaMemcpyAsync encola la copia como una tarea más. Pero entonces el número tiene que estar en RAM fijada y no cambiar hasta que la cola llegue a él. Reservar esa memoria es lento y se le quita al sistema operativo, así que no se puede pedir un búfer nuevo para cada número. Hace falta un pool de celdas y llevar la cuenta de cuáles ya leyó la GPU. Todo un subsistema por 4 bytes.

En NeoML no existía. Casi todos los métodos recibían los escalares como una dirección en la memoria de la tarjeta, y los ponía ahí cudaMemcpy. El épsilon de máquina en la función de pérdida, el umbral de ReLU en los bloques de MobileNet, los límites del gradiente en el optimizador, en fin, cualquier coeficiente viajaba a la tarjeta con una parada completa del pipeline. En cada paso del entrenamiento.

Se encontró una vía alternativa: los argumentos de la tarea se pasan por valor, dentro del propio comando de lanzamiento del kernel. El número se escribe en el comando en el momento de encolarlo: ni búfer ni viaje. Venga de donde venga el coeficiente, de la memoria del programa por valor o de la memoria de la GPU por dirección, cuando la tarea arranca ya se conoce. No hay paradas en ningún caso.

El [PR](https://github.com/neoml-lib/neoml/pull/1070){: hreflang=en } que ayuda a la GPU a no esperar lleva desde 2024 esperando su turno.

¿Y a ustedes les ha tocado buscar qué está esperando su código?

\#CUDA #GPU #ML #rendimiento

Para leer:

* NVIDIA, CUDA Runtime API: API synchronization behavior — qué copia espera a la cola y cuál no https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html
* NVIDIA, How to Optimize Data Transfers in CUDA C/C++ — la memoria fijada y el coste de las transferencias pequeñas https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/
* NVIDIA, Getting Started with CUDA Graphs — de dónde salen las cifras de 2,9 / 3,8 / 9,6 µs https://developer.nvidia.com/blog/cuda-graphs/
* PyTorch Performance Tuning Guide https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html

![Imagen del post](cover.jpg)
