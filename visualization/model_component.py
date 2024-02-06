from datetime import datetime
import pandas as pd
from string import punctuation
import underthesea
import joblib

def modelsetup():
    abbreviation_dict = '../vncorenlp/abbreviation_dictionary_vn.xlsx'
    df = pd.read_csv('../vncorenlp/abbreviation_dictionary_vn.csv')
    abbreviation_dict = df.set_index("abbreviation")["meaning"].to_dict()
    # Define the base Vietnamese alphabet without tone marks
    vietnamese_alphabet = "aăâbcdđeêghiklmnoôơpqrstuưvwxy"
    vietnamese_letter_with_tone = "áàạãảắằẵẳặấầẩẫậéèẻẽẹềếểễệòóỏõọồốổỗộờớởỡợúùũủụứừửữựíìĩỉịýỳỹỷỵ"

    # Create uppercase Vietnamese letters with tone marks
    uppercase_vietnamese_letters_with_tone = [char.upper() for char in vietnamese_letter_with_tone]
    uppercase_vietnamese_alphabet = vietnamese_alphabet.upper()

    # Combine the lists into strings
    lowercase_string = vietnamese_alphabet + "".join(vietnamese_letter_with_tone)
    uppercase_string = uppercase_vietnamese_alphabet + "".join(uppercase_vietnamese_letters_with_tone)
    allcase_string = lowercase_string + uppercase_string

    punctuation = "!\"#$%&'()*+,./:;<=>?@[\]^_`{|}~"

    from vncorenlp import VnCoreNLP
    annotator = VnCoreNLP("../vncorenlp/VnCoreNLP-1.1.1.jar", annotators="wseg", max_heap_size='-Xmx500m')
    
def formatToDatetime(date_string):
    date_string_without_fraction = date_string[:-5] + 'Z'
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strptime(date_string_without_fraction, date_format)

def unicodeReplace(text):
    replacements = {
        "òa": "oà", "óa": "oá", "ỏa": "oả", "õa": "oã", "ọa": "oạ",
        "òe": "oè", "óe": "oé", "ỏe": "oẻ", "õe": "oẽ", "ọe": "oẹ",
        "ùy": "uỳ", "úy": "uý", "ủy": "uỷ", "ũy": "uỹ", "ụy": "uỵ",
        "Ủy": "Uỷ", "\n": "." , "\t": "."  
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def unicode(data):
    data['text'] = data['text'].apply(unicodeReplace)
    return data

import re

def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251" 
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def stickyPreprocess(data):
    def processText(text):
        result = []
        for letter_id in range(len(text) - 2):
            prev, letter, after = text[letter_id], text[letter_id + 1], text[letter_id + 2]

            if letter in punctuation:
                if prev in allcase_string:
                    result.append(letter_id + 1)
                if after in allcase_string:
                    result.append(letter_id + 2)

            if letter in uppercase_string and prev in lowercase_string and letter_id != 0:
                result.extend([letter_id, letter_id + 1])

        for index in reversed(result):
            text = text[:index] + " " + text[index:]

        return text

    data['text'] = data['text'].apply(processText)
    return data

def abbreviationPreprocess(data):
    def replaceWord(word, dictionary):
        return dictionary.get(word, word)

    def processText(text):
        annotator_text = annotator.tokenize(text)

        tokens = [it for sublist in annotator_text for it in sublist if it != '_']
        tokens = [replaceWord(it.lower(), abbreviation_dict) for it in tokens]

        sentences = [' '.join(sublist) for sublist in annotator_text]

        return pd.Series([' '.join(tokens), sentences], index=['text', 'sentences'])

    data[['text', 'sentences']] = data['text'].apply(processText)

    return data

def sentimentCal(sentences):
    sentiments = [underthesea.sentiment(text) for text in sentences]
    return sentiments

def predictions_and_other(df_in):
    # Format "publishedAtDate" to datetime
    df_in['publishedAtDate'] = df_in['publishedAtDate'].apply(lambda x: formatToDatetime(x))

    df_in = unicode(df_in)
    df_in['text'] = df_in['text'].apply(remove_emojis)
    df_in = stickyPreprocess(df_in)
    df_in = abbreviationPreprocess(df_in)

    df_in["sentiment"] = df_in["sentences"].apply(sentimentCal)
    df_in['sentiment'] = df_in['sentiment'].apply(lambda sentiments: ["neutral" if sentiment is None else sentiment for sentiment in sentiments])

    df_in["text"] = [item + " ." for item in df_in["text"]]
    df_in["reviewHour"] = [item.hour for item in df_in["publishedAtDate"]]
    df_in["reviewLength"] = [len(item) for item in df_in["text"]]

    count_pos = df_in['sentiment'].apply(lambda sentiments: sum(sentiment == "positive" for sentiment in sentiments))
    count_neg = df_in['sentiment'].apply(lambda sentiments: sum(sentiment == "negative" for sentiment in sentiments))

    df_in['num_sentiments'] = df_in['sentiment'].apply(lambda sentiments: len(sentiments) if sentiments else 0)

    df_in['pos_prop'] = count_pos / df_in['num_sentiments']
    df_in['neg_prop'] = count_neg / df_in['num_sentiments']

    model = joblib.load("..\models\model.joblib")

    selected_columns = ["pos_prop", "neg_prop", "reviewLength", "reviewHour"]
    X = df_in[selected_columns]

    predictions = model.predict(X)

    df_in["Rating_predict"] = predictions
