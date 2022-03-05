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

    res_dict = dict()

    for comb in results:
        all_positive = 0
        with open("results/evaluated/" + comb + ".results", 'r') as fp:
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
                    _, v1, v2, _ = file.split('---')
                    if v1 not in res_dict:
                        res_dict[v1] = dict()
                    if v2 not in res_dict[v1]:
                        res_dict[v1][v2] = {"Precision": [], "Recall": []}
                    with open(os.path.join(root, file), 'r') as fp:
                        file_res = json.load(fp)
                    file_stats = []
                    for _, (s1, s2), _ in file_res:
                        val = res[str(s1)][str(s2)]
                        if val != None:
                            file_stats.append(val)

                    print(file_stats)
                    print("Precision:", np.mean(file_stats))
                    res_dict[v1][v2]["Precision"] = np.mean(file_stats)
                    print("Recall:", np.sum(file_stats) / float(all_positive))
                    res_dict[v1][v2]["Recall"] = np.sum(file_stats) / float(all_positive)

    for elem in res_dict:
        for elem2 in res_dict[elem]:
            print(elem, elem2)
            print("Average precision:", np.mean(res_dict[elem][elem2]["Precision"]))
            print("Average recall:", np.mean(res_dict[elem][elem2]["Recall"]))


def get_matches():
    results_done = set()
    results_started = set()
    for comb in file_matchings:
        if os.path.exists(os.path.join("results/evaluated", comb + ".results")):
            with open("results/evaluated/" + comb + ".results", 'r') as fp:
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
