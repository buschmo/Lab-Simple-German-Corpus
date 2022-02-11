import utilities as util
from collections import Counter
import numpy as np
import spacy
import spacy.tokens.span
import matplotlib.pyplot as plt


def n_gram_similarity(sentence1, sentence2, tf1, tf2, idf, n=3):
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


def bag_of_words_tf_idf_similarity(sentence1, sentence2, tf1, tf2, idf):
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


def _tf_idf_similarity(n_1, n_2, tf1, tf2, idf):
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

    numerator = sum([util.weighted(x, tf1, idf) * vec1[x] * util.weighted(x, tf2, idf) * vec2[x] for x in intersection])

    sum1 = sum([(util.weighted(x, tf1, idf) * vec1[x]) ** 2 for x in vec1.keys()])
    sum2 = sum([(util.weighted(x, tf2, idf) * vec2[x]) ** 2 for x in vec2.keys()])
    denominator = np.sqrt(sum1 * sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator


def cosine_similarity(sentence1: spacy.tokens.span.Span, sentence2: spacy.tokens.span.Span):
    """
    Calculates cosine similarity between two sentences

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Cosine similarity, calculated automatically by spacy
    """
    return sentence1.similarity(sentence2)


def average_similarity(sentence1: spacy.tokens.span.Span, sentence2: spacy.tokens.span.Span):
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

    return np.mean(sim_matrix)


def max_similarity(sentence1: spacy.tokens.span.Span, sentence2: spacy.tokens.span.Span):
    """
    Calculates the maximal similarity first for the words from the first sentence, then for the words from the second
    sentence, and averages the two obtained values.

    Args:
        sentence1: First sentence
        sentence2: Second sentence

    Returns:
        Similarity measure between 0 and 1
    """
    sim_matrix = np.zeros(shape=(len(sentence1), len(sentence2)))

    for i, word1 in enumerate(sentence1):
        for j, word2 in enumerate(sentence2):
            sim_matrix[i, j] = word1.similarity(word2)

    max1 = np.max(sim_matrix, axis=0)
    sts1 = sum(max1) / len(max1)

    max2 = np.max(sim_matrix, axis=1)
    sts2 = sum(max2) / len(max2)

    return (sts1 + sts2) / 2


def CWASA_similarity(sentence1: spacy.tokens.span.Span, sentence2: spacy.tokens.span.Span):
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


if __name__ == '__main__':

    nlp = spacy.load('de_core_news_lg')

    # doc1 = nlp("Warum ist die Banane krumm? Weil niemand in den Urwald zog und die Banane gerade bog. ")
    # doc2 = nlp("Was hat dafür gesorgt, dass die Banane krumm wurde? Keiner besuchte den Regenwald, um die Frucht zu "
    #            "begradigen.")
    #
    # tf1 = util.calculate_n_gram_tf(doc1.text, n=3)
    # tf2 = util.calculate_n_gram_tf(doc2.text, n=3)
    # idf = util.calculate_full_n_gram_idf_from_texts([doc1.text, doc2.text, "Wer hat die Kuckucksuhr geklaut?",
    #                                                  "Die Affen tanzen durch en Wald",
    #                                                  "Wer nicht wagt der nicht gewinnt"], n=3)
    #
    # for sent in doc1.sents:
    #     for sent2 in doc2.sents:
    #         print(sent)
    #         print(sent2)
    #         print("CWASA:", CWASA_similarity(sent, sent2))
    #         print("avg:", average_similarity(sent, sent2))
    #         print("cos:", cosine_similarity(sent, sent2))
    #         print("max:", max_similarity(sent, sent2))
    #         print("n_gram:", n_gram_similarity(sent, sent2, tf1, tf2, idf, n=3))

    n = 4

    article_pairs = util.get_article_pairs()

    all_articles = util.get_unnested_articles()

    idf = util.calculate_full_n_gram_idf(all_articles, n, lowercase=True)

    word_idf = util.calculate_full_word_idf(all_articles, lowercase=True)

    cwasa_sims = []
    avg_sims = []
    cos_sims = []
    max_sims = []
    n_gram_sims = []
    word_tf_idf_sims = []

    for nr, (art1, art2) in enumerate(article_pairs):

        # art2 = article_pairs[nr + 55 % len(article_pairs)][1]

        try:
            with open(art1, 'r') as fp:
                text1 = fp.read()
            with open(art2, 'r') as fp:
                text2 = fp.read()
        except FileNotFoundError:
            continue

        kwargs = {'remove_hyphens': True, 'lowercase': False, 'remove_gender': True, 'lemmatization': False,
                  'spacy_sentences': True, 'remove_stopwords': False, 'remove_punctuation': True}

        kwargs_ngram = {'remove_hyphens': True, 'lowercase': True, 'remove_gender': True, 'lemmatization': False,
                        'spacy_sentences': True, 'remove_stopwords': False, 'remove_punctuation': True}

        pre1_v1 = util.preprocess(text1, **kwargs)
        pre2_v1 = util.preprocess(text2, **kwargs)
        pre1_v2_n_gram = util.preprocess(text1, **kwargs_ngram)
        pre2_v2_n_gram = util.preprocess(text2, **kwargs_ngram)

        tf1 = util.calculate_n_gram_tf(pre1_v2_n_gram, n)
        tf2 = util.calculate_n_gram_tf(pre2_v2_n_gram, n)

        tf_word1 = util.calculate_word_tf(pre1_v2_n_gram)

        tf_word2 = util.calculate_word_tf(pre2_v2_n_gram)

        for i, sent1 in enumerate(pre1_v1):
            for j, sent2 in enumerate(pre2_v1):
                if j < i:
                    continue
                cwasa_sims.append(CWASA_similarity(sent1, sent2))
                avg_sims.append(average_similarity(sent1, sent2))
                cos_sims.append(cosine_similarity(sent1, sent2))
                max_sims.append(max_similarity(sent1, sent2))

        for i, sent1 in enumerate(pre1_v2_n_gram):
            for j, sent2 in enumerate(pre2_v2_n_gram):
                if j < i:
                    continue
                n_gram_sims.append(n_gram_similarity(sent1, sent2, tf1, tf2, idf, n))
                word_tf_idf_sims.append(bag_of_words_tf_idf_similarity(sent1, sent2, tf_word1, tf_word2, word_idf))

        if len(word_tf_idf_sims) > 5000:
            break

    # print("CWASA", cwasa_sims[:100])
    # print("AVG", avg_sims[:100])
    # print("COS", cos_sims[:100])
    # print("MAX", max_sims[:100])
    # print("N-GRAM", n_gram_sims[:100])
    # print("N-GRAM", word_tf_idf_sims[:100])

    plt.hist(cwasa_sims, 50)
    plt.yscale('log')
    plt.title("CWASA DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cwasa_sims)}')
    plt.savefig("../figures/CWASA_distance_log.png")
    plt.show()

    plt.hist(avg_sims, 50)
    plt.yscale('log')
    plt.title("AVERAGE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(avg_sims)}')
    plt.savefig("../figures/avg_sim_distance_log.png")
    plt.show()

    plt.hist(cos_sims, 50)
    plt.yscale('log')
    plt.title("COSINE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cos_sims)}')
    plt.savefig("../figures/cos_sim_distance_log.png")
    plt.show()

    plt.hist(max_sims, 50)
    plt.yscale('log')
    plt.title("MAX DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(max_sims)}')
    plt.savefig("../figures/max_sim_distance_log.png")
    plt.show()

    plt.hist(n_gram_sims, 50)
    plt.yscale('log')
    plt.title("N-GRAM DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(n_gram_sims)}')
    plt.savefig("../figures/n_gram_distance_log.png")
    plt.show()

    plt.hist(word_tf_idf_sims, 50)
    plt.yscale('log')
    plt.title("WORD-TF-IDF DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(word_tf_idf_sims)}')
    plt.savefig("../figures/bag_of_words_distance_log.png")
    plt.show()


    ############## non-log images

    plt.hist(cwasa_sims, 50)
    # plt.yscale('log')
    plt.title("CWASA DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cwasa_sims)}')
    plt.savefig("../figures/CWASA_distance.png")
    plt.show()

    plt.hist(avg_sims, 50)
    # plt.yscale('log')
    plt.title("AVERAGE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(avg_sims)}')
    plt.savefig("../figures/avg_sim_distance.png")
    plt.show()

    plt.hist(cos_sims, 50)
    # plt.yscale('log')
    plt.title("COSINE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cos_sims)}')
    plt.savefig("../figures/cos_sim_distance.png")
    plt.show()

    plt.hist(max_sims, 50)
    # plt.yscale('log')
    plt.title("MAX DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(max_sims)}')
    plt.savefig("../figures/max_sim_distance.png")
    plt.show()

    plt.hist(n_gram_sims, 50)
    # plt.yscale('log')
    plt.title("N-GRAM DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(n_gram_sims)}')
    plt.savefig("../figures/n_gram_distance.png")
    plt.show()

    plt.hist(word_tf_idf_sims, 50)
    # plt.yscale('log')
    plt.title("WORD-TF-IDF DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(word_tf_idf_sims)}')
    plt.savefig("../figures/bag_of_words_distance.png")
    plt.show()
