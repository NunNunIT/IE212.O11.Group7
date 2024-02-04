from dash import Dash, html, dcc, callback, Output, Input, State
from dash import dash_table
import ast
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



def create_Year_layout():
    return html.Div([
            html.Label('Year'),
            dcc.Dropdown(
                value='All',
                id='dropdown-year',
                placeholder='Chọn năm',
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'})

def create_Category_layout():
    return html.Div([
            html.Label('Categories'),
            dcc.Dropdown(
                value='All',
                id='dropdown-categories',
                placeholder='Category',
            ),
        ], style={'display': 'inline-block'})

def create_Placename_layout():
    return html.Div([
            html.Label('Place Name'),
            dcc.Dropdown(
                value='All',
                id='dropdown-placename',
            ),
        ], className='dropdown-item')

def create_IDPlace_layout():
    return html.Div([
            html.Label('ID Place'),
            dcc.Dropdown(
                value='All',
                id='dropdown-idplace',
            ),
        ], className='dropdown-item')

df_result = pd.read_csv('result_HCM1.csv',encoding='utf-8')
def create_dashtable_result():
    df_result_filtered = df_result.drop(columns=["gPlusPlaceId"])
    df_result_filtered = df_result_filtered.drop(df_result.index[0])
    print(df_result_filtered)
    return html.Div([
            html.Div([
                dcc.Graph(id='map-result', config={'displayModeBar': False})
            ]),
            # Điều chỉnh kích thước bản đồ
            html.Div([
                dash_table.DataTable(
                    id='table_result',
                    columns=[{'name': col, 'id': col} for col in df_result_filtered.columns],
                    data=df_result_filtered.to_dict('records'),
                    style_table={'height': '400px'},
                    style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis',
                                'whiteSpace': 'nowrap'},
                    style_header={
                        'backgroundColor': '#043296',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'textAlign': 'center'
                    },
                )
            ])
        ], className='contain-layout')

def create_SearchButton_layout():
    return html.Div([
            html.Button("Search", id='button-get-value', n_clicks=0,
                        style={'font-size': '18px', 'border': '2px solid #015fc2', 'padding': '5px 10px',
                               'background-color': '#015fc2', 'color': 'white', 'display': 'inline-block',
                               'border-radius': '5px', 'padding': '10px'}),
        ], style={'margin-right': '20px', 'margin-top': '10px', 'text-align': 'center'})
def update_idplace(df_placename, value_name):
    if value_name == 'All':
        idplace = ['All'] + df_placename['gPlusPlaceId'].tolist()
    else:
        filter_idplace = df_placename[df_placename['placename'] == value_name]['gPlusPlaceId'].tolist()
        if len(filter_idplace) > 0:
            idplace = filter_idplace[0]
        else:
            idplace = 'All'
    return idplace

def update_categories_options(df, value_year):
    if value_year == 'All':
        categories_string = ', '.join(df['categories'].tolist())
        categories_list = categories_string.replace("[", "").replace("]", "").replace("'", "").split(", ")
        unique_categories = list(set(categories_list))
        categories = ['All'] + unique_categories
    else:
        filtered_categories = df[df['reviewTime'].dt.year == int(value_year)]
        if len(filtered_categories) > 0:
            categories_string = ', '.join(filtered_categories['categories'].tolist())
            categories_list = categories_string.replace("[", "").replace("]", "").replace("'", "").split(", ")
            unique_categories = list(set(categories_list))
            categories = ['All'] + unique_categories
        else:
            categories = ['All']

    options = [{'label': category, 'value': category} for category in categories]

    return options


def filter_by_selecttion1(dateframe_input, value_year='All', value_categories='All'):
    filtered_df = dateframe_input.copy()
    if value_year != 'All' and value_categories != 'All':
        # Lọc DataFrame dựa trên cả hai điều kiện
        filtered_df = filtered_df[(filtered_df['year'] == value_year) & (filtered_df['categories'].str.contains(value_categories))]
    if value_year != 'All':
        filtered_df = filtered_df[filtered_df['year'] == value_year]
    elif value_categories != 'All':
        filtered_df = filtered_df[filtered_df['categories'].str.contains(value_categories)]

    return filtered_df
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
# Import file
input_file_path = './place_name_dict.pkl'
with open(input_file_path, 'rb') as file:
    place_name_dict = pickle.load(file)
#Create dictionary
dict_placename = {}
def find_name2(place_id):
    # Đọc place_name_dict từ tệp
    place_name = place_name_dict.get(place_id)
    dict_placename[place_name] = place_id
    return place_name
def find_placeid(place_name):
    place_id = None
    for key, value in dict_placename.items():
        if key == place_name:
            place_id = value
            break
    return place_id

# Đọc dữ liệu từ tệp CSV và xây dựng mô hình ở đây
data = pd.read_csv('rated_places_new.csv', encoding='utf-8')

# Tiền xử lý dữ liệu
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data['categories'].fillna(''))

# Xây dựng mô hình
model = NearestNeighbors(n_neighbors=6, algorithm='ball_tree')
model.fit(tfidf_matrix)
# Hàm khuyến nghị
def recommend(gPlusPlaceId):
    # Lấy thông tin từ dataset dựa trên gPlusPlaceId
    user_info = data[data['gPlusPlaceId'] == gPlusPlaceId][['name', 'categories', 'average_rating', 'location/lat',
                                                          'location/lng', 'gPlusPlaceId']]

    # Lấy vị trí từ dataset dựa trên gPlusPlaceId
    input_lat = data[data['gPlusPlaceId'] == gPlusPlaceId]['location/lat'].iloc[0]
    input_lng = data[data['gPlusPlaceId'] == gPlusPlaceId]['location/lng'].iloc[0]

    input_coords = [input_lat, input_lng]

    idx = data[data['gPlusPlaceId'] == gPlusPlaceId].index[0]
    distances, indices = model.kneighbors(tfidf_matrix[idx])
    recommended_places = data.loc[indices[0][1:]]

    # Kiểm tra khoảng cách giữa vị trí nhập vào và vị trí của các địa điểm được khuyến nghị
    input_coords_radians = [radians(coord) for coord in input_coords]
    recommended_places['distance'] = recommended_places.apply(
        lambda row: haversine(input_coords_radians, [radians(row['location/lat']), radians(row['location/lng'])],
                              unit=Unit.KILOMETERS), axis=1)
    recommended_places = recommended_places.sort_values(by='distance').drop(columns=['distance'])

    # Loại bỏ gPlusPlaceId nhập vào khỏi danh sách khuyến nghị
    recommended_places = recommended_places[recommended_places['gPlusPlaceId'] != gPlusPlaceId]

    # Sắp xếp theo average_rating giảm dần
    recommended_places = recommended_places.sort_values(by='average_rating', ascending=False)

    return user_info, recommended_places[['name','categories','average_rating','location/lat','location/lng','gPlusPlaceId']]

# average_ratings = df.groupby('gPlusPlaceId')['average_rating'].mean().reset_index()
# merged_data = pd.merge(average_ratings, df[['gPlusPlaceId', 'gps', 'categories', 'name']], on='gPlusPlaceId', how='left')
# df1 = merged_data.drop_duplicates(subset='gPlusPlaceId', keep='first')

def recommendation(placeid):
    df1 = data
    user_info, result = recommend(placeid)
    # Ghi thông tin của user_input và kết quả vào cùng một tệp CSV
    with open('result_HCM1.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # Ghi header
        writer.writerow(['name', 'categories', 'average_rating', 'location/lat', 'location/lng', 'gPlusPlaceId'])

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