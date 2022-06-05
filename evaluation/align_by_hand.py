import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askinteger
import os
import json
import spacy
import re
import pickle
import math
import random
import platform
from pathlib import Path

import matching.utilities as utl
from matching.defaultvalues import *

SHORT = "vt" # None

class gui:
    def __init__(self, root):
        self.root = root
        self.mainframe = ttk.Frame(root, padding="5")
        self.mainframe.grid(column=0, row=0, sticky="NEWS")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Canvas
        self.canvas = tk.Canvas(self.mainframe, height=720, width=1280)
        self.canvas.grid(column=0, row=0, sticky="NEWS")
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.mainframe, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(column=1, row=0, sticky="NS")

        # configure scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.update_canvas_layout)

        # MouseWheel action
        self.root.bind_all("<MouseWheel>", self.on_mousewheel)
        self.root.bind_all("<Button-4>", self.on_mousewheel)
        self.root.bind_all("<Button-5>", self.on_mousewheel)

        # configure innerframe
        self.innerframe = ttk.Frame(self.canvas, padding="5")
        self.innerframe.grid(column=0, row=0, sticky="NEWS")
        self.canvas.create_window(0, 0, anchor="nw", window=self.innerframe)
        self.canvas.columnconfigure(0, weight=1)
        self.canvas.rowconfigure(0, weight=1)
        self.innerframe.columnconfigure(0, weight=1)
        self.innerframe.columnconfigure(1, weight=1)
        self.innerframe.columnconfigure(2, weight=1)

        self.normal_radio = self.easy_check = []
        self.match_generator = self.get_articles()
        self.pairs = utl.get_article_pairs()

        self.button_progress = tk.Button(
            self.mainframe, text="Show progress", command=self.show_progress)
        self.button_progress.grid(column=0, row=1, sticky="sw")

        self.button_proceed = tk.Button(
            self.mainframe, text="Only proceed", command=self.next_website)
        self.button_proceed.grid(column=0, row=1, sticky="s")

        self.button_save = tk.Button(
            self.mainframe, text="Save and proceed", command=self.save)
        self.button_save.grid(column=0, row=1, sticky="e")
        self.next_website()

    def update_canvas_layout(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        wraplength = int(event.width/2-50)
        for label in self.easy_labels:
            label.configure(wraplength=wraplength)
        for radio in self.normal_radio:
            radio.configure(wraplength=wraplength)

    def on_mousewheel(self, event):
        delta = 1

        # make mousewheel work in macOS
        if platform.system() == "Darwin":
            self.canvas.yview_scroll(-1 * event.delta, "units")
        else:
            if event.num == 5:
                # scroll down
                self.canvas.yview_scroll(delta, "units")
            elif event.num == 4:
                # scroll up
                self.canvas.yview_scroll(-delta, "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def get_articles(self):
        path = "results/website_samples.pkl"
        if os.path.exists(path):
            print(f"Using presampled sites from {path}")
            # load existing subset
            with open(path, "rb") as fp:
                self.pairs_sample = pickle.load(fp)
        else:
            # sample new 5% subset
            with open(path, "wb") as fp:
                k = math.ceil(len(self.pairs)*0.05)

                # remove already aligned ones
                pairs = [pair for pair in self.pairs if (not os.path.exists(
                    utl.make_hand_aligned_path(pair[0], pair[1])[0]))]
                # relative path instead of absolute
                pairs = [(Path(pair[0]).relative_to(dataset_location), Path(pair[1]).relative_to(dataset_location)) for pair in pairs]

                self.pairs_sample = random.sample(pairs, k)
                pickle.dump(self.pairs_sample, fp)

        for pair in self.pairs_sample:
            if not os.path.exists(utl.make_hand_aligned_path(pair[0], pair[1])[0]):
                yield pair

    def show_progress(self):
        n_aligned = int(len(os.listdir("results/hand_aligned"))/2)
        n_sample = len(self.pairs_sample)
        print(f"{n_aligned}/{n_sample} already aligned.")

    def next_website(self):
        try:
            simple_path, normal_path = next(self.match_generator)
        except StopIteration:
            quit()

        # Paths from match_generator are relative to dataset_location
        simple_path = os.path.join(dataset_location, simple_path)
        normal_path = os.path.join(dataset_location, normal_path)

        print(f"New simple file: {os.path.split(simple_path)[1]}")
        print(f"New standard file: {os.path.split(normal_path)[1]}")

        self.alignment = {}

        self.save_path_easy, self.save_path_normal = utl.make_hand_aligned_path(
            simple_path, normal_path, short=SHORT)

        # delete old contents
        for child in self.innerframe.winfo_children():
            child.destroy()

        # setup new boxes
        wraplength = 600
        with open(simple_path) as fp:
            self.easy_check = []
            self.easy_check_bool = []
            self.easy_labels = []

            # Add easy lines
            self.easy_lines = prep_text(fp.read())
            for i, line in enumerate(self.easy_lines):
                value = tk.BooleanVar(value=False)
                check = ttk.Checkbutton(
                    self.innerframe, text="", variable=value, command=self.pair_to_normal)
                check.grid(column=1, row=i, sticky="NEWS")
                label = ttk.Label(self.innerframe, text=line,
                                  wraplength=wraplength, justify="left")
                label.grid(column=2, row=i, sticky="NEWS")
                self.easy_check_bool.append(value)
                self.easy_check.append(check)
                self.easy_labels.append(label)

        with open(normal_path) as fp:
            self.normal_sentence = tk.StringVar()
            self.normal_radio = []
            self.normal_lines = prep_text(fp.read())

            # Add normal lines
            for i, line in enumerate(self.normal_lines):
                radio = tk.Radiobutton(self.innerframe, text=line, variable=self.normal_sentence,
                                       value=line, command=self.show_paired_easy, wraplength=wraplength, justify="left")
                radio.grid(column=0, row=i, sticky="W")
                self.normal_radio.append(radio)
                self.alignment[line] = []
            # set default to first sentence
            self.normal_sentence.set(self.normal_lines[0])

        # print(self.innerframe.winfo_children())
        # for child in self.innerframe.winfo_children():
        #     child.grid_configure(padx=5,pady=5)

    def pair_to_normal(self):
        normal_sentence = self.normal_sentence.get()
        self.alignment[normal_sentence] = []
        for i, line in enumerate(self.easy_lines):
            if self.easy_check_bool[i].get() and self.easy_check[i].instate(["!disabled"]):
                self.alignment[normal_sentence].append(line)

    def show_paired_easy(self):
        normal_sentence = self.normal_sentence.get()
        for i, easy_line in enumerate(self.easy_lines):
            if easy_line in self.alignment[normal_sentence]:
                self.easy_check[i].state(["!disabled"])
            elif self.easy_check_bool[i].get():
                self.easy_check[i].state(["disabled"])

    def save(self):
        with open(self.save_path_easy, "w", encoding="utf-8") as fp_easy, open(self.save_path_normal, "w", encoding="utf-8") as fp_normal:
            for normal in self.alignment:
                for easy in self.alignment[normal]:
                    if not easy.endswith("\n"):
                        easy += "\n"
                    if not normal.endswith("\n"):
                        normal += "\n"
                    fp_easy.write(easy)
                    fp_normal.write(normal)
        self.next_website()

    def quit(self):
        self.root.destroy()


def prep_text(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    sents = [str(sent) for sent in nlp(text).sents]
    return sents


def choose_website():
    set_aligned = set([file[:-8]
                      for file in os.listdir("results/hand_aligned")])
    global website_hashes

    for website in website_hashes:
        set_website = set(website_hashes[website])
        print(f"{website}: {len(set_aligned & set_website)}")

    string = "\n".join(["0: all websites [Default]"] +
                       [f"{i + 1}: {website}" for i, website in enumerate(website_hashes)])
    website_selection = askinteger(
        "Choose website", string, minvalue=0, maxvalue=len(website_hashes), initialvalue=0)

    return website_selection


website_hashes = utl.get_website_hashes()
nlp = spacy.load("de_core_news_lg")

if __name__ == "__main__":
    if not os.path.isdir("results/hand_aligned/"):
        os.makedirs("results/hand_aligned/")
    root = tk.Tk()
    # root.geometry("1280x720")
    gui(root)
    root.mainloop()
