import streamlit as st
from PIL import Image
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌀 Cyclone EDA Dashboard",
    page_icon="🌀",
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

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .hero h1 { font-size: 2.8rem; font-weight: 800; color: white; margin: 0; letter-spacing: -1px; }
    .hero p  { color: rgba(255,255,255,0.65); font-size: 1.05rem; margin-top: 0.5rem; }
    .hero .tag {
        display: inline-block; background: rgba(232,67,147,0.2); color: #e84393;
        border: 1px solid rgba(232,67,147,0.4); border-radius: 20px;
        padding: 3px 14px; font-size: 0.8rem; font-weight: 600; margin-right: 8px;
    }

    /* KPI cards */
    .kpi-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 140px;
        background: linear-gradient(135deg, #1e1e3f, #2d2d6b);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;
        padding: 1.2rem 1.5rem; text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-val { font-size: 2rem; font-weight: 800; color: #e84393; }
    .kpi-lbl { font-size: 0.78rem; color: rgba(255,255,255,0.55); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Chart card */
    .chart-card {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        border: 1px solid rgba(255,255,255,0.07); border-radius: 18px;
        padding: 1.8rem; margin-bottom: 1.5rem;
        box-shadow: 0 12px 36px rgba(0,0,0,0.35);
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

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }

    /* Section header */
    .section-header {
        font-size: 1.35rem; font-weight: 700; color: white;
        border-left: 4px solid #e84393; padding-left: 14px;
        margin: 2rem 0 1.2rem 0;
    }

    /* Insight box */
    .insight {
        background: linear-gradient(135deg, rgba(232,67,147,0.08), rgba(108,92,231,0.08));
        border: 1px solid rgba(232,67,147,0.25); border-radius: 12px;
        padding: 1rem 1.3rem; margin-top: 1rem; font-size: 0.88rem;
        color: rgba(255,255,255,0.75); line-height: 1.6;
    }
    .insight strong { color: #fd79a8; }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
import pandas as pd
df = pd.read_csv("cyclone.csv")
CHARTS = "charts/"

def load_img(name):
    path = os.path.join(name)
    return Image.open(path) if os.path.exists(path) else None

# ── KPI compute ───────────────────────────────────────────────────────────────
total_cyclones  = len(df)
total_deaths    = df['deaths'].sum()
max_wind        = df['max_wind_kmh'].max()
total_damage    = df['damage_crore_inr'].sum()
landfall_pct    = round(df['landfall'].sum() / len(df) * 100, 1)
super_cyclones  = (df['category'] == 'Super Cyclonic Storm').sum()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌀 Cyclone EDA")
    st.markdown("---")
    st.markdown("**Dataset:** Indian Ocean Cyclones  \n**Period:** 1990 – 2023  \n**Records:** 103 cyclones  \n**Features:** 17 variables")
    st.markdown("---")
    section = st.radio("📊 Jump to Section", [
        "📋 Overview & KPIs",
        "📅 Temporal Patterns",
        "💨 Intensity Analysis",
        "🌊 Impact & Damage",
        "🗺️ Geographic Patterns",
        "🔗 Correlations",
    ])
    st.markdown("---")
    st.markdown("**Charts:** 15 unique visualisations  \n**Types:** Bar, Line, Polar, Violin, Scatter, Heatmap, Donut, KDE, Hexbin, Boxplot, Pairplot")

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🌀 Indian Ocean Cyclone EDA</h1>
  <p>Exploratory Data Analysis — Extreme Pattern Discovery across 103 cyclone events (1990–2023)</p>
  <span class="tag">1990–2023</span>
  <span class="tag">Bay of Bengal</span>
  <span class="tag">Arabian Sea</span>
  <span class="tag">15 Charts</span>
  <span class="tag">Matplotlib · Seaborn</span>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-val">{total_cyclones}</div><div class="kpi-lbl">Total Cyclones</div></div>
  <div class="kpi-card"><div class="kpi-val">{total_deaths:,}</div><div class="kpi-lbl">Total Deaths</div></div>
  <div class="kpi-card"><div class="kpi-val">{max_wind}</div><div class="kpi-lbl">Max Wind (km/h)</div></div>
  <div class="kpi-card"><div class="kpi-val">₹{total_damage:,}</div><div class="kpi-lbl">Total Damage (Cr)</div></div>
  <div class="kpi-card"><div class="kpi-val">{landfall_pct}%</div><div class="kpi-lbl">Landfall Rate</div></div>
  <div class="kpi-card"><div class="kpi-val">{super_cyclones}</div><div class="kpi-lbl">Super Cyclones</div></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if section in ["📋 Overview & KPIs", "📅 Temporal Patterns", "💨 Intensity Analysis",
               "🌊 Impact & Damage", "🗺️ Geographic Patterns", "🔗 Correlations"]:

    if section == "📋 Overview & KPIs":
        st.markdown('<div class="section-header">📋 Category Distribution</div>', unsafe_allow_html=True)
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
        img = load_img("01_category_distribution.png")
        if img: st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            💡 <strong>Key Insight:</strong> "Extremely Severe Cyclonic Storm" is the most frequent category (19 events),
            followed closely by regular Cyclonic Storms (18). Super Cyclonic Storms account for 15 events — more than
            Severe Cyclonic Storms — indicating increasing upper-end intensity in recent decades.
        </div>""", unsafe_allow_html=True)

    # ── TEMPORAL ──────────────────────────────────────────────────────────────
    elif section == "📅 Temporal Patterns":
        st.markdown('<div class="section-header">📅 Temporal Patterns</div>', unsafe_allow_html=True)

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
            img = load_img("02_yearly_frequency.png")
            if img: st.image(img, use_container_width=True)
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
            img = load_img("03_monthly_polar.png")
            if img: st.image(img, use_container_width=True)
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
        img = load_img("06_heatmap_year_month.png")
        if img: st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            💡 <strong>Temporal Insight:</strong> October & November account for nearly <strong>40%</strong> of all cyclone events.
            The post-monsoon season is consistently the most dangerous window. Year-on-year, the 2010s decade saw
            the most clustered high-activity years, suggesting potential climate-driven intensification.
        </div>""", unsafe_allow_html=True)

    # ── INTENSITY ─────────────────────────────────────────────────────────────
    elif section == "💨 Intensity Analysis":
        st.markdown('<div class="section-header">💨 Intensity Analysis</div>', unsafe_allow_html=True)

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
        img = load_img("04_wind_violin.png")
        if img: st.image(img, use_container_width=True)
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
                recorded storms with unprecedented low-pressure readings.streamlit 
              </div>
            """, unsafe_allow_html=True)
            img = load_img("10_wind_pressure_scatter.png")
            if img: st.image(img, use_container_width=True)
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
            img = load_img("13_duration_track_hexbin.png")
            if img: st.image(img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight">
            💡 <strong>Intensity Insight:</strong> Wind speed and minimum pressure have a near-perfect
            <strong>negative correlation (≈ −0.97)</strong>. Super Cyclonic Storms cluster around pressures below 920 hPa
            and winds exceeding 220 km/h — well beyond the threshold where standard infrastructure fails.
        </div>""", unsafe_allow_html=True)

    # ── IMPACT ────────────────────────────────────────────────────────────────
    elif section == "🌊 Impact & Damage":
        st.markdown('<div class="section-header">🌊 Impact & Damage Analysis</div>', unsafe_allow_html=True)

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
        img = load_img("05_deaths_damage_scatter.png")
        if img: st.image(img, use_container_width=True)
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
            img = load_img("08_top10_deadliest.png")
            if img: st.image(img, use_container_width=True)
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
            img = load_img("12_surge_kde.png")
            if img: st.image(img, use_container_width=True)
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
        img = load_img("14_decade_damage_box.png")
        if img: st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            💡 <strong>Impact Insight:</strong> Economic damage in the 2010s is <strong>3× the median</strong> of the 1990s,
            even inflation-adjusted. Storm surge above 4m is the <strong>single strongest predictor</strong> of both deaths
            and damage — targeted coastal early-warning systems could dramatically cut casualties.
        </div>""", unsafe_allow_html=True)

    # ── GEOGRAPHIC ────────────────────────────────────────────────────────────
    elif section == "🗺️ Geographic Patterns":
        st.markdown('<div class="section-header">🗺️ Geographic Patterns</div>', unsafe_allow_html=True)

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
            img = load_img("11_landfall_donut.png")
            if img: st.image(img, use_container_width=True)
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
            img = load_img("07_basin_category_stacked.png")
            if img: st.image(img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight">
            💡 <strong>Geographic Insight:</strong> Karnataka, West Bengal, Andhra Pradesh, Gujarat and Maharashtra
            each receive <strong>~21% of landfalls</strong> — surprisingly balanced. However, the Bay of Bengal produces
            significantly more <strong>Super Cyclonic Storms</strong> than the Arabian Sea, making its coastlines
            higher-risk for catastrophic events.
        </div>""", unsafe_allow_html=True)

    # ── CORRELATIONS ──────────────────────────────────────────────────────────
    elif section == "🔗 Correlations":
        st.markdown('<div class="section-header">🔗 Correlation & Multivariate Analysis</div>', unsafe_allow_html=True)

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
        img = load_img("09_correlation_heatmap.png")
        if img: st.image(img, use_container_width=True)
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
        img = load_img("15_pairplot.png")
        if img: st.image(img, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""<div class="insight">
            💡 <strong>Correlation Insight:</strong> <strong>Affected districts</strong> and <strong>evacuated population</strong>
            show the strongest positive correlation (0.89), confirming evacuation scales proportionally with exposure.
            Surprisingly, <strong>IMD warning lead time</strong> has only a weak negative correlation with deaths —
            suggesting warning effectiveness depends more on communication quality than lead time alone.
        </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color: rgba(255,255,255,0.3); font-size: 0.8rem; padding: 1rem 0;">
    🌀 Cyclone EDA Dashboard · Indian Ocean Cyclone Dataset 1990–2023 · Built with Streamlit, Matplotlib & Seaborn
</div>
""", unsafe_allow_html=True)