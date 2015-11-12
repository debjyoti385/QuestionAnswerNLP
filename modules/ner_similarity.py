#!/usr/bin/python
#  -*- coding: utf-8 -*-

import nltk
import QuestionClassifier
from nltk.corpus import wordnet as wn
import re
import math
from nltk.stem import PorterStemmer


from nltk.corpus import stopwords
stop_words= stopwords.words("english")
irrelevant_loc_words=["north", "east", "west","south","top","bottom","up","down"]
numbers = ["half","quarter","one","two","three","four","five","six","seven","eight","nine","ten","hundred","hundreds","thousand","thousands","million","millions","billion","billions"]
currency = ["dollar","dollars","pound","pounds","gbp","cent","cents","dime","dimes","penny","rupee","dinar","cost","costs","price","shillings","shilling"]
date_words=["monday","tuesday","wednesday","thursday","friday","saturday","sunday","yesterday","today","tomorrow","january","february","march","april","may","june","july","august","september","october","november","december", "year","years","month","months","decade","decades","century","week","fortnight","night"]
reason_words=["because","since","meant","cause","reason"]

def extract_entities(text):
    result=dict()
    for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text))):
        # chunk.draw()
        if(isinstance(chunk, nltk.tree.Tree)):
            for subtree in chunk.subtrees(filter=lambda t: (t.label() == 'PERSON' or t.label() == 'GPE' or t.label() == 'LOCATION')):
                for leave in subtree.leaves():
                    if leave[0].lower() not in irrelevant_loc_words:
                        result[leave[0].lower()]=subtree.label()
    # print result
    return result



def sigmoid(x):
  return 1 / (1 + math.exp(-0.5*x))

def escore(x):
    return 10**(x)

# def extract_entities(text):
#     return st.tag(text.split())

def similarityScore(sentence_1,sentence_2, qtype):
    words_1 = [i.lower() for i in nltk.word_tokenize(sentence_1) if i not in stop_words ]
    words_2 = [i.lower() for i in nltk.word_tokenize(sentence_2) if i not in stop_words ]

    nums = re.compile(r"[+-]?\d+(?:[\,\.]\d+)?(?:[eE][+-]?\d+)?")
    score=0.0
    flag=False
    specialFlag=False

################## category specific detailing #####################################
    if "NUM:money".lower() in qtype.lower() or "NUM:cost".lower() in qtype.lower() or "cost" in sentence_1 or "money" in sentence_1:
        money = re.compile('|'.join([
              r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
              r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
              r'^\$(\d+\.?)$',         # e.g., $5.
            ]))
        for w2 in words_2:
            w2 = w2.split("-",1)[0]
            w2 = re.sub('[ ]', '', w2)
            val = money.search(w2)
            val1 = nums.search(w2)
            if val != None:
                # print "NUM:money", val.group(0),
                score += 0.25
                flag=True
                specialFlag=True
                break
            elif val1 != None:
                score += 0.05
                flag=True
                specialFlag=True
                break
            if w2.lower() in currency:
                score+=0.25
                flag=True
                specialFlag=True
                break
            if w2.lower() in numbers:
                score+=0.15
                flag=True
                specialFlag=True
                break
    elif "NUM".lower() in qtype.lower() and "NUM:other".lower() not in qtype.lower() and "NUM:date".lower() not in qtype.lower():
        for w2 in words_2:
            w2 = w2.split("-",1)[0]
            w2 = re.sub('[,!.]', '', w2)
            val = nums.search(w2)
            if val != None:
                # if "NUM:count".lower() in qtype.lower() and val.group(0).isdigit() and int(val.group(0)) > 1900 and int(val.group(0)) > 1999: # if value is a year in range 1900,1999 then its a year..
                #     continue
                # print "NUM:", val.group(0),
                score += 0.2
                flag = True
                specialFlag=True
                break
            # elif "NUM:period".lower() in qtype.lower():
            #     if w2 in date_words or w2 in numbers:
            #         score+=0.2
            #         flag = True
            #         break

    elif "NUM:date".lower() in qtype.lower() :
        for w2 in words_2:
            if w2 in date_words:
                score=+0.25
                flag = True
                break
            elif w2.isdigit():
                try:
                    if int(w2) > 1600 and int(w2) < 2100:
                        score += 0.25
                except:
                    pass

    if "LOC".lower() in qtype.lower():
        entities= extract_entities(sentence_2)
        for w2 in words_2:
            if w2.lower() in entities.keys():
                if entities[w2.lower()]=="LOCATION" or entities[w2.lower()]=="GPE":
                    flag=True
                    if "LOC:other".lower() in qtype.lower():
                        score+=0.1
                    else:
                        score+=0.3
                    break

####################
# if NAME's apostophy relation .. NAME should not be counted for similarity measure
# to do
####################
    eliminate_entities = dict()
    if "'s" in sentence_1.lower() :
        eliminate_entities = extract_entities(sentence_1)
        eliminate_entities = {k: v for k, v in eliminate_entities.iteritems() if v == "PERSON"}

    # print eliminate_entities

    if sentence_1.lower().strip(" ").startswith("who") and ("HUM:ind".lower() in qtype.lower() or "HUM:desc".lower() in qtype.lower()):
        entities= extract_entities(sentence_2)
        for w2 in words_2:
            if w2.lower() in entities.keys():
                if entities[w2.lower()]=="PERSON" and w2.lower() not in eliminate_entities.keys():
                    # print w2.lower()
                    flag=True
                    if len(eliminate_entities)> 0:
                        specialFlag=True
                    score+=0.3
                    break

    if "DESC:reason".lower() in qtype.lower():
        reasons = re.compile("to (see|do|visit)")
        if reasons.search(sentence_2) != None:
                score +=0.08
                specialFlag=True
                flag=True
        for w2 in words_2:
            if w2 in reason_words:
                score +=0.2
                specialFlag=True
                flag=True
                break

    w1_synsets=[]
    w1_hypersets=[]
    w2_synsets=[]
    w2_hypersets=[]

    for w2 in words_2:
        w2_synsets.extend(wn.synsets(w2))
    for w1 in words_1:
        w1_synsets.extend(wn.synsets(w1))

    for ss in w1_synsets:
        w1_hypersets.extend(ss.hypernyms())
    for ss in w2_synsets:
        w2_hypersets.extend(ss.hypernyms())

    w1_synsets = set([ w1.name().split(".")[0] for w1 in w1_synsets])
    w2_synsets = set([ w2.name().split(".")[0] for w2 in w2_synsets])
    w1_hypersets = set([ w1.name().split(".")[0] for w1 in w1_hypersets if w1.name().split(".")[0] not in w1_synsets])
    w2_hypersets = set([ w2.name().split(".")[0] for w2 in w2_hypersets if w2.name().split(".")[0] not in w2_synsets])
    # w2_hypersets = list(w2_hypersets).extend(w2_synsets)

    # print w1_synsets
    # print w1_hypersets
    # print w2_synsets
    # print w2_hypersets

    # for w1 in words_1:
    #     for w2 in words_2:
    #         if w1 ==  w2 and w1 not in ["!",",",".","-","(",")","\\","/"]:
    #             # print w1, w2,
    #             # print sentence_2
    #             flag= True
    #             if nums.search(w1) !=None:
    #                 # print w1
    #                 score += 3.0/((len(words_2)+1) * (len(words_1)+1))
    #             else:
    #                 score += 0.08/((len(words_2)+1) * (len(words_1)+1))
    #             if specialFlag == True:
    #                     break

    for w1ss in w1_synsets:
        for w2ss in w2_synsets:
            if w1ss ==  w2ss:
                # print w1ss, w2ss,
                # print sentence_2
                flag= True
                score += 2.0/((len(w1_synsets)+1) * (len(w2_synsets)+1))
                if specialFlag == True:
                        break
        # if specialFlag == True:
        #                 break

    for w1ss in w1_hypersets:
        for w2ss in w2_hypersets:
            if w1ss ==  w2ss:
                # print w1ss, w2ss,
                # print sentence_2
                flag= True
                score += 0.5/((len(w1_hypersets)+1) * (len(w2_hypersets)+1))
                if specialFlag == True:
                        break
        if specialFlag == True:
                        break


############ search for question related synsets in sentence ##################################
    qtype_synsets= QuestionClassifier.liroth_to_wordnet(qtype)
    if qtype_synsets != None:
        qtype_synsets_names=set([ q.name().split(".")[0] for q in qtype_synsets ])
        # print qtype_synsets_names
        for w2ss in w2_hypersets:
            for q in qtype_synsets_names:
                if w2ss == q:
                    # print w2ss,q,
                    flag=True
                    score += 3.0/((len(qtype_synsets_names)+1) * (len(w2_hypersets)+1))




    if flag == False:
        score-=0.2
    if "what" in sentence_1:
        score =score/2.0
    if "what" in sentence_1.lower() and  ("known as" in sentence_2.lower() or "called as" in sentence_2.lower() or "named as" in sentence_2.lower()):
        score =score *2.0 + 0.2
    if specialFlag==True:
        score*=1.1
    # if score > 0:
        # print "  --- " , score, sentence_2,
    return score, specialFlag


if __name__=="__main__":
    # print similarityScore("Where is South Queens Junior High School located?","South Queens Junior High School is taking aim at the fitness market.","LOC:other")
    # print similarityScore("Where is South Queens Junior High School located?","A middle school in Liverpool, Nova Scotia is pumping up bodies as well as minds","LOC:other")
    print similarityScore("Who is the principal of South Queens Junior High School?","South Queens Junior High School is, taking aim at the fitness market.","HUM:DESC")
    print similarityScore("Who is the principal of South Queens Junior High School?","Principal Betty Jean Aucoin says the, club is a first for a Nova Scotia public school.","HUM:DESC")
    # print similarityScore("Why did Babe stop playing basketball?","Babe Belanger married Ian MacLean, who continued the family sports tradition.","DESC:reason")
    # print extract_entities(" South Queens Junior High School is taking aim at the fitness market")
    # print extract_entities(" A middle school in Liverpool, Nova Scotia is pumping up bodies as well as minds")
    # print similarityScore("who is Merry Hilbert's husband", "Merry Hilbert is a famous person","HUM:ind")
    # print similarityScore("who is Merry Hilbert's husband", "her husband is a Jerry Burhaer","HUM:ind")
    print similarityScore("When did Calgary, Alberta receive not a single snowflake?","When a sun tanned movie making team flew up to Calgary, Alberta, from Hollywood, California to film the movie \"Snow Day\", they thought the least they could expect from the Great White North was a little snow.","NUM:date")
    print similarityScore("How many cases of measles were there in 1995 in Canada?","Last , year Canada had only cases of measles, down from about in.","NUM:count")

    # print extract_entities("Wiarton Willie, the famous Canadian groundhog who predicted the arrival of spring")
    # print similarityScore("Where did Willie live?","Wiarton Willie, the famous Canadian groundhog who predicted the arrival of spring","LOC:other")
    # print similarityScore("Where did Willie live?","But Willie did make one more prediction.","LOC:other")
    # print extract_entities("Wiarton Willie, the famous Canadian groundhog who predicted the arrival of spring")
    # print getKeywords(nltk.word_tokenize("How tall was Babe?"))
    # print similarityScore("What team did Babe play for?","None of the members of the team expected to do as well as they did.","HUM:gr")
    # print similarityScore("What team did Babe play for?","She played for Edmonto Grads.","HUM:gr")
    # print similarityScore("What team did Babe play for?","They were just a group of young women from the same school who liked to play basketball.","HUM:gr")
    # print similarityScore("Why did Kachmar say he announced the ban on kissing?","Kachmar says he made the announcement after receiving complaints about a few students whose intense kissing was making others uncomfortable.","DESC:desc")
    # print similarityScore("Why did Kachmar say he announced the ban on kissing?"," Kissing has a long history in Western civilization, with references dating back to the Old Testament.","DESC:desc")
