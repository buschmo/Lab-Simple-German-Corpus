import matching.utilities as util

import matching.DocumentMatching as dm

import json

import hashlib

from pathlib import Path

similarity_measures = ["n_gram", "bag_of_words", "cosine", "average", "maximum", "max_matching", "CWASA"]

sd_thresholds = [0.0, 1.5]

doc_matchings = ["max", "max_increasing_subsequence"]

header_file = "results/header.json"

if not Path(header_file).exists():
    header = dict()

else:
    with open(header_file, 'r') as fp:
        header = json.load(fp)

n = 4

if __name__ == '__main__':

    print("Start working")

    articles = util.get_article_pairs()
    unnested_articles = util.get_unnested_articles(articles)

    kwargs_gram = util.make_preprocessing_dict(remove_punctuation=True)
    kwargs_embeddings = util.make_preprocessing_dict(lowercase=False, remove_punctuation=True)

    idf_article_string = ''.join([art.split('/')[-1] for art in sorted(list(unnested_articles))])
    idf_article_hash = int(hashlib.sha1(idf_article_string.encode("utf-8")).hexdigest(), 16)

    print("ARTICLE HASH", idf_article_hash)

    found = False
    word_idf = dict()

    if Path("results/word_idf.json").exists():
        with open("results/word_idf.json", 'r') as fp:
            hash, word_idf = json.load(fp)
            if hash == idf_article_hash:
                found = True
                print("Word idf was already computed!")

    if not found:
        word_idf = util.calculate_full_word_idf(unnested_articles, **kwargs_gram)
        print("Calculated new word idf")
        with open("results/word_idf.json", 'w') as fp:
            json.dump([idf_article_hash, word_idf], fp, ensure_ascii=False)

    found = False
    n_gram_idf = dict()

    if Path(f"results/{n}_gram_idf.json").exists():
        with open(f"results/{n}_gram_idf.json", 'r') as fp:
            hash, n_gram_idf = json.load(fp)
            if hash == idf_article_hash:
                found = True
                print("n_gram idf was already computed!")

    if not found:
        n_gram_idf = util.calculate_full_n_gram_idf(unnested_articles, n, **kwargs_gram)
        print("Calculated new n gram idf")
        with open(f"results/{n}_gram_idf.json", 'w') as fp:
            json.dump([idf_article_hash, n_gram_idf], fp, ensure_ascii=False)

    for simple_name, normal_name, simple_gram, simple_embedding, normal_gram, normal_embedding in util.article_generator(
        articles, kwargs_gram, kwargs_embeddings):
        print(simple_name, normal_name)

        simple_file = simple_name.split('/')[-1]
        normal_file = normal_name.split('/')[-1]

        if simple_file in header:

            finished = True

            for sim_measure in similarity_measures:
                for matching in doc_matchings:
                    for sd_threshold in sd_thresholds:
                        filename = util.make_file_name(simple_file, normal_file, sim_measure, matching, sd_threshold)
                        if filename not in header[simple_file]:
                            finished = False
                            break
                    if finished == False:
                        break
                if finished == False:
                    break

            if finished == True:
                continue

        else:
            header[simple_file] = []
            print(f"Created new entry for file {simple_file}")

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

                    filename = util.make_file_name(simple_file, normal_file, sim_measure, matching, sd_threshold)

                    with open(filename, 'w') as fp:
                        json.dump(results, fp, ensure_ascii=False, indent=2)

                    header[simple_file].append(filename)

                    with open(header_file, 'w') as fp:
                        json.dump(header, fp, ensure_ascii=False, indent=2)

import sys

sys.exit(0)
