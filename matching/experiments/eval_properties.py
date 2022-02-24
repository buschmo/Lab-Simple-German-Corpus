import matching.utilities as util
import numpy as np
import matplotlib.pyplot as plt




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
            continue
        else:
            different_articles.append((art1, art2))

    percentage_correct = len(different_articles) / (float(len(article_pairs)) - not_found)

    print(
        f"There are {len(different_articles)} article pairs that are not identical, which is {round(percentage_correct * 100, 2)} "
        f"percent of all found article pairs.")

    return percentage_correct, different_articles


def test_lengths(article_pairs=None):
    if not article_pairs:
        _, article_pairs = test_identical()

    len_simple = []
    len_normal = []

    words_simple = []
    words_normal = []

    len_words_simple = []
    len_words_normal = []

    for (art_simple, art_complex) in article_pairs:
        with open(art_simple, 'r') as fp:
            article1 = fp.read()
            len_simple.append(len(article1))

            nlp1 = util.nlp(article1)
            words = 0
            for word in nlp1:
                if word.is_punct:
                    continue
                words += 1
                len_words_simple.append(len(str(word)))
            words_simple.append(words)

        with open(art_complex, 'r') as fp:
            article2 = fp.read()
            len_normal.append(len(article2))

            nlp2 = util.nlp(article2)
            words = 0
            for word in nlp2:
                if word.is_punct:
                    continue
                words += 1
                len_words_normal.append(len(str(word)))
            words_normal.append(words)

    print(f"The average length of the Simple German articles is {np.round(np.mean(len_simple), 1)} characters "
          f"(std: {np.round(np.std(len_simple), 1)}).\n"
          f"The average length of the standard German articles is {np.round(np.mean(len_normal), 1)} characters "
          f"(std: {np.round(np.std(len_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")

    print(f"The average number of words in Simple German articles is {np.round(np.mean(words_simple),1)}. "
          f"(std: {np.round(np.std(words_simple), 1)}).\n"
          f"The average number of words in standard German articles is {np.round(np.mean(words_normal), 1)} "
          f"(std: {np.round(np.std(words_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")

    print(f"The average length of the words in Simple German articles is {np.round(np.mean(len_words_simple), 1)} characters "
          f"(std: {np.round(np.std(len_words_simple), 1)}).\n"
          f"The average length of the words in standard German articles is {np.round(np.mean(len_words_normal), 1)} characters "
          f"(std: {np.round(np.std(len_words_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")

    combined_data = []
    combined_data.append(len_simple)
    combined_data.append(len_normal)

    plt.hist(combined_data, bins=20, range=(0, 20000), label=['Simple German', 'Standard German'],
             color=['red', 'blue'], stacked=False)
    plt.legend()
    plt.title('Length of German articles')

    plt.show()

    combined_data = []
    combined_data.append(words_simple)
    combined_data.append(words_normal)

    plt.hist(combined_data, bins=20, range=(0, 3000), label=['Simple German', 'Standard German'],
             color=['red', 'blue'], stacked=False)
    plt.legend()
    plt.title('Number of words in German articles')

    plt.show()

    combined_data = []
    combined_data.append(len_words_simple)
    combined_data.append(len_words_normal)

    plt.hist(combined_data, range=(0,25), label=['Simple German', 'Standard German'],
             color=['red', 'blue'], stacked=False)
    plt.legend()
    plt.title('Length of words in German articles')

    plt.show()


if __name__ == '__main__':
    print("Working")

    percentage_correct, different_arts = test_identical()

    test_lengths(different_arts)

import sys

sys.exit(0)
