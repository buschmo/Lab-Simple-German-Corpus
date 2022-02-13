import matching.utilities as util

from matching.DocumentMatching import *


if __name__ == '__main__':

    preprocessing_dict = util.make_preprocessing_dict(lowercase=False, remove_punctuation=True)

    articles = util.get_article_pairs()

    for i, (art1, art2) in enumerate(articles):

        try:
            with open(art1, 'r') as fp:
                text1 = fp.read()
                prep_text1 = util.preprocess(text1, **preprocessing_dict)

            with open(art2, 'r') as fp:
                text2 = fp.read()
                prep_text2 = util.preprocess(text2, **preprocessing_dict)
        except FileNotFoundError:
            print("FILE NOT FOUND")
            continue

        print("(Simple) Text 1\n\n", prep_text1)
        print("(Normal) Text 2\n\n", prep_text2)

        sim_matrix = calculate_similarity_matrix(prep_text1, prep_text2, 'max_matching')

        print(sim_matrix)

        print(match_documents_max(prep_text1, prep_text2, match_matrix=sim_matrix, sd_threshold=1.0))

        if i > 5:
            break

