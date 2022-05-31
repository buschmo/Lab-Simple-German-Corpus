# A Simple German corpus
Repository for the lab module MA-INF 4306 of the university of Bonn.

## About
The German language knows two versions of plain language: Einfache Sprache (Simple German) and [Leichte Sprache](https://leichte-sprache.de/), the latter being controlled by the _Netzwerk Leichte Sprache_.

Currently, there are only few works that build a parallel corpus between Simple German and standard German. The goal of this lab is to build such a corpus by

1. Scraping websites with parallel versions for Simple German and standard German
2. Implementing various algorithms presented in the literature to form a corpus that contains aligned, "translated" sentences.

In later work, such a (potentially expanded) corpus may be used to implement automatic machine learning translation from standard German to Simple German. However, as it stands now, the amount of data is not sufficient for such a task.


## Resources
Papers that we use as inspiration for our work can be found in the resources wiki.

## Using this repository
Before using the repo, you **must** create the file `matching/defaultvalues.py`.
Within it, define a variable `dataset_location` with the absolute path to the `Dataset` folder. E.g. `dataset=/home/bob/Simple-German-Corpus/Datasets`
Please note, that downloading is throttled by a 5 second delay to reduce network traffic.
You can change this in `crawler/utilities.py`


To run the whole code, simply setup the environment and run `python main.py`.
This calls both `main_crawler.py` as well as `main_matching.py`.
The crawler downloads the archived websites and parses all contents.
The matcher calculates all corresponding match distances.
**Beware that the latter might take a lot of time, even though it is parallelized**.
The end result can be found in the `results/` folder.


To run other code, i.e. `evaluate.py` in the `evaluation` folder, use `python -m evaluation.evaluate`.
For manual alignment `python -m evaluation.align_by_hand` might come in handy.
*(This tool is by no means fully fleshed out)*


## Tools/Libraries
The code was written using python version 3.10.4.\
All python packages needed to run the code can be found in the "requirements" file and installed using
`pip install -r requirements`.
We recommend using a virtualenv.
- [spacy.io](https://spacy.io/) python library for natural language processing supporting a plethora of languages, including [German](https://spacy.io/models/de)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) python library for html parsing / crawling.
