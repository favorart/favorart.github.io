---
title: "Pasar a AVX-512 no aceleró los cálculos"
summary: "Por qué reescribir los bucles calientes de NeoML de AVX2 a AVX-512 no dio ninguna mejora: las «licencias» de frecuencia de Intel, el coste de la transición y la regla de Lemire."
source: posts/2026-11-avx512-frequency/index.md
source_lang: ru
source_hash: 8b5e3da9
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
En 2023 trabajaba en ABBYY en NeoML. Es un framework de ML de código abierto sobre el que corría, en servidores Windows, la inferencia de redes neuronales en producción. El código era lo más portable posible, así que al compilador solo se le permitía vectorizar hasta SSE/SSE2.

Un día se decidió acelerar puntualmente las partes más calientes para unos Xeon concretos. Las convoluciones, la multiplicación de matrices y las funciones vectoriales se reescribieron a mano con AVX2 y FMA, y para parte de las convoluciones se hizo JIT con xbyak. La mejora fue evidente.

Cuando llegué al equipo, la tarea sonaba lógica: si AVX2 dio una buena mejora, reescribamos los mismos cuellos de botella con AVX-512, que tiene el vector el doble de ancho. Irá más rápido, ¿verdad?

Lo reescribí y lo medí. Pues no: no hubo mejora.

La causa está en las «licencias» de frecuencia de Intel. Cuando un núcleo Xeon (Skylake-SP / Cascade Lake) ejecuta instrucciones vectoriales, pasa a un techo de frecuencia más bajo: L0 para el código normal, L1 para AVX2 pesado, L2 para AVX-512 pesado. Con AVX-512 intensivo en muchos núcleos, la pérdida de frecuencia llega a ~40 %. En nuestro caso, las instrucciones anchas iban en un flujo continuo dentro de bucles largos, y la ganancia por la anchura del vector se la comía la frecuencia más baja.

Probablemente se puede dejar que el compilador añada él mismo las instrucciones donde hagan falta, es decir, «echarlas poco a poco», pero eso tampoco sale gratis. Pasar a otra licencia cuesta 10–20 µs trabajando a medio gas, y la frecuencia anterior solo vuelve al cabo de ~2 ms. Una sola instrucción pesada suelta ralentiza todo el resto del código en ese núcleo, en el que, por cierto, corren 2 hilos de hyper-threading. Es revelador que GCC y Clang, incluso con AVX-512 activado, prefieran por defecto vectores de 256 bits (-mprefer-vector-width=256) precisamente por esto.

¿De dónde salen estas reglas? Todo es cuestión de energía y calor. Un FMA de 512 bits por ciclo conmuta muchísimos más transistores que el código escalar. La energía no se disipa por todo el chip, sino en una zona pequeña, la de las unidades vectoriales, y ahí se forma un punto caliente. La corriente sube de golpe, el voltaje cae, y el chip necesita subir el voltaje para que las unidades anchas funcionen de forma estable. Para no pasarse de los límites de potencia (TDP), corriente y temperatura, el procesador baja la frecuencia por adelantado, sin esperar a sobrecalentarse. De ahí el coste de la transición: mientras sube el voltaje y se encienden las mitades superiores de los registros vectoriales, que en modo normal están sin alimentación para ahorrar, el núcleo trabaja a medio gas.

Algo parecido ya lo había visto nuestro equipo antes: en procesadores con AVX-512, nuestra convolución rápida con AVX primero se desactivaba y luego se eliminó del todo.

Lo que saqué de todo esto:

- La regla de Daniel Lemire: AVX-512 se justifica si la ganancia por ciclo es claramente mayor que 2x.
- En los procesadores nuevos la penalización probablemente será menor, así que la respuesta depende del hardware. Mandan la frecuencia, la memoria y el tipo de carga.
- Primero medir, luego sacar conclusiones.

Para leer:

- [Cloudflare Blog: On the dangers of Intel's frequency scaling](https://blog.cloudflare.com/on-the-dangers-of-intels-frequency-scaling/){: hreflang=en }
- [Travis Downs, Performance Matters: Gathering Intel on Intel AVX-512 Transitions](https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html){: hreflang=en }
- [Daniel Lemire's blog: AVX-512: when and how to use these new instructions](https://lemire.me/blog/2018/09/07/avx-512-when-and-how-to-use-these-new-instructions){: hreflang=en }

![Imagen del post](cover.jpg)
