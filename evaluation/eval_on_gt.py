import os
import json
import spacy
import pickle
import pandas as pd
from itertools import product

import matching.utilities as utl
from matching.defaultvalues import *

path_to_samples = "results/better_samples.pkl"
path_to_gt = "results/hand_aligned"
path_to_matchings = "/Users/vtoborek/sciebo/Lab Development and Application of Data Mining and Learning Systems/results/matched"

with open(path_to_samples, "rb") as f:
    samples = pickle.load(f)

sim_measures = ["average", "bag_of_words", "cosine", "CWASA", "max_matching", "maximum", "n_gram"]
matching_methods = ["max", "max_increasing_subsequence"]
sd_thresholds = [0.0, 1.5]

nlp = spacy.load("de_core_news_lg")

# results = pd.DataFrame(columns=["sim_measure", "matching_method", "thres", "correct", "precision", "recall", "F1"])
results = []


def create_gt_dict(simple_path, normal_path, nlp) -> dict:
    """
    Creates a dictionary of aligned sentences for one article.
    Args:
        path_names: list of two path names [simple article, article]

    Returns:
        Dictionary à la {simple_German_sentence: corresponding_German_sentence}
    """
    hash_easy_path, hash_normal_path = utl.make_hand_aligned_path(simple_path, normal_path)
    with open(hash_easy_path) as f:
        simple_article = f.read()

    with open(hash_normal_path) as f:
        article = f.read()

    simple_sents = [str(s) for s in nlp(simple_article).sents]
    normal_sents = [str(s) for s in nlp(article).sents]

    # breaks here for certain articles, because spacy cannot reconstruct original sentences from result files
    # assert len(simple_sents)==len(normal_sents), f"Amount of German and simple German sentences doesn't match: " \
    #                                              f"Simple {len(simple_sents)} vs. German {len(normal_sents)} " \
    #                                              f"for {simple_path}"

    gt = {}
    for s, n in zip(simple_sents, normal_sents):
        gt[s] = n
    return gt

not_found = 0
nothing_correct = 0

# for each article from samples
for simple_article, article in samples:
    simple_article_name = os.path.split(simple_article)[1]
    article_name = os.path.split(article)[1]

    # create ground truth dict: {simple sentence: normal sentence}
    article_gt = create_gt_dict(simple_article, article, nlp)

    # for each combination of sim_measure, matching_method, sd_threshold
    for sim, match_m, thres in product(sim_measures, matching_methods, sd_thresholds):
        name = utl.make_matching_path(simple_article_name, article_name, sim, match_m, thres)
        correct_alignments = 0
        try:
            with open(os.path.join(path_to_matchings, os.path.split(name)[1])) as f:
                alignments = json.load(f)
        # TODO: find out, why some files are not found under matches
        except FileNotFoundError:
            print(f">> FileNotFoundError: for article '{article_name}' with matching path '{name}'")
            not_found += 1
            continue

        for a in alignments:
            try:
                if article_gt[a[1][0]] == a[1][1]:
                    correct_alignments += 1
            except KeyError:
                pass

        if correct_alignments > 0:
            precision = correct_alignments / len(alignments)
            recall = correct_alignments / len(article_gt)
            F1 = 2 * (precision * recall) / (precision + recall)
        else:
            print(f">>> No correct alignments found in {article} by {sim}-{match_m}-{thres}")
            precision = 0
            recall = 0
            F1 = 0
            nothing_correct += 1

        results.append({"website": article.split("/")[0],
                        "article": article_name,
                        "sim_measure": sim,
                        "matching_method": match_m,
                        "thres": thres,
                        "correct": correct_alignments,
                        "precision": precision,
                        "recall": recall,
                        "F1": F1})

results_df = pd.DataFrame(results)
print(f"Number of files not found: {not_found}")
print(f"Number of instances with not a single correct alignment: {nothing_correct}")
print(results_df)
