from dash import Dash, html, dcc, callback, Output, Input, State
from dash import dash_table
import ast
import plotly.express as px
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv


# Sử dụng mã màu: aqua "#04fffe", blue "#043296", red "#ff0000"
# Tạo DataFrame chứa thông tin sinh viên
dataSV = {
    'STT': [1, 2, 3, 4],
    'Tên': ['Đặng Huỳnh Vĩnh Tân', 'Nguyễn Thị Hồng Nhung', 'Nguyễn Viết Kha', 'Nguyễn Huy Hoàng'],
    'MSSV': [21520442, 21522436, 21520949, 21522093]
}
dfSV = pd.DataFrame(dataSV)

df = pd.read_csv('df_ca.csv')
df_result = pd.read_csv('result.csv')
df_placename = pd.read_csv('placename.csv')


years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

# Ép cột 'reviewTime' thành kiểu datetime
df['reviewTime'] = pd.to_datetime(df['reviewTime'])

# Thêm kiểu CSS tổng quát cho phần body
external_stylesheets = ['general.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
            html.H3(children='BÁO CÁO ĐỒ ÁN CUỐI KỲ', className="app-header",),
            html.H1(children='Tên đề tài', className="app-header",),
            html.H4(children='Môn học: IE212.O11 - Công nghệ dữ liệu lớn', className="app-header",),
            html.H4(children='GVHD: TS. Đỗ Trọng Hợp', className="app-header",),
            html.H4(children='Nhóm sinh viên thực hiện: Group 7', className="app-header",),
            # dash_table.DataTable(
            #     id='SV_info',
            #     columns=[{'name': col, 'id': col} for col in dfSV.columns],
            #     data=dfSV.to_dict('records'),
            #     style_table={'width': '500px', 'height': '300px', 'overflowY': 'auto', 'margin': 'auto'},
            #     style_header={
            #         'backgroundColor': '#043296',
            #         'fontWeight': 'bold',
            #         'color': 'white',
            #         'textAlign': 'center'
            #     },
            # ),
        ], className="app-header-container"),

    html.Div([
        # dash_table.DataTable(
        #     id='table',
        #     columns=[{'name': col, 'id': col} for col in df.columns],
        #     data=df.to_dict('records'),
        #     page_size=10,
        #     style_table={'height': '400px'},
        #     style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'},
        #     style_header={
        #         'backgroundColor': '#043296',
        #         'fontWeight': 'bold',
        #         'color': 'white',
        #         'textAlign': 'center'
        #     },
        # ),
        html.Br(),
        html.Div([
            html.Label('Year'),
            dcc.Dropdown(
                options=[{'label': str(year), 'value': year} for year in ['All'] + years],
                value='All',
                id='dropdown-year',
                style={'width': '250px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Categories'),
            dcc.Dropdown(
                options=[{'label': categories, 'value': categories} for categories in ['All'] + df['categories'].unique().tolist()],
                value='All',
                id='dropdown-categories',
                style={'width': '350px', 'padding': '0 15px'}
            ),
        ], style={'display': 'inline-block'}),
        dcc.Graph(id='graph-content'),
        html.H1("Map with all data"),
        dcc.Graph(id='map-content'),
        html.H1("Find Nearest Station"),
        html.Div(id='output-value'),
        html.Div([
            html.Label('Place Name'),
            dcc.Dropdown(
                options=[{'label': placename, 'value': placename} for placename in ['All'] + df_placename['placename'].tolist()],
                value='All',
                id='dropdown-placename',
                style={'width': '350px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),
        html.Div([
            html.Label('ID Place', style={'margin-right': '10px'}),
            dcc.Dropdown(
                options=[{'label': idplace, 'value': idplace} for idplace in ['All'] + df_placename['gPlusPlaceId'].tolist()],
                value='All',
                id='dropdown-idplace',
                style={'width': '350px', 'padding': '0 0px', 'margin-right': '20px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),
        html.Div([
            html.Button("Search", id='button-get-value', n_clicks=0,
                        style={'font-size': '18px', 'border': '2px solid blue', 'padding': '5px 10px',
                               'background-color': 'blue', 'color': 'white', 'display': 'inline-block',
                               'border-radius': '5px'}),
        ], style={'margin-right': '20px', 'margin-top': '10px', 'text-align': 'center'}),

        html.Br(),
        # html.Div([
        #     dash_table.DataTable(
        #         id='table_result',
        #         columns=[{'name': col, 'id': col} for col in df_result.columns],
        #         data=df_result.to_dict('records'),
        #         page_size=10,
        #         style_table={'height': '400px'},
        #         style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis',
        #                     'whiteSpace': 'nowrap'},
        #         style_header={
        #             'backgroundColor': '#043296',
        #             'fontWeight': 'bold',
        #             'color': 'white',
        #             'textAlign': 'center'
        #         },
        #     ),
        # ]),
        # html.Div([
        #     dcc.Graph(id='map-result')
        # ]
        # ),
        html.Div([
            html.Div([
                dcc.Graph(id='map-result', config={'displayModeBar': False})
            ], className='six columns', style={'margin-bottom': '20px'}),
            # Điều chỉnh kích thước bản đồ

            html.Div([
                dash_table.DataTable(
                    id='table_result',
                    columns=[{'name': col, 'id': col} for col in df_result.columns],
                    data=df_result.to_dict('records'),
                    page_size=10,
                    style_table={'height': '200px'},
                    style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis',
                                'whiteSpace': 'nowrap'},
                    style_header={
                        'backgroundColor': '#043296',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'textAlign': 'center'
                    },
                )
            ], className='six columns')
            # Điều chỉnh kích thước DataTable và đặt marginTop

        ], className='row', style={'marginBottom': '20px'}),
        dcc.Store(id='result-store', data=df_result.to_dict('records'))
    ], className='main-container')
], className='container')
@app.callback(
    Output('dropdown-idplace', 'value'),
    [Input('dropdown-placename', 'value')]
)
def update_idplace(value_name):
    if value_name == 'All':
        idplace = ['All'] + df_placename['gPlusPlaceId'].tolist()
    else:
        filter_idplace = df_placename[df_placename['placename'] == value_name]['gPlusPlaceId'].tolist()
        if len(filter_idplace) > 0:
            idplace = filter_idplace[0]
        else:
            idplace = 'All'
    return idplace



@app.callback(
    Output('dropdown-categories', 'options'),
    [Input('dropdown-year', 'value')]
)
def update_categories_options(value_year):
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



@app.callback(
    [Output('graph-content', 'figure'),
     Output('map-content', 'figure')],
    [Input('dropdown-year', 'value'),
     Input('dropdown-categories', 'value')]
)
def update_graph(value_year, value_categories):
    title = 'Số lượng đánh giá'

    dff = df.copy()  # Tạo một bản sao của DataFrame ban đầu

    if value_year != 'All':
        dff = dff[dff['reviewTime'].dt.year == value_year]
        title += f' theo năm {value_year}'

    if value_categories != 'All':
        dff = dff[dff['categories'] == value_categories]

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
                                   text='gPlusPlaceId',
                                   mapbox_style='carto-positron',
                                   color_discrete_sequence=['#ff0000'])

    map_figure.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=4
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return histogram_figure, map_figure


def find_name(place_id):
    input_file_path = './place_name_dict/place_name_dict.pkl'
    # Đọc place_name_dict từ tệp
    with open(input_file_path, 'rb') as file:
        place_name_dict = pickle.load(file)
    place_name = place_name_dict.get(place_id)
    return place_name


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

def recommendation(placeid):
    data = df
    # Get the categories, ratings, reviewer names, and GPS columns
    categories = data['categories'].tolist()
    ratings = data['rating'].tolist()
    reviewer_names = data['reviewerName'].tolist()
    gps = data['gps'].tolist()
    gPlusPlaceId = data['gPlusPlaceId'].tolist()
    input_gplus_place_id = placeid

    # Tìm danh mục (category) tương ứng với input_gplus_place_id
    filtered_data = data[data['gPlusPlaceId'] == input_gplus_place_id]
    index_input = filtered_data.index.tolist()[0]
    input_category = filtered_data['categories'].iloc[0]
    rating_input = filtered_data['rating'].iloc[0]
    reviewername_input = filtered_data['reviewerName'].iloc[0]
    Gps_input = filtered_data['gps'].iloc[0]
    Place_name_input = find_name(input_gplus_place_id)

    if input_category:
        # Find similar categories and their indices, along with sorted ratings
        similar_category_indices, sorted_ratings = find_similar_categories(input_category, categories, ratings,
                                                                           reviewer_names, gps)
        # Print and write the similar categories, indices, ratings, reviewer names, and GPS values in the desired format
        print("Indices, Similar Categories, Ratings, Reviewer Names, GPS, Place_ID and Name:")
        with open('result.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Index', 'Category', 'Rating', 'Reviewer Name', 'GPS', 'Place_ID', 'Place Name'])
            writer.writerow(
                [index_input, input_category, rating_input, reviewername_input, Gps_input, input_gplus_place_id,
                 Place_name_input])
            for index, rating, reviewer_name, gps_value in sorted_ratings[:5]:
                category = categories[index]
                gplus_place_id = gPlusPlaceId[index]
                place_name = find_name(gplus_place_id)
                writer.writerow([index, category, rating, reviewer_name, gps_value, gplus_place_id, place_name])
                print(f"{index:5}  {category:60} {rating:<5} {reviewer_name} {gps_value} {gplus_place_id} {place_name}")

            file.close()
    else:
        print("Không tìm thấy gPlusPlaceId trong dữ liệu.")

    df_result_updated = pd.read_csv('result.csv')
    data_updated = df_result_updated.to_dict('records')
    return data_updated
# @app.callback(
#     Output('output-value', 'children'),
#     [Input('button-get-value', 'n_clicks'),
#      Input('dropdown-idplace', 'value')],
# )
# def get_input_placeid(n_clicks, input_value):
#     if n_clicks > 0:
#         print("Xin vui lòng đợi...")
#         data_updated = recommendation(input_value)
#         return 'Success!'
#     else:
#         return 'Xin nhập giá trị'
#

@app.callback(
    Output('table_result', 'data'),
    [Input('result-store', 'data')]
)
def update_table(data):
    return data

@app.callback(
    Output('result-store', 'data'),
    [Input('button-get-value', 'n_clicks'),
     Input('dropdown-idplace', 'value')],
)
def update_data(n_clicks, input_value):
    if n_clicks > 0:
        print("Xin vui lòng đợi...")
        data_updated = recommendation(input_value)
        print("Success")
        return data_updated
    else:
        return df_result.to_dict('records')

@app.callback(
    Output('map-result', 'figure'),
    [Input('button-get-value', 'n_clicks')],
    [Input('table_result', 'data')]
)
def update_map(n_clicks, data):
    # Đọc dữ liệu từ DataFrame df_result (giả sử cột GPS và Place Name chứa thông tin vị trí và tên địa điểm)
    df_result = pd.DataFrame(data).copy()
    gps_data = df_result['GPS']
    place_name_data = df_result['Place Name']

    # Tạo DataFrame mới chứa thông tin vị trí và tên địa điểm
    df_location = pd.DataFrame({'GPS': gps_data, 'Place Name': place_name_data})

    # Chia cột GPS thành cột Latitude và Longitude
    df_location[['Latitude', 'Longitude']] = df_location['GPS'].str.extract('\[(.*?),\s(.*?)\]', expand=True)

    # Chuyển đổi cột 'Longitude' và 'Latitude' sang kiểu dữ liệu số
    df_location['Longitude'] = pd.to_numeric(df_location['Longitude'])
    df_location['Latitude'] = pd.to_numeric(df_location['Latitude'])

    # Tạo cột 'Color' để xác định màu sắc cho các điểm
    df_location['Color'] = '#ff0000'  # Mặc định là màu đỏ cho tất cả các điểm
    df_location.loc[0, 'Color'] = '#00ff00'  # Điểm đầu tiên có màu xanh

    # Vẽ bản đồ bằng px.scatter_mapbox
    fig = px.scatter_mapbox(
        df_location,
        lat="Latitude",
        lon="Longitude",
        text="Place Name",
        mapbox_style='carto-positron',
        color="Color"  # Sử dụng cột 'Color' để xác định màu sắc
    )

    # Cấu hình layout cho bản đồ
    fig.update_layout(
        mapbox=dict(
            style='carto-positron',
            zoom=4
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
