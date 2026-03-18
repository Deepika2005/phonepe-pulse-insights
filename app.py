import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine
import requests

engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

st.set_page_config(page_title="PhonePe Pulse Dashboard", page_icon="💜", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0e0b1a; }
    section[data-testid="stSidebar"] { background-color: #1a0a2e; }
    .map-header {
        background: linear-gradient(135deg, #2d1b69 0%, #1a0a2e 100%);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 18px;
        border: 1px solid #4a2d8e;
    }
    .map-kpi-row { display: flex; gap: 16px; margin-bottom: 10px; }
    .map-kpi {
        background: #1e1040;
        border-radius: 12px;
        padding: 16px 24px;
        flex: 1;
        border: 1px solid #3a1f7a;
    }
    .map-kpi-label { color: #aaa; font-size: 13px; margin-bottom: 4px; }
    .map-kpi-value { color: #00d4ff; font-size: 26px; font-weight: 700; }
    .cat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a0a2e;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 8px;
        border-left: 3px solid #6739B7;
    }
    .cat-name { color: #ddd; font-size: 14px; }
    .cat-val  { color: #00d4ff; font-weight: 700; font-size: 15px; }
    .section-divider {
        border: none;
        border-top: 1px solid #2d1b69;
        margin: 28px 0;
    }
    .pulse-section-title {
        color: #00d4ff;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 14px;
        letter-spacing: 0.5px;
    }
    .top-district-badge {
        background: #2d1b69;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#6739B7'>💜 PhonePe Transaction Insights</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:grey'>Interactive dashboard powered by PhonePe Pulse data</p>", unsafe_allow_html=True)

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")
year    = st.sidebar.selectbox("Select Year",    [2018,2019,2020,2021,2022,2023,2024])
quarter = st.sidebar.selectbox("Select Quarter", [1,2,3,4])

# ── KPI Cards ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_kpis(year, quarter):
    return pd.read_sql(
        f"SELECT SUM(count) AS total_txns, SUM(amount) AS total_amount "
        f"FROM aggregated_transaction WHERE year={year} AND quarter={quarter}",
        engine
    )

kpi          = get_kpis(year, quarter)
total_txns   = int(kpi["total_txns"].iloc[0])
total_amount = float(kpi["total_amount"].iloc[0])

col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", f"{total_txns:,}")
col2.metric("Total Amount",       f"Rs.{total_amount/1e9:.2f} Billion")
col3.metric("Year / Quarter",     f"{year} Q{quarter}")

st.divider()

# ── Top States & Categories ───────────────────────────────────────────────────
@st.cache_data
def top_states(year, quarter):
    return pd.read_sql(
        f"SELECT state, SUM(amount) AS total_amount "
        f"FROM aggregated_transaction WHERE year={year} AND quarter={quarter} "
        f"GROUP BY state ORDER BY total_amount DESC LIMIT 10",
        engine
    )

@st.cache_data
def categories(year, quarter):
    return pd.read_sql(
        f"SELECT name, SUM(count) AS total_count "
        f"FROM aggregated_transaction WHERE year={year} AND quarter={quarter} "
        f"GROUP BY name ORDER BY total_count DESC",
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

# ── Yearly Growth & Mobile Brands ─────────────────────────────────────────────
@st.cache_data
def yearly_growth():
    return pd.read_sql(
        "SELECT year, quarter, SUM(count) AS total_transactions "
        "FROM aggregated_transaction GROUP BY year, quarter ORDER BY year, quarter",
        engine
    )

@st.cache_data
def brands(year, quarter):
    return pd.read_sql(
        f"SELECT brand, SUM(count) AS total_users "
        f"FROM aggregated_user WHERE year={year} AND quarter={quarter} "
        f"GROUP BY brand ORDER BY total_users DESC LIMIT 8",
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

# ── Top Districts ─────────────────────────────────────────────────────────────
@st.cache_data
def top_districts(year, quarter):
    return pd.read_sql(
        f"SELECT district, state, SUM(amount) AS total_amount "
        f"FROM map_transaction WHERE year={year} AND quarter={quarter} "
        f"GROUP BY district, state ORDER BY total_amount DESC LIMIT 10",
        engine
    )

st.subheader("Top 10 Districts by Transaction Amount")
df = top_districts(year, quarter)
fig = px.bar(df, x="district", y="total_amount", color="state",
             color_discrete_sequence=px.colors.qualitative.Vivid)
st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
#  🗺️  INDIA MAP SECTION  (appended — PhonePe Pulse style)
# ═════════════════════════════════════════════════════════════════════════════

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="map-header">
    <span style="color:#00d4ff; font-size:24px; font-weight:700;">🗺️ India Transaction Map</span><br>
    <span style="color:#aaa; font-size:13px;">State-wise heatmap — inspired by PhonePe Pulse</span>
</div>
""", unsafe_allow_html=True)

# State name mapping: pulse slug → GeoJSON display name
STATE_MAP = {
    'andaman-&-nicobar-islands':           'Andaman & Nicobar Island',
    'andhra-pradesh':                      'Andhra Pradesh',
    'arunachal-pradesh':                   'Arunachal Pradesh',
    'assam':                               'Assam',
    'bihar':                               'Bihar',
    'chandigarh':                          'Chandigarh',
    'chhattisgarh':                        'Chhattisgarh',
    'dadra-&-nagar-haveli-&-daman-&-diu':  'Dadara & Nagar Havelli',
    'delhi':                               'NCT of Delhi',
    'goa':                                 'Goa',
    'gujarat':                             'Gujarat',
    'haryana':                             'Haryana',
    'himachal-pradesh':                    'Himachal Pradesh',
    'jammu-&-kashmir':                     'Jammu & Kashmir',
    'jharkhand':                           'Jharkhand',
    'karnataka':                           'Karnataka',
    'kerala':                              'Kerala',
    'ladakh':                              'Ladakh',
    'lakshadweep':                         'Lakshadweep',
    'madhya-pradesh':                      'Madhya Pradesh',
    'maharashtra':                         'Maharashtra',
    'manipur':                             'Manipur',
    'meghalaya':                           'Meghalaya',
    'mizoram':                             'Mizoram',
    'nagaland':                            'Nagaland',
    'odisha':                              'Odisha',
    'puducherry':                          'Puducherry',
    'punjab':                              'Punjab',
    'rajasthan':                           'Rajasthan',
    'sikkim':                              'Sikkim',
    'tamil-nadu':                          'Tamil Nadu',
    'telangana':                           'Telangana',
    'tripura':                             'Tripura',
    'uttar-pradesh':                       'Uttar Pradesh',
    'uttarakhand':                         'Uttarakhand',
    'west-bengal':                         'West Bengal',
}

# Map view selector
map_view = st.sidebar.selectbox(
    "🗺️ Map View",
    ["Transactions", "Users", "Insurance"],
    key="map_view"
)

# ── Load map data ─────────────────────────────────────────────────────────────
@st.cache_data
def map_transaction_data(year, quarter):
    return pd.read_sql(
        f"SELECT state, SUM(count) AS total_count, SUM(amount) AS total_amount "
        f"FROM aggregated_transaction WHERE year={year} AND quarter={quarter} "
        f"GROUP BY state",
        engine
    )

@st.cache_data
def map_user_data(year, quarter):
    return pd.read_sql(
        f"SELECT state, SUM(registered_users) AS total_count, SUM(app_opens) AS total_amount "
        f"FROM aggregated_user WHERE year={year} AND quarter={quarter} "
        f"GROUP BY state",
        engine
    )

@st.cache_data
def map_insurance_data(year, quarter):
    try:
        return pd.read_sql(
            f"SELECT state, SUM(transaction_count) AS total_count, SUM(transaction_amount) AS total_amount "
            f"FROM aggregated_insurance WHERE year={year} AND quarter={quarter} "
            f"GROUP BY state",
            engine
        )
    except Exception:
        return pd.DataFrame(columns=["state","total_count","total_amount"])

@st.cache_data
def map_top_districts(year, quarter):
    return pd.read_sql(
        f"SELECT district, state, SUM(transaction_amount) AS total_amount "
        f"FROM map_transaction WHERE year={year} AND quarter={quarter} "
        f"GROUP BY district, state ORDER BY total_amount DESC LIMIT 5",
        engine
    )

@st.cache_data
def map_top_pincodes(year, quarter):
    return pd.read_sql(
        f"SELECT entity_name AS pincode, state, SUM(transaction_amount) AS total_amount "
        f"FROM top_transaction WHERE year={year} AND quarter={quarter} AND entity_type='pincode' "
        f"GROUP BY entity_name, state ORDER BY total_amount DESC LIMIT 5",
        engine
    )

# Pick dataset
if map_view == "Transactions":
    df_map = map_transaction_data(year, quarter)
    color_col   = "total_amount"
    hover_count = "total_count"
    count_label = "Transactions"
    amount_label= "Amount (₹)"
elif map_view == "Users":
    df_map = map_user_data(year, quarter)
    color_col   = "total_count"
    hover_count = "total_amount"
    count_label = "Registered Users"
    amount_label= "App Opens"
else:
    df_map = map_insurance_data(year, quarter)
    color_col   = "total_amount"
    hover_count = "total_count"
    count_label = "Policies"
    amount_label= "Amount (₹)"

# Apply state name mapping
df_map["state_display"] = df_map["state"].map(STATE_MAP).fillna(df_map["state"])

# ── KPI row for map section ───────────────────────────────────────────────────
map_total_count  = df_map["total_count"].sum()
map_total_amount = df_map["total_amount"].sum()
avg_val = map_total_amount / map_total_count if map_total_count > 0 else 0

st.markdown(f"""
<div class="map-kpi-row">
    <div class="map-kpi">
        <div class="map-kpi-label">All PhonePe {map_view}</div>
        <div class="map-kpi-value">{map_total_count:,.0f}</div>
        <div class="map-kpi-label">{count_label}</div>
    </div>
    <div class="map-kpi">
        <div class="map-kpi-label">Total Payment Value</div>
        <div class="map-kpi-value">₹{map_total_amount/1e7:,.0f} Cr</div>
    </div>
    <div class="map-kpi">
        <div class="map-kpi-label">Avg. Value per Transaction</div>
        <div class="map-kpi-value">₹{avg_val:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Map + Right Panel ─────────────────────────────────────────────────────────
map_col, panel_col = st.columns([2, 1])

with map_col:
    GEOJSON_URL = (
        "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112"
        "/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    )
    try:
        geojson = requests.get(GEOJSON_URL, timeout=10).json()

        fig_map = px.choropleth(
            df_map,
            geojson=geojson,
            featureidkey="properties.ST_NM",
            locations="state_display",
            color=color_col,
            hover_name="state_display",
            hover_data={
                "total_count":  True,
                "total_amount": True,
                color_col:      False
            },
            color_continuous_scale=["#1a0a2e", "#4a2d8e", "#6739B7", "#ff6b00", "#ffd700"],
            labels={"total_count": count_label, "total_amount": amount_label}
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(
            paper_bgcolor="#0e0b1a",
            plot_bgcolor="#0e0b1a",
            font_color="white",
            geo_bgcolor="#0e0b1a",
            margin={"r": 0, "t": 10, "l": 0, "b": 0},
            height=520,
            coloraxis_colorbar=dict(
                title=amount_label,
                tickfont=dict(color="white"),
                titlefont=dict(color="white")
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ Could not load India GeoJSON map. Check internet connection.\n\n{e}")
        # Fallback: bubble map using state lat/lon approximation
        st.info("Showing fallback bar chart instead.")
        fig_fb = px.bar(
            df_map.sort_values(color_col, ascending=False).head(15),
            x="state_display", y=color_col,
            color=color_col, color_continuous_scale="purples"
        )
        fig_fb.update_layout(paper_bgcolor="#0e0b1a", font_color="white", xaxis_tickangle=-45)
        st.plotly_chart(fig_fb, use_container_width=True)

with panel_col:
    # ── Payment Categories ────────────────────────────────────────────────────
    st.markdown(f'<div class="pulse-section-title">{map_view} Breakdown</div>', unsafe_allow_html=True)

    cat_df = categories(year, quarter) if map_view == "Transactions" else pd.DataFrame()

    if not cat_df.empty:
        for _, row in cat_df.iterrows():
            pct = (row["total_count"] / cat_df["total_count"].sum() * 100)
            st.markdown(f"""
            <div class="cat-row">
                <span class="cat-name">{row['name']}</span>
                <span class="cat-val">{row['total_count']:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(pct / 100, 1.0))
    else:
        st.markdown(f"""
        <div class="cat-row">
            <span class="cat-name">{count_label}</span>
            <span class="cat-val">{map_total_count:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 5 States (map section) ────────────────────────────────────────────
    st.markdown('<div class="pulse-section-title">🏆 Top 5 States</div>', unsafe_allow_html=True)
    top5 = df_map.nlargest(5, color_col)[["state_display", color_col]]
    fig_top5 = px.bar(
        top5, x=color_col, y="state_display",
        orientation="h",
        color=color_col,
        color_continuous_scale=["#4a2d8e", "#ff6b00"],
        text=top5[color_col].apply(lambda x: f"₹{x/1e7:,.1f}Cr" if map_view != "Users" else f"{x:,.0f}")
    )
    fig_top5.update_traces(textposition="outside")
    fig_top5.update_layout(
        paper_bgcolor="#0e0b1a", plot_bgcolor="#0e0b1a",
        font_color="white", showlegend=False,
        margin={"r": 10, "t": 10, "l": 0, "b": 0},
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"),
        height=280
    )
    st.plotly_chart(fig_top5, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Top Districts & Pincodes ──────────────────────────────────────────────────
dist_col, pin_col = st.columns(2)

with dist_col:
    st.markdown('<div class="pulse-section-title">📍 Top 5 Districts</div>', unsafe_allow_html=True)
    try:
        df_dist = map_top_districts(year, quarter)
        for i, row in df_dist.iterrows():
            st.markdown(f"""
            <div class="top-district-badge">
                <span style="color:#ddd">{row['district'].title()}<br>
                    <small style="color:#888">{row['state']}</small>
                </span>
                <span style="color:#00d4ff; font-weight:700">
                    ₹{row['total_amount']/1e7:,.1f} Cr
                </span>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load district data: {e}")

with pin_col:
    st.markdown('<div class="pulse-section-title">📮 Top 5 Pincodes</div>', unsafe_allow_html=True)
    try:
        df_pin = map_top_pincodes(year, quarter)
        for i, row in df_pin.iterrows():
            st.markdown(f"""
            <div class="top-district-badge">
                <span style="color:#ddd">📮 {row['pincode']}<br>
                    <small style="color:#888">{row['state']}</small>
                </span>
                <span style="color:#00d4ff; font-weight:700">
                    ₹{row['total_amount']/1e7:,.1f} Cr
                </span>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load pincode data: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.caption("Data Source: PhonePe Pulse GitHub Repository | Dashboard built with Streamlit & Plotly")