import streamlit as st
from PIL import Image
import os
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌪️ India Extreme Weather EDA",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
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
    .hero h1 { font-size: 2.8rem; font-weight: 800; color: white; margin: 0; letter-spacing: -1px; }
    .hero p  { color: rgba(255,255,255,0.65); font-size: 1.05rem; margin-top: 0.5rem; }
    .hero .tag {
        display: inline-block; border-radius: 20px;
        padding: 3px 14px; font-size: 0.8rem; font-weight: 600; margin-right: 8px;
    }
    .tag-cyclone { background: rgba(232,67,147,0.2); color: #e84393; border: 1px solid rgba(232,67,147,0.4); }
    .tag-heat    { background: rgba(255,120,0,0.25); color: #ff9944; border: 1px solid rgba(255,120,0,0.4); }
    .tag-cold    { background: rgba(0,180,216,0.2);  color: #00b4d8; border: 1px solid rgba(0,180,216,0.4); }

    .kpi-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
        padding: 1.2rem 1.5rem; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-card-cyclone { background: linear-gradient(135deg, #1e1e3f, #2d2d6b); }
    .kpi-card-heat    { background: linear-gradient(135deg, #2e1000, #4a1800); }
    .kpi-val-cyclone { font-size: 2rem; font-weight: 800; color: #e84393; }
    .kpi-val-heat    { font-size: 2rem; font-weight: 800; color: #ff9944; }
    .kpi-val-cold    { font-size: 2rem; font-weight: 800; color: #00b4d8; }
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

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
        min-width: 260px !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    /* Text inside sidebar — be specific, NOT wildcard * */
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

    /* ── NEVER hide the sidebar collapse button or header ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: #e84393 !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 3px 0 20px rgba(232,67,147,0.7) !important;
        z-index: 9999 !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        color: white !important;
        stroke: white !important;
    }

    /* ── Hide ONLY hamburger menu and footer, NOT the header bar itself ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none !important; }

    /* ── Section headers ── */
    .section-header-cyclone {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #e84393; padding-left: 14px; margin: 2rem 0 1.2rem 0;
    }
    .section-header-heat {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #ff9944; padding-left: 14px; margin: 2rem 0 1.2rem 0;
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

    /* Sidebar radio hover */
    [data-testid="stSidebar"] .stRadio > div > label {
        padding: 5px 10px !important;
        border-radius: 8px !important;
        transition: background 0.2s !important;
        cursor: pointer !important;
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

# ── Load datasets ─────────────────────────────────────────────────────────────
cyc_df = try_load_csv("cyclone.csv")
hw_df  = try_load_csv("heatcold.csv")

# ── Cyclone KPIs ──────────────────────────────────────────────────────────────
if cyc_df is not None:
    total_cyclones = len(cyc_df)
    total_deaths_c = int(cyc_df['deaths'].sum()) if 'deaths' in cyc_df.columns else "N/A"
    max_wind       = cyc_df['max_wind_kmh'].max() if 'max_wind_kmh' in cyc_df.columns else "N/A"
    total_damage   = int(cyc_df['damage_crore_inr'].sum()) if 'damage_crore_inr' in cyc_df.columns else "N/A"
    landfall_pct   = round(cyc_df['landfall'].sum() / len(cyc_df) * 100, 1) if 'landfall' in cyc_df.columns else "N/A"
    super_cyclones = int((cyc_df['category'] == 'Super Cyclonic Storm').sum()) if 'category' in cyc_df.columns else "N/A"
else:
    total_cyclones = total_deaths_c = max_wind = total_damage = landfall_pct = super_cyclones = "N/A"

# ── Heatwave KPIs ─────────────────────────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  — FIX: use a single `section` key per dashboard, reset on switch
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌪️ India Weather EDA")
    st.markdown("---")

    # Dashboard picker — no session_state key tricks, just read the value directly
    dashboard = st.radio(
        "🗂️ Select Dashboard",
        ["🌀 Cyclone Dashboard", "🌡️ Heatwave & Coldwave Dashboard"],
    )

    st.markdown("---")

    # When the dashboard changes, reset the section index stored in session state
    db_key = "cyc" if dashboard == "🌀 Cyclone Dashboard" else "hw"
    prev_db_key = st.session_state.get("prev_db_key", db_key)
    if prev_db_key != db_key:
        # Dashboard switched → reset section to first item
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
        # Keep index in sync for reset logic
        st.session_state["section_idx"] = CYCLONE_SECTIONS.index(section)
        st.markdown("---")
        st.markdown("**Charts:** 15 unique visualisations  \n**Types:** Bar, Line, Polar, Violin, Scatter, Heatmap, Donut, KDE, Hexbin, Boxplot, Pairplot")
    else:
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

    # KPI row — guard against "N/A" for format spec
    def fmt(v, prefix="", suffix=""):
        return f"{prefix}{v:,}{suffix}" if isinstance(v, (int, float)) else str(v)

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

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    if section == "📋 Overview & KPIs":
        st.markdown('<div class="section-header-cyclone">📋 Category Distribution</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Cyclone Category Distribution</div>
          <span class="chart-badge badge-dist">Count Plot</span>
          <div class="chart-desc">
            Shows how cyclones are distributed across intensity categories from Depression to Super Cyclonic Storm.
            <b>Extremely Severe</b> storms dominate, revealing a worrying skew toward high-intensity events —
            a critical signal for disaster preparedness and policy planning.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/01_category_distribution.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 01_category_distribution.png — run the notebook to generate charts.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Key Insight:</strong> "Extremely Severe Cyclonic Storm" is the most frequent category (19 events),
            followed closely by regular Cyclonic Storms (18). Super Cyclonic Storms account for 15 events — more than
            Severe Cyclonic Storms — indicating increasing upper-end intensity in recent decades.
        </div>""", unsafe_allow_html=True)

    # ── TEMPORAL ──────────────────────────────────────────────────────────────
    elif section == "📅 Temporal Patterns":
        st.markdown('<div class="section-header-cyclone">📅 Temporal Patterns</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Annual Cyclone Frequency (1990–2023)</div>
              <span class="chart-badge badge-trend">Line + Area Chart</span>
              <div class="chart-desc">
                Tracks how cyclone activity has evolved year-on-year. The shaded area highlights cumulative
                intensity of activity while peak years are annotated directly on the chart for instant spotting
                of anomalous or record-breaking seasons.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/02_yearly_frequency.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 02_yearly_frequency.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Monthly Seasonality (Polar)</div>
              <span class="chart-badge badge-trend">Polar Bar Chart</span>
              <div class="chart-desc">
                A polar chart maps cyclone frequency to the 12-month calendar wheel — immediately
                revealing the bimodal seasonality: pre-monsoon (May) and post-monsoon (Oct–Nov) are
                the dominant windows for cyclogenesis in the Indian Ocean.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/03_monthly_polar.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 03_monthly_polar.png")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Year × Month Activity Heatmap</div>
          <span class="chart-badge badge-corr">Heatmap</span>
          <div class="chart-desc">
            A 2D grid where every cell shows how many cyclones occurred in a given year and month.
            Hot colours (red/orange) expose multi-cyclone months — years like 2007 and 2015 stand out
            as unusually active, while certain months are almost always quiet (e.g. February–March).
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/06_heatmap_year_month.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 06_heatmap_year_month.png")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Temporal Insight:</strong> October & November account for nearly <strong>40%</strong> of all cyclone events.
            The post-monsoon season is consistently the most dangerous window. Year-on-year, the 2010s decade saw
            the most clustered high-activity years, suggesting potential climate-driven intensification.
        </div>""", unsafe_allow_html=True)

    # ── INTENSITY ─────────────────────────────────────────────────────────────
    elif section == "💨 Intensity Analysis":
        st.markdown('<div class="section-header-cyclone">💨 Intensity Analysis</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Wind Speed Distribution by Category (Violin + Strip)</div>
          <span class="chart-badge badge-dist">Violin Plot</span>
          <div class="chart-desc">
            Violin plots show the full probability density of wind speeds within each category, while white strip dots
            reveal individual cyclone data points. The thicker the violin at a value, the more cyclones cluster there —
            exposing overlaps and outliers between adjacent intensity classes.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/04_wind_violin.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 04_wind_violin.png")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Wind Speed vs Pressure (Regression)</div>
              <span class="chart-badge badge-corr">Scatter + Regression</span>
              <div class="chart-desc">
                The classic inverse relationship between central pressure and wind speed.
                Lower pressure = higher winds. Annotated outliers highlight the most intense
                recorded storms with unprecedented low-pressure readings.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/10_wind_pressure_scatter.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 10_wind_pressure_scatter.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Duration vs Track Length (Hexbin)</div>
              <span class="chart-badge badge-dist">Hexbin Density</span>
              <div class="chart-desc">
                Hexbin bins show where the most cyclones cluster in duration–track space.
                Long-lived storms that travel far are rare but extremely destructive —
                the sparse hot cells at the extreme corners are the most dangerous events.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/13_duration_track_hexbin.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 13_duration_track_hexbin.png")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Intensity Insight:</strong> Wind speed and minimum pressure have a near-perfect
            <strong>negative correlation (≈ −0.97)</strong>. Super Cyclonic Storms cluster around pressures below 920 hPa
            and winds exceeding 220 km/h — well beyond the threshold where standard infrastructure fails.
        </div>""", unsafe_allow_html=True)

    # ── IMPACT ────────────────────────────────────────────────────────────────
    elif section == "🌊 Impact & Damage":
        st.markdown('<div class="section-header-cyclone">🌊 Impact & Damage Analysis</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Deaths vs Economic Damage — Bubble Chart (Log Scale)</div>
          <span class="chart-badge badge-impact">Bubble Scatter</span>
          <div class="chart-desc">
            Plots every cyclone at the intersection of human cost (deaths) and economic damage, with bubble size
            encoding wind speed and colour showing category. Log scale prevents a handful of mega-disasters from
            collapsing all other data — enabling pattern detection across the full severity spectrum.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/05_deaths_damage_scatter.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 05_deaths_damage_scatter.png")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Top 10 Deadliest Cyclones</div>
              <span class="chart-badge badge-impact">Horizontal Bar</span>
              <div class="chart-desc">
                Ranks the 10 most lethal cyclones with death toll and year. Colour gradient
                (light → dark red) visually reinforces magnitude. The catastrophic gap between
                the top event and the rest is immediately visible.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/08_top10_deadliest.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 08_top10_deadliest.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Storm Surge Distribution (KDE + Histogram)</div>
              <span class="chart-badge badge-dist">KDE Histogram</span>
              <div class="chart-desc">
                Overlays a histogram with a kernel density curve to reveal the surge distribution shape.
                The 95th percentile marker highlights the extreme tail — surges above this level
                cause catastrophic coastal inundation and are the primary driver of mass casualties.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/12_surge_kde.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 12_surge_kde.png")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Decade-wise Economic Damage (Boxplot)</div>
          <span class="chart-badge badge-trend">Box + Strip Plot</span>
          <div class="chart-desc">
            Compares damage distributions across four decades. The box shows the interquartile range,
            the horizontal line is the median, and diamond-shaped outliers are extreme economic disaster events.
            The rising medians decade over decade tell a stark story about escalating costs.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/14_decade_damage_box.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 14_decade_damage_box.png")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Impact Insight:</strong> Economic damage in the 2010s is <strong>3× the median</strong> of the 1990s,
            even inflation-adjusted. Storm surge above 4m is the <strong>single strongest predictor</strong> of both deaths
            and damage — targeted coastal early-warning systems could dramatically cut casualties.
        </div>""", unsafe_allow_html=True)

    # ── GEOGRAPHIC ────────────────────────────────────────────────────────────
    elif section == "🗺️ Geographic Patterns":
        st.markdown('<div class="section-header-cyclone">🗺️ Geographic Patterns</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Landfall Distribution by State (Donut)</div>
              <span class="chart-badge badge-geo">Donut Chart</span>
              <div class="chart-desc">
                A donut chart shows each state's share of total landfall events. The hollow centre
                displays the total count. States with larger slices bear a disproportionate risk burden
                and require more robust cyclone infrastructure investment.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/11_landfall_donut.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 11_landfall_donut.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card">
              <div class="chart-title">Category Split by Basin (Stacked Bar)</div>
              <span class="chart-badge badge-geo">Stacked Bar</span>
              <div class="chart-desc">
                Compares how cyclone intensity categories are distributed between the Bay of Bengal
                and the Arabian Sea. The stacking reveals whether one basin disproportionately produces
                extreme storms — a key insight for regional hazard risk modelling.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/07_basin_category_stacked.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: 07_basin_category_stacked.png")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Geographic Insight:</strong> Karnataka, West Bengal, Andhra Pradesh, Gujarat and Maharashtra
            each receive <strong>~21% of landfalls</strong> — surprisingly balanced. However, the Bay of Bengal produces
            significantly more <strong>Super Cyclonic Storms</strong> than the Arabian Sea, making its coastlines
            higher-risk for catastrophic events.
        </div>""", unsafe_allow_html=True)

    # ── CORRELATIONS ──────────────────────────────────────────────────────────
    elif section == "🔗 Correlations":
        st.markdown('<div class="section-header-cyclone">🔗 Correlation & Multivariate Analysis</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Correlation Matrix — All Numerical Features</div>
          <span class="chart-badge badge-corr">Heatmap</span>
          <div class="chart-desc">
            A triangular correlation matrix covering all 10 numerical variables. Red cells show strong
            positive correlations, blue cells show negative ones. This is the key chart for understanding
            which variables move together — guiding feature selection for predictive modelling.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/09_correlation_heatmap.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 09_correlation_heatmap.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card">
          <div class="chart-title">Pairplot — Extreme Cyclone Indicators (Basin Hue)</div>
          <span class="chart-badge badge-corr">Pairplot</span>
          <div class="chart-desc">
            Every variable is plotted against every other variable in a grid. Diagonal cells show KDE
            distributions for each basin. This single chart encodes dozens of bivariate relationships
            simultaneously — pink = Bay of Bengal, green = Arabian Sea — revealing basin-specific clustering.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/15_pairplot.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: 15_pairplot.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-cyclone">
            💡 <strong>Correlation Insight:</strong> <strong>Affected districts</strong> and <strong>evacuated population</strong>
            show the strongest positive correlation (0.89), confirming evacuation scales proportionally with exposure.
            Surprisingly, <strong>IMD warning lead time</strong> has only a weak negative correlation with deaths —
            suggesting warning effectiveness depends more on communication quality than lead time alone.
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HEATWAVE & COLDWAVE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
else:

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

    def fmt(v, prefix="", suffix=""):
        return f"{prefix}{v:,}{suffix}" if isinstance(v, (int, float)) else str(v)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(total_events)}</div><div class="kpi-lbl">Total Events</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(n_heatwaves)}</div><div class="kpi-lbl">Heatwaves</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-cold">{fmt(n_coldwaves)}</div><div class="kpi-lbl">Coldwaves</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(total_deaths_h)}</div><div class="kpi-lbl">Total Deaths</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(max_temp, suffix='°C')}</div><div class="kpi-lbl">Peak Temp Recorded</div></div>
      <div class="kpi-card kpi-card-heat"><div class="kpi-val-heat">{fmt(states_affected)}</div><div class="kpi-lbl">States Affected</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1: EVENT OVERVIEW & KPIs ─────────────────────────────────────
    if section == "📋 Event Overview & KPIs":
        st.markdown('<div class="section-header-heat">📋 Heatwave vs Coldwave — Event Split</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 1 · Heatwave vs Coldwave — Donut Chart</div>
          <span class="chart-badge badge-heat">Donut Chart</span>
          <div class="chart-desc">
            Overall proportion of heatwaves (pink) vs coldwaves (blue) across the full 44-year record.
            The hollow centre displays total event count — an instant baseline before deeper analysis.
            The ratio is shifting: heatwave frequency has risen steeply since 2000, a direct fingerprint of long-term warming.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/01_event_type_donut.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/01_event_type_donut.png — run heatwave_eda notebook first.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Key Insight:</strong> Heatwaves make up the majority of events yet both types carry
            severe mortality risk across different seasons. Heatwave counts are accelerating post-2000 while
            coldwaves have plateaued — a direct signal of India's warming trajectory over 44 years.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 2: ANNUAL & SEASONAL TRENDS ──────────────────────────────────
    elif section == "📅 Annual & Seasonal Trends":
        st.markdown('<div class="section-header-heat">📅 Annual & Seasonal Trends (Charts 2, 3, 6)</div>', unsafe_allow_html=True)

        # Chart 2 + Chart 3 side by side
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 2 · Annual Frequency — Dual Line + Area (1980–2023)</div>
              <span class="chart-badge badge-trend">Line + Area Chart</span>
              <div class="chart-desc">
                Heatwave (pink) and coldwave (blue) event counts tracked year-on-year with shaded fills.
                Diverging trends between the two series are a direct climate-change signal —
                heatwaves climbing while coldwaves remain flat or decline over four decades.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/02_yearly_frequency.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/02_yearly_frequency.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 3 · Monthly Seasonality — Dual Polar Bar</div>
              <span class="chart-badge badge-heat">Polar Bar Chart</span>
              <div class="chart-desc">
                12 months mapped onto a polar wheel with side-by-side bars per event type.
                The near-opposite positioning of pink (Mar–Jun) vs blue (Dec–Feb) encodes
                India's entire temperature seasonality in a single striking chart.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/03_monthly_polar.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/03_monthly_polar.png")
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart 6 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 6 · Year × Month Event Frequency Heatmap</div>
          <span class="chart-badge badge-corr">2D Heatmap</span>
          <div class="chart-desc">
            Every cell shows the number of extreme temperature events in a given year–month pair.
            The bright March–June band for heatwaves and December–February band for coldwaves are
            clearly visible year after year — certain years like 2015 and 2022 show exceptionally dense clusters.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/06_heatmap_year_month.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/06_heatmap_year_month.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Temporal Insight:</strong> Heatwaves peak in <strong>May–June</strong>; coldwaves dominate
            <strong>December–January</strong>. The 2010s saw the most concentrated heatwave clusters —
            multiple years recording 5+ events vs. fewer than 2 per year in the 1980s.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 3: TEMPERATURE & SEVERITY ────────────────────────────────────
    elif section == "🌡️ Temperature & Severity":
        st.markdown('<div class="section-header-heat">🌡️ Temperature & Severity Analysis (Charts 4, 9, 10, 11)</div>', unsafe_allow_html=True)

        # Chart 4 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 4 · Peak Temperature by Severity — Side-by-side Violin + Strip</div>
          <span class="chart-badge badge-dist">Violin + Strip Plot</span>
          <div class="chart-desc">
            Violin width = event density at each temperature; white dots = individual events.
            Heatwave Severe class easily exceeds 45°C while Coldwave Severe drops below 5°C —
            the dangerous overlap between Moderate and Severe heatwaves is exposed clearly.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/04_temp_violin.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/04_temp_violin.png")
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart 9 + Chart 10 side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 9 · Severity vs IMD Alert Level — Cross-tab Heatmap</div>
              <span class="chart-badge badge-corr">Cross-tab Heatmap</span>
              <div class="chart-desc">
                Maps IMD alert levels (Yellow/Orange/Red) against actual severity class.
                Misaligned cells — Severe events with only Yellow alerts, or Red alerts for Mild events —
                reveal real calibration gaps in India's national weather warning system.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/09_severity_alert_heatmap.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/09_severity_alert_heatmap.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 10 · Temperature Anomaly by Severity — Grouped Boxplot</div>
              <span class="chart-badge badge-heat">Grouped Boxplot</span>
              <div class="chart-desc">
                Grouped boxes show how far temperatures deviated from historical norms per severity class.
                The dashed zero line divides positive (heat) from negative (cold) anomalies —
                Severe heatwaves sit at +6°C to +10°C above the norm.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/10_anomaly_severity_box.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/10_anomaly_severity_box.png")
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart 11 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 11 · Event Duration Distribution — Overlapping KDE + Histogram</div>
          <span class="chart-badge badge-dist">KDE + Histogram</span>
          <div class="chart-desc">
            Overlapping histograms and KDE curves for both event types with annotated mean lines.
            A longer right tail means more chronic multi-week events — these accumulate far greater
            physiological and economic damage than short-duration spikes of equal peak intensity.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/11_duration_kde.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/11_duration_kde.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Severity Insight:</strong> Severe heatwaves record anomalies of <strong>+6°C to +10°C</strong>
            above historical norms. IMD Red alerts are under-issued for Moderate events — a calibration gap
            that directly raises mortality risk. Heatwaves also run significantly longer on average than coldwaves.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 4: DEATHS & MORTALITY IMPACT ─────────────────────────────────
    elif section == "💀 Deaths & Mortality Impact":
        st.markdown('<div class="section-header-heat">💀 Deaths & Mortality Impact (Charts 5, 7, 12, 13)</div>', unsafe_allow_html=True)

        # Chart 5 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 5 · Deaths vs Temperature Anomaly — Bubble Scatter</div>
          <span class="chart-badge badge-impact">Bubble Scatter</span>
          <div class="chart-desc">
            Each bubble = one event, positioned at the intersection of temperature deviation and death toll.
            Bubble size encodes event duration in days. Annotated outliers are the 4 most lethal events in 44 years.
            Right half (positive anomaly) = heatwaves; left half = coldwaves.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/05_deaths_anomaly_scatter.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/05_deaths_anomaly_scatter.png")
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart 7 + Chart 12 side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 7 · Top 10 Deadliest Events (1980–2023)</div>
              <span class="chart-badge badge-impact">Horizontal Bar Chart</span>
              <div class="chart-desc">
                Pink = heatwave, blue = coldwave. Annotated with death count, year, and state.
                Reveals which type has historically dominated mortality and which single events
                were catastrophic outliers far above the rest of the distribution.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/07_top10_deadliest.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/07_top10_deadliest.png")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="chart-card-heat">
              <div class="chart-title">Chart 12 · Decade-wise Total Deaths — Grouped Bar</div>
              <span class="chart-badge badge-trend">Grouped Bar Chart</span>
              <div class="chart-desc">
                Side-by-side decade bars compare total mortality from heatwaves vs coldwaves.
                Totals float above each bar. A widening gap across decades reveals the long-term
                shift in which extreme temperature type poses the greater mortality risk to India.
              </div>
            """, unsafe_allow_html=True)
            img = load_img("CHARTS/12_decade_deaths_bar.png")
            if img: st.image(img, width="stretch")
            else: st.info("📂 Chart not found: CHARTS/12_decade_deaths_bar.png")
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart 13 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 13 · Districts Affected vs Deaths — Hexbin Density</div>
          <span class="chart-badge badge-dist">Hexbin Density Plot</span>
          <div class="chart-desc">
            Hexagonal bins show where the majority of events cluster in districts-vs-deaths space.
            The dense core near low values is the "typical" event; rare bright cells in the upper-right
            are catastrophic multi-district events that overwhelm state emergency response systems.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/13_districts_deaths_hexbin.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/13_districts_deaths_hexbin.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Mortality Insight:</strong> Heatwave deaths in the 2010s were <strong>2.4× higher</strong> than the 1990s.
            Events spanning more than 20 districts are rare but account for a disproportionate share of total deaths —
            geographic spread amplifies mortality by exhausting healthcare and emergency response capacity simultaneously.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 5: STATE-WISE RISK PATTERNS ──────────────────────────────────
    elif section == "🗺️ State-wise Risk Patterns":
        st.markdown('<div class="section-header-heat">🗺️ State-wise Risk Patterns (Chart 8)</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 8 · Top 15 States — Heatwave & Coldwave Event Count (Stacked Bar)</div>
          <span class="chart-badge badge-geo">Stacked Horizontal Bar</span>
          <div class="chart-desc">
            Heatwave (pink) and coldwave (blue) event counts stacked per state — ranked by total exposure.
            A state with balanced colours faces year-round dual-season risk; dominance of one colour reveals
            seasonal skew. Directly informs state-level NDRF deployment and disaster preparedness planning.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/08_state_events_stacked.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/08_state_events_stacked.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Geographic Insight:</strong> <strong>Rajasthan, Uttar Pradesh, and Odisha</strong> top the heatwave count,
            while <strong>Bihar and West Bengal</strong> face the highest coldwave exposure. States across the Indo-Gangetic Plain
            face dual-season risk from both types simultaneously — requiring year-round extreme weather preparedness infrastructure.
        </div>""", unsafe_allow_html=True)

    # ── SECTION 6: CORRELATIONS & PAIRPLOT ───────────────────────────────────
    elif section == "🔗 Correlations & Pairplot":
        st.markdown('<div class="section-header-heat">🔗 Correlations & Pairplot (Charts 14, 15)</div>', unsafe_allow_html=True)

        # Chart 14 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 14 · Correlation Matrix — All Numerical Features</div>
          <span class="chart-badge badge-corr">Lower-Triangular Heatmap</span>
          <div class="chart-desc">
            Lower-triangular correlation heatmap across 6 key numeric variables: duration, peak_temp, temp_anomaly,
            threshold_exceeded, estimated_deaths, districts_affected. Red = strong positive, blue = strong negative.
            The near-perfect correlation between temp_anomaly and threshold_exceeded confirms feature redundancy.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/14_correlation_heatmap.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/14_correlation_heatmap.png")
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart 15 full width
        st.markdown("""
        <div class="chart-card-heat">
          <div class="chart-title">Chart 15 · Pairplot — Key Extreme-Temperature Indicators (Hue = Event Type)</div>
          <span class="chart-badge badge-corr">5×5 Pairplot Grid</span>
          <div class="chart-desc">
            Every key variable plotted against every other in a 5×5 grid — pink = heatwave, blue = coldwave.
            Diagonal KDE curves show whether the two event types form distinct distributions.
            Bivariate scatter panels expose nonlinear relationships that single correlation values miss entirely.
          </div>
        """, unsafe_allow_html=True)
        img = load_img("CHARTS/15_pairplot.png")
        if img: st.image(img, width="stretch")
        else: st.info("📂 Chart not found: CHARTS/15_pairplot.png")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight-heat">
            💡 <strong>Correlation Insight:</strong> <strong>Duration × districts_affected</strong> show the strongest
            positive correlation (≈ 0.71) — longer events spread further geographically. Surprisingly, peak temperature alone
            is a <strong>weak predictor of deaths</strong>; it's the interaction of anomaly, duration, and affected population
            density that drives mortality — pointing to the need for multi-variable composite risk indices.
        </div>""", unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
footer_txt = (
    "🌀 Cyclone EDA · Indian Ocean Cyclone Dataset 1990–2023 · Streamlit + Matplotlib + Seaborn"
    if dashboard == "🌀 Cyclone Dashboard"
    else "🌡️ Heatwave & Coldwave EDA · India Extreme Temperature Dataset 1980–2023 · Streamlit + Matplotlib + Seaborn"
)
st.markdown(f"""
<div style="text-align:center; color: rgba(255,255,255,0.3); font-size: 0.8rem; padding: 1rem 0;">
    {footer_txt}
</div>
""", unsafe_allow_html=True)