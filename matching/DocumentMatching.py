import numpy as np
import matching.SimilarityMeasures as measures


# TODO: Add possibility to link original sentences to preprocessed ones!
def match_documents_max(simple_doc, normal_doc, match_matrix, threshold=0.0, sd_threshold=0.0):
    """

    Args:
        simple_doc: The simple document in preprocessed format
        normal_doc: The normal document in preprocessed format
        match_matrix: A matrix with similarity scores for the sentences in the documents
        threshold: Minimum matching threshold, is different for different kinds of matching algorithms.
        sd_threshold: Calculates the mean and standard deviation of all sentence similarities and sets the threshold to mean+(sd_threshold*std)

    Returns:
        A list of matched sentences
    """

    if sd_threshold > 0.0:
        std = np.std(match_matrix)
        mean = np.mean(match_matrix)
        threshold = mean + (sd_threshold * std)

        print(threshold)

    max_values = np.argmax(match_matrix, axis=1)

    return [(simple_doc[i], normal_doc[j]) for i, j in enumerate(max_values) if match_matrix[i, j] > threshold]


def calculate_similarity_matrix(simple_doc, normal_doc, similarity_measure, n=4, tf1=None, tf2=None,
                                idf=None):
    """
    Calculates the matrix of similarity scores for each sentence pairing

    Args:
        simple_doc: A preprocessed document in simple German
        normal_doc: A preprocessed document in normal German
        similarity_measure: A similarity measure from the list of possible similarity measures, can be n_gram, bag_of_words, cosine, average, maximum, max_matching, and CWASA
        threshold: Minimal threshold for matching
        n: needed for n-grams
        tf1: Needed for tfidf similarity measures
        tf2: Needed for tfidf similarity measures
        idf: Needed for tfidf similarity measures

    Returns:
        A len(doc1), len(doc2)-Matrix with similarity scores for both documents
    """
    match_matrix = np.zeros(shape=(len(simple_doc), len(normal_doc)))

    for i, sent1 in enumerate(simple_doc):
        for j, sent2 in enumerate(normal_doc):

            value = 0.0

            if similarity_measure == "n_gram":
                assert tf1 is not None and tf2 is not None and idf is not None
                value = measures.n_gram_similarity(sent1, sent2, tf1, tf2, idf, n)
            elif similarity_measure == "bag_of_words":
                assert tf1 is not None and tf2 is not None and idf is not None
                value = measures.bag_of_words_tf_idf_similarity(sent1, sent2, tf1, tf2, idf)
            elif similarity_measure == "cosine":
                value = measures.cosine_similarity(sent1, sent2)
            elif similarity_measure == "average":
                value = measures.average_similarity(sent1, sent2)
            elif similarity_measure == "maximum":
                value = measures.max_similarity(sent1, sent2)
            elif similarity_measure == "max_matching":
                value = measures.max_matching_similarity(sent1, sent2)
            elif similarity_measure == "CWASA":
                value = measures.CWASA_similarity(sent1, sent2)
            else:
                print(f"Similarity measure {similarity_measure} not known and/or not implemented")

            match_matrix[i, j] = value

    return match_matrix
