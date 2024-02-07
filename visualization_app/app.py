import dash     # need Dash version 1.21.0 or higher
from dash import dcc, html, Input, Output, State
import dash_table
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
# from bson import ObjectId
from dashboard_layout import *
from recomended_layout import *
from sentiments_layout import *
from gensim.utils import simple_preprocess

# Connect to local server
client = MongoClient("mongodb://127.0.0.1:27017/")
# Create database called animals
mydb = client["ie212_o11_group7"]
# Create Collection (table) called shelterA
collection_reviews = mydb.reviews

app = dash.Dash(__name__, suppress_callback_exceptions=True)


# Layout của Dash App
app.layout = html.Div([
    create_introduct_layout(),
    html.H1("Overview", className="centered-heading", id="see-here"),
    html.Div([
        create_introduct_overview_layout()
    ], className="dashboard-container"),
    html.H1("Dashboard", className="centered-heading"),
    html.Div([
        create_dashboard_option_layout(),
        create_dashboard_total_layout(),
        html.Div([
                dcc.Graph(id='dashboard-review-chart'),
                dcc.Graph(id='dashboard-fig-star'),
            ], className='contain-layout'),
        html.Div(id='mongo-datatable', children=[]),
        # dcc.Graph(id='dashboard-map'),
    ], className="dashboard-container"),
    html.H1("Recomended System", className="centered-heading"),
    html.Div([
        create_PlaceName_PlaceID_Dropdown(),
        create_SearchButton_layout(),
        html.Div([
            create_dashtable_result(),
            dcc.Store(id='result-store', data=df_result.to_dict('records')),
        ], className='contain-layout'),
    ], className="dashboard-container"),
    html.H1("Sentiment", className="centered-heading"),
    html.Div([
        create_sentiment_option_layout(),
        html.Div([
                dcc.Graph(id='sentiment-positive-chart'),
                dcc.Graph(id='sentiment-negative-chart'),
            ], className='contain-layout'),
    ], className="dashboard-container"),
    html.Div([
    ], className="dashboard-container"),
    # activated once/week or when page refreshed
    # dcc.Interval(id='interval_db', interval=86400000 * 7, n_intervals=0),
    dcc.Interval(id='interval_db', interval=10*1000, n_intervals=0),
    html.Button("Save to Mongo Database", id="save-it"),
    html.Button('Add Row', id='adding-rows-btn', n_clicks=0),
], className='main-container')

########## BEGIN OF INTRODUCT TOTAL ############################################################
@app.callback([Output('overview-total-ratings', 'children'),
               Output('overview-total-places', 'children'),
               Output('overview-total-user', 'children'),],
              [Input('interval_db', 'n_intervals')])
def overview_display(select_year='All', select_place='All'):
    # Truy vấn để lấy dữ liệu từ MongoDB
    query = {}
    
    # Đếm số lượng đánh giá (ratings), số lượng bình luận (reviews), số lượng địa điểm (places) và số lượng người dùng (users)
    ratings = collection_reviews.count_documents(query)

    places = len(collection_reviews.distinct("placeId", query))
    users = len(collection_reviews.distinct("reviewerId", query))

    return [ratings, places, users]
########## END OF INTRODUCT TOTAL ############################################################


########### BEGIN OF DASH BOARD ################################################################
# Dashboard - 1. Callback to update dropdown options *************************
def get_dropdown_options(field_name):
    distinct_values = collection_reviews.distinct(field_name) 
    options = [
        {'label': str(value), 'value': str(value)}
        for value in distinct_values
    ]
    return options

@app.callback(
    [Output('place-dropdown', 'options'),
     Output('place-sentiment-dropdown', 'options')],
    Input('interval_db', 'n_intervals'),
)
def update_dropdown(n_intervals):
    dropdown_place_options = get_dropdown_options("placeId")

    return [dropdown_place_options, dropdown_place_options]

# Dashboard - 2. Display with data from Mongo database *************************
@app.callback([Output('mongo-datatable', 'children'),
               Output('total-ratings', 'children'),
               Output('total-user', 'children'),
               Output('dashboard-review-chart', 'figure'),
               Output('dashboard-fig-star', 'figure'),],
              [Input('year-dropdown', 'value'),
               Input('place-dropdown', 'value')])
def dashboard_display(select_year='All', select_place='All'):
    # Truy vấn để lấy dữ liệu từ MongoDB
    query = {}
    
    if select_year != 'All':
        query["publishedAtDate"] = {"$regex": f"^{select_year}"}
        
    if select_place != 'All':
        query["placeId"] = select_place

    # Convert the collection_reviews (table) date to a pandas DataFrame with applied filter
    df = pd.DataFrame(list(collection_reviews.find(query, {
    "reviewId": 1,
    "placeId": 1,
    "title": 1,
    "categories": 1,
    "address": 1,
    "reviewerId": 1,
    "name": 1,
    "stars": 1,
    "text": 1,
    "publishedAtDate": 1,
    "Predict_rating": 1,
    })))
    
    # Drop the _id column generated automatically by Mongo
    df.drop('_id', axis=1, inplace=True)
    detail_table = [
            dash_table.DataTable(
                id='my-table',
                columns=[{
                    'name': x,
                    'id': x,
                } for x in df.columns],
                data=df.to_dict('records'),
                editable=True,
                row_deletable=True,
                filter_action="native",
                filter_options={"case": "sensitive"},
                sort_action="native",  # give user capability to sort columns
                sort_mode="single",  # sort across 'multi' or 'single' columns
                page_current=0,  # page number that user is on
                page_size=10,  # number of rows visible per page
                style_table={'height': '400px'},
                style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'},
                style_header={
                    'backgroundColor': '#043296',
                    'fontWeight': 'bold',
                    'color': 'white',
                    'textAlign': 'center'
                },
            )
        ]
    
    # Đếm số lượng đánh giá (ratings), số lượng bình luận (reviews), số lượng địa điểm (places) và số lượng người dùng (users)
    ratings = collection_reviews.count_documents(query)
    users = len(collection_reviews.distinct("reviewerId", query))

    # Draw graph
    statistics_df = calculate_reviews_dashboard(df)
    fig_bar = draw_chart_reviews_dashboard(statistics_df)

    fig_pie = draw_chart_reviews_by_star_dashboard(df)
    
    return [detail_table, ratings, users, fig_bar, fig_pie]

########## END OF DASHBOARD ################################################################################

# Add new rows to DataTable ***********************************************
@app.callback(
    Output('my-table', 'data'),
    [Input('adding-rows-btn', 'n_clicks')],
    [State('my-table', 'data'),
     State('my-table', 'columns')],
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


# Save new DataTable data to the Mongo database ***************************
@app.callback(
    Output("placeholder", "children"),
    Input("save-it", "n_clicks"),
    State("my-table", "data"),
    prevent_initial_call=True
)
def save_data(n_clicks, data):
    dff = pd.DataFrame(data)
    collection_reviews.delete_many({})
    collection_reviews.insert_many(dff.to_dict('records'))
    return ""

########## BEGIN OF RECOMENDED SYSTEM ################################################################################
# Callback để động cập nhật danh sách tùy chọn của dropdown PlaceID dựa trên giá trị được chọn trong dropdown placename
@app.callback(
    Output('dropdown-idplace', 'options'),
    Input('dropdown-placename', 'value')
)
def update_idplace_options(selected_place_name):
    # Lấy lại danh sách tên địa điểm và ID địa điểm từ MongoDB (có thể cần cập nhật nếu dữ liệu thay đổi)
    place_data = collectionkha.find({"title": selected_place_name}, {"placeId": 1})
    updated_place_ids = [place["placeId"] for place in place_data]

    # Tạo danh sách tùy chọn mới cho dropdown PlaceID
    dropdown_options = [{'label': place_id, 'value': place_id} for place_id in updated_place_ids]

    return dropdown_options

@app.callback(
    Output('result-store', 'data'),
    [Input('button-get-value', 'n_clicks'),
     Input('dropdown-idplace', 'value')],
)

def update_data_recommend(n_clicks, input_value):
    if n_clicks > 0:
        data_updated = recommendation(input_value)
        return data_updated
    else:
        return df_result.to_dict('records')

@app.callback(
    Output('table_result', 'data'),
    [Input('result-store', 'data')]
)
def update_table(data):
    return data

@app.callback(
    Output('map-result', 'figure'),
    [Input('button-get-value', 'n_clicks')],
    [Input('table_result', 'data')]
)
def update_map_recommendation(n_clicks, data):
    fig = update_map(n_clicks,data)
    return fig

# Define callback to update links when table_result changes
@app.callback(
    Output('link-container', 'children'),
    [Input('table_result', 'data')]
)
def update_links(data):
    # Extract the 'url' column from the table data
    urls = [row.get('url', '') for row in data]
    links = [html.A(href=url, target='_blank', children="Xem", className='button2') for url in urls]
    return links

########## END OF RECOMENDED SYSTEM ################################################################################

########## BEGIN OF SENTIMENTS ################################################################################
@app.callback([Output('sentiment-positive-chart', 'figure'),
               Output('sentiment-negative-chart', 'figure')],
              [Input('year-sentiment-dropdown', 'value'),
               Input('place-sentiment-dropdown', 'value')])

def update_sentiments(select_year='All', select_place='All'):
    # Khởi tạo danh sách rỗng cho sentences và sentiment
    sentences = []
    sentiment = []
    query = {}

    if select_year != 'All':
        query["publishedAtDate"] = {"$regex": f"^{select_year}"}
        
    if select_place != 'All':
        query["placeId"] = select_place

    data_from_mongo = collection_reviews.find(query, {"sentences": 1, "sentiment": 1})

    for data in data_from_mongo:
        sentences.extend(data["sentences"])  # Sử dụng extend để thêm tất cả các phần tử của list vào danh sách sentences
        sentiment.extend(data["sentiment"])

    # Lọc các câu có sentiment là "negative"
    negative_sentences = [sentences[i] for i in range(len(sentences)) if sentiment[i] == "negative"]
    positive_sentences = [sentences[i] for i in range(len(sentences)) if sentiment[i] == "positive"]

    # Tiền xử lý văn bản
    cleaned_negative_sentences = [' '.join(simple_preprocess(sentence, min_len=2, max_len=15)) for sentence in negative_sentences]
    cleaned_positive_sentences = [' '.join(simple_preprocess(sentence, min_len=2, max_len=15)) for sentence in positive_sentences]


    fig_negative = create_fig_sentiments(cleaned_negative_sentences, 'lightsalmon')
    fig_positive = create_fig_sentiments(cleaned_positive_sentences, 'lightsalmon')

    return [fig_positive, fig_negative]
########## BEGIN OF SENTIMENTS ################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)
