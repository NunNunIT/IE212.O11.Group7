from dash import Dash, html, dcc, callback, Output, Input
from dash import dash_table
import plotly.express as px
import pandas as pd

# Sử dụng mã màu: aqua "#04fffe", blue "#043296", red "#ff0000"

df = pd.read_csv('df_ca.csv')
years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

# Ép cột 'reviewTime' thành kiểu datetime
df['reviewTime'] = pd.to_datetime(df['reviewTime'])

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
        dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            style_table={'height': '400px'},  # Điều chỉnh chiều cao của bảng
            style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'},
        ),
        html.Br(),
        html.Div([
            html.Label('Năm:'),
            dcc.Dropdown(
                options=[{'label': str(year), 'value': year} for year in ['All'] + years],
                value='All',  # Giá trị mặc định
                id='dropdown-year',
                style={'width': '250px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Reviewer Name:'),
            dcc.Dropdown(
                options=[{'label': name, 'value': name} for name in ['All'] + df['reviewerName'].unique().tolist()],
                value='All',  # Giá trị mặc định
                id='dropdown-reviewerName',
                style={'width': '250px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block'}),
        dcc.Graph(id='graph-content')
    ], style={'width': '80%', 'margin': 'auto'})  # Điều chỉnh max-width của container div
])

@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-year', 'value'),
     Input('dropdown-reviewerName', 'value')]
)

def update_graph(value_year, value_reviewerName):
    title = 'Số lượng đánh giá'

    if value_year != 'All' and value_reviewerName != 'All':
        dff = df[(df['reviewTime'].dt.year == value_year) & (df['reviewerName'] == value_reviewerName)]
        title += f' theo năm {value_year} của {value_reviewerName}'

    elif value_year != 'All':
        dff = df[df['reviewTime'].dt.year == value_year]
        title += f' theo năm {value_year}'

    elif value_reviewerName != 'All':
        dff = df[df['reviewerName'] == value_reviewerName]
        title += f' của {value_reviewerName}'

    else:
        dff = df.copy()

    return px.histogram(dff, x='rating', title=title,
                       labels={'x': 'Rating', 'y': 'Số lượng đánh giá'},
                       color_discrete_sequence=['#043296'],
                       category_orders=dict(rating=["1", "2", "3", "4", "5"]))  # Số lượng bins cho rating


if __name__ == '__main__':
    app.run(debug=True)
