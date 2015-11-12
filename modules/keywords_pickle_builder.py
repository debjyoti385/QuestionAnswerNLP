import os, cPickle as pickle
from pprint import pprint
from collections import defaultdict
from itertools import chain

KEYWORDS_VERSION = 1

def load_keywords(try_cache=True, dir='qcdata/publish/lists'):
    if try_cache:
        try:
            with open('qcdata/keywords2pickle', 'rb') as f:
                keywords,version = pickle.load(f)
                if version == KEYWORDS_VERSION:
                  return keywords
        except:
            pass
    
    keywords = defaultdict(list)
    for dirname, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            if "." in filename:
                continue
            with open(os.path.join(dirname, filename), 'r') as f:
                for line in f:
                    keywords[line.strip()].append(filename)
    save_keywords(keywords=keywords)
    return keywords

def save_keywords(keywords):
    # Write to a pickle
    with open('qcdata/keywords2pickle', 'wb') as fout:
        pickle.dump((keywords,KEYWORDS_VERSION), fout)
    # pprint(keywords)

#to use, download the file linked http://cogcomp.cs.illinois.edu/Data/QA/QC/QC.tar
#and extract into data/train/qc/
if __name__ == '__main__':
    k = load_keywords(try_cache=False)
    print len(set( chain( *(k.values()) ) ))
