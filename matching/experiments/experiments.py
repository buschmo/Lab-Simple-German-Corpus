import matching.utilities as util

import matching.DocumentMatching as dm

similarity_measures = ["n_gram", "bag_of_words", "cosine", "average", "maximum", "max_matching", "CWASA"]

sd_thresholds = [0.0, 1.5]

doc_matchings = ["max", "max_increasing_subsequence"]

n = 4

if __name__ == '__main__':

    print("Start working")

    articles = util.get_article_pairs()
    unnested_articles = util.get_unnested_articles(articles)

    kwargs_gram = util.make_preprocessing_dict(remove_punctuation=True)
    kwargs_embeddings = util.make_preprocessing_dict(lowercase=False, remove_punctuation=True)

    word_idf = util.calculate_full_word_idf(unnested_articles, **kwargs_gram)

    print("Calculated word idf")

    n_gram_idf = util.calculate_full_n_gram_idf(unnested_articles, n, **kwargs_gram)

    print("Calculated n-gram idf")

    for simple_name, normal_name, simple_gram, simple_embedding, normal_gram, normal_embedding in util.article_generator(
        articles, kwargs_gram, kwargs_embeddings):
        print(simple_name, normal_name)

        for sim_measure in similarity_measures:
            if sim_measure == "n_gram":
                simple_n_tf = util.calculate_n_gram_tf(simple_gram, n)
                normal_n_tf = util.calculate_n_gram_tf(normal_gram, n)
                sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                            simple_n_tf, normal_n_tf, n_gram_idf)

            elif sim_measure == "bag_of_words":
                simple_word_tf = util.calculate_word_tf(simple_gram)
                normal_word_tf = util.calculate_word_tf(normal_gram)
                sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                            simple_word_tf, normal_word_tf, word_idf)

            else:
                sim_matrix = dm.calculate_similarity_matrix(simple_embedding, normal_embedding, sim_measure)

            for matching in doc_matchings:
                for sd_threshold in sd_thresholds:
                    if sim_measure in ["n_gram", "bag_of_words"]:
                        results = dm.match_documents(matching, simple_gram, normal_gram, sim_matrix, sd_threshold=sd_threshold)
                    else:
                        results = dm.match_documents(matching, simple_embedding, normal_embedding, sim_matrix, sd_threshold=sd_threshold)

                    print(sim_measure, matching, sd_threshold, results)

        break

import sys

sys.exit(0)
