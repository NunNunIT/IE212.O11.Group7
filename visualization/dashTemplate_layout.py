from dash import Dash, html, dcc, callback, Output, Input, State
from dash import dash_table
import ast
import plotly.express as px
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv

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

df_result = pd.read_csv('result.csv',encoding='latin-1')
def create_dashtable_result():
    df_result_filtered = df_result.drop(columns=["Index", "Place_ID"])
    df_result_filtered = df_result_filtered.drop(df_result_filtered.index[0])
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
    df2['gps'] = dff['gps'].apply(lambda x: ast.literal_eval(x))
    df2['lat'] = df2['gps'].apply(lambda x: x[0])
    df2['lon'] = df2['gps'].apply(lambda x: x[1])
    df2 = df2.drop(columns=['gps'])

    map_figure = px.scatter_mapbox(df2,
                                   lat='lat',
                                   lon='lon',
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

def find_similar_categories(input_category, categories, ratings, reviewer_names, gps):
    # Combine the input category, categories, ratings, and reviewer names into a list
    all_categories = [(input_category, 1.0, "", "")] + list(zip(categories, ratings, reviewer_names, gps))

    # Create a TfidfVectorizer
    vectorizer = TfidfVectorizer()

    # Transform the categories into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform([category for category, _, _, _ in all_categories])

    # Calculate the cosine similarity between the input category and all other categories
    similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])

    # Get the indices of the most similar categories
    most_similar_indices = similarity_scores.argsort()[0][::-1]

    # Sort the ratings and GPS based on the category indices
    sorted_ratings = sorted(zip(most_similar_indices, ratings, reviewer_names, gps), key=lambda x: x[1], reverse=True)

    unique_gps = set()
    unique_sorted_ratings = []

    # Filter out duplicate GPS values
    for index, rating, reviewer_name, gps_value in sorted_ratings:
        if gps_value not in unique_gps:
            unique_gps.add(gps_value)
            unique_sorted_ratings.append((index, rating, reviewer_name, gps_value))

    return most_similar_indices[:5], unique_sorted_ratings


# df = pd.read_csv('Predict.csv')
df = pd.read_csv('Predict.csv')

average_ratings = df.groupby('gPlusPlaceId')['average_rating'].mean().reset_index()
merged_data = pd.merge(average_ratings, df[['gPlusPlaceId', 'gps', 'categories', 'name']], on='gPlusPlaceId', how='left')
df1 = merged_data.drop_duplicates(subset='gPlusPlaceId', keep='first')
def recommendation(placeid):
    data = df1
    # Get the categories, ratings, reviewer names, and GPS columns
    categories = data['categories'].tolist()
    ratings = data['average_rating'].tolist()
    reviewer_names = data['name'].tolist()
    gps = data['gps'].tolist()
    gPlusPlaceId = data['gPlusPlaceId'].tolist()
    input_gplus_place_id = placeid

    # Tìm danh mục (category) tương ứng với input_gplus_place_id
    filtered_data = data[data['gPlusPlaceId'] == input_gplus_place_id]
    index_input = filtered_data.index.tolist()[0]
    input_category = filtered_data['categories'].iloc[0]
    rating_input = filtered_data['average_rating'].iloc[0]
    reviewername_input = filtered_data['name'].iloc[0]
    Gps_input = filtered_data['gps'].iloc[0]

    if input_category:
        # Find similar categories and their indices, along with sorted ratings
        similar_category_indices, sorted_ratings = find_similar_categories(input_category, categories, ratings,
                                                                           reviewer_names, gps)
        # Print and write the similar categories, indices, ratings, reviewer names, and GPS values in the desired format
        print("Indices, Similar Categories, Ratings, Reviewer Names, GPS, Place_ID and Name:")
        with open('result.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Index', 'Category', 'Rating', 'Place Name', 'GPS', 'Place_ID'])
            writer.writerow(
                [index_input, input_category, rating_input, reviewername_input, Gps_input, input_gplus_place_id])
            for index, rating, reviewer_name, gps_value in sorted_ratings[:5]:
                category = categories[index]
                gplus_place_id = gPlusPlaceId[index]
                writer.writerow([index, category, rating, reviewer_name, gps_value, gplus_place_id])
                print(f"{index:5}  {category:60} {rating:<5} {reviewer_name} {gps_value} {gplus_place_id} ")

            file.close()
    else:
        print("Không tìm thấy gPlusPlaceId trong dữ liệu.")

    df_result_updated = pd.read_csv('result.csv')
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
    gps_data = df_result['GPS']
    place_name_data = df_result['Place Name']
    df_location = pd.DataFrame({'GPS': gps_data, 'Place Name': place_name_data})
    # Chia cột GPS thành cột Latitude và Longitude
    df_location[['Latitude', 'Longitude']] = df_location['GPS'].str.extract('\[(.*?),\s(.*?)\]', expand=True)
    # Chuyển đổi cột 'Longitude' và 'Latitude' sang kiểu dữ liệu số
    df_location['Longitude'] = pd.to_numeric(df_location['Longitude'])
    df_location['Latitude'] = pd.to_numeric(df_location['Latitude'])
    # Tạo cột 'Color' để xác định màu sắc cho các điểm
    df_location['Color'] = 'others'  # Mặc định là màu đỏ cho tất cả các điểm
    df_location.loc[0, 'Color'] = 'target'  # Điểm đầu tiên có màu xanh
    # Định nghĩa bản đồ màu sắc
    color_discrete_map = {'target': '#f86134', 'others': '#002f72'}
    # Vẽ bản đồ bằng px.scatter_mapbox
    fig = px.scatter_mapbox(
        df_location,
        lat="Latitude",
        lon="Longitude",
        text="Place Name",
        mapbox_style='carto-positron',
        hover_data={'Place Name': True},
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