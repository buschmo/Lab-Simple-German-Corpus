import json
import os
import sys

import numpy as np

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

import pandas as pd

stat_file = pd.DataFrame(columns=["Similarity measure", "Alignment strategy", "sd-Threshold", "Avg. number of matches", "Avg. similarity of matches"])

for root, dirs, files in os.walk("results/matched"):
    for file in files:
        if not file.endswith(".matches"):
            continue

        with open(os.path.join(root, file), 'r') as fp:
            try:
                match_data = json.load(fp)
            except json.decoder.JSONDecodeError:
                continue

        sim, matching, thres = file.split('---')[-3:]
        thres.replace('.matches', '')

        stat_file = stat_file.append({"Similarity measure": sim,
                                      "Alignment strategy": matching,
                                      "sd-Threshold": thres,
                                      "Avg. number of matches": len(match_data),
                                      "Avg. similarity of matches": np.mean([x[2] for x in match_data]) if match_data else 0.0},
                                     ignore_index=True)

sim_stat = stat_file.groupby(["Similarity measure"]).mean().round({'Avg. number of matches':1, 'Avg. similarity of matches':2})
match_stat = stat_file.groupby(["Alignment strategy"]).mean().round({'Avg. number of matches':1, 'Avg. similarity of matches':2})
thres_stat = stat_file.groupby(["sd-Threshold"]).mean().round({'Avg. number of matches':1, 'Avg. similarity of matches':2})

print(sim_stat.to_latex(index=False,
                        caption="Match statistics by similarity measure",
                        label="tab:sim-stat"))
print(match_stat.to_latex(index=False,
                          caption="Match statistics by alignment strategy",
                          label="tab:align-stat"))
print(thres_stat.to_latex(index=False,
                          caption="Match statistics by threshold value",
                          label="tab:thres-stat"))

print(sim_stat)
print(match_stat)
print(thres_stat)
