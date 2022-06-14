import os
import random
import re
import spacy
import pickle
import bisect
import copy

from random import shuffle

import matching.utilities as utl
from align_by_hand import prep_text
from matching.defaultvalues import *

nlp = spacy.load("de_core_news_lg")

with open(website_sample_location, "rb") as f:
    samples = pickle.load(f)
# TODO: remove shuffle after finishing script
random.seed(42)
shuffle(samples)


def insert_break(text, index):
    inserted = text[:index] + "\n" + text[index:]
    return inserted


def remove_substring(text, start, substring):
    removed = text[:start] + text[start+len(substring):]
    return removed


def prepare_gt(hash_path):
    with open(hash_path) as f:
        gt = f.read()

    gt = gt.replace('\n', ' ')
    gt = re.sub('\s+', ' ', gt)
    # should return one big string here
    return gt


for simple_article_name, article_name in samples:
    with open(os.path.join(dataset_location, simple_article_name)) as f:
        simple_article = f.read()

    with open(os.path.join(dataset_location, article_name)) as f:
        article = f.read()

    hash_simple_article_path, hash_article_path = utl.make_hand_aligned_path(simple_article_name, article_name)

    variants = {"simple_german": {"article": list(set(prep_text(simple_article))),
                                  "gt": prepare_gt(hash_simple_article_path),
                                  "len(gt)": len(prepare_gt(hash_simple_article_path)),
                                  "fix": prepare_gt(hash_simple_article_path)},
                "german": {"article": list(set(prep_text(article))),
                           "gt": prepare_gt(hash_article_path),
                           "len(gt)": len(prepare_gt(hash_article_path)),
                           "fix": prepare_gt(hash_article_path)}}

    # sort sentences by length in descending order to first match and remove the longest sentences
    # such that the problem matching a smaller substring is avoided
    variants["simple_german"]["article"].sort(key=len, reverse=True)
    variants["german"]["article"].sort(key=len, reverse=True)
    assert isinstance(variants["simple_german"]["gt"], str), f"gt_article is not one big string, " \
                                                             f"but {type(variants['simple_german']['gt'])}"

    for v in variants.keys():
        # keep track of all insertions by index, sorted
        inserts = []
        # iterate over each sentence in the respective article
        for i in range(len(variants[v]["article"])):
            sentence = variants[v]["article"][i]
            # find all occurrences of the sentence in the respective gt file
            try:
                occur_indices = [f.start() for f in re.finditer(sentence, variants[v]["gt"])]
            except re.error:
                continue

            # might be int if there's only one occurrence
            if isinstance(occur_indices, int):
                occur_indices = [occur_indices]
            for ix in occur_indices:
                # keep inserts sorted
                bisect.insort(inserts, ix)
                assert inserts == sorted(inserts), "Inserts do not always stay sorted"

                position = inserts.index(ix)
                # insert break after the occurrence (+len(sent)),
                # taking into account the number of insertions made beforehand (+position)
                insert_at = ix+len(sentence)+position
                variants[v]["fix"] = insert_break(variants[v]["fix"], insert_at)
                # remove found sentence from gt to not match the same string again with a smaller substring
                # variants[v]["gt"] = remove_substring(variants[v]["gt"], ix, sentence)

        assert len(variants[v]["fix"]) == (variants[v]["len(gt)"]+len(inserts)), \
            f"Fixed gt {len(variants[v]['fix'])} has not length of gt ({variants[v]['len(gt)']}) " \
            f"+ len(inserts) ({len(inserts)})"

    num_simple_lines = len(variants["simple_german"]["fix"].split("\n"))
    num_lines = len(variants["german"]["fix"].split("\n"))

    assert num_simple_lines == num_lines, \
        f"Length of fixed ground truths doesn't match: {num_simple_lines} vs {num_lines}"

    # now save new result files with same names in different folder




