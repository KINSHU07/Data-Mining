import streamlit as st
from PIL import Image
import os
import pandas as pd

st.set_page_config(
    page_title="🌪️ India Extreme Weather EDA",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .block-container { padding: 2rem 3rem 3rem 3rem; }

    .hero {
        border-radius: 20px; padding: 2.5rem 3rem; margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .hero-cyclone  { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .hero-heatwave { background: linear-gradient(135deg, #1a0a00 0%, #2e1000 50%, #4a1800 100%); }
    .hero-aqi      { background: linear-gradient(135deg, #0a1a0a 0%, #0d2e1a 50%, #0a3020 100%); }
    .hero-rainfall { background: linear-gradient(135deg, #001a2e 0%, #00264d 50%, #003870 100%); }
    .hero h1 { font-size: 2.8rem; font-weight: 800; color: white; margin: 0; letter-spacing: -1px; }
    .hero p  { color: rgba(255,255,255,0.65); font-size: 1.05rem; margin-top: 0.5rem; }
    .hero .tag {
        display: inline-block; border-radius: 20px;
        padding: 3px 14px; font-size: 0.8rem; font-weight: 600; margin-right: 8px;
    }
    .tag-cyclone { background: rgba(232,67,147,0.2); color: #e84393; border: 1px solid rgba(232,67,147,0.4); }
    .tag-heat    { background: rgba(255,120,0,0.25); color: #ff9944; border: 1px solid rgba(255,120,0,0.4); }
    .tag-cold    { background: rgba(0,180,216,0.2);  color: #00b4d8; border: 1px solid rgba(0,180,216,0.4); }
    .tag-aqi     { background: rgba(0,184,148,0.2);  color: #00b894; border: 1px solid rgba(0,184,148,0.4); }
    .tag-aqi-warn{ background: rgba(253,203,110,0.25); color: #fdcb6e; border: 1px solid rgba(253,203,110,0.4); }
    .tag-aqi-bad { background: rgba(214,48,49,0.2);  color: #ff7675; border: 1px solid rgba(214,48,49,0.4); }
    .tag-rain    { background: rgba(9,132,227,0.25);  color: #74b9ff; border: 1px solid rgba(9,132,227,0.45); }
    .tag-rain-ex { background: rgba(0,100,200,0.2);   color: #a8d8ff; border: 1px solid rgba(0,100,200,0.4); }
    .tag-rain-def{ background: rgba(225,112,85,0.2);  color: #e17055; border: 1px solid rgba(225,112,85,0.4); }

    .kpi-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
        padding: 1.2rem 1.5rem; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-card-cyclone { background: linear-gradient(135deg, #1e1e3f, #2d2d6b); }
    .kpi-card-heat    { background: linear-gradient(135deg, #2e1000, #4a1800); }
    .kpi-card-aqi     { background: linear-gradient(135deg, #0a1f0a, #0d3020); }
    .kpi-card-rainfall{ background: linear-gradient(135deg, #00152e, #001f47); }
    .kpi-val-cyclone { font-size: 2rem; font-weight: 800; color: #e84393; }
    .kpi-val-heat    { font-size: 2rem; font-weight: 800; color: #ff9944; }
    .kpi-val-cold    { font-size: 2rem; font-weight: 800; color: #00b4d8; }
    .kpi-val-aqi     { font-size: 2rem; font-weight: 800; color: #00b894; }
    .kpi-val-aqi-warn{ font-size: 2rem; font-weight: 800; color: #fdcb6e; }
    .kpi-val-aqi-bad { font-size: 2rem; font-weight: 800; color: #ff7675; }
    .kpi-val-rain    { font-size: 2rem; font-weight: 800; color: #74b9ff; }
    .kpi-val-rain-ex { font-size: 2rem; font-weight: 800; color: #0984e3; }
    .kpi-val-rain-def{ font-size: 2rem; font-weight: 800; color: #e17055; }
    .kpi-lbl { font-size: 0.78rem; color: rgba(255,255,255,0.55); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

    .chart-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border: 1px solid rgba(255,255,255,0.07); border-radius: 18px;
        padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 12px 36px rgba(0,0,0,0.35);
    }
    .chart-card-heat {
        background: linear-gradient(135deg, #1a0a00, #1e1200);
        border: 1px solid rgba(255,120,0,0.12); border-radius: 18px;
        padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 12px 36px rgba(0,0,0,0.35);
    }
    .chart-card-aqi {
        background: linear-gradient(135deg, #0a1f0a, #0d2a1a);
        border: 1px solid rgba(0,184,148,0.15); border-radius: 18px;
        padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 12px 36px rgba(0,0,0,0.35);
    }
    .chart-card-rainfall {
        background: linear-gradient(135deg, #001a2e, #002244);
        border: 1px solid rgba(9,132,227,0.18); border-radius: 18px;
        padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 12px 36px rgba(0,0,0,0.35);
    }
    .chart-title { font-size: 1.15rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.4rem; }
    .chart-desc  { font-size: 0.88rem; color: rgba(255,255,255,0.5); line-height: 1.55; margin-bottom: 1rem; }
    .chart-badge {
        display: inline-block; font-size: 0.72rem; font-weight: 600; border-radius: 8px;
        padding: 2px 10px; margin-right: 6px; margin-bottom: 10px;
    }
    .badge-dist   { background: rgba(108,92,231,0.25); color: #a29bfe; border: 1px solid rgba(108,92,231,0.4); }
    .badge-trend  { background: rgba(232,67,147,0.2);  color: #fd79a8; border: 1px solid rgba(232,67,147,0.4); }
    .badge-geo    { background: rgba(0,184,148,0.2);   color: #55efc4; border: 1px solid rgba(0,184,148,0.4); }
    .badge-corr   { background: rgba(253,203,110,0.2); color: #fdcb6e; border: 1px solid rgba(253,203,110,0.4); }
    .badge-impact { background: rgba(225,112,85,0.2);  color: #e17055; border: 1px solid rgba(225,112,85,0.4); }
    .badge-heat   { background: rgba(255,120,0,0.2);   color: #ff9944; border: 1px solid rgba(255,120,0,0.4); }
    .badge-cold   { background: rgba(0,180,216,0.2);   color: #00b4d8; border: 1px solid rgba(0,180,216,0.4); }
    .badge-aqi    { background: rgba(0,184,148,0.2);   color: #00b894; border: 1px solid rgba(0,184,148,0.4); }
    .badge-poll   { background: rgba(214,48,49,0.2);   color: #ff7675; border: 1px solid rgba(214,48,49,0.4); }
    .badge-rain   { background: rgba(9,132,227,0.22);  color: #74b9ff; border: 1px solid rgba(9,132,227,0.4); }
    .badge-rain-x { background: rgba(0,60,150,0.25);   color: #a8d8ff; border: 1px solid rgba(0,60,150,0.4); }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
        min-width: 260px !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small {
        color: rgba(255,255,255,0.85) !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important; visibility: visible !important; opacity: 1 !important;
        background: #e84393 !important; border-radius: 0 8px 8px 0 !important;
        box-shadow: 3px 0 20px rgba(232,67,147,0.7) !important; z-index: 9999 !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important; color: white !important; stroke: white !important;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none !important; }

    .section-header-cyclone {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #e84393; padding-left: 14px; margin: 2rem 0 1.2rem 0;
    }
    .section-header-heat {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #ff9944; padding-left: 14px; margin: 2rem 0 1.2rem 0;
    }
    .section-header-aqi {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #00b894; padding-left: 14px; margin: 2rem 0 1.2rem 0;
    }
    .section-header-rainfall {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #0984e3; padding-left: 14px; margin: 2rem 0 1.2rem 0;
    }

    .insight-cyclone {
        background: linear-gradient(135deg, rgba(232,67,147,0.08), rgba(108,92,231,0.08));
        border: 1px solid rgba(232,67,147,0.25); border-radius: 12px;
        padding: 1rem 1.3rem; margin-top: 1rem; font-size: 0.88rem;
        color: rgba(255,255,255,0.75); line-height: 1.6;
    }
    .insight-cyclone strong { color: #fd79a8; }

    .insight-heat {
        background: linear-gradient(135deg, rgba(255,120,0,0.08), rgba(255,60,0,0.08));
        border: 1px solid rgba(255,120,0,0.25); border-radius: 12px;
        padding: 1rem 1.3rem; margin-top: 1rem; font-size: 0.88rem;
        color: rgba(255,255,255,0.75); line-height: 1.6;
    }
    .insight-heat strong { color: #ff9944; }

    .insight-aqi {
        background: linear-gradient(135deg, rgba(0,184,148,0.08), rgba(0,150,100,0.08));
        border: 1px solid rgba(0,184,148,0.25); border-radius: 12px;
        padding: 1rem 1.3rem; margin-top: 1rem; font-size: 0.88rem;
        color: rgba(255,255,255,0.75); line-height: 1.6;
    }
    .insight-aqi strong { color: #00b894; }

    .insight-rainfall {
        background: linear-gradient(135deg, rgba(9,132,227,0.08), rgba(0,80,160,0.08));
        border: 1px solid rgba(9,132,227,0.28); border-radius: 12px;
        padding: 1rem 1.3rem; margin-top: 1rem; font-size: 0.88rem;
        color: rgba(255,255,255,0.75); line-height: 1.6;
    }
    .insight-rainfall strong { color: #74b9ff; }

    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 5px 10px !important; border-radius: 8px !important;
        transition: background 0.2s !important; cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(232,67,147,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_img(name):
    return Image.open(name) if os.path.exists(name) else None

def try_load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return None

def fmt(v, prefix="", suffix=""):
    return f"{prefix}{v:,}{suffix}" if isinstance(v, (int, float)) else str(v)

def show_chart(card_class, title, badge_class, badge_label, desc, img_path, info_msg=None):
    st.markdown(f"""
    <div class="{card_class}">
      <div class="chart-title">{title}</div>
      <span class="chart-badge {badge_class}">{badge_label}</span>
      <div class="chart-desc">{desc}</div>
    """, unsafe_allow_html=True)
    img = load_img(img_path)
    if img:
        st.image(img, use_column_width=True)
    else:
        st.info(info_msg or f"📂 Chart not found: {img_path} — run the notebook to generate charts.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Load datasets ─────────────────────────────────────────────────────────────
cyc_df  = try_load_csv("cyclone.csv")
hw_df   = try_load_csv("heatcold.csv")
aqi_df  = try_load_csv("10_air_quality_index_2015_2023.csv")
rain_df = try_load_csv("02_monthly_rainfall_district_1901_2023.csv")

# Cyclone KPIs
if cyc_df is not None:
    total_cyclones = len(cyc_df)
    total_deaths_c = int(cyc_df['deaths'].sum()) if 'deaths' in cyc_df.columns else "N/A"
    max_wind       = cyc_df['max_wind_kmh'].max() if 'max_wind_kmh' in cyc_df.columns else "N/A"
    total_damage   = int(cyc_df['damage_crore_inr'].sum()) if 'damage_crore_inr' in cyc_df.columns else "N/A"
    landfall_pct   = round(cyc_df['landfall'].sum() / len(cyc_df) * 100, 1) if 'landfall' in cyc_df.columns else "N/A"
    super_cyclones = int((cyc_df['category'] == 'Super Cyclonic Storm').sum()) if 'category' in cyc_df.columns else "N/A"
else:
    total_cyclones = total_deaths_c = max_wind = total_damage = landfall_pct = super_cyclones = "N/A"

# Heatwave KPIs
if hw_df is not None:
    hw_only        = hw_df[hw_df['event_type'] == 'Heatwave'] if 'event_type' in hw_df.columns else hw_df
    cw_only        = hw_df[hw_df['event_type'] == 'Coldwave'] if 'event_type' in hw_df.columns else hw_df
    total_events   = len(hw_df)
    n_heatwaves    = len(hw_only)
    n_coldwaves    = len(cw_only)
    total_deaths_h = int(hw_df['estimated_deaths'].sum()) if 'estimated_deaths' in hw_df.columns else "N/A"
    max_temp       = hw_df['peak_temp_c'].max() if 'peak_temp_c' in hw_df.columns else "N/A"
    states_affected= hw_df['state'].nunique() if 'state' in hw_df.columns else "N/A"
else:
    total_events = n_heatwaves = n_coldwaves = total_deaths_h = max_temp = states_affected = "N/A"

# AQI KPIs
if aqi_df is not None:
    aqi_total_records = f"{len(aqi_df):,}"
    aqi_mean          = round(aqi_df['aqi'].mean(), 1) if 'aqi' in aqi_df.columns else "N/A"
    aqi_max           = int(aqi_df['aqi'].max()) if 'aqi' in aqi_df.columns else "N/A"
    aqi_stations      = aqi_df['station'].nunique() if 'station' in aqi_df.columns else "N/A"
    aqi_severe_pct    = round(
        aqi_df['category'].isin(['Poor','Very Poor','Severe']).sum() / len(aqi_df) * 100, 1
    ) if 'category' in aqi_df.columns else "N/A"
    aqi_dominant      = aqi_df['dominant_pollutant'].value_counts().idxmax() if 'dominant_pollutant' in aqi_df.columns else "N/A"
else:
    aqi_total_records = aqi_mean = aqi_max = aqi_stations = aqi_severe_pct = aqi_dominant = "N/A"

# Rainfall KPIs
if rain_df is not None:
    rain_total_records = f"{len(rain_df):,}"
    rain_mean          = round(rain_df['rainfall_mm'].mean(), 1) if 'rainfall_mm' in rain_df.columns else "N/A"
    rain_max           = round(rain_df['rainfall_mm'].max(), 0) if 'rainfall_mm' in rain_df.columns else "N/A"
    rain_states        = rain_df['state'].nunique() if 'state' in rain_df.columns else "N/A"
    rain_districts     = rain_df['district'].nunique() if 'district' in rain_df.columns else "N/A"
    rain_excess_pct    = round(
        (rain_df['category'] == 'Excess').sum() / len(rain_df) * 100, 1
    ) if 'category' in rain_df.columns else "N/A"
    rain_deficit_pct   = round(
        rain_df['category'].isin(['Deficient','Scanty']).sum() / len(rain_df) * 100, 1
    ) if 'category' in rain_df.columns else "N/A"
else:
    rain_total_records = rain_mean = rain_max = rain_states = rain_districts = rain_excess_pct = rain_deficit_pct = "N/A"

# ── Section lists ─────────────────────────────────────────────────────────────
CYCLONE_SECTIONS = [
    "📋 Overview & KPIs",
    "📅 Temporal Patterns",
    "💨 Intensity Analysis",
    "🌊 Impact & Damage",
    "🗺️ Geographic Patterns",
    "🔗 Correlations",
]
HEAT_SECTIONS = [
    "📋 Event Overview & KPIs",
    "📅 Annual & Seasonal Trends",
    "🌡️ Temperature & Severity",
    "💀 Deaths & Mortality Impact",
    "🗺️ State-wise Risk Patterns",
    "🔗 Correlations & Pairplot",
]
AQI_SECTIONS = [
    "📋 Overview & KPIs",
    "📅 Annual & Seasonal Trends",
    "💨 Pollutant & Category Analysis",
    "🏭 Station & Geographic Patterns",
    "🔗 Correlations & Distributions",
]
RAINFALL_SECTIONS = [
    "📋 Overview & KPIs",
    "📅 Annual & Seasonal Trends",
    "💧 Category & Departure Analysis",
    "🗺️ State & Zone Patterns",
    "🔗 Correlations & Distributions",
]

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌪️ India Weather EDA")
    st.markdown("---")

    dashboard = st.radio(
        "🗂️ Select Dashboard",
        ["🌀 Cyclone Dashboard", "🌡️ Heatwave & Coldwave Dashboard", "🌫️ Air Quality Index Dashboard", "🌧️ Rainfall Dashboard"],
    )

    st.markdown("---")

    db_key = "cyc" if "Cyclone" in dashboard else ("hw" if "Heatwave" in dashboard else ("aqi" if "Air Quality" in dashboard else "rain"))
    if st.session_state.get("prev_db_key", db_key) != db_key:
        st.session_state["section_idx"] = 0
    st.session_state["prev_db_key"] = db_key

    if dashboard == "🌀 Cyclone Dashboard":
        st.markdown(
            "**Dataset:** Indian Ocean Cyclones  \n"
            "**Period:** 1990 – 2023  \n"
            "**Records:** 103 cyclones  \n"
            "**Features:** 17 variables"
        )
        st.markdown("---")
        section = st.radio(
            "📊 Jump to Section",
            CYCLONE_SECTIONS,
            index=st.session_state.get("section_idx", 0),
            key="section_cyclone",
        )
        st.session_state["section_idx"] = CYCLONE_SECTIONS.index(section)
        st.markdown("---")
        st.markdown("**Charts:** 15 unique visualisations  \n**Types:** Bar, Line, Polar, Violin, Scatter, Heatmap, Donut, KDE, Hexbin, Boxplot, Pairplot")

    elif dashboard == "🌡️ Heatwave & Coldwave Dashboard":
        st.markdown(
            "**Dataset:** India Extreme Temp Events  \n"
            "**Period:** 1980 – 2023  \n"
            "**Records:** 613 events  \n"
            "**Features:** 13 variables"
        )
        st.markdown("---")
        section = st.radio(
            "📊 Jump to Section",
            HEAT_SECTIONS,
            index=st.session_state.get("section_idx", 0),
            key="section_heat",
        )
        st.session_state["section_idx"] = HEAT_SECTIONS.index(section)
        st.markdown("---")
        st.markdown("**Charts:** 15 unique visualisations  \n**Types:** Donut, Line+Area, Polar, Violin+Strip, Bubble Scatter, Heatmap, Horizontal Bar, Grouped Bar, Hexbin, Stacked Bar, KDE+Histogram, Grouped Boxplot, Cross-tab, Pairplot")

    elif dashboard == "🌫️ Air Quality Index Dashboard":
        st.markdown(
            "**Dataset:** India Air Quality Index  \n"
            "**Period:** 2015 – 2023  \n"
            "**Records:** 32,870 readings  \n"
            "**Features:** 15 variables"
        )
        st.markdown("---")
        section = st.radio(
            "📊 Jump to Section",
            AQI_SECTIONS,
            index=st.session_state.get("section_idx", 0),
            key="section_aqi",
        )
        st.session_state["section_idx"] = AQI_SECTIONS.index(section)
        st.markdown("---")
        st.markdown("**Charts:** 12 unique visualisations  \n**Types:** Donut, Line+Area, Polar, Violin+Strip, Bubble Scatter, Heatmap, Horizontal Bar, Stacked Bar, Cross-tab, Grouped Boxplot, KDE+Histogram, Correlation Matrix")

    else:  # Rainfall
        st.markdown(
            "**Dataset:** India Monthly Rainfall  \n"
            "**Period:** 1901 – 2023  \n"
            "**Records:** 44,280 readings  \n"
            "**Features:** 12 variables"
        )
        st.markdown("---")
        section = st.radio(
            "📊 Jump to Section",
            RAINFALL_SECTIONS,
            index=st.session_state.get("section_idx", 0),
            key="section_rainfall",
        )
        st.session_state["section_idx"] = RAINFALL_SECTIONS.index(section)
        st.markdown("---")
        st.markdown("**Charts:** 15 unique visualisations  \n**Types:** Donut, Line+Area, Polar, Violin+Strip, Bubble Scatter, Heatmap, Horizontal Bar, Stacked Bar, Cross-tab, Grouped Boxplot, KDE+Histogram, Grouped Bar, Hexbin, Correlation Matrix, Pairplot")


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLONE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if dashboard == "🌀 Cyclone Dashboard":

    st.markdown("""
    <div class="hero hero-cyclone">
      <h1>🌀 Indian Ocean Cyclone EDA</h1>
      <p>Exploratory Data Analysis — Extreme Pattern Discovery across 103 cyclone events (1990–2023)</p>
      <span class="tag tag-cyclone">1990–2023</span>
      <span class="tag tag-cyclone">Bay of Bengal</span>
      <span class="tag tag-cyclone">Arabian Sea</span>
      <span class="tag tag-cyclone">15 Charts</span>
      <span class="tag tag-cyclone">Matplotlib · Seaborn</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(total_cyclones)}</div><div class="kpi-lbl">Total Cyclones</div></div>
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(total_deaths_c)}</div><div class="kpi-lbl">Total Deaths</div></div>
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(max_wind)}</div><div class="kpi-lbl">Max Wind (km/h)</div></div>
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(total_damage, '₹', ' Cr')}</div><div class="kpi-lbl">Total Damage</div></div>
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(landfall_pct, suffix='%')}</div><div class="kpi-lbl">Landfall Rate</div></div>
      <div class="kpi-card kpi-card-cyclone"><div class="kpi-val-cyclone">{fmt(super_cyclones)}</div><div class="kpi-lbl">Super Cyclones</div></div>
    </div>
    """, unsafe_allow_html=True)

    if section == "📋 Overview & KPIs":
        st.markdown('<div class="section-header-cyclone">📋 Category Distribution</div>', unsafe_allow_html=True)
        show_chart("chart-card","Cyclone Category Distribution","badge-dist","Count Plot",
            "Shows how cyclones are distributed across intensity categories from Depression to Super Cyclonic Storm. <b>Extremely Severe</b> storms dominate, revealing a worrying skew toward high-intensity events — a critical signal for disaster preparedness and policy planning.",
            "CHARTS/01_category_distribution.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Key Insight:</strong> "Extremely Severe Cyclonic Storm" is the most frequent category (19 events),
            followed closely by regular Cyclonic Storms (18). Super Cyclonic Storms account for 15 events — more than
            Severe Cyclonic Storms — indicating increasing upper-end intensity in recent decades.
        </div>""", unsafe_allow_html=True)

    elif section == "📅 Temporal Patterns":
        st.markdown('<div class="section-header-cyclone">📅 Temporal Patterns</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            show_chart("chart-card","Annual Cyclone Frequency (1990–2023)","badge-trend","Line + Area Chart",
                "Tracks how cyclone activity has evolved year-on-year. The shaded area highlights cumulative intensity of activity while peak years are annotated directly on the chart for instant spotting of anomalous or record-breaking seasons.",
                "CHARTS/02_yearly_frequency.png")
        with col2:
            show_chart("chart-card","Monthly Seasonality (Polar)","badge-trend","Polar Bar Chart",
                "A polar chart maps cyclone frequency to the 12-month calendar wheel — immediately revealing the bimodal seasonality: pre-monsoon (May) and post-monsoon (Oct–Nov) are the dominant windows for cyclogenesis in the Indian Ocean.",
                "CHARTS/03_monthly_polar.png")
        show_chart("chart-card","Year × Month Activity Heatmap","badge-corr","Heatmap",
            "A 2D grid where every cell shows how many cyclones occurred in a given year and month. Hot colours (red/orange) expose multi-cyclone months — years like 2007 and 2015 stand out as unusually active, while certain months are almost always quiet.",
            "CHARTS/06_heatmap_year_month.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Temporal Insight:</strong> October & November account for nearly <strong>40%</strong> of all cyclone events.
            The post-monsoon season is consistently the most dangerous window. Year-on-year, the 2010s decade saw
            the most clustered high-activity years, suggesting potential climate-driven intensification.
        </div>""", unsafe_allow_html=True)

    elif section == "💨 Intensity Analysis":
        st.markdown('<div class="section-header-cyclone">💨 Intensity Analysis</div>', unsafe_allow_html=True)
        show_chart("chart-card","Wind Speed Distribution by Category (Violin + Strip)","badge-dist","Violin Plot",
            "Violin plots show the full probability density of wind speeds within each category, while white strip dots reveal individual cyclone data points. The thicker the violin at a value, the more cyclones cluster there — exposing overlaps and outliers between adjacent intensity classes.",
            "CHARTS/04_wind_violin.png")
        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card","Wind Speed vs Pressure (Regression)","badge-corr","Scatter + Regression",
                "The classic inverse relationship between central pressure and wind speed. Lower pressure = higher winds. Annotated outliers highlight the most intense recorded storms with unprecedented low-pressure readings.",
                "CHARTS/10_wind_pressure_scatter.png")
        with col2:
            show_chart("chart-card","Duration vs Track Length (Hexbin)","badge-dist","Hexbin Density",
                "Hexbin bins show where the most cyclones cluster in duration–track space. Long-lived storms that travel far are rare but extremely destructive — the sparse hot cells at the extreme corners are the most dangerous events.",
                "CHARTS/13_duration_track_hexbin.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Intensity Insight:</strong> Wind speed and minimum pressure have a near-perfect
            <strong>negative correlation (≈ −0.97)</strong>. Super Cyclonic Storms cluster around pressures below 920 hPa
            and winds exceeding 220 km/h — well beyond the threshold where standard infrastructure fails.
        </div>""", unsafe_allow_html=True)

    elif section == "🌊 Impact & Damage":
        st.markdown('<div class="section-header-cyclone">🌊 Impact & Damage Analysis</div>', unsafe_allow_html=True)
        show_chart("chart-card","Deaths vs Economic Damage — Bubble Chart (Log Scale)","badge-impact","Bubble Scatter",
            "Plots every cyclone at the intersection of human cost (deaths) and economic damage, with bubble size encoding wind speed and colour showing category. Log scale prevents a handful of mega-disasters from collapsing all other data — enabling pattern detection across the full severity spectrum.",
            "CHARTS/05_deaths_damage_scatter.png")
        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card","Top 10 Deadliest Cyclones","badge-impact","Horizontal Bar",
                "Ranks the 10 most lethal cyclones with death toll and year. Colour gradient (light → dark red) visually reinforces magnitude. The catastrophic gap between the top event and the rest is immediately visible.",
                "CHARTS/08_top10_deadliest.png")
        with col2:
            show_chart("chart-card","Storm Surge Distribution (KDE + Histogram)","badge-dist","KDE Histogram",
                "Overlays a histogram with a kernel density curve to reveal the surge distribution shape. The 95th percentile marker highlights the extreme tail — surges above this level cause catastrophic coastal inundation and are the primary driver of mass casualties.",
                "CHARTS/12_surge_kde.png")
        show_chart("chart-card","Decade-wise Economic Damage (Boxplot)","badge-trend","Box + Strip Plot",
            "Compares damage distributions across four decades. The box shows the interquartile range, the horizontal line is the median, and diamond-shaped outliers are extreme economic disaster events. The rising medians decade over decade tell a stark story about escalating costs.",
            "CHARTS/14_decade_damage_box.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Impact Insight:</strong> Economic damage in the 2010s is <strong>3× the median</strong> of the 1990s,
            even inflation-adjusted. Storm surge above 4m is the <strong>single strongest predictor</strong> of both deaths
            and damage — targeted coastal early-warning systems could dramatically cut casualties.
        </div>""", unsafe_allow_html=True)

    elif section == "🗺️ Geographic Patterns":
        st.markdown('<div class="section-header-cyclone">🗺️ Geographic Patterns</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card","Landfall Distribution by State (Donut)","badge-geo","Donut Chart",
                "A donut chart shows each state's share of total landfall events. The hollow centre displays the total count. States with larger slices bear a disproportionate risk burden and require more robust cyclone infrastructure investment.",
                "CHARTS/11_landfall_donut.png")
        with col2:
            show_chart("chart-card","Category Split by Basin (Stacked Bar)","badge-geo","Stacked Bar",
                "Compares how cyclone intensity categories are distributed between the Bay of Bengal and the Arabian Sea. The stacking reveals whether one basin disproportionately produces extreme storms — a key insight for regional hazard risk modelling.",
                "CHARTS/07_basin_category_stacked.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Geographic Insight:</strong> Karnataka, West Bengal, Andhra Pradesh, Gujarat and Maharashtra
            each receive <strong>~21% of landfalls</strong> — surprisingly balanced. However, the Bay of Bengal produces
            significantly more <strong>Super Cyclonic Storms</strong> than the Arabian Sea, making its coastlines
            higher-risk for catastrophic events.
        </div>""", unsafe_allow_html=True)

    elif section == "🔗 Correlations":
        st.markdown('<div class="section-header-cyclone">🔗 Correlation & Multivariate Analysis</div>', unsafe_allow_html=True)
        show_chart("chart-card","Correlation Matrix — All Numerical Features","badge-corr","Heatmap",
            "A triangular correlation matrix covering all 10 numerical variables. Red cells show strong positive correlations, blue cells show negative ones. This is the key chart for understanding which variables move together — guiding feature selection for predictive modelling.",
            "CHARTS/09_correlation_heatmap.png")
        show_chart("chart-card","Pairplot — Extreme Cyclone Indicators (Basin Hue)","badge-corr","Pairplot",
            "Every variable is plotted against every other variable in a grid. Diagonal cells show KDE distributions for each basin. This single chart encodes dozens of bivariate relationships simultaneously — pink = Bay of Bengal, green = Arabian Sea — revealing basin-specific clustering.",
            "CHARTS/15_pairplot.png")
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Correlation Insight:</strong> <strong>Affected districts</strong> and <strong>evacuated population</strong>
            show the strongest positive correlation (0.89), confirming evacuation scales proportionally with exposure.
            Surprisingly, <strong>IMD warning lead time</strong> has only a weak negative correlation with deaths —
            suggesting warning effectiveness depends more on communication quality than lead time alone.
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HEATWAVE & COLDWAVE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif dashboard == "🌡️ Heatwave & Coldwave Dashboard":

    st.markdown("""
    <div class="hero hero-heatwave">
      <h1>🌡️ Heatwave & Coldwave EDA</h1>
      <p>Exploratory Data Analysis — Extreme Temperature Pattern Discovery across 613 events (1980–2023)</p>
      <span class="tag tag-heat">1980–2023</span>
      <span class="tag tag-heat">Heatwaves</span>
      <span class="tag tag-cold">Coldwaves</span>
      <span class="tag tag-heat">15 Charts</span>
      <span class="tag tag-heat">Matplotlib · Seaborn</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(total_events)}</div><div class="kpi-lbl">Total Events</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(n_heatwaves)}</div><div class="kpi-lbl">Heatwaves</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-cold">{fmt(n_coldwaves)}</div><div class="kpi-lbl">Coldwaves</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(total_deaths_h)}</div><div class="kpi-lbl">Total Deaths</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(max_temp)}°C</div><div class="kpi-lbl">Peak Temp Recorded</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(states_affected)}</div><div class="kpi-lbl">States Affected</div></div>
    </div>
    """, unsafe_allow_html=True)

    if section == "📋 Event Overview & KPIs":
        st.markdown('<div class="section-header-heat">📋 Heatwave vs Coldwave — Event Split</div>', unsafe_allow_html=True)
        show_chart("chart-card-heat","Chart 1 · Heatwave vs Coldwave — Donut Chart","badge-heat","Donut Chart",
            "Overall proportion of heatwaves (pink) vs coldwaves (blue) across the full 44-year record. The hollow centre displays total event count — an instant baseline before deeper analysis. The ratio is shifting: heatwave frequency has risen steeply since 2000, a direct fingerprint of long-term warming.",
            "CHARTS/01_event_type_donut.png","📂 Chart not found: CHARTS/01_event_type_donut.png — run heatwave_eda notebook first.")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Key Insight:</strong> Heatwaves make up the majority of events yet both types carry
            severe mortality risk across different seasons. Heatwave counts are accelerating post-2000 while
            coldwaves have plateaued — a direct signal of India's warming trajectory over 44 years.
        </div>""", unsafe_allow_html=True)

    elif section == "📅 Annual & Seasonal Trends":
        st.markdown('<div class="section-header-heat">📅 Annual & Seasonal Trends (Charts 2, 3, 6)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            show_chart("chart-card-heat","Chart 2 · Annual Frequency — Dual Line + Area (1980–2023)","badge-trend","Line + Area Chart",
                "Heatwave (pink) and coldwave (blue) event counts tracked year-on-year with shaded fills. Diverging trends between the two series are a direct climate-change signal — heatwaves climbing while coldwaves remain flat or decline over four decades.",
                "CHARTS/02_yearly_frequency.png")
        with col2:
            show_chart("chart-card-heat","Chart 3 · Monthly Seasonality — Dual Polar Bar","badge-heat","Polar Bar Chart",
                "12 months mapped onto a polar wheel with side-by-side bars per event type. The near-opposite positioning of pink (Mar–Jun) vs blue (Dec–Feb) encodes India's entire temperature seasonality in a single striking chart.",
                "CHARTS/03_monthly_polar.png")
        show_chart("chart-card-heat","Chart 6 · Year × Month Event Frequency Heatmap","badge-corr","2D Heatmap",
            "Every cell shows the number of extreme temperature events in a given year–month pair. The bright March–June band for heatwaves and December–February band for coldwaves are clearly visible year after year — certain years like 2015 and 2022 show exceptionally dense clusters.",
            "CHARTS/06_heatmap_year_month.png")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Temporal Insight:</strong> Heatwaves peak in <strong>May–June</strong>; coldwaves dominate
            <strong>December–January</strong>. The 2010s saw the most concentrated heatwave clusters —
            multiple years recording 5+ events vs. fewer than 2 per year in the 1980s.
        </div>""", unsafe_allow_html=True)

    elif section == "🌡️ Temperature & Severity":
        st.markdown('<div class="section-header-heat">🌡️ Severity & Intensity Analysis (Charts 4, 9, 10, 11)</div>', unsafe_allow_html=True)
        show_chart("chart-card-heat","Chart 4 · Peak Temperature by Severity — Side-by-side Violin + Strip","badge-dist","Violin + Strip Plot",
            "Violin width = event density at each temperature; white dots = individual events. Heatwave Severe class easily exceeds 45°C while Coldwave Severe drops below 5°C — the dangerous overlap between Moderate and Severe heatwaves is exposed clearly.",
            "CHARTS/04_temp_violin.png")
        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card-heat","Chart 9 · Severity vs IMD Alert Level — Cross-tab Heatmap","badge-corr","Cross-tab Heatmap",
                "Maps IMD alert levels (Yellow/Orange/Red) against actual severity class. Misaligned cells — Severe events with only Yellow alerts, or Red alerts for Mild events — reveal real calibration gaps in India's national weather warning system.",
                "CHARTS/09_severity_alert_heatmap.png")
        with col2:
            show_chart("chart-card-heat","Chart 10 · Temperature Anomaly by Severity — Grouped Boxplot","badge-heat","Grouped Boxplot",
                "Grouped boxes show how far temperatures deviated from historical norms per severity class. The dashed zero line divides positive (heat) from negative (cold) anomalies — Severe heatwaves sit at +6°C to +10°C above the norm.",
                "CHARTS/10_anomaly_severity_box.png")
        show_chart("chart-card-heat","Chart 11 · Event Duration Distribution — Overlapping KDE + Histogram","badge-dist","KDE + Histogram",
            "Overlapping histograms and KDE curves for both event types with annotated mean lines. A longer right tail means more chronic multi-week events — these accumulate far greater physiological and economic damage than short-duration spikes of equal peak intensity.",
            "CHARTS/11_duration_kde.png")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Severity Insight:</strong> Severe heatwaves record anomalies of <strong>+6°C to +10°C</strong>
            above historical norms. IMD Red alerts are under-issued for Moderate events — a calibration gap
            that directly raises mortality risk. Heatwaves also run significantly longer on average than coldwaves.
        </div>""", unsafe_allow_html=True)

    elif section == "💀 Deaths & Mortality Impact":
        st.markdown('<div class="section-header-heat">💀 Deaths & Mortality Impact (Charts 5, 7, 12, 13)</div>', unsafe_allow_html=True)
        show_chart("chart-card-heat","Chart 5 · Deaths vs Temperature Anomaly — Bubble Scatter","badge-impact","Bubble Scatter",
            "Each bubble = one event, positioned at the intersection of temperature deviation and death toll. Bubble size encodes event duration in days. Annotated outliers are the 4 most lethal events in 44 years. Right half (positive anomaly) = heatwaves; left half = coldwaves.",
            "CHARTS/05_deaths_anomaly_scatter.png")
        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card-heat","Chart 7 · Top 10 Deadliest Events (1980–2023)","badge-impact","Horizontal Bar Chart",
                "Pink = heatwave, blue = coldwave. Annotated with death count, year, and state. Reveals which type has historically dominated mortality and which single events were catastrophic outliers far above the rest of the distribution.",
                "CHARTS/07_top10_deadliest.png")
        with col2:
            show_chart("chart-card-heat","Chart 12 · Decade-wise Total Deaths — Grouped Bar","badge-trend","Grouped Bar Chart",
                "Side-by-side decade bars compare total mortality from heatwaves vs coldwaves. Totals float above each bar. A widening gap across decades reveals the long-term shift in which extreme temperature type poses the greater mortality risk to India.",
                "CHARTS/12_decade_deaths_bar.png")
        show_chart("chart-card-heat","Chart 13 · Districts Affected vs Deaths — Hexbin Density","badge-dist","Hexbin Density Plot",
            "Hexagonal bins show where the majority of events cluster in districts-vs-deaths space. The dense core near low values is the 'typical' event; rare bright cells in the upper-right are catastrophic multi-district events that overwhelm state emergency response systems.",
            "CHARTS/13_districts_deaths_hexbin.png")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Mortality Insight:</strong> Heatwave deaths in the 2010s were <strong>2.4× higher</strong> than the 1990s.
            Events spanning more than 20 districts are rare but account for a disproportionate share of total deaths —
            geographic spread amplifies mortality by exhausting healthcare and emergency response capacity simultaneously.
        </div>""", unsafe_allow_html=True)

    elif section == "🗺️ State-wise Risk Patterns":
        st.markdown('<div class="section-header-heat">🗺️ State-wise Risk Patterns (Chart 8)</div>', unsafe_allow_html=True)
        show_chart("chart-card-heat","Chart 8 · Top 15 States — Heatwave & Coldwave Event Count (Stacked Bar)","badge-geo","Stacked Horizontal Bar",
            "Heatwave (pink) and coldwave (blue) event counts stacked per state — ranked by total exposure. A state with balanced colours faces year-round dual-season risk; dominance of one colour reveals seasonal skew. Directly informs state-level NDRF deployment and disaster preparedness planning.",
            "CHARTS/08_state_events_stacked.png")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Geographic Insight:</strong> <strong>Rajasthan, Uttar Pradesh, and Odisha</strong> top the heatwave count,
            while <strong>Bihar and West Bengal</strong> face the highest coldwave exposure. States across the Indo-Gangetic Plain
            face dual-season risk from both types simultaneously — requiring year-round extreme weather preparedness infrastructure.
        </div>""", unsafe_allow_html=True)

    elif section == "🔗 Correlations & Pairplot":
        st.markdown('<div class="section-header-heat">🔗 Correlations & Pairplot (Charts 14, 15)</div>', unsafe_allow_html=True)
        show_chart("chart-card-heat","Chart 14 · Correlation Matrix — All Numerical Features","badge-corr","Lower-Triangular Heatmap",
            "Lower-triangular correlation heatmap across 6 key numeric variables: duration, peak_temp, temp_anomaly, threshold_exceeded, estimated_deaths, districts_affected. Red = strong positive, blue = strong negative. The near-perfect correlation between temp_anomaly and threshold_exceeded confirms feature redundancy.",
            "CHARTS/14_correlation_heatmap.png")
        show_chart("chart-card-heat","Chart 15 · Pairplot — Key Extreme-Temperature Indicators (Hue = Event Type)","badge-corr","5×5 Pairplot Grid",
            "Every key variable plotted against every other in a 5×5 grid — pink = heatwave, blue = coldwave. Diagonal KDE curves show whether the two event types form distinct distributions. Bivariate scatter panels expose nonlinear relationships that single correlation values miss entirely.",
            "CHARTS/15_pairplot.png")
        st.markdown("""<div class="insight-heat">
            💡 <strong>Correlation Insight:</strong> <strong>Duration × districts_affected</strong> show the strongest
            positive correlation (≈ 0.71) — longer events spread further geographically. Surprisingly, peak temperature alone
            is a <strong>weak predictor of deaths</strong>; it's the interaction of anomaly, duration, and affected population
            density that drives mortality — pointing to the need for multi-variable composite risk indices.
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# AIR QUALITY INDEX DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif dashboard == "🌫️ Air Quality Index Dashboard":

    st.markdown("""
    <div class="hero hero-aqi">
      <h1>🌫️ Air Quality Index EDA</h1>
      <p>Exploratory Data Analysis — Pollutant Pattern Discovery across 32,870 readings from 9 states (2015–2023)</p>
      <span class="tag tag-aqi">2015–2023</span>
      <span class="tag tag-aqi">4 Zones</span>
      <span class="tag tag-aqi-warn">PM2.5 · PM10 · NO2</span>
      <span class="tag tag-aqi-bad">12 Charts</span>
      <span class="tag tag-aqi">Matplotlib · Seaborn</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi">{aqi_total_records}</div><div class="kpi-lbl">Total Records</div></div>
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi">{fmt(aqi_stations)}</div><div class="kpi-lbl">Monitoring Stations</div></div>
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi-warn">{fmt(aqi_mean)}</div><div class="kpi-lbl">Mean AQI</div></div>
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi-bad">{fmt(aqi_max)}</div><div class="kpi-lbl">Peak AQI Recorded</div></div>
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi-bad">{fmt(aqi_severe_pct, suffix='%')}</div><div class="kpi-lbl">Poor+ Days</div></div>
      <div class="kpi-card kpi-card-aqi"><div class="kpi-val-aqi-warn">{aqi_dominant}</div><div class="kpi-lbl">Top Pollutant</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1: OVERVIEW & KPIs ────────────────────────────────────────────
    if section == "📋 Overview & KPIs":
        st.markdown('<div class="section-header-aqi">📋 AQI Category Distribution</div>', unsafe_allow_html=True)
        show_chart("chart-card-aqi",
            "Chart 1 · AQI Category Distribution — Donut Chart",
            "badge-aqi", "Donut Chart",
            "Overall proportion of all six AQI categories (Good → Severe) across the full 9-year record. The hollow centre displays total record count — an instant baseline before deeper analysis. <b>Satisfactory and Moderate together dominate</b>, signalling persistent mid-level pollution pressure across India's monitoring network.",
            "CHARTS/01_category_donut.png",
            "📂 Chart not found: CHARTS/01_category_donut.png — run aqi_eda notebook first.")
        st.markdown("""<div class="insight-aqi">
            💡 <strong>Key Insight:</strong> Satisfactory (39.3%) and Moderate (35.1%) together account for nearly
            <strong>75% of all readings</strong>. Severe days represent only 0.7% of records but are heavily concentrated
            in the winter months across North Indian stations — where temperature inversions trap particulate matter
            close to the surface and AQI can spike to 400+.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 2: ANNUAL & SEASONAL TRENDS ──────────────────────────────────
    elif section == "📅 Annual & Seasonal Trends":
        st.markdown('<div class="section-header-aqi">📅 Annual & Seasonal Trends (Charts 2, 3, 6)</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            show_chart("chart-card-aqi",
                "Chart 2 · Annual Average AQI Trend by Zone (2015–2023)",
                "badge-trend", "Line + Area Chart",
                "Mean AQI tracked year-on-year for each geographic zone with shaded fills encoding cumulative air-quality pressure. The <b>2020 dip is unmistakable</b> across all zones — a direct COVID-19 lockdown signal. The subsequent rebound trajectory tells the story of India's post-lockdown pollution recovery.",
                "CHARTS/02_annual_aqi_trend.png")
        with col2:
            show_chart("chart-card-aqi",
                "Chart 3 · Monthly Seasonality — Polar Bar by Zone",
                "badge-aqi", "Polar Bar Chart",
                "12 months mapped onto a polar wheel with bars per zone. The sharp <b>winter spike (Oct–Feb)</b> captures India's biomass burning and temperature-inversion season; the <b>monsoon dip (Jun–Sep)</b> confirms wet scavenging of particulates as a natural seasonal cleanser.",
                "CHARTS/03_monthly_polar.png")

        show_chart("chart-card-aqi",
            "Chart 6 · Year × Month Mean AQI Heatmap",
            "badge-corr", "2D Heatmap",
            "Every cell = mean AQI for that year–month pair. The bright <b>winter band (Nov–Jan)</b> running across all nine years is unmistakable. The noticeably cooler 2020 row validates the lockdown effect. Aug–Sep cells are consistently the lightest — the cleaner months driven by monsoon rainfall.",
            "CHARTS/06_year_month_heatmap.png")

        st.markdown("""<div class="insight-aqi">
            💡 <strong>Temporal Insight:</strong> January is consistently the worst month, with mean AQI often
            exceeding 160 in North India. August is the cleanest at roughly half that level.
            The <strong>2020 lockdown cut mean AQI by ~25%</strong> across all zones — providing a rare natural
            experiment confirming that transport and industrial emissions are the primary controllable levers.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 3: POLLUTANT & CATEGORY ANALYSIS ─────────────────────────────
    elif section == "💨 Pollutant & Category Analysis":
        st.markdown('<div class="section-header-aqi">💨 Pollutant & Category Analysis (Charts 4, 5, 9)</div>', unsafe_allow_html=True)

        show_chart("chart-card-aqi",
            "Chart 4 · AQI Distribution by Category & Zone — Side-by-Side Violin + Strip",
            "badge-dist", "Violin + Strip Plot",
            "Violin width = record density at each AQI level; white strip dots = individual readings. The left panel confirms category thresholds are internally consistent. The right panel reveals how <b>North and East zones consistently skew higher</b> than South, reflecting the Indo-Gangetic plain's geographic pollution trap.",
            "CHARTS/04_aqi_violin.png")

        show_chart("chart-card-aqi",
            "Chart 5 · PM2.5 vs AQI — Bubble Scatter (Bubble Size = PM10)",
            "badge-poll", "Bubble Scatter",
            "Each point sits at the intersection of PM2.5 concentration and AQI. Bubble size encodes PM10 load; colour encodes zone. Stations annotated in red are the <b>top-4 all-time worst readings</b>. The strong linear cluster confirms PM2.5 as the dominant AQI driver — a critical finding for pollution control targeting.",
            "CHARTS/05_pm25_aqi_bubble.png")

        show_chart("chart-card-aqi",
            "Chart 9 · AQI Category vs Dominant Pollutant — Cross-tabulation Heatmap",
            "badge-corr", "Cross-tab Heatmap",
            "Maps dominant pollutant type against observed AQI category. PM2.5 dominating the <b>Severe row</b> confirms fine particulate matter as the primary culprit at the worst end of the scale. NO2 dominance in Good/Satisfactory rows reveals traffic-origin baseline pollution that persists even on cleaner days.",
            "CHARTS/09_category_pollutant_heatmap.png")

        st.markdown("""<div class="insight-aqi">
            💡 <strong>Pollutant Insight:</strong> PM2.5 is the dominant pollutant in <strong>55.6% of all readings</strong>
            and accounts for virtually all Severe-category days. NO2 leads on lower-AQI days, pointing to vehicular
            traffic as a persistent baseline source. PM10 dominates in dry seasons when dust resuspension amplifies
            coarse particle loads — especially in western and northern states.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 4: STATION & GEOGRAPHIC PATTERNS ─────────────────────────────
    elif section == "🏭 Station & Geographic Patterns":
        st.markdown('<div class="section-header-aqi">🏭 Station & Geographic Patterns (Charts 7, 8)</div>', unsafe_allow_html=True)

        show_chart("chart-card-aqi",
            "Chart 7 · Top 15 Most Polluted Stations — Mean AQI (2015–2023)",
            "badge-poll", "Horizontal Bar Chart",
            "Colour-coded by zone, annotated with mean AQI and zone label. Reveals which specific monitoring stations have borne the <b>highest chronic pollution burden</b> over the 9-year period — directly informing targeted intervention priorities for regulators and urban planners.",
            "CHARTS/07_top15_stations.png")

        show_chart("chart-card-aqi",
            "Chart 8 · State-wise AQI Category Breakdown — Stacked Horizontal Bar",
            "badge-geo", "Stacked Horizontal Bar",
            "Stacks all six AQI category counts per state. A state dominated by green (Good/Satisfactory) faces low chronic risk; dominance of red/purple (Poor/Very Poor/Severe) flags a <b>public health priority</b>. Directly supports state-level pollution control and CPCB enforcement prioritisation.",
            "CHARTS/08_state_category_stacked.png")

        st.markdown("""<div class="insight-aqi">
            💡 <strong>Geographic Insight:</strong> <strong>North zone stations</strong> occupy the top positions for
            chronic pollution, with some stations averaging AQI above 200 — firmly in the Poor category year-round.
            Southern states show a far more favourable category mix, with Good and Satisfactory readings forming the
            majority. This north–south divide reflects both industrial density and seasonal meteorological differences
            that trap pollutants across the Indo-Gangetic plain.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 5: CORRELATIONS & DISTRIBUTIONS ───────────────────────────────
    elif section == "🔗 Correlations & Distributions":
        st.markdown('<div class="section-header-aqi">🔗 Correlations & Distributions (Charts 10, 11, 12)</div>', unsafe_allow_html=True)

        show_chart("chart-card-aqi",
            "Chart 10 · AQI Distribution by Year & Zone — Grouped Boxplot",
            "badge-corr", "Grouped Boxplot",
            "Grouped boxes compare zone-level AQI spread for each year. The <b>2020 box shift downward</b> across all zones marks the lockdown period. Widening IQR in recent years may indicate increasing AQI variability — more extreme both good and bad days — reflecting intensifying seasonal pollution cycles.",
            "CHARTS/10_aqi_year_zone_box.png")

        show_chart("chart-card-aqi",
            "Chart 11 · Pollutant Concentration Distribution — KDE + Histogram",
            "badge-dist", "KDE + Histogram",
            "Overlapping histograms and smooth KDE curves for PM2.5, PM10, and NO2 with annotated mean and median lines. The <b>longer right tail for PM2.5</b> indicates chronic high-load events that push AQI into Poor/Severe range and dominate public health impact far beyond what the median concentration would suggest.",
            "CHARTS/11_pollutant_kde.png")

        show_chart("chart-card-aqi",
            "Chart 12 · Pollutant Correlation Matrix — Lower Triangle Heatmap",
            "badge-corr", "Correlation Heatmap",
            "Pearson correlations between AQI and all six pollutants (lower triangle only). <b>Strong PM2.5–AQI and PM10–AQI correlations</b> confirm particulate dominance. The weak or negative O3 (ozone) correlation reflects its photochemical origin — rising with sunlight intensity precisely when other combustion pollutants may drop.",
            "CHARTS/12_pollutant_correlation.png")

        st.markdown("""<div class="insight-aqi">
            💡 <strong>Correlation Insight:</strong> PM2.5 shows the <strong>strongest positive correlation with AQI (≈ 0.93)</strong>,
            confirming it as the primary driver. CO follows closely, reflecting shared combustion sources.
            Ozone (O3) shows a weak negative correlation with PM2.5 — an anti-correlation that occurs because
            ozone formation peaks on sunny, low-particulate days. This means high-PM2.5 and high-O3 days
            rarely coincide, but both pose independent health risks requiring separate monitoring strategies.
        </div>""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# RAINFALL DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
else:

    st.markdown("""
    <div class="hero hero-rainfall">
      <h1>🌧️ Monthly Rainfall EDA</h1>
      <p>Exploratory Data Analysis — Extreme Pattern Discovery across 44,280 district-month records (1901–2023)</p>
      <span class="tag tag-rain">1901–2023</span>
      <span class="tag tag-rain">123 Years</span>
      <span class="tag tag-rain-ex">Excess · Normal</span>
      <span class="tag tag-rain-def">Deficient · Scanty</span>
      <span class="tag tag-rain">15 Charts</span>
      <span class="tag tag-rain">Matplotlib · Seaborn</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain">{rain_total_records}</div><div class="kpi-lbl">Total Records</div></div>
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain">{fmt(rain_states)}</div><div class="kpi-lbl">States</div></div>
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain">{fmt(rain_districts)}</div><div class="kpi-lbl">Districts</div></div>
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain-ex">{fmt(rain_mean)} mm</div><div class="kpi-lbl">Mean Monthly Rainfall</div></div>
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain-ex">{fmt(rain_excess_pct, suffix='%')}</div><div class="kpi-lbl">Excess Months</div></div>
      <div class="kpi-card kpi-card-rainfall"><div class="kpi-val-rain-def">{fmt(rain_deficit_pct, suffix='%')}</div><div class="kpi-lbl">Deficit Months</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1: OVERVIEW & KPIs ────────────────────────────────────────────
    if section == "📋 Overview & KPIs":
        st.markdown('<div class="section-header-rainfall">📋 Rainfall Category Distribution</div>', unsafe_allow_html=True)
        show_chart("chart-card-rainfall",
            "Chart 1 · Rainfall Category Split — Donut Chart",
            "badge-rain", "Donut Chart",
            "Overall proportion of Excess, Normal, Deficient, and Scanty months across the full 123-year record. The hollow centre displays total record count — an instant baseline before deeper analysis. <b>Normal months form the majority</b> but Deficient and Scanty together signal chronic water-stress years that drive India's recurring drought cycles.",
            "CHARTS/01_category_donut.png",
            "📂 Chart not found: CHARTS/01_category_donut.png — run rainfall_eda notebook first.")
        st.markdown("""<div class="insight-rainfall">
            💡 <strong>Key Insight:</strong> Normal months dominate at over 50% of all records, yet
            <strong>Deficient and Scanty months combined account for roughly 30%</strong> of observations —
            a persistent deficit signal embedded in India's century-long rainfall record. Excess months cluster
            heavily in the June–September monsoon window, confirming that annual water availability is largely
            determined in just 4 months of the year.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 2: ANNUAL & SEASONAL TRENDS ──────────────────────────────────
    elif section == "📅 Annual & Seasonal Trends":
        st.markdown('<div class="section-header-rainfall">📅 Annual & Seasonal Trends (Charts 2, 3, 6)</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            show_chart("chart-card-rainfall",
                "Chart 2 · Annual Mean Monthly Rainfall — Line + Area (1901–2023)",
                "badge-trend", "Line + Area Chart",
                "District-averaged monthly rainfall tracked year-on-year with shaded fill encoding cumulative seasonal pressure. The <b>peak year is annotated</b> with an arrow label. Long-term shifts in the trend line are a direct monsoon-variability and climate-change signal across 12 decades.",
                "CHARTS/02_yearly_trend.png")
        with col2:
            show_chart("chart-card-rainfall",
                "Chart 3 · Monthly Seasonality — Polar Bar Chart",
                "badge-rain", "Polar Bar Chart",
                "12 months on a polar wheel coloured by intensity (YlGnBu). The <b>towering bars at June–September</b> encode India's monsoon dominance in a single visual — the sharp shoulder flanking the peak marks the onset and withdrawal of the South-West Monsoon.",
                "CHARTS/03_monthly_polar.png")

        show_chart("chart-card-rainfall",
            "Chart 6 · Year × Month Mean Rainfall Heatmap (every 5 years)",
            "badge-corr", "2D Heatmap",
            "Every cell = average district rainfall in that year–month pair, sampled every 5 years for readability. The <b>bright Jun–Sep band</b> is clearly visible across all decades, while drought years appear as conspicuously cold rows. Historical anomalies — failed monsoons, El Niño years — jump out as isolated pale rows.",
            "CHARTS/06_heatmap_year_month.png")

        st.markdown("""<div class="insight-rainfall">
            💡 <strong>Temporal Insight:</strong> June–September accounts for over <strong>75% of India's annual rainfall</strong>.
            The heatmap clearly shows that years with below-normal June and July readings almost always produce full-year
            deficits — making early monsoon onset a critical leading indicator for annual water security assessment.
            Post-2000, the annual trend line shows increased inter-annual variability, a known fingerprint of
            climate-driven monsoon disruption.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 3: CATEGORY & DEPARTURE ANALYSIS ─────────────────────────────
    elif section == "💧 Category & Departure Analysis":
        st.markdown('<div class="section-header-rainfall">💧 Category & Departure Analysis (Charts 4, 5, 10)</div>', unsafe_allow_html=True)

        show_chart("chart-card-rainfall",
            "Chart 4 · Rainfall Distribution by Category — Violin + Strip",
            "badge-dist", "Violin + Strip Plot",
            "Violin width = record density at each rainfall level; white strip dots = individual district-months. Comparing the four IMD category panels reveals how thresholds translate into actual mm distributions — and whether <b>Excess events create a heavy upper tail</b> that overwhelms drainage infrastructure.",
            "CHARTS/04_category_violin.png")

        show_chart("chart-card-rainfall",
            "Chart 5 · Departure % vs Rainfall — Bubble Scatter (Bubble = Rainy Days)",
            "badge-rain-x", "Bubble Scatter",
            "Each point = one district-month at the intersection of % departure from normal and actual rainfall (mm). Bubble size encodes estimated rainy days. <b>Top-4 record rainfall events</b> are annotated in red. The dashed zero line separates surplus (right) from deficit (left) — visually anchoring the climatological norm.",
            "CHARTS/05_departure_scatter.png")

        show_chart("chart-card-rainfall",
            "Chart 10 · Departure % by Month — Grouped Boxplot",
            "badge-corr", "Grouped Boxplot",
            "Boxes compare how far monthly rainfall deviated from historical norms for each calendar month. The dashed zero line separates surplus from deficit. <b>Wide boxes at monsoon months</b> indicate high inter-annual variability; tight boxes in winter confirm near-predictable dryness that planners can reliably model.",
            "CHARTS/10_departure_month_box.png")

        st.markdown("""<div class="insight-rainfall">
            💡 <strong>Departure Insight:</strong> July and August show the <b>widest departure distributions</b> of any month —
            confirming these mid-monsoon months carry the highest year-to-year uncertainty.
            Excess events (positive departure > 60%) in July are associated with the most damaging floods, while
            Deficient July readings trigger immediate drought alerts across the Kharif crop belt.
            January and February show near-zero median departures with very tight IQRs — essentially deterministic dry months.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 4: STATE & ZONE PATTERNS ─────────────────────────────────────
    elif section == "🗺️ State & Zone Patterns":
        st.markdown('<div class="section-header-rainfall">🗺️ State & Zone Patterns (Charts 7, 8, 9)</div>', unsafe_allow_html=True)

        show_chart("chart-card-rainfall",
            "Chart 7 · Top 10 Highest District Monthly Rainfall Records (1901–2023)",
            "badge-rain", "Horizontal Bar Chart",
            "Blue bars for the highest-ever district-month rainfall records, annotated with mm value, year, state, and month. Reveals which districts and seasons have historically broken records — and whether the extremes are <b>concentrated in a few monsoon-belt states</b> or spread across India's geography.",
            "CHARTS/07_top10_rainfall.png")

        show_chart("chart-card-rainfall",
            "Chart 8 · Top 15 States — Rainfall Category Record Count (Stacked Bar)",
            "badge-geo", "Stacked Horizontal Bar",
            "Stacks Excess (blue), Normal (green), Deficient (orange), and Scanty (grey) record counts per state. A state with dominant blue faces <b>chronic flood risk</b>; one with dominant orange/grey faces <b>perennial drought</b>. Directly informs state-level water security and irrigation investment prioritisation.",
            "CHARTS/08_state_stacked.png")

        show_chart("chart-card-rainfall",
            "Chart 9 · Agro-Zone vs Rainfall Category — Cross-tabulation Heatmap",
            "badge-corr", "Cross-tab Heatmap",
            "Maps how agro-ecological zones (Arid, Semi-Arid, Sub-Humid, Humid) align with actual rainfall categories. Cells where <b>Arid zones recorded Excess events</b> — or where Humid zones went Scanty — reveal climate stress anomalies beyond the zone's historical baseline, flagging regions most impacted by monsoon disruption.",
            "CHARTS/09_agrozone_category_heatmap.png")

        st.markdown("""<div class="insight-rainfall">
            💡 <strong>Geographic Insight:</strong> The <strong>Humid agro-zone dominates Normal and Excess counts</strong>,
            confirming its reliable monsoon receipt. Critically, even Arid zones record a significant share of Excess months —
            these are intense, short-duration events that generate flash floods rather than beneficial recharge,
            as the dry soils cannot absorb the sudden surplus. Semi-Arid zones show the most balanced Deficient/Normal mix,
            making them the most sensitive to inter-annual monsoon shifts for agricultural planning.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 5: CORRELATIONS & DISTRIBUTIONS ───────────────────────────────
    elif section == "🔗 Correlations & Distributions":
        st.markdown('<div class="section-header-rainfall">🔗 Correlations & Distributions (Charts 11, 12, 13, 14, 15)</div>', unsafe_allow_html=True)

        show_chart("chart-card-rainfall",
            "Chart 11 · Rainy Days Distribution by Category — KDE + Histogram",
            "badge-dist", "KDE + Histogram",
            "Overlapping histograms and smooth KDE curves for each IMD category on the same axis. Mean lines annotated per category. A <b>longer right tail for Excess events</b> indicates months with near-continuous precipitation — these are the events that overwhelm drainage infrastructure and trigger urban flooding.",
            "CHARTS/11_rainy_days_kde.png")

        show_chart("chart-card-rainfall",
            "Chart 12 · Decade-wise Mean Monthly Rainfall by Agro-Zone — Grouped Bar",
            "badge-rain-x", "Grouped Bar Chart",
            "Side-by-side decade bars compare average monthly rainfall across agro-zones with annotated values floating above each bar. A <b>shrinking Humid-zone bar</b> across recent decades reveals the long-term monsoon weakening signal most relevant to India's food security and groundwater recharge planning.",
            "CHARTS/12_decade_zone_bar.png")

        col1, col2 = st.columns(2)
        with col1:
            show_chart("chart-card-rainfall",
                "Chart 13 · Departure % vs Rainy Days — Hexbin Density",
                "badge-dist", "Hexbin Density",
                "Hexagonal bins show where the majority of district-months cluster in departure-vs-rainy-days space. The dense core near zero departure represents the climatological normal; <b>rare hot cells in the extremes</b> are drought or flood outliers that stress infrastructure and relief systems.",
                "CHARTS/13_departure_rainydays_hexbin.png")
        with col2:
            show_chart("chart-card-rainfall",
                "Chart 14 · Correlation Matrix — Rainfall Features",
                "badge-corr", "Correlation Heatmap",
                "Lower-triangular Pearson correlation heatmap across 5 key numeric variables. The <b>near-perfect correlation between departure_mm and departure_pct</b> confirms feature redundancy — a critical insight for avoiding multicollinearity in drought prediction models.",
                "CHARTS/14_correlation_heatmap.png")

        show_chart("chart-card-rainfall",
            "Chart 15 · Pairplot — Key Rainfall Indicators (Hue = IMD Category)",
            "badge-rain", "4×4 Pairplot Grid",
            "Every key variable plotted against every other in a 4×4 grid — blue = Excess, green = Normal, orange = Deficient, grey = Scanty. Diagonal KDE curves show whether the four IMD categories form distinct distributions. <b>Bivariate scatter panels expose threshold effects</b> between normal_mm and departure_pct that single correlation values miss entirely.",
            "CHARTS/15_pairplot.png")

        st.markdown("""<div class="insight-rainfall">
            💡 <strong>Correlation Insight:</strong> <strong>departure_mm and departure_pct share a near-perfect correlation (≈ 0.99)</strong>
            — only one should be retained as a model feature. Rainy days and rainfall_mm show a strong positive
            correlation (≈ 0.75), but the scatter reveals substantial variance: some extreme events compress
            very high rainfall into very few days, the hallmark of convective flash-flood events.
            The pairplot KDE diagonals confirm that Excess and Scanty categories form clearly separable distributions
            on all key variables — a promising signal for classification-based drought and flood early-warning models.
        </div>""", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
if dashboard == "🌀 Cyclone Dashboard":
    footer_text = "🌀 Cyclone EDA · Indian Ocean Cyclone Dataset 1990–2023 · Streamlit + Matplotlib + Seaborn"
elif dashboard == "🌡️ Heatwave & Coldwave Dashboard":
    footer_text = "🌡️ Heatwave & Coldwave EDA · India Extreme Temperature Dataset 1980–2023 · Streamlit + Matplotlib + Seaborn"
elif dashboard == "🌫️ Air Quality Index Dashboard":
    footer_text = "🌫️ AQI EDA · India Air Quality Index Dataset 2015–2023 · Streamlit + Matplotlib + Seaborn"
else:
    footer_text = "🌧️ Rainfall EDA · India Monthly Rainfall Dataset 1901–2023 · Streamlit + Matplotlib + Seaborn"

st.markdown(f"""
<div style="text-align:center; color: rgba(255,255,255,0.3); font-size: 0.8rem; padding: 1rem 0;">
    {footer_text}
</div>
""", unsafe_allow_html=True)