---
title: "Algoritam učenja sistema sa diskretnim upravljanjem"
summary: "Saopštenje: model pneumatskog pogona robota kao slučajnog procesa i algoritam koji u hodu kompenzuje drift mehanizma i održava tačnost pozicioniranja."
source: sources.yml papers/lomonosov-2020-learning-algorithm
source_lang: ru
source_hash: 5018b640
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---

Robot, jednom postavljen na radno mesto, neprekidno izvodi pozicionirajuće pokrete, a u njegovom mehanizmu i okruženju s vremenom nastaju promene koje utiču na tačnost. Predložen je model mišića (pneumatskog pogona) robota u aditivno-multiplikativnom obliku slučajnog procesa: deterministička komponenta sa ograničenjima brzine i ubrzanja, visokofrekventne prigušene oscilacije, niskofrekventni spori drift i izuzetne vrednosti. Algoritam učenja filtrira izuzetne vrednosti, podešava nestohastičke parametre i prati stohastičke, prebacujući se u hodu između nekoliko scenarija rada mišića kako bi održao zahtevanu tačnost pozicioniranja. Robot je opisan nehomogenim Markovljevim procesom odlučivanja sa diskretnim stanjima i diskretnim vremenom; za učenje se koristi varijanta metode spusta (hill climbing) sa prelaskom na prvo pronađeno susedno rešenje koje poboljšava rezultat.
