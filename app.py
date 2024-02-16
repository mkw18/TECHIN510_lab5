import streamlit as st
import pandas.io.sql as sqlio
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta

from db import conn_str

st.title("Seattle Events")

# Load the dataset
df = sqlio.read_sql_query("SELECT * FROM events", conn_str)

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Extract month and day of the week from the date
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.day_name()

# Preparing data for visualizations
# 1. Most common categories of events
event_category_counts = df['category'].value_counts().reset_index()

# 2. Month with the most number of events
events_per_month = df['month'].value_counts().sort_index().reset_index()

# 3. Day of the week with the most number of events
events_per_day = df['day_of_week'].value_counts().reset_index()

# 4. Most common event locations
event_location_counts = df['location'].value_counts().head(10).reset_index()  # Top 10 locations

# Most Common Categories of Events
chart1 = alt.Chart(event_category_counts).mark_bar().encode(
    x='category:Q',
    y=alt.Y('index:N', sort='-x', title='Event Category'),
    tooltip=['index', 'category']
).properties(
    title='Most Common Categories of Events'
)

# Events Distribution by Month
chart2 = alt.Chart(events_per_month).mark_bar().encode(
    x='index:O',  # Treat month as ordinal to keep order
    y='month:Q',
    tooltip=['index', 'month']
).properties(
    title='Events Distribution by Month'
)

# Events Distribution by Day of the Week
chart3 = alt.Chart(events_per_day).mark_bar().encode(
    x='day_of_week:Q',
    y=alt.Y('index:N', sort='-x', title='Day of the Week'),
    tooltip=['index', 'day_of_week']
).properties(
    title='Events Distribution by Day of the Week'
)

# Top 10 Common Locations for Events
chart4 = alt.Chart(event_location_counts).mark_bar().encode(
    x='location:Q',
    y=alt.Y('index:N', sort='-x', title='Location'),
    tooltip=['index', 'location']
).properties(
    title='Top 10 Common Locations for Events'
)

# Display the charts
chart1 & chart2 & chart3 & chart4

category = st.selectbox("Select a category", df['category'].unique())

# Create a date range selector for event dates
start_date, end_date = st.date_input('Select date range', [date.today(), date.today()+timedelta(days=7)])
start_date = pd.to_datetime(start_date).tz_localize('UTC')
end_date = pd.to_datetime(end_date).tz_localize('UTC')

m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)
folium.Marker([47.6062, -122.3321], popup='Seattle').add_to(m)
st_folium(m, width=1200, height=600)

# df = df[df['category'] == category]
# st.write(df)

# Create a multiselect box for location selection
location = st.multiselect('Select location', options=df['location'].unique())

# Create a multiselect box for weather selection
weather = st.multiselect('Select weather', options=df['condition'].unique())

# Filter the data based on user selections
filtered_df = df[
    (df['category'] == category) & 
    df['date'].between(start_date, end_date) & 
    df['location'].isin(location) & 
    df['condition'].isin(weather)
]

st.write(filtered_df)