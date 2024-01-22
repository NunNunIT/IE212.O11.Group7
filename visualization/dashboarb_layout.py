from dash import html, dash_table
from dash import Dash, html, dcc, callback, Output, Input
# from dash_core_components import Interval
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from data_utils import *

# def filter_by_selecttion(dateframe_input, select_year = 'All', select_place = 'All'):
def filter_by_selection(dateframe_input, select_year = 'All'):
    filtered_df = dateframe_input.copy()
    # if select_year != 'All' and select_place != 'All':
        # Lọc DataFrame dựa trên cả hai điều kiện
        # filtered_df = filtered_df[(filtered_df['year'] == select_year) & (filtered_df['place'] == select_place)]
    if select_year != 'All':
        filtered_df = filtered_df(filtered_df['year'] == select_year)
    # elif select_place != 'All':
        # filtered_df = filtered_df[(filtered_df['place'] == select_place)
                            
    return filtered_df


def create_detail_table_layout(): 
    return  html.Div([
                dash_table.DataTable(
                    id='detail-table',
                    columns=[],
                    data=[],
                    page_size=10,
                    style_table={'height': '400px'},
                    style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'},
                    style_header={
                        'backgroundColor': '#043296',
                        'fontWeight': 'bold',
                        'color': 'white',
                        'textAlign': 'center'
                    },
                )
            ])

def create_dashboard_option_layout():
    return html.Div([
                html.H1("Dashboard"),
                html.Div([
                    html.Label('Year'),
                    dcc.Dropdown(
                        id='year-dropdown',
                        # options=[],
                        value= 'All',  # Giá trị mặc định là All
                        placeholder='Chọn năm',  # Nhãn placeholder
                    ),
                ]),
            ])

def create_dashboard_total_layout(df):
    return html.Div([
                html.Div([
                    html.Div([
                    html.Label("Ratings"),
                    html.Div(id='total-ratings', children=len(df))
                    ]),
                    html.Div([
                    html.Label("Reviews"),
                    html.Div(id='total-reviews', children=(df['reviewText'].count()))
                    ]),
                    html.Div([
                        html.Label("Places"),
                        html.Div(id='total-businesses', children=len(df['gPlusPlaceId'].unique()))
                    ]),
                    html.Div([
                        html.Label("User"),
                        html.Div(id='total-user', children=len(df['gPlusUserId'].unique()))
                    ]),
                ], style={'columnCount': 4}),
            ])

def calculate_reviews_dashboarb(dataframe_input):
    temp_df = dataframe_input.copy()

    # Creating columns for each rating
    for i in range(6):
        temp_df[f'{i}_star'] = temp_df['rating'] == i

    # Creating columns for the total number of stars and reviews
    temp_df['total_stars'] = temp_df.loc[:, '0_star':'5_star'].sum(axis=1)
    temp_df['total_reviews'] = temp_df['reviewText'].notna().astype(int)


    return temp_df


def draw_chart_reviews_dashboard(dataframe_input):
    temp_df2 = dataframe_input.copy()

    # Grouping by year and calculating the sum for each group
    statistics_df = temp_df2.groupby('year').agg({
        '0_star': 'sum',
        '1_star': 'sum',
        '2_star': 'sum',
        '3_star': 'sum',
        '4_star': 'sum',
        '5_star': 'sum',
        'total_stars': 'sum',
        'rating': 'mean',
        'total_reviews': 'sum'
    }).reset_index()

    # Renaming the 'avg_rating' column for clarity
    statistics_df = statistics_df.rename(columns={'rating': 'avg_star'})

    fig = px.bar(statistics_df, x='year', y=[f'{i}_star' for i in range(6)],
              labels={'value': 'Số lượng', 'variable': 'Rating'},
              title='Combined Plot: Distribution of Ratings, Average Rating, and Total Reviews Over Years',
              color_discrete_sequence=['#fff363', '#fde725', '#9fda3a', '#1fa187', '#004ebe', '#002f72'],)
                

    # Adding trace for total reviews with blue color and legend label
    total_reviews_trace = px.line(statistics_df, x='year', y='total_stars',
                                labels={'value': 'Total Reviews', 'variable': 'Metric'},
                                line_shape='linear', title='')
    total_reviews_trace.update_traces(line=dict(color='#44d2e6', width=2, dash='solid'), name='Total Reviews')

    # Adding markers on the 'Total Reviews' line
    total_reviews_trace.update_traces(mode='markers+lines', marker=dict(symbol='circle', size=16, color='#44d2e6', line=dict(color='#44d2e6', width=1)))
    fig.add_trace(total_reviews_trace.data[0])

    # Adding trace for average rating on the secondary Y-axis with yellow color and legend label
    avg_star_trace = px.line(statistics_df, x='year', y='avg_star',
                            labels={'value': 'Average Rating', 'variable': 'Metric'},
                            line_shape='linear', title='')
    avg_star_trace.update_traces(yaxis="y2", line=dict(color='#f86134', width=2, dash='solid'), name='Average Rating')

    # Adding markers on the 'Average Rating' line
    avg_star_trace.update_traces(mode='markers+lines', marker=dict(symbol='circle', size=16, color='#f86134', line=dict(color='#f86134', width=1)))
    fig.add_trace(avg_star_trace.data[0])

    # Updating layout
    fig.update_layout(
        xaxis=dict(title='Năm'),
        yaxis=dict(title='Số lượng đánh giá'),
        yaxis2=dict(title='Điểm đánh giá trung bình', overlaying='y', side='right'),
        legend=dict(title='', orientation="h", x=0.1, y=-0.15),
        # height=1000,
    )
    
    return fig

# Grouping by year and calculating the sum for each group
def calculate_reviews_by_star_dashboarb(dataframe_input):
    df_temp = dataframe_input.copy()
    df_temp = calculate_reviews_dashboarb(df_temp)

    result_df = df_temp.agg({
        '0_star': 'sum',
        '1_star': 'sum',
        '2_star': 'sum',
        '3_star': 'sum',
        '4_star': 'sum',
        '5_star': 'sum',
    }).reset_index()

    rating_sum = sum(result_df.loc[result_df['index'] == f'{i}_star', 0].values[0] * i for i in range(6))
    total_reviews = sum(result_df.loc[result_df['index'] == f'{i}_star', 0].values[0] for i in range(6))

    rating_mean = rating_sum / total_reviews

    return result_df, rating_mean


def draw_chart_reviews_by_star_dashboard(dataframe_input):
    # Filter data for years from 2010 onwards
    df_temp = dataframe_input.copy()
    df_temp, rating_mean = calculate_reviews_by_star_dashboarb(df_temp)
    selected_rows = df_temp[df_temp['index'].str.endswith('_star')]
    labels = selected_rows['index'].tolist()
    sizes = selected_rows[0].tolist()
    
    # rating_mean = df_temp[df_temp['index'] == 'avg_star'][0].values[0]

    # Đảo ngược thứ tự của labels và sizes
    labels.reverse()
    sizes.reverse()

    # Colors
    colors = ['#fff363', '#fde725', '#9fda3a', '#1fa187', '#004ebe', '#002f72']
    colors.reverse()

    # Tạo biểu đồ vòng khuyên
    fig = px.pie(df_temp, values=sizes, names=labels, hole=0.4, title='Distribution of Ratings', color_discrete_sequence=colors,
                category_orders={'names': labels})  # Define the order of slices

    fig.update_traces(textposition='inside', textfont_size=14)

    # Thêm text annotation cho giá trị trung bình của "rating"
    fig.add_annotation(
        text=f'{rating_mean:.2f} \u2605',
        x=0.5, y=0.5,  # Vị trí của text annotation trong biểu đồ
        showarrow=False,
        font=dict(size=24, color='#fbb040',)
    )
    
    return fig

