from dash import Dash, html, dcc, callback, Output, Input
from dash import dash_table
import ast
import plotly.express as px
import pandas as pd

# Sử dụng mã màu: aqua "#04fffe", blue "#043296", red "#ff0000"
# Tạo DataFrame chứa thông tin sinh viên
dataSV = {
    'STT': [1, 2, 3, 4],
    'Tên': ['Đặng Huỳnh Vĩnh Tân', 'Nguyễn Thị Hồng Nhung', 'Nguyễn Viết Kha', 'Nguyễn Huy Hoàng'],
    'MSSV': [21520442, 21522436, 21520949, 21522093]
}
dfSV = pd.DataFrame(dataSV)

df = pd.read_csv('df_ca.csv')
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
        dash_table.DataTable(
            id='table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            style_table={'height': '400px'},
            style_cell={'maxWidth': 100, 'overflow': 'ellipsis', 'textOverflow': 'ellipsis', 'whiteSpace': 'nowrap'},
            style_header={
                'backgroundColor': '#043296',
                'fontWeight': 'bold',
                'color': 'white',
                'textAlign': 'center'
            },
        ),
        html.Br(),
        html.Div([
            html.Label('Năm:'),
            dcc.Dropdown(
                options=[{'label': str(year), 'value': year} for year in ['All'] + years],
                value='All',
                id='dropdown-year',
                style={'width': '250px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),

        html.Div([
            html.Label('Reviewer Name:'),
            dcc.Dropdown(
                options=[{'label': name, 'value': name} for name in ['All'] + df['reviewerName'].unique().tolist()],
                value='All',
                id='dropdown-reviewerName',
                style={'width': '250px', 'padding': '0 12px'}
            ),
        ], style={'display': 'inline-block', 'margin-right':'20px'}),

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
        html.H1("Bản đồ với Dash và Plotly Express"),
        dcc.Graph(id='map-content'),
    ], className='main-container')
], className='container')
@app.callback(
    Output('dropdown-categories', 'options'),
    Input('dropdown-year', 'value'),
    Input('dropdown-reviewerName', 'value')
)
def update_categories_options(value_year, value_reviewerName):
    if value_year == 'All' and value_reviewerName == 'All':
        categories = ['All'] + df['categories'].unique().tolist()
    elif value_year == 'All':
        filtered_categories = df[df['reviewerName'] == value_reviewerName]['categories'].unique().tolist()
        if len(filtered_categories) > 0:
            categories = ['All'] + filtered_categories
        else:
            categories = ['All']
    elif value_reviewerName == 'All':
        filtered_categories = df[df['reviewTime'].dt.year == value_year]['categories'].unique().tolist()
        if len(filtered_categories) > 0:
            categories = ['All'] + filtered_categories
        else:
            categories = ['All']
    else:
        filtered_categories = df[(df['reviewTime'].dt.year == value_year) & (df['reviewerName'] == value_reviewerName)]['categories'].unique().tolist()
        if len(filtered_categories) > 0:
            categories = ['All'] + filtered_categories
        else:
            categories = ['All']

    options = [{'label': category, 'value': category} for category in categories]

    return options


@app.callback(
    Output('dropdown-reviewerName', 'options'),
    Input('dropdown-year', 'value')
)
def update_reviewername_options(dropdown_year):
    if dropdown_year == 'All':
        reviewer_name = ['All'] + df['reviewerName'].unique().tolist()
    else:
        filtered_reviewers = df[df['reviewTime'].dt.year == dropdown_year]['reviewerName'].unique().tolist()
        if len(filtered_reviewers) > 0:
            reviewer_name = ['All'] + filtered_reviewers
        else:
            reviewer_name = ['All']

    options = [{'label': name, 'value': name} for name in reviewer_name]

    return options

@app.callback(
    [Output('graph-content', 'figure'),
     Output('map-content', 'figure')],
    [Input('dropdown-year', 'value'),
     Input('dropdown-reviewerName', 'value'),
     Input('dropdown-categories', 'value')]
)
def update_graph(value_year, value_reviewerName, value_categories):
    title = 'Số lượng đánh giá'

    dff = df.copy()  # Tạo một bản sao của DataFrame ban đầu

    if value_year != 'All':
        dff = dff[dff['reviewTime'].dt.year == value_year]
        title += f' theo năm {value_year}'

    if value_reviewerName != 'All':
        dff = dff[dff['reviewerName'] == value_reviewerName]
        title += f' của {value_reviewerName}'

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




if __name__ == '__main__':
    app.run(debug=True)
