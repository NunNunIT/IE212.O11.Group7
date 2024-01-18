# import streamlit as st # web development
# import numpy as np # np mean, np random 
# import pandas as pd # read csv, df manipulation
# import time # to simulate a real time data, time loop 
# import plotly.express as px # interactive charts 


# # read csv from a github repo
# df = pd.read_csv("https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv")


# st.set_page_config(
#     page_title = 'Real-Time Data Science Dashboard',
#     page_icon = '✅',
#     layout = 'wide'
# )

# # dashboard title

# st.title("Real-Time / Live Data Science Dashboard")

# # top-level filters 

# job_filter = st.selectbox("Select the Job", pd.unique(df['job']))


# # creating a single-element container.
# placeholder = st.empty()

# # dataframe filter 

# df = df[df['job']==job_filter]

# # near real-time / live feed simulation 

# for seconds in range(200):
# #while True: 
    
#     df['age_new'] = df['age'] * np.random.choice(range(1,5))
#     df['balance_new'] = df['balance'] * np.random.choice(range(1,5))

#     # creating KPIs 
#     avg_age = np.mean(df['age_new']) 

#     count_married = int(df[(df["marital"]=='married')]['marital'].count() + np.random.choice(range(1,30)))
    
#     balance = np.mean(df['balance_new'])

#     with placeholder.container():
#         # create three columns
#         kpi1, kpi2, kpi3 = st.columns(3)

#         # fill in those three columns with respective metrics or KPIs 
#         kpi1.metric(label="Age ⏳", value=round(avg_age), delta= round(avg_age) - 10)
#         kpi2.metric(label="Married Count 💍", value= int(count_married), delta= - 10 + count_married)
#         kpi3.metric(label="A/C Balance ＄", value= f"$ {round(balance,2)} ", delta= - round(balance/count_married) * 100)

#         # create two columns for charts 

#         fig_col1, fig_col2 = st.columns(2)
#         with fig_col1:
#             st.markdown("### First Chart")
#             fig = px.density_heatmap(data_frame=df, y = 'age_new', x = 'marital')
#             st.write(fig)
#         with fig_col2:
#             st.markdown("### Second Chart")
#             fig2 = px.histogram(data_frame = df, x = 'age_new')
#             st.write(fig2)
#         st.markdown("### Detailed Data View")
#         st.dataframe(df)
#         time.sleep(1)
#     #placeholder.empty()

import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dashTemplate import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)





app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Dash_Introduction/intro_bees.csv")

df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)
print(df[:5])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["Year"] == option_slctd]
    dff = dff[dff["Affected by"] == "Varroa_mites"]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        geojson="https://opendata.arcgis.com/datasets/48d12b2864ed469fb8bfbeae2e732848_0.geojson",
        featureidkey="properties.lad19cd",
        locations='Region Code',
        color='Pct of Colonies Impacted',
        hover_data=['Region', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.YlOrRd,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_dark'
    )

    # Plotly Graph Objects (GO)
    # fig = go.Figure(
    #     data=[go.Choropleth(
    #         locationmode='USA-states',
    #         locations=dff['state_code'],
    #         z=dff["Pct of Colonies Impacted"].astype(float),
    #         colorscale='Reds',
    #     )]
    # )
    #
    # fig.update_layout(
    #     title_text="Bees Affected by Mites in the USA",
    #     title_xanchor="center",
    #     title_font=dict(size=24),
    #     title_x=0.5,
    #     geo=dict(scope='usa'),
    # )

    return container, fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)