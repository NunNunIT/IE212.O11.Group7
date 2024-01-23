from dash import Dash, html, dcc, callback, Output, Input
from dash_core_components import Interval
from dash import dash_table
import requests
import pandas as pd
from dashboarb_layout import *
from data_utils import *
from dashTemplate_layout import *
from functools import partial
from model_component import *
from sentiment_layout import *

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
        api_data['gps'] = str(api_data['gps'])
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
                dcc.Graph(id='dashboard-review-chart'),
                dcc.Graph(id='dashboarb-fig-star'),
            ], className='contain-layout'),
        create_detail_table_layout(),
        # dcc.Graph(id='dashboard-map'),
        Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Set interval to 5 seconds
    ], className="dashboard-container"),
    html.H1("Categories", className="centered-heading"),
    html.Div([
        html.Div([ 
            create_Year_layout(),
            create_Category_layout(),
        ], className='contain-layout'),
        html.Div([
            dcc.Graph(id='graph-content'),
            dcc.Graph(id='map-content'),
        ], className='contain-layout'),
    ], className="dashboard-container"),
    html.H1("Recomended System", className="centered-heading"),
    html.Div([
        html.Div([ 
            create_Placename_layout(),
            create_IDPlace_layout(),
        ], className='contain-layout'),
        create_SearchButton_layout(),
        html.Div([ 
            create_dashtable_result(),
            dcc.Store(id='result-store', data=df_result.to_dict('records')),
        ], className='contain-layout'),
    ], className="dashboard-container"),
    html.H1("Sentiment", className="centered-heading"),
    html.Div([
        create_update_counter_button_layout(),
        html.Div([
            create_sentiment_layout(1),
            create_sentiment_layout(2),
        ], className='contain-layout'),
    ], className='dashboard-container'),
], className='main-container')


# DASHBOARD
# Callback để cập nhật dữ liệu từ API và cập nhật dropdown
@app.callback(
    [Output('year-dropdown', 'options'),
     Output('place-dropdown', 'options'),],
    [Input('interval-component', 'n_intervals')],
)
def update_dropdown(n_intervals):
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
        'gps',
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


# CATEGORIES
@app.callback(
    [Output('dropdown-year', 'options')],
    [Input('interval-component', 'n_intervals')],
)
def update_dropdown_year2(n_intervals):
    updated_df = update_dataframe()
    dropdown_year_options = [{'label': 'All', 'value': 'All'}] + [{'label': str(year) + str(' (') + str(updated_df[updated_df['year'] == year].shape[0]) + str(')'), 'value': year} for year in updated_df['year'].unique()]
    return [dropdown_year_options]

@app.callback(
    [Output('dropdown-categories', 'options')],
    [Input('dropdown-year', 'value')],
)
def update_dropdown_categories(selected_year):
    updated_df = update_dataframe()
    filtered_df = updated_df[updated_df['year'] == selected_year] if selected_year != 'All' else updated_df

    # Split and get unique categories, excluding empty values
    categories = filtered_df['categories'].apply(
        lambda x: x.replace("[", "").replace("]", "").replace("'", "").split(", "))
    unique_categories = list(set(category for sublist in categories for category in sublist if category))

    dropdown_options = [{'label': 'All', 'value': 'All'}] + [{'label': category, 'value': category} for category in
                                                             unique_categories]
    return [dropdown_options]

@app.callback(
    [Output('graph-content', 'figure'),
        Output('map-content', 'figure')],
    [Input('interval-component', 'n_intervals'),
        Input('dropdown-year', 'value'),
        Input('dropdown-categories', 'value'),]
    )

def update_chart_categories_dashboarb(n_intervals, value_year = 'All', value_categories = 'All'):
    df = update_dataframe()
    if value_year != 'All' or value_categories != 'All':
        df = filter_by_selecttion1(df, value_year, value_categories)
    histogram_figure, map_figure = update_graph(df)
    return histogram_figure, map_figure

@app.callback(
    Output('dropdown-placename', 'options'),
    [Input('interval-component', 'n_intervals')],
)
def update_placename(n_intervals):
    updated_df = update_dataframe()
    options = updated_df['gPlusPlaceId'].unique().tolist()
    options = [{'label': 'All', 'value': 'All'}] + [{'label': find_name2(place_id), 'value': find_name2(place_id)} for place_id in options]
    return options

@app.callback(
    [Output('dropdown-idplace', 'value'),
     Output('dropdown-idplace', 'options')],
    [Input('dropdown-placename', 'value')]
)
def update_idplace_dropdown(value_name):
    updated_df = update_dataframe()
    print(value_name)
    if value_name == 'All':
        idplace = ['All']
        dropdown_placeID_options = [{'label': 'All', 'value': 'All'}] + [{'label': placeid, 'value': placeid} for
                                                                         placeid in updated_df['gPlusPlaceId'].unique()]
    else:
        filter_idplace = find_placeid(value_name)
        print(filter_idplace)
        if filter_idplace:
            idplace = [filter_idplace]  # Wrap the single value in a list
            dropdown_placeID_options = [{'label': filter_idplace, 'value': filter_idplace}]
        else:
            idplace = ['All']
            dropdown_placeID_options = [{'label': 'All', 'value': 'All'}]
    return idplace, dropdown_placeID_options


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

#SENTIMENT
# Update counter
@app.callback(
    [Output('dropdown-place-1', 'options'),
    Output('dropdown-place-2', 'options'),],
    [Input('button-counter-data', 'n_clicks')],
    [State('dropdown-place-1', 'value'),
     State('dropdown-place-2', 'value')]
)

def update_dropdown_counter_data(n_clicks, dropdown1_value, dropdown2_value):
    updated_df = update_dataframe()
    dropdown_place_options = [{'label': 'Selected place', 'value': 'Selected place'}] + [{'label': str(place) + str(' (') + str(updated_df[updated_df['gPlusPlaceId'] == place].shape[0]) + str(')'), 'value': place} for place in updated_df['gPlusPlaceId'].unique()]
    return [dropdown_place_options, dropdown_place_options]


@app.callback(
    [Output('graph-percent-sentiment-1', 'fig'),
    Output('graph-pos-amount-sentiment-1', 'fig'),
    Output('graph-neg-amount-sentiment-1', 'fig'),],
    [Input('dropdown-place-1', 'value')],
)

def update_sentiment_1(dropdown_place_options_1):
    df = update_dataframe()

    # Load data from the pickle file
    with open('../data_result/counter.pkl', 'rb') as file:
        data_counter = pickle.load(file)

    top_nouns_by_sentiment_range(df, data_counter)

    filtered_df = df[df['gPlusPlaceId'] == dropdown_place_options_1]
    total_count = filtered_df.count()
    avg_star = filtered_df['rating'].mean()
    
    # update_counter()
    # Access the data for the specified key
    pos_df = pd.DataFrame([data_counter[dropdown_place_options_1]['positive']]).transpose()
    neg_df = pd.DataFrame([data_counter[dropdown_place_options_1]['negative']]).transpose()
    # Đếm số lượng pos, neg, neu, rating_avg
    pos_count = pos_df.count()
    neg_count = neg_df.count()
    # neu_count = total_count - (pos_count + neg_count)

    fig1 = draw_fig_percent_sentiment(pos_count, neg_count, avg_star)
    fig2 = draw_fig_pos_sentiment(pos_df)
    fig3 = draw_fig_neg_sentiment(neg_df)
    return fig1, fig2, fig3

# Khởi chạy Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
