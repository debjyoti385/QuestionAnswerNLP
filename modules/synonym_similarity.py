#!/usr/bin/python
#  -*- coding: utf-8 -*-

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn

stop = set([u'|',u"?", u",", u"=",u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now',  u"a", u"about", u"above", u"after", u"again", u"against", u"all", u"am", u"an", u"and", u"any", u"are", u"aren't", u"as", u"at", u"be", u"because", u"been", u"before", u"being", u"below", u"between", u"both", u"but", u"by", u"can't", u"cannot", u"could", u"couldn't", u"did", u"didn't", u"do", u"does", u"doesn't", u"doing", u"don't", u"down", u"during", u"each", u"few", u"for", u"from", u"further", u"had", u"hadn't", u"has", u"hasn't", u"have", u"haven't", u"having", u"he", u"he'd", u"he'll", u"he's", u"her", u"here", u"here's", u"hers", u"herself", u"him", u"himself", u"his", u"how", u"how's", u"i", u"i'd", u"i'll", u"i'm", u"i've", u"if", u"in", u"into", u"is", u"isn't", u"it", u"it's", u"its", u"itself", u"let's", u"me", u"more", u"most", u"mustn't", u"my", u"myself", u"no", u"nor", u"not", u"of", u"off", u"on", u"once", u"only", u"or", u"other", u"ought", u"our", u"ours    ourselves", u"out", u"over", u"own", u"same", u"shan't", u"she", u"she'd", u"she'll", u"she's", u"should", u"shouldn't", u"so", u"some", u"such", u"than", u"that", u"that's", u"the", u"their", u"theirs", u"them", u"themselves", u"then", u"there", u"there's", u"these", u"they", u"they'd", u"they'll", u"they're", u"they've", u"this", u"those", u"through", u"to", u"too", u"under", u"until", u"up", u"very", u"was", u"wasn't", u"we", u"we'd", u"we'll", u"we're", u"we've", u"were", u"weren't", u"what", u"what's", u"when", u"when's", u"where", u"where's", u"which", u"while", u"who", u"who's", u"whom", u"why", u"why's", u"with", u"won't", u"would", u"wouldn't", u"you", u"you'd", u"you'll", u"you're", u"you've", u"your", u"yours", u"yourself", u"yourselves"])

def similarityScore(sentence_1,sentence_2):
    """
    finds synonyms of each words in both sentences and relate them to look-up for similarity
    """
    words_1 = [i.lower() for i in nltk.word_tokenize(sentence_1) if i.lower() not in stop ]
    words_2 = [i.lower() for i in nltk.word_tokenize(sentence_2) if i.lower() not in stop ]
    if len(words_1) == 0 or len(words_2) == 0:
        return 0.0

    # print words_1
    # print words_2
    synonym_1=[]
    for word in  words_1:
        for sysset in wn.synsets(word):
            synonym_1.extend(sysset.lemma_names())
    synonym_1 = [i.lower() for i in set(synonym_1) if i.lower() not in words_1]
    synonym_2=[]
    for word in  words_2:
        for sysset in wn.synsets(word):
            synonym_2.extend(sysset.lemma_names())
    synonym_2 = [i.lower() for i in set(synonym_2) if i.lower() not in words_2]

    # print synonym_1
    # print synonym_2
    # print set(synonym_1).intersection(set(synonym_2))
    score =0.0
    for w1 in words_1:
        if w1 in words_2:
            score+= 1.0/(len(words_1) * len(words_2))
        elif w1 in synonym_2:
            score+= 1.0/((len(synonym_1)+1)* (len(words_1)+1))

    for s1 in synonym_1:
        for s2 in synonym_2:
            if s1 == s2:
                score += 1.0/((len(synonym_1)+1)*(len(synonym_2) + 1)* len(words_1))

    return (1+score*10)

if __name__=="__main__":
    print similarityScore("It is a good day", "it is you my dear")