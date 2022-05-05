# Experiments and Data Analysis

In order for this work to be as scientifically accurate as possible, we need to collect data and conduct experiments. These experiments can roughly be separated into three classes: General data properties, matching data analysis, and matching accuracy

## General data properties
We want to know

- How many of the scraped texts are identical in Simple and standard German
- How many words are in the texts on average?
- How many characters are in the texts on average?
- Can we find other interesting differences between the two kinds of German? (optional)

## Matching data analysis

As it stands, various preprocessing options, six similarity measures and two alignment strategies have been implemented:
#### Preprocessing options
- remove_hyphens: removes hyphens of the form '-[A-Z]' (often found in Simple German) from the text. E.g., Bürger-Meister becomes Bürgermeister
- lowercase: lowercases the text
- remove_gender: removes German gendering endings like \*in, \*innen (with \*, _, : and "Binnen-I" (BäckerInnen))
- lemmatization: lemmatizes the text
- spacy_sentences: should be the standard behavior: Lets spacy determine sentence borders
- remove_stopwords: removes stopwords (very common words) for German as defined internally by spacy
- remove_punctuation: Removes punctuation marks

#### Similarity measures:
- bag of words similarity with TF*IDF weighting
- character n-gram similarity with TF*IDF weighting
- cosine similarity with averaged word embedding vectors
- average similarity with averaged similarities between all pairs of words
- maximal similarity with max matching in both directions and average of the two obtained values
- maximum matching similarity, calculating a maximum matching between the sentences and averaging its similarity
- CWASA similarity, that calculates maximum matchings for each word, does not allow i-j and j-i matchings, and averages the obtained similarity values (see paper for details)
#### Alignment strategies:
- Maximal alignment, that matches each sentence of the Simple sentences to its maximal match in the standard sentences
- Maximal increasing alignment, that works like Maximal alignment, but forces the alignment to keep the order of information

Both alignment strategies allow to introduce a minimum matching threshold, i.e., the minimal similarity value for which we allow matching between sentences. This can be set either as an absolute value or as dependent on mean and standard deviation of the data (i.e., mean + factor*std, where factor can be set by the user) 


### Experiments
Naturally, it would be most accurate to evaluate all combinations of options. As this is at odds with the available computing power and the scope of the paper, we will restrict ourselves to certain promising combinations of the settings, which are yet to be determined.

## Matching accuracy

Our current idea is the following: We will create matchings with different settings and let human users (i.e., ourselves) evaluate the percentage of accurate matchings by looking at a random set of created matchings. This of course can only measure precision, not recall, but since we get a different amount of matched sentences per setting, it might be possible to estimate the number of probably "optimal" matchings. For each measure, we can calculate precision*matches and use this as a lower bound for the actual number of matchings. As there are some liberal settings (e.g. those without a threshold, which are expected to have a low precision but a high recall), this lower bound may (in the optimal case) be quite close to the actual number of potential matching, making it possible to calculate an estimated recall value. 