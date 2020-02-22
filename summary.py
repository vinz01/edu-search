from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
import json

import sys
import re
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from youtube_transcript_api import YouTubeTranscriptApi

import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx

final_stopWords = []
temp_file = open('stopwords.txt', 'r')
final_stopWords = [line.rstrip('\n') for line in temp_file]

def getListFromDict(dict):
    dictlist= []
    for x in dict:
        dictlist.append(x['text'])
    return dictlist

def getFullPhrase(query, dictList):
    listOfPhrases = []
    for phrase in dictList:
        if query.lower() in phrase.lower().split(" "):
            idx = dictList.index(phrase)
            if idx == 0:
                listOfPhrases.append(dictList[idx] + " " + dictList[idx+1])
            elif idx == len(dictList)-1:
                listOfPhrases.append(dictList[idx-1] + " " + dictList[idx])
            else:
                listOfPhrases.append(dictList[idx-1] + " " + dictList[idx] + " " + dictList[idx+1])
           # listOfPhrases.append(dictList[idx])

    return listOfPhrases

def totalKeywordscore(a,b,c,phrase):
    numerator = 0
    denominator = 0
    p = []
    n = []
    nu = []
    index = 0
    p_sum=""
    n_sum=""
    nu_sum=""
    for i in range(len(a)):
        numerator += (a[i]*b[i]*c[i])
        denominator += (b[i]*a[i])

    positive = 0.0
    negative = 0.0
    neutral = 0.0

    for i in range(len(a)):
        if float(c[i]) > 0.01:
            # print("positve",c[i])
            p.append(phrase[index])
            positive += a[i]
            index=index+1
        elif float(c[i]) < -0.01:
            n.append(phrase[index])
            negative += a[i]
            index=index+1
        else:
            nu.append(phrase[index])
            neutral += a[i]
            index=index+1

    pos = positive/(positive+neutral+negative)
    neu = neutral/(positive+neutral+negative)
    neg = negative/(positive+neutral+negative)

    if denominator==0:
        denominator=1

    if len(p)!=0:
        p_sum = generate_summary(list2string(p),2)
    if len(n)!=0:
        n_sum = generate_summary(list2string(n), 2)
    if len(nu)!=0:
        nu_sum = generate_summary(list2string(nu), 2)

    return round(numerator/denominator,2),round(pos,2),round(neg,2),round(neu,2),p_sum,n_sum,nu_sum

def list2string(text):
    str=""
    for i in range(len(text)):
        str+=text[i]
        str+="."
    return str

def sample_analyze_entity_sentiment(text_content,query):
    type_ = enums.Document.Type.PLAIN_TEXT
    language = "en"
    document = {"content": text_content, "type": type_, "language": language}
    encoding_type = enums.EncodingType.UTF8
    client = language_v1.LanguageServiceClient()
    response = client.analyze_entity_sentiment(document, encoding_type=encoding_type)
    # Loop through entitites returned from the API
    salience = []
    score = []
    magnitude = []

    for entity in response.entities:
        if query.lower() in re.sub(r'[^\w\s]','',entity.name).lower().split(" "):

            salience.append(entity.salience)
            sentiment = entity.sentiment
            score.append(sentiment.score)
            magnitude.append(sentiment.magnitude)

    return salience,magnitude,score


def merge(keywordList):
    returnList = ""
    for i in keywordList:
        # print(i["text"])
        returnList += " " + i["text"]
    # print(returnList)
    return returnList





# creating a Flask app
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])


@app.route('/<query>/<videoID>', methods = ['GET'])
def getJSON(videoID, query):
    items = dict()
    if query in final_stopWords:        #if the query is not good enough to be searched,return -1
        return(json.dumps(items))
    phrases = getFullPhrase(query, getListFromDict(YouTubeTranscriptApi.get_transcript(videoID)))

    a = []
    b = []
    c = []

    if len(phrases)==0:             #if the keyword not found in any phrases
        return(json.dumps(items))

    for x in phrases:
        l,m,n = sample_analyze_entity_sentiment(x,query)
        print(l,m,n)
        if len(l) > 0:
            a.append(l[0])
            b.append(m[0])
            c.append(n[0])

    total2,p,n,nu,p_sum,n_sum,nu_sum = totalKeywordscore(a,b,c,phrases)
    print(total2)
    temp = {"p_summary":p_sum,"n_summary":n_sum,"nu_summary":nu_sum}
    print(temp)

    return (json.dumps(temp))


def read_article(file_name):
    # file = open(file_name, "r")
    # filedata = file.readlines()
    # article = filedata[0].split(". ")
    article = file_name.split(".")
    sentences = []

    for sentence in article:
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences


def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(file_name, top_n):
    nltk.download("stopwords")
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences = read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    # print("Indexes of top ranked_sentence order are ", ranked_sentence)

    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    str = ""
    for i in range(top_n):
        str += summarize_text[i]
        str += "."
    return str

# driver function
if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5004', threaded=True, debug = True)