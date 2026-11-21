---
tagline: "Brza C++20 biblioteka bez zavisnosti za VCD talasne oblike"
summary: "Biblioteka u C++20 koja piše VCD fajlove sa talasnim oblicima: bez alokacije pri svakoj promeni vrednosti i sa izlazom koji je bajt po bajt isti na svakom OS-u. Provera sanitizerima otkrila je oštećenje hipa koje 18 zelenih testova nije primetilo."
kind: "Biblioteka · C++20"
---

Value Change Dump (VCD) je tekstualni format u kome hardverski simulatori beleže kako se signali menjaju u vremenu; GTKWave i drugi preglednici prikazuju ga kao talasne oblike. Python biblioteku [pyvcd](https://github.com/SanDisk-Open-Source/pyvcd) portovao sam u C++ 2017. godine. Godine 2026. pokrenuo sam je pod AddressSanitizer-om i UndefinedBehaviorSanitizer-om i pronašao prekoračenje bafera na hipu, dereferenciranje null pokazivača, destruktor koji baca izuzetak i neispravan VCD izlaz — sve skriveno iza 18 testova koji su prolazili, jer je referentni fajl sa kojim su testovi poredili rezultat zacementirao pogrešan izlaz. Posle ispravki biblioteka ima 39 testova, a prepisana kritična putanja učinila je `change()` [2–5 puta bržim](https://github.com/favorart/vcd-writer/pull/10).

## Šta je unutra

- **Standard, tačku po tačku.** VCD sa četiri stanja iz IEEE 1364-2005 §18.2: zaglavlje, ugnežđene oblasti, svih 18 tipova promenljivih, skalarne, vektorske i realne vrednosti, `$dumpvars`, `$dumpoff` / `$dumpon`; string vrednosti kao proširenje GTKWave-a. U README-u je tabela onoga što jeste i što nije podržano.
- **Bez alokacije po promeni.** Vrednosti se formatiraju u bafer od 64 KiB i upisuju jednim pozivom; benčmark je deo repozitorijuma.
- **Validacija bez sporednih efekata.** Imena, veličine, vrednosti i datum proveravaju se pre bilo kakve promene stanja, pa neuspeo poziv ne ostavlja trag u fajlu; vremenska oznaka u prošlosti baca izuzetak.
- **Deterministički izlaz iza malog interfejsa.** Fajl je bajt po bajt isti na svim platformama; interno stanje je sakriveno iza pimpl-a, a zavisnosti od biblioteka trećih strana nema.

## Inženjerska strana

- CI na Linux-u, Windows-u i macOS-u: GoogleTest i poređenje bajt po bajt sa referentnim fajlom; zaseban zadatak sve pokreće pod sanitizerima.
- Svaki komit koji prođe CI dobija oznaku semantičke verzije i GitHub Release sa unapred izgrađenim bibliotekama.
- U CMake projekat se uključuje preko `CPMAddPackage`; u README-u je poređenje sa pyvcd-om i cpp-vcd-tracer-om, funkciju po funkciju.
