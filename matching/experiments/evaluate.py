import os
import json
from tkinter import *
from tkinter.simpledialog import askinteger

file_matchings = set()

print(os.environ.get("USERNAME"))

if not os.path.isdir("results/evaluated/"):
    os.mkdir("results/evaluated/")

websites = ["www.apotheken-umschau.de",
            "www.behindertenbeauftragter.de",
            "www.brandeins.de",
            "www.lebenshilfe-main-taunus.de",
            "www.mdr.de",
            "www.sozialpolitik.com",
            "www.stadt-koeln.de",
            "www.taz.de",
            "www.unsere-zeitung.at"]
string = "\n".join(["0: all websites [Default]"]+[f"{i+1}: {website}" for i, website in enumerate(websites)])
global file_filter
file_filter = None
website_selection = askinteger("Choose website", string, minvalue=0, maxvalue=len(websites))

# Print out number of already evaluated results per website
website_count = [0 for _ in websites]
set_evaluated = set([file[:-8] for file in os.listdir("results/evaluated")])
for i, website in enumerate(websites):
    with open(f"../../Datasets/{website}/header.json") as fp:
        header = json.load(fp)
        website_keys = header.keys()

    with open("results/header.json") as fp:
        header = json.load(fp)
        set_matched = set()
        for key in header:
            if key[:-4] in website_keys:
                for file in header[key]:
                    set_matched.add(file.split("---")[0].split("/")[-1])
    print(f"{website}: {len(set_evaluated & set_matched)}")

# prepare the filtering per website
if website_selection:
    with open(f"../../Datasets/{websites[website_selection-1]}/header.json") as fp:
        header = json.load(fp)
        website_keys = header.keys()
    with open("results/header.json") as fp:
        header = json.load(fp)
        file_filter = []
        for key in header:
            if key[:-4] in website_keys:
                for file in header[key]:
                    file_filter.append(file.split("/")[-1])

for root, dirs, files in os.walk("results/matched"):
    for file in files:
        if file.endswith(".matches"):
            filepath = os.path.join(root, file)
            combination = file.split('---')[0]
            file_matchings.add(combination)


def get_matches():
    user = os.environ.get("USERNAME")
    all_files = sorted(list(file_matchings), reverse=(user == "malte"))
    for comb in all_files:
        matches = set()
        for root, dirs, files in os.walk("results/matched"):
            for file in files:
                if (not file_filter) or (file in file_filter):
                    if file.endswith("1.5.matches") and file.startswith(comb):
                        with open(os.path.join(root, file), 'r') as fp:
                            doc_matches = json.load(fp)
                            for ind, sentences, sim in doc_matches:
                                sentence_tuple = (sentences[0], sentences[1])
                                matches.add(sentence_tuple)

        for match in matches:
            yield comb, match


window = Tk()

match_generator = get_matches()

simpleLabel = StringVar()
normalLabel = StringVar()

currentComb = ""
currentResults = dict()


def correct():
    if simpleLabel.get() not in currentResults:
        currentResults[simpleLabel.get()] = dict()

    currentResults[simpleLabel.get()][normalLabel.get()] = True

    write_results(currentComb, currentResults)

    update_sentences()


def incorrect():
    if simpleLabel.get() not in currentResults:
        currentResults[simpleLabel.get()] = dict()

    currentResults[simpleLabel.get()][normalLabel.get()] = False

    write_results(currentComb, currentResults)

    update_sentences()


def undefined():
    if simpleLabel.get() not in currentResults:
        currentResults[simpleLabel.get()] = dict()

    currentResults[simpleLabel.get()][normalLabel.get()] = None

    write_results(currentComb, currentResults)

    update_sentences()


buttonYes = Button(text="Similar", command=correct)

buttonNo = Button(text="Not similar", command=incorrect)

buttonUndefined = Button(text="Undefined", command=undefined)


def write_results(comb, res):
    with open("results/evaluated/" + comb + ".results", 'w') as fp:
        json.dump(res, fp, indent=2, ensure_ascii=False)


def load_results(comb):
    try:
        with open("results/evaluated/" + comb + ".results", 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return dict()


def update_sentences():
    global currentComb, currentResults
    try:
        next_elem = next(match_generator)
        nextSimple = next_elem[1][0]
        nextNormal = next_elem[1][1]
        newComb = next_elem[0]
    except StopIteration:
        newComb = "FINISHED"
        nextSimple = "Finished Evaluating All Pairs"
        nextNormal = "No more work to do :)"
        buttonYes['state'] = 'disabled'
        buttonNo['state'] = 'disabled'
        buttonUndefined['state'] = 'disabled'

    if currentComb != newComb:
        if currentComb != "":
            currentResults["finished"] = True
            write_results(currentComb, currentResults)
        currentComb = newComb
        currentResults = load_results(currentComb)

    if "finished" in currentResults:
        update_sentences()
        return

    if str(nextSimple) in currentResults:
        if str(nextNormal) in currentResults[nextSimple]:
            print("Already evaluated!")
            update_sentences()
            return

    simpleLabel.set(nextSimple)
    normalLabel.set(nextNormal)


window.title("Evaluate results of sentence matching")

window.geometry('700x200')

for i in range(3):
    window.columnconfigure(i, weight=1, minsize=75)
    window.rowconfigure(i, weight=1, minsize=50)

update_sentences()

labelSimpleSentence = Label(textvariable=simpleLabel, wraplength=700, bg='white', font=('Helvetica 14'))

labelSimpleSentence.grid(column=0, row=0, columnspan=3)

labelNormalSentence = Label(textvariable=normalLabel, wraplength=700, bg='white', font=('Helvetica 14'))

labelNormalSentence.grid(column=0, row=1, columnspan=3)

buttonYes.grid(column=0, row=2)
buttonNo.grid(column=1, row=2)
buttonUndefined.grid(column=2, row=2)

window.mainloop()
