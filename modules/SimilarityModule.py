#!/usr/bin/python
#  -*- coding: utf-8 -*-
import nltk
import sentence_similarity
import synonym_similarity
import ner_similarity
import sourceContentSelector

def getScoredSentences(question, articles, qtype):
    sentences = nltk.tokenize.sent_tokenize(articles)
    # print "length of article and ner ", len(sentences), len(ner)
    result=[]
    i=0
    for sentence in sentences:
        score =0
        score, specialFlag = ner_similarity.similarityScore(question,sentence, qtype)
        # print "1st score done ", score
        if score > 0 :
            # print score,
            score *= synonym_similarity.similarityScore(question,sentence)
        # print "2nd score done ", score
        # print score,
        # if specialFlag == False and score>0:
        #     score *= sentence_similarity.similarityScore(question,sentence,True)
            # score *= sourceContentSelector.score(question,sentence)
        # print score
        result.append((sentence,score))
        i += 1
    # result.sort(key=lambda t:t[1], reverse=True)
    return result
