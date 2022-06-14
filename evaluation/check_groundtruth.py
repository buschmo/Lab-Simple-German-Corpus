import os
import json
import pickle
import random

from collections import Counter
from defaultvalues import dataset_location

data_samples = "results/website_sample.pkl"
apo_header = os.path.join(dataset_location, "www.apotheken-umschau.de/header.json")

with open(data_samples, "rb") as f:
    samples = pickle.load(f)

print(f"Number of sampled article pairs: {len(samples)}")
print(samples[0])

with open(apo_header, "rb") as f:
    apo = json.load(f)

websites = [str(os.path.split(w[0])[0]).split("/")[-2] for w in samples]

print(Counter(websites))
# we see that there are some sources of which we only evaluate one sample

apo_topics = ["niedriger-blutdruck", "akute-mittelohr", "nasennebenhoehlen", "reizdarm"]

for k, v in apo.items():
    if any(t in k for t in apo_topics):
        print(f">> Simple: {k.replace('__', '/')}")
        print(f">>> Matched: {[entry.replace('__', '/') for entry in v['matching_files']]}")

# when following the URLs we see that the matching is wrong: the links of the rectangular fields at the bottom of
# the article only refer to articles connected to the overall topic (e.g., ears). The matching article
# is instead linked in the last paragraph under "hier".

sample_from = ["www.lebenshilfe-main-taunus.de", "www.sozialpolitik.com", "www.behindertenbeauftragter.de", "www.taz.de"]

new_samples = []
for s in sample_from:
    with open(os.path.join(dataset_location, s, "header.json"), "rb") as f:
        all_entries = json.load(f)
    # get paths of easy articles
    simple_entries = {k: v for k, v in all_entries.items() if v['easy']}

    # sample from all easy articles and keep if new article not in old list of samples
    while True:
        new_key, new_value = random.sample(simple_entries.items(), 1)[0]
        if len(new_value['matching_files']) > 1:
            continue
        if any(k[0] in os.path.split(new_value["url"]) for k in samples):
            continue
        new_samples.append([os.path.join(s, new_key),
                            os.path.join(s, new_value['matching_files'][0])])
        break

print(f"New samples: {new_samples}")

rel_samples = []
for entry in samples:
    # remove all samples from apotheken-umschau
    if "apotheken" in entry[0]:
        continue
    else:
        rel_samples.append([os.path.join(*entry[0].split(os.sep)[-3:]), os.path.join(*entry[1].split(os.sep)[-3:])])

rel_samples += new_samples
print(rel_samples[0])

# with open(os.path.join(os.path.split(data_samples)[0], "better_samples.pkl"), "wb") as f:
#     pickle.dump(rel_samples, f)

with open(os.path.join(os.path.split(data_samples)[0], "better_samples.pkl"), "rb") as fb:
    test_file = pickle.load(fb)

print(f"Output of test_file: {test_file}")