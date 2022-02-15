from matching.utilities import *

if __name__ == '__main__':

    kwargs_embeddings = make_preprocessing_dict(lowercase=False, remove_punctuation=True)
    kwargs_n_gram = make_preprocessing_dict(lowercase=True, remove_punctuation=True)


    # articles = ['../../../Datasets/toy_dataset/art1', '../../../Datasets/toy_dataset/art2', '../../../Datasets/toy_dataset/art3',
    #             '../../../Datasets/toy_dataset/art4', '../../../Datasets/toy_dataset/art5']

    exemplary_articles = get_exemplary_article_pairs()

    exemplary_articles_unnested = get_unnested_articles(exemplary_articles)

    # idf = calculate_full_n_gram_idf(exemplary_articles_unnested, n=4, **kwargs)
    #
    # print(idf)

    import matching.DocumentMatching as dm

    for simple, normal in article_generator(exemplary_articles, kwargs_embeddings):
        match_matrix = dm.calculate_similarity_matrix(simple, normal, 'CWASA')
        matches = dm.match_documents_max_increasing_subsequence(simple, normal, match_matrix, sd_threshold=1.5)
        for elem in matches:
            print(elem)