import random
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---- PAGE SETUP ---- #
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #F4F6FA;
        }
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #003366;
        }
        .stMetric {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.title("Sales Performance Dashboard")
st.markdown("### _Stay updated with the latest insights_")

# ---- SIDEBAR ---- #
with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_file = st.file_uploader("**Upload your Excel file**")
    st.markdown("---")
    st.markdown("Designed by **Areesha Kainat** ")

if uploaded_file is None:
    st.info("ℹ️ Please upload a file to get started.")
    st.stop()


@st.cache_data
def load_data(file):
    return pd.read_excel(file)


df = load_data(uploaded_file)

# ---- PREVIEW ---- #
with st.expander("🔍 Preview Data", expanded=False):
    st.dataframe(df, use_container_width=True)

# ---- METRICS SECTION ---- #
st.markdown("---")
st.subheader("📊 Key Financial Metrics")
metrics_container = st.container()
with metrics_container:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Accounts Receivable", "$6,621,280")
        st.metric("Current Ratio", "1.86 %")
        
    with col2:
        st.metric("Total Accounts Payable", "$1,630,270")
        st.metric("In Stock", "10 days")
        
    with col3:
        st.metric("Equity Ratio", "75.38 %")
        st.metric("Out Stock", "7 days")
        
    with col4:
        st.metric("Debt Equity", "1.10 %")
        st.metric("Delay", "28 days")

# ---- CHARTS SECTION ---- #
st.markdown("---")
st.subheader("Visual Insights")

top_row = st.columns((2, 1))

with top_row[0]:
    st.markdown("#### 📌 Sales Overview (2023)")
    sales_data = duckdb.sql(
        """
        SELECT Scenario, business_unit, SUM(sales) as sales
        FROM (
            UNPIVOT (
                SELECT Scenario, business_unit, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
                FROM df
                WHERE Year='2023' AND Account='Sales'
            )
            ON Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
            INTO NAME month VALUE sales
        )
        GROUP BY Scenario, business_unit
        """
    ).df()

    fig = px.bar(
        sales_data, x="business_unit", y="sales", color="Scenario",
        barmode="group", text_auto=".2s", height=400,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

with top_row[1]:
    st.markdown("#### 🔄 Yearly Actuals")
    actuals_data = duckdb.sql(
        """
        SELECT Account, Year, SUM(sales) as sales
        FROM (
            UNPIVOT (
                SELECT Account, Year, ABS(Jan) AS Jan, ABS(Feb) AS Feb, ABS(Mar) AS Mar, 
                ABS(Apr) AS Apr, ABS(May) AS May, ABS(Jun) AS Jun, ABS(Jul) AS Jul, 
                ABS(Aug) AS Aug, ABS(Sep) AS Sep, ABS(Oct) AS Oct, ABS(Nov) AS Nov, ABS(Dec) AS Dec
                FROM df
                WHERE Scenario='Actuals' AND Account!='Sales'
            )
            ON Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
            INTO NAME month VALUE sales
        )
        GROUP BY Account, Year
        """
    ).df()

    fig = px.bar(
        actuals_data, x="Year", y="sales", color="Account",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

bottom_row = st.columns(1)
with bottom_row[0]:
    st.markdown("#### 📅 Monthly Budget vs Forecast (2023)")
    monthly_data = duckdb.sql(
        """
        SELECT Scenario, month, sales
        FROM (
            UNPIVOT (
                SELECT Scenario, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
                FROM df
                WHERE Year='2023' AND Account='Sales' AND business_unit='Software'
            )
            ON Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
            INTO NAME month VALUE sales
        )
        """
    ).df()

    fig = px.line(
        monthly_data, x="month", y="sales", color="Scenario", markers=True,
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.success(" Dashboard loaded successfully!")
st.markdown(" Designed by **Areesha Kainat** ")
