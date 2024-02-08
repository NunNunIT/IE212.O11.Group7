from dash import html, dash_table
from dash import Dash, html, dcc, callback, Output, Input
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import colormaps
import plotly.graph_objects as go
import nltk

def create_sentiment_option_layout():
    return html.Div([
                html.Div([
                    html.Label('Year'),
                    dcc.Dropdown(
                        id='year-sentiment-dropdown',
                        options= [{'label': 'All', 'value': 'All'}] + [{'label': str(year), 'value': str(year)} for year in range(1990, 2025)],
                        value= 'All',  # Giá trị mặc định là All
                        placeholder='Chọn năm',  # Nhãn placeholder
                    ),
                ], className = 'dropdown-item'),
                html.Div([
                    html.Label('Places'),
                    dcc.Dropdown(
                        id='place-sentiment-dropdown',
                        options= [{'label': 'ChIJ-cMNqQApdTERLoYJepwMbQM', 'value': 'ChIJ-cMNqQApdTERLoYJepwMbQM'}],
                        value= 'ChIJ-cMNqQApdTERLoYJepwMbQM',
                        placeholder='Chọn địa điểm',  # Nhãn placeholder
                    ),
                ], className = 'dropdown-item'),
            ], className='contain-layout')

# Tạo danh sách stopwords (đã có từ trước)
stop_words = set()
# Đọc từng dòng trong file stopwords.txt và thêm từ vào set stop_words
with open("vietnamese-stopwords.txt", "r", encoding="utf-8") as file:
    for line in file:
        word = line.strip()  # Loại bỏ khoảng trắng và ký tự xuống dòng
        stop_words.add(word)

# Định nghĩa hàm combine_negation
def combine_negation(tokens):
    combined_tokens = []
    i = 0
    while i < len(tokens):
        if i > 0 and i < len(tokens) - 1:
            combined_tokens.append(tokens[i - 1] + "_" + tokens[i] + "_" + tokens[i + 1])
            combined_tokens.append(tokens[i])
            combined_tokens.append(tokens[i - 1] + "_" + tokens[i])
            combined_tokens.append(tokens[i] + "_" + tokens[i + 1])
        i += 1
    return combined_tokens


def create_fig_sentiments(data_list, color_c, text):
    data_list_combined = []
    for sentence in data_list:
        tokens = nltk.word_tokenize(sentence)
        tokens = [token.lower() for token in tokens if token.lower() not in stop_words]  # Loại bỏ stop words
        combined_tokens = combine_negation(tokens)
        combined_tokens = [token for token in combined_tokens if token not in stop_words]
        data_list_combined.extend(combined_tokens)
    
    # Đếm tần suất xuất hiện của các từ
    word_freq = Counter(data_list_combined)
    most_common_words = word_freq.most_common(20)  # Lấy 20 từ xuất hiện nhiều nhất
    
    # Tạo biểu đồ cột
    words, frequencies = zip(*most_common_words)
    fig = go.Figure(data=[go.Bar(x=words, y=frequencies, text=frequencies,
            textposition='auto', marker_color=color_c)]) # Chú ý marker_color ở đây
    fig.update_layout(title_text=text, xaxis_title="Words", yaxis_title="Frequency")
    return fig

def create_info_sentiments_layout():
    return html.Div([
                html.Div([
                html.Div(id='info-sentiments-name', className = 'bold-text', children=[])
                ], className = 'row-item'),
                html.Div([
                    html.Div(id='info-sentiments-address', children=[])
                ], className = 'row-item'),
                html.Div([
                    html.Label("Categories:  "),
                    html.Div(id='info-sentiments-categories', children=[])
                ], className = 'row-item'),
            ], className='row-layout')

