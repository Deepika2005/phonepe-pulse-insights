import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import requests
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="PhonePe Pulse",page_icon="💜",layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html,body,.stApp{background-color:#120f2d!important;font-family:'Inter',sans-serif;color:#e8e0ff;}
section[data-testid="stSidebar"]{background-color:#0b0920!important;border-right:1px solid #1e1a4a;}
.pp-header{background:linear-gradient(135deg,#1e0f5e 0%,#120f2d 100%);border:1px solid #2e1f6e;
  border-radius:14px;padding:18px 28px;margin-bottom:18px;}
.pp-logo{color:#00d4ff;font-size:24px;font-weight:700;}
.pp-sub{color:#6b5fa0;font-size:11px;letter-spacing:1px;}
.kpi-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px;}
.kpi-box{background:#1c1240;border:1px solid #2e1f6e;border-radius:12px;padding:16px 18px;}
.kpi-lbl{color:#9b8ec4;font-size:11px;text-transform:uppercase;letter-spacing:.7px;margin-bottom:4px;}
.kpi-val{color:#00d4ff;font-size:22px;font-weight:700;line-height:1.2;}
.kpi-sub{color:#4a3f80;font-size:10px;margin-top:2px;}
.sec-hd{color:#00d4ff;font-size:16px;font-weight:700;letter-spacing:.3px;margin:16px 0 10px;
  border-left:3px solid #6739B7;padding-left:10px;}
.cat-row{display:flex;justify-content:space-between;align-items:center;background:#1a1040;
  border-left:3px solid #6739B7;border-radius:8px;padding:10px 14px;margin-bottom:7px;}
.cat-name{color:#ccc6f0;font-size:12px;}
.cat-val{color:#00d4ff;font-weight:700;font-size:13px;}
.rk-row{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;
  margin-bottom:5px;background:#160f38;border-radius:8px;border-left:2px solid #6739B7;}
.rk-num{color:#6739B7;font-weight:700;width:20px;font-size:12px;}
.rk-name{color:#ccc6f0;flex:1;margin-left:8px;font-size:12px;}
.rk-val{color:#00d4ff;font-weight:600;font-size:12px;}
.insight{background:#160f38;border:1px solid #2e1f6e;border-radius:10px;padding:12px 16px;margin:8px 0;}
.ins-t{color:#00d4ff;font-weight:600;font-size:12px;margin-bottom:3px;}
.ins-b{color:#b0a8d8;font-size:11px;line-height:1.6;}
.ph-hr{border:none;border-top:1px solid #1e1a4a;margin:16px 0;}
div[data-testid="metric-container"]{background:#1c1240;border:1px solid #2e1f6e;border-radius:12px;padding:12px 16px;}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")
engine = get_engine()

@st.cache_data(ttl=300)
def q(sql): return pd.read_sql(sql, engine)

@st.cache_data(ttl=86400)
def load_geojson():
    urls = [
        "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception:
            continue
    raise ConnectionError("Could not load India GeoJSON. Check internet connection.")

STATE_MAP={
    'andaman-&-nicobar-islands':'Andaman & Nicobar Island',
    'andhra-pradesh':'Andhra Pradesh','arunachal-pradesh':'Arunachal Pradesh',
    'assam':'Assam','bihar':'Bihar','chandigarh':'Chandigarh',
    'chhattisgarh':'Chhattisgarh',
    'dadra-&-nagar-haveli-&-daman-&-diu':'Dadara & Nagar Havelli',
    'delhi':'NCT of Delhi','goa':'Goa','gujarat':'Gujarat','haryana':'Haryana',
    'himachal-pradesh':'Himachal Pradesh','jammu-&-kashmir':'Jammu & Kashmir',
    'jharkhand':'Jharkhand','karnataka':'Karnataka','kerala':'Kerala',
    'ladakh':'Ladakh','lakshadweep':'Lakshadweep',
    'madhya-pradesh':'Madhya Pradesh','maharashtra':'Maharashtra',
    'manipur':'Manipur','meghalaya':'Meghalaya','mizoram':'Mizoram',
    'nagaland':'Nagaland','odisha':'Odisha','puducherry':'Puducherry',
    'punjab':'Punjab','rajasthan':'Rajasthan','sikkim':'Sikkim',
    'tamil-nadu':'Tamil Nadu','telangana':'Telangana','tripura':'Tripura',
    'uttar-pradesh':'Uttar Pradesh','uttarakhand':'Uttarakhand',
    'west-bengal':'West Bengal',
}

P="#6739B7";C="#00d4ff";O="#ff6b35";G="#34d399";Y="#f59e0b";BG="#120f2d";CB="#1c1240";TX="#e8e0ff"
PAL=[P,C,O,"#a855f7",G,Y,"#22d3ee","#fb7185"]
PL=dict(paper_bgcolor=BG,plot_bgcolor=CB,font_color=TX,
        margin=dict(l=8,r=8,t=36,b=8),
        legend=dict(bgcolor=CB,bordercolor=CB),
        xaxis=dict(gridcolor="#1e1a4a"),yaxis=dict(gridcolor="#1e1a4a"))

def kpi(l,v,s=""): return f'<div class="kpi-box"><div class="kpi-lbl">{l}</div><div class="kpi-val">{v}</div><div class="kpi-sub">{s}</div></div>'
def sec(t): st.markdown(f'<div class="sec-hd">{t}</div>',unsafe_allow_html=True)
def hr(): st.markdown('<hr class="ph-hr">',unsafe_allow_html=True)
def tip(t,b): st.markdown(f'<div class="insight"><div class="ins-t">💡 {t}</div><div class="ins-b">{b}</div></div>',unsafe_allow_html=True)

def bh(df,x,y,title,color=P,h=380,pal=False):
    # x = value column (numeric), y = label column (category)
    # For horizontal bars: x is numeric axis, y is category axis
    if pal:
        fig=px.bar(df,x=x,y=y,orientation="h",title=title,height=h,
                   color=y, color_discrete_sequence=PAL)
    else:
        fig=px.bar(df,x=x,y=y,orientation="h",title=title,height=h,
                   color_discrete_sequence=[color])
    fig.update_layout(**PL,title_font_color=TX,showlegend=False)
    fig.update_xaxes(tickformat=",.0f")
    return fig

def bv(df,x,y,title,color=P,h=360,pal=False):
    # x = category column, y = value column
    if pal:
        fig=px.bar(df,x=x,y=y,title=title,height=h,
                   color=x, color_discrete_sequence=PAL)
    else:
        fig=px.bar(df,x=x,y=y,title=title,height=h,
                   color_discrete_sequence=[color])
    fig.update_layout(**PL,title_font_color=TX,showlegend=False)
    return fig

def donut(df,n,v,title,h=360):
    fig=px.pie(df,names=n,values=v,title=title,hole=0.45,
               color_discrete_sequence=PAL,height=h)
    fig.update_layout(paper_bgcolor=BG,font_color=TX,title_font_color=TX,
                      legend=dict(bgcolor=CB),margin=dict(l=8,r=8,t=36,b=8))
    fig.update_traces(textposition="inside",textinfo="percent+label",
                      marker=dict(line=dict(color=BG,width=2)))
    return fig

def ln(df,x,y,title,color=C,h=320):
    fig=px.line(df,x=x,y=y,title=title,markers=True,
                color_discrete_sequence=[color],height=h)
    fig.update_layout(**PL,title_font_color=TX)
    fig.update_traces(line_width=2.5,marker_size=6); return fig

try: HAS_INS=int(q("SELECT COUNT(*) AS c FROM aggregated_insurance")["c"].iloc[0])>0
except: HAS_INS=False

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:14px 0 10px'>"
                "<div style='color:#00d4ff;font-size:22px;font-weight:700'>💜 PhonePe Pulse</div>"
                "<div style='color:#4a3f80;font-size:10px;letter-spacing:1px'>THE BEAT OF PROGRESS</div>"
                "</div>",unsafe_allow_html=True)
    hr()
    page=st.radio("",["🏠  Home","🗺️  Explore Data (Map)",
        "📊  Case 1 · Transaction Dynamics","📱  Case 2 · Device & Engagement",
        "🛡️  Case 3 · Insurance","🚀  Case 4 · Market Expansion",
        "👥  Case 5 · User Growth"],label_visibility="collapsed")
    hr()
    st.markdown('<div style="color:#9b8ec4;font-size:10px;text-transform:uppercase;'
                'letter-spacing:1px;margin-bottom:8px">Global Filters</div>',unsafe_allow_html=True)
    yrs=q("SELECT DISTINCT Year FROM aggregated_transaction ORDER BY Year")["Year"].tolist()
    sel_yr=st.selectbox("Year",yrs,index=len(yrs)-1)
    sel_qtr=st.selectbox("Quarter",[1,2,3,4])
    hr(); st.caption("Source: PhonePe Pulse GitHub")

# ═══════════════════════════════ HOME ═══════════════════════════════
if page=="🏠  Home":
    st.markdown('<div class="pp-header"><div class="pp-logo">💜 PhonePe Pulse</div>'
                '<div class="pp-sub">THE BEAT OF PROGRESS · TRANSACTION INSIGHTS DASHBOARD</div></div>',
                unsafe_allow_html=True)
    ka=q("SELECT SUM(Transacion_count) AS tc,SUM(Transacion_amount) AS ta FROM aggregated_transaction")
    ku=q("SELECT SUM(Registered_user) AS ru FROM aggregated_user")
    tc=int(ka["tc"].iloc[0] or 0); ta=float(ka["ta"].iloc[0] or 0)
    ru=int(ku["ru"].iloc[0] or 0); av=ta/tc if tc else 0
    st.markdown(f'<div class="kpi-strip">{kpi("All Transactions",f"{tc/1e9:.2f}B","All years")}'
                f'{kpi("Total Value",f"₹{ta/1e7:,.0f}Cr","Cumulative")}'
                f'{kpi("Avg Value",f"₹{av:,.0f}","Per transaction")}'
                f'{kpi("Registered Users",f"{ru/1e6:.1f}M","All years")}</div>',
                unsafe_allow_html=True)
    kq=q(f"SELECT SUM(Transacion_count) AS tc,SUM(Transacion_amount) AS ta FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr}")
    kqu=q(f"SELECT SUM(Registered_user) AS ru,SUM(App_opens) AS ao FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr}")
    qtc=int(kq["tc"].iloc[0] or 0); qta=float(kq["ta"].iloc[0] or 0)
    qru=int(kqu["ru"].iloc[0] or 0); qao=int(kqu["ao"].iloc[0] or 0)
    hr(); sec(f"📆 Q{sel_qtr} {sel_yr} Snapshot")
    st.markdown(f'<div class="kpi-strip">{kpi(f"Transactions",f"{qtc/1e6:.2f}M",f"Q{sel_qtr} {sel_yr}")}'
                f'{kpi("Amount",f"₹{qta/1e7:,.0f}Cr","Payment value")}'
                f'{kpi("Registered Users",f"{qru/1e6:.2f}M",f"Q{sel_qtr} {sel_yr}")}'
                f'{kpi("App Opens",f"{qao/1e9:.2f}B",f"Q{sel_qtr} {sel_yr}")}</div>',
                unsafe_allow_html=True)
    hr()
    c1,c2=st.columns([3,2])
    with c1:
        sec("📈 Quarterly Growth")
        df_tr=q("SELECT Year,Quater,SUM(Transacion_count) AS Tc,SUM(Transacion_amount) AS Ta FROM aggregated_transaction GROUP BY Year,Quater ORDER BY Year,Quater")
        df_tr["Period"]=df_tr["Year"].astype(str)+" Q"+df_tr["Quater"].astype(str)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=df_tr["Period"],y=df_tr["Ta"],mode="lines+markers",
            name="Amount",line=dict(color=P,width=2.5),fill="tozeroy",
            fillcolor="rgba(103,57,183,0.12)",marker=dict(size=6,color=C,line=dict(color=BG,width=1))))
        fig.update_layout(**PL,height=300,title="Transaction Amount Growth",
                           title_font_color=TX,xaxis_tickangle=-45)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        sec(f"💳 Category Mix")
        df_cm=q(f"SELECT Transacion_type,SUM(Transacion_count) AS Cnt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY Transacion_type ORDER BY Cnt DESC")
        st.plotly_chart(donut(df_cm,"Transacion_type","Cnt",f"Q{sel_qtr} {sel_yr}",h=300),use_container_width=True)
    hr(); c3,c4=st.columns(2)
    with c3:
        sec("🏆 Top 5 States")
        df_t5=q(f"SELECT State,SUM(Transacion_amount) AS Amt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Amt DESC LIMIT 5")
        for i,r in enumerate(df_t5.itertuples(),1):
            st.markdown(f'<div class="rk-row"><span class="rk-num">{i}</span><span class="rk-name">{r.State.title()}</span><span class="rk-val">₹{r.Amt/1e7:,.1f}Cr</span></div>',unsafe_allow_html=True)
    with c4:
        sec("📱 Top 5 Brands")
        df_b5=q(f"SELECT Brands,SUM(Count) AS Users FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} AND Brands IS NOT NULL GROUP BY Brands ORDER BY Users DESC LIMIT 5")
        for i,r in enumerate(df_b5.itertuples(),1):
            st.markdown(f'<div class="rk-row"><span class="rk-num">{i}</span><span class="rk-name">{r.Brands}</span><span class="rk-val">{r.Users/1e6:.2f}M</span></div>',unsafe_allow_html=True)

# ═══════════════════════════════ MAP ════════════════════════════════
elif page=="🗺️  Explore Data (Map)":
    ctrl1,ctrl2,ctrl3=st.columns([1,1,4])
    with ctrl1: view=st.selectbox("",["Transactions","Users","Insurance"],label_visibility="collapsed")
    with ctrl2: tab_sel=st.selectbox("",["States","Districts","Postal Codes"],label_visibility="collapsed")
    if view=="Transactions":
        df_map=q(f"SELECT State,SUM(Transacion_count) AS Total_Count,SUM(Transacion_amount) AS Total_Amount FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State")
        color_col="Total_Amount"; count_lbl="Transactions"; amt_lbl="Amount (₹)"
        df_cat=q(f"SELECT Transacion_type,SUM(Transacion_count) AS Cnt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY Transacion_type ORDER BY Cnt DESC")
    elif view=="Users":
        df_map=q(f"SELECT State,SUM(Registered_user) AS Total_Count,SUM(App_opens) AS Total_Amount FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State")
        color_col="Total_Count"; count_lbl="Registered Users"; amt_lbl="App Opens"; df_cat=pd.DataFrame()
    else:
        if HAS_INS:
            df_map=q(f"SELECT State,SUM(Transacion_count) AS Total_Count,SUM(Transacion_amount) AS Total_Amount FROM aggregated_insurance WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State")
            df_cat=q(f"SELECT Transacion_type,SUM(Transacion_count) AS Cnt FROM aggregated_insurance WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY Transacion_type ORDER BY Cnt DESC")
        else:
            df_map=pd.DataFrame(columns=["State","Total_Count","Total_Amount"]); df_cat=pd.DataFrame()
        color_col="Total_Amount"; count_lbl="Policies"; amt_lbl="Amount (₹)"
    df_map["State_NM"]=df_map["State"].map(STATE_MAP).fillna(df_map["State"])
    mc=df_map["Total_Count"].sum(); ma=df_map["Total_Amount"].sum(); av=ma/mc if mc else 0
    st.markdown(f'<div class="kpi-strip">{kpi(f"All PhonePe {view}",f"{mc:,.0f}",count_lbl)}'
                f'{kpi("Total Payment Value",f"₹{ma/1e7:,.0f}Cr","")}'
                f'{kpi("Avg Transaction Value",f"₹{av:,.0f}","")}'
                f'{kpi("Active States",f"{df_map[chr(83)+chr(116)+chr(97)+chr(116)+chr(101)].nunique()}","")}</div>',
                unsafe_allow_html=True)
    map_col,right_col=st.columns([2.3,1])
    with map_col:
        try:
            geojson=load_geojson()
            fig=px.choropleth(df_map,geojson=geojson,featureidkey="properties.ST_NM",
                locations="State_NM",color=color_col,hover_name="State_NM",
                hover_data={"Total_Count":True,"Total_Amount":True,color_col:False},
                color_continuous_scale=["#0b0920","#1e0f5e","#6739B7","#ff6b35","#ffd700"],
                labels={"Total_Count":count_lbl,"Total_Amount":amt_lbl},height=530)
            fig.update_geos(fitbounds="locations",visible=False)
            fig.update_layout(paper_bgcolor=BG,geo_bgcolor=BG,font_color=TX,
                margin=dict(r=0,t=10,l=0,b=0),
                coloraxis_colorbar=dict(title=amt_lbl,
                    tickfont=dict(color=TX,size=9),
                    title_font=dict(color=TX,size=9),
                    thickness=12,len=0.6))
            st.plotly_chart(fig,use_container_width=True)
        except Exception as e:
            st.info("🗺️ Map loading... If it stays blank, check internet connection.")
            fb=df_map.nlargest(15,color_col).sort_values(color_col)
            fig=px.bar(fb,x=color_col,y="State_NM",orientation="h",height=450,
                       color=color_col,
                       color_continuous_scale=["#2e1f6e","#00d4ff"],
                       title="State-wise Data (Fallback Chart)")
            fig.update_layout(
                paper_bgcolor=BG, plot_bgcolor=CB, font_color=TX,
                margin=dict(l=8,r=8,t=36,b=8),
                coloraxis_colorbar=dict(
                    title="Amount",
                    tickfont=dict(color=TX,size=9),
                    title_font=dict(color=TX,size=9)
                )
            )
            st.plotly_chart(fig,use_container_width=True)
    with right_col:
        sec(f"{view}")
        if not df_cat.empty:
            tot=df_cat["Cnt"].sum()
            for _,row in df_cat.iterrows():
                pct=row["Cnt"]/tot if tot else 0
                st.markdown(f'<div class="cat-row"><span class="cat-name">{row.iloc[0]}</span><span class="cat-val">{row["Cnt"]:,.0f}</span></div>',unsafe_allow_html=True)
                st.progress(min(pct,1.0))
        hr()
        if tab_sel=="States":
            sec("Top 10 States")
            top10=df_map.nlargest(10,color_col).reset_index(drop=True)
            for i,row in top10.iterrows():
                st.markdown(f'<div class="rk-row"><span class="rk-num">{i+1}</span><span class="rk-name">{row["State_NM"]}</span><span class="rk-val">₹{row["Total_Amount"]/1e7:,.2f}Cr</span></div>',unsafe_allow_html=True)
        elif tab_sel=="Districts":
            sec("Top 10 Districts")
            df_dist=q(f"SELECT District,State,SUM(Amount) AS Amt FROM map_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY District,State ORDER BY Amt DESC LIMIT 10")
            for i,row in df_dist.iterrows():
                st.markdown(f'<div class="rk-row"><span class="rk-num">{i+1}</span><span class="rk-name">{row["District"].title()}<br><small style="color:#4a3f80">{row["State"]}</small></span><span class="rk-val">₹{row["Amt"]/1e7:,.1f}Cr</span></div>',unsafe_allow_html=True)
        else:
            sec("Top 10 Pincodes")
            df_pin=q(f"SELECT EntityName AS Pincode,State,SUM(Amount) AS Amt FROM top_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} AND EntityType='Pincode' GROUP BY EntityName,State ORDER BY Amt DESC LIMIT 10")
            for i,row in df_pin.iterrows():
                st.markdown(f'<div class="rk-row"><span class="rk-num">{i+1}</span><span class="rk-name">📮 {row["Pincode"]}<br><small style="color:#4a3f80">{row["State"]}</small></span><span class="rk-val">₹{row["Amt"]/1e7:,.1f}Cr</span></div>',unsafe_allow_html=True)

# ═══════════════════════════════ CASE 1 ═════════════════════════════
elif page=="📊  Case 1 · Transaction Dynamics":
    st.markdown('<div class="pp-header"><div class="pp-logo">📊 Case 1 — Decoding Transaction Dynamics</div><div class="pp-sub">Transaction behavior across states, quarters & payment categories</div></div>',unsafe_allow_html=True)
    k=q(f"SELECT SUM(Transacion_count) AS tc,SUM(Transacion_amount) AS ta FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr}")
    tc=int(k["tc"].iloc[0] or 0); ta=float(k["ta"].iloc[0] or 0)
    st.markdown(f'<div class="kpi-strip">{kpi("Transactions",f"{tc/1e6:.2f}M",f"Q{sel_qtr} {sel_yr}")}{kpi("Amount",f"₹{ta/1e7:,.0f}Cr",f"Q{sel_qtr} {sel_yr}")}{kpi("Avg Value",f"₹{ta/tc:,.0f}" if tc else "—","Per txn")}{kpi("States","36","All India")}</div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["💳 Categories","🏆 State Performance","📈 Growth Trends","🔍 Deep Dive"])
    with t1:
        df_ty=q(f"SELECT Transacion_type,SUM(Transacion_count) AS Cnt,SUM(Transacion_amount) AS Amt,ROUND(SUM(Transacion_amount)*100.0/SUM(SUM(Transacion_amount)) OVER(),2) AS Pct FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY Transacion_type ORDER BY Amt DESC")
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(donut(df_ty,"Transacion_type","Cnt","Count Share"),use_container_width=True)
        with c2: st.plotly_chart(bh(df_ty.sort_values("Amt"),"Amt","Transacion_type","Amount by Type",pal=True),use_container_width=True)
        disp=df_ty.copy(); disp["Amt"]=disp["Amt"].apply(lambda x:f"₹{x/1e7:,.1f}Cr"); disp["Cnt"]=disp["Cnt"].apply(lambda x:f"{x/1e6:.2f}M")
        st.dataframe(disp.rename(columns={"Transacion_type":"Type","Cnt":"Count","Amt":"Amount","Pct":"Amount %"}),use_container_width=True,hide_index=True)
        if not df_ty.empty: tip("Dominant Type",f"'{df_ty.iloc[0]['Transacion_type']}' leads with {df_ty.iloc[0]['Pct']}% of total amount.")
    with t2:
        c1,c2=st.columns(2)
        with c1:
            df_top=q(f"SELECT State,SUM(Transacion_amount) AS Amt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Amt DESC LIMIT 10")
            st.plotly_chart(bh(df_top.sort_values("Amt"),"Amt","State","🏆 Top 10 States",pal=True),use_container_width=True)
        with c2:
            df_bot=q(f"SELECT State,SUM(Transacion_amount) AS Amt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Amt ASC LIMIT 10")
            st.plotly_chart(bh(df_bot,"Amt","State","⚠️ Bottom 10 States",color=O),use_container_width=True)
        df_pop=q("SELECT t1.State,t1.Transacion_type,t1.TC FROM (SELECT State,Transacion_type,SUM(Transacion_count) AS TC,RANK() OVER (PARTITION BY State ORDER BY SUM(Transacion_count) DESC) rk FROM aggregated_transaction GROUP BY State,Transacion_type) t1 WHERE t1.rk=1 ORDER BY TC DESC")
        fig=px.treemap(df_pop,path=["Transacion_type","State"],values="TC",color="Transacion_type",color_discrete_sequence=PAL,height=420)
        fig.update_layout(paper_bgcolor=BG,font_color=TX,margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig,use_container_width=True)
    with t3:
        df_q=q("SELECT Year,Quater,SUM(Transacion_count) AS Tc,SUM(Transacion_amount) AS Ta FROM aggregated_transaction GROUP BY Year,Quater ORDER BY Year,Quater")
        df_q["Period"]=df_q["Year"].astype(str)+" Q"+df_q["Quater"].astype(str)
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(ln(df_q,"Period","Tc","Count Growth",P),use_container_width=True)
        with c2: st.plotly_chart(ln(df_q,"Period","Ta","Amount Growth",C),use_container_width=True)
        df_yy=q("SELECT Year,SUM(Transacion_amount) AS Amt,ROUND((SUM(Transacion_amount)-LAG(SUM(Transacion_amount)) OVER(ORDER BY Year))/LAG(SUM(Transacion_amount)) OVER(ORDER BY Year)*100,2) AS YoY FROM aggregated_transaction GROUP BY Year ORDER BY Year")
        fig=bv(df_yy.dropna(),"Year","YoY","YoY Growth (%)",C,300)
        st.plotly_chart(fig,use_container_width=True)
    with t4:
        df_tyr=q("SELECT Year,Transacion_type,ROUND(SUM(Transacion_amount)/1e7,2) AS Amt_Cr FROM aggregated_transaction GROUP BY Year,Transacion_type ORDER BY Year")
        fig=px.bar(df_tyr,x="Year",y="Amt_Cr",color="Transacion_type",barmode="group",title="Type Trend per Year (₹Cr)",color_discrete_sequence=PAL,height=380)
        fig.update_layout(**PL,title_font_color=TX); st.plotly_chart(fig,use_container_width=True)

# ═══════════════════════════════ CASE 2 ═════════════════════════════
elif page=="📱  Case 2 · Device & Engagement":
    st.markdown('<div class="pp-header"><div class="pp-logo">📱 Case 2 — Device Dominance & User Engagement</div><div class="pp-sub">Brand preferences · engagement ratios · underutilised regions</div></div>',unsafe_allow_html=True)
    ku=q(f"SELECT SUM(Registered_user) AS ru,SUM(App_opens) AS ao FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr}")
    ru=int(ku["ru"].iloc[0] or 0); ao=int(ku["ao"].iloc[0] or 0)
    st.markdown(f'<div class="kpi-strip">{kpi("Registered Users",f"{ru/1e6:.2f}M",f"Q{sel_qtr} {sel_yr}")}{kpi("App Opens",f"{ao/1e9:.2f}B",f"Q{sel_qtr} {sel_yr}")}{kpi("Engagement",f"{ao/ru:.1f}x" if ru else "—","Opens/user")}{kpi("Brands","10+","Tracked")}</div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["📱 Brands","📍 Regional","📈 Trends"])
    with t1:
        # Check which years have brand data
        brand_years=q("SELECT DISTINCT Year FROM aggregated_user WHERE Brands IS NOT NULL ORDER BY Year")["Year"].tolist()
        brand_qtrs=q(f"SELECT DISTINCT Quater FROM aggregated_user WHERE Brands IS NOT NULL ORDER BY Quater")["Quater"].tolist()
        if brand_years:
            bc1,bc2=st.columns([1,1])
            with bc1:
                sel_byr=st.selectbox("Brand Year",brand_years,index=len(brand_years)-1,key="brand_yr")
            with bc2:
                sel_bqtr=st.selectbox("Brand Quarter",brand_qtrs,index=0,key="brand_qtr")
            df_br=q(f"SELECT Brands,SUM(Count) AS Users,ROUND(SUM(Count)*100.0/SUM(SUM(Count)) OVER(),2) AS Pct FROM aggregated_user WHERE Year={sel_byr} AND Quater={sel_bqtr} AND Brands IS NOT NULL GROUP BY Brands ORDER BY Users DESC LIMIT 10")
            if df_br.empty:
                df_br=q("SELECT Brands,SUM(Count) AS Users,ROUND(SUM(Count)*100.0/SUM(SUM(Count)) OVER(),2) AS Pct FROM aggregated_user WHERE Brands IS NOT NULL GROUP BY Brands ORDER BY Users DESC LIMIT 10")
                st.info("ℹ️ Showing all-time brand data.")
        else:
            df_br=pd.DataFrame()
        if not df_br.empty:
            c1,c2=st.columns(2)
            with c1: st.plotly_chart(donut(df_br,"Brands","Users","Brand Market Share"),use_container_width=True)
            with c2: st.plotly_chart(bh(df_br.sort_values("Users"),"Users","Brands","Users per Brand",pal=True),use_container_width=True)
            tip("Brand Leader",f"'{df_br.iloc[0]['Brands']}' leads with {df_br.iloc[0]['Pct']}% share.")
        else:
            st.warning("⚠️ No brand data found in the database.")
    with t2:
        c1,c2=st.columns(2)
        with c1:
            df_su=q(f"SELECT State,SUM(Registered_user) AS Reg,SUM(App_opens) AS Opens FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Reg DESC LIMIT 10")
            fig=go.Figure()
            fig.add_trace(go.Bar(x=df_su["State"],y=df_su["Reg"],name="Registered",marker_color=P))
            fig.add_trace(go.Bar(x=df_su["State"],y=df_su["Opens"],name="App Opens",marker_color=C))
            fig.update_layout(**PL,barmode="group",height=360,title="Registered vs App Opens",title_font_color=TX,xaxis_tickangle=-30)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            df_lw=q(f"SELECT State,ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State HAVING Eng<(SELECT ROUND(AVG(App_opens/Registered_user),2) FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} AND Registered_user>0) ORDER BY Eng ASC LIMIT 10")
            st.plotly_chart(bh(df_lw.sort_values("Eng"),"Eng","State","⚠️ Low Engagement",O),use_container_width=True)
        df_sc=q("SELECT State,SUM(Registered_user) AS Reg,ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Eng FROM aggregated_user GROUP BY State")
        fig=px.scatter(df_sc,x="Reg",y="Eng",text="State",size="Reg",color="Eng",color_continuous_scale=["#ff6b35","#6739B7","#00d4ff"],title="Users vs Engagement Score",height=420)
        fig.update_layout(**PL,title_font_color=TX); fig.update_traces(textposition="top center",textfont_size=8)
        st.plotly_chart(fig,use_container_width=True)
    with t3:
        df_ut=q("SELECT Year,Quater,SUM(Registered_user) AS Reg,SUM(App_opens) AS Opens FROM aggregated_user GROUP BY Year,Quater ORDER BY Year,Quater")
        df_ut["Period"]=df_ut["Year"].astype(str)+" Q"+df_ut["Quater"].astype(str)
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(ln(df_ut,"Period","Reg","Registered Users Growth",P),use_container_width=True)
        with c2: st.plotly_chart(ln(df_ut,"Period","Opens","App Opens Growth",G),use_container_width=True)
        df_by=q("SELECT Brands,Year,SUM(Count) AS Users FROM aggregated_user WHERE Brands IS NOT NULL GROUP BY Brands,Year ORDER BY Year")
        top5b=q("SELECT Brands FROM aggregated_user WHERE Brands IS NOT NULL GROUP BY Brands ORDER BY SUM(Count) DESC LIMIT 5")["Brands"].tolist()
        df_by=df_by[df_by["Brands"].isin(top5b)]
        fig=px.line(df_by,x="Year",y="Users",color="Brands",markers=True,color_discrete_sequence=PAL,title="Top 5 Brands Year-wise",height=340)
        fig.update_layout(**PL,title_font_color=TX); st.plotly_chart(fig,use_container_width=True)

# ═══════════════════════════════ CASE 3 ═════════════════════════════
elif page=="🛡️  Case 3 · Insurance":
    st.markdown('<div class="pp-header"><div class="pp-logo">🛡️ Case 3 — Insurance Penetration & Growth</div><div class="pp-sub">Growth trajectory · untapped markets · penetration analysis</div></div>',unsafe_allow_html=True)
    if not HAS_INS: st.warning("⚠️ Insurance table empty or missing."); st.stop()
    ki=q(f"SELECT SUM(Transacion_count) AS ic,SUM(Transacion_amount) AS ia FROM aggregated_insurance WHERE Year={sel_yr} AND Quater={sel_qtr}")
    ic=int(ki["ic"].iloc[0] or 0); ia=float(ki["ia"].iloc[0] or 0)
    kt=q(f"SELECT SUM(Transacion_amount) AS ta FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr}")
    ta=float(kt["ta"].iloc[0] or 1)
    st.markdown(f'<div class="kpi-strip">{kpi("Policies",f"{ic/1e3:,.0f}K",f"Q{sel_qtr} {sel_yr}")}{kpi("Amount",f"₹{ia/1e7:,.0f}Cr",f"Q{sel_qtr} {sel_yr}")}{kpi("Penetration",f"{ia/ta*100:.4f}%","vs total")}{kpi("Avg Premium",f"₹{ia/ic:,.0f}" if ic else "—","Per policy")}</div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["📊 State Analysis","📈 Growth Trend","🔍 Penetration"])
    with t1:
        df_is=q(f"SELECT State,SUM(Transacion_count) AS Policies,SUM(Transacion_amount) AS Amount FROM aggregated_insurance WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Amount DESC LIMIT 10")
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(donut(df_is,"State","Amount","Amount — Top 10"),use_container_width=True)
        with c2: st.plotly_chart(bh(df_is.sort_values("Amount"),"Amount","State","Top 10 States",pal=True),use_container_width=True)
    with t2:
        df_it=q("SELECT Year,Quater,SUM(Transacion_count) AS Policies,SUM(Transacion_amount) AS Amount FROM aggregated_insurance GROUP BY Year,Quater ORDER BY Year,Quater")
        df_it["Period"]=df_it["Year"].astype(str)+" Q"+df_it["Quater"].astype(str)
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(ln(df_it,"Period","Policies","Policy Count Trend",G),use_container_width=True)
        with c2: st.plotly_chart(ln(df_it,"Period","Amount","Amount Trend",Y),use_container_width=True)
    with t3:
        df_pen=q("SELECT t.State,ROUND(SUM(i.Transacion_amount)/SUM(t.Transacion_amount)*100,4) AS Pen FROM aggregated_transaction t JOIN aggregated_insurance i ON t.State=i.State AND t.Year=i.Year AND t.Quater=i.Quater GROUP BY t.State ORDER BY Pen DESC LIMIT 10")
        df_unt=q("SELECT State,SUM(Transacion_count) AS Policies FROM aggregated_insurance GROUP BY State ORDER BY Policies ASC LIMIT 10")
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(bh(df_pen.sort_values("Pen"),"Pen","State","Penetration Rate (%)",pal=True),use_container_width=True)
        with c2: st.plotly_chart(bh(df_unt.sort_values("Policies"),"Policies","State","⚠️ Untapped Markets",O),use_container_width=True)
        if not df_pen.empty: tip("Top Penetration",f"'{df_pen.iloc[0]['State']}' leads at {df_pen.iloc[0]['Pen']}%.")
        if not df_unt.empty: tip("Growth Opportunity",f"'{df_unt.iloc[0]['State']}' has lowest adoption.")

# ═══════════════════════════════ CASE 4 ═════════════════════════════
elif page=="🚀  Case 4 · Market Expansion":
    st.markdown('<div class="pp-header"><div class="pp-logo">🚀 Case 4 — Transaction Analysis for Market Expansion</div><div class="pp-sub">State rankings · expansion targets · districts & pincodes</div></div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["🏆 Rankings","🎯 Expansion","📍 Districts & Pincodes","📊 Type Filter"])
    with t1:
        df_rk=q(f"SELECT State,SUM(Transacion_count) AS Txns,SUM(Transacion_amount) AS Amt,ROUND(SUM(Transacion_amount)/SUM(Transacion_count),2) AS Avg,RANK() OVER(ORDER BY SUM(Transacion_amount) DESC) AS Rnk FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Rnk")
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(bh(df_rk.head(15).sort_values("Amt"),"Amt","State","By Amount",pal=True),use_container_width=True)
        with c2: st.plotly_chart(bh(df_rk.sort_values("Txns",ascending=False).head(15).sort_values("Txns"),"Txns","State","By Count",pal=True),use_container_width=True)
        disp=df_rk[["Rnk","State","Txns","Amt","Avg"]].copy()
        disp["Amt"]=disp["Amt"].apply(lambda x:f"₹{x/1e7:,.1f}Cr"); disp["Txns"]=disp["Txns"].apply(lambda x:f"{x/1e6:.2f}M"); disp["Avg"]=disp["Avg"].apply(lambda x:f"₹{x:,.0f}")
        st.dataframe(disp.rename(columns={"Rnk":"Rank","Txns":"Transactions","Amt":"Amount","Avg":"Avg Value"}),use_container_width=True,hide_index=True)
    with t2:
        df_ex=q(f"SELECT State,SUM(Transacion_count) AS Vol,ROUND(SUM(Transacion_amount)/SUM(Transacion_count),2) AS Avg FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State HAVING Avg<(SELECT SUM(Transacion_amount)/SUM(Transacion_count) FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr}) ORDER BY Vol DESC LIMIT 10")
        c1,c2=st.columns(2)
        with c1: st.plotly_chart(bh(df_ex.sort_values("Vol"),"Vol","State","High Volume States",pal=True),use_container_width=True)
        with c2: st.plotly_chart(bh(df_ex.sort_values("Avg"),"Avg","State","Below-Avg Value",O),use_container_width=True)
        tip("Expansion Strategy","High-volume, below-average value states are prime targets for premium product upselling.")
    with t3:
        c1,c2=st.columns(2)
        with c1:
            df_dt=q(f"SELECT District,State,SUM(Amount) AS Amt FROM map_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY District,State ORDER BY Amt DESC LIMIT 10")
            df_dt["Lbl"]=df_dt["District"].str.title()+" ("+df_dt["State"]+")"
            st.plotly_chart(bh(df_dt.sort_values("Amt"),"Amt","Lbl","Top 10 Districts",pal=True),use_container_width=True)
        with c2:
            df_pc=q(f"SELECT EntityName AS Pin,State,SUM(Amount) AS Amt FROM top_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} AND EntityType='Pincode' GROUP BY EntityName,State ORDER BY Amt DESC LIMIT 10")
            df_pc["Lbl"]=df_pc["Pin"].astype(str)+" ("+df_pc["State"]+")"
            st.plotly_chart(bh(df_pc.sort_values("Amt"),"Amt","Lbl","Top 10 Pincodes",pal=True),use_container_width=True)
    with t4:
        df_tf=q(f"SELECT Transacion_type,State,SUM(Transacion_amount) AS Amt FROM aggregated_transaction WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY Transacion_type,State")
        sel_t=st.selectbox("Payment Type",df_tf["Transacion_type"].unique())
        filt=df_tf[df_tf["Transacion_type"]==sel_t].nlargest(10,"Amt")
        st.plotly_chart(bh(filt.sort_values("Amt"),"Amt","State",f"Top States — {sel_t}",pal=True),use_container_width=True)

# ═══════════════════════════════ CASE 5 ═════════════════════════════
elif page=="👥  Case 5 · User Growth":
    st.markdown('<div class="pp-header"><div class="pp-logo">👥 Case 5 — User Engagement & Growth Strategy</div><div class="pp-sub">Engagement scores · district drill-down · YoY growth</div></div>',unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["🎯 Engagement","📍 Districts & Pincodes","📈 Growth"])
    with t1:
        df_eg=q(f"SELECT State,SUM(Registered_user) AS Reg,SUM(App_opens) AS Opens,ROUND(SUM(App_opens)/SUM(Registered_user),2) AS Score,CASE WHEN SUM(App_opens)/SUM(Registered_user)>=50 THEN 'High' WHEN SUM(App_opens)/SUM(Registered_user)>=20 THEN 'Medium' ELSE 'Low' END AS Category FROM aggregated_user WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY State ORDER BY Score DESC")
        cat_color={"High":"#34d399","Medium":"#f59e0b","Low":"#ff6b35"}
        fig=px.bar(df_eg.sort_values("Score"),x="Score",y="State",orientation="h",color="Category",color_discrete_map=cat_color,title=f"Engagement Score Q{sel_qtr} {sel_yr}",height=720)
        fig.update_layout(**PL,title_font_color=TX); st.plotly_chart(fig,use_container_width=True)
        c1,c2=st.columns(2)
        cat_c=df_eg["Category"].value_counts().reset_index(); cat_c.columns=["Category","Count"]
        with c1: st.plotly_chart(donut(cat_c,"Category","Count","Category Distribution"),use_container_width=True)
        with c2:
            h=len(df_eg[df_eg["Category"]=="High"]); m=len(df_eg[df_eg["Category"]=="Medium"]); l=len(df_eg[df_eg["Category"]=="Low"])
            tip("Summary",f"<b style='color:#34d399'>High</b>:{h} | <b style='color:#f59e0b'>Medium</b>:{m} | <b style='color:#ff6b35'>Low</b>:{l} states<br>Top: <b style='color:#00d4ff'>{df_eg.iloc[0]['State'].title()}</b> — {df_eg.iloc[0]['Score']}x")
            tip("Strategy","Low-engagement states need push notifications, cashback offers & offline campaigns.")
    with t2:
        c1,c2=st.columns(2)
        with c1:
            df_td=q(f"SELECT District,State,SUM(Registered_user) AS Reg FROM map_user WHERE Year={sel_yr} AND Quater={sel_qtr} GROUP BY District,State ORDER BY Reg DESC LIMIT 10")
            df_td["Lbl"]=df_td["District"].str.title()+" ("+df_td["State"]+")"
            st.plotly_chart(bh(df_td.sort_values("Reg"),"Reg","Lbl","Top 10 Districts",pal=True),use_container_width=True)
        with c2:
            df_tp=q(f"SELECT EntityName AS Pin,State,SUM(Registered_user) AS Reg FROM top_user WHERE Year={sel_yr} AND Quater={sel_qtr} AND EntityType='Pincode' GROUP BY EntityName,State ORDER BY Reg DESC LIMIT 10")
            df_tp["Lbl"]=df_tp["Pin"].astype(str)+" ("+df_tp["State"]+")"
            st.plotly_chart(bh(df_tp.sort_values("Reg"),"Reg","Lbl","Top 10 Pincodes",pal=True),use_container_width=True)
    with t3:
        df_ug=q("WITH uy AS (SELECT State,Year,SUM(Registered_user) AS U FROM aggregated_user GROUP BY State,Year) SELECT c.State,c.Year,ROUND((c.U-p.U)/p.U*100,2) AS Growth FROM uy c JOIN uy p ON c.State=p.State AND c.Year=p.Year+1 ORDER BY Growth DESC LIMIT 10")
        c1,c2=st.columns(2)
        with c1:
            df_ug["Lbl"]=df_ug["State"]+" ("+df_ug["Year"].astype(str)+")"
            st.plotly_chart(bh(df_ug.sort_values("Growth"),"Growth","Lbl","YoY User Growth (%)",G),use_container_width=True)
        with c2:
            df_qr=q("SELECT Year,Quater,SUM(Registered_user) AS Reg FROM aggregated_user GROUP BY Year,Quater ORDER BY Year,Quater")
            df_qr["Period"]=df_qr["Year"].astype(str)+" Q"+df_qr["Quater"].astype(str)
            st.plotly_chart(ln(df_qr,"Period","Reg","Quarterly Registration Trend",P),use_container_width=True)
        tip("Growth Strategy","High YoY growth states are ideal for referral programs. High transactions-per-user states are monetisation hotspots.")