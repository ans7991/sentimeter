# -*- coding: utf-8 -*-
import en
import nltk
from bigram_handler import BigramHandler
from nltk.corpus import stopwords

__author__ = 'pankajs'

#TODO: replace bigrams containing not and other negetive words with antonyms before executing

class DataCleaner:
    def execute(self, text):
        bigram = BigramHandler()
        tokens = bigram.reduce(text.replace('#', 'hash'))
        tokens = self.remove_stop_words(tokens)
        tokens = self.remove_punctuations(tokens)
        tokens = filter(self.is_a_expression, tokens)
        return map(lambda t: t.replace('hash', ''), tokens)

    def remove_stop_words(self, tokens):
        stop = stopwords.words('english')
        return filter(lambda word: word.encode('utf-8') not in stop, tokens)

    def remove_punctuations(self, tokens):
        return filter(lambda word: word.isalpha(), tokens)

    def is_negation(self, word):
        return word.startswith('not')

    def is_a_hash_tag(self, word):
        return word.startswith('hash')

    def is_a_expression(self, word):
        return self.is_a_hash_tag(word)\
               or self.is_negation(word) \
               or en.is_noun(word) \
               or en.is_adjective(word) \
               or en.is_verb(word) \
               or en.is_adverb(word) \
               or self.is_orality(word)

    def is_orality(self, word):
        summary = en.content.categorise(word)
        for category in summary:
            if category.name == 'orality':
                return True