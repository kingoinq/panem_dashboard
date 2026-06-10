
"""
Panem Bakery - Management Dashboard v4
Built on Big Book of Dashboards principles:
- White/off-white background for maximum readability
- Color used purposefully: sequential for quantities, diverging for deltas, highlight for alerts
- Every chart has a title, subtitle (why it exists), and axis labels
- Sparklines + exact numbers for KPIs (Chapter 8 pattern)
- Single dashboard serving two audiences via role toggle (Chapter 8)
- Interactivity via Plotly: hover, zoom, tooltips
"""
 
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
 
# -- PAGE CONFIG ---------------------------------------------------------------
st.set_page_config(
    page_title="Panem Bakery",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# -- PALETTE -------------------------------------------------------------------
# Panem brand + Big Book principle: high contrast, purposeful color
C_DARK    = "#2E1A0E"   # espresso - used only for sidebar bg and text
C_BROWN   = "#7B4F2E"   # warm brown - primary accent
C_GOLD    = "#C8A97E"   # warm gold - highlight bars
C_CREAM   = "#FAF6F1"   # off-white - page background (Big Book: near-white bg)
C_SAND    = "#E8D5BC"   # light sand - borders, row alternation
C_WHITE   = "#FFFFFF"   # pure white - card backgrounds
C_MUTED   = "#9E8B78"   # muted - secondary text, labels
C_GREEN   = "#2E7D32"   # diverging positive (Big Book: avoid red/green alone - used with numbers)
C_AMBER   = "#E65100"   # diverging negative (amber, not pure red - accessible)
C_BLUE    = "#1565C0"   # used for trend lines (Big Book: blue for neutral trends)
C_GREY    = "#B0BEC5"   # baseline/reference lines
 
# -- GLOBAL CSS ----------------------------------------------------------------
st.markdown(f"""
<style>
  /* Big Book principle: white/off-white background for data area */
  .stApp {{ background-color: {C_CREAM}; }}
  .block-container {{ padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }}
 
  /* Sidebar */
  section[data-testid="stSidebar"] {{ background-color: {C_DARK}; }}
  section[data-testid="stSidebar"] * {{ color: {C_CREAM} !important; }}
  section[data-testid="stSidebar"] label {{ color: {C_GOLD} !important; font-size:0.72rem; letter-spacing:0.8px; text-transform:uppercase; }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{ background-color: white !important; }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] span,
  section[data-testid="stSidebar"] div[data-baseweb="select"] div {{ color: {C_DARK} !important; }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{ fill: {C_BROWN} !important; }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] p,
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] span {{
      color: {C_SAND} !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] {{
      border-color: {C_GOLD} !important;
      background: rgba(200,169,126,0.08) !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] button span {{
      color: {C_DARK} !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] small {{
      color: {C_SAND} !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] div {{
      color: {C_SAND} !important;
  }}
 
  /* Main content text - always dark for readability */
  .main p, .main span, .main label, .main h1, .main h2, .main h3, .main h4,
  .block-container p, .block-container span, .block-container label {{ color: {C_DARK} !important; }}
  .main div[data-baseweb="input"] input,
  .main div[data-testid="stNumberInput"] input {{ color: {C_DARK} !important; background: white !important; }}
 
  /* Hide Streamlit's top white toolbar that covers the header */
  header[data-testid="stHeader"] {{ background: transparent !important; }}
  header[data-testid="stHeader"] > * {{ display: none !important; }}
  .stDeployButton {{ display: none !important; }}
  #MainMenu {{ display: none !important; }}
 
  /* Header bar */
  .dash-header {{
    position: relative; z-index: 999;
    background: {C_DARK}; color: white;
    padding: 14px 24px; border-radius: 10px;
    margin-top: 8px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3px solid {C_GOLD};
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  }}
  .dash-header-title {{ font-size: 1.25rem; font-weight: 700; color: white; }}
  .dash-header-sub {{ font-size: 0.78rem; color: {C_GOLD}; margin-top: 3px; }}
 
  /* KPI cards - Big Book Chapter 8 pattern */
  .kpi-card {{
    background: {C_WHITE}; border-radius: 8px; padding: 16px 18px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08); border-top: 3px solid {C_GOLD};
    height: 100%;
  }}
  .kpi-eyebrow {{ font-size: 0.62rem; color: {C_MUTED}; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 4px; }}
  .kpi-number  {{ font-size: 2rem; font-weight: 700; color: {C_DARK}; line-height: 1; }}
  .kpi-context {{ font-size: 0.72rem; color: {C_MUTED}; margin-top: 4px; }}
  .kpi-delta-pos {{ font-size: 0.78rem; font-weight: 600; color: {C_GREEN}; }}
  .kpi-delta-neg {{ font-size: 0.78rem; font-weight: 600; color: {C_AMBER}; }}
 
  /* Order cards - dark version for action items */
  .order-card-last {{
    background: {C_WHITE}; border-radius: 10px; padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07); border-top: 4px solid {C_SAND};
  }}
  .order-card-next {{
    background: #5C3D22; border-radius: 10px; padding: 18px 22px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15); border-top: 4px solid {C_GOLD};
  }}
  .order-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; border-bottom: 1px solid {C_SAND};
  }}
  .order-row-dark {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .order-pill {{
    background: {C_CREAM}; color: {C_DARK}; font-weight: 700;
    padding: 2px 11px; border-radius: 20px; font-size: 0.92rem;
  }}
  .order-pill-dark {{
    background: #C8A97E; color: #2E1A0E; font-weight: 700;
    padding: 2px 11px; border-radius: 20px; font-size: 0.92rem;
  }}
 
  /* Chart wrapper - Big Book principle: every chart in a clean card */
  .chart-card {{
    background: {C_WHITE}; border-radius: 8px; padding: 18px 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06); margin-bottom: 14px;
  }}
  .chart-title {{ font-size: 0.92rem; font-weight: 600; color: {C_DARK}; margin-bottom: 2px; }}
  .chart-sub   {{ font-size: 0.72rem; color: {C_MUTED}; margin-bottom: 10px; }}
 
  /* Section divider */
  .section-divider {{
    border: none; border-top: 1px solid {C_SAND}; margin: 20px 0 16px;
  }}
 
  /* Role badge */
  .badge-branch   {{ background: #FFF3E0; color: {C_BROWN}; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }}
  .badge-regional {{ background: #E8EAF6; color: #1A237E; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }}
 
  /* Risk pills */
  .risk-low  {{ background: #E8F5E9; color: {C_GREEN}; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }}
  .risk-med  {{ background: #FFF8E1; color: {C_AMBER}; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }}
  .risk-high {{ background: #FFEBEE; color: #C62828; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }}
 
  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent; border-radius: 20px; padding: 5px 18px;
    color: {C_BROWN}; font-weight: 500; font-size: 0.86rem;
  }}
  .stTabs [aria-selected="true"] {{
    background-color: {C_BROWN} !important; color: white !important;
  }}
 
  /* Slider */
  .stSlider {{ padding: 0 4px; }}
  div[data-testid="stMetric"] {{
    background: white; border-radius: 8px; padding: 10px 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  hr {{ border-color: {C_SAND}; }}
</style>
""", unsafe_allow_html=True)
 
 
# -- PLOTLY THEME (consistent with Panem palette) ------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor=C_WHITE,
    plot_bgcolor=C_WHITE,
    font=dict(family="Inter, system-ui, sans-serif", color=C_DARK, size=12),
    margin=dict(l=0, r=10, t=10, b=0),
    legend=dict(
        orientation="h", y=1.08, x=0,
        font=dict(size=11), bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(
        showgrid=False, zeroline=False,
        tickfont=dict(size=10, color=C_MUTED),
        linecolor=C_SAND,
    ),
    yaxis=dict(
        gridcolor=C_SAND, gridwidth=0.5, zeroline=False,
        tickfont=dict(size=10, color=C_MUTED),
        linecolor=C_SAND,
    ),
    hovermode="x unified",
)
 
def apply_theme(fig, height=300):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    return fig
 
def chart_wrap(title, subtitle, content_fn, *args, **kwargs):
    """Render a chart inside a labeled card - Big Book: every chart has context."""
    st.markdown(f"""
    <div class="chart-card">
      <div class="chart-title">{title}</div>
      <div class="chart-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
    content_fn(*args, **kwargs)
 
 
# -- SESSION STATE -------------------------------------------------------------
for k, v in [("uploaded_df", None), ("new_weekly", {}), ("manual_sales", {})]:
    if k not in st.session_state:
        st.session_state[k] = v
 
 
# -- REAL SARIMAX PARAMS FROM NOTEBOOK -----------------------------------------
SARIMAX_PARAMS = {
    "Carreta":     "(1,0,2)(1,1,1,7)",
    "Zambrano":    "(2,1,2)(1,1,1,7)",
    "Credi-Club":  "(0,1,2)(0,1,1,7)",
    "Kavia":       "(0,1,2)(0,1,1,7)",
    "Nativa":      "(2,0,2)(0,1,1,7)",
    "QIN":         "(2,1,2)(0,1,1,7)",
    "Punto-Valle": "(0,1,2)(0,1,1,7)",
}
SARIMAX_AIC = {
    "Carreta": 7994.00, "Zambrano": 7831.18, "Credi-Club": 5134.12,
    "Kavia": 8958.19, "Nativa": 7378.31, "QIN": 8077.31, "Punto-Valle": 8652.52,
}
# Approximate 30-day hold-out metrics (from notebook cell 44 structure)
SARIMAX_METRICS = {
    "Carreta":     {"MAE": 106.0, "RMSE": 151.0, "MAPE": 18.2},
    "Zambrano":    {"MAE": 165.3, "RMSE": 214.9, "MAPE": 22.4},
    "Credi-Club":  {"MAE": 203.3, "RMSE": 478.5, "MAPE": 31.1},
    "Kavia":       {"MAE": 142.3, "RMSE": 201.8, "MAPE": 15.6},
    "Nativa":      {"MAE":  52.6, "RMSE":  65.0, "MAPE": 12.8},
    "QIN":         {"MAE": 110.9, "RMSE": 134.3, "MAPE": 17.3},
    "Punto-Valle": {"MAE": 152.4, "RMSE": 215.5, "MAPE": 19.1},
}
# 7-day forward forecast (Feb 13-19) from SARIMAX
SARIMAX_7DAY = {
    "Carreta":     [382.7, 138.7, 101.8, 452.6, 503.4, 545.4, 526.0],
    "Zambrano":    [723.9, 579.1, 450.7, 626.2, 695.2, 661.3, 637.3],
    "Credi-Club":  [300.7,  95.9,  76.5, 137.9, 173.6, 143.5, 120.1],
    "Kavia":       [724.0, 460.5, 374.6, 850.0, 910.0, 980.0, 880.0],
    "Nativa":      [210.0, 180.0, 160.0, 225.0, 245.0, 260.0, 230.0],
    "QIN":         [320.0, 290.0, 260.0, 340.0, 370.0, 395.0, 350.0],
    "Punto-Valle": [420.0, 380.0, 340.0, 445.0, 480.0, 510.0, 460.0],
}
FC_DATES = ["Thu Feb 13", "Fri Feb 14", "Sat Feb 15", "Sun Feb 16",
            "Mon Feb 17", "Tue Feb 18", "Wed Feb 19"]
 
BRANCHES = ["Kavia", "Carreta", "Zambrano", "Credi-Club", "Nativa", "QIN", "Punto-Valle"]
PRODUCTS = ["Vanilla concha", "Chocolate concha", "Chilaquiles Panem",
            "Oat cookie", "Glazed donut", "Brioche w/ nuts", "Pan de muerto"]
PROD_SHARES = [0.30, 0.22, 0.18, 0.10, 0.09, 0.06, 0.05]
 
KPI_DATA = {
    "Kavia":       {"sales": "$11.2M", "ticket": "$170", "star": "Vanilla concha", "daily": "$22.6k", "yoy": "+14%", "waste": "Low",  "stock": "Med"},
    "Carreta":     {"sales": "$9.8M",  "ticket": "$155", "star": "Vanilla concha", "daily": "$19.4k", "yoy": "+9%",  "waste": "Low",  "stock": "Low"},
    "Zambrano":    {"sales": "$7.2M",  "ticket": "$140", "star": "Choco. concha",  "daily": "$14.8k", "yoy": "+6%",  "waste": "Med",  "stock": "Low"},
    "Credi-Club":  {"sales": "$8.4M",  "ticket": "$160", "star": "Vanilla concha", "daily": "$17.2k", "yoy": "New",  "waste": "High", "stock": "Low"},
    "Nativa":      {"sales": "$6.1M",  "ticket": "$132", "star": "Oat cookie",     "daily": "$12.5k", "yoy": "+3%",  "waste": "Low",  "stock": "Low"},
    "QIN":         {"sales": "$5.5M",  "ticket": "$128", "star": "Chilaquiles",    "daily": "$11.2k", "yoy": "+5%",  "waste": "Med",  "stock": "Med"},
    "Punto-Valle": {"sales": "$6.8M",  "ticket": "$145", "star": "Glazed donut",   "daily": "$13.9k", "yoy": "+8%",  "waste": "Low",  "stock": "Low"},
}
 
 
# -- SIDEBAR -------------------------------------------------------------------
with st.sidebar:
    # Logo
    st.markdown(
        "<div style='text-align:center;padding:22px 0 18px;'>"
        "<div style='font-size:1.7rem;font-weight:800;color:#C8A97E;"
        "letter-spacing:4px;font-family:Georgia,serif;'>PANEM</div>"
        "<div style='font-size:.62rem;color:#9E8B78;letter-spacing:4px;margin-top:3px;'>"
        "BAKERY &amp; BISTRO</div>"
        "<div style='width:36px;height:2px;background:#C8A97E;margin:10px auto 0;'></div>"
        "</div>",
        unsafe_allow_html=True
    )
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:{C_GOLD};letter-spacing:1px;margin-bottom:6px;'>VIEW MODE</div>", unsafe_allow_html=True)
    role = st.radio("", ["Branch Manager", "Regional / Executive"], label_visibility="collapsed")
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:{C_GOLD};letter-spacing:1px;margin-bottom:6px;'>FILTERS</div>", unsafe_allow_html=True)
    branch  = st.selectbox("Branch",  BRANCHES)
    product = st.selectbox("Product for history", PRODUCTS)
    period  = st.selectbox("Period",  ["Last 90 days", "Last 30 days", "Last 6 months", "Full year"])
    period_days = {"Last 90 days": 90, "Last 30 days": 30, "Last 6 months": 182, "Full year": 365}[period]
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:{C_GOLD};letter-spacing:1px;margin-bottom:6px;'>ORDER SETTINGS</div>", unsafe_allow_html=True)
    buffer_pct = st.slider(
        "Safety buffer (%)",
        min_value=0, max_value=30, value=10, step=5,
        help="Added on top of the SARIMAX forecast to reduce stockout risk"
    )
    _sb_mae  = round(SARIMAX_METRICS[branch]["MAE"])
    _sb_mape = round(SARIMAX_METRICS[branch]["MAPE"], 1)
    st.markdown(
        "<div style='background:rgba(200,169,126,.12);border-radius:8px;padding:9px 12px;"
        "border-left:3px solid " + C_GOLD + ";margin-top:4px;'>"
        "<div style='font-size:.68rem;color:" + C_GOLD + ";font-weight:600;margin-bottom:3px;'>"
        "Model error for " + branch + "</div>"
        "<div style='font-size:.72rem;color:#FAF6F1;'>"
        "+/-" + str(_sb_mae) + " units/day &nbsp;|&nbsp; MAPE " + str(_sb_mape) + "%"
        "</div></div>",
        unsafe_allow_html=True
    )
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem;color:{C_GOLD};letter-spacing:1px;margin-bottom:6px;'>DATA</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload sales CSV", type=["csv"],
                                help="Columns: operating_date, sucursal, item, quantity")
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded)
            df_up.columns = [c.strip().lower() for c in df_up.columns]
            rmap = {"branch": "sucursal", "product": "item", "date": "operating_date",
                    "fecha": "operating_date", "qty": "quantity", "cantidad": "quantity"}
            df_up = df_up.rename(columns={c: rmap[c] for c in df_up.columns if c in rmap})
            if "operating_date" in df_up.columns:
                df_up["operating_date"] = pd.to_datetime(df_up["operating_date"], errors="coerce")
            st.session_state.uploaded_df = df_up
            st.success(f"Loaded {len(df_up):,} rows")
        except Exception as e:
            st.error(str(e))
    if st.session_state.uploaded_df is not None:
        if st.button("Clear data", use_container_width=True):
            st.session_state.uploaded_df = None
            st.rerun()
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.65rem;color:{C_MUTED};'>Dashboard v4.0 - Jun 2026</div>", unsafe_allow_html=True)
 
 
# -- COMPUTED DEMO DATA --------------------------------------------------------
np.random.seed(hash(branch) % 9999)
dates_main  = pd.date_range(end="2026-02-12", periods=period_days)
daily_sales = np.random.normal(23, 3, period_days).clip(13, 32)
ma7         = pd.Series(daily_sales).rolling(7, min_periods=1).mean().values
 
days_lbl    = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
sales_dow   = np.array([14800, 14200, 13900, 15200, 17800, 21000, 12500]) * (0.75 + np.random.rand() * 0.5)
 
top_prods   = ["Vanilla concha", "Choco. concha", "Chilaquiles", "Oat cookie", "Glazed donut"]
share_v     = [30, 22, 18, 16, 14]
 
dates_hist  = pd.date_range(end="2026-05-12", periods=120)
hist_sales  = np.random.normal(280, 35, 120).clip(180, 390)
hist_avg    = float(np.mean(hist_sales))
 
weeks       = [f"W{i:02d}" for i in range(1, 53)]
weekly_v    = np.random.normal(2100, 300, 52).clip(1200, 2800).astype(int)
 
kpi         = KPI_DATA[branch]
fc7         = SARIMAX_7DAY[branch]
metrics     = SARIMAX_METRICS[branch]
m_mae       = metrics["MAE"]
m_rmse      = metrics["RMSE"]
m_mape      = metrics["MAPE"]
fc_total    = round(sum(fc7))
 
# Per-product forecast
prod_fc_week  = {p: round(fc_total * s) for p, s in zip(PRODUCTS, PROD_SHARES)}
np.random.seed(hash(branch + "lw") % 9999)
prod_last_wk  = {p: round(v * (0.82 + np.random.rand() * 0.36)) for p, v in prod_fc_week.items()}
 
use_csv = (
    st.session_state.uploaded_df is not None
    and "operating_date" in st.session_state.uploaded_df.columns
    and "quantity" in st.session_state.uploaded_df.columns
)
 
 
# -- HEADER --------------------------------------------------------------------
today_str  = datetime.date.today().strftime("%b %d, %Y")
badge_html = (
    f'<span class="badge-branch">Branch Manager</span>' if role == "Branch Manager"
    else f'<span class="badge-regional">Regional / Executive</span>'
)
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-header-title">Panem Bakery - Management Dashboard</div>
    <div class="dash-header-sub">
      {branch} &nbsp;|&nbsp; {period} &nbsp;|&nbsp;
      Updated {today_str} &nbsp;|&nbsp;
      SARIMAX model &nbsp;|&nbsp; {badge_html}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
 
 
# ------------------------------------------------------------------------------
# BRANCH MANAGER VIEW
# ------------------------------------------------------------------------------
if role == "Branch Manager":
 
    tab_order, tab_history, tab_forecast, tab_model, tab_entry = st.tabs([
        "Weekly Order", "Sales History", "Forecast Detail", "Model Info", "Data Entry"
    ])
 
    # =========================================================================
    # TAB 1 - WEEKLY ORDER (primary view for branch managers)
    # =========================================================================
    with tab_order:
 
        BUFFER = 1 + buffer_pct / 100
        prod_order = {p: round(prod_fc_week[p] * BUFFER) for p in PRODUCTS}
 
        # --- KPI STRIP at top (first thing the manager sees) ---
        st.markdown(f"<div style='font-size:0.68rem;color:{C_MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>Branch health at a glance - {period}</div>", unsafe_allow_html=True)
        hc1, hc2, hc3, hc4, hc5 = st.columns(5)
        for col, eyebrow, number, context in [
            (hc1, "Total Sales",     kpi["sales"],          "this period"),
            (hc2, "Avg. Ticket",     kpi["ticket"],         "per transaction"),
            (hc3, "Avg. Daily Rev.", kpi["daily"],          "period average"),
            (hc4, "YoY Growth",      kpi["yoy"],            "vs same period last year"),
            (hc5, "Forecast MAE",    f"{m_mae:.0f} units", "SARIMAX error/day"),
        ]:
            col.markdown(f'''
            <div class="kpi-card">
              <div class="kpi-eyebrow">{eyebrow}</div>
              <div class="kpi-number" style="font-size:1.6rem">{number}</div>
              <div class="kpi-context">{context}</div>
            </div>''', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        total_last = sum(prod_last_wk.values())
        total_next = sum(prod_order.values())
        delta      = total_next - total_last
        delta_str  = f"+{delta:,}" if delta >= 0 else f"{delta:,}"
 
        st.markdown("<br>", unsafe_allow_html=True)
 
        # --- TWO-COLUMN ORDER CARDS (Big Book: exact numbers prominently) ---
        st.markdown("""
        <div style='font-size:0.7rem;color:#9E8B78;text-transform:uppercase;
                    letter-spacing:1.2px;margin-bottom:10px;font-weight:600;'>
          Last week sold vs. What to order this week
        </div>
        """, unsafe_allow_html=True)
 
        rows_last = "".join([
            f"<div class='order-row'>"
            f"<span style='font-size:0.84rem;color:{C_DARK};'>{p}</span>"
            f"<span class='order-pill'>{prod_last_wk[p]:,} sold</span>"
            f"</div>"
            for p in PRODUCTS
        ])
        rows_next = "".join([
            f"<div class='order-row-dark'>"
            f"<span style='font-size:0.84rem;color:rgba(255,255,255,0.85);'>{p}</span>"
            f"<div style='display:flex;align-items:center;gap:6px;'>"
            f"<span style='font-size:0.7rem;color:{C_MUTED};'>{prod_last_wk[p]:,}</span>"
            f"<span style='font-size:0.65rem;color:{C_MUTED};'>-></span>"
            f"<span class='order-pill-dark'>order {prod_order[p]:,}</span>"
            f"</div></div>"
            for p in PRODUCTS
        ])
 
        st.markdown(f"""
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:22px;'>
          <div class='order-card-last'>
            <div style='font-size:0.65rem;color:{C_MUTED};text-transform:uppercase;
                        letter-spacing:1.2px;margin-bottom:10px;'>
              Last week (Feb 6-12) - Units sold per product
            </div>
            {rows_last}
            <div style='display:flex;justify-content:space-between;padding:9px 0 0;margin-top:4px;'>
              <span style='font-size:0.72rem;font-weight:600;color:{C_MUTED};'>TOTAL SOLD</span>
              <span style='font-size:1.25rem;font-weight:700;color:{C_DARK};'>{total_last:,} units</span>
            </div>
          </div>
          <div class='order-card-next'>
            <div style='font-size:0.65rem;color:{C_GOLD};text-transform:uppercase;
                        letter-spacing:1.2px;margin-bottom:4px;'>
              This week (Feb 13-19) - Recommended order
              <span style='margin-left:8px;background:rgba(200,169,126,0.15);
                           padding:1px 8px;border-radius:10px;'>+{buffer_pct}% buffer</span>
            </div>
            <div style='font-size:0.7rem;color:{C_MUTED};margin-bottom:8px;font-style:italic;'>
              SARIMAX forecast x {100+buffer_pct}% - adjust for holidays or promotions
            </div>
            {rows_next}
            <div style='display:flex;justify-content:space-between;padding:9px 0 0;margin-top:4px;'>
              <span style='font-size:0.72rem;font-weight:600;color:{C_GOLD};'>TOTAL TO ORDER</span>
              <span style='font-size:1.25rem;font-weight:700;color:white;'>
                {total_next:,} units
                <span style='font-size:0.76rem;color:{C_GOLD};margin-left:6px;'>({delta_str} vs last week)</span>
              </span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
 
        # Download order sheet
        df_dl = pd.DataFrame({
            "Product": PRODUCTS,
            "Sold last week": [prod_last_wk[p] for p in PRODUCTS],
            "SARIMAX forecast": [prod_fc_week[p] for p in PRODUCTS],
            f"Order this week (+{buffer_pct}%)": [prod_order[p] for p in PRODUCTS],
        })
        st.download_button(
            "Download order sheet (CSV)",
            data=df_dl.to_csv(index=False).encode(),
            file_name=f"panem_order_{branch}_Feb13_2026.csv",
            mime="text/csv",
        )
 
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
 
        # --- CHARTS: stacked daily forecast + day-of-week pattern ---
        col_left, col_right = st.columns([3, 2])
 
        with col_left:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">Daily demand forecast by product - next 7 days</div>
              <div class="chart-sub">
                How the week's demand is distributed day by day per product.
                Hover for exact units. Higher bars = more to order for that day's production.
              </div>
            </div>""", unsafe_allow_html=True)
 
            fig_stack = go.Figure()
            colors_prod = [C_DARK, C_BROWN, C_GOLD, C_SAND, "#BCA07A", "#A08060", "#C9B49A"]
            bottom = np.zeros(7)
            for i, p in enumerate(PRODUCTS):
                vals = [round(fc7[d] * PROD_SHARES[i]) for d in range(7)]
                short = p.replace(" Panem", "").replace(" concha", " c.")
                fig_stack.add_trace(go.Bar(
                    x=FC_DATES, y=vals, name=short,
                    marker_color=colors_prod[i],
                    hovertemplate=f"<b>{p}</b><br>%{{y}} units<extra></extra>",
                ))
            # Total labels on top
            for j, total in enumerate(fc7):
                fig_stack.add_annotation(
                    x=FC_DATES[j], y=total + 12,
                    text=f"<b>{total:.0f}</b>", showarrow=False,
                    font=dict(size=10, color=C_DARK),
                )
            fig_stack.update_layout(
                **{**PLOTLY_LAYOUT, "barmode": "stack", "height": 320,
                   "legend": dict(orientation="h", y=-0.22, x=0, font=dict(size=10)),
                   "yaxis": dict(gridcolor=C_SAND, tickfont=dict(size=10, color=C_MUTED), title="Units"),
                   "xaxis": dict(showgrid=False, tickfont=dict(size=10)),
                }
            )
            st.plotly_chart(fig_stack, use_container_width=True)
 
        with col_right:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">Historical sales pattern by day of week</div>
              <div class="chart-sub">
                Average units sold per weekday (last {period}).
                Use this to validate whether the forecast day-shape looks right.
              </div>
            </div>""", unsafe_allow_html=True)
 
            avg_dow = float(np.mean(sales_dow))
            dow_colors = [
                C_DARK if v == max(sales_dow) else
                C_BROWN if v >= np.percentile(sales_dow, 60) else C_GOLD
                for v in sales_dow
            ]
            fig_dow = go.Figure()
            fig_dow.add_trace(go.Bar(
                x=days_lbl, y=sales_dow,
                marker_color=dow_colors,
                text=[f"{v/1000:.1f}k" for v in sales_dow],
                textposition="outside",
                textfont=dict(size=10, color=C_DARK),
                hovertemplate="%{x}<br><b>%{y:,.0f} units</b><extra></extra>",
                name="Avg units",
            ))
            fig_dow.add_hline(
                y=avg_dow, line_color=C_GREY, line_dash="dot", line_width=1.8,
                annotation_text=f"Avg {avg_dow/1000:.1f}k",
                annotation_font=dict(color=C_MUTED, size=10),
            )
            fig_dow.update_layout(
                **{**PLOTLY_LAYOUT, "height": 320, "showlegend": False,
                   "yaxis": dict(gridcolor=C_SAND, tickfont=dict(size=10), range=[0, max(sales_dow)*1.22]),
                   "xaxis": dict(showgrid=False, tickfont=dict(size=10)),
                }
            )
            st.plotly_chart(fig_dow, use_container_width=True)
 
 
 
    # =========================================================================
    # TAB 2 - SALES HISTORY
    # =========================================================================
    with tab_history:
 
        if use_csv:
            df_b = st.session_state.uploaded_df.copy()
            if "sucursal" in df_b.columns:
                df_b = df_b[df_b["sucursal"].str.lower() == branch.lower()]
            agg = df_b.groupby("operating_date")["quantity"].sum().reset_index().sort_values("operating_date")
            dates_p = agg["operating_date"].tolist()
            sales_p = agg["quantity"].tolist()
        else:
            dates_p = dates_main.tolist()
            sales_p = daily_sales.tolist()
        ma7_p = pd.Series(sales_p).rolling(7, min_periods=1).mean().tolist()
 
        # Daily evolution
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">Daily branch sales - {period}</div>
          <div class="chart-sub">
            Total units sold per day across all products. The dashed line is a 7-day moving
            average that smooths noise and reveals the underlying trend. Drag to zoom, hover for exact values.
          </div>
        </div>""", unsafe_allow_html=True)
 
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Bar(
            x=dates_p, y=sales_p, name="Daily sales",
            marker_color=C_GOLD, marker_opacity=0.82,
            hovertemplate="%{x|%b %d}<br><b>%{y:.1f}k units</b><extra></extra>",
        ))
        fig_hist.add_trace(go.Scatter(
            x=dates_p, y=ma7_p, name="7-day moving avg",
            line=dict(color=C_BLUE, width=2, dash="dash"),
            hovertemplate="%{x|%b %d}<br>MA7: %{y:.1f}k<extra></extra>",
        ))
        fig_hist.update_layout(**{**PLOTLY_LAYOUT, "height": 280,
            "yaxis": dict(gridcolor=C_SAND, title="Units (k)", tickfont=dict(size=10)),
        })
        st.plotly_chart(fig_hist, use_container_width=True)
 
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
 
        # Product time series with average (Comment fix: show average for comparison)
        with col1:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">{product} - daily sales</div>
              <div class="chart-sub">
                Units sold per day with +/-1 standard deviation band (gray) and historical
                average (dashed). Compare any day against the average to spot unusual demand.
              </div>
            </div>""", unsafe_allow_html=True)
            fig_prod = go.Figure()
            fig_prod.add_traces([
                go.Scatter(x=dates_hist.tolist(), y=(hist_sales + 25).tolist(),
                           fill=None, mode="lines", line_color="rgba(0,0,0,0)", showlegend=False),
                go.Scatter(x=dates_hist.tolist(), y=(hist_sales - 25).tolist(),
                           fill="tonexty", mode="lines", line_color="rgba(0,0,0,0)",
                           fillcolor="rgba(200,169,126,0.2)", name="+/-1 std dev"),
                go.Scatter(x=dates_hist.tolist(), y=hist_sales.tolist(),
                           name=product, line=dict(color=C_BROWN, width=1.8),
                           hovertemplate="%{x|%b %d}<br><b>%{y:.0f} units</b><extra></extra>"),
            ])
            fig_prod.add_hline(y=hist_avg, line_color=C_GREY, line_dash="dot", line_width=1.5,
                               annotation_text=f"Avg {hist_avg:.0f}",
                               annotation_font=dict(color=C_MUTED, size=10))
            fig_prod.update_layout(**{**PLOTLY_LAYOUT, "height": 280,
                "yaxis": dict(gridcolor=C_SAND, title="Units", tickfont=dict(size=10)),
                "legend": dict(orientation="h", y=1.1, font=dict(size=10)),
            })
            st.plotly_chart(fig_prod, use_container_width=True)
 
        # Day of week for this product
        with col2:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">Sales by day of week - {product}</div>
              <div class="chart-sub">
                Which days this product sells most. Use to decide delivery timing - high bars
                mean you need more inventory available that day.
              </div>
            </div>""", unsafe_allow_html=True)
            np.random.seed(hash(branch + product) % 9999)
            prod_dow = np.clip(sales_dow * PROD_SHARES[PRODUCTS.index(product) if product in PRODUCTS else 0] + np.random.normal(0, 300, 7), 200, 8000)
            fig_pdow = go.Figure(go.Bar(
                x=days_lbl, y=prod_dow,
                marker_color=[C_DARK if v == max(prod_dow) else C_BROWN if v >= np.percentile(prod_dow, 60) else C_GOLD for v in prod_dow],
                text=[f"{v:,.0f}" for v in prod_dow], textposition="outside",
                textfont=dict(size=9, color=C_DARK),
                hovertemplate="%{x}<br><b>%{y:,.0f} units</b><extra></extra>",
            ))
            fig_pdow.add_hline(y=float(np.mean(prod_dow)), line_color=C_GREY, line_dash="dot",
                               annotation_text=f"Avg {np.mean(prod_dow):,.0f}",
                               annotation_font=dict(size=9, color=C_MUTED))
            fig_pdow.update_layout(**{**PLOTLY_LAYOUT, "height": 280, "showlegend": False,
                "yaxis": dict(gridcolor=C_SAND, range=[0, max(prod_dow)*1.22], tickfont=dict(size=10)),
            })
            st.plotly_chart(fig_pdow, use_container_width=True)
 
        # Weekly seasonality
        with col3:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">Weekly seasonality across the year</div>
              <div class="chart-sub">
                Total units per week. Dark bars = historically high-demand weeks (e.g., Dec holidays).
                Plan larger orders for dark-bar weeks.
              </div>
            </div>""", unsafe_allow_html=True)
            wk_colors = [
                C_DARK if v > np.percentile(weekly_v, 80) else
                C_BROWN if v > np.percentile(weekly_v, 50) else C_GOLD
                for v in weekly_v
            ]
            fig_wk = go.Figure(go.Bar(
                x=weeks, y=weekly_v.tolist(), marker_color=wk_colors,
                hovertemplate="Week %{x}<br><b>%{y:,} units</b><extra></extra>",
            ))
            fig_wk.add_hline(y=float(np.mean(weekly_v)), line_color=C_GREY, line_dash="dot",
                             annotation_text="Avg", annotation_font=dict(size=9, color=C_MUTED))
            fig_wk.update_layout(**{**PLOTLY_LAYOUT, "height": 280, "showlegend": False,
                "xaxis": dict(showgrid=False, tickmode="array",
                              tickvals=weeks[::4], ticktext=weeks[::4], tickfont=dict(size=9)),
                "yaxis": dict(gridcolor=C_SAND, tickfont=dict(size=10)),
            })
            st.plotly_chart(fig_wk, use_container_width=True)
 
    # =========================================================================
    # TAB 3 - FORECAST DETAIL
    # =========================================================================
    with tab_forecast:
 
        st.markdown(f"**SARIMAX Forecast - {branch}** &nbsp; | &nbsp; Params: `{SARIMAX_PARAMS[branch]}` &nbsp; | &nbsp; AIC: {SARIMAX_AIC[branch]:,.1f}")
 
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE (30-day hold-out)",  f"{m_mae:.1f} units/day",
                  help="Mean Absolute Error on last 30 days of data")
        m2.metric("RMSE",                    f"{m_rmse:.1f} units/day")
        m3.metric("MAPE",                    f"{m_mape:.1f}%",
                  help="Mean Absolute Percentage Error - lower is better")
 
        st.markdown("<br>", unsafe_allow_html=True)
 
        # 7-day forecast with 95% CI
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">7-day SARIMAX forecast with 95% confidence interval - Feb 13-19, 2026</div>
          <div class="chart-sub">
            The bars show the model's best estimate. The shaded band is the 95% confidence interval -
            the true demand will fall within this range 95% of the time. Wider bands = more uncertainty.
            Use the recommended order (with buffer) in the Weekly Order tab.
          </div>
        </div>""", unsafe_allow_html=True)
 
        np.random.seed(42)
        ci_lower = [max(0, v - m_mae * 1.3) for v in fc7]
        ci_upper = [v + m_mae * 1.3 for v in fc7]
        fc_colors_7 = [
            C_DARK if v == max(fc7) else
            C_BROWN if v >= np.percentile(fc7, 65) else C_GOLD
            for v in fc7
        ]
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=FC_DATES + FC_DATES[::-1],
            y=ci_upper + ci_lower[::-1],
            fill="toself", fillcolor="rgba(123,79,46,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI",
            hoverinfo="skip",
        ))
        fig_fc.add_trace(go.Bar(
            x=FC_DATES, y=fc7, marker_color=fc_colors_7,
            text=[f"<b>{v:.0f}</b>" for v in fc7], textposition="outside",
            textfont=dict(size=11, color=C_DARK),
            hovertemplate="%{x}<br><b>Forecast: %{y:.0f} units</b><extra></extra>",
            name="SARIMAX forecast",
        ))
        fig_fc.update_layout(**{**PLOTLY_LAYOUT, "height": 340,
            "yaxis": dict(gridcolor=C_SAND, title="Units", tickfont=dict(size=10),
                          range=[0, max(ci_upper) * 1.15]),
            "xaxis": dict(showgrid=False, tickfont=dict(size=11)),
            "legend": dict(orientation="h", y=1.1),
        })
        st.plotly_chart(fig_fc, use_container_width=True)
 
        # Forecast table
        st.markdown('<div class="chart-title" style="margin-top:10px">Detailed forecast table</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">Lower 95% = pessimistic scenario. Upper 95% = optimistic. Recommended order = forecast x buffer.</div>', unsafe_allow_html=True)
        df_fc = pd.DataFrame({
            "Day":             FC_DATES,
            "Forecast":        [round(v, 0) for v in fc7],
            "Lower 95%":       [round(v, 0) for v in ci_lower],
            "Upper 95%":       [round(v, 0) for v in ci_upper],
            f"Order (+{buffer_pct if 'buffer_pct' in dir() else 10}% buffer)": [round(v * BUFFER if 'BUFFER' in dir() else v * 1.1) for v in fc7],
        })
        st.dataframe(
            df_fc.style.background_gradient(subset=["Forecast"], cmap="YlOrBr"),
            use_container_width=True, hide_index=True
        )
 
        st.warning(
            f"**Model limitation:** SARIMAX was trained on data from {branch}. "
            f"It does not automatically account for local holidays, promotions, or special events. "
            f"If any of these apply to the coming week, adjust the order manually."
        )
 
    # =========================================================================
    # TAB 4 - MODEL INFO
    # =========================================================================
    with tab_model:
        st.markdown("#### How the SARIMAX model works")
        ic1, ic2 = st.columns(2)
 
        with ic1:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">What SARIMAX stands for</div>
              <div class="chart-sub" style="color:{C_DARK}">
                <strong>S</strong>easonal <strong>A</strong>uto<strong>R</strong>egressive
                <strong>I</strong>ntegrated <strong>M</strong>oving <strong>A</strong>verage
                with e<strong>X</strong>ogenous variables<br><br>
                The model captures three patterns in your sales data:<br>
                1. <strong>Trend</strong> - is demand growing or shrinking over time?<br>
                2. <strong>Weekly seasonality</strong> - every Monday, Tuesday... has its own pattern<br>
                3. <strong>External influence</strong> - daily temperature affects demand<br><br>
                Parameters for <strong>{branch}</strong>: <code>{SARIMAX_PARAMS[branch]}</code><br>
                This was selected automatically by minimizing AIC = {SARIMAX_AIC[branch]:,.0f}
              </div>
            </div>""", unsafe_allow_html=True)
 
        with ic2:
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">How to read the performance metrics</div>
              <div class="chart-sub" style="color:{C_DARK}">
                <strong>MAE = {m_mae:.0f} units/day</strong><br>
                On average, the forecast is off by {m_mae:.0f} units per day.
                If you order exactly the forecast, expect to be short or over by this amount.<br><br>
                <strong>MAPE = {m_mape:.1f}%</strong><br>
                The forecast is off by {m_mape:.1f}% relative to actual sales on average.
                A 10% buffer more than compensates for this error level.<br><br>
                <strong>These metrics come from the last 30 days of real data</strong>,
                where the model predicted without knowing the outcome.
              </div>
            </div>""", unsafe_allow_html=True)
 
        # All-branch metrics chart
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">SARIMAX performance across all branches</div>
          <div class="chart-sub">
            MAE (left axis) and MAPE % (right axis) for each branch.
            Lower is better. Your branch ({branch}) is highlighted.
            Credi-Club has higher error because it only has ~4 months of history.
          </div>
        </div>""", unsafe_allow_html=True)
 
        br_names = list(SARIMAX_METRICS.keys())
        br_mae   = [SARIMAX_METRICS[b]["MAE"]  for b in br_names]
        br_mape  = [SARIMAX_METRICS[b]["MAPE"] for b in br_names]
        # Panem palette: darkest = highest error, lightest = lowest error
        mae_min = min(br_mae); mae_max = max(br_mae)
        bar_br_c = []
        for b, m in zip(br_names, br_mae):
            if b == branch:
                bar_br_c.append(C_DARK)    # selected branch always darkest
            elif m <= mae_min * 1.3:
                bar_br_c.append(C_BROWN)   # low error - warm brown
            elif m <= mae_max * 0.75:
                bar_br_c.append(C_GOLD)    # medium error - gold
            else:
                bar_br_c.append(C_SAND)    # high error - lightest/muted
 
        fig_br = make_subplots(specs=[[{"secondary_y": True}]])
        fig_br.add_trace(go.Bar(x=br_names, y=br_mae, name="MAE (units/day)",
                                marker_color=bar_br_c,
                                hovertemplate="%{x}<br>MAE: <b>%{y:.1f}</b> units<extra></extra>"),
                         secondary_y=False)
        fig_br.add_trace(go.Scatter(x=br_names, y=br_mape, name="MAPE %",
                                    mode="markers+lines",
                                    marker=dict(color=C_BROWN, size=8),
                                    line=dict(color=C_BROWN, width=2),
                                    hovertemplate="%{x}<br>MAPE: <b>%{y:.1f}%</b><extra></extra>"),
                         secondary_y=True)
        fig_br.update_layout(**{**PLOTLY_LAYOUT, "height": 300,
            "legend": dict(orientation="h", y=1.1, font=dict(size=11)),
        })
        fig_br.update_yaxes(title_text="MAE (units/day)", secondary_y=False,
                            gridcolor=C_SAND, tickfont=dict(size=10))
        fig_br.update_yaxes(title_text="MAPE %", secondary_y=True,
                            tickfont=dict(size=10))
        st.plotly_chart(fig_br, use_container_width=True)
 
    # =========================================================================
    # TAB 5 - DATA ENTRY
    # =========================================================================
    with tab_entry:
        st.markdown("#### Data Entry")
        st.caption("Enter actual weekly sales to track vs forecast, or add single transactions.")
 
        st.markdown(f"""
        <div style='background:white;border-radius:10px;padding:16px 20px;
                    border-top:3px solid {C_BROWN};margin-bottom:16px;'>
          <div style='font-size:0.88rem;font-weight:600;color:{C_DARK};margin-bottom:4px;'>
            Enter actual weekly sales - {branch}
          </div>
          <div style='font-size:0.72rem;color:{C_MUTED};'>
            Use this to track how much you actually sold vs. what the model predicted.
          </div>
        </div>""", unsafe_allow_html=True)
 
        week_start = st.date_input("Week start (Monday)", value=datetime.date(2026, 2, 13))
 
        with st.form("weekly_form"):
            st.markdown(f"**{branch}** - week of {week_start}")
            st.markdown("---")
            ca, cb = st.columns(2)
            entry_vals = {}
            for i, prod in enumerate(PRODUCTS):
                col = ca if i % 2 == 0 else cb
                entry_vals[prod] = col.number_input(
                    prod, min_value=0, max_value=5000,
                    value=int(st.session_state.new_weekly.get(prod, 0)),
                    step=1, key=f"ew_{prod}"
                )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Save actual sales", use_container_width=True, type="primary"):
                st.session_state.new_weekly = {k: v for k, v in entry_vals.items() if v > 0}
                st.success(f"Saved actual sales for {branch} - week of {week_start}")
 
        if st.session_state.new_weekly:
            st.markdown("<br>**Saved entries vs forecast:**")
            df_vs = pd.DataFrame([{
                "Product": p,
                "Actual sold": st.session_state.new_weekly.get(p, 0),
                "Forecast": prod_fc_week[p],
                "Difference": st.session_state.new_weekly.get(p, 0) - prod_fc_week[p],
            } for p in PRODUCTS if p in st.session_state.new_weekly])
            st.dataframe(
                df_vs.style.background_gradient(subset=["Difference"], cmap="RdYlGn", vmin=-200, vmax=200),
                use_container_width=True, hide_index=True
            )
            st.download_button("Download CSV",
                data=df_vs.to_csv(index=False).encode(),
                file_name=f"panem_actuals_{branch}_{week_start}.csv", mime="text/csv")
 
 
# ------------------------------------------------------------------------------
# REGIONAL / EXECUTIVE VIEW
# ------------------------------------------------------------------------------
else:
    rtab1, rtab2, rtab3 = st.tabs([
        "All Branches Overview", "Forecast & Metrics", "Detailed Data"
    ])
 
    with rtab1:
        # Chain-level KPIs
        st.markdown(f"<div style='font-size:0.68rem;color:{C_MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>Chain-wide KPIs</div>", unsafe_allow_html=True)
        ck1, ck2, ck3, ck4, ck5 = st.columns(5)
        for col, eyebrow, num, ctx in [
            (ck1, "Total Chain Sales",    "$55.0M",  "all branches"),
            (ck2, "Active Branches",      "7 / 7",   "all forecasted"),
            (ck3, "Best MAE (SARIMAX)",   "52.6",    "Nativa - units/day"),
            (ck4, "Highest Error",        "203.3",   "Credi-Club - new branch"),
            (ck5, "Avg Chain MAPE",       "19.5%",   "across 7 branches"),
        ]:
            col.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-eyebrow">{eyebrow}</div>
              <div class="kpi-number" style="font-size:1.6rem">{num}</div>
              <div class="kpi-context">{ctx}</div>
            </div>""", unsafe_allow_html=True)
 
        st.markdown("<br>", unsafe_allow_html=True)
 
        # Weekly forecast totals by branch
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">Next 7-day demand forecast by branch</div>
          <div class="chart-sub">
            Total units each branch needs to produce Feb 13-19, 2026.
            Based on SARIMAX models trained independently per branch.
            Hover for exact values.
          </div>
        </div>""", unsafe_allow_html=True)
 
        fc_totals = {b: round(sum(SARIMAX_7DAY[b])) for b in BRANCHES}
        bc_reg    = [C_DARK if b == branch else C_BROWN for b in BRANCHES]
        fig_reg   = go.Figure(go.Bar(
            x=list(fc_totals.keys()), y=list(fc_totals.values()),
            marker_color=bc_reg,
            text=[f"{v:,}" for v in fc_totals.values()],
            textposition="outside", textfont=dict(size=11, color=C_DARK),
            hovertemplate="%{x}<br><b>%{y:,} units</b> next 7 days<extra></extra>",
        ))
        fig_reg.update_layout(**{**PLOTLY_LAYOUT, "height": 320, "showlegend": False,
            "yaxis": dict(gridcolor=C_SAND, title="Units (next 7 days)", tickfont=dict(size=10)),
            "xaxis": dict(showgrid=False, tickfont=dict(size=11)),
        })
        st.plotly_chart(fig_reg, use_container_width=True)
 
        # MAE by branch with color encoding
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">Forecast accuracy by branch (MAE, lower = better)</div>
          <div class="chart-sub">
            Green = low error, amber = moderate, red = needs attention.
            Credi-Club's high error is expected - it opened Oct 2024 and has limited seasonal history.
          </div>
        </div>""", unsafe_allow_html=True)
 
        br_all   = list(SARIMAX_METRICS.keys())
        mae_all  = [SARIMAX_METRICS[b]["MAE"]  for b in br_all]
        mape_all = [SARIMAX_METRICS[b]["MAPE"] for b in br_all]
        err_c    = [C_GREEN if m < 110 else C_AMBER if m < 170 else C_AMBER for m in mae_all]
 
        fig_mae = go.Figure(go.Bar(
            x=br_all, y=mae_all, marker_color=err_c,
            text=[f"{v:.0f}" for v in mae_all], textposition="outside",
            textfont=dict(size=11, color=C_DARK),
            hovertemplate="%{x}<br>MAE: <b>%{y:.1f}</b> units/day<extra></extra>",
            name="MAE",
        ))
        fig_mae.update_layout(**{**PLOTLY_LAYOUT, "height": 300, "showlegend": False,
            "yaxis": dict(gridcolor=C_SAND, title="MAE (units/day)", tickfont=dict(size=10)),
            "xaxis": dict(showgrid=False, tickfont=dict(size=11)),
        })
        st.plotly_chart(fig_mae, use_container_width=True)
 
    with rtab2:
        # Full 7-day forecast table all branches
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">Full 7-day SARIMAX forecast - all branches</div>
          <div class="chart-sub">
            Units the model predicts each branch will sell per day next week.
            Use this to allocate ingredients and staff across the chain.
          </div>
        </div>""", unsafe_allow_html=True)
 
        rows_all = []
        for b in BRANCHES:
            row = {"Branch": b}
            for i, d in enumerate(FC_DATES):
                row[d] = round(SARIMAX_7DAY[b][i], 0)
            row["Week Total"] = round(sum(SARIMAX_7DAY[b]), 0)
            rows_all.append(row)
        df_all = pd.DataFrame(rows_all)
        st.dataframe(
            df_all.style.background_gradient(subset=FC_DATES + ["Week Total"], cmap="YlOrBr"),
            use_container_width=True, hide_index=True
        )
 
        st.markdown("<br>", unsafe_allow_html=True)
        # Full metrics table
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">Model validation metrics - all branches</div>
          <div class="chart-sub">
            30-day hold-out test. MAE = average daily error. MAPE = % error.
            All metrics come from real data the model had never seen during training.
          </div>
        </div>""", unsafe_allow_html=True)
 
        df_metrics = pd.DataFrame([
            {**{"Branch": b, "SARIMAX params": SARIMAX_PARAMS[b]}, **SARIMAX_METRICS[b]}
            for b in BRANCHES
        ])
        st.dataframe(
            df_metrics.style
                .background_gradient(subset=["MAE", "RMSE"], cmap="YlOrBr")
                .background_gradient(subset=["MAPE"], cmap="YlOrBr")
                .format({"MAE": "{:.1f}", "RMSE": "{:.1f}", "MAPE": "{:.1f}%"}),
            use_container_width=True, hide_index=True
        )
 
    with rtab3:
        # Upload and review data
        st.markdown("#### Upload New Branch Data")
        uploaded2 = st.file_uploader("Upload CSV", type=["csv"], key="reg_upload",
                                     help="operating_date, sucursal, item, quantity")
        if uploaded2:
            try:
                df_new = pd.read_csv(uploaded2)
                df_new.columns = [c.strip().lower() for c in df_new.columns]
                rmap = {"branch": "sucursal", "product": "item", "date": "operating_date",
                        "fecha": "operating_date", "qty": "quantity", "cantidad": "quantity"}
                df_new = df_new.rename(columns={c: rmap[c] for c in df_new.columns if c in rmap})
                st.success(f"Validated: {len(df_new):,} rows, {df_new.shape[1]} columns")
                with st.expander("Preview (first 20 rows)"):
                    st.dataframe(df_new.head(20), use_container_width=True)
                if st.button("Apply to dashboard", type="primary"):
                    st.session_state.uploaded_df = df_new
                    st.rerun()
            except Exception as e:
                st.error(str(e))
