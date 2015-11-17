# get training set 5 and test set from http://cogcomp.cs.illinois.edu/Data/QA/QC/

import nltk
import re
import os, cPickle as pickle
from nltk import NaiveBayesClassifier
from pprint import pprint
from scikit_classifier import scikit_classifier
from collections import defaultdict
from keywords_pickle_builder import load_keywords
from nltk.corpus import wordnet as wn

keywordlist = ['do','substance','currency','religion','instrument','last','other','code','num','ord','speed','time','weight','body','def','desc','quot','state','abb','dimen','plant','popu','group','title','mount','dise','job','act','prod','art','vessel','food','anim','abb','term','city','comp','country','date','eff','dist','event','lang','loca','money','name','nick','peop','perc','sport','prof','temp','title','univ','vessel','eff','cause','tech','letter','symbol','word','color','big','fast','invent','discover','live','wrote','born']

#converts question categories in Li Roth Taxonomy to wordnet
def liroth_to_wordnet(category):
    # Abbreviation questions would need to be handled differently
    # since wordnet doesn't treat abbreviations differently
    if category == 'ABBR:abb': senses = None
    elif category == 'ABBR:exp': senses =  None
    elif category == 'ENTY:animal': senses = ['animal.n.01','big_cat.n.01','carnivore.n.01','food_fish.n.01']
    elif category == 'ENTY:body': senses = ['body_part.n.01','extremity.n.01','extremity.n.05','external_body_part.n.01']
    elif category == 'ENTY:color': senses = ['color.n.01','color.n.08']
    elif category == 'ENTY:cremat': senses = ['show.n.03','creation.n.02','writing.n.02','publication.n.01','music.n.01']
    elif category == 'ENTY:currency': senses = ['currency.n.01']
    elif category == 'ENTY:dismed': senses = ['illness.n.01','disorder.n.01','medicine.n.02','drug.n.01']
    # probably won't work well for events since they are usually names like "World War II"
    elif category == 'ENTY:event': senses = ['event.n.01','event.n.02','event.n.03','holiday.n.02']
    elif category == 'ENTY:food': senses = ['food.n.01','food.n.02']
    elif category == 'ENTY:instru': senses = ['instrument.n.06']
    elif category == 'ENTY:lang': senses = ['language.n.01']
    elif category == 'ENTY:letter': senses = ['letter.n.02']
    #ENTY:other can be pretty much everything
    elif category == 'ENTY:other': senses = None
    elif category == 'ENTY:plant': senses = ['plant.n.02']
    elif category == 'ENTY:product': senses = ['product.n.01','product.n.02','artifact.n.01']
    elif category == 'ENTY:religion': senses = ['religion.n.01','religion.n.02']
    elif category == 'ENTY:sport': senses = ['sport.n.01','sport.n.02']
    elif category == 'ENTY:substance': senses = ['element.n.02','substance.n.01']
    elif category == 'ENTY:symbol': senses = ['symbol.n.01','sign.n.01','sign.n.02']
    elif category == 'ENTY:techmeth': senses = ['technique.n.01','method.n.01']
    # ENTY:termeq can be anything, occurs in "what is the term for"
    elif category == 'ENTY:termeq': senses = ['term.n.01'] # the actual term won't have this sense, but the word 'term' might occur near it
    elif category == 'ENTY:veh': senses = ['vehicle.n.01']
    # ENTY:word can be anything, occurs in questions like "What English word has the most letters ?"
    elif category == 'ENTY:word': senses = None
    # Description questions can't be mapped to a word sense since they don't ask for a specific entity
    elif category == 'DESC:def': senses = None
    elif category == 'DESC:desc': senses = None
    elif category == 'DESC:manner': senses = None
    elif category == 'DESC:reason': senses = None
    elif category == 'HUM:gr': senses = ['organization','group','alumnus']
    elif category == 'HUM:ind': senses = ['person']
    elif category == 'HUM:title': senses = ['person'] #both names and titles have person as their hypernym
    elif category == 'HUM:desc': senses = ['person']
    elif category == 'LOC:city': senses = ['city','location']
    elif category == 'LOC:country': senses = ['country','location']
    elif category == 'LOC:mount': senses = ['mountain','location']
    elif category == 'LOC:other': senses = ['location.n.01']
    elif category == 'LOC:state': senses = ['state','location']
    # senses won't correspond to the numeric answer, but to words near it
    elif category == 'NUM:code': senses = ['phone_number','code']
    elif category == 'NUM:count': senses = ['number'] # could be anything
    elif category == 'NUM:date': senses = ['time_period','date','time']
    elif category == 'NUM:money': senses = ['monetary_unit','fractional_monetary_unit','sri_lanka_rupee.n.01','coin.n.01','bill.n.03']
    elif category == 'NUM:ord': senses = ['chapter','rank']
    elif category == 'NUM:other': senses = ['number.n.02']
    elif category == 'NUM:period': senses = ['time_period','time_unit']
    elif category == 'NUM:perc': senses = ['percent.n.01']
    elif category == 'NUM:speed': senses = ['speed.n.01','rate.n.02']
    elif category == 'NUM:temp': senses = ['Fahrenheit.a.01','Celsius.n.01']
    elif category == 'NUM:size': senses = ['linear_measure.n.01']
    elif category == 'NUM:weight': senses = ['mass_unit.n.01']
    else: senses = None
    if senses == None:
        return None
    else:
        result=[]
        for s in senses:
            result.extend(wn.synsets(s))
        return result


def liroth_to_sst(category):
    # Abbreviation questions would need to be handled differently
    # since wordnet doesn't treat abbreviations differently
    if category == 'ABBR:abb': senses = None
    elif category == 'ABBR:exp': senses =  None
    elif category == 'ENTY:animal': senses = ['noun.animal','noun.person']
    elif category == 'ENTY:body': senses = ['noun.body','noun.person']
    elif category == 'ENTY:color': senses = ['noun.color']
    elif category == 'ENTY:cremat': senses = ['noun.congnition','creation.n.02','writing.n.02','publication.n.01','music.n.01']
    elif category == 'ENTY:currency': senses = ['noun.currency','noun.quantity']
    elif category == 'ENTY:dismed': senses = ['noun.illness','noun.medicine','noun.drug','noun.health']
    # probably won't work well for events since they are usually names like "World War II"
    elif category == 'ENTY:event': senses = ['noun.event','noun.holiday']
    elif category == 'ENTY:food': senses = ['noun.food']
    elif category == 'ENTY:instru': senses = ['noun.instrument','noun.artifact', 'noun.object']
    elif category == 'ENTY:lang': senses = ['noun.language','noun.communication']
    elif category == 'ENTY:letter': senses = ['noun.communication','noun.letter']
    #ENTY:other can be pretty much everything
    elif category == 'ENTY:other': senses = ['noun.other']
    elif category == 'ENTY:plant': senses = ['noun.plant']
    elif category == 'ENTY:product': senses = ['noun.product','noun.object','noun.artifact']
    elif category == 'ENTY:religion': senses = ['noun.religion','noun.group']
    elif category == 'ENTY:sport': senses = ['noun.sport','noun.game']
    elif category == 'ENTY:substance': senses = ['noun.element','noun.object','noun.substance']
    elif category == 'ENTY:symbol': senses = ['noun.symbol','noun.sign']
    elif category == 'ENTY:techmeth': senses = ['noun.technique','noun.method']
    # ENTY:termeq can be anything, occurs in "what is the term for"
    elif category == 'ENTY:termeq': senses = ['noun.term'] # the actual term won't have this sense, but the word 'term' might occur near it
    elif category == 'ENTY:veh': senses = ['noun.vehicle']
    # ENTY:word can be anything, occurs in questions like "What English word has the most letters ?"
    elif category == 'ENTY:word': senses = None
    # Description questions can't be mapped to a word sense since they don't ask for a specific entity
    elif category == 'DESC:def': senses = None
    elif category == 'DESC:desc': senses = ['noun.motive']
    elif category == 'DESC:manner': senses = ['noun.manner']
    elif category == 'DESC:reason': senses = None
    elif category == 'HUM:gr': senses = ['noun.group','noun.organization']
    elif category == 'HUM:ind': senses = ['noun.person']
    elif category == 'HUM:title': senses = ['noun.person'] #both names and titles have person as their hypernym
    elif category == 'HUM:desc': senses = ['noun.person']
    elif category == 'LOC:city': senses = ['noun.location','noun.city']
    elif category == 'LOC:country': senses = ['noun.location','noun.country']
    elif category == 'LOC:mount': senses = ['noun.location','noun.mountain']
    elif category == 'LOC:other': senses = ['noun.location']
    elif category == 'LOC:state': senses = ['noun.location']
    # senses won't correspond to the numeric answer, but to words near it
    elif category == 'NUM:code': senses = ['noun.phone_number','noun.code']
    elif category == 'NUM:count': senses = None # could be anything
    elif category == 'NUM:date': senses = ['noun.time_period','noun.date','noun.time']
    elif category == 'NUM:money': senses = ['noun.monetary_unit','noun.currency','noun.money']
    elif category == 'NUM:ord': senses = ['noun.chapter','noun.rank']
    elif category == 'NUM:other': senses = ['noun.number']
    elif category == 'NUM:period': senses = ['noun.time_period','noun.time_unit','noun.time']
    elif category == 'NUM:perc': senses = ['noun.percent']
    elif category == 'NUM:speed': senses = ['noun.speed','noun.rate']
    elif category == 'NUM:temp': senses = ['Fahrenheit.a.01','Celsius.n.01']
    elif category == 'NUM:size': senses = ['linear_measure.n.01']
    elif category == 'NUM:weight': senses = ['mass_unit.n.01']
    else: senses = None
    if senses == None:
        return None
    else:
        return [wn.synset(s) for s in senses]


def liroth_to_corenlp(category):
    if category == 'ENTY:currency': senses = 'MONEY'
    elif category == 'HUM:gr': senses = 'ORGANIZATION'
    elif category == 'HUM:ind': senses = 'PERSON'
    # however, in corenlp 'PERSON' is only for names, titles are ignored by corenlp
    elif category == 'HUM:title': senses = 'PERSON'
    elif category == 'HUM:desc': senses = 'PERSON'
    elif category == 'LOC:city': senses = 'LOCATION'
    elif category == 'LOC:country': senses = 'LOCATION'
    elif category == 'LOC:mount': senses = 'LOCATION'
    elif category == 'LOC:other': senses = 'LOCATION'
    elif category == 'LOC:state': senses = 'LOCATION'
    elif category == 'NUM:code': senses = 'NUMBER'
    elif category == 'NUM:count': senses = 'NUMBER'
    elif category == 'NUM:date': senses = 'DATE'
    elif category == 'NUM:money': senses = 'MONEY'
    elif category == 'NUM:ord': senses = 'NUMBER'
    elif category == 'NUM:other': senses = 'NUMBER'
    elif category == 'NUM:period': senses = 'DURATION'
    elif category == 'NUM:perc': senses = 'PERCENT'
    elif category == 'NUM:speed': senses = 'NUMBER'
    elif category == 'NUM:temp': senses = 'NUMBER'
    elif category == 'NUM:size': senses = 'NUMBER'
    elif category == 'NUM:weight': senses = 'NUMBER'
    else: senses = None
    return senses

class QuestionClassifier:
    def __init__(self, fine_grain=True):
        self.keywordlist2 = load_keywords()
        train_set = self.load_labelled_data('qcdata/train_5500.label', fine_grain=fine_grain)
        self.train_classifier(train_set, fine_grain=fine_grain)

    def question_features(self, question):
        features = defaultdict(int)
        words = nltk.word_tokenize(question)
        # First few words (positional)
        for idx,w in enumerate(words[0:2]):
            features['w%d:'%idx + w.lower()] = 1
        # Bag of words of keywords
        for word in words:
            if word in self.keywordlist2:
                for keyword in self.keywordlist2[word]:
                    features['kw:'+keyword] += 1
        return features

    def load_labelled_data(self, filename, fine_grain=True):
        train_set = []
        with open(filename, 'r') as f:
            for line in f:
                if fine_grain:
                    match = re.match('([A-Z]+:[a-z]+) (.+)', line)
                else:
                    match = re.match('([A-Z]+):[a-z]+ (.+)', line)
                train_set.append((self.question_features(match.groups()[1]),match.groups()[0]))
        return train_set

    def train_classifier(self, train_set, C=1e5, fine_grain=True):
        # self.classifier = NaiveBayesClassifier.train(train_set)
        # self.classifier = nltk.classify.DecisionTreeClassifier.train(train_set)
        # self.classifier = nltk.MaxentClassifier.train(train_set,algorithm="gis",max_iter=50,trace=3)
        self.classifier = scikit_classifier.train(train_set,C=C)

    def classify(self, question):
        return self.classifier.classify(self.question_features(question))

def get_classifier():
    fine_grain = True
    classifier = QuestionClassifier(fine_grain)
    test_set = classifier.load_labelled_data('qcdata/TREC_10.label',fine_grain)
    # test_set = classifier.load_labelled_data('qcdata/train_4000.label',fine_grain)
    train_set = classifier.load_labelled_data('qcdata/train_5500.label', fine_grain=fine_grain)
    accuracy =0
    for C in [3**x for x in range(0,10)]:
        # for C in [0.1,0.01,0.001,0.0001,0.00001]:
        classifier.train_classifier(train_set, C=C, fine_grain=fine_grain)
        tempAcc =nltk.classify.accuracy(classifier.classifier, test_set)
        if tempAcc > accuracy:
            accuracy=tempAcc
            C_VAL = C
        # print C,":", tempAcc
    # print "Training with C ", C_VAL
    classifier.train_classifier(train_set, C=C_VAL, fine_grain=fine_grain)
    return classifier


if __name__ == '__main__':
    fine_grain = True
    classifier = QuestionClassifier(fine_grain)
    test_set = classifier.load_labelled_data('qcdata/TREC_10.label',fine_grain)
    train_set = classifier.load_labelled_data('qcdata/train_5500.label', fine_grain=fine_grain)
    for C in [10**x for x in range(0,8)]:
        # for C in [0.1,0.01,0.001,0.0001,0.00001]:
        classifier.train_classifier(train_set, C=C, fine_grain=fine_grain)
        print C,":",nltk.classify.accuracy(classifier.classifier, test_set)
    classifier.train_classifier(train_set, fine_grain=fine_grain)
    # print "DONEEEEEEEEEEEEEE -----------"
    print classifier.classify('How much money does the Sultan of Brunei have?')
    print classifier.classify('When did Geraldine Ferraro run for vice president?')
    print classifier.classify('What is the nickname of Pennsylvania?') #it got this wrong
    print classifier.classify('Who is Desmond Tutu?')
    print classifier.classify('How fast can a Corvette go?')
