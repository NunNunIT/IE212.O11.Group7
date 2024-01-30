from dash import html, dash_table
from dash import Dash, html, dcc, callback, Output, Input
# from dash_core_components import Interval
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from data_utils import *


def create_update_counter_button_layout():
    return html.Div([
            html.Button("Search", id='button-counter-data', n_clicks=0,
                        style={'font-size': '18px', 'border': '2px solid #015fc2', 'padding': '5px 10px',
                               'background-color': '#015fc2', 'color': 'white', 'display': 'inline-block',
                               'border-radius': '5px', 'padding': '10px'}),
        ], style={'margin-right': '20px', 'margin-top': '10px', 'text-align': 'center'})

def create_sentiment_layout(item_id):
    return html.Div([
                # html.H1("Dash App với Dropdown và Biểu đồ"),

                # Dropdown cho việc chọn biểu đồ
                dcc.Dropdown(
                    id=f'dropdown-place-{item_id}',
                    options=[],
                    value='chart1'
                ),

                # Biểu đồ phần trăm
                dcc.Graph(id=f'graph-percent-sentiment-{item_id}'),

                # Biểu đồ pos
                dcc.Graph(id=f'graph-pos-amount-sentiment-{item_id}'),

                # Biểu đồ neg
                dcc.Graph(id=f'graph-neg-amount-sentiment-{item_id}'),
            ], className='sentiment-layout')

def draw_fig_percent_sentiment(positive_feedback, negative_feedback, rating_mean):
    # Tạo biểu đồ tròn
    fig = go.Figure(data=[go.Pie(labels=['Positive', 'Negative'],
                                values=[positive_feedback, negative_feedback],
                                hole=0.4,
                                marker=dict(colors=['#2ca155', '#e63946', '#a8a8a8'],
                                            line=dict(color='white', width=2)),
                                textinfo='label+percent'
                                )])

    # Tùy chỉnh layout (nếu cần)
    fig.update_layout(title='Distribution of User Feedback',
                    annotations=[dict(text=f'{rating_mean:.2f} \u2605', x=0.5, y=0.5, font_size=20, showarrow=False)])
    
    return fig



def draw_fig_pos_sentiment(dateframe_input):
    # Sort the DataFrame by the 'count' column in descending order
    pos_data = dateframe_input.sort_values(by='count', ascending=True)

    # Calculate percentage
    total_count = pos_data['count'].sum()
    pos_data['percentage'] = pos_data['count'] / total_count * 100

    # Keep only the top 10 items
    top_10 = pos_data.tail(10)

    # Sum the remaining items and create an 'Other' category
    other_category = pd.DataFrame({'count': [total_count - top_10['count'].sum()], 
                                    'percentage': [(total_count - top_10['count'].sum()) / total_count * 100]}, 
                                    index=['Other'])

    # Concatenate the top 10 items and the 'Other' category
    pos_data_combined = pd.concat([top_10, other_category])

    # Convert 'percentage' to string for color parameter
    pos_data_combined['percentage_str'] = pos_data_combined['percentage'].apply(lambda x: f"{x:.2f}%").astype(str)

    # Plot the horizontal bar chart using Plotly with color and text parameters
    fig = px.bar(pos_data_combined, y=pos_data_combined.index, x='count', color_discrete_sequence=['#2ca155'],
                    labels={'index': 'Words', 'count': 'Count', 'percentage_str': 'Percentage'},
                    title='Top 10 những điều được đánh giá tích cực', orientation='h', text='percentage_str')

    # Update the color bar label
    fig.update_coloraxes(colorbar_title='Percentage %')
    return fig

def draw_fig_neg_sentiment(dateframe_input):
    # Sort the DataFrame by the 'count' column in descending order
    neg_data = dateframe_input.sort_values(by='count', ascending=True)

    # Calculate percentage
    total_count = neg_data['count'].sum()
    neg_data['percentage'] = neg_data['count'] / total_count * 100

    # Keep only the top 10 items
    top_10 = neg_data.tail(10)

    # Sum the remaining items and create an 'Other' category
    other_category = pd.DataFrame({'count': [total_count - top_10['count'].sum()], 
                                    'percentage': [(total_count - top_10['count'].sum()) / total_count * 100]}, 
                                    index=['Other'])

    # Concatenate the top 10 items and the 'Other' category
    neg_data_combined = pd.concat([top_10, other_category])

    # Convert 'percentage' to string for color parameter
    neg_data_combined['percentage_str'] = neg_data_combined['percentage'].apply(lambda x: f"{x:.2f}%").astype(str)

    # Plot the horizontal bar chart using Plotly with color and text parameters
    fig = px.bar(neg_data_combined, y=neg_data_combined.index, x='count', color_discrete_sequence=['#e63946'],
                    labels={'index': 'Words', 'count': 'Count', 'percentage_str': 'Percentage'},
                    title='Top 10 những điều được đánh giá tiêu cực', orientation='h', text='percentage_str')

    # Update the color bar label
    fig.update_coloraxes(colorbar_title='Percentage %')

    return fig