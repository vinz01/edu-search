from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys
import re
from google.cloud import language_v1
from google.cloud.language_v1 import enums

final_stopWords = []
temp_file = open('stopwords.txt', 'r')
final_stopWords = [line.rstrip('\n') for line in temp_file]


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])

@app.route('/<query>/<videoID>', methods = ['GET'])
def getJSON(videoID, query):
    returnList = []
    if query in final_stopWords:        #if the query is not good enough to be searched,return -1
        return(json.dumps(returnList))
    keywordList = YouTubeTranscriptApi.get_transcript(videoID)
    for i in keywordList:
        phrase = i['text']
        if query.lower() in phrase.lower():
            temp = {"timestamp": str(i['start']) + 's',
                    "phrase": i['text']}
            returnList.append(temp)
   
    return (json.dumps(returnList))

# driver function
if __name__ == '__main__':

	app.run(host='0.0.0.0', port='5000', threaded=True, debug = True)
