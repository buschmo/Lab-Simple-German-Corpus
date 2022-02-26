from spacy.tokens.doc import Doc

import matching.utilities as util
from collections import Counter
import numpy as np
import scipy.optimize


def n_gram_similarity(sentence1: Doc, sentence2: Doc, tf1: dict[str, float], tf2: dict[str, float], idf: dict[str, float], n=3) \
        -> float:
    """
    Calculates n-gram-similarity between two sentences

    Args:
        sentence1: First sentence
        sentence2: Second sentence
        tf1: TF dictionary for the document sentence1 belongs to
        tf2: TF dictionary for the document sentence1 belongs to
        idf: IDF dictionary for the whole set of documents
        n: length of the n-grams (needs to be the same as for tf and idf)

    Returns:
        A similarity value for the sentences between 0 and 1
    """
    n_1 = util.make_n_grams(str(sentence1), n)
    n_2 = util.make_n_grams(str(sentence2), n)

    return _tf_idf_similarity(n_1, n_2, tf1, tf2, idf)


def bag_of_words_tf_idf_similarity(sentence1: Doc, sentence2: Doc, tf1: dict[str, float], tf2: dict[str, float], idf: dict[str, float]) \
        -> float:
    """
    Calculates the bag of words similarity between sentence1 and sentence2

    Args:
        sentence1: First sentence
        sentence2: Second sentence
        tf1: TF dictionary for the document sentence1 belongs to
        tf2: TF dictionary for the document sentence1 belongs to
        idf: IDF dictionary for the whole set of documents

    Returns:
        A similarity value for the sentences between 0 and 1
    """

    n_1 = util.make_n_grams(sentence1, 1)
    n_2 = util.make_n_grams(sentence2, 1)
    return _tf_idf_similarity(n_1, n_2, tf1, tf2, idf)


def _tf_idf_similarity(n_1: list[str], n_2: list[str], tf1: dict[str, float], tf2: dict[str, float], idf: dict[str, float]) \
        -> float:
    """
    Calculates tf_idf_similarity between two lists of values (could be words in sentences as well as n-grams)

    Args:
        n_1: list of words or n-grams
        n_2: second list of words or n-grams
        tf1: tf dict belonging to n_1
        tf2: tf dict belonging to n_2
        idf: idf dict

    Returns:
        A similarity value for the lists between 0 and 1
    """
    vec1 = Counter(n_1)
    vec2 = Counter(n_2)

    intersection = set(vec1.keys()) & set(vec2.keys())

    numerator = sum([util.weighted(x, tf1, idf) * vec1[x] *
                    util.weighted(x, tf2, idf) * vec2[x] for x in intersection])

    sum1 = sum([(util.weighted(x, tf1, idf) * vec1[x])
               ** 2 for x in vec1.keys()])
    sum2 = sum([(util.weighted(x, tf2, idf) * vec2[x])
               ** 2 for x in vec2.keys()])
    denominator = np.sqrt(sum1 * sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator


def cosine_similarity(sentence1: Doc, sentence2: Doc) \
        -> float:
    """
    Calculates cosine similarity between two sentences

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Cosine similarity, calculated automatically by spacy
    """
    return sentence1.similarity(sentence2)


def average_similarity(sentence1: Doc, sentence2: Doc) \
        -> float:
    """
    Calculates the average similarity between all word pairs

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Average similarity
    """
    sim_matrix = np.zeros(shape=(len(sentence1), len(sentence2)))

    for i, word1 in enumerate(sentence1):
        for j, word2 in enumerate(sentence2):
            sim_matrix[i, j] = word1.similarity(word2)

    return float(np.mean(sim_matrix))


def max_similarity(sentence1: Doc, sentence2: Doc) \
        -> float:
    """
    Calculates the maximal similarity first for the words from the first sentence, then for the words from the second
    sentence, and averages the two obtained values.

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Similarity measure between 0 and 1
    """
    if len(sentence1) == 0 or len(sentence2) == 0:
        return 0.0

    sim_matrix = np.zeros(shape=(len(sentence1), len(sentence2)))

    for i, word1 in enumerate(sentence1):
        for j, word2 in enumerate(sentence2):
            sim_matrix[i, j] = word1.similarity(word2)

    max1 = np.max(sim_matrix, axis=0)
    sts1 = sum(max1) / len(max1)

    max2 = np.max(sim_matrix, axis=1)
    sts2 = sum(max2) / len(max2)

    return (sts1 + sts2) / 2


def max_matching_similarity(sentence1: Doc, sentence2: Doc) \
        -> float:
    """
    Calculates the similarity by calculating a maximum weight matching using the Hungarian algorithm.
    A scipy function is used for the actual calculation on the matrix of word similarities.

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        A similarity measure, most likely between 0 and 1.
    """
    sim_matrix = np.zeros(shape=(len(sentence1), len(sentence2)))

    for i, word1 in enumerate(sentence1):
        for j, word2 in enumerate(sentence2):
            sim_matrix[i, j] = word1.similarity(word2)

    row_ind, col_ind = scipy.optimize.linear_sum_assignment(
        sim_matrix, maximize=True)

    if len(sentence1) == 0 or len(sentence2) == 0:
        return 0.0

    return (1.0 / min(len(sentence1), len(sentence2))) * sim_matrix[row_ind, col_ind].sum()


def CWASA_similarity(sentence1: Doc, sentence2: Doc) \
        -> float:
    """
    Calculates the CWASA similarity

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Similarity score between 0 and 1
    """
    match_s1 = np.array([-1.0] * len(sentence1))
    match_s2 = np.array([-1.0] * len(sentence2))
    index_s1 = np.array([-1] * len(sentence1))
    index_s2 = np.array([-1] * len(sentence2))

    for i, word1 in enumerate(sentence1):
        for j, word2 in enumerate(sentence2):
            sim = word1.similarity(word2)
            if sim > match_s1[i]:
                match_s1[i] = sim
                index_s1[i] = j

            if sim > match_s2[j]:
                match_s2[j] = sim
                index_s2[j] = i

    values = 0
    total = 0.0
    for i, (match, ind) in enumerate(zip(match_s1, index_s1)):
        if match <= 0:
            continue
        if i == index_s2[ind]:
            continue
        values += 1
        total += match

    for match, ind in zip(match_s2, index_s2):
        if match <= 0:
            continue
        values += 1
        total += match

    if values == 0:
        return 0

    return total / values
