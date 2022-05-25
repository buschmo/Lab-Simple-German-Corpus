from typing import Union, List

import spacy
import re
import numpy as np
import os
import json
import hashlib

from spacy.tokens import Doc

from matching import defaultvalues

nlp = spacy.load('de_core_news_lg')

dataset_location = defaultvalues.dataset_location

stopwords = nlp.Defaults.stop_words


def preprocess(text: str, remove_hyphens: bool = True, lowercase: bool = True, remove_gender: bool = True,
               lemmatization: bool = False, spacy_sentences: bool = True, remove_stopwords: bool = False,
               remove_punctuation: bool = False) \
        -> list[Doc]:
    """
    Preprocesses a string according to parameters that can be set by the user.

    Args:
        text: string that is to be preprocessed
        remove_hyphens: if true, removes hyphens of the form '-[A-Z]' (often found in Simple German) from the text
        lowercase: lowercases the article
        remove_gender: removes German gendering endings like *in or *innen
        lemmatization: lemmatizes the text
        spacy_sentences: removes the paragraphs from the text and thereby forces spacy to determine sentence borders
        remove_stopwords: removes stopwords for German as defined internally by spacy
        remove_punctuation: Removes punctuation marks

    Returns:
        A list of sentences, each in spacy format (e.g., including embedding vectors)
    """
    if spacy_sentences:
        text = text.replace('\n', ' ')
        text = re.sub('\s+', ' ', text)

    original_text_sents = [sent for sent in nlp(text).sents]

    if spacy_sentences:
        sent_list = [str(sent) for sent in nlp(text).sents]
    else:
        sent_list = [sent for sent in text.split('\n')]

    if remove_hyphens:
        sent_list = [re.sub('-[A-Z]', _kill_hyphen, sent)
                     for sent in sent_list]

    if remove_gender:
        sent_list = [re.sub('\*in(nen)?', '', sent) for sent in sent_list]
        sent_list = [re.sub(':in(nen)?', '', sent) for sent in sent_list]
        sent_list = [re.sub('_in(nen)?', '', sent) for sent in sent_list]
        sent_list = [re.sub('[a-z]In(nen)?', _kill_binnenI, sent)
                     for sent in sent_list]

    if lowercase:
        sent_list = [sent.lower() for sent in sent_list]

    if lemmatization:
        sent_list = [' '.join([word.lemma_ for word in nlp(sent)])
                     for sent in sent_list]

    if remove_stopwords:
        nlp_text = nlp(text)
        # TODO This is removable
        text = ' '.join(
            [word.text for word in nlp_text if word.text not in stopwords])

        sent_list = [' '.join(
            word.text for word in sent if word.text not in stopwords) for sent in sent_list]

    sent_list = [re.sub(' +', ' ', sent) for sent in sent_list]

    sent_list = [nlp(sent) for sent in sent_list]

    if remove_punctuation:
        sent_list = [nlp(' '.join(
            [str(token) for token in sent if not token.is_punct])) for sent in sent_list]

    assert len(sent_list) == len(original_text_sents)

    return sent_list


def _kill_hyphen(matchobj) -> str:
    """
    Helper function to remove hyphens

    Args:
        matchobj: matching object of re library

    Returns:
        The second element of the matching object, in lower case
    """
    return matchobj.group(0)[1].lower()


def _kill_binnenI(matchobj) -> str:
    """
    Helper function to remove the German Binnen-I (PilotInnen)

    Args:
        matchobj: matching object of re library

    Returns:
        The first element of the matching object
    """
    return matchobj.group(0)[0]


def get_unnested_articles(art_pairs=None) -> set[str]:
    """
    Uses the function get_article_pairs to get all articles, then calculates the complete set of articles

    Returns:
        Set of all articles
    """
    if art_pairs == None:
        art_pairs = get_article_pairs()

    article_set = set()

    for art0, art1 in art_pairs:
        article_set.add(art0)
        article_set.add(art1)

    return article_set


def get_exemplary_article_pairs(root_dir: str = dataset_location) -> list[tuple[str, str]]:
    """
    Returns a list of tuples in the form of (easy_article, normal_article) in the specified directory, one per source

    Args:
        root_dir: Directory in which to find the articles, potentially nested. Info needs to be given in exemplary_header.json files
    """
    parallel_list = []
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            if name == 'exemplary_header.json':
                with open(os.path.join(root, name), 'r') as fp:
                    data = json.load(fp)

                for fname in data:
                    for parallel_article in data[fname]['matching_files']:
                        parallel_list.append((os.path.join(root, fname + '.txt'),
                                              os.path.join(root, parallel_article + '.txt')))

    return parallel_list


def get_article_pairs(root_dir: str = dataset_location) -> list:
    """
    Returns a list of tuples in the form of (easy_article, normal_article) in the specified directory

    Args:
        root_dir: Directory in which to find the articles, potentially nested. Info needs to be given in parsed_header.json files
    """
    parallel_list = []
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            if name == 'parsed_header.json':
                with open(os.path.join(root, name), 'r') as fp:
                    data = json.load(fp)

                for fname in data:
                    # if str(root).endswith("www.brandeins.de"):
                    #     name = str(fname).replace('.html', '')
                    #     parallel_list.append((os.path.join(root, 'parsed/' + name + '_easy.html.txt'),
                    #                           os.path.join(root, 'parsed/' + name + '_normal.html.txt')))
                    #     continue
                    if 'matching_files' not in data[fname]:
                        continue
                    if 'easy' not in data[fname]:
                        continue
                    if not data[fname]['easy']:
                        continue
                    for parallel_article in data[fname]['matching_files']:
                        parallel_list.append((os.path.join(root, 'parsed/' + fname + '.txt'),
                                              os.path.join(root, 'parsed/' + parallel_article + '.txt')))

    return parallel_list


def calculate_full_n_gram_idf(articles: set[str], n=3, **kwargs) -> dict[str, float]:
    """
    Calculates the inverse document frequency, the inverse fraction of articles a n-gram appears in.

    Args:
        articles: list of article paths
        n: specify for n-gram
        **kwargs: arguments needed for preprocessing, can include remove_hyphens=True, lowercase, remove_gender, lemmatization, spacy_sentences, remove_stopwords, remove_punctuation

    Returns:
        idf dictionary from the articles
    """
    idf_dict = dict()
    article_count = 0

    for article in articles:

        article_n_gram_set = set()

        try:
            with open(article, 'r') as fp:
                text = fp.read()
                prep_text = preprocess(text, **kwargs)
                prep_text = ' '.join([str(sent) for sent in prep_text])

        except FileNotFoundError:
            print(f"Did not find file {article}")
            continue

        article_count += 1

        for i in range(len(prep_text) - n + 1):
            article_n_gram_set.add(prep_text[i:i + n])

        for elem in article_n_gram_set:
            if elem in idf_dict:
                idf_dict[elem] += 1
            else:
                idf_dict[elem] = 1

    if article_count == 0:
        return dict()
    # Usually, this is calculated as log(count/(v+1)), but as we know that v>0, we can leave out the +1
    return {k: np.log(article_count / v) for k, v in idf_dict.items()}


def calculate_full_n_gram_idf_from_texts(text_list: set[str], n=3, **kwargs) -> dict[str, float]:
    """
    Same as calculate_full_n_gram_idf, only for list of texts instead of file paths

    Args:
        articles: Set of article texts
        n: specify for n-gram
        **kwargs: arguments needed for preprocessing, can include remove_hyphens=True, lowercase, remove_gender, lemmatization, spacy_sentences, remove_stopwords, remove_punctuation


    Returns:
        idf dictionary from the articles
    """
    idf_dict = dict()
    article_count = 0

    for text in text_list:

        article_n_gram_set = set()

        article_count += 1

        prep_text = preprocess(text, **kwargs)
        prep_text = ' '.join([str(sent) for sent in prep_text])

        for i in range(len(prep_text) - n + 1):
            article_n_gram_set.add(prep_text[i:i + n])

        for elem in article_n_gram_set:
            if elem in idf_dict:
                idf_dict[elem] += 1
            else:
                idf_dict[elem] = 1

    if article_count == 0:
        return dict()
    return {k: np.log(article_count / v) for k, v in idf_dict.items()}


def calculate_full_word_idf(articles: set[str], **kwargs) -> dict[str, float]:
    """
    Calculates idf for words

    Args:
        articles: list of article paths
        **kwargs: argument dict for preprocessing

    Returns:
        idf for the articles
    """
    idf_dict = dict()
    article_count = 0

    for article in articles:

        article_n_gram_set = set()

        try:
            with open(article, 'r') as fp:
                text = fp.read()
                prep_text = preprocess(text, **kwargs)

        except FileNotFoundError:
            print(f"Did not find file {article}")
            continue

        article_count += 1

        for sent in prep_text:
            for word in sent:
                article_n_gram_set.add(str(word))

        for elem in article_n_gram_set:
            if str(elem) in idf_dict:
                idf_dict[str(elem)] += 1
            else:
                idf_dict[str(elem)] = 1

    if article_count == 0:
        return dict()
    return {k: np.log(article_count / v) for k, v in idf_dict.items()}


# TODO This function is never used and might be unnecessary
def calculate_n_gram_tf_from_article(article: str, n=3, **kwargs) -> dict[str, float]:
    """
    Calculates a n-gram tf dict for the text in the file path

    Args:
        article: file path
        n: specify for n-gram
        **kwargs: arguments for preprocessing, if applicable

    Returns:
        The n-gram tf dictionary
    """
    try:
        with open(article, 'r') as fp:
            text = fp.read()
            prep_text = preprocess(text, **kwargs)
    except FileNotFoundError:
        print(f"Did not find file {article}")
        return dict()

    return calculate_n_gram_tf(prep_text, n)


def calculate_n_gram_tf(preprocessed_text: list[Doc], n: int = 3) -> dict[str, float]:
    """
    Calculates the n-gram tf dictionary for a given text

    Args:
        preprocessed_text: text string, needs to be already preprocessed, in the form [s1, s2, s3, ...]!
        n: specified for n-gram length

    Returns:
        tf dictionary for the given text
    """
    n_gram_dict = dict()

    preprocessed_text = ' '.join([str(sent) for sent in preprocessed_text])

    if len(preprocessed_text) - n + 1 < 1:
        return dict()

    addition = 1.0 / (len(preprocessed_text) - n + 1)

    for i in range(len(preprocessed_text) - n + 1):
        if preprocessed_text[i:i + n] in n_gram_dict:
            n_gram_dict[preprocessed_text[i:i + n]] += addition
        else:
            n_gram_dict[preprocessed_text[i:i + n]] = addition

    return n_gram_dict


def calculate_word_tf(text: list[Doc]) -> dict[str, float]:
    """
        Calculates the n-gram tf dictionary for a given text

        Args:
            text: text, needs to be already preprocessed and in spacy format!

        Returns:
            tf dictionary for the given text
        """
    text = nlp(' '.join([str(sent) for sent in text]))

    if len(text) == 0:
        return dict()
    tf_dict = dict()
    addition = 1 / len(text)

    for word in text:
        if str(word) in tf_dict:
            tf_dict[str(word)] += addition
        else:
            tf_dict[str(word)] = addition

    return tf_dict


def make_n_grams(doc, n=3) -> list[str]:
    """
    Creates a list of n-grams for a given text

    Args:
        doc: spacy document or text string
        n: specify for n-gram length

    Returns:
        list of n-grams
    """
    return [str(doc[i:i + n]) for i in range(len(doc) - n + 1)]


def weighted(elem, tf: dict[str, float], idf: dict[str, float]) -> float:
    """
    Given an element and a tf and idf dictionary, returns the tf*idf value for this element

    Args:
        elem: string or word
        tf: tf dictionary
        idf: idf dictionary

    Returns:
        Value, i.e., tf[elem] * idf[elem] or 0 if the element is not existent in either dictionary
    """
    str_elem = str(elem)
    if str_elem not in tf:
        return 0.0
    if str_elem not in idf:
        return 0.0
    return tf[str_elem] * idf[str_elem]


def article_generator(matched_article_list: list[tuple[str, str]], *preprocessing_options) \
        -> tuple[str, str, list[Doc], list[Doc], list[Doc], list[Doc]]:
    """
    Generator function that iteratively returns preprocessed articles.

    Args:
        matched_article_list: List of article pairs that is iterated through
        *preprocessing_options: 1 or many preprocessing options.

    Returns:
        simple and normal link to file and preprocessed articles in the form simple_preprocessed(option_1), (..., simple_preprocessed(option_n)), normal_preprocessed(option_1), (..., normal_preprocessed(option_n))
    """
    for simple, normal in matched_article_list:
        simple_arts = []
        normal_arts = []
        with open(simple, 'r') as fp:
            simple_text = fp.read()
        with open(normal, 'r') as fp:
            normal_text = fp.read()

        # don't process exact copies
        if simple_text == normal_text:
            continue

        simple_original = get_original_text_preprocessed(simple_text)
        normal_original = get_original_text_preprocessed(normal_text)

        for kwargs in preprocessing_options:
            simple_arts.append(preprocess(simple_text, **kwargs))
            normal_arts.append(preprocess(normal_text, **kwargs))

        yield simple, normal, simple_original, normal_original, *simple_arts, *normal_arts


def get_original_text_preprocessed(text: str, spacy_sentences: bool = True) -> list[Doc]:
    if spacy_sentences:
        text = text.replace('\n', ' ')
        text = re.sub('\s+', ' ', text)
        sent_list = [sent for sent in nlp(text).sents]
    else:
        sent_list = [nlp(sent) for sent in text.split('\n')]

    return sent_list


def make_preprocessing_dict(remove_hyphens=True, lowercase=True, remove_gender=True, lemmatization=False,
                            spacy_sentences=True,
                            remove_stopwords=False, remove_punctuation=False) \
        -> dict[str, bool]:
    """
    Helper function that creates a dictionary that can be given as **kwargs argument to preprocessing, idf and other functions.
    Contains all the possible settings for preprocessing.
    Can be used as follows: kwargs=make_preprocessing_dict(); preprocess(text, **kwargs)

    Args:
        remove_hyphens: if true, removes hyphens of the form '-[A-Z]' (often found in Simple German) from the text
        lowercase: lowercases the article
        remove_gender: removes German gendering endings like *in or *innen
        lemmatization: lemmatizes the text
        spacy_sentences: removes the paragraphs from the text and thereby forces spacy to determine sentence borders
        remove_stopwords: removes stopwords for German as defined internally by spacy
        remove_punctuation: Removes punctuation marks

    Returns:
        Dictionary with the settings
    """
    return {'remove_hyphens': remove_hyphens, 'lowercase': lowercase, 'remove_gender': remove_gender,
            'lemmatization': lemmatization, 'spacy_sentences': spacy_sentences,
            'remove_stopwords': remove_stopwords, 'remove_punctuation': remove_punctuation}


def get_hash(string: str) -> int:
    if not isinstance(string, str):
        raise TypeError(f"Expected string, but got {type(string)}")
    return int(hashlib.sha1(string.encode("utf-8")).hexdigest(), 16)


def get_file_name_hash(simple_file: str, normal_file: str) -> int:
    string = simple_file + "___" + normal_file
    return get_hash(string)


def make_matching_path(simple_file: str, normal_file: str, sim_measure: str, matching: str, sd_threshold: float) -> str:
    hash = get_file_name_hash(simple_file, normal_file)
    return f"results/matched/{hash}--{sim_measure}--{matching}--{str(sd_threshold)}.matches"


def make_hand_aligned_path(simple_file: str, normal_file: str) -> str:
    hash = get_file_name_hash(simple_file, normal_file)
    simple = f"results/hand_aligned/{hash}.simple"
    normal = f"results/hand_aligned/{hash}.normal"
    return (simple, normal)


def make_alignment_path(simple_file: str, normal_file: str) -> tuple[str, str]:
    hash = get_file_name_hash(simple_file, normal_file)
    simple = f"results/alignment/{hash}.simple"
    normal = f"results/alignment/{hash}.normal"
    return (simple, normal)

def get_website_hashes(root_dir: str = dataset_location)->list:
    """
    Returns a list of tuples in the form of (easy_article, normal_article) in the specified directory

    Args:
        root_dir: Directory in which to find the articles, potentially nested. Info needs to be given in parsed_header.json files
    """
    website_hashes = {}
    for root, _, files in os.walk(root_dir):
        for name in files:
            if name == 'parsed_header.json':
                with open(os.path.join(root, name), 'r') as fp:
                    header = json.load(fp)

                website = root.split("/")[-1]
                website_hashes[website] = []
                for fname in header:
                    # if str(root).endswith("www.brandeins.de"):
                    #     name = str(fname).replace('.html', '')
                    #     parallel_list.append((os.path.join(root, 'parsed/' + name + '_easy.html.txt'),
                    #                           os.path.join(root, 'parsed/' + name + '_normal.html.txt')))
                    #     continue
                    if 'matching_files' not in header[fname]:
                        continue
                    if 'easy' not in header[fname]:
                        continue
                    if not header[fname]['easy']:
                        continue
                    for parallel_article in header[fname]['matching_files']:
                        website_hashes[website].append(get_file_name_hash(fname, parallel_article))

    return website_hashes