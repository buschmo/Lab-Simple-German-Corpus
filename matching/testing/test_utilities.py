from matching.utilities import *

if __name__ == '__main__':

    kwargs = {'remove_hyphens': True, 'lowercase': True, 'remove_gender': True, 'lemmatization': False,
            'spacy_sentences': True, 'remove_stopwords': False, 'remove_punctuation': True}

    articles = ['../../Datasets/toy_dataset/art1', '../../Datasets/toy_dataset/art2', '../../Datasets/toy_dataset/art3',
                '../../Datasets/toy_dataset/art4', '../../Datasets/toy_dataset/art5']

    idf_dict = calculate_full_n_gram_idf(articles, n=4, **kwargs)
    tf_dict_art1 = calculate_n_gram_tf_from_article(articles[1], n=4, **kwargs)

    print(tf_dict_art1)

    with open(articles[1], 'r') as fp:
        text1 = fp.read()
        prep_text1 = preprocess(text1, **kwargs)

    for n_gram in make_n_grams(' '.join([str(sent) for sent in prep_text1]), n=4):
        print(n_gram, weighted(n_gram, tf_dict_art1, idf_dict))