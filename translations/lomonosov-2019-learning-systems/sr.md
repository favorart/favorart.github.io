---
title: "Učenje sistema sa diskretnim upravljanjem"
summary: "Saopštenje: sistem se uči pozicioniranju metodom pokušaja i grešaka, iskustvo se čuva u bazi podataka, a ravnomerna rešetka krajnjih položaja i gradijentni spust daju tačnu interpolaciju upravljanja."
source: sources.yml papers/lomonosov-2019-learning-systems
source_lang: ru
source_hash: 0502921f
translated: 2026-11-19
translator: Claude
reviewed: 2026-11-20
---
Sistem sa diskretnim upravljanjem uči da upravlja sobom metodom pokušaja i grešaka i njihovim uopštavanjem; celokupno iskustvo sistema čuva se u bazi podataka. Algoritam se razrađuje u virtuelnom okruženju na zadatku pozicioniranja dve vrste robota: manipulatora sa 2–3 rotaciona i prizmatična zgloba i mobilnog robota sa dve gusenice. Razvijen je dvoetapni algoritam za izgradnju ravnomerne rešetke krajnjih položaja, koji obezbeđuje uporedivost upravljanja i mogućnost njihovog usrednjavanja; pokazano je da se nasumično generisanim upravljanjima bez takve rešetke za razumno vreme učenja ne dobija dobra interpolacija. Približavanje ciljnim tačkama po rešetki vrši se stohastičkim gradijentnim spustom, a lokalna interpolacija upravljanja za bliske krajnje položaje obezbeđuje visoku tačnost pogađanja. Za korišćenje obučenog sistema podaci se prilagođavaju „u hodu“: pomeraji pri ponavljanju referentnih radnji beleže se i klasterizuju.
