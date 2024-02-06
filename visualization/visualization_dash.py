from dash import Dash, html, dcc, callback, Output, Input
from dash_core_components import Interval
from dash import dash_table
import requests
import pandas as pd
from dashboarb_layout import *
# from dashTemplate_layout import *
from functools import partial
# from model_component import *
# from sentiment_layout import *
from pymongo import MongoClient

# Đường dẫn của API
api_url = 'http://127.0.0.1:5000/api/ie212_o11_group7/endpoint'

# Kết nối đến MongoDB
# Connect to local server
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client.ie212_o11_group7
db = client["ie212_o11_group7"]
collection = db.reviews_thpcm_tan

def update_dataframe2():
    # Lấy dữ liệu từ MongoDB và chuyển đổi thành DataFrame
    # data_from_mongo = list(collection.find())
    df = pd.DataFrame(list(collection.find()))
    # df = pd.DataFrame(data_from_mongo)

    df['publishedAtDate'] = pd.to_datetime(df['publishedAtDate'])
    df['year'] = df['publishedAtDate'].dt.year

    return df

# Khởi tạo Dash App
app = Dash(__name__)
dropdown_options = [{'label': 'All', 'value': 'All'}]
# Layout của Dash App
app.layout = html.Div([
    create_introduct_layout(),
    html.H1("Dashboard", className="centered-heading", id="see-here"),
    html.Div([
        create_dashboard_option_layout(),
        create_dashboard_total_layout(),
        html.Div(id='dashboarb-total'),
        html.Div([
                # dcc.Graph(id='dashboard-review-chart'),
                # dcc.Graph(id='dashboarb-fig-star'),
            ], className='contain-layout'),
        create_detail_table_layout(),
        # dcc.Graph(id='dashboard-map'),
        Interval(id='interval-component', interval=60*1000, n_intervals=0),  # Set interval to 5 seconds
    ], className="dashboard-container"),
    html.H1("Categories", className="centered-heading"),
    html.H1("Recomended System", className="centered-heading"),
    html.H1("Sentiment", className="centered-heading"),
], className='main-container')


# DASHBOARD
# # Callback để cập nhật dữ liệu từ API và cập nhật dropdown
# @app.callback(
#     [Output('year-dropdown', 'options'),
#      Output('place-dropdown', 'options'),],
#     [Input('interval-component', 'n_intervals')],
# )
# def update_dropdown(n_intervals):
#     updated_df = update_dataframe2()
#     print(updated_df)

#     dropdown_year_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(year) + str(' (') + str(updated_df[updated_df['year'] == year].shape[0]) + str(')'), 'value': year} for year in updated_df['year'].unique()]
#     dropdown_place_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(place) + str(' (') + str(updated_df[updated_df['placeId'] == place].shape[0]) + str(')'), 'value': place} for place in updated_df['placeId'].unique()]
#     return [dropdown_year_options, dropdown_place_options]  # Đặt danh sách trong dấu ngoặc vuông để trả về một danh sách


# Callback để cập nhật dữ liệu từ API và cập nhật Dash App
# @app.callback(
#     [Output('detail-table', 'columns'),
#      Output('detail-table', 'data')],
#     [Input('interval-component', 'n_intervals'),
#      Input('year-dropdown', 'value'),
#      Input('place-dropdown', 'value'),]
# )
@app.callback(
    [Output('detail-table', 'columns'),
     Output('detail-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)

def update_data_table(n_intervals):
    dff = update_dataframe2()
    # if select_year != 'All' or select_place != 'All':
        # dff = filter_by_selecttion(dff, select_year, select_place)
    print(dff)
    # Specify the columns you want to display
    # display_columns = [
    #     'rating',
    #     'reviewerName',
    #     'text',
    #     'categories',
    #     'gPlusPlaceId',
    #     'gps',
    #     'unixReviewTime',
    #     'reviewTime',
    #     'placeId',
    #     'last_update_time',
    # ]
    # columns = [{'name': col, 'id': col} for col in dff.columns]
    # Create a list of dictionaries for columns based on the display_columns
    # columns = [{'name': col, 'id': col} for col in display_columns]
    # data = dff.to_dict('records')

     # Lấy tên của tất cả các cột trong DataFrame
    all_columns = dff.columns.tolist()

    # Tạo danh sách dictionaries cho columns
    columns = [{'name': col, 'id': col} for col in all_columns]

    # Tạo data dưới dạng list của dictionaries
    data = dff.to_dict('records')
    return columns, data

# @app.callback(
#     [Output('total-ratings', 'children'),
#      Output('total-reviews', 'children'),
#      Output('total-places', 'children'),
#      Output('total-user', 'children')],
#     [Input('interval-component', 'n_intervals'),
#      Input('year-dropdown', 'value'),
#      Input('place-dropdown', 'value'),]
# )

# def update_total_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
#     # Prevent initial callback trigger and subsequent ones if no changes in dropdowns
#     df = update_dataframe2()
#     if select_year != 'All' or select_place != 'All':
#         df = filter_by_selecttion(df, select_year, select_place)

#     ratings = len(df)
#     reviews = df['text'].count()
#     places = len(df['placeId'].unique())
#     users = len(df['placeId'].unique())

#     return ratings, reviews, places, users

# @app.callback(
#         Output('dashboard-review-chart', 'figure'),
#         [Input('interval-component', 'n_intervals'),
#          Input('year-dropdown', 'value'),
#          Input('place-dropdown', 'value'),]
#     )

# def update_chart_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
#     df = update_dataframe2()
#     if select_year != 'All' or select_place != 'All':
#         df = filter_by_selecttion(df, select_year, select_place)

#     statistics_df = calculate_reviews_dashboarb(df)
#     fig = draw_chart_reviews_dashboard(statistics_df)
#     return fig

# @app.callback(
#         Output('dashboarb-fig-star', 'figure'),
#         [Input('interval-component', 'n_intervals'),
#          Input('year-dropdown', 'value'),
#          Input('place-dropdown', 'value'),]
#     )

# def update_chart_star_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
#     df = update_dataframe2()
#     if select_year != 'All' or select_place != 'All':
#         df = filter_by_selecttion(df, select_year, select_place)

#     fig = draw_chart_reviews_by_star_dashboard(df)
#     return fig

############## END OF DASHBOARB #################################################################

############# BEGIN OF CATEGORIES ###############################################################
############# END OF CATEGORIES #################################################################

############# BEGIN OF RECOMENDED SYSTEM ###############################################################
############# END OF RECOMENDED SYSTEM #################################################################

############# BEGIN OF SENTIMENT SYSTEM ###############################################################
############# END OF SENTIMENT SYSTEM #################################################################


# Khởi chạy Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True, dev_tools_hot_reload_timeout=120)

