# A Simple German corpus
Repository for the lab module MA-INF 4306 of the university of Bonn.

## About
The German language knows two versions of plain language: Einfach Sprache and [Leichte Sprache](https://leichte-sprache.de/), the latter being controlled by the _Netzwerk Leichte Sprache_.

## Tools/Libraries
- [spacy.io](https://spacy.io/) python library for natural language processing supporting a plethora of languages, including [german](https://spacy.io/models/de)

## Resources
### Mono
- Leichte Sprache:
    - https://www.nachrichtenleicht.de/
    - https://www1.wdr.de/hilfe/leichte-sprache/index.html
    - https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/Nachrichten-in-Leichter-Sprache,nachrichtenleichtesprache100.html
    - https://www.ard-text.de/mobil/870
    - https://www.bundesregierung.de/breg-de/leichte-sprache
    - https://www.institut-fuer-menschenrechte.de/leichte-sprache
    - https://www.deutsche-rentenversicherung.de/DRV/LS/Home/leichtesprache_node.html
    - https://taz.de/Leichte-Sprache/

- Einfach Sprache
    - https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/index.html


### Parallel
- Leichte Sprache:
    - https://www.mdr.de/nachrichten-leicht/index.html (am Ende findet sich der Link zum Artikel in Alltags-Sprache)
    - https://www.lebenshilfe-main-taunus.de/wohnen-und-arbeit-m-20/ (oben rechts Schalter zwischen Sprachen)
    - https://www.behindertenbeauftragter.de/DE/LS/startseite/startseite-node.html (Wechsel zur Alltags-Sprache in der Infobox)
    - https://www.einfach-teilhaben.de/DE/AS/Home/alltagssprache_node.html (Wechsel zur Alltags-Sprache im Reiter oberhalb des Textes)
    - https://www.sozialpolitik.com/ (durch Button oben wechseln)
    - https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache (einzelne Artikel lassen sich umschalten durch Button oberhalb des Textes)
    - https://www.augsburger-allgemeine.de/special/nachrichten-in-leichter-sprache/ (oft ein Artikel äquivalent in Alltags-Sprache durch Banner mitten im Text)
    - https://taz.de/Politik/Deutschland/Leichte-Sprache/!p5097/
    - https://www.brandeins.de/themen/rubriken/leichte-sprache

- Einfache Sprache:
    - https://www.apotheken-umschau.de/einfache-sprache/ (am Ende der Seite führt es zum Artikel in Alltags-Sprache)


- Einfache Sprache/ leichte Sprache
    - https://www.unsere-zeitung.at/category/nachrichten/topeasy/

### Potential Sources
- German learning platforms. Here we might be able to match course content from different speaking levels, i.e. A1 with C1.
    - [BBC](https://www.bbc.co.uk/languages/german/)
    - [Deutsche Welle](https://www.dw.com/en/learn-german/s-2469)
- Translating english websites
    - [Simple English Wikipedia](https://simple.wikipedia.org/wiki/Main_Page)

### Further Reading
- [Paper on stemming german words](https://refubium.fu-berlin.de/bitstream/handle/fub188/18405/tr-b-99-16.pdf;jsessionid=4CCD841DD41B12C997B47D899874D0C1?sequence=1)

## Difficulties

### English and German

- Long sentences are shortened drastically, which is not typical for traditional translations
    - Open question: How about learning summaries and returning summaries of paragraphs?
    - text summarization e.g. in https://arxiv.org/abs/1908.08345 (English) or https://reposit.haw-hamburg.de/handle/20.500.12738/9137 (German), https://reposit.haw-hamburg.de/handle/20.500.12738/9137 (PEGASUS), https://konfuzio.com/de/automatic-text-summarization-in-pdf-files/ (3. point, use PEGASUS)
- it may be hard to find and notice corresponding paragraph - sentence pairs. However, sentences that have a one-to-one correspondence may not be that hard in the original version of the sentence.

### Only German

- Composed nouns cause problems and are usually separated by a hyphen. 
    - Might be solvable by using spacy or learning from examples?
- It is difficult to separate capitalized words from proper names.
    - Potential solutions:
        - use spacy or something alike (if a word is not known/known to be a name, disregard)?
        - Words in all caps and words containing capitalized letter inside the word are probably proper names
- There is only little data, generally about few topics (often information for handicapped people) in German.
