from flask import Flask
from flask import request
from flask import make_response
from flask import Response
from flask import send_file
import flask
import os
import seaborn as sns
import matplotlib
import datetime
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
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
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

sns.set()
sns.set_style("darkgrid")
sns.set(rc={'figure.figsize':(11.7,8)})

# Instantiates a client
client = language.LanguageServiceClient()

scoring = {'Clearly Positive': 0.3, 'Neutral': 0.1, 'Mixed': -0.1,'Clearly Negative': -0.6}
scoring = sorted(scoring.items(), key = itemgetter(1), reverse = True)
data_path = "/Users/alextaylor/Desktop/news"

app = Flask(__name__)

def produce_pdf(graphname,max_upvotes,max_votes,run_data):
    image_path = os.path.join(data_path,graphname)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",style= 'B', size=24)
    pdf.cell(200, 10, txt="User Feedback and Sentiment Analysis", ln=1, align="C")
    pdf.image(image_path, w=200)
    
    pdf.ln(1)  # move 5 down
    pdf.set_font("Arial", size=8)
    pdf.cell(200, 10, txt="This image describes the average sentiment score of users towards this product during each month with recorded data", ln=2)
    pdf.set_font("Arial",style = 'B', size=18)
    pdf.cell(200,10, txt = "Interpreting the Graph:",ln = 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200,10, txt = "Positive Sentiment: 0.3, Neutral Sentiment: 0.1, Mixed Sentiment: -0.1, Negative Sentiment: -0.3",ln = 1)
    pdf.set_font("Arial",style = 'B', size=18)
    pdf.cell(200,10, txt = "Relevant Comments:",ln = 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200,10, txt = 'Comment that received the most positive votes (%i): %s' % (max_upvotes[1],run_data[max_upvotes[0]]), ln = 1)
    pdf.cell(200,10, txt = 'Comment that received the most votes (%i): %s' % (max_votes[1],run_data[max_votes[0]]), ln =1)
    pdf.output("Sentiment_Report.pdf")

    return pdf

def produce_graph(graphname,df):
    plt.xticks(np.arange(1, 13, 1.0))
    ax = sns.lineplot(data=df, legend=False)

    plt.xlabel("Month Number")
    plt.ylabel("Sentiment Score")
    fig = ax.get_figure()
    fig.savefig(graphname)

def vote_processing(vote_data):
    max_upvotes = None
    max_votes = None
    max_votes_tracked = 0
    max_upvotes_tracked = 0
    for id_ in vote_data:
        if vote_data[id_][0] > max_upvotes_tracked: 
            max_upvotes = (id_,vote_data[id_][0])
            max_upvotes_tracked = vote_data[id_][0]
            
        if vote_data[id_][1] + vote_data[id_][0] > max_votes_tracked: 
            max_votes_tracked = vote_data[id_][1] + vote_data[id_][0]
            max_votes = (id_, max_votes_tracked)
    return max_upvotes,max_votes

def sentiment_analysis(ex):
    # The text to analyze
    try:
        unicode(ex)
    except UnicodeError:
        return None, None,''
    text = ex
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment

    #print('Text: {}'.format(text))
    print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    for score in scoring: 
        if sentiment.score >= score[1]: 
            print score[0]
            break
    return sentiment.score, sentiment.magnitude

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

    graphname = "sentiment_analysis.png"
    run_data,vote_data, time_data = retrieve_data(content)
    
    dates_scores = defaultdict(lambda: [])

    num_files = 0
    for id_ in run_data:
        if num_files >= 50: break
        score, magnitude = sentiment_analysis(run_data[id_])
        date = datetime.datetime.fromtimestamp(time_data[id_]).strftime('%m')
        if score != None: dates_scores[date].append(score)
        num_files += 1
    #iterate over dicts and avg scores
    avg_score_list = []
    for date, score in dates_scores.iteritems():
        avg_score_list.append(np.mean(dates_scores[date]))
    produce_graph(graphname,pd.DataFrame(np.array(avg_score_list).T, np.array([int(i) for i in dates_scores])))
    max_upvotes,max_votes = vote_processing(vote_data)
    pdf = produce_pdf(graphname,max_upvotes,max_votes,run_data)
    return pdf
  
@app.route('/postjson', methods = ['POST'])
def postJsonHandler():
    print 'accepted'
    content = request.get_json(force = True)
    pdf = orchestrate(content)
    jpg_to_pdf(pdf)
    return ''
    

@app.route('/jpg_to_pdf')
def jpg_to_pdf(pdf):
    flask.send_file(
    pdf,  # file path or file-like object
    'application/pdf',
    as_attachment=True,
    attachment_filename="whatever_you_want_to_name_it.pdf"
    )
    
    
  