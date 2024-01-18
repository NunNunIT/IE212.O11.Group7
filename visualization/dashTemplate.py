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
        ], style={'display': 'inline-block'}),
        dcc.Graph(id='graph-content'),
        html.H1("Bản đồ với Dash và Plotly Express"),
        dcc.Graph(id='map-content'),
    ], className='main-container')
], className='container')


@callback(
    [Output('graph-content', 'figure'),
     Output('map-content', 'figure')],
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
                             mapbox_style='carto-positron',  # Chọn kiểu bản đồ (có thể là 'open-street-map', 'stamen-terrain', 'mapbox/dark',...)
                             color_discrete_sequence=['#ff0000'],  # Màu đỏ
                            #  size=2  # Điều chỉnh mức độ zoom
                            )
    
    map_figure.update_layout(
        mapbox=dict(
            style='carto-positron',  # Kiểu bản đồ
            zoom=4
        ),
        autosize=True,  # Tự động điều chỉnh kích thước để chiếm hết không gian hiển thị
        margin=dict(l=0, r=0, t=0, b=0),  # Đặt lề về 0 để loại bỏ khoảng trắng xung quanh bản đồ
    )
    
    return histogram_figure, map_figure

if __name__ == '__main__':
    app.run(debug=True)
