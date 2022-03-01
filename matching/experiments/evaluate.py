import os
import json
from tkinter import *

file_matchings = set()

for root, dirs, files in os.walk("results/matched"):
    for file in files:
        if file.endswith(".matches"):
            filepath = os.path.join(root, file)
            combination = file.split('---')[0]
            file_matchings.add(combination)


def get_matches():
    for comb in file_matchings:
        matches = set()
        for root, dirs, files in os.walk("results/matched"):
            for file in files:
                if file.endswith(".matches") and file.startswith(comb):
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
    with open("results/matched/" + comb + ".results", 'w') as fp:
        json.dump(res, fp, indent=2, ensure_ascii=False)


def load_results(comb):
    try:
        with open("results/matched/" + comb + ".results", 'r') as fp:
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

labelSimpleSentence = Label(textvariable=simpleLabel, wraplength=700, bg='white', font=('helvetica 14'))

labelSimpleSentence.grid(column=0, row=0, columnspan=3)

labelNormalSentence = Label(textvariable=normalLabel, wraplength=700, bg='white', font=('helvetica 14'))

labelNormalSentence.grid(column=0, row=1, columnspan=3)

buttonYes.grid(column=0, row=2)
buttonNo.grid(column=1, row=2)
buttonUndefined.grid(column=2, row=2)

window.mainloop()
