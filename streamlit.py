# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import folium

# st.write('Hello world!')

# st.header('st.button')

# if st.button('Say hello'):
#      st.write('Why hello there')
# else:
#      st.write('Goodbye')

# # Load CSV file into a DataFrame
# file_path = 'df_ca.csv'
# df = pd.read_csv(file_path)

# # Streamlit App
# st.title('Display DataFrame in Streamlit')

# # Display the DataFrame as a table
# st.write(df)

# # Drop missing values
# df_f = df.dropna()

# # Group by price and hour, calculate average rating
# summ_by_price = df_f.groupby(['price', 'hour'])['rating'].mean().reset_index()

# # Plot with Plotly Express
# fig = px.line(summ_by_price, x='hour', y='rating', color='price', 
#               labels={'hour': 'Hour', 'rating': 'Avg. Rating'},
#               color_discrete_map={"$": "#AEAEAE", "$$": "#7A7A7A", "$$$": "#4D4D4D"},
#               title='Change in avg. rating for different price levels',
#               template='plotly')

# # Display the plot using Streamlit
# st.plotly_chart(fig)

# from datetime import time, datetime

# st.header('st.slider')

# # Example 1

# st.subheader('Slider')

# age = st.slider('How old are you?', 0, 130, 25)
# st.write("I'm ", age, 'years old')

# # Example 2

# st.subheader('Range slider')

# values = st.slider(
#      'Select a range of values',
#      0.0, 100.0, (25.0, 75.0))
# st.write('Values:', values)

# # Example 3

# st.subheader('Range time slider')

# appointment = st.slider(
#      "Schedule your appointment:",
#      value=(time(11, 30), time(12, 45)))
# st.write("You're scheduled for:", appointment)

# # Example 4

# st.subheader('Datetime slider')

# start_time = st.slider(
#      "When do you start?",
#      value=datetime(2020, 1, 1, 9, 30),
#      format="MM/DD/YY - hh:mm")
# st.write("Start time:", start_time)

# def main():
#     st.title("Bản đồ trong Streamlit")

#     # Tạo một DataFrame với cột 'latitude' và 'longitude'
#     data = {'latitude': [10.7769], 'longitude': [106.7009]}
#     df = pd.DataFrame(data)

#     # Hiển thị bản đồ trong Streamlit
#     st.map(df, zoom=12, use_container_width=True)

# if __name__ == "__main__":
#     main()

import pandas as pd

def json_to_csv(json_file, csv_file):
    # Đọc dữ liệu JSON vào DataFrame
    df = pd.read_json(json_file)

    # Ghi DataFrame vào CSV
    df.to_csv(csv_file, index=False)

# Sử dụng hàm
json_to_csv('.\data\places_TX.json.gz_', 'output.csv')
