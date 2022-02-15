# A Simple German corpus
Repository for the lab module MA-INF 4306 of the university of Bonn.

## About
The German language knows two versions of plain language: Einfache Sprache (Simple German) and [Leichte Sprache](https://leichte-sprache.de/), the latter being controlled by the _Netzwerk Leichte Sprache_.

Currently, there are only few works that build a parallel corpus between Simple German and standard German. The goal of this lab is to build such a corpus by

1. Scraping websites with parallel versions for Simple German and standard German
2. Implementing various algorithms presented in the literature to form a corpus that contains aligned, "translated" sentences.

In later work, such a (potentially expanded) corpus may be used to implement automatic machine learning translation from standard German to Simple German. However, as it stands now, the amount of data is not sufficient for such a task 

## Resources

Papers that we use as inspiration for our work can be found in the resources wiki.

## Tools/Libraries
- [spacy.io](https://spacy.io/) python library for natural language processing supporting a plethora of languages, including [German](https://spacy.io/models/de)
