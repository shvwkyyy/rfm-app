import streamlit as st
import pandas as pd
import plotly.express as px
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PASTEL_COLORS = ['#80DEEA', '#FFCC80', '#EF9A9A', '#CE93D8', '#A5D6A7']

# Load data
try:
    df = pd.read_csv('rfm_finalone.csv')
    logger.info(f"CSV file loaded successfully. Rows: {len(df)}")
    logger.info(f"Columns: {df.columns.tolist()}")
except FileNotFoundError:
    logger.error("CSV file not found at specified path")
    df = pd.DataFrame()
except Exception as e:
    logger.error(f"Error loading CSV: {e}")
    df = pd.DataFrame()

# Inspect and clean data
if not df.empty:
    df['RECENCY'] = pd.to_numeric(df['RECENCY'], errors='coerce')
    df['FREQUENCY'] = pd.to_numeric(df['FREQUENCY'], errors='coerce')
    df['MONETARY'] = pd.to_numeric(df['MONETARY'], errors='coerce')

    # Impute NaN values
    df['RECENCY'] = df['RECENCY'].fillna(df['RECENCY'].median())
    df['FREQUENCY'] = df['FREQUENCY'].fillna(1)
    df['MONETARY'] = df['MONETARY'].fillna(df['MONETARY'].median())

    # Clean and convert LastPurchaseDate to datetime
    df['LastPurchaseDate'] = pd.to_datetime(df['LastPurchaseDate'], errors='coerce', format='mixed')
    df['Year'] = df['LastPurchaseDate'].dt.year
    df['Year'] = df['Year'].fillna('Unknown').astype(str)
    unique_years = sorted(df['Year'].unique())
else:
    unique_years = []

# Streamlit App Layout
st.title("📊 RFM Customer Segmentation Dashboard")

st.markdown("---")

# Filters
segment_filter = st.multiselect(
    'Select Customer Segments:',
    options=sorted(df["Value_Segment"].unique()),
    default=sorted(df["Value_Segment"].unique())
)

year_filter = st.multiselect(
    'Select Year of Last Purchase:',
    options=unique_years,
    default=unique_years
)

recency_range = st.slider(
    'Select Recency Range (days):',
    min_value=int(df['RECENCY'].min()) if not df.empty else 0,
    max_value=int(df['RECENCY'].max()) if not df.empty else 100,
    value=(int(df['RECENCY'].min()), int(df['RECENCY'].max()))
)

frequency_range = st.slider(
    'Select Frequency Range (transactions):',
    min_value=int(df['FREQUENCY'].min()) if not df.empty else 0,
    max_value=int(df['FREQUENCY'].max()) if not df.empty else 10,
    value=(int(df['FREQUENCY'].min()), int(df['FREQUENCY'].max()))
)

monetary_range = st.slider(
    'Select Monetary Range ($):',
    min_value=int(df['MONETARY'].min()) if not df.empty else 0,
    max_value=int(df['MONETARY'].max() + 1) if not df.empty else 1000,
    value=(int(df['MONETARY'].min()), int(df['MONETARY'].max() + 1))
)

st.markdown("---")

# Apply Filters
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['Value_Segment'].isin(segment_filter)]
filtered_df = filtered_df[filtered_df['Year'].isin(year_filter)]
filtered_df = filtered_df[filtered_df['RECENCY'].between(recency_range[0], recency_range[1])]
filtered_df = filtered_df[filtered_df['FREQUENCY'].between(frequency_range[0], frequency_range[1])]
filtered_df = filtered_df[filtered_df['MONETARY'].between(monetary_range[0], monetary_range[1])]

# Metric Cards
recency_value = round(filtered_df['RECENCY'].mean(), 2) if not filtered_df.empty else 0
frequency_value = round(filtered_df['FREQUENCY'].mean(), 2) if not filtered_df.empty else 0
monetary_value = round(filtered_df['MONETARY'].mean(), 2) if not filtered_df.empty else 0
customer_count = len(filtered_df)
total_revenue = round(filtered_df['MONETARY'].sum(), 2) if not filtered_df.empty else 0

# Display Metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg. Recency", recency_value)
col2.metric("Avg. Frequency", frequency_value)
col3.metric("Avg. Monetary", f"${monetary_value}")
col4.metric("Customers", customer_count)
col5.metric("Total Revenue", f"${total_revenue}")

st.markdown("---")

# Pie chart for Segment distribution
pie_fig = px.pie(filtered_df, names='Value_Segment', title="Customer Segment Distribution",
                 color_discrete_sequence=PASTEL_COLORS)
st.plotly_chart(pie_fig)

# Bar chart: Number of customers per segment
segment_counts = filtered_df['Value_Segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Customer Count']

bar_fig = px.bar(
    segment_counts,
    x='Segment',
    y='Customer Count',
    color='Segment',
    title="Number of Customers per Segment",
    color_discrete_sequence=PASTEL_COLORS
)
st.plotly_chart(bar_fig)

# Box plot: Monetary distribution by segment
box_fig = px.box(filtered_df, x='Value_Segment', y='MONETARY',
                 color='Value_Segment', color_discrete_sequence=PASTEL_COLORS,
                 title="Monetary Value Distribution by Segment")
st.plotly_chart(box_fig)

# 3D Scatter Plot
scatter_fig = px.scatter_3d(
    filtered_df, x='RECENCY', y='FREQUENCY', z='MONETARY',
    color='Value_Segment', color_discrete_sequence=PASTEL_COLORS,
    title="RFM 3D Scatter Plot"
)
st.plotly_chart(scatter_fig)

# Data Table
st.subheader("📋 Customer Data")
st.dataframe(filtered_df)
