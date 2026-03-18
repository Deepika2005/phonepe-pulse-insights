"""
PhonePe Pulse — Complete Interactive Streamlit Dashboard
=========================================================
5 Case Studies fully integrated with real-time filters:
  Case 1 : Decoding Transaction Dynamics
  Case 2 : Device Dominance & User Engagement
  Case 3 : Insurance Penetration & Growth
  Case 4 : Transaction Analysis for Market Expansion
  Case 5 : User Engagement & Growth Strategy

+ Home page with KPI summary
+ India Choropleth Map

DB Column Standards (Colab):
  aggregated_transaction : State, Year, Quater, Transacion_type,
                           Transacion_count, Transacion_amount
  aggregated_user        : State, Year, Quater, Brands, Count,
                           Percentage, Registered_user, App_opens
  aggregated_insurance   : State, Year, Quater, Transacion_type,
                           Transacion_count, Transacion_amount
  map_transaction        : State, Year, Quater, District, Count, Amount
  map_user               : State, Year, Quater, District,
                           Registered_user, App_opens
  top_transaction        : State, Year, Quater, EntityType, EntityName,
                           Count, Amount
  top_user               : State, Year, Quater, EntityType, EntityName,
                           Registered_user
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine
import requests
import warnings
warnings.filterwarnings("ignore")

# ═════════════════════════════════════════════════════════════════════════════
#  CONFIG & CONNECTION
# ═════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title  = "PhonePe Pulse Dashboard",
    page_icon   = "💜",
    layout      = "wide",
    initial_sidebar_state = "expanded"
)

@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse"
    )

engine = get_engine()

@st.cache_data(ttl=300)
def q(sql):
    return pd.read_sql(sql, engine)

# ── Check insurance table ─────────────────────────────────────────────────────
try:
    HAS_INS = int(q("SELECT COUNT(*) AS c FROM aggregated_insurance")["c"].iloc[0]) > 0
except Exception:
    HAS_INS = False

# ── GeoJSON state name map (pulse slug → properties.ST_NM) ───────────────────
STATE_MAP = {
    'andaman-&-nicobar-islands':          'Andaman & Nicobar Island',
    'andhra-pradesh':                     'Andhra Pradesh',
    'arunachal-pradesh':                  'Arunachal Pradesh',
    'assam':                              'Assam',
    'bihar':                              'Bihar',
    'chandigarh':                         'Chandigarh',
    'chhattisgarh':                       'Chhattisgarh',
    'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadara & Nagar Havelli',
    'delhi':                              'NCT of Delhi',
    'goa':                                'Goa',
    'gujarat':                            'Gujarat',
    'haryana':                            'Haryana',
    'himachal-pradesh':                   'Himachal Pradesh',
    'jammu-&-kashmir':                    'Jammu & Kashmir',
    'jharkhand':                          'Jharkhand',
    'karnataka':                          'Karnataka',
    'kerala':                             'Kerala',
    'ladakh':                             'Ladakh',
    'lakshadweep':                        'Lakshadweep',
    'madhya-pradesh':                     'Madhya Pradesh',
    'maharashtra':                        'Maharashtra',
    'manipur':                            'Manipur',
    'meghalaya':                          'Meghalaya',
    'mizoram':                            'Mizoram',
    'nagaland':                           'Nagaland',
    'odisha':                             'Odisha',
    'puducherry':                         'Puducherry',
    'punjab':                             'Punjab',
    'rajasthan':                          'Rajasthan',
    'sikkim':                             'Sikkim',
    'tamil-nadu':                         'Tamil Nadu',
    'telangana':                          'Telangana',
    'tripura':                            'Tripura',
    'uttar-pradesh':                      'Uttar Pradesh',
    'uttarakhand':                        'Uttarakhand',
    'west-bengal':                        'West Bengal',
}

PURPLE = "#6739B7"
CYAN   = "#00d4ff"
ORANGE = "#ff6b35"
GREEN  = "#34d399"
YELLOW = "#f59e0b"
PINK   = "#a855f7"
BG     = "#0d0b1e"
CARD   = "#1c1240"
TEXT   = "#e0d8ff"
MUTED  = "#9b8ec4"

PALETTE = [PURPLE, CYAN, ORANGE, PINK, GREEN, YELLOW, "#22d3ee", "#fb7185"]

PLOT_LAYOUT = dict(
    paper_bgcolor = BG,
    plot_bgcolor  = CARD,
    font_color    = TEXT,
    margin        = dict(l=10, r=10, t=40, b=10),
    legend        = dict(bgcolor=CARD, bordercolor=CARD),
    xaxis         = dict(gridcolor="#1e1650"),
    yaxis         = dict(gridcolor="#1e1650"),
)

# ═════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, .stApp { background-color:#0d0b1e; color:#f0eeff;
                     font-family:'Inter',sans-serif; }
section[data-testid="stSidebar"] {
    background-color:#0a0818;
    border-right:1px solid #1e1650;
}
/* KPI cards */
.kpi-grid  { display:grid; grid-template-columns:repeat(4,1fr);
             gap:14px; margin-bottom:20px; }
.kpi-card  { background:#1c1240; border:1px solid #2e1f6e;
             border-radius:14px; padding:18px 20px; }
.kpi-label { color:#9b8ec4; font-size:11px; text-transform:uppercase;
             letter-spacing:.8px; margin-bottom:5px; }
.kpi-value { color:#00d4ff; font-size:24px; font-weight:700; line-height:1.2; }
.kpi-sub   { color:#6b5fa0; font-size:11px; margin-top:3px; }
/* Section title */
.sec-title { color:#00d4ff; font-size:17px; font-weight:700;
             letter-spacing:.3px; margin:20px 0 10px; border-left:3px solid #6739B7;
             padding-left:10px; }
/* Insight card */
.insight   { background:#160f38; border:1px solid #2e1f6e; border-radius:10px;
             padding:14px 18px; margin-bottom:10px; }
.ins-title { color:#00d4ff; font-weight:600; font-size:13px; margin-bottom:4px; }
.ins-body  { color:#ccc6f0; font-size:12px; line-height:1.6; }
/* Rank row */
.rank-row  { display:flex; justify-content:space-between; align-items:center;
             padding:8px 14px; margin-bottom:5px;
             background:#160f38; border-radius:8px; border-left:2px solid #6739B7; }
.rank-num  { color:#6739B7; font-weight:700; width:22px; font-size:13px; }
.rank-name { color:#ddd; flex:1; margin-left:8px; font-size:12px; }
.rank-val  { color:#00d4ff; font-weight:600; font-size:12px; }
/* Tab styling */
div[data-baseweb="tab-list"] { background:#0a0818 !important; }
div[data-baseweb="tab"]      { color:#9b8ec4 !important; }
/* Divider */
.ph-hr { border:none; border-top:1px solid #1e1650; margin:20px 0; }
/* Sidebar nav label */
.nav-label { color:#9b8ec4; font-size:11px; text-transform:uppercase;
             letter-spacing:1px; margin:16px 0 6px; padding-left:4px; }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:16px 0 8px;'>
      <span style='color:#00d4ff; font-size:22px; font-weight:700;'>💜 PhonePe</span><br>
      <span style='color:#6b5fa0; font-size:11px;'>Pulse Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">📍 Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        label="",
        options=[
            "🏠 Home — KPI Overview",
            "🗺️ India Map Explorer",
            "📊 Case 1 : Transaction Dynamics",
            "📱 Case 2 : Device & User Engagement",
            "🛡️ Case 3 : Insurance Penetration",
            "🚀 Case 4 : Market Expansion",
            "👥 Case 5 : User Growth Strategy",
        ],
        label_visibility="collapsed"
    )

    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">🔍 Global Filters</div>', unsafe_allow_html=True)

    all_years = q("SELECT DISTINCT Year FROM aggregated_transaction ORDER BY Year")
    year_list = all_years["Year"].tolist()
    sel_year  = st.selectbox("📅 Year", year_list, index=len(year_list)-1)
    sel_qtr   = st.selectbox("📆 Quarter", [1, 2, 3, 4])

    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
    st.caption("Data: PhonePe Pulse GitHub")


# ═════════════════════════════════════════════════════════════════════════════
#  HELPER: plotly bar / line with dark theme
# ═════════════════════════════════════════════════════════════════════════════
def dark_bar(df, x, y, title, color=PURPLE, h=380,
             xfmt=None, orientation="v", color_col=None, palette=None):
    kwargs = dict(x=x, y=y, title=title,
                  color_discrete_sequence=palette or [color],
                  height=h)
    if color_col:
        kwargs["color"] = color_col
        kwargs["color_discrete_sequence"] = palette or PALETTE
    if orientation == "h":
        kwargs["x"], kwargs["y"] = y, x
        kwargs["orientation"] = "h"
    fig = px.bar(df, **kwargs)
    fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
    if xfmt:
        if orientation == "h":
            fig.update_xaxes(tickformat=xfmt)
        else:
            fig.update_yaxes(tickformat=xfmt)
    return fig

def dark_line(df, x, y, title, color=CYAN, h=340, markers=True):
    fig = px.line(df, x=x, y=y, title=title,
                  markers=markers,
                  color_discrete_sequence=[color],
                  height=h)
    fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
    fig.update_traces(line_width=2.5)
    return fig

def dark_pie(df, names, values, title, h=360):
    fig = px.pie(df, names=names, values=values, title=title,
                 color_discrete_sequence=PALETTE,
                 height=h, hole=0.45)
    fig.update_layout(paper_bgcolor=BG, font_color=TEXT,
                      title_font_color=TEXT,
                      legend=dict(bgcolor=CARD),
                      margin=dict(l=10,r=10,t=40,b=10))
    fig.update_traces(textposition="inside", textinfo="percent+label",
                      marker=dict(line=dict(color=BG, width=2)))
    return fig

def kpi_html(label, value, sub=""):
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def sec(title):
    st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)

def insight(title, body):
    st.markdown(f"""<div class="insight">
        <div class="ins-title">💡 {title}</div>
        <div class="ins-body">{body}</div>
    </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 0 — HOME KPI OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home — KPI Overview":

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1e0f5e,#0d0b1e);
                border:1px solid #2e1f6e; border-radius:16px;
                padding:22px 28px; margin-bottom:22px;'>
      <span style='color:#00d4ff;font-size:28px;font-weight:700;'>💜 PhonePe Pulse</span>
      <span style='color:#6b5fa0;font-size:13px;margin-left:14px;'>| THE BEAT OF PROGRESS</span><br>
      <span style='color:#9b8ec4;font-size:13px;'>
        Interactive Business Intelligence Dashboard — 5 Case Studies
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── All-time KPIs ─────────────────────────────────────────────────────────
    kpi_all = q("""
        SELECT SUM(Transacion_count)  AS total_txn,
               SUM(Transacion_amount) AS total_amt
        FROM   aggregated_transaction
    """)
    kpi_usr = q("SELECT SUM(Registered_user) AS total_users FROM aggregated_user")
    kpi_ins = q("SELECT SUM(Transacion_amount) AS ins_amt FROM aggregated_insurance") \
              if HAS_INS else pd.DataFrame({"ins_amt": [0]})

    total_txn   = int(kpi_all["total_txn"].iloc[0] or 0)
    total_amt   = float(kpi_all["total_amt"].iloc[0] or 0)
    total_users = int(kpi_usr["total_users"].iloc[0] or 0)
    ins_amt     = float(kpi_ins["ins_amt"].iloc[0] or 0)
    avg_val     = total_amt / total_txn if total_txn else 0

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html("Total Transactions (All Time)",
                f"{total_txn/1e9:.2f}B", "UPI + Cards + Wallets")}
      {kpi_html("Total Payment Value",
                f"₹{total_amt/1e7:,.0f} Cr", "Cumulative")}
      {kpi_html("Avg Transaction Value",
                f"₹{avg_val:,.0f}", "Per transaction")}
      {kpi_html("Registered Users",
                f"{total_users/1e6:.1f}M", "All states · all years")}
    </div>
    """, unsafe_allow_html=True)

    # ── Selected Year+Quarter KPIs ────────────────────────────────────────────
    kpi_q = q(f"""
        SELECT SUM(Transacion_count)  AS txn,
               SUM(Transacion_amount) AS amt
        FROM   aggregated_transaction
        WHERE  Year={sel_year} AND Quater={sel_qtr}
    """)
    txn_q = int(kpi_q["txn"].iloc[0] or 0)
    amt_q = float(kpi_q["amt"].iloc[0] or 0)

    kpi_u2 = q(f"""
        SELECT SUM(Registered_user) AS reg,
               SUM(App_opens)       AS opens
        FROM   aggregated_user
        WHERE  Year={sel_year} AND Quater={sel_qtr}
    """)
    reg_q   = int(kpi_u2["reg"].iloc[0] or 0)
    opens_q = int(kpi_u2["opens"].iloc[0] or 0)

    st.markdown(f"<hr class='ph-hr'>", unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">📆 Q{sel_qtr} {sel_year} Snapshot</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html(f"Transactions Q{sel_qtr} {sel_year}",
                f"{txn_q/1e6:.1f}M", "Count")}
      {kpi_html(f"Amount Q{sel_qtr} {sel_year}",
                f"₹{amt_q/1e7:,.0f} Cr", "Payment value")}
      {kpi_html("Registered Users",
                f"{reg_q/1e6:.2f}M", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("App Opens",
                f"{opens_q/1e9:.2f}B", f"Q{sel_qtr} {sel_year}")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Trend overview
    with col1:
        sec("📈 All-time Quarterly Growth")
        df_trend = q("""
            SELECT Year, Quater,
                   SUM(Transacion_count)  AS Transactions,
                   SUM(Transacion_amount) AS Amount
            FROM   aggregated_transaction
            GROUP  BY Year, Quater ORDER BY Year, Quater
        """)
        df_trend["Period"] = df_trend["Year"].astype(str) + " Q" + df_trend["Quater"].astype(str)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_trend["Period"], y=df_trend["Amount"],
                                  mode="lines+markers", name="Amount (₹)",
                                  line=dict(color=PURPLE, width=2.5),
                                  fill="tozeroy", fillcolor="rgba(103,57,183,0.1)",
                                  marker=dict(size=6, color=CYAN)))
        fig.update_layout(**PLOT_LAYOUT, height=320,
                           title="Transaction Amount Growth",
                           title_font_color=TEXT,
                           xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sec("💳 Payment Category Mix")
        df_cat = q(f"""
            SELECT Transacion_type,
                   SUM(Transacion_count) AS Total_Count
            FROM   aggregated_transaction
            WHERE  Year={sel_year} AND Quater={sel_qtr}
            GROUP  BY Transacion_type
            ORDER  BY Total_Count DESC
        """)
        fig = dark_pie(df_cat, "Transacion_type", "Total_Count",
                       f"Category Mix — Q{sel_qtr} {sel_year}")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        sec("🏆 Top 5 States")
        df_t5 = q(f"""
            SELECT State, SUM(Transacion_amount) AS Amt
            FROM   aggregated_transaction
            WHERE  Year={sel_year} AND Quater={sel_qtr}
            GROUP  BY State ORDER BY Amt DESC LIMIT 5
        """)
        for i, row in enumerate(df_t5.itertuples(), 1):
            st.markdown(f"""<div class="rank-row">
              <span class="rank-num">{i}</span>
              <span class="rank-name">{row.State.title()}</span>
              <span class="rank-val">₹{row.Amt/1e7:,.1f} Cr</span>
            </div>""", unsafe_allow_html=True)

    with col4:
        sec("📱 Top 5 Brands")
        df_b5 = q(f"""
            SELECT Brands, SUM(Count) AS Users
            FROM   aggregated_user
            WHERE  Year={sel_year} AND Quater={sel_qtr}
              AND  Brands IS NOT NULL
            GROUP  BY Brands ORDER BY Users DESC LIMIT 5
        """)
        for i, row in enumerate(df_b5.itertuples(), 1):
            st.markdown(f"""<div class="rank-row">
              <span class="rank-num">{i}</span>
              <span class="rank-name">{row.Brands}</span>
              <span class="rank-val">{row.Users/1e6:.2f}M users</span>
            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — INDIA MAP EXPLORER
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ India Map Explorer":

    st.markdown('<div class="sec-title">🗺️ India Transaction Map Explorer</div>',
                unsafe_allow_html=True)

    map_view = st.radio("View by", ["Transactions", "Users", "Insurance"],
                        horizontal=True)

    if map_view == "Transactions":
        df_map = q(f"""
            SELECT State,
                   SUM(Transacion_count)  AS Total_Count,
                   SUM(Transacion_amount) AS Total_Amount
            FROM   aggregated_transaction
            WHERE  Year={sel_year} AND Quater={sel_qtr}
            GROUP  BY State
        """)
        color_col, count_lbl, amt_lbl = "Total_Amount", "Transactions", "Amount (₹)"
    elif map_view == "Users":
        df_map = q(f"""
            SELECT State,
                   SUM(Registered_user) AS Total_Count,
                   SUM(App_opens)       AS Total_Amount
            FROM   aggregated_user
            WHERE  Year={sel_year} AND Quater={sel_qtr}
            GROUP  BY State
        """)
        color_col, count_lbl, amt_lbl = "Total_Count", "Registered Users", "App Opens"
    else:
        if HAS_INS:
            df_map = q(f"""
                SELECT State,
                       SUM(Transacion_count)  AS Total_Count,
                       SUM(Transacion_amount) AS Total_Amount
                FROM   aggregated_insurance
                WHERE  Year={sel_year} AND Quater={sel_qtr}
                GROUP  BY State
            """)
        else:
            df_map = pd.DataFrame(columns=["State","Total_Count","Total_Amount"])
        color_col, count_lbl, amt_lbl = "Total_Amount", "Policies", "Amount (₹)"

    df_map["State_Display"] = df_map["State"].map(STATE_MAP).fillna(df_map["State"])

    mc = df_map["Total_Count"].sum()
    ma = df_map["Total_Amount"].sum()

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html(f"{map_view} Count", f"{mc:,.0f}", count_lbl)}
      {kpi_html("Total Value", f"₹{ma/1e7:,.0f} Cr", "")}
      {kpi_html("Avg per Transaction", f"₹{ma/mc:,.0f}" if mc else "—", "")}
      {kpi_html("States Active", f"{df_map['State'].nunique()}", "")}
    </div>
    """, unsafe_allow_html=True)

    map_col, side_col = st.columns([2.2, 1])
    with map_col:
        GEOJSON_URL = ("https://gist.githubusercontent.com/jbrobst/"
                       "56c13bbbf9d97d187fea01ca62ea5112/raw/"
                       "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
        try:
            geojson = requests.get(GEOJSON_URL, timeout=10).json()
            fig = px.choropleth(
                df_map, geojson=geojson,
                featureidkey="properties.ST_NM",
                locations="State_Display",
                color=color_col,
                hover_name="State_Display",
                hover_data={"Total_Count": True, "Total_Amount": True,
                            color_col: False},
                color_continuous_scale=["#0d0b1e","#2e1f6e","#6739B7",
                                        "#ff6b35","#ffd700"],
                labels={"Total_Count": count_lbl, "Total_Amount": amt_lbl},
                height=520
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(paper_bgcolor=BG, geo_bgcolor=BG,
                               font_color=TEXT, margin=dict(r=0,t=10,l=0,b=0),
                               coloraxis_colorbar=dict(
                                   tickfont=dict(color=TEXT),
                                   titlefont=dict(color=TEXT)))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Map unavailable — check internet connection.\n{e}")
            fig_fb = px.bar(df_map.nlargest(15, color_col),
                            x="State_Display", y=color_col,
                            color=color_col,
                            color_continuous_scale=["#2e1f6e","#00d4ff"])
            fig_fb.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig_fb, use_container_width=True)

    with side_col:
        sec(f"🏆 Top 10 States")
        top10 = df_map.nlargest(10, color_col).reset_index(drop=True)
        for i, row in top10.iterrows():
            st.markdown(f"""<div class="rank-row">
              <span class="rank-num">{i+1}</span>
              <span class="rank-name">{row['State_Display']}</span>
              <span class="rank-val">₹{row['Total_Amount']/1e7:,.1f}Cr</span>
            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  CASE 1 — TRANSACTION DYNAMICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📊 Case 1 : Transaction Dynamics":

    st.markdown('<div class="sec-title">📊 Case 1 — Decoding Transaction Dynamics</div>',
                unsafe_allow_html=True)
    st.caption("Understand variation in transaction behavior across states, quarters & payment categories.")

    # KPIs
    k = q(f"""SELECT SUM(Transacion_count) AS tc, SUM(Transacion_amount) AS ta
              FROM aggregated_transaction WHERE Year={sel_year} AND Quater={sel_qtr}""")
    tc, ta = int(k["tc"].iloc[0] or 0), float(k["ta"].iloc[0] or 0)
    st.markdown(f"""<div class="kpi-grid">
      {kpi_html("Transactions", f"{tc/1e6:.2f}M", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Total Amount", f"₹{ta/1e7:,.0f}Cr", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Avg Value", f"₹{ta/tc:,.0f}" if tc else "—", "Per transaction")}
      {kpi_html("States Covered", "36", "All states")}
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "💳 Category Breakdown",
        "🏆 State Performance",
        "📈 Growth Trends",
        "🔍 Deep Dive"
    ])

    with tab1:
        df_type = q(f"""
            SELECT Transacion_type,
                   SUM(Transacion_count)  AS Total_Count,
                   SUM(Transacion_amount) AS Total_Amount,
                   ROUND(SUM(Transacion_count)*100.0
                         /SUM(SUM(Transacion_count)) OVER(),2) AS Count_Pct,
                   ROUND(SUM(Transacion_amount)*100.0
                         /SUM(SUM(Transacion_amount)) OVER(),2) AS Amount_Pct
            FROM aggregated_transaction
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY Transacion_type ORDER BY Total_Amount DESC
        """)
        c1, c2 = st.columns(2)
        with c1:
            fig = dark_pie(df_type, "Transacion_type", "Total_Count",
                           "Transaction Count Share")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = dark_bar(df_type, "Total_Amount", "Transacion_type",
                           "Transaction Amount by Type",
                           orientation="h", color_col="Transacion_type")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        # Table
        sec("📋 Category Details")
        display_df = df_type.copy()
        display_df["Total_Amount"] = display_df["Total_Amount"].apply(
            lambda x: f"₹{x/1e7:,.1f} Cr")
        display_df["Total_Count"] = display_df["Total_Count"].apply(
            lambda x: f"{x/1e6:.2f}M")
        st.dataframe(display_df.rename(columns={
            "Transacion_type":  "Payment Type",
            "Total_Count":      "Transaction Count",
            "Total_Amount":     "Amount",
            "Count_Pct":        "Count Share %",
            "Amount_Pct":       "Amount Share %"
        }), use_container_width=True, hide_index=True)

        insight("Dominant Payment Type",
                f"'{df_type.iloc[0]['Transacion_type']}' leads with "
                f"{df_type.iloc[0]['Amount_Pct']}% of total transaction amount "
                f"in Q{sel_qtr} {sel_year}.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            df_top = q(f"""
                SELECT State, SUM(Transacion_amount) AS Total_Amount,
                       SUM(Transacion_count) AS Total_Count
                FROM aggregated_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY State ORDER BY Total_Amount DESC LIMIT 10
            """)
            fig = dark_bar(df_top.sort_values("Total_Amount"),
                           "Total_Amount", "State",
                           "🏆 Top 10 States by Amount",
                           orientation="h", color_col="State")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_bot = q(f"""
                SELECT State, SUM(Transacion_amount) AS Total_Amount
                FROM aggregated_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY State ORDER BY Total_Amount ASC LIMIT 10
            """)
            fig = dark_bar(df_bot, "Total_Amount", "State",
                           "⚠️ Bottom 10 States (Low Adoption)",
                           color=ORANGE, orientation="h")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        # Most popular type per state
        sec("💳 Most Popular Payment Type per State")
        df_pop = q("""
            SELECT t1.State, t1.Transacion_type, t1.Total_Count
            FROM (
                SELECT State, Transacion_type,
                       SUM(Transacion_count) AS Total_Count,
                       RANK() OVER (PARTITION BY State
                                    ORDER BY SUM(Transacion_count) DESC) AS rnk
                FROM aggregated_transaction
                GROUP BY State, Transacion_type
            ) t1 WHERE t1.rnk=1 ORDER BY Total_Count DESC
        """)
        fig = px.treemap(df_pop, path=["Transacion_type","State"],
                         values="Total_Count",
                         color="Transacion_type",
                         color_discrete_sequence=PALETTE,
                         height=400)
        fig.update_layout(paper_bgcolor=BG, font_color=TEXT,
                           margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df_qtr = q("""
            SELECT Year, Quater,
                   SUM(Transacion_count)  AS Transactions,
                   SUM(Transacion_amount) AS Amount
            FROM aggregated_transaction
            GROUP BY Year, Quater ORDER BY Year, Quater
        """)
        df_qtr["Period"] = (df_qtr["Year"].astype(str)
                             + " Q" + df_qtr["Quater"].astype(str))

        c1, c2 = st.columns(2)
        with c1:
            fig = dark_line(df_qtr, "Period", "Transactions",
                            "📈 Transaction Count Growth", color=PURPLE)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = dark_line(df_qtr, "Period", "Amount",
                            "💰 Transaction Amount Growth", color=CYAN)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        # Yearly YoY
        df_yoy = q("""
            SELECT Year,
                   SUM(Transacion_amount) AS Amount,
                   ROUND((SUM(Transacion_amount)
                          - LAG(SUM(Transacion_amount)) OVER (ORDER BY Year))
                         / LAG(SUM(Transacion_amount)) OVER (ORDER BY Year)*100,2
                   ) AS YoY_Growth
            FROM aggregated_transaction
            GROUP BY Year ORDER BY Year
        """)
        fig = px.bar(df_yoy.dropna(), x="Year", y="YoY_Growth",
                     title="📊 Year-on-Year Growth (%)",
                     color="YoY_Growth",
                     color_continuous_scale=["#ff6b35","#6739B7","#00d4ff"],
                     height=320)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        # Type × Year grouped
        df_ty = q("""
            SELECT Year, Transacion_type,
                   ROUND(SUM(Transacion_amount)/1e7,2) AS Amount_Cr
            FROM aggregated_transaction
            GROUP BY Year, Transacion_type ORDER BY Year
        """)
        fig = px.bar(df_ty, x="Year", y="Amount_Cr",
                     color="Transacion_type",
                     barmode="group",
                     title="Transaction Type Trend per Year (₹ Crore)",
                     color_discrete_sequence=PALETTE, height=380)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        st.plotly_chart(fig, use_container_width=True)

        # Declining states
        sec("⚠️ States with Declining Transactions (YoY)")
        df_dec = q("""
            WITH y AS (SELECT State,Year,SUM(Transacion_amount) AS Amt
                       FROM aggregated_transaction GROUP BY State,Year)
            SELECT c.State, c.Year,
                   ROUND((c.Amt-p.Amt)/p.Amt*100,2) AS Growth_Pct
            FROM y c JOIN y p ON c.State=p.State AND c.Year=p.Year+1
            WHERE c.Amt < p.Amt ORDER BY Growth_Pct ASC LIMIT 10
        """)
        if not df_dec.empty:
            fig = px.bar(df_dec, x="State", y="Growth_Pct",
                         color="Growth_Pct",
                         color_continuous_scale=["#ff6b35","#6739B7"],
                         title="YoY Growth % (Negative = Decline)", height=340)
            fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No declining states found.")


# ═════════════════════════════════════════════════════════════════════════════
#  CASE 2 — DEVICE & USER ENGAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📱 Case 2 : Device & User Engagement":

    st.markdown('<div class="sec-title">📱 Case 2 — Device Dominance & User Engagement</div>',
                unsafe_allow_html=True)
    st.caption("Brand preferences, engagement ratios & underutilised regions.")

    ku = q(f"""SELECT SUM(Registered_user) AS reg, SUM(App_opens) AS opens
               FROM aggregated_user WHERE Year={sel_year} AND Quater={sel_qtr}""")
    reg = int(ku["reg"].iloc[0] or 0)
    opn = int(ku["opens"].iloc[0] or 0)
    eng = round(opn / reg, 1) if reg else 0

    st.markdown(f"""<div class="kpi-grid">
      {kpi_html("Registered Users", f"{reg/1e6:.2f}M", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Total App Opens", f"{opn/1e9:.2f}B", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Engagement Ratio", f"{eng}x", "Opens per user")}
      {kpi_html("Device Brands", "10+", "Tracked")}
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📱 Brand Analysis",
        "📍 Regional Engagement",
        "📈 Growth Trends"
    ])

    with tab1:
        df_brands = q(f"""
            SELECT Brands, SUM(Count) AS Total_Users,
                   ROUND(SUM(Count)*100.0/SUM(SUM(Count)) OVER(),2) AS Share_Pct
            FROM aggregated_user
            WHERE Year={sel_year} AND Quater={sel_qtr} AND Brands IS NOT NULL
            GROUP BY Brands ORDER BY Total_Users DESC LIMIT 10
        """)
        c1, c2 = st.columns(2)
        with c1:
            fig = dark_pie(df_brands, "Brands", "Total_Users",
                           f"Brand Market Share — Q{sel_qtr} {sel_year}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = dark_bar(df_brands.sort_values("Total_Users"),
                           "Total_Users", "Brands",
                           "Users per Brand", orientation="h",
                           color_col="Brands")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        insight("Brand Dominance",
                f"'{df_brands.iloc[0]['Brands']}' leads with "
                f"{df_brands.iloc[0]['Share_Pct']}% market share "
                f"in Q{sel_qtr} {sel_year}.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            df_su = q(f"""
                SELECT State,
                       SUM(Registered_user) AS Registered,
                       SUM(App_opens)       AS App_Opens,
                       ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Ratio
                FROM aggregated_user
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY State ORDER BY Registered DESC LIMIT 10
            """)
            x = list(range(len(df_su)))
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_su["State"], y=df_su["Registered"],
                                  name="Registered Users", marker_color=PURPLE))
            fig.add_trace(go.Bar(x=df_su["State"], y=df_su["App_Opens"],
                                  name="App Opens", marker_color=CYAN))
            fig.update_layout(**PLOT_LAYOUT, barmode="group",
                               title="Registered vs App Opens (Top 10)",
                               title_font_color=TEXT, height=380,
                               xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_low = q(f"""
                SELECT State,
                       ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Ratio,
                       SUM(Registered_user) AS Registered
                FROM aggregated_user
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY State
                HAVING Eng_Ratio < (
                    SELECT ROUND(AVG(App_opens/Registered_user),2)
                    FROM aggregated_user
                    WHERE Year={sel_year} AND Quater={sel_qtr}
                      AND Registered_user > 0
                )
                ORDER BY Registered DESC LIMIT 10
            """)
            fig = dark_bar(df_low.sort_values("Eng_Ratio"),
                           "Eng_Ratio", "State",
                           "⚠️ Low Engagement States",
                           color=ORANGE, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

        # Engagement scatter
        sec("🎯 Registered Users vs Engagement Score")
        df_scat = q("""
            SELECT State,
                   SUM(Registered_user) AS Registered,
                   ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Ratio
            FROM aggregated_user GROUP BY State
        """)
        fig = px.scatter(df_scat, x="Registered", y="Eng_Ratio",
                         text="State", size="Registered",
                         color="Eng_Ratio",
                         color_continuous_scale=["#ff6b35","#6739B7","#00d4ff"],
                         title="Users vs Engagement (size = user count)",
                         height=400)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        fig.update_traces(textposition="top center", textfont_size=8)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df_ut = q("""
            SELECT Year, Quater,
                   SUM(Registered_user) AS Registered,
                   SUM(App_opens)       AS App_Opens
            FROM aggregated_user GROUP BY Year, Quater ORDER BY Year, Quater
        """)
        df_ut["Period"] = df_ut["Year"].astype(str) + " Q" + df_ut["Quater"].astype(str)

        c1, c2 = st.columns(2)
        with c1:
            fig = dark_line(df_ut, "Period", "Registered",
                            "📈 Registered Users Growth", PURPLE)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = dark_line(df_ut, "Period", "App_Opens",
                            "📲 App Opens Growth", GREEN)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        # Top brand per year
        df_by = q("""
            SELECT Brands, Year, SUM(Count) AS Users
            FROM aggregated_user WHERE Brands IS NOT NULL
            GROUP BY Brands, Year ORDER BY Year, Users DESC
        """)
        top5b = q("""
            SELECT Brands FROM aggregated_user
            WHERE Brands IS NOT NULL
            GROUP BY Brands ORDER BY SUM(Count) DESC LIMIT 5
        """)["Brands"].tolist()
        df_by = df_by[df_by["Brands"].isin(top5b)]
        fig = px.line(df_by, x="Year", y="Users",
                      color="Brands",
                      markers=True,
                      color_discrete_sequence=PALETTE,
                      title="Top 5 Brands — Year-wise Growth",
                      height=360)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  CASE 3 — INSURANCE PENETRATION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🛡️ Case 3 : Insurance Penetration":

    st.markdown('<div class="sec-title">🛡️ Case 3 — Insurance Penetration & Growth Potential</div>',
                unsafe_allow_html=True)
    st.caption("Growth trajectory & untapped opportunities for insurance adoption.")

    if not HAS_INS:
        st.warning("⚠️ Insurance table is empty or not found in the database.")
        st.stop()

    ki = q(f"""SELECT SUM(Transacion_count) AS cnt,
                      SUM(Transacion_amount) AS amt
               FROM aggregated_insurance WHERE Year={sel_year} AND Quater={sel_qtr}""")
    ic  = int(ki["cnt"].iloc[0] or 0)
    ia  = float(ki["amt"].iloc[0] or 0)
    kt  = q(f"""SELECT SUM(Transacion_amount) AS ta FROM aggregated_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}""")
    ta  = float(kt["ta"].iloc[0] or 1)
    pen = round(ia / ta * 100, 4)

    st.markdown(f"""<div class="kpi-grid">
      {kpi_html("Insurance Policies", f"{ic/1e3:,.0f}K", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Insurance Amount", f"₹{ia/1e7:,.0f}Cr", f"Q{sel_qtr} {sel_year}")}
      {kpi_html("Penetration Rate", f"{pen}%", "vs total transactions")}
      {kpi_html("Avg Premium", f"₹{ia/ic:,.0f}" if ic else "—", "Per policy")}
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 State Analysis",
        "📈 Growth Trend",
        "🔍 Penetration & Untapped"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            df_is = q(f"""
                SELECT State,
                       SUM(Transacion_count)  AS Policies,
                       SUM(Transacion_amount) AS Amount
                FROM aggregated_insurance
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY State ORDER BY Amount DESC LIMIT 10
            """)
            fig = dark_pie(df_is, "State", "Amount",
                           f"Insurance Amount — Top 10 States")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = dark_bar(df_is.sort_values("Amount"),
                           "Amount", "State",
                           "Top 10 States by Insurance Amount",
                           orientation="h", color_col="State")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_it = q("""
            SELECT Year, Quater,
                   SUM(Transacion_count)  AS Policies,
                   SUM(Transacion_amount) AS Amount
            FROM aggregated_insurance
            GROUP BY Year, Quater ORDER BY Year, Quater
        """)
        df_it["Period"] = df_it["Year"].astype(str) + " Q" + df_it["Quater"].astype(str)

        c1, c2 = st.columns(2)
        with c1:
            fig = dark_line(df_it, "Period", "Policies",
                            "Insurance Policy Count Trend", GREEN)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = dark_line(df_it, "Period", "Amount",
                            "Insurance Amount Trend (₹)", YELLOW)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        # YoY growth
        df_iyoy = q("""
            SELECT Year, SUM(Transacion_amount) AS Amt,
                   ROUND((SUM(Transacion_amount)
                          - LAG(SUM(Transacion_amount)) OVER (ORDER BY Year))
                         / LAG(SUM(Transacion_amount)) OVER (ORDER BY Year)*100,2
                   ) AS YoY
            FROM aggregated_insurance GROUP BY Year ORDER BY Year
        """)
        fig = px.bar(df_iyoy.dropna(), x="Year", y="YoY",
                     title="Insurance YoY Growth (%)",
                     color="YoY",
                     color_continuous_scale=["#ff6b35","#34d399"], height=300)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df_pen = q("""
            SELECT t.State,
                   ROUND(SUM(i.Transacion_amount)/SUM(t.Transacion_amount)*100,4)
                     AS Penetration_Pct
            FROM aggregated_transaction t
            JOIN aggregated_insurance i
              ON t.State=i.State AND t.Year=i.Year AND t.Quater=i.Quater
            GROUP BY t.State ORDER BY Penetration_Pct DESC LIMIT 10
        """)
        c1, c2 = st.columns(2)
        with c1:
            fig = dark_bar(df_pen.sort_values("Penetration_Pct"),
                           "Penetration_Pct", "State",
                           "Insurance Penetration Rate (%)",
                           orientation="h", color_col="State")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_unt = q("""
                SELECT State, SUM(Transacion_count) AS Policies
                FROM aggregated_insurance
                GROUP BY State ORDER BY Policies ASC LIMIT 10
            """)
            fig = dark_bar(df_unt.sort_values("Policies"),
                           "Policies", "State",
                           "⚠️ Untapped Markets (Lowest Policies)",
                           color=ORANGE, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

        insight("Highest Penetration",
                f"'{df_pen.iloc[0]['State']}' has the highest insurance "
                f"penetration at {df_pen.iloc[0]['Penetration_Pct']}% "
                f"of total transactions.")
        insight("Untapped Opportunity",
                f"States like '{df_unt.iloc[0]['State']}' have very low "
                f"insurance adoption and represent key growth targets.")


# ═════════════════════════════════════════════════════════════════════════════
#  CASE 4 — MARKET EXPANSION
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🚀 Case 4 : Market Expansion":

    st.markdown('<div class="sec-title">🚀 Case 4 — Transaction Analysis for Market Expansion</div>',
                unsafe_allow_html=True)
    st.caption("Identify expansion opportunities, high-growth states & top districts.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 State Rankings",
        "🎯 Expansion Targets",
        "📍 Districts & Pincodes",
        "📊 Type Analysis"
    ])

    with tab1:
        df_rank = q(f"""
            SELECT State,
                   SUM(Transacion_count)  AS Total_Txn,
                   SUM(Transacion_amount) AS Total_Amt,
                   ROUND(SUM(Transacion_amount)/SUM(Transacion_count),2) AS Avg_Val,
                   RANK() OVER (ORDER BY SUM(Transacion_amount) DESC) AS Rank_Amt
            FROM aggregated_transaction
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY State ORDER BY Rank_Amt
        """)

        c1, c2 = st.columns(2)
        with c1:
            top15a = df_rank.head(15).sort_values("Total_Amt")
            fig = dark_bar(top15a, "Total_Amt", "State",
                           "By Transaction Amount",
                           orientation="h", color_col="State")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            top15c = df_rank.sort_values("Total_Txn", ascending=False).head(15)
            top15c = top15c.sort_values("Total_Txn")
            fig = dark_bar(top15c, "Total_Txn", "State",
                           "By Transaction Count",
                           orientation="h", color_col="State")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        sec("📋 Full State Ranking Table")
        disp = df_rank[["Rank_Amt","State","Total_Txn","Total_Amt","Avg_Val"]].copy()
        disp["Total_Amt"] = disp["Total_Amt"].apply(lambda x: f"₹{x/1e7:,.1f}Cr")
        disp["Total_Txn"] = disp["Total_Txn"].apply(lambda x: f"{x/1e6:.2f}M")
        disp["Avg_Val"]   = disp["Avg_Val"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(disp.rename(columns={
            "Rank_Amt":"Rank", "Total_Txn":"Transactions",
            "Total_Amt":"Amount", "Avg_Val":"Avg Value"
        }), use_container_width=True, hide_index=True)

    with tab2:
        df_exp = q(f"""
            SELECT State,
                   SUM(Transacion_count)  AS Total_Count,
                   SUM(Transacion_amount) AS Total_Amt,
                   ROUND(SUM(Transacion_amount)/SUM(Transacion_count),2) AS Avg_Val
            FROM aggregated_transaction
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY State
            HAVING Avg_Val < (
                SELECT SUM(Transacion_amount)/SUM(Transacion_count)
                FROM aggregated_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}
            )
            ORDER BY Total_Count DESC LIMIT 10
        """)

        c1, c2 = st.columns(2)
        with c1:
            fig = dark_bar(df_exp.sort_values("Total_Count"),
                           "Total_Count", "State",
                           "High Volume States (Expansion Targets)",
                           orientation="h", color_col="State")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = dark_bar(df_exp.sort_values("Avg_Val"),
                           "Avg_Val", "State",
                           "Below National Avg Transaction Value",
                           color=ORANGE, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

        # Emerging states
        sec("🌱 Emerging States — Highest Growth")
        df_emer = q("""
            WITH sy AS (SELECT State, Year,
                               SUM(Transacion_amount) AS Amt
                        FROM aggregated_transaction GROUP BY State, Year),
            base AS (SELECT MIN(Year) AS min_yr FROM aggregated_transaction)
            SELECT c.State,
                   ROUND((c.Amt-p.Amt)/p.Amt*100,2) AS Growth_Pct,
                   p.Amt AS Base_Amt
            FROM sy c JOIN sy p ON c.State=p.State AND c.Year=p.Year+1,
            base
            WHERE p.Year=base.min_yr
            ORDER BY Growth_Pct DESC LIMIT 10
        """)
        fig = px.bar(df_emer, x="State", y="Growth_Pct",
                     color="Growth_Pct",
                     title="Emerging States — Growth from Base Year",
                     color_continuous_scale=["#6739B7","#00d4ff","#34d399"],
                     height=360)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT,
                           xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

        insight("Expansion Insight",
                f"States with high transaction volumes but below-average "
                f"transaction values are prime targets for value-added "
                f"financial products and premium service upselling.")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            df_dist = q(f"""
                SELECT District, State,
                       SUM(Count)  AS Total_Txn,
                       SUM(Amount) AS Total_Amt
                FROM map_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY District, State
                ORDER BY Total_Amt DESC LIMIT 10
            """)
            df_dist["Label"] = df_dist["District"].str.title() + " (" + df_dist["State"] + ")"
            fig = dark_bar(df_dist.sort_values("Total_Amt"),
                           "Total_Amt", "Label",
                           "Top 10 Districts by Amount",
                           orientation="h", color_col="Label")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_pin = q(f"""
                SELECT EntityName AS Pincode, State,
                       SUM(Amount) AS Total_Amt
                FROM top_transaction
                WHERE Year={sel_year} AND Quater={sel_qtr}
                  AND EntityType='Pincode'
                GROUP BY EntityName, State
                ORDER BY Total_Amt DESC LIMIT 10
            """)
            df_pin["Label"] = df_pin["Pincode"].astype(str) + " (" + df_pin["State"] + ")"
            fig = dark_bar(df_pin.sort_values("Total_Amt"),
                           "Total_Amt", "Label",
                           "Top 10 Pincodes by Amount",
                           orientation="h", color_col="Label")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        df_t5t = q(f"""
            SELECT Transacion_type, State,
                   SUM(Transacion_amount) AS Total_Amt
            FROM aggregated_transaction
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY Transacion_type, State
            ORDER BY Transacion_type, Total_Amt DESC
        """)
        sel_type = st.selectbox("Select Payment Type",
                                df_t5t["Transacion_type"].unique())
        df_filt = df_t5t[df_t5t["Transacion_type"] == sel_type].head(10)
        fig = dark_bar(df_filt.sort_values("Total_Amt"),
                       "Total_Amt", "State",
                       f"Top 10 States — {sel_type}",
                       orientation="h", color_col="State")
        fig.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
#  CASE 5 — USER GROWTH STRATEGY
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👥 Case 5 : User Growth Strategy":

    st.markdown('<div class="sec-title">👥 Case 5 — User Engagement & Growth Strategy</div>',
                unsafe_allow_html=True)
    st.caption("Engagement scores, top districts, YoY growth & strategic recommendations.")

    tab1, tab2, tab3 = st.tabs([
        "🎯 Engagement Scores",
        "📍 District & Pincode",
        "📈 Growth Analysis"
    ])

    with tab1:
        df_eng = q(f"""
            SELECT State,
                   SUM(Registered_user) AS Registered,
                   SUM(App_opens)       AS App_Opens,
                   ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Score,
                   CASE
                       WHEN SUM(App_opens)/SUM(Registered_user) >= 50 THEN 'High'
                       WHEN SUM(App_opens)/SUM(Registered_user) >= 20 THEN 'Medium'
                       ELSE 'Low'
                   END AS Category
            FROM aggregated_user
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY State ORDER BY Eng_Score DESC
        """)

        # Engagement score bar colored by category
        cat_color = {"High": GREEN, "Medium": YELLOW, "Low": ORANGE}
        df_eng["Color"] = df_eng["Category"].map(cat_color)

        fig = px.bar(df_eng.sort_values("Eng_Score"),
                     x="Eng_Score", y="State",
                     color="Category",
                     orientation="h",
                     color_discrete_map=cat_color,
                     title=f"Engagement Score — All States (Q{sel_qtr} {sel_year})",
                     height=700)
        fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
        st.plotly_chart(fig, use_container_width=True)

        # Category distribution
        c1, c2 = st.columns(2)
        cat_cnt = df_eng["Category"].value_counts().reset_index()
        cat_cnt.columns = ["Category", "Count"]
        with c1:
            fig = dark_pie(cat_cnt, "Category", "Count",
                           "Engagement Category Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            high_ct  = len(df_eng[df_eng["Category"]=="High"])
            med_ct   = len(df_eng[df_eng["Category"]=="Medium"])
            low_ct   = len(df_eng[df_eng["Category"]=="Low"])
            top_eng  = df_eng.iloc[0]["State"]
            top_sc   = df_eng.iloc[0]["Eng_Score"]
            insight("Engagement Summary",
                    f"<b style='color:{GREEN}'>High:</b> {high_ct} states &nbsp;|&nbsp; "
                    f"<b style='color:{YELLOW}'>Medium:</b> {med_ct} states &nbsp;|&nbsp; "
                    f"<b style='color:{ORANGE}'>Low:</b> {low_ct} states<br>"
                    f"Top state: <b style='color:{CYAN}'>{top_eng.title()}</b> "
                    f"with score {top_sc}x")
            insight("Strategy Recommendation",
                    "Low-engagement states have registered users but minimal "
                    "activity. Target them with push notifications, cashback "
                    "offers & offline campaigns to improve retention.")

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            df_td = q(f"""
                SELECT District, State,
                       SUM(Registered_user) AS Registered,
                       SUM(App_opens)       AS App_Opens,
                       ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Score
                FROM map_user
                WHERE Year={sel_year} AND Quater={sel_qtr}
                GROUP BY District, State
                ORDER BY Registered DESC LIMIT 10
            """)
            df_td["Label"] = df_td["District"].str.title() + " (" + df_td["State"] + ")"
            fig = dark_bar(df_td.sort_values("Registered"),
                           "Registered", "Label",
                           "Top 10 Districts by Registered Users",
                           orientation="h", color_col="Label")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df_tp = q(f"""
                SELECT EntityName AS Pincode, State,
                       SUM(Registered_user) AS Registered
                FROM top_user
                WHERE Year={sel_year} AND Quater={sel_qtr}
                  AND EntityType='Pincode'
                GROUP BY EntityName, State
                ORDER BY Registered DESC LIMIT 10
            """)
            df_tp["Label"] = df_tp["Pincode"].astype(str) + " (" + df_tp["State"] + ")"
            fig = dark_bar(df_tp.sort_values("Registered"),
                           "Registered", "Label",
                           "Top 10 Pincodes by Registered Users",
                           orientation="h", color_col="Label")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

        # Low engagement districts
        sec("⚠️ Low Engagement Districts (High Users, Low Opens)")
        df_ld = q(f"""
            SELECT District, State,
                   SUM(Registered_user) AS Registered,
                   ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng_Score
            FROM map_user
            WHERE Year={sel_year} AND Quater={sel_qtr}
            GROUP BY District, State
            HAVING Registered > 10000 AND Eng_Score < 5
            ORDER BY Registered DESC LIMIT 10
        """)
        if not df_ld.empty:
            df_ld["Label"] = df_ld["District"].str.title() + " (" + df_ld["State"] + ")"
            fig = dark_bar(df_ld, "Registered", "Label",
                           "High-User Low-Engagement Districts",
                           color=ORANGE, orientation="h")
            fig.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No low-engagement districts found with current filters.")

    with tab3:
        # YoY user growth
        df_uyoy = q("""
            WITH uy AS (SELECT State, Year,
                               SUM(Registered_user) AS Users
                        FROM aggregated_user GROUP BY State, Year)
            SELECT c.State, c.Year,
                   c.Users AS Current_Users,
                   ROUND((c.Users-p.Users)/p.Users*100,2) AS Growth_Pct
            FROM uy c JOIN uy p ON c.State=p.State AND c.Year=p.Year+1
            ORDER BY Growth_Pct DESC LIMIT 10
        """)
        c1, c2 = st.columns(2)
        with c1:
            fig = dark_bar(df_uyoy.sort_values("Growth_Pct"),
                           "Growth_Pct",
                           df_uyoy["State"] + " (" + df_uyoy["Year"].astype(str) + ")",
                           "Top 10 States — YoY User Growth (%)",
                           color=GREEN, orientation="h")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            # Txn per user correlation
            df_corr = q("""
                SELECT t.State,
                       ROUND(SUM(t.Transacion_count)/SUM(u.Registered_user),2) AS Txn_Per_User,
                       ROUND(SUM(u.App_opens)/SUM(u.Registered_user),2) AS Opens_Per_User
                FROM aggregated_transaction t
                JOIN aggregated_user u
                  ON t.State=u.State AND t.Year=u.Year AND t.Quater=u.Quater
                GROUP BY t.State ORDER BY Txn_Per_User DESC LIMIT 15
            """)
            fig = px.scatter(df_corr, x="Txn_Per_User", y="Opens_Per_User",
                             text="State", size="Txn_Per_User",
                             color="Opens_Per_User",
                             color_continuous_scale=["#6739B7","#00d4ff"],
                             title="Transactions vs App Opens per User",
                             height=380)
            fig.update_layout(**PLOT_LAYOUT, title_font_color=TEXT)
            fig.update_traces(textposition="top center", textfont_size=7.5)
            st.plotly_chart(fig, use_container_width=True)

        # Quarterly new users
        df_qnew = q("""
            SELECT Year, Quater,
                   SUM(Registered_user) AS New_Users
            FROM aggregated_user GROUP BY Year, Quater ORDER BY Year, Quater
        """)
        df_qnew["Period"] = (df_qnew["Year"].astype(str)
                              + " Q" + df_qnew["Quater"].astype(str))
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_qnew["Period"], y=df_qnew["New_Users"],
                              marker_color=PURPLE, name="Registered Users",
                              opacity=0.8))
        fig.add_trace(go.Scatter(x=df_qnew["Period"], y=df_qnew["New_Users"],
                                  mode="lines+markers", name="Trend",
                                  line=dict(color=CYAN, width=2),
                                  marker=dict(size=6)))
        fig.update_layout(**PLOT_LAYOUT, height=340,
                           title="Quarterly User Registration Trend",
                           title_font_color=TEXT,
                           xaxis_tickangle=-45, barmode="overlay")
        st.plotly_chart(fig, use_container_width=True)

        insight("Growth Strategy",
                "States with high YoY growth indicate strong organic adoption. "
                "Leverage these regions for referral programs & brand partnerships. "
                "States with high transactions-per-user are monetisation hotspots.")