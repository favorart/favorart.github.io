---
title: "Aprendizaje de sistemas con control discreto"
summary: "Un algoritmo de aprendizaje para un sistema con control discreto: la experiencia de ensayo y error se almacena en una base de datos, y la predicción con interpolación reduce el tiempo de entrenamiento."
keywords: "posicionamiento, algoritmo de aprendizaje, robot, interpolación, aproximación"
source: sources.yml papers/learning-systems-discrete-control
source_lang: ru
source_hash: bc86fa48
translated: 2026-11-14
translator: Claude
reviewed: 2026-11-14
---
La ponencia presenta el desarrollo de un algoritmo que enseña a un sistema con control discreto a actuar y alcanzar objetivos. El aprendizaje se basa en el ensayo y error. Toda la experiencia del sistema se almacena en una base de datos. El algoritmo se optimiza según dos criterios: la precisión con la que se alcanzan los objetivos fijados y la máxima reducción del tiempo de aprendizaje. La reducción del tiempo de aprendizaje se consigue, principalmente, disminuyendo el número de acciones de prueba mediante métodos de predicción e interpolación a partir de los datos experimentales.
