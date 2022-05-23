from pathlib import Path
import os
import json

import matching.utilities as utl

def main():
    sim_measure = "maximum"
    sd_threshold = 1.5
    matching = "max"

    pairs = utl.get_article_pairs()
    if not os.path.isdir("results/alignment"):
        os.makedirs("results/alignment")

    alignment = {}
    for matching_simple, matching_normal in pairs:
        simple_file = matching_simple.split("/")[-1]
        normal_file = matching_normal.split("/")[-1]
        name = utl.make_matching_path(simple_file, normal_file, sim_measure, matching, sd_threshold)
        easy_lines = []
        normal_lines= []
        with open(name) as fp:
            matches = json.load(fp)
            for match in matches:
                i_normal = match[0][1]
                sentence_pair = match[1]
                dist = match[2]
                easy_lines.append(sentence_pair[0])
                normal_lines.append(sentence_pair[1])
                if not normal_file in alignment:
                    alignment[normal_file] = {
                        i_normal: [{"sent":sentence_pair, "dist":dist}]
                    }
                elif not i_normal in alignment[normal_file]:
                    alignment[normal_file][i_normal] = [{"sent":sentence_pair, "dist": dist}]
                else:
                    alignment[normal_file][i_normal].append({"sent":sentence_pair, "dist": dist})
        align_simple, align_normal = utl.make_alignment_path(simple_file, normal_file)
        with open(align_simple, "w", encoding="utf-8") as fp_simple, open(align_normal,"w", encoding="utf-8") as fp_normal:
            fp_simple.write("\n".join(easy_lines))
            fp_normal.write("\n".join(normal_lines))
    with open("temp_res.json", "w", encoding="utf-8") as fp:
        json.dump(alignment, fp, indent=4, ensure_ascii=False)
    



if __name__ == "__main__":
    main()
