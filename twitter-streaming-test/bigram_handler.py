# -*- coding: utf-8 -*-
import nltk
from nltk.collocations import *
#from nltk.corpus import wordnet as wn

__author__ = 'pankajs'

class BigramHandler:
    def identify(self, tokens):
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(tokens)
        scored = finder.score_ngrams(bigram_measures.raw_freq)
        return sorted(bigram for bigram, score in scored)

    def negetive_bigrams(self, bigrams):
        return filter(lambda pair: pair[0] in ['no', 'not', 'hardly', 'scarcely'], bigrams)

    def replace_negation(self, text, negative):
        for pair in negative:
            text = text.replace(' '.join(pair), ''.join(pair))
        return nltk.wordpunct_tokenize(text)

    def reduce(self, text):
        tokens = nltk.wordpunct_tokenize(text.lower())
        bigrams = self.identify(tokens)
        negative = self.negetive_bigrams(bigrams)
        return self.replace_negation(text.lower(), negative)