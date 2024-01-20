from dash import Dash, html, dcc, callback, Output, Input
from dash_core_components import Interval
from dash import dash_table
import requests
import pandas as pd

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
            print(f"Error fetching data from API: {response.status_code}")
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
        df_new = pd.DataFrame.from_dict(api_data)
        print(df_new['categories'])

        global initial_data  # Truy cập biến global initial_data

        update_time = df_new.iloc[-1]['last_update_time']

        if update_time > last_update_time:
            last_update_time = update_time
            # Nối df_new vào initial_data
            initial_data = pd.concat([initial_data, df_new])

        return initial_data


# Khởi tạo Dash App
app = Dash(__name__)

# Layout của Dash App
app.layout = html.Div([
    html.Div([
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
        ),
        Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Set interval to 5 seconds
    ], className="main-container")
])

# Callback để cập nhật dữ liệu từ API và cập nhật Dash App
@app.callback(
    [Output('detail-table', 'columns'),
     Output('detail-table', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_data_table(n_intervals):
    df = update_dataframe()
    columns = [{'name': col, 'id': col} for col in df.columns]
    data = df.to_dict('records')
    return columns, data

# Khởi chạy Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
