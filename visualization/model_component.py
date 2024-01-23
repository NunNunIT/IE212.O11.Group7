import gzip
import pandas as pd
import goslate
import json
import requests

import nltk
import string
from nltk.stem.porter import *
from nltk.corpus import stopwords
from textblob import TextBlob
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from collections import Counter

from sklearn import linear_model
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

import joblib

import re

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def predictions_and_other(df_in):
    df_in["reviewText"] = [item + "." for item in df_in["reviewText"]]
    df_in["reviewLength"] = [len(item) for item in df_in["reviewText"]]
    df_in["reviewHour"] = [item.hour for item in df_in["dtime"]]
    df_in["priceRank"] = [1 if price == '$' else 2 if price == '$$' else 3 if price == '$$$' else 0 for price in df_in['price']]

    df_in['sentences'] = df_in['reviewText'].apply(split_into_sentences)
    df_in['sentiments'] = df_in.apply(lambda row: [TextBlob(sentence).sentiment[0] for sentence in row['sentences']] if len(row['sentences']) > 0 else [TextBlob(row['reviewText']).sentiment[0]], axis=1)

    count_pos = df_in['sentiments'].apply(lambda sentiments: sum(sentiment > 0 for sentiment in sentiments))
    count_neg = len(df_in['sentiments'][0]) - count_pos

    df_in['Pos_prop'] = count_pos / len(df_in['sentiments'][0])
    df_in['Neg_prop'] = count_neg / len(df_in['sentiments'][0])

    model = joblib.load(".\models\model.joblib")

    selected_columns = ["Pos_prop", "Neg_prop", "reviewLength", "priceRank", "reviewHour"]
    X = df_in[selected_columns]

    predictions = model.predict(X)

    df_in["Rating_predict"] = predictions

def top_nouns_by_sentiment_range(df_in, counters):
    noun_freq_by_id_sentiment_range = {}

    text_column = 'sentences'
    sentiment_column = 'sentiments'
    id_column = 'gPlusPlaceId'
    negative_range = (-1, 0)
    positive_range = (0, 1)
    n = 20

    for index, row in df_in.iterrows():
        sentiments = row[sentiment_column]
        if not sentiments:
            continue

        text_data = row[text_column]
        if not text_data:
            continue

        place_id = row[id_column]
        place_name = row["name"]

        if place_id not in noun_freq_by_id_sentiment_range:
            noun_freq_by_id_sentiment_range[place_id] = {
                'negative': Counter(),
                'positive': Counter(),
                'name': string
            }

        for i, sentiment in enumerate(sentiments):
            if negative_range[0] <= sentiment < negative_range[1]:
                sentiment_label = 'negative'
            elif positive_range[0] <= sentiment <= positive_range[1]:
                sentiment_label = 'positive'
            else:
                continue

            tokens = word_tokenize(text_data[i])
            tagged_words = pos_tag(tokens)

            nouns = [word for word, pos in tagged_words if pos.startswith('N')]
            stop_words = set(stopwords.words('english'))
            nouns = [word.lower() for word in nouns if word.lower() not in stop_words]

            noun_freq_by_id_sentiment_range[place_id][sentiment_label].update(nouns)

    # Extract the top n items for each sentiment category
    top_nouns_by_id_sentiment_range = {}
    for place_id, sentiment_counts in noun_freq_by_id_sentiment_range.items():
        top_nouns_by_id_sentiment_range[place_id] = {}
        for sentiment_label, noun_counter in sentiment_counts.items():
            top_nouns_by_id_sentiment_range[place_id][sentiment_label] = dict(noun_counter.most_common(n))
    top_nouns_by_id_sentiment_range[place_id]['name'] = place_name

    counters = merge_data(counters, top_nouns_by_id_sentiment_range)

def merge_data(dict1, dict2):
    merged_data = dict1

    for place_id, data2 in dict2.items():
        if place_id in merged_data:
            # Update counters
            merged_data[place_id]['negative'].update(data2.get('negative', Counter()))
            merged_data[place_id]['positive'].update(data2.get('positive', Counter()))

            # Update other values, for example, 'name'
            merged_data[place_id]['name'] = data2.get('name', merged_data[place_id]['name'])
        else:
            # If the place_id doesn't exist in the first dictionary, add it
            merged_data[place_id] = data2.copy()

    return merged_data