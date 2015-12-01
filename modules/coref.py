#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Arne Neumann <pybart.programming@arne.cl>
# Edited to work here in QA system by Debjyoti Paul <deb@cs.utah.edu>

"""
Simple Python wrapper for BART (Beautiful Anaphora Resolution Toolkit).

Usage::

    bart.py input.txt output.xml
"""

import sys
import os, nltk
import urlparse
import requests
from bs4 import BeautifulSoup, NavigableString
import re
pronouns= set(["he", "she", "it", "its", "it's", "him", "her", "his","their","we", "our","i","you","your","my","mine","yours","ours","all" ])

BART_SERVER = 'http://localhost:8125'


def strip_tags(html, invalid_tags):
    soup = BeautifulSoup(html,"html.parser")
    coref_id_set=set()
    set2text={}
    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""

            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(unicode(c), invalid_tags)
                s += unicode(c)

            tag.replaceWith(s)

    for t in soup.find_all("coref"):
        if t['set-id'] in coref_id_set :
            pronoun_regex = re.compile('|'.join(pronouns))
            # print t.get_text(),
            if len(pronouns.intersection(nltk.word_tokenize(t.get_text().lower()))) > 0:
                # print t.get_text(),
                t.replaceWith(set2text[t['set-id']])
                # print "REPLACED WITH :" , set2text[t['set-id']]
        else:
            coref_id_set.add(t['set-id'])
            set2text[t['set-id']]=t.get_text()


    # print soup
    soup =  re.sub("(\\t|\\r?\\n)+", " ",str(soup))
    soup = re.sub("</s><s>","\n",soup)
    soup = re.sub('<[^>]*>', '', soup)
    return soup


def get_coreferences(input_filepath, host=BART_SERVER):
    """
    Takes a plain text file as input, pushes it to a running BART
    coreference server and returns a string that contains an inline XML
    representation of the input with coreferences added.
    """
    assert os.path.isfile(input_filepath), \
        "File doesn't exist: {}".format(input_filepath)
    with open(input_filepath, 'r') as input_file:
        post_url = urlparse.urljoin(host, '/BARTDemo/ShowText/process/')
        response = requests.post(post_url, input_file)
    return response.content



def resolve(filepath):
    xml_data = get_coreferences(filepath)
    invalid_tags = ['w']
    return strip_tags(xml_data,invalid_tags)

if __name__ == '__main__':

    input_filepath = "/Users/deb/Education/NLP/Projects/qa/developset/1999-W02-5.story"
    output_string = resolve(input_filepath)

    print output_string
