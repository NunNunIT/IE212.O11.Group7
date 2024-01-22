from dash import Dash, html, dcc, callback, Output, Input
from dash_core_components import Interval
from dash import dash_table
import requests
import pandas as pd
from dashboarb_layout import *
from data_utils import *

# Đường dẫn của API
api_url = 'http://127.0.0.1:5000/api/ie212_o11_group7/endpoint'

# Dữ liệu ban đầu
initial_data = pd.DataFrame()

# Hàm để lấy dữ liệu từ API
def get_api_data():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error fetching data from API: {str(e)}")
        return None
    
# Khởi tạo biến global lưu thời gian cập nhật cuối cùng
last_update_time = 0

# Hàm để cập nhật DataFrame từ dữ liệu API
def update_dataframe():
    global last_update_time
    api_data = get_api_data()
    if api_data is not None:
        # Chuyển đổi cột 'categories' thành chuỗi
        api_data['categories'] = str(api_data['categories'])
        df_new = pd.DataFrame.from_dict([api_data])

        global initial_data  # Truy cập biến global initial_data

        update_time = df_new.iloc[0]['last_update_time']

        if update_time > last_update_time:
            last_update_time = update_time
            # Chuyển đổi cột gps thành 2 cột lat, longitude
            # lat_long = extract_lat_long(api_data['gps'])
            # df_new['latitude'] = lat_long['latitude']
            # df_new['longitude'] = lat_long['longitude']

            # Convert Unix timestamps to datetime objects
            df_new['review_date'] = pd.to_datetime(df_new['unixReviewTime'], unit='s')

            # Extract the year from the datetime objects and create a 'year' column
            df_new['year'] = df_new['review_date'].dt.year
            df_new['month'] = df_new['review_date'].dt.year

            initial_data = pd.concat([initial_data, df_new], ignore_index=True)

    return initial_data

# Khởi tạo Dash App
app = Dash(__name__)

# Layout của Dash App
app.layout = html.Div([
    html.Div([], className='introduct-heading'),
    html.H1("Dashboard", className="centered-heading"),
    html.Div([
        create_dashboard_option_layout(),
        create_dashboard_total_layout(),
        html.Div(id='dashboarb-total'),
        html.Div([
                dcc.Graph(id='dashboard-review-chart'),
                dcc.Graph(id='dashboarb-fig-star'),
            ], style={'columnCount': 2}),
        create_detail_table_layout(),
        dcc.Graph(id='dashboard-map'),
        Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Set interval to 5 seconds
    ], className="dashboard-container"),
    html.H1("Recomended System", className="centered-heading"),
    html.H1("Sentiment", className="centered-heading"),
], className='main-container')

# Callback để cập nhật dữ liệu từ API và cập nhật dropdown
@app.callback(
    [Output('year-dropdown', 'options'),
     Output('place-dropdown', 'options'),],
    [Input('interval-component', 'n_intervals')],
)
def update_dropdown_year(n_intervals):
    updated_df = update_dataframe()
    dropdown_year_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(year) + str(' (') + str(updated_df[updated_df['year'] == year].shape[0]) + str(')'), 'value': year} for year in updated_df['year'].unique()]
    dropdown_place_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(place) + str(' (') + str(updated_df[updated_df['gPlusPlaceId'] == place].shape[0]) + str(')'), 'value': place} for place in updated_df['gPlusPlaceId'].unique()]
    return [dropdown_year_options, dropdown_place_options]  # Đặt danh sách trong dấu ngoặc vuông để trả về một danh sách


# Callback để cập nhật dữ liệu từ API và cập nhật Dash App
@app.callback(
    [Output('detail-table', 'columns'),
     Output('detail-table', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('year-dropdown', 'value'),
     Input('place-dropdown', 'value'),]
)

def update_data_table(n_intervals, select_year = 'All', select_place = 'All'):
    dff = update_dataframe()
    if select_year != 'All' or select_place != 'All':
        dff = filter_by_selecttion(dff, select_year, select_place)
    # Specify the columns you want to display
    display_columns = [
        'rating',
        'reviewerName',
        'reviewText',
        'categories',
        'gPlusPlaceId',
        'unixReviewTime',
        'reviewTime',
        'gPlusUserId',
        'last_update_time'
    ]
    # columns = [{'name': col, 'id': col} for col in dff.columns]
    # Create a list of dictionaries for columns based on the display_columns
    columns = [{'name': col, 'id': col} for col in display_columns]
    data = dff[display_columns].to_dict('records')
    return columns, data

@app.callback(
    [Output('total-ratings', 'children'),
     Output('total-reviews', 'children'),
     Output('total-places', 'children'),
     Output('total-user', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('year-dropdown', 'value'),
     Input('place-dropdown', 'value'),]
)

def update_total_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
    # Prevent initial callback trigger and subsequent ones if no changes in dropdowns
    df = update_dataframe()
    if select_year != 'All' or select_place != 'All':
        df = filter_by_selecttion(df, select_year, select_place)

    ratings = len(df)
    reviews = df['reviewText'].count()
    places = len(df['gPlusPlaceId'].unique())
    users = len(df['gPlusUserId'].unique())

    return ratings, reviews, places, users

@app.callback(
        Output('dashboard-review-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('year-dropdown', 'value'),
         Input('place-dropdown', 'value'),]
    )

def update_chart_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
    df = update_dataframe()
    if select_year != 'All' or select_place != 'All':
        df = filter_by_selecttion(df, select_year, select_place)

    statistics_df = calculate_reviews_dashboarb(df)
    fig = draw_chart_reviews_dashboard(statistics_df)
    return fig

@app.callback(
        Output('dashboarb-fig-star', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('year-dropdown', 'value'),
         Input('place-dropdown', 'value'),]
    )

def update_chart_star_dashboarb(n_intervals, select_year = 'All', select_place = 'All'):
    df = update_dataframe()
    if select_year != 'All' or select_place != 'All':
        df = filter_by_selecttion(df, select_year, select_place)

    fig = draw_chart_reviews_by_star_dashboard(df)
    return fig




# Khởi chạy Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
