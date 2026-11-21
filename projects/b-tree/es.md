---
tagline: "Almacén clave-valor en disco: árbol B en C con journal"
summary: "Un almacén clave-valor en un único archivo, en C puro: páginas de árbol B, una caché LRU y un journal con sumas de verificación. La recuperación tras caídas se prueba matando un proceso hijo; los peores casos están medidos."
kind: "Motor de almacenamiento · C"
---

Un almacén clave-valor embebido con una API en C fijada de antemano, que escribí en 2015 en Technosphere, el programa de Mail.Ru Group y la Universidad Estatal de Moscú (MSU), y terminé en 2026. Cada página del archivo es un nodo del árbol B. La caché escribe todas las páginas modificadas a la vez, así que el archivo siempre contiene un árbol coherente, y al volver a aplicar el journal tras una caída del proceso se recuperan todos los cambios confirmados. Dividir una página llena en el punto de inserción mantiene las inserciones secuenciales con un 68 % de llenado de página.

## Cómo funciona

- **Árbol B sobre páginas.** Páginas de tamaño fijo (4 KB por defecto); las claves y los valores de longitud variable se guardan directamente en los nodos, hasta 1/8 de página por entrada. Las páginas llenas se dividen durante el descenso, en una sola pasada; al eliminar, una página con poco contenido se fusiona con su vecina o le toma entradas prestadas.
- **Mapa de espacio libre.** Unas páginas de servicio guardan un mapa de bits de las páginas libres, de modo que las páginas eliminadas se reutilizan.
- **Caché LRU.** Las páginas usadas recientemente permanecen en memoria (16 MB por defecto); al desalojar una página modificada se escriben todas y se llama a `fsync`.
- **Registro de cambios (journal).** Cada cambio se escribe primero en un registro con sumas de verificación en cada entrada; al abrir la base, se vuelven a aplicar las entradas posteriores al último checkpoint, y una entrada cortada por una caída se descarta.
- **Diagnóstico.** `db_check` verifica el árbol, `db_stats` informa de su forma y su nivel de llenado, `db_trace` registra las operaciones con cuatro niveles de detalle.

## Ingeniería

- C99 y POSIX puros, sin dependencias, compilado con Make.
- Pruebas con cmocka: pruebas unitarias de los módulos, operaciones aleatorias comparadas con un modelo de referencia, recuperación tras una caída en un proceso hijo y cargas de peor caso; todas se ejecutan también con AddressSanitizer y UndefinedBehaviorSanitizer.
- Un benchmark en el README: cuando el árbol cabe en la caché, unas 186 mil inserciones aleatorias y 594 mil consultas por segundo.
- CI en Linux (gcc y clang, con y sin los sanitizers) y macOS; cada push a `master` que pasa la CI recibe una etiqueta de versión y una GitHub Release.

## Limitaciones

El journal protege frente a una caída del proceso, no frente a un corte de luz; la base de datos la usa un solo proceso a la vez; es un árbol B, no un árbol B+.
