from dash import Dash, html, dcc, callback, Output, Input, State
from dash import dash_table
import plotly.express as px
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import haversine_distances
from math import radians
from haversine import haversine, Unit
from pymongo import MongoClient

# Connect to local server
client = MongoClient("mongodb://127.0.0.1:27017/")
# Create database called animals
mydbkha = client["ie212_o11_group7"]
# Create Collectionkha (table) called shelterA
collectionkha = mydbkha.places
# Lấy danh sách tên địa điểm và ID địa điểm từ MongoDB
place_data = collectionkha.find({}, {"title": 1, "placeId": 1})
place_names = [place["title"] for place in place_data]
place_ids = [place["placeId"] for place in place_data]


df_result = pd.read_csv('result_HCM1.csv',encoding='utf-8')

def create_PlaceName_PlaceID_Dropdown():
    return html.Div([
            html.Div([
                html.Label('Place Name'),
                dcc.Dropdown(
                    id='dropdown-placename',
                    options=[{'label': place_name, 'value': place_name} for place_name in place_names],
                    value='All',
                ),
                ], className='dropdown-item'),
            html.Div([
                html.Label('ID Place'),
                dcc.Dropdown(
                    id='dropdown-idplace',
                    options=[{'label': place_id, 'value': place_id} for place_id in place_ids],
                    value='All',
                ),
            ], className='dropdown-item')
        ], className='contain-layout')
def create_dashtable_result():
    df_result_filtered = df_result.drop(columns=["gPlusPlaceId", "url"])
    df_result_filtered = df_result_filtered.drop(df_result_filtered.index[0])

    # Tạo một danh sách chứa thẻ <a> tương ứng với từng giá trị trong cột 'url'
    links = [html.A(href=url, target='_blank', children="Xem", className='button2') for url in df_result['url']]

    return html.Div([
        html.Div([
            dcc.Graph(id='map-result', config={'displayModeBar': False})
        ]),
        html.Div([
            dash_table.DataTable(
                id='table_result',
                columns=[
                    {'name': col, 'id': col} for col in df_result_filtered.columns
                ],
                data=df_result_filtered.to_dict('records'),
                style_table={'height': '400px', 'width': '100%', 'minWidth': '100%'},
                style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis',
                            'whiteSpace': 'nowrap'},
                style_header={
                    'backgroundColor': '#043296',
                    'fontWeight': 'bold',
                    'color': 'white',
                    'textAlign': 'center'
                },
            ),
            html.Div(links, id='link-container', className="link-container1"),
        ], className='contain-layout2'),
    ], className='contain-layout')
def create_SearchButton_layout():
    return html.Div([
            html.Button("Search", id='button-get-value', n_clicks=0,
                        style={'font-size': '18px', 'border': '2px solid #015fc2', 'padding': '5px 10px',
                               'background-color': '#015fc2', 'color': 'white', 'display': 'inline-block',
                               'border-radius': '5px', 'padding': '10px'}),
        ], style={'margin-right': '20px', 'margin-top': '10px', 'text-align': 'center'})



def update_graph(df):
    title = 'Number of reviews'
    dff = df.copy()
    histogram_figure = px.histogram(dff, x='rating', title=title,
                                    labels={'x': 'Rating', 'y': 'Số lượng đánh giá'},
                                    color_discrete_sequence=['#043296'],
                                    category_orders=dict(rating=["1", "2", "3", "4", "5"]))
    df2 = dff.copy()

    map_figure = px.scatter_mapbox(df2,
                                   lat='location/lat',
                                   lon='location/lng',
                                   text='name',
                                   mapbox_style='carto-positron',
                                   color_discrete_sequence=['#002f72'])
    map_figure.update_traces(
        marker=dict(
            size=10
        ),
        textposition='top center'
    )
    map_figure.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=4
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return histogram_figure, map_figure

# Đọc dữ liệu từ MongoDB và xây dựng mô hình ở đây
cursor = collectionkha.find({})
data = pd.DataFrame(list(cursor))

# Tiền xử lý dữ liệu
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data['categories'].fillna(''))

# Xây dựng mô hình
model = NearestNeighbors(n_neighbors=6, algorithm='ball_tree')
model.fit(tfidf_matrix)

# Hàm khuyến nghị
def recommend(gPlusPlaceId, num_recommendations=10):
    # Lấy thông tin từ dataset dựa trên gPlusPlaceId
    user_info = data[data['placeId'] == gPlusPlaceId][['title', 'categories', 'average_predict_rating', 'location/lat',
                                                          'location/lng', 'placeId','url']]

    # Lấy vị trí từ dataset dựa trên gPlusPlaceId
    input_lat = data[data['placeId'] == gPlusPlaceId]['location/lat'].iloc[0]
    input_lng = data[data['placeId'] == gPlusPlaceId]['location/lng'].iloc[0]

    input_coords = [input_lat, input_lng]

    idx = data[data['placeId'] == gPlusPlaceId].index[0]
    distances, indices = model.kneighbors(tfidf_matrix[idx], n_neighbors=num_recommendations+1)  # +1 để bao gồm chính điểm đầu tiên
    recommended_places = data.loc[indices[0][1:]]

    # Kiểm tra khoảng cách giữa vị trí nhập vào và vị trí của các địa điểm được khuyến nghị
    input_coords_radians = [radians(coord) for coord in input_coords]
    recommended_places['distance'] = recommended_places.apply(
        lambda row: haversine(input_coords_radians, [radians(row['location/lat']), radians(row['location/lng'])],
                              unit=Unit.KILOMETERS), axis=1)
    recommended_places = recommended_places.sort_values(by='distance').drop(columns=['distance'])

    # Loại bỏ gPlusPlaceId nhập vào khỏi danh sách khuyến nghị
    recommended_places = recommended_places[recommended_places['placeId'] != gPlusPlaceId]

    # Sắp xếp theo average_rating giảm dần
    recommended_places = recommended_places.sort_values(by='average_predict_rating', ascending=False)

    # Chỉ lấy num_recommendations đầu tiên
    recommended_places = recommended_places.head(num_recommendations)

    return user_info, recommended_places[['title','categories','average_predict_rating','location/lat','location/lng','placeId','url']]
# average_ratings = df.groupby('gPlusPlaceId')['average_predict_rating'].mean().reset_index()
# merged_data = pd.merge(average_ratings, df[['gPlusPlaceId', 'gps', 'categories', 'name']], on='gPlusPlaceId', how='left')
# df1 = merged_data.drop_duplicates(subset='gPlusPlaceId', keep='first')

def recommendation(placeid):
    user_info, result = recommend(placeid, num_recommendations=10)
    # Ghi thông tin của user_input và kết quả vào cùng một tệp CSV
    with open('result_HCM1.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # Ghi header
        writer.writerow(['name', 'categories', 'average_predict_rating', 'location/lat', 'location/lng', 'gPlusPlaceId','url'])

        # Ghi user_info vào tệp
        writer.writerow(user_info.values.flatten())

        # Ghi result vào tệp
        result.to_csv(file, header=False, index=False)
    df_result_updated = pd.read_csv('result_HCM1.csv')
    data_updated = df_result_updated.to_dict('records')
    return data_updated


def update_data(df_result,n_clicks, input_value):
    if n_clicks > 0:
        print("Xin vui lòng đợi...")
        data_updated = recommendation(input_value)
        print("Success")
        return data_updated
    else:
        return df_result.to_dict('records')
def update_map(n_clicks, data):
    df_result = pd.DataFrame(data).copy()
    # Tạo cột 'Color' để xác định màu sắc cho các điểm
    df_result['Color'] = 'others'  # Mặc định là màu đỏ cho tất cả các điểm
    df_result.loc[0, 'Color'] = 'target'  # Điểm đầu tiên có màu xanh
    # Định nghĩa bản đồ màu sắc
    color_discrete_map = {'target': '#f86134', 'others': '#002f72'}
    # Vẽ bản đồ bằng px.scatter_mapbox
    fig = px.scatter_mapbox(
        df_result,
        lat="location/lat",
        lon="location/lng",
        text="name",
        mapbox_style='carto-positron',
        hover_data={'name': True},
        color="Color",  # Sử dụng cột 'Color' để xác định màu sắc
        color_discrete_map=color_discrete_map  # Bản đồ màu sắc
    )
    # Cấu hình layout cho bản đồ
    fig.update_traces(
        marker=dict(
            size=10
        ),
        textposition='top center'
    )
    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=4
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig