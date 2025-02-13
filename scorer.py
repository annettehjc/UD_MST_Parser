#!/usr/bin/env python3
import numpy as np
from collections import Counter
from conllu import read_conllu


class BaselineScorer:
    """A simple baseline scoring class.

    train() method keeps two counters: one for childpos-headpos pairs,
    and another for childpos-deprel.

    score() returns the product of relevant counts for a given arc.
    """

    def __init__(self):
        self.deplabels = None
        self.heads = None
        pass

    def train(self, train_conllu, dev_conllu=None):
        self.deplabels = Counter()
        self.heads = Counter()
        for sent in read_conllu(train_conllu):
            for token in sent[1:]:
                self.deplabels[(token.upos, token.deprel)] += 1
                self.heads[(token.upos, sent[token.head].upos)] += 1

    def score(self, sent, i, j, deprel):
        if self.deplabels is None or self.heads is None:
            raise Exception("The model is not trained.")
        headpos, childpos = sent[i].upos, sent[j].upos
        return self.deplabels[(childpos, deprel)] \
            * self.heads[(childpos, headpos)]


class Scorer:
    # Assignment part 3: implement a better scorer below
    # You should keep the same interface: train() updates all
    # necessary information needed from the scoring, and score()
    # returns a score that is higher for high-probability edges.
    # You can implement any method you see fit. See the assignment
    # description for the requirements and some ideas that may help
    # implementing a simple scorer better than the baseline provided
    # above.
    def __init__(self):
        """
        Initialize the scorer.
        """
        self.deplabels = None  # (token.upos, token.deprel)
        self.heads = None  # (sent[token.head].upos, token.upos)
        self.pos_arc = None  # (head.upos, child.upos, deprel)
        self.lemmas = None  # (head.lemma, child.lemma)
        self.deprel_features = None  # deprel: (head_features, child_features)

    def train(self, train_conllu, dev_conllu=None):
        """
        Train the scorer on a training set.
        Arguments:
            train_conllu: training conllu file.
            dev_conllu: dev conllu file.
        """
        self.deplabels = Counter()
        self.heads = Counter()
        self.pos_arc = Counter()
        self.lemmas = Counter()
        self.deprel_features = dict()

        for sent in read_conllu(train_conllu):
            for token in sent[1:]:
                # Count frequencies of a double (token.upos, token.deprel)
                self.deplabels[(token.upos, token.deprel)] += 1

                # Count frequencies of a double (sent[token.head].upos, token.upos)
                self.heads[(sent[token.head].upos, token.upos)] += 1

                # Count frequencies of a triple (head.upos, child.upos, deprel)
                self.pos_arc[(sent[token.head].upos, token.upos, token.deprel)] += 1

                # Count frequencies of a tuple (head.lemma, child.lemma)
                self.lemmas[(sent[token.head].lemma, token.lemma)] += 1

                # Count frequency of each individual feature of child and parent given a deprel

                # If we encounter a new deprel we create a new slot in the dictionary for it's counters
                if token.deprel not in self.deprel_features.keys():
                    self.deprel_features[token.deprel] = (Counter(), Counter())

                # Count feature for head or child if it was found with the given deprel
                if sent[token.head].feat is not None:
                    for feat in sent[token.head].feat.split('|'):
                        self.deprel_features[token.deprel][0][feat] += 1
                if token.feat is not None:
                    for feat in token.feat.split('|'):
                        self.deprel_features[token.deprel][1][feat] += 1

    def score(self, sent, i, j, deprel):
        """
        Produce a score based on relevant features.
        Arguments:
            sent: a list of tokens
            i: the index of the head
            j: the index of the child
            deprel: deprel label
        Returns:
            score: the score of the sentence based on the dependency distance, pos tags, and lemmas
        """

        if self.pos_arc is None:
            raise Exception("The model is not trained.")

        # Get frequencies and other features
        deplabels = self.deplabels[(sent[i].upos, deprel)]

        heads = self.heads[(sent[i].upos, sent[j].upos)]

        dependency_dist = 0 if j - i == 0 else 1 / abs(j - i)  # closer elements get a higher score

        pos_arc = self.pos_arc[(sent[i].upos, sent[j].upos, deprel)]

        lemmas = self.lemmas[(sent[i].lemma, sent[j].lemma)]


        # get string of features or lack there of
        head_features = sent[i].feat if sent[i].feat is not None else ''
        child_features = sent[j].feat if sent[j].feat is not None else ''

        # Get scores of the features given the deprel
        head_feat, child_feat = 0, 0
        if deprel in self.deprel_features.keys():
            if sent[i].feat is not None:
                head_feat = sum(self.deprel_features[deprel][0][feat] for feat in head_features.split('|'))
            if sent[j].feat is not None:
                child_feat = sum(self.deprel_features[deprel][1][feat] for feat in child_features.split('|'))

        features_vector = [
            deplabels,
            heads,
            dependency_dist,
            pos_arc,
            lemmas,
            head_feat,
            child_feat,
        ]

        # Manually tuned weights - record of our experiments is in the file weights_record.txt
        weight_vector = [
            0.005,  # deplabels
            0.01,  # heads
            3.5,  # dependency_dist
            4.5,  # pos_arc
            0.001,  # lemmas
            0.000075,  # head_feat
            0.0001,  # child_feat
        ]

        return np.dot(features_vector, weight_vector)
