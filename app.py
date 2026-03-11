import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

st.set_page_config(page_title="PhonePe Pulse Dashboard", page_icon="💜", layout="wide")

st.markdown("<h1 style='color:#6739B7'>💜 PhonePe Transaction Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:grey'>Interactive dashboard powered by PhonePe Pulse data</p>", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Select Year", [2018,2019,2020,2021,2022,2023,2024])
quarter = st.sidebar.selectbox("Select Quarter", [1,2,3,4])

# KPI Cards
@st.cache_data
def get_kpis(year, quarter):
    return pd.read_sql(
        f"SELECT SUM(count) AS total_txns, SUM(amount) AS total_amount FROM aggregated_transaction WHERE year={year} AND quarter={quarter}",
        engine
    )

kpi = get_kpis(year, quarter)
total_txns = int(kpi["total_txns"].iloc[0])
total_amount = float(kpi["total_amount"].iloc[0])

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", f"{total_txns:,}")
col2.metric("Total Amount", f"Rs.{total_amount/1e9:.2f} Billion")
col3.metric("Year / Quarter", f"{year} Q{quarter}")

st.divider()

# Top States
@st.cache_data
def top_states(year, quarter):
    return pd.read_sql(
        f"SELECT state, SUM(amount) AS total_amount FROM aggregated_transaction WHERE year={year} AND quarter={quarter} GROUP BY state ORDER BY total_amount DESC LIMIT 10",
        engine
    )

# Payment Categories
@st.cache_data
def categories(year, quarter):
    return pd.read_sql(
        f"SELECT name, SUM(count) AS total_count FROM aggregated_transaction WHERE year={year} AND quarter={quarter} GROUP BY name ORDER BY total_count DESC",
        engine
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 States by Amount")
    df = top_states(year, quarter)
    fig = px.bar(df, x="total_amount", y="state", orientation="h",
                 color="total_amount", color_continuous_scale="purples")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Payment Category Breakdown")
    df = categories(year, quarter)
    fig = px.pie(df, names="name", values="total_count",
                 color_discrete_sequence=px.colors.sequential.Purples_r)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Yearly Growth
@st.cache_data
def yearly_growth():
    return pd.read_sql(
        "SELECT year, quarter, SUM(count) AS total_transactions FROM aggregated_transaction GROUP BY year, quarter ORDER BY year, quarter",
        engine
    )

# Mobile Brands
@st.cache_data
def brands(year, quarter):
    return pd.read_sql(
        f"SELECT brand, SUM(count) AS total_users FROM aggregated_user WHERE year={year} AND quarter={quarter} GROUP BY brand ORDER BY total_users DESC LIMIT 8",
        engine
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("Year-wise Transaction Growth")
    df = yearly_growth()
    df["period"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)
    fig = px.line(df, x="period", y="total_transactions",
                  markers=True, color_discrete_sequence=["#6739B7"])
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Mobile Brands")
    df = brands(year, quarter)
    fig = px.bar(df, x="brand", y="total_users",
                 color="total_users", color_continuous_scale="purples")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Top Districts
@st.cache_data
def top_districts(year, quarter):
    return pd.read_sql(
        f"SELECT district, state, SUM(amount) AS total_amount FROM map_transaction WHERE year={year} AND quarter={quarter} GROUP BY district, state ORDER BY total_amount DESC LIMIT 10",
        engine
    )

st.subheader("Top 10 Districts by Transaction Amount")
df = top_districts(year, quarter)
fig = px.bar(df, x="district", y="total_amount", color="state",
             color_discrete_sequence=px.colors.qualitative.Vivid)
st.plotly_chart(fig, use_container_width=True)

st.caption("Data Source: PhonePe Pulse GitHub Repository")