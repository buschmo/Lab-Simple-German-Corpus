import matching.utilities as util
import numpy as np


def test_identical():
    article_pairs = util.get_article_pairs()

    different_articles = []

    not_found = 0

    for (art1, art2) in article_pairs:
        try:
            with open(art1, 'r') as fp:
                article1 = fp.read()
            with open(art2, 'r') as fp:
                article2 = fp.read()
        except FileNotFoundError:
            not_found += 1
            continue

        if article1 == article2:
            print("SIMILAR ARTICLE:", art1)
        else:
            different_articles.append((art1, art2))

    percentage_correct = len(different_articles) / (float(len(article_pairs)) - not_found)

    print(
        f"There are {len(different_articles)} article pairs that are not identical, which is {round(percentage_correct * 100, 2)} "
        f"percent of all found article pairs.")

    return percentage_correct, different_articles


def test_lengths():
    _, article_pairs = test_identical()

    len_normal = []
    len_simple = []

    for (art_simple, art_complex) in article_pairs:
        with open(art_simple, 'r') as fp:
            article1 = fp.read()
            len_simple.append(len(article1))
        with open(art_complex, 'r') as fp:
            article2 = fp.read()
            len_normal.append(len(article2))

    print(f"The average length of the Simple German articles is {np.round(np.mean(len_simple), 1)} characters "
          f"(std: {np.round(np.std(len_simple), 1)}).\n"
          f"The average length of the standard German articles is {np.round(np.mean(len_normal), 1)} characters "
          f"(std: {np.round(np.std(len_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")



if __name__ == '__main__':
    percentage_correct, different_arts = test_identical()
    test_lengths()


