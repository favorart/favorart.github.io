---
title: "vcd-writer: biblioteka u C++20 za VCD fajlove sa talasnim oblicima"
summary: "Port biblioteke pyvcd u C++20 bez zavisnosti, koji piše Value Change Dump fajlove (IEEE 1364-2005) bez alokacije pri svakoj promeni vrednosti."
kind: Biblioteka · C++20
---

Value Change Dump (VCD) je tekstualni format u kome hardverski simulatori beleže kako se signali menjaju u vremenu; preglednici kao što je GTKWave prikazuju ga kao talasne oblike. **vcd-writer** piše takve fajlove iz C++ koda: simulator, emulator ili test-okruženje registruje promenljive u ugnežđenim oblastima i javlja njihove promene, a biblioteka pravi VCD fajl koji otvara bilo koji preglednik talasnih oblika.

Nastala je 2017. kao port Python biblioteke [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd), a 2026. je preuređena u modernu biblioteku.

## Šta je unutra

- **Standard, proveren tačku po tačku.** VCD sa četiri stanja iz IEEE 1364-2005 §18.2: zaglavlje (`$date`, `$version`, `$timescale`, `$comment`), ugnežđene oblasti, svih 18 tipova promenljivih, skalarne, vektorske, realne i string vrednosti, `$dumpvars`, `$dumpoff` / `$dumpon`. U README-u je tabela onoga što jeste i što nije podržano.
- **Bez alokacije po promeni.** Vrednosti idu u izlazni bafer od 64 KiB; benčmark je deo repozitorijuma.
- **Validacija bez sporednih efekata.** Imena, veličine, vrednosti i datum proveravaju se pre bilo kakve promene stanja, pa neuspeo poziv ne ostavlja trag u fajlu; vremenska oznaka u prošlosti baca izuzetak.
- **Deterministički izlaz.** Fajl je bajt po bajt isti na svim platformama.
- **Čist interfejs.** Interno stanje je sakriveno iza pimpl-a; nema zavisnosti od biblioteka trećih strana.

## Inženjerska strana

- CI na Linux-u, Windows-u i macOS-u: jedinični testovi na GoogleTest-u i poređenje bajt po bajt sa referentnim fajlom; zaseban CI zadatak na Linux-u ih pokreće pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om.
- Svaki komit koji prođe CI dobija oznaku semantičke verzije i GitHub Release sa unapred izgrađenim bibliotekama.
- U CMake projekat se uključuje preko `CPMAddPackage`; postoji i build običnim Makefile-om.
- U README-u je poređenje sa pyvcd-om i cpp-vcd-tracer-om, funkciju po funkciju.

## Zašto je to važno

Mala biblioteka je dobro mesto da se pokaže ceo inženjerski ciklus: pažljivo pročitan standard, API koji je teško pogrešno upotrebiti, izmerene performanse i proces izdavanja kome nisu potrebni ručni koraci.
