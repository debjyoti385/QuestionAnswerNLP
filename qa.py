#!/usr/bin/python

import argparse
import glob, os, sys, subprocess
import pickle,re
import nltk

sys.path.append("modules")
import sourceContentSelector
import QuestionClassifier
import SimilarityModule
import AnswerUtility

resolved_articles={}
resolved_ner={}
arkref_temp_path ="/tmp/story.txt"
pronouns= set(["he", "she", "it", "its", "it's", "him", "her", "his","they","their","we", "our","i","you","your","my","mine","yours","ours","all", "", "he", "her", "hers", "herself", "him", "himself", "his", "", "", "it", "its", "itself", "many", "me mine", "more", "most", "much", "my", "myself", "neither", "no one", "nobody", "none", "nothing", "one", "other", "others", "our", "ours", "ourselves", "several", "she", "some", "somebody", "someone", "something", "that", "their", "theirs", "them", "themselves", "these", "they", "this", "those", "us", "we", "which",  "who", "whoever", "whom", "whose", "you", "your", "yours", "yourself", "yourselves"])

sst_type=set()

def get_metadata(file):
    with open(file,"r") as storyfile:
        flag = 0
        text=""
        for line in storyfile:
            if flag==0:
                if "TEXT" in line:
                    flag=1
                if "HEADLINE" in line:
                    text += line[line.rfind("LINE")+5:].rstrip("\n") +". \n"
                if "DATE" in line:
                    text +=  line[line.rfind("DATE")+5:].rstrip("\n") +". \n"
                if "STORYID" in line:
                    text +=  line[line.rfind("ID")+3:].rstrip("\n") +". \n"
                    storyid= line[line.rfind("ID")+3:]
            else:
                text += re.sub("[\n-]"," ",line)
    return storyid,text

def get_questions(file):
    questions=[]
    with open(file,"r") as qfile:
        flag=0
        for line in qfile:
            if flag==0:
                if "QuestionID:" in line:
                    question_id = line [line.find("ID:")+3:].rstrip("\n")
                    flag=1
            else:
                if "Question:" in line:
                    question = line[line.find("tion") + 5 :].rstrip("\n")
                    questions.append((question_id,question))
                    flag=0
    return questions

def get_sst(filename):
    lines=dict()
    try:
        with open(filename,"r") as infile:
            for line in infile:
                wordList=line.split()
                for w in wordList:
                    e=w.split("/")
                    try:
                        if e[1]!=None and e[1] !="0" and ( "noun" in e[1] or "verb" in e[1] ) :
                            sst_type.add(e[1])
                            lines[e[0]] = e[1]
                    except:
                        pass
    except:
        return None
    return lines

def load_resolved_articles():
    if os.path.isfile("resolved_articles.p"):
        with open("resolved_articles.p", "rb") as input_file:
            return pickle.load(input_file)
    else:
        return {}

def load_resolved_ner():
    if os.path.isfile("resolved_ner.p"):
        with open("resolved_ner.p", "rb") as input_file:
            return pickle.load(input_file)
    else:
        return {}


def process_input(article_path):
    # try:
    #     if article_path in resolved_articles:
    #         resolve1 = resolved_articles[article_path]
    #         resolve2 = resolved_ner[article_path]
    #         return resolve1,resolve2
    #     fh = open("NUL", "w")
    #     subprocess.call(["rm", arkref_temp_path.replace("txt","tagged")], stderr=fh)
    #     subprocess.call(["rm", arkref_temp_path.replace("txt","sst")], stderr=fh)
    #     subprocess.call(["rm", arkref_temp_path.replace("txt","parse")], stderr=fh)
    #     subprocess.call(["rm", arkref_temp_path.replace("txt","osent")], stderr=fh)
    #     subprocess.call(["arkref.sh", "-input", arkref_temp_path], stderr=fh)
    #     fh.close()
    #
    #     tagged_article = open(arkref_temp_path.replace("txt", "tagged")).read()
    #     tagged_article = "<root>" + tagged_article + "</root>"  # trick arkref into doing entire doc
    #     soup = bs4.BeautifulSoup(tagged_article, "html.parser").root
    #     for entity in soup.find_all(True):
    #         if entity.string != None and entity.string.strip().lower() in pronouns:
    #             antecedent_id = entity["entityid"].split("_")[0]
    #             antecedent = soup.find(mentionid=antecedent_id)
    #             antecedent = str(antecedent).split(">", 1)[1].split("<", 1)[0]
    #             antecedent = re.sub("[-!,`']","",antecedent)
    #             print antecedent
    #             # print antecedent_id, antecedent
    #             # string = re.sub('<.*?>',' ',str(antecedent))
    #             # tok = nltk.word_tokenize(string)
    #             # ants = [(x,y) for x,y in nltk.pos_tag(tok) if y in {'NNP','NN'}]
    #             entity.string.replace_with(antecedent)
    #     # print soup
    #     resolve1 = re.sub("<.*?>", "", str(soup))
    #     resolve2 = get_sst(arkref_temp_path.replace("txt", "sst"))
    #     resolved_articles[article_path] = resolve1
    #     resolved_ner[article_path] = resolve2
    #     return resolve1, resolve2
    # except:
        resolve1= open(arkref_temp_path).read()
        resolve2 = get_sst(arkref_temp_path.replace("txt", "sst"))
        return resolve1, resolve2




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='QUESTION ANSWER SYSTEM',
                                     epilog='',
                                     prog='')
    parser.add_argument("-i", "--input", required=True,
                        help="Input file containing list of story files")
    parser.add_argument("-t", "--temp", default="story.txt",
                        help="temp file to operate on story")
    parser.add_argument("-o", "--output", type=str, default="myresponse.txt",
                    help=" Output file where answers will be stored")
    args = vars(parser.parse_args())
    input_file=args['input']
    out_filename=args['output']

    out = open(out_filename,"w")
    out.close()


    # resolved_articles=load_resolved_articles()
    # resolved_ner = load_resolved_ner()
    q_classifier = QuestionClassifier.get_classifier()
    arkref_temp_path = args['temp']
    with open(input_file,"r") as inputListFile:
        input_dir = inputListFile.readline().strip("\n")
        storyFileList = []
        for line in inputListFile:
            storyFileList.append(line.strip("\n"))

    for file in storyFileList:
        file = input_dir +"/"+ file + ".story"
    # for file in glob.glob(input_dir+"/*.story"):
        storyid,text = get_metadata(file)
        article=text
        # with open (arkref_temp_path,"w") as tempfile:
        #     tempfile.write(text)
        #
        # article, ner = process_input(file)
        # print "length of article and ner ", len(article), len(ner)
        questions = get_questions(file.replace("story","questions"))


        for question in questions:
            q_type = q_classifier.classify(question[1])
            relevant = SimilarityModule.getScoredSentences(question[1],article, q_type)

            relevant.sort(key=lambda t:t[1],reverse=True)
            out = open(out_filename,"a")
            # print "##################################################################"
            # print question[0], question[1], q_type
            answer=AnswerUtility.filter(question[1],relevant[0][0], q_type)
            print("QuestionID: "+ question[0] )
            out.write("QuestionID: "+ question[0] + "\n")
            print ("Answer: "+ answer +"\n")

            out.write("Answer: "+ answer +"\n\n")
            out.close()
            # print "##################################################################"
            print
            # print "2: ", relevant[1]

        # print sst_type

    with open("resolved_articles.p", "wb") as output_file:
        pickle.dump(resolved_articles,output_file)
    with open("resolved_ner.p", "wb") as output_file:
        pickle.dump(resolved_ner,output_file)
