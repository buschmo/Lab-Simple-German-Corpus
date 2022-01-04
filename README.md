# A Simple German corpus
Repository for the lab module MA-INF 4306 of the university of Bonn.

## About
The German language knows two versions of plain language: Einfache Sprache and [Leichte Sprache](https://leichte-sprache.de/), the latter being controlled by the _Netzwerk Leichte Sprache_.

## Tools/Libraries
- [spacy.io](https://spacy.io/) python library for natural language processing supporting a plethora of languages, including [german](https://spacy.io/models/de)


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
