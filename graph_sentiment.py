from flask import Flask
from flask import request
from flask import make_response
from flask import Response
from flask import send_file
import flask
import os
import datetime
import random
import pandas as pd
import string
import calendar
import numpy as np
import json
from operator import itemgetter
from collections import defaultdict
from collections import OrderedDict
from fpdf import FPDF
# Imports the Google Cloud client library
import six
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
# Import database module.
from firebase_admin import db

# Get a database reference to our posts
ref = db.reference('https://lmigos.firebaseio.com/messages/-LjRVSiJcpJ_X7ilCKEBhttps://lmigos.firebaseio.com/messages/-LjRVSiJcpJ_X7ilCKEB/body')

# Read the data at the posts reference (this is a blocking operation)
print(ref.get())

data_path = "/Users/alextaylor/Desktop/hackathon_2019"
dates_dict = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}


app = Flask(__name__)

# Instantiates a client
client = language.LanguageServiceClient()

def sentiment_analysis(text):
    # The text to analyze
    if isinstance(text, six.binary_type): text = text.decode('utf-8')

    document = types.Document(content=text,type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    #print('Text: {}'.format(text))
    print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    return sentiment.score * sentiment.magnitude

def retrieve_data(content):
    
    run_data = {}
    vote_data = {}
    time_data = {}
        
    os.chdir(data_path)
    for message in content.keys():
        run_data[content[message]['id']] = content[message]['body']
        vote_data[content[message]['id']] = (int(content[message]['upvote']),int(content[message]['downvote']))
        time_data[content[message]['id']] = int(content[message]['timestamp'])

    return run_data, vote_data, time_data

def orchestrate(content):

    run_data, _, time_data = retrieve_data(content)
    
    dates_scores = defaultdict(lambda: [])

    for id_ in run_data:
        score = sentiment_analysis(run_data[id_]) #sentiment_score * sentiment_magnitude
        date = datetime.datetime.fromtimestamp(time_data[id_]).strftime('%m')
        if score != None: dates_scores[date].append(score)
    #iterate over dicts and avg scores
    avg_score_list = []

    for date, score in dates_scores.iteritems():
        avg_score_list.append(np.mean(dates_scores[date]))
    
    return
  
@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print 'accepted'
    content = request.get_json(force = True)
    orchestrate(content)
    return ''