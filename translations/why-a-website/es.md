---
title: "¿Para qué quieres una web?"
summary: "Mi mujer me preguntó para qué quería una web. En dos tardes con Claude la hice y encontré la respuesta: cien pequeños «no» y orden en la cabeza."
source: posts/2026-11-why-a-website/index.md
source_lang: ru
source_hash: 79974efc
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-15
---
—me preguntó mi mujer con sorna.

No tenía respuesta. Tenía un currículum en un archivo YAML, un perfil en LinkedIn y unas vagas ganas de algo bonito, no hecho de cualquier manera. Dos tardes después, la web estaba lista. Y la respuesta, también.

## No sabía lo que quería

Llegué a Claude sin especificaciones. Solo tenía una idea de la web: cálida y moderna, con un toque de sol.

Claude me hacía preguntas y luego me proponía opciones: tres maquetas de la web, con un párrafo de descripción cada una. De una me gustaron la disposición y la navegación, de otra el estilo, de la tercera la animación. Elegí un fondo pastel y esquinas redondeadas, un ambiente suave y soleado, un menú en cada página y un zoom bien visible en las imágenes al pasar el ratón.

![Una de las tres maquetas: fondo pastel y el sol en el centro](img/cmp-a-full.png)

El sol se quedó en el centro por algo. Hace veintiséis siglos, el rey persa Kurush reunió el mayor imperio que el mundo había visto hasta entonces. Los griegos lo llamaban Kýros, Ciro, y al oído casi coincidía con su palabra «kýrios», señor. Al rey le venía como anillo al dedo. Y más de seiscientos años después, Plutarco escribió que a Ciro le pusieron ese nombre por el sol, porque así llaman al sol los persas. Los lingüistas no se fían de Plutarco. A mí me cae bien: soy casi tocayo del rey. Así que en el centro de la web brillo yo.

## ¿Qué aspecto tiene el cristal?

Al principio Claude me propuso lo que propone siempre: un minimalismo estricto, un estilo oscuro e ingenieril, tipo terminal, y una maquetación de revista con titulares grandes. Pero yo quería una web que no delatara mi slop de IA. Miré en mi interior y sentencié: cristal, superficies modernas, translúcidas y esmeriladas, con un reflejo.

Después nos peleamos mucho tiempo con los efectos y los fondos. El sol o deslumbraba y aplastaba todo lo que tenía alrededor, o desaparecía del todo.

![El sol: cuatro intentos](img/anim/10-sun.es.gif)

La reacción al ratón tampoco salió a la primera. Yo quería justo ese zoom sobre la imagen de la tercera maqueta.

![1. Rechazado: la tarjeta se eleva](img/anim/01-lift.es.gif)

![2. Aceptado: la imagen se amplía dentro de una tarjeta inmóvil](img/anim/02-zoom.es.gif)

Elegimos el zoom, pero yo no lo veía, y dos veces me quejé de que a mí simplemente no se ampliaba nada. Claude revisó los estilos dos veces, y todo estaba en su sitio. Resultó que en mi Windows los efectos de animación estaban desactivados. El navegador le transmitía fielmente a la web la petición de prescindir del movimiento, y la web fielmente no se movía. Mi propio Windows me prohibía ver lo que yo había encargado. Ahora, para los que son como yo, hay una versión discreta, en la que la imagen se amplía un poquito y rápido.

![Versión discreta: un poquito y rápido](img/anim/02b-quiet.es.gif)

Lo que más se resistió fue el propio cristal.

![3. Rechazado: el cristal se desliza fuera](img/anim/03-slide.es.gif)

![4. Paso: el cristal se desvanece entero](img/anim/04-fade.es.gif)

![5. Rechazado: la diagonal avanza desplazándose](img/anim/05-sweep.es.gif)

![6. Paso: la diagonal se desvanece](img/anim/06-diagfade.es.gif)

Por dónde pasa la diagonal y cuánto se difumina no se puede explicar con palabras. Así que Claude hizo una página de pruebas aparte, donde nueve variantes se mueven a la vez. Cubren el 30, el 20 o el 10 por ciento de la imagen, y su borde es nítido, medio o ancho. Uno mira y señala con el dedo la que quiere.

Elegí. Y luego me di cuenta de que todo ese tiempo había querido lo contrario.

![7. Casi: una esquina transparente, pero no la buena](img/anim/07-peekTL.es.gif)

![8. Aceptado: la esquina de abajo a la derecha; al pasar el ratón, el cristal se desvanece entero](img/anim/08-peekBR.es.gif)

## De los enlaces a los botones

Cómo resaltar los enlaces también lo decidimos al tercer intento.

![Enlaces: subrayado, rotulador, aparición](img/anim/09-links.es.gif)

El icono de la pestaña es toda la web en un cuadradito, con ese mismo sol. Ahora el sol nos recibe en el fondo, en la pestaña y en el logo de la página.

![Icono de la web: del cuadrado naranja al sol detrás de las letras](img/favicon-evolution.svg)

El botón bajo la sección de la página principal al principio decía simplemente «Todos los textos» y se escondía, pequeñito, en una esquina. No se entendía que detrás hubiera mucho más. Ahora invita a entrar con colores vivos y dice «Ver las 12 publicaciones», según su número real.

Debajo de cada nota hay dos botones iguales, pero solo «Enviar comentarios» es llamativo. Llama a quien ha leído hasta el final y casi se ha decidido a escribir. El camino de vuelta a la lista ya lo encontrará solo.

## ¿Qué hay bajo el capó? ¡Yo también tengo curiosidad!

Las notas de mis repositorios no se copian a la web. Corrijo el README en el repositorio y se corrige la página. No hay una segunda versión, así que no hay nada que pueda desincronizarse.

![Cómo se construye la web](img/build-scheme.es.png)

La web habla inglés, español, ruso, serbio y uzbeko. Quien haya leído mi currículum reconocerá en esta lista un mapa.

## Head of Slop Review

Bajo mi nombre, en la página principal, se van turnando unos cargos de broma. Uno se lo robé, lo confieso, a un colega: jefe del departamento de revisión de slop de IA. Es también el que mejor describe mi trabajo.

La firma al pie de cada página la escribió Claude por su cuenta: la web la hizo Claude mientras el humano elegía colores pastel. Yo le taché una palabra, y esa es, seguramente, mi mayor aportación a los textos de la web.

Cien pequeños «no», y salió una web con la que estoy contento. Cada uno precisaba algo no tanto de la web como de mí. Lo que quería lo iba descubriendo al rechazar.

Detalles como el tono del sol o la transparencia de los paneles los veía con solo recargar la página: la nueva versión se publica sola en un minuto o dos. Para las decisiones grandes, Claude montaba páginas de pruebas donde se veían todas las variantes a la vez. Eso es lo que más me fascina. Una sensación se convierte en una variante, la variante en una decisión, y esa decisión ya funciona en la web.

## Entonces, ¿para qué quiero una web?

Mientras la hacía, me di cuenta de cuántas cosas tengo por contar.

Notas que llevaban años repartidas por distintos repositorios. Posts que vivían en LinkedIn detrás del muro de inicio de sesión. Marcadores de «ya lo leeré», enlaces de «habría que darle forma», ideas a medio pensar. La web me obligó a ponerlo todo en orden. Algo acabó en una página. Algo, por fin, lo tiré. Preguntas abiertas desde hacía tiempo se cerraron.

La web no resultó ser un escaparate, sino una forma de poner orden en mi cabeza.

¡Estoy emocionadísimo! I'm excited, я очень вдохновлён! Soy como un niño con un juguete nuevo. Si de pequeño hubiera tenido uno así, ¡no habría salido de casa nunca, por nada del mundo!
