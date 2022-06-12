import os
import json
import matching.utilities as utl
import pickle as pkl
import re
from pathlib import Path
from matching.defaultvalues import *
import spacy

nlp = spacy.load("de_core_news_lg")
def prep_text(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    sents = [str(sent) for sent in nlp(text).sents]
    return sents

def split_lines():
    """ By a mistake in hand_align all lines were saved without a trailing \n
    This function fixes that
    """
    out = "results/new/"
    if not os.path.isdir(out):
        os.makedirs(out)
    
    with open("results/website_samples.pkl", "rb") as fp:
        pairs = pkl.load(fp)

    for pair in pairs:
        with open(Path(dataset_location, pair[0])) as fp_simple, open(Path(dataset_location, pair[1])) as fp_normal:
            # print(pair)
            # print(*pair)
            p_s,p_n = utl.make_hand_aligned_path(*pair)
            with open(p_s) as fp_ressim, open(p_n) as fp_resnor:
                simple_lines = prep_text(fp_simple.read())
                normal_lines = prep_text(fp_normal.read())
                align_simple = fp_ressim.read()
                align_normal = fp_resnor.read()
                orig_s = align_simple
                orig_n = align_normal

                simple_lines.sort(reverse=True)

                align_pairs = []
                for normal in normal_lines:
                    match = True
                    while(align_normal.startswith(normal) and match):
                        # print("Matched")
                        match = False
                        short = []
                        for simple in simple_lines:
                            if align_simple.startswith(simple):
                                if len(simple)<3:
                                    short.append(simple)
                                    continue
                                match = True
                                align_pairs.append([normal,simple])
                                # print(f"Removing #{simple}# from\n\t{align_simple}")
                                align_normal = align_normal[len(normal):]
                                align_simple = align_simple[len(simple):]
                                break
                        if not match:
                            for simple in short:
                                # print(f"\t\tshort list: {short}")
                                match = True
                                align_pairs.append([normal,simple])
                                # print(f"Stemming from {simple_lines}")
                                # print(f"Removing #{simple}# from\n\t #{align_simple}")
                                align_normal = align_normal[len(normal):]
                                align_simple = align_simple[len(simple):]
                        if not match:
                            # print(f"{align_normal}")
                            # print(f"{align_simple}")
                            print("##### Not accounted #####")
                            print(f"{simple_lines}")
                            print("@@@@@")
                            print(f"{align_simple}")
                            return
                        
        h = utl.get_file_name_hash(*pair)
        # print(h)
        with open(f"{out}/{h}.normal", "w") as write_normal, open(f"{out}/{h}.simple", "w") as write_simple:
            for align_pair in align_pairs:
                write_normal.write(align_pair[0]+"\n")
                write_simple.write(align_pair[1]+"\n")
        
    # with open("out.md", "w") as fp_out:
        # for path, _, files in os.walk("results/hand_aligned"):
        #     for file in files:
        #         if os.path.exists(out + file):
        #             continue
        #         lines = []
        #         with open(path+"/"+file) as fp:
        #             print(file)
        #             string = fp.read()
        #             while string:
        #                 match = re.search("\S[.:!?]\S", string)
        #                 if not match:
        #                     if string:
        #                         lines.append(string)
        #                         break
        #                     else:
        #                         print("Unaccounted")
        #                         exit()
        #                 line = string[:match.end()-1]
        #                 new_string = string[match.end()-1:]
        #                 m = re.search('\S[.:!?]\S', new_string)
        #                 if m:
        #                     pos = m.end()-1
        #                 else:
        #                     pos = len(new_string)
        #                 fp_out.write(
        #                     f"#####\n\t{line}\n\t{new_string[:pos]}\n")
        #                 lines.append(line)
        #                 string = new_string
        #         with open(out + file, "w") as fp:
        #             for line in lines:
        #                 fp.write(line+"\n")


def rename_hashes_and_files():
    """ Rename hash files according to new/correct urls
    """
    with open("results/website_samples.pkl", "rb") as fp:
        pairs = pkl.load(fp)
        new_pairs = []
        for p in pairs:
            for i in [0, 1]:
                if not "/parsed/" in p[i]:
                    path = Path(p[i])
                    path = Path(path.parent, "parsed", path.name)
                    p[i] = str(path)
                if not p[i].endswith(".txt"):
                    p[i] += ".txt"
                p[i] = re.sub("parsed/www.", "parsed/", p[i])
            old_hash = utl.get_file_name_hash(p[0], p[1])
            for i in [0,1]:
                p[i] = re.sub("__.html.txt", ".html.txt", p[i])
            if p[1] == "www.stadt-koeln.de/parsed/stadt-koeln.de__service__produkt__anmeldung-eines-hundes.html.txt":
                p[1] = "www.stadt-koeln.de/parsed/stadt-koeln.de__service__produkt__anmeldung-eines-hundes-1.html.txt"
            if p[1] == "www.stadt-koeln.de/parsed/stadt-koeln.de__service__produkte__wunschkennzeichen.html.txt":
                p[1] = "www.stadt-koeln.de/parsed/stadt-koeln.de__service__produkt__wunschkennzeichen.html.txt"
            new_hash = utl.get_file_name_hash(p[0], p[1])
            if old_hash != new_hash:
                print(p)
                os.rename(
                    f"results/hand_aligned/{old_hash}.normal", f"results/hand_aligned/{new_hash}.normal")
                os.rename(
                    f"results/hand_aligned/{old_hash}.simple", f"results/hand_aligned/{new_hash}.simple")
            new_pairs.append(p)
    with open("results/website_samples.pkl", "wb") as fp:
        pkl.dump(new_pairs, fp)


def get_old_hash(easy, normal):
    string = easy + "___" + normal
    return utl.get_hash(string)


def compare(pairs):
    """ Compare the hashes
    """
    old_hashes = [get_old_hash(p[0], p[1]) for p in pairs]
    new_hashes = [utl.get_file_name_hash(p[0], p[1]) for p in pairs]

    print("\t", "old")
    c = 0
    for hash in old_hashes:
        if os.path.exists(f"results/hand_aligned/{hash}.normal"):
            c += 1
        if os.path.exists(f"results/hand_aligned/{hash}.simple"):
            c += 1
    print("\t", c)

    print("\t", "new")
    c = 0
    for hash in new_hashes:
        if os.path.exists(f"results/hand_aligned/{hash}.normal"):
            c += 1
        if os.path.exists(f"results/hand_aligned/{hash}.simple"):
            c += 1
    print("\t", c)



def statistics():
    pairs = 0
    normal_sentences = 0
    for path, dirs, files in os.walk("results/evaluated/"):
        for file in files:
            with open(path+file) as fp:
                data = json.load(fp)
                for k,v in data.items():
                    if k!="finished":
                        normal_sentences += 1
                        pairs += len(v)
    print(f"Evaluated pairs: {pairs}\nEvaluated normal sentences: {normal_sentences}")

    easy_sentences = 0
    normal_sentences = 0
    for path, dirs, files in os.walk("Datasets/"):
        if "parsed_header.json" in files:
            with open(path+"/parsed_header.json") as fp:
                header = json.load(fp)
            for k,v in header.items():
                if v["easy"]:
                    with open(path+"/parsed/"+k+".txt") as fp:
                        easy_sentences += len(fp.readlines())
                else:
                    with open(path+"/parsed/"+k+".txt") as fp:
                        normal_sentences += len(fp.readlines())

    print(f"Parsed easy sentences: {easy_sentences}\nParsed normal sentences: {normal_sentences}")

    pairs = utl.get_article_pairs()
    similarity_measures = ["n_gram", "bag_of_words",
                            "cosine", "average", "maximum", "max_matching", "CWASA"]

    sd_thresholds = [0.0, 1.5]

    doc_matchings = ["max", "max_increasing_subsequence"]

    paths = []
    for sim_measure in similarity_measures:
        for sd_threshold in sd_thresholds:
            for matching in doc_matchings:
                for simple_file, normal_file in pairs:
                    if "apotheke" in simple_file:
                        print(simple_file)
                    path = utl.make_matching_path(
                        simple_file, normal_file, sim_measure, matching, sd_threshold)
                    paths.append(path)

    matched = os.listdir("results/matched")
    print(f"{len(paths)} vs {len(matched)}")


def main():
    temp = utl.get_article_pairs()
    all_pairs = []
    for p in temp:
        t = [0, 0]
        for i in [0, 1]:
            t[i] = str(Path(p[i]).relative_to(dataset_location))
        all_pairs.append(tuple(t))
    print("All")
    compare(all_pairs)

    with open("results/website_samples.pkl", "rb") as fp:
        pairs = pkl.load(fp)
        pairs = [tuple(p) for p in pairs]
    print("Sample")
    compare(pairs)


if __name__ == "__main__":
    pass