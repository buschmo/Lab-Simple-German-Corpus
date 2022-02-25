import matching.utilities as util

similarity_measures = ["n_gram", "bag_of_words", "cosine", "average", "maximum", "max_matching", "CWASA"]

sd_thresholds = [0.0, 1.5]

if __name__ == '__main__':

    articles = util.get_article_pairs()

    kwargs_gram = util.make_preprocessing_dict(remove_punctuation=True)
    kwargs_embeddings = util.make_preprocessing_dict(lowercase=False, remove_punctuation=True)

    for simple_name, normal_name, simple_gram, simple_embedding, normal_gram, normal_embedding in util.article_generator(
        articles, kwargs_gram, kwargs_embeddings):
        print(simple_name, normal_name)

import sys

sys.exit(0)
