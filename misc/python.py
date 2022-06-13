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
            p_s, p_n = utl.make_hand_aligned_path(*pair)
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
                                if len(simple) < 3:
                                    short.append(simple)
                                    continue
                                match = True
                                align_pairs.append([normal, simple])
                                # print(f"Removing #{simple}# from\n\t{align_simple}")
                                align_normal = align_normal[len(normal):]
                                align_simple = align_simple[len(simple):]
                                break
                        if not match:
                            for simple in short:
                                # print(f"\t\tshort list: {short}")
                                match = True
                                align_pairs.append([normal, simple])
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
            for i in [0, 1]:
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


def get_old_name(easy, normal):
    return f"{easy[-20:]}___{normal[-20:]}"


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
                for k, v in data.items():
                    if k != "finished":
                        normal_sentences += 1
                        pairs += len(v)
    print(
        f"Evaluated pairs: {pairs}\nEvaluated normal sentences: {normal_sentences}")

    easy_sentences = 0
    normal_sentences = 0
    for path, dirs, files in os.walk("Datasets/"):
        if "parsed_header.json" in files:
            with open(path+"/parsed_header.json") as fp:
                header = json.load(fp)
            for k, v in header.items():
                if v["easy"]:
                    with open(path+"/parsed/"+k+".txt") as fp:
                        easy_sentences += len(fp.readlines())
                else:
                    with open(path+"/parsed/"+k+".txt") as fp:
                        normal_sentences += len(fp.readlines())

    print(
        f"Parsed easy sentences: {easy_sentences}\nParsed normal sentences: {normal_sentences}")

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


def compare_hashes():
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


def rename_old_results():
    pairs = utl.get_article_pairs()
    hash_pairs = {(s.split("/")[-1],n.split("/")[-1]):utl.get_file_name_hash(s,n) for s,n in pairs}
    all_list = [get_old_name(easy, normal) +
                ".results" for easy, normal in pairs]
    all_set = set(all_list)
    dir_list = os.listdir("results/evaluated")
    if "1234654218863846309050772957188108835422355600671.results" in dir_list:
        dir_list.remove("1234654218863846309050772957188108835422355600671.results")
    if "1178337156844710522646525482484095458050847051918.results" in dir_list:
        dir_list.remove("1178337156844710522646525482484095458050847051918.results")
    if "-reden_easy.html.txt___eden_normal.html.txt.results" in dir_list:
        dir_list.remove("-reden_easy.html.txt___eden_normal.html.txt.results")
    if "gesetz-node.html.txt___gesetz-node.html.txt.results" in dir_list:
        dir_list.remove("gesetz-node.html.txt___gesetz-node.html.txt.results")

    rename = []
    rename.append(("-reden_easy.html.txt___eden_normal.html.txt.results","1178337156844710522646525482484095458050847051918.results"))
    rename.append(("gesetz-node.html.txt___gesetz-node.html.txt.results","1234654218863846309050772957188108835422355600671.results"))
    c = 0
    for s,n in hash_pairs:
        if "5621822" in s and "5613660" in n:
            rename.append(("e__!5621822.html.txt____!5613660__.html.txt.results", str(hash_pairs[(s,n)])+".results"))
            continue
        if "5617312" in s and "5613086" in n:
            rename.append(("e__!5617312.html.txt____!5613086__.html.txt.results", str(hash_pairs[(s,n)])+".results"))
            continue
        if "5621822" in s and "5616434" in n:
            rename.append(("e__!5621822.html.txt____!5616434__.html.txt.results", str(hash_pairs[(s,n)])+".results"))
            continue
        if "5634433" in s and "5619787" in n:
            rename.append(("e__!5634433.html.txt____!5619787__.html.txt.results", str(hash_pairs[(s,n)])+".results"))
            continue
        if "5621822" in s and "5617309" in n:
            rename.append(("e__!5621822.html.txt____!5617309__.html.txt.results", str(hash_pairs[(s,n)])+".results"))
            continue
        name = get_old_name(s, n)+".results"
        if name in dir_list:
            c+=1
            rename.append((name, hash_pairs[(s,n)]))

    for o,n in rename:
        os.rename(f"results/evaluated/{o}", f"results/evaluated/{n}")


if __name__ == "__main__":
    pass