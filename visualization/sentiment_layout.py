from dash import html, dash_table
from dash import Dash, html, dcc, callback, Output, Input
# from dash_core_components import Interval
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from data_utils import *

def create_sentiment_layout(item_id):
    return html.Div([
                html.H1("Dash App với Dropdown và Biểu đồ"),

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

def draw_fig_percent_sentiment(positive_feedback, negative_feedback, neutral_feedback, rating_mean):
    # Tạo biểu đồ tròn
    fig = go.Figure(data=[go.Pie(labels=['Positive', 'Negative', 'Neutral'],
                                values=[positive_feedback, negative_feedback, neutral_feedback],
                                hole=0.4,
                                marker=dict(colors=['#2ca155', '#e63946', '#a8a8a8'],
                                            line=dict(color='white', width=2)),
                                textinfo='label+percent'
                                )])

    # Tùy chỉnh layout (nếu cần)
    fig.update_layout(title='Distribution of User Feedback',
                    annotations=[dict(text=f'{rating_mean:.2f} \u2605', x=0.5, y=0.5, font_size=20, showarrow=False)])
    
    return fig

# def draw_fig_pos_sentiment(positive_feedback, negative_feedback, neutral_feedback, rating_mean):
#     return fig