import spacy

import matplotlib.pyplot as plt

import numpy as np

from matching.SimilarityMeasures import *

np.random.seed(42)

evals = 100000

if __name__ == '__main__':

    import matching.DocumentMatching as doc_matching

    nlp = spacy.load('de_core_news_lg')

    n = 4

    article_pairs = util.get_article_pairs()

    all_articles = util.get_unnested_articles(article_pairs)

    idf = util.calculate_full_n_gram_idf(all_articles, n, lowercase=True)

    word_idf = util.calculate_full_word_idf(all_articles, lowercase=True)

    cwasa_sims = []
    avg_sims = []
    cos_sims = []
    max_sims = []
    n_gram_sims = []
    word_tf_idf_sims = []
    hungarian_sims = []

    np.random.shuffle(article_pairs)

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

        print(doc_matching.match_documents_max(pre1_v1, pre2_v1,
                                               doc_matching.calculate_similarity_matrix(pre1_v1, pre2_v1, "max_matching")))

        for i, sent1 in enumerate(pre1_v1):
            for j, sent2 in enumerate(pre2_v1):
                cwasa_sims.append(CWASA_similarity(sent1, sent2))
                avg_sims.append(average_similarity(sent1, sent2))
                cos_sims.append(cosine_similarity(sent1, sent2))
                max_sims.append(max_similarity(sent1, sent2))
                hungarian_sims.append(max_matching_similarity(sent1, sent2))

        for i, sent1 in enumerate(pre1_v2_n_gram):
            for j, sent2 in enumerate(pre2_v2_n_gram):
                n_gram_sims.append(n_gram_similarity(sent1, sent2, tf1, tf2, idf, n))
                word_tf_idf_sims.append(bag_of_words_tf_idf_similarity(sent1, sent2, tf_word1, tf_word2, word_idf))

        if len(word_tf_idf_sims) > evals:
            break

    # print("CWASA", cwasa_sims[:100])
    # print("AVG", avg_sims[:100])
    # print("COS", cos_sims[:100])
    # print("MAX", max_sims[:100])
    # print("N-GRAM", n_gram_sims[:100])
    # print("N-GRAM", word_tf_idf_sims[:100])

    plt.hist(cwasa_sims[:evals], 50)
    plt.yscale('log')
    plt.title("CWASA DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cwasa_sims[:evals])}')
    plt.savefig("../figures/CWASA_distance_log.png")
    plt.show()

    plt.hist(avg_sims[:evals], 50)
    plt.yscale('log')
    plt.title("AVERAGE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(avg_sims[:evals])}')
    plt.savefig("../figures/avg_sim_distance_log.png")
    plt.show()

    plt.hist(cos_sims[:evals], 50)
    plt.yscale('log')
    plt.title("COSINE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cos_sims[:evals])}')
    plt.savefig("../figures/cos_sim_distance_log.png")
    plt.show()

    plt.hist(max_sims[:evals], 50)
    plt.yscale('log')
    plt.title("MAX DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(max_sims[:evals])}')
    plt.savefig("../figures/max_sim_distance_log.png")
    plt.show()

    plt.hist(n_gram_sims[:evals], 50)
    plt.yscale('log')
    plt.title("N-GRAM DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(n_gram_sims[:evals])}')
    plt.savefig("../figures/n_gram_distance_log.png")
    plt.show()

    plt.hist(word_tf_idf_sims[:evals], 50)
    plt.yscale('log')
    plt.title("WORD-TF-IDF DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(word_tf_idf_sims[:evals])}')
    plt.savefig("../figures/bag_of_words_distance_log.png")
    plt.show()

    plt.hist(hungarian_sims[:evals], 50)
    plt.yscale('log')
    plt.title("MAXIMUM MATCHING DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(hungarian_sims[:evals])}')
    plt.savefig("../figures/maximum_matching_distance_log.png")
    plt.show()


    ############## non-log images

    plt.hist(cwasa_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("CWASA DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cwasa_sims[:evals])}')
    plt.savefig("../figures/CWASA_distance.png")
    plt.show()

    plt.hist(avg_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("AVERAGE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(avg_sims[:evals])}')
    plt.savefig("../figures/avg_sim_distance.png")
    plt.show()

    plt.hist(cos_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("COSINE DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(cos_sims[:evals])}')
    plt.savefig("../figures/cos_sim_distance.png")
    plt.show()

    plt.hist(max_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("MAX DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(max_sims[:evals])}')
    plt.savefig("../figures/max_sim_distance.png")
    plt.show()

    plt.hist(n_gram_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("N-GRAM DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(n_gram_sims[:evals])}')
    plt.savefig("../figures/n_gram_distance.png")
    plt.show()

    plt.hist(word_tf_idf_sims[:evals], 50)
    # plt.yscale('log')
    plt.title("WORD-TF-IDF DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(word_tf_idf_sims[:evals])}')
    plt.savefig("../figures/bag_of_words_distance.png")
    plt.show()

    plt.hist(hungarian_sims[:evals], 50)
    plt.title("MAXIMUM MATCHING DISTANCE")
    plt.xlabel('distance')
    plt.ylabel(f'total ocurrences of {len(hungarian_sims[:evals])}')
    plt.savefig("../figures/maximum_matching_distance.png")
    plt.show()