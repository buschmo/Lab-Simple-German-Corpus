import matching.utilities as utl
import matching.DocumentMatching as dm
import json
import os
import sys
from pathlib import Path
from multiprocessing import Pool


def generate_aligned_corpus():
    similarity_measure = "maximum"
    sd_threshold = 1.5
    doc_matchings = "max"

    header_file = Path("results/header.json")

    if not os.path.exists("results/matched"):
        os.makedirs("results/matched")


def article_generator_parallel(matched_article_list: list[tuple[str, str]]) \
        -> tuple[str, str]:
    """
    Generator function that iteratively returns preprocessed articles.

    Args:
        matched_article_list: List of article pairs that is iterated through

    Returns:
        simple and normal link to file and preprocessed articles in the form simple_preprocessed(option_1), (..., simple_preprocessed(option_n)), normal_preprocessed(option_1), (..., normal_preprocessed(option_n))
    """

    for simple, normal in matched_article_list:

        with open(simple, 'r') as fp:
            simple_text = fp.read()
        with open(normal, 'r') as fp:
            normal_text = fp.read()

        # don't process exact copies
        if simple_text == normal_text:
            continue
        yield simple, normal, simple_text, normal_text


def article_preprocess(simple_text, normal_text):
    simple_original = utl.get_original_text_preprocessed(simple_text)
    normal_original = utl.get_original_text_preprocessed(normal_text)
    simple_arts = []
    normal_arts = []
    preprocessing_options = [kwargs_gram, kwargs_embeddings]
    for kwargs in preprocessing_options:
        simple_arts.append(utl.preprocess(simple_text, **kwargs))
        normal_arts.append(utl.preprocess(normal_text, **kwargs))

    return simple_original, normal_original, *simple_arts, *normal_arts


def parallel(simple_name, normal_name, simple_text, normal_text) -> dict[str, list[str]]:
    simple_original, normal_original, simple_gram, simple_embedding, normal_gram, normal_embedding = article_preprocess(
        simple_text, normal_text)

    simple_file = simple_name.split('/')[-1]
    normal_file = normal_name.split('/')[-1]

    if simple_file in header:
        finished = True
        for sim_measure in similarity_measures:
            for matching in doc_matchings:
                for sd_threshold in sd_thresholds:
                    filename = utl.make_file_name(
                        simple_file, normal_file, sim_measure, matching, sd_threshold)
                    if filename not in header[simple_file]:
                        finished = False
                        break
                if finished == False:
                    break
            if finished == False:
                break

        if finished == True:
            return {}

    else:
        header_extension = {simple_file: []}
        # print(f"Created new entry for file {simple_file}")

    for sim_measure in similarity_measures:
        if sim_measure == "n_gram":
            simple_n_tf = utl.calculate_n_gram_tf(simple_gram, n)
            normal_n_tf = utl.calculate_n_gram_tf(normal_gram, n)
            sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                        simple_n_tf, normal_n_tf, n_gram_idf)

        elif sim_measure == "bag_of_words":
            simple_word_tf = utl.calculate_word_tf(simple_gram)
            normal_word_tf = utl.calculate_word_tf(normal_gram)
            sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                        simple_word_tf, normal_word_tf, word_idf)

        else:
            sim_matrix = dm.calculate_similarity_matrix(
                simple_embedding, normal_embedding, sim_measure)

        for matching in doc_matchings:
            for sd_threshold in sd_thresholds:
                filename = utl.make_file_name(
                    simple_file, normal_file, sim_measure, matching, sd_threshold)
                if not os.path.exists(filename):
                    try:
                        results = dm.match_documents(matching, simple_original, normal_original,
                                                    sim_matrix, sd_threshold=sd_threshold)
                    except ValueError as err:
                        print(f"ValueError raised by {simple_file} - {normal_file}")
                        with open("error_log.txt", "a", encoding="utf-8") as fp:
                            fp.write(f"simple_file:{simple_file} - normal_file:{normal_file}\n\tsim_measure:{sim_measure} - matching:{matching} - thresh:{sd_threshold}\n")
                            fp.write(f"{sim_matrix}")
                            fp.write("\n\n\n#####\n\n\n")
                        continue

                    with open(filename, 'w') as fp:
                        json.dump(results, fp, ensure_ascii=False, indent=2)

                header_extension[simple_file].append(filename)

    return header_extension


def main():
    """
    Calculates all pairings of similarity measures and alignment methods.

    BEWARE! This calculation is not computed in parallel and thus takes a lot of time
    """
    global similarity_measures, sd_thresholds, doc_matchings, header, n, word_idf, n_gram_idf, kwargs_gram, kwargs_embeddings

    similarity_measures = ["n_gram", "bag_of_words",
                           "cosine", "average", "maximum", "max_matching", "CWASA"]

    sd_thresholds = [0.0, 1.5]

    doc_matchings = ["max", "max_increasing_subsequence"]

    header_file = "results/header.json"

    kwargs_gram = utl.make_preprocessing_dict(remove_punctuation=True)
    kwargs_embeddings = utl.make_preprocessing_dict(
        lowercase=False, remove_punctuation=True)

    if not os.path.exists("results/"):
        os.mkdir("results")

    if not os.path.exists("results/matched"):
        os.mkdir("results/matched")

    if not Path(header_file).exists():
        header = dict()

    else:
        with open(header_file, 'r') as fp:
            header = json.load(fp)

    n = 4

    print("Start working")

    articles = utl.get_article_pairs()
    unnested_articles = utl.get_unnested_articles(articles)

    idf_article_string = ''.join([art.split('/')[-1]
                                 for art in sorted(list(unnested_articles))])
    idf_article_hash = utl.get_hash(idf_article_string)

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
        word_idf = utl.calculate_full_word_idf(
            unnested_articles, **kwargs_gram)
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
        n_gram_idf = utl.calculate_full_n_gram_idf(
            unnested_articles, n, **kwargs_gram)
        print("Calculated new n gram idf")
        with open(f"results/{n}_gram_idf.json", 'w') as fp:
            json.dump([idf_article_hash, n_gram_idf], fp, ensure_ascii=False)

    with Pool() as p:
        header_extensions = p.starmap(parallel, article_generator_parallel(
            articles))
        for ext in header_extensions:
            for key in ext:
                if key in header.keys():
                    header[key] = header[key] + ext[key]
                else:
                    header[key] = ext[key]
        with open(header_file, 'w') as fp:
            json.dump(header, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
