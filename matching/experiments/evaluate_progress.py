import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
                    if len(file_stats):
                        res_dict[v1][v2]["Precision"].append(np.mean(file_stats))
                    else:
                        res_dict[v1][v2]["Precision"].append(0.0)
                    print("Recall:", np.sum(file_stats) / float(all_positive))
                    res_dict[v1][v2]["Recall"].append(np.sum(file_stats) / float(all_positive))

    perf = pd.DataFrame(columns=["similarity_measure", "matching_strategy", "precision", "recall", "f1"])

    for elem in res_dict:
        for elem2 in res_dict[elem]:
            print(elem, elem2)
            prec = np.mean(res_dict[elem][elem2]["Precision"])
            rec = np.mean(res_dict[elem][elem2]["Recall"])
            f1 = 2 * (prec * rec) / (prec + rec)
            print("Average precision:", prec)
            print("Average recall:", rec)
            print("F1 score:", f1)
            elem2_short = ""
            if elem2 == "max_increasing_subsequence": elem2_short = "*"
            perf = perf.append({"similarity_measure": elem, "matching_strategy": elem2_short,
                                "precision": prec, "recall": rec, "f1": f1}, ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 10))

    perf.plot.scatter('precision', 'recall', c='f1', s=100, cmap='plasma', fig=fig, ax=ax, edgecolor='k')
    fig.get_axes()[1].set_ylabel('f1')
    for idx, row in perf.iterrows():
        ax.annotate(row['similarity_measure'] + row['matching_strategy'], row[['precision', 'recall']], fontsize=18, xytext=(10, -5),
                    textcoords='offset points')
    plt.show()


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
