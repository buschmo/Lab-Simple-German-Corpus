import os
import json
import numpy as np

file_matchings = set()

for root, dirs, files in os.walk("results/matched"):
    for file in files:
        if file.endswith(".matches"):
            filepath = os.path.join(root, file)
            combination = file.split('---')[0]
            file_matchings.add(combination)


def get_results_done(results):
    for comb in results:
        all_positive = 0
        with open("results/matched/" + comb + ".results", 'r') as fp:
            res = json.load(fp)
        for elem in res:
            if elem != "finished":
                for e in res[elem]:
                    if res[elem][e]:
                        all_positive += 1

        for root, dirs, files in os.walk("results/matched"):
            for file in files:
                if file.startswith(comb) and file.endswith("1.5.matches"):
                    print("\t".join(file.split('---')[1:]))
                    with open(os.path.join(root, file), 'r') as fp:
                        file_res = json.load(fp)
                    file_stats = []
                    for _, (s1, s2), _ in file_res:
                        val = res[str(s1)][str(s2)]
                        if val != None:
                            file_stats.append(val)

                    print(file_stats)
                    print("Precision:", np.mean(file_stats))
                    print("Recall:", np.sum(file_stats) / float(all_positive))


def get_matches():
    results_done = set()
    results_started = set()
    for comb in file_matchings:
        if os.path.exists(os.path.join("results/matched", comb + ".results")):
            with open("results/matched/" + comb + ".results", 'r') as fp:
                res = json.load(fp)

            if "finished" in res:
                results_done.add(comb)
            else:
                results_started.add(comb)

    print("RESULTS FINISHED:", len(results_done))
    print("RESULTS STARTED: ", len(results_started))

    get_results_done(results_done)


if __name__ == '__main__':
    get_matches()
