#!/usr/bin/python
#  -*- coding: utf-8 -*-

import nltk
import re, string
from nltk.corpus import stopwords
import ner_similarity
stop_words= [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'himself', u'she', u'her', u'hers', u'herself', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'up', u'down', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now',",","!","?","/","\\"]

numbers = ["half","quarter","one","two","three","four","five","six","seven","eight","nine","ten","hundred","hundreds","thousand","thousands","million","millions","billion","billions"]
currency = ["dollar","dollars","pound","pounds","gbp","cent","cents","dime","dimes","penny","rupee","dinar","cost","costs","price","shillings","shilling"]
date_words=["monday","tuesday","wednesday","thursday","friday","saturday","sunday","yesterday","today","tomorrow","january","february","march","april","may","june","july","august","september","october","november","december", "year","years","month","months","decade","decades","century","week","fortnight"]
reason_words=["because","since","meant","cause","reason"]


def filter(question,sentence,qtype):
    # sentence = re.sub("['!,\"\'`]"," ",sentence)
    words_1 = [i.lower() for i in nltk.word_tokenize(question)]
    sentence = " ".join([i for i in nltk.word_tokenize(sentence) if i.lower() not in words_1 ])


    if "DESC".lower() in qtype.lower():
        return sentence
    sentence = re.sub('[%s]' % '\\!\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\-\\.\\/\\:\\;\\<\\=\\>\\?\\@\\[\\\\\\]\\^\\_\\`\\{\\|\\}\\~', ' ', sentence)
    # print(sentence)
    words =  [ w for w in nltk.word_tokenize(sentence) if w.lower() not in stop_words]
    nums = re.compile(r"[+-]?\d+(?:[\,\.]\d+)?(?:[eE][+-]?\d+)?")
    if "NUM:money".lower() in qtype.lower() or "NUM:cost".lower() in qtype.lower():
        money = re.compile('|'.join([
              r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
              r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
              r'^\$(\d+\.?)$',         # e.g., $5.
            ]))
        positions = [i.start(0) for i in re.finditer(money,sentence)]
        answer=""
        if len(positions) > 0:
            answer= " ".join([ " ".join(sentence[p:].split(" ")[:2]) for p in positions])
            for w in words:
                if (w in currency or w in numbers) and w not in answer:
                    answer = answer + " " + w
            return answer


    elif "NUM".lower() in qtype.lower() and "NUM:date".lower() not in qtype.lower():
        positions = [i.start(0) for i in re.finditer(nums,sentence)]
        answer=""
        if len(positions) > 0:
            answer= " ".join([ " ".join(sentence[p:].split(" ")[:2]) for p in positions])
            for w in words:
                if (w in numbers or w in date_words) and w not in answer:
                    answer = answer + " " + w
            return answer
    #
    if "HUM:ind".lower() in qtype.lower() :
        answer = ner_similarity.extract_entities(sentence)
        if len(answer.keys())>0:
            return " ".join(answer.keys())


    if "LOC:".lower() in qtype.lower() and "LOC:other".lower() not in qtype.lower():
        answer = ner_similarity.extract_entities(sentence)
        location_entities = {k: v for k, v in answer.iteritems() if v == "LOCATION" or v=="GPE"}
        if len(location_entities.keys())>0:
            return " ".join(answer.keys())

    if "loc:other" in qtype.lower():
        location_prep = re.compile('|'.join([
            r'in ',
            r'outside ',
            r'on ',
            r'between ',
            r'at ',
            r'beside ',
            r'by ',
            r'beyond ',
            r'near ',
            r'in front of ',
            r'nearby ',
            r'in back of ',
            r'above ',
            r'behind ',
            r'below ',
            r'next to ',
            r'over ',
            r'on top of ',
            r'under ',
            r'within ',
            r'up ',
            r'beneath ',
            r'down ',
            r'underneath ',
            r'around ',
            r'among ',
            r'through ',
            r'along ',
            r'inside ',
            r'against '
            ]))
        positions = [i.start(0) for i in re.finditer(location_prep,sentence)]
        answer=""
        if len(positions) > 0:
            answer= sentence[positions[0]:]
            return answer

    return " ".join(words)




if __name__=="__main__":
    print filter('`"This has nothing to do with legalizing marijuana," he said.''', "HUM:ind")
    print filter("It is a Good day 12,000 dollar square", "NUM:money")