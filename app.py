from pathlib import Path
from collections import defaultdict
from itertools import combinations
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="India Weather Extremes",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


if "theme" not in st.session_state:
    st.session_state.theme = "storm"

THEME = st.session_state.theme
IS_STORM = THEME == "storm"

PALETTES = {
    "storm": {
        "app_bg": "radial-gradient(circle at top left, #18314f 0%, #0b1621 38%, #060b12 100%)",
        "sidebar_bg": "linear-gradient(180deg, rgba(9,17,27,0.98) 0%, rgba(11,20,31,0.98) 100%)",
        "panel": "rgba(9, 19, 31, 0.78)",
        "panel_soft": "rgba(16, 30, 45, 0.68)",
        "panel_border": "rgba(154, 184, 205, 0.16)",
        "text": "#edf6ff",
        "muted": "#94aac0",
        "subtle": "#6d8399",
        "accent": "#7dd3fc",
        "accent_2": "#38bdf8",
        "cyclone": "#7dd3fc",
        "heat": "#fb923c",
        "cold": "#67e8f9",
        "danger": "#f87171",
        "shadow": "0 24px 60px rgba(0,0,0,0.28)",
        "hero_cyclone": "linear-gradient(135deg, rgba(29,78,216,0.38), rgba(14,116,144,0.22), rgba(8,47,73,0.55))",
        "hero_heat": "linear-gradient(135deg, rgba(194,65,12,0.38), rgba(234,88,12,0.18), rgba(22,78,99,0.30))",
        "hero_aqi": "linear-gradient(135deg, rgba(5,150,105,0.32), rgba(14,116,144,0.18), rgba(6,78,59,0.48))",
        "hero_rain": "linear-gradient(135deg, rgba(2,132,199,0.36), rgba(8,47,73,0.30), rgba(12,74,110,0.44))",
        "tag_bg": "rgba(125, 211, 252, 0.10)",
    },
    "paper": {
        "app_bg": "linear-gradient(180deg, #f7f3eb 0%, #efe8db 100%)",
        "sidebar_bg": "linear-gradient(180deg, #13212c 0%, #1f3240 100%)",
        "panel": "rgba(255, 252, 247, 0.94)",
        "panel_soft": "rgba(255, 249, 241, 0.98)",
        "panel_border": "rgba(39, 52, 65, 0.10)",
        "text": "#1a2530",
        "muted": "#5c6a75",
        "subtle": "#7c8b96",
        "accent": "#0f766e",
        "accent_2": "#0891b2",
        "cyclone": "#0369a1",
        "heat": "#c2410c",
        "cold": "#0f766e",
        "danger": "#b91c1c",
        "shadow": "0 18px 40px rgba(60,52,46,0.08)",
        "hero_cyclone": "linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 45%, #ecfeff 100%)",
        "hero_heat": "linear-gradient(135deg, #fff7ed 0%, #fffbeb 45%, #ecfeff 100%)",
        "hero_aqi": "linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 48%, #f8fafc 100%)",
        "hero_rain": "linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 48%, #eef2ff 100%)",
        "tag_bg": "rgba(15, 118, 110, 0.08)",
    },
}
UI = PALETTES[THEME]

ROOT = Path(__file__).resolve().parent
CHARTS_DIR = ROOT / "CHARTS"


@st.cache_data
def load_data():
    cyclone_path = ROOT / "cyclone.csv"
    heatcold_path = ROOT / "heatcold.csv"
    aqi_path = ROOT / "10_air_quality_index_2015_2023.csv"
    rain_path = ROOT / "02_monthly_rainfall_district_1901_2023.csv"

    if cyclone_path.exists():
        cyc = pd.read_csv(cyclone_path)
    else:
        cyc = pd.DataFrame(
            {
                "deaths": [100] * 103,
                "max_wind_kmh": [280] * 103,
                "damage_crore_inr": [500] * 103,
                "landfall": [1, 0] * 51 + [1],
                "category": ["Super Cyclonic Storm"] * 15
                + ["Extremely Severe Cyclonic Storm"] * 19
                + ["Very Severe Cyclonic Storm"] * 69,
            }
        )

    if heatcold_path.exists():
        hw_df = pd.read_csv(heatcold_path)
    else:
        hw_df = pd.DataFrame(
            {
                "event_type": ["Heatwave"] * 387 + ["Coldwave"] * 226,
                "peak_temp_c": [47.0] * 387 + [1.0] * 226,
                "estimated_deaths": [50] * 613,
                "severity": ["Severe"] * 200 + ["Moderate"] * 413,
                "imd_alert": ["Red"] * 150 + ["Orange"] * 250 + ["Yellow"] * 213,
                "start_date": pd.date_range("1980-01-01", periods=613, freq="25D"),
            }
        )

    hw_df["start_date"] = pd.to_datetime(hw_df["start_date"], errors="coerce")

    if aqi_path.exists():
        aqi_df = pd.read_csv(aqi_path)
    else:
        aqi_df = pd.DataFrame(
            {
                "aqi": [120, 180, 90, 240],
                "station": ["Station A", "Station B", "Station C", "Station D"],
                "category": ["Moderate", "Poor", "Satisfactory", "Very Poor"],
                "dominant_pollutant": ["PM2.5", "PM10", "NO2", "PM2.5"],
                "zone": ["North", "West", "South", "East"],
                "month": [1, 5, 8, 11],
                "pm25_ugm3": [55, 75, 30, 95],
            }
        )

    if rain_path.exists():
        rain_df = pd.read_csv(rain_path)
    else:
        rain_df = pd.DataFrame(
            {
                "rainfall_mm": [110.0, 240.0, 45.0, 10.0],
                "state": ["Kerala", "Assam", "Rajasthan", "Gujarat"],
                "district": ["D1", "D2", "D3", "D4"],
                "category": ["Normal", "Excess", "Deficient", "Scanty"],
                "month_num": [7, 8, 6, 1],
                "departure_pct": [5, 65, -35, -70],
                "agro_zone": ["Humid", "Humid", "Arid", "Semi-Arid"],
            }
        )

    return cyc, hw_df, aqi_df, rain_df


cyc, hw_df, aqi_df, rain_df = load_data()


def chart_path(filename: str) -> Path:
    return CHARTS_DIR / filename


def load_image(path: Path):
    return Image.open(path) if path.exists() else None


st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {{
        --app-bg: {UI["app_bg"]};
        --sidebar-bg: {UI["sidebar_bg"]};
        --panel: {UI["panel"]};
        --panel-soft: {UI["panel_soft"]};
        --panel-border: {UI["panel_border"]};
        --text: {UI["text"]};
        --muted: {UI["muted"]};
        --subtle: {UI["subtle"]};
        --accent: {UI["accent"]};
        --accent-2: {UI["accent_2"]};
        --shadow: {UI["shadow"]};
    }}

    html, body, [class*="css"] {{
        font-family: 'Manrope', sans-serif !important;
    }}

    .stApp {{
        background: var(--app-bg) !important;
        color: var(--text);
    }}

    .block-container {{
        padding: 1rem 1.6rem 2.5rem 1.6rem !important;
        max-width: 1440px !important;
    }}

    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }}

    [data-testid="stSidebar"] * {{
        color: #f4f8fb !important;
    }}

    [data-testid="stSidebar"] .stRadio > div {{
        gap: 0.35rem;
    }}

    [data-testid="stSidebar"] .stRadio label {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        padding: 0.75rem 0.9rem !important;
        transition: 0.18s ease;
    }}

    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(255,255,255,0.10) !important;
        border-color: rgba(255,255,255,0.18) !important;
    }}

    [data-testid="stSidebar"] .stRadio label:has(input:checked) {{
        background:
            linear-gradient(135deg, rgba(125,211,252,0.22), rgba(56,189,248,0.10)) !important;
        border-color: rgba(125,211,252,0.48) !important;
        box-shadow: 0 10px 28px rgba(14,165,233,0.18) !important;
    }}

    [data-testid="stSidebar"] .stRadio label:has(input:checked) p {{
        font-weight: 800 !important;
        color: #ffffff !important;
    }}

    .sidebar-step {{
        margin: 0.9rem 0 0.5rem 0;
        padding: 0.55rem 0.75rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        font-size: 0.78rem;
        font-weight: 800;
        color: rgba(255,255,255,0.72);
    }}

    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.08);
        color: #ffffff;
        font-weight: 700;
        min-height: 2.8rem;
    }}

    [data-testid="stSidebarCollapseButton"] {{
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        border-radius: 999px !important;
        background: rgba(255,255,255,0.08) !important;
    }}

    .panel {{
        background:
            linear-gradient(135deg, rgba(255,255,255,0.065), rgba(255,255,255,0.018)),
            var(--panel);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 24px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
    }}

    .hero {{
        padding: 1.55rem 1.7rem 1.45rem 1.7rem;
        overflow: hidden;
        position: relative;
        margin-bottom: 1rem;
        border-radius: 20px;
    }}

    .hero::after {{
        content: "";
        position: absolute;
        inset: auto -80px -80px auto;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.16), rgba(255,255,255,0));
        filter: blur(8px);
    }}

    .eyebrow {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0;
        color: var(--muted);
        font-weight: 800;
        margin-bottom: 0.55rem;
    }}

    .hero-title {{
        font-size: clamp(1.85rem, 3vw, 2.75rem);
        line-height: 1.08;
        font-weight: 800;
        margin: 0;
        color: var(--text);
        letter-spacing: 0;
    }}

    .hero-copy {{
        max-width: 900px;
        margin-top: 0.65rem;
        color: var(--muted);
        font-size: 0.98rem;
        line-height: 1.6;
    }}

    .chip {{
        display: inline-block;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        margin-right: 0.45rem;
        margin-top: 0.6rem;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid var(--panel-border);
        background: """
    + UI["tag_bg"]
    + """;
        color: var(--text);
    }}

    .section-title {{
        color: var(--text);
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: 0;
        margin: 0.15rem 0 0 0;
    }}

    .section-kicker {{
        color: var(--accent);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0;
        font-weight: 800;
        margin-top: 1.35rem;
        padding-left: 0.8rem;
        border-left: 4px solid var(--accent);
    }}

    .section-box {{
        margin: 1.35rem 0 1rem 0;
        padding: 1rem 1.15rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.13);
        background:
            radial-gradient(circle at top right, rgba(125,211,252,0.11), transparent 36%),
            linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.025)),
            var(--panel);
        box-shadow: var(--shadow);
    }}

    .section-box .section-kicker {{
        margin-top: 0;
    }}

    .stat-card {{
        background:
            radial-gradient(circle at top right, rgba(125,211,252,0.16), transparent 34%),
            linear-gradient(145deg, rgba(255,255,255,0.105), rgba(255,255,255,0.035)),
            var(--panel-soft);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 20px;
        padding: 1.05rem 1.05rem 1rem 1.05rem;
        min-height: 128px;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        margin-bottom: 0.95rem;
    }}

    .stat-card::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
    }}

    .stat-value {{
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 0.65rem;
        color: var(--text);
    }}

    .stat-label {{
        color: var(--muted);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0;
        font-weight: 800;
    }}

    .stat-accent {{
        width: 54px;
        height: 4px;
        border-radius: 999px;
        margin-bottom: 0.7rem;
        box-shadow: 0 0 20px currentColor;
    }}

    .chart-shell {{
        background:
            linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.025)),
            var(--panel);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 24px;
        padding: 1.25rem;
        margin-bottom: 1.15rem;
        box-shadow: var(--shadow);
        overflow: hidden;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid rgba(255,255,255,0.16) !important;
        border-radius: 24px !important;
        background:
            radial-gradient(circle at top right, rgba(125,211,252,0.16), transparent 30%),
            linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.026)),
            var(--panel) !important;
        box-shadow: 0 22px 48px rgba(0,0,0,0.34) !important;
        padding: 0.25rem !important;
        margin-bottom: 1rem !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background: transparent !important;
    }}

    .chart-head {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid var(--panel-border);
    }}

    .boxed-chart-head {{
        margin-bottom: 0.8rem;
    }}

    .chart-title {{
        color: var(--text);
        font-weight: 800;
        font-size: 1.05rem;
        margin: 0;
    }}

    .chart-copy {{
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0.45rem 0 0 0;
        max-width: 900px;
    }}

    .chart-badge {{
        white-space: nowrap;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        border: 1px solid var(--panel-border);
        background: rgba(255,255,255,0.05);
        color: var(--text);
        font-size: 0.72rem;
        font-weight: 800;
    }}

    .chart-media {{
        border-radius: 18px;
        overflow: hidden;
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--panel-border);
    }}

    .chart-shell [data-testid="stImage"] img {{
        border-radius: 18px;
    }}

    .stMetric {{
        background:
            linear-gradient(145deg, rgba(255,255,255,0.095), rgba(255,255,255,0.035)),
            var(--panel-soft);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        box-shadow: var(--shadow);
    }}

    .insight {{
        border-radius: 18px;
        padding: 1.05rem 1.15rem;
        margin: 0.4rem 0 1.2rem 0;
        border: 1px solid rgba(125,211,252,0.18);
        background:
            radial-gradient(circle at top left, rgba(125,211,252,0.12), transparent 32%),
            linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.022)),
            var(--panel);
        color: var(--text);
        line-height: 1.7;
        box-shadow: var(--shadow);
    }}

    .insight b {{
        color: var(--accent);
    }}

    .empty-chart {{
        border: 1px dashed var(--panel-border);
        border-radius: 18px;
        background: rgba(255,255,255,0.03);
        color: var(--muted);
        padding: 3rem 1rem;
        text-align: center;
    }}

    .project-card {{
        border-radius: 24px;
        padding: 1.35rem;
        border: 1px solid var(--panel-border);
        box-shadow: var(--shadow);
    }}

    footer {{
        visibility: hidden !important;
    }}

    .stDeployButton {{
        display: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_hero(title: str, copy: str, chips: list[str], background: str):
    chips_html = "".join([f"<span class='chip'>{item}</span>" for item in chips])
    st.markdown(
        f"""
        <div class="panel hero" style="background:{background};">
            <div class="eyebrow">India Weather Extremes</div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-copy">{copy}</p>
            <div>{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(value, label: str, accent: str):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-accent" style="background:{accent};"></div>
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(kicker: str, title: str):
    st.markdown(
        f"""
        <div class="section-box">
            <div class="section-kicker">{kicker}</div>
            <div class="section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_chart(title: str, badge: str, description: str, filename: str | None = None, renderer=None):
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="chart-head boxed-chart-head">
                <div>
                    <p class="chart-title">{title}</p>
                    <p class="chart-copy">{description}</p>
                </div>
                <div class="chart-badge">{badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        image = load_image(chart_path(filename)) if filename else None
        if renderer is not None:
            st.markdown('<div class="chart-media">', unsafe_allow_html=True)
            renderer()
            st.markdown("</div>", unsafe_allow_html=True)
        elif image is not None:
            st.markdown('<div class="chart-media">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"""
                <div class="empty-chart">
                    <div style="font-size:1.2rem;font-weight:800;margin-bottom:0.4rem;">Chart image not found</div>
                    <div>Expected file: <code>{filename or "chart image"}</code> inside the <code>CHARTS/</code> folder.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def insight(text: str):
    st.markdown(f"<div class='insight'><b>Insight.</b> {text}</div>", unsafe_allow_html=True)


def data_notice(filename: str):
    if (ROOT / filename).exists():
        return
    st.markdown(
        f"""
        <div class="insight" style="border-color:rgba(251,146,60,0.35);background:linear-gradient(135deg,rgba(251,146,60,0.10),rgba(255,255,255,0.025));">
            <b>Dataset file missing.</b> Add <code>{filename}</code> to the project folder to show real KPIs and charts.
            The current values are lightweight placeholder rows so the layout can still render.
        </div>
        """,
        unsafe_allow_html=True,
    )


def native_category_chart(df, column, color):
    if column not in df or df.empty:
        st.info("No category data available for this chart.")
        return
    chart_df = df[column].fillna("Unknown").value_counts().reset_index()
    chart_df.columns = [column, "records"]
    chart = (
        alt.Chart(chart_df)
        .mark_arc(innerRadius=64, outerRadius=118, stroke="#0b1621", strokeWidth=2)
        .encode(
            theta=alt.Theta("records:Q"),
            color=alt.Color(f"{column}:N", legend=alt.Legend(title=None), scale=alt.Scale(scheme=color)),
            tooltip=[alt.Tooltip(f"{column}:N", title="Category"), alt.Tooltip("records:Q", title="Records")],
        )
        .properties(height=330)
    )
    labels = (
        alt.Chart(chart_df)
        .mark_text(radius=148, size=12, fontWeight="bold")
        .encode(theta="records:Q", text="records:Q", color=alt.value(UI["text"]))
    )
    st.altair_chart(chart + labels, use_container_width=True)


def native_bar_chart(df, column, color_value):
    if column not in df or df.empty:
        st.info("No data available for this chart.")
        return
    chart_df = df[column].fillna("Unknown").value_counts().head(15).reset_index()
    chart_df.columns = [column, "records"]
    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopRight=7, cornerRadiusBottomRight=7, color=color_value)
        .encode(
            y=alt.Y(f"{column}:N", sort="-x", title=None),
            x=alt.X("records:Q", title="Records"),
            tooltip=[alt.Tooltip(f"{column}:N", title=column.replace("_", " ").title()), "records:Q"],
        )
        .properties(height=max(260, len(chart_df) * 30))
    )
    st.altair_chart(chart, use_container_width=True)


def native_month_chart(df, month_column, value_column, color_value):
    if month_column not in df or value_column not in df or df.empty:
        st.info("No monthly data available for this chart.")
        return
    chart_df = df.groupby(month_column, as_index=False)[value_column].mean().sort_values(month_column)
    chart = (
        alt.Chart(chart_df)
        .mark_area(
            line={"color": color_value, "strokeWidth": 3},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color=color_value, offset=0),
                    alt.GradientStop(color="rgba(255,255,255,0.02)", offset=1),
                ],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
            interpolate="monotone",
        )
        .encode(
            x=alt.X(f"{month_column}:O", title="Month"),
            y=alt.Y(f"{value_column}:Q", title=value_column.replace("_", " ").title()),
            tooltip=[month_column, alt.Tooltip(f"{value_column}:Q", format=".1f")],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def get_support(transactions, itemset, n):
    return sum(1 for transaction in transactions if itemset.issubset(transaction)) / n


def make_rules(all_freq, transactions, min_conf):
    n = len(transactions)
    rules = []
    for itemset, supp in all_freq.items():
        if len(itemset) < 2:
            continue
        for size in range(1, len(itemset)):
            for ant_tuple in combinations(sorted(itemset), size):
                antecedent = frozenset(ant_tuple)
                consequent = itemset - antecedent
                ant_supp = all_freq.get(antecedent, get_support(transactions, antecedent, n))
                con_supp = all_freq.get(consequent, get_support(transactions, consequent, n))
                if ant_supp == 0 or con_supp == 0:
                    continue
                confidence = supp / ant_supp
                if confidence >= min_conf:
                    lift = confidence / con_supp
                    leverage = supp - ant_supp * con_supp
                    conviction = (1 - con_supp) / (1 - confidence) if confidence < 1 else 99.9
                    rules.append(
                        {
                            "antecedent": " + ".join(sorted(antecedent)),
                            "consequent": " + ".join(sorted(consequent)),
                            "support": round(supp, 4),
                            "confidence": round(confidence, 4),
                            "lift": round(lift, 4),
                            "leverage": round(leverage, 4),
                            "conviction": round(min(conviction, 99.9), 4),
                        }
                    )
    if not rules:
        return pd.DataFrame()
    return (
        pd.DataFrame(rules)
        .sort_values(["lift", "confidence", "support"], ascending=False)
        .drop_duplicates(subset=["antecedent", "consequent"])
        .reset_index(drop=True)
    )


def frequent_items_frame(all_freq):
    if not all_freq:
        return pd.DataFrame()
    return pd.DataFrame(
        [{"itemset": " + ".join(sorted(items)), "support": supp, "size": len(items)} for items, supp in all_freq.items()]
    ).sort_values(["support", "size"], ascending=[False, True])


def run_apriori(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    all_items = set(item for transaction in transactions for item in transaction)
    current = []
    all_freq = {}

    for item in all_items:
        itemset = frozenset([item])
        support = get_support(transactions, itemset, n)
        if support >= min_sup:
            all_freq[itemset] = round(support, 4)
            current.append(itemset)

    for length in range(2, max_len + 1):
        candidates = set()
        for left in range(len(current)):
            for right in range(left + 1, len(current)):
                union = current[left] | current[right]
                if len(union) == length:
                    candidates.add(union)
        next_level = []
        for candidate in candidates:
            support = get_support(transactions, candidate, n)
            if support >= min_sup:
                all_freq[candidate] = round(support, 4)
                next_level.append(candidate)
        if not next_level:
            break
        current = next_level

    return make_rules(all_freq, transactions, min_conf), frequent_items_frame(all_freq), all_freq


def run_eclat(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    min_count = max(1, int(np.ceil(min_sup * n)))
    tidlists = defaultdict(set)
    for tid, transaction in enumerate(transactions):
        for item in transaction:
            tidlists[frozenset([item])].add(tid)

    current = {itemset: tids for itemset, tids in tidlists.items() if len(tids) >= min_count}
    all_tidlists = dict(current)
    all_freq = {itemset: round(len(tids) / n, 4) for itemset, tids in current.items()}

    for length in range(2, max_len + 1):
        items = list(current.items())
        next_level = {}
        for left in range(len(items)):
            for right in range(left + 1, len(items)):
                union = items[left][0] | items[right][0]
                if len(union) == length:
                    tids = items[left][1] & items[right][1]
                    if len(tids) >= min_count:
                        next_level[union] = tids
        if not next_level:
            break
        all_tidlists.update(next_level)
        all_freq.update({itemset: round(len(tids) / n, 4) for itemset, tids in next_level.items()})
        current = next_level

    return make_rules(all_freq, transactions, min_conf), frequent_items_frame(all_freq), all_freq


class FPNode:
    def __init__(self, item, count=0, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}


class FPTree:
    def __init__(self):
        self.root = FPNode(None)
        self.headers = defaultdict(list)

    def insert(self, transaction, count=1):
        node = self.root
        for item in transaction:
            if item not in node.children:
                node.children[item] = FPNode(item, 0, node)
                self.headers[item].append(node.children[item])
            node = node.children[item]
            node.count += count

    def prefix_paths(self, item):
        paths = []
        for node in self.headers[item]:
            path = []
            parent = node.parent
            while parent and parent.item is not None:
                path.append(parent.item)
                parent = parent.parent
            if path:
                paths.append((list(reversed(path)), node.count))
        return paths


def run_fpgrowth(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    min_count = max(1, int(np.ceil(min_sup * n)))
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1

    frequent_1 = {item: count for item, count in item_counts.items() if count >= min_count}
    if not frequent_1:
        return pd.DataFrame(), pd.DataFrame(), {}

    order = sorted(frequent_1, key=lambda item: (-frequent_1[item], item))
    rank = {item: idx for idx, item in enumerate(order)}
    tree = FPTree()
    for transaction in transactions:
        filtered = sorted([item for item in transaction if item in frequent_1], key=lambda item: rank[item])
        if filtered:
            tree.insert(filtered)

    all_freq = {frozenset([item]): round(count / n, 4) for item, count in frequent_1.items()}

    def mine(base_item, prefix):
        conditional_counts = defaultdict(int)
        for path, count in tree.prefix_paths(base_item):
            for item in path:
                conditional_counts[item] += count
        for item, count in conditional_counts.items():
            if count >= min_count:
                new_itemset = prefix | frozenset([item])
                if len(new_itemset) <= max_len:
                    all_freq[new_itemset] = max(all_freq.get(new_itemset, 0), round(count / n, 4))
                    if len(new_itemset) < max_len:
                        mine(item, new_itemset)

    for item in frequent_1:
        mine(item, frozenset([item]))

    return make_rules(all_freq, transactions, min_conf), frequent_items_frame(all_freq), all_freq


@st.cache_data
def load_mining_data():
    def read_csv_or_empty(filename):
        path = ROOT / filename
        return pd.read_csv(path) if path.exists() else pd.DataFrame()

    return {
        "Cyclone": read_csv_or_empty("cyclone.csv"),
        "Heatwave / Coldwave": read_csv_or_empty("heatcold.csv"),
        "Air Quality Index": read_csv_or_empty("10_air_quality_index_2015_2023.csv"),
        "Rainfall": read_csv_or_empty("02_monthly_rainfall_district_1901_2023.csv"),
    }


def safe_value(row, column, default=None):
    return row[column] if column in row and pd.notna(row[column]) else default


def build_cyclone_transactions(df):
    transactions = []
    for _, row in df.iterrows():
        month = int(safe_value(row, "month", 0) or 0)
        items = {
            f"basin={str(safe_value(row, 'basin', 'Unknown')).replace(' ', '_')}",
            f"cat={str(safe_value(row, 'category', 'Unknown')).split()[0]}",
            f"landfall={'Yes' if bool(safe_value(row, 'landfall', False)) else 'No'}",
            f"season={'PostMonsoon' if month in [10, 11, 12] else ('PreMonsoon' if month in [4, 5, 6] else 'Other')}",
            f"wind={'High(>150kmh)' if float(safe_value(row, 'max_wind_kmh', 0) or 0) > 150 else 'Low(<=150kmh)'}",
            f"deaths={'Fatal(>100)' if float(safe_value(row, 'deaths', 0) or 0) > 100 else 'Low(<=100)'}",
            f"surge={'High(>3m)' if float(safe_value(row, 'surge_m', 0) or 0) > 3 else 'Low(<=3m)'}",
        }
        transactions.append(frozenset(items))
    return transactions


def build_heatwave_transactions(df):
    transactions = []
    for _, row in df.iterrows():
        state = str(safe_value(row, "state", "Unknown"))
        items = {
            f"type={safe_value(row, 'event_type', 'Unknown')}",
            f"severity={safe_value(row, 'severity', 'Unknown')}",
            f"alert={safe_value(row, 'imd_alert', 'Unknown')}",
            f"duration={'Long(>5d)' if float(safe_value(row, 'duration_days', 0) or 0) > 5 else 'Short(<=5d)'}",
            f"deaths={'Fatal(>50)' if float(safe_value(row, 'estimated_deaths', 0) or 0) > 50 else 'Low(<=50)'}",
            f"region={'North' if state in ['Delhi', 'Rajasthan', 'Punjab', 'Haryana', 'UP', 'Uttar Pradesh'] else 'Other'}",
        }
        transactions.append(frozenset(items))
    return transactions


def build_aqi_transactions(df, sample_n=5000):
    sample = df.sample(min(sample_n, len(df)), random_state=42) if len(df) > sample_n else df
    transactions = []
    for _, row in sample.iterrows():
        month = int(safe_value(row, "month", 0) or 0)
        aqi = float(safe_value(row, "aqi", 0) or 0)
        items = {
            f"zone={safe_value(row, 'zone', 'Unknown')}",
            f"cat={safe_value(row, 'category', 'Unknown')}",
            f"pollutant={safe_value(row, 'dominant_pollutant', 'Unknown')}",
            f"season={'Winter' if month in [11, 12, 1, 2] else ('Monsoon' if month in [6, 7, 8, 9] else 'Dry')}",
            f"pm25={'High(>60)' if float(safe_value(row, 'pm25_ugm3', 0) or 0) > 60 else 'Low(<=60)'}",
            f"aqi_band={'Severe' if aqi > 300 else ('Poor' if aqi > 200 else 'Moderate_Good')}",
        }
        transactions.append(frozenset(items))
    return transactions


def build_rainfall_transactions(df, sample_n=3000):
    sample = df.sample(min(sample_n, len(df)), random_state=42) if len(df) > sample_n else df
    transactions = []
    for _, row in sample.iterrows():
        month = int(safe_value(row, "month_num", safe_value(row, "month", 0)) or 0)
        departure = float(safe_value(row, "departure_pct", 0) or 0)
        zone = str(safe_value(row, "agro_zone", "Unknown")).replace(" ", "_").replace("-", "_")
        items = {
            f"zone={zone}",
            f"cat={safe_value(row, 'category', 'Unknown')}",
            f"season={'Monsoon' if month in [6, 7, 8, 9] else ('Winter' if month in [11, 12, 1, 2] else 'Dry')}",
            f"depart={'Excess' if departure > 20 else ('Deficit' if departure < -20 else 'Normal')}",
            f"rain_level={'Heavy(>150mm)' if float(safe_value(row, 'rainfall_mm', 0) or 0) > 150 else 'Low(<=150mm)'}",
        }
        transactions.append(frozenset(items))
    return transactions


def build_transactions(dataset_name, data_map):
    df = data_map.get(dataset_name, pd.DataFrame())
    if df.empty:
        return []
    if dataset_name == "Cyclone":
        return build_cyclone_transactions(df)
    if dataset_name == "Heatwave / Coldwave":
        return build_heatwave_transactions(df)
    if dataset_name == "Air Quality Index":
        return build_aqi_transactions(df)
    return build_rainfall_transactions(df)


@st.cache_data
def run_mining_cached(dataset_name, algorithm, min_sup, min_conf, max_len, _transactions):
    start = time.time()
    if algorithm == "Apriori":
        rules, freq, _ = run_apriori(_transactions, min_sup, min_conf, max_len)
    elif algorithm == "ECLAT":
        rules, freq, _ = run_eclat(_transactions, min_sup, min_conf, max_len)
    else:
        rules, freq, _ = run_fpgrowth(_transactions, min_sup, min_conf, max_len)
    return rules, freq, round(time.time() - start, 3)


def render_rules_table(df, max_rows=20):
    if df.empty:
        st.warning("No rules found. Lower min support or min confidence to widen the search.")
        return
    display = df.head(max_rows).copy()
    st.dataframe(
        display[["antecedent", "consequent", "support", "confidence", "lift", "leverage"]],
        use_container_width=True,
        hide_index=True,
    )


def render_frequent_items(freq_df, top_n=15):
    if freq_df.empty:
        st.info("No frequent itemsets found for the current thresholds.")
        return
    for _, row in freq_df.head(top_n).iterrows():
        pct = min(100, int(row["support"] * 100))
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.55rem;">
                <div style="flex:1;color:{UI["text"]};font-size:0.86rem;">{row["itemset"]}</div>
                <div style="width:140px;height:10px;border-radius:999px;background:rgba(255,255,255,0.08);overflow:hidden;">
                    <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{UI["accent"]},{UI["accent_2"]});"></div>
                </div>
                <div style="width:48px;text-align:right;color:{UI["accent"]};font-weight:800;font-size:0.82rem;">{pct}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


DASHBOARD_OPTIONS = [
    "Cyclone Analysis",
    "Heatwave / Coldwave Analysis",
    "Air Quality Analysis",
    "Rainfall Analysis",
    "Association Mining",
]

DASHBOARD_LABELS = {
    "Cyclone Analysis": "Cyclone Analysis",
    "Heatwave / Coldwave Analysis": "Heatwave / Coldwave",
    "Air Quality Analysis": "Air Quality Index",
    "Rainfall Analysis": "Rainfall Analysis",
    "Association Mining": "Association Mining",
}

SECTION_OPTIONS = {
    "Cyclone Analysis": [
        "Overview",
        "Temporal Patterns",
        "Intensity Analysis",
        "Impact & Damage",
        "Geographic Patterns",
        "Correlations",
    ],
    "Heatwave / Coldwave Analysis": [
        "Overview",
        "Temporal Patterns",
        "Temperature Analysis",
        "Impact & Deaths",
        "State-wise Patterns",
        "Correlations",
    ],
    "Air Quality Analysis": [
        "Overview",
        "Annual & Seasonal Trends",
        "Pollutant Analysis",
        "Station & Geography",
        "Correlations",
    ],
    "Rainfall Analysis": [
        "Overview",
        "Annual & Seasonal Trends",
        "Category & Departure",
        "State & Zone Patterns",
        "Correlations",
    ],
}


def section_label(name: str) -> str:
    icons = {
        "Overview": "Overview",
        "Temporal Patterns": "Temporal Patterns",
        "Intensity Analysis": "Intensity Analysis",
        "Impact & Damage": "Impact & Damage",
        "Geographic Patterns": "Geographic Patterns",
        "Correlations": "Correlations",
        "Temperature Analysis": "Temperature Analysis",
        "Impact & Deaths": "Impact & Deaths",
        "State-wise Patterns": "State-wise Patterns",
        "Annual & Seasonal Trends": "Annual & Seasonal Trends",
        "Pollutant Analysis": "Pollutant Analysis",
        "Station & Geography": "Station & Geography",
        "Category & Departure": "Category & Departure",
        "State & Zone Patterns": "State & Zone Patterns",
    }
    return icons.get(name, name)


with st.sidebar:
    st.markdown(
        """
        <div style="padding:0.4rem 0 1.1rem 0;">
            <div style="font-size:0.74rem;text-transform:uppercase;letter-spacing:0;color:rgba(255,255,255,0.55);font-weight:800;">India Weather Extremes</div>
            <div style="font-size:1.55rem;font-weight:800;line-height:1.1;margin-top:0.45rem;">Climate Risk Dashboard</div>
            <div style="font-size:0.92rem;color:rgba(255,255,255,0.7);margin-top:0.55rem;line-height:1.7;">
                One project: EDA dashboards plus association-rule mining.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Switch Theme"):
        st.session_state.theme = "paper" if IS_STORM else "storm"
        st.rerun()

    st.markdown('<div class="sidebar-step">1. Choose dashboard</div>', unsafe_allow_html=True)

    dataset = st.radio(
        "Choose dashboard",
        DASHBOARD_OPTIONS,
        format_func=lambda value: DASHBOARD_LABELS[value],
        label_visibility="collapsed",
        key="dashboard_choice",
    )

    if st.session_state.get("previous_dashboard") != dataset:
        st.session_state["previous_dashboard"] = dataset
        if dataset in SECTION_OPTIONS:
            st.session_state[f"section_choice_{dataset}"] = "Overview"

    if dataset in SECTION_OPTIONS:
        st.markdown('<div class="sidebar-step">2. Open section</div>', unsafe_allow_html=True)
        section = st.radio(
            "Open section",
            SECTION_OPTIONS[dataset],
            format_func=section_label,
            label_visibility="collapsed",
            key=f"section_choice_{dataset}",
        )

    if dataset == "Cyclone Analysis":
        st.markdown(
            """
            <div style="margin-top:1rem;padding:0.95rem;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);">
                <div style="font-size:0.74rem;text-transform:uppercase;letter-spacing:0;color:rgba(255,255,255,0.58);font-weight:800;">Dataset Snapshot</div>
                <div style="margin-top:0.55rem;line-height:1.8;font-size:0.9rem;">
                    103 cyclone events<br>
                    1990 to 2023<br>
                    15 chart outputs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif dataset == "Heatwave / Coldwave Analysis":
        st.markdown(
            """
            <div style="margin-top:1rem;padding:0.95rem;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);">
                <div style="font-size:0.74rem;text-transform:uppercase;letter-spacing:0;color:rgba(255,255,255,0.58);font-weight:800;">Dataset Snapshot</div>
                <div style="margin-top:0.55rem;line-height:1.8;font-size:0.9rem;">
                    613 temperature events<br>
                    1980 to 2023<br>
                    15 chart outputs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif dataset == "Air Quality Analysis":
        st.markdown(
            """
            <div style="margin-top:1rem;padding:0.95rem;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);">
                <div style="font-size:0.74rem;text-transform:uppercase;letter-spacing:0;color:rgba(255,255,255,0.58);font-weight:800;">Dataset Snapshot</div>
                <div style="margin-top:0.55rem;line-height:1.8;font-size:0.9rem;">
                    AQI readings<br>
                    2015 to 2023<br>
                    12 chart outputs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif dataset == "Rainfall Analysis":
        st.markdown(
            """
            <div style="margin-top:1rem;padding:0.95rem;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);">
                <div style="font-size:0.74rem;text-transform:uppercase;letter-spacing:0;color:rgba(255,255,255,0.58);font-weight:800;">Dataset Snapshot</div>
                <div style="margin-top:0.55rem;line-height:1.8;font-size:0.9rem;">
                    Monthly district rainfall<br>
                    1901 to 2023<br>
                    15 chart outputs
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="sidebar-step">2. Select mining data</div>', unsafe_allow_html=True)
        mining_dataset = st.radio(
            "Mining Dataset",
            ["Cyclone", "Heatwave / Coldwave", "Air Quality Index", "Rainfall"],
            label_visibility="collapsed",
        )
        st.markdown('<div class="sidebar-step">3. Tune thresholds</div>', unsafe_allow_html=True)
        min_sup = st.slider("Min Support", 0.05, 0.50, 0.10, 0.01)
        min_conf = st.slider("Min Confidence", 0.20, 0.95, 0.40, 0.05)
        max_len = st.slider("Max Itemset Length", 2, 4, 3, 1)
        st.markdown('<div class="sidebar-step">4. Run algorithm</div>', unsafe_allow_html=True)
        mining_algorithm = st.radio(
            "Algorithm",
            ["Apriori", "ECLAT", "FP-Growth", "Compare All Three"],
            label_visibility="collapsed",
        )
        st.markdown(
            """
            <div style="margin-top:1rem;padding:0.95rem;border-radius:18px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);font-size:0.88rem;line-height:1.7;">
                Apriori uses candidate pruning.<br>
                ECLAT uses vertical TID lists.<br>
                FP-Growth uses a compact prefix tree.
            </div>
            """,
            unsafe_allow_html=True,
        )

if dataset == "Cyclone Analysis":
    render_hero(
        "Cyclone Risk Intelligence",
        "A focused view of Indian Ocean cyclone behavior across time, intensity, geography, and impact. The layout is structured for presentation: quick metrics first, then visual evidence section by section.",
        ["1990-2023", "103 cyclone records", "Bay of Bengal + Arabian Sea", "15 visual outputs"],
        UI["hero_cyclone"],
    )

    total_deaths = int(cyc["deaths"].sum()) if "deaths" in cyc else 0
    max_wind = cyc["max_wind_kmh"].max() if "max_wind_kmh" in cyc else 0
    total_damage = int(cyc["damage_crore_inr"].sum()) if "damage_crore_inr" in cyc else 0
    landfall_rate = round(cyc["landfall"].sum() / len(cyc) * 100, 1) if len(cyc) and "landfall" in cyc else 0
    super_count = int((cyc["category"] == "Super Cyclonic Storm").sum()) if "category" in cyc else 0

    cols = st.columns(5)
    with cols[0]:
        stat_card(len(cyc), "Total Cyclones", UI["cyclone"])
    with cols[1]:
        stat_card(f"{total_deaths:,}", "Deaths", UI["danger"])
    with cols[2]:
        stat_card(max_wind, "Max Wind km/h", UI["accent"])
    with cols[3]:
        stat_card(f"₹{total_damage:,}", "Damage Crore", UI["cyclone"])
    with cols[4]:
        stat_card(f"{landfall_rate}% | {super_count}", "Landfall | Super", UI["accent_2"])

    if section == "Overview":
        section_heading("Cyclone Analysis", "Category distribution and baseline project context")
        show_chart(
            "Cyclone Category Distribution",
            "Count Plot",
            "This is the baseline read on the dataset: which intensity classes dominate the record, and whether the distribution is skewed toward more dangerous storm types.",
            "01_category_distribution.png",
        )
        insight("The category mix already tells a story: upper-end cyclone classes occupy a large share of the dataset, which makes this project feel closer to risk analysis than simple weather summarization.")

    elif section == "Temporal Patterns":
        section_heading("Cyclone Analysis", "When cyclones cluster across years and seasons")
        col1, col2 = st.columns([1.45, 1], gap="large")
        with col1:
            show_chart(
                "Annual Cyclone Frequency",
                "Line + Area",
                "Use this as the big-picture temporal trend chart. It surfaces active years quickly and gives the dashboard a strong narrative anchor.",
                "02_yearly_frequency.png",
            )
        with col2:
            show_chart(
                "Monthly Seasonality",
                "Polar Chart",
                "The radial presentation works well here because seasonality is cyclical. It makes the peak cyclone months feel immediate instead of tucked inside a bar chart.",
                "03_monthly_polar.png",
            )
        show_chart(
            "Year by Month Activity Heatmap",
            "Heatmap",
            "This chart pinpoints exactly where dense activity clusters appear across the historical timeline and helps connect anomalous years to specific months.",
            "06_heatmap_year_month.png",
        )
        insight("This section now reads more cleanly as a sequence: annual trend, seasonal rhythm, then high-resolution year-month concentration.")

    elif section == "Intensity Analysis":
        section_heading("Cyclone Analysis", "How storm intensity behaves across variables")
        show_chart(
            "Wind Speed Distribution by Category",
            "Violin + Strip",
            "This view gives the clearest distributional feel for wind speed by category. It is one of the most valuable charts in the whole cyclone module.",
            "04_wind_violin.png",
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Wind Speed vs Pressure",
                "Scatter + Regression",
                "A clean relationship chart that helps the audience immediately understand how stronger storms align with lower pressure systems.",
                "10_wind_pressure_scatter.png",
            )
        with col2:
            show_chart(
                "Duration vs Track Length",
                "Hexbin Density",
                "This adds movement behavior into the intensity conversation and broadens the analysis beyond a single wind-speed dimension.",
                "13_duration_track_hexbin.png",
            )
        insight("The intensity section now feels less cramped and more analytical: one distribution chart followed by two relationship charts.")

    elif section == "Impact & Damage":
        section_heading("Cyclone Analysis", "Human and economic cost")
        show_chart(
            "Deaths vs Economic Damage",
            "Bubble Scatter",
            "This works as the anchor chart for impact because it combines human cost, financial cost, and severity in one visual frame.",
            "05_deaths_damage_scatter.png",
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Top 10 Deadliest Cyclones",
                "Ranked Bar",
                "A straightforward ranking view is useful here because it highlights historical outliers immediately and supports presentation-style storytelling.",
                "08_top10_deadliest.png",
            )
        with col2:
            show_chart(
                "Storm Surge Distribution",
                "Histogram + KDE",
                "This gives a good explanatory layer for why some cyclone events become so destructive and rounds out the impact section.",
                "12_surge_kde.png",
            )
        show_chart(
            "Decade-wise Economic Damage",
            "Box Plot",
            "This chart adds longer-term structure to the impact section and helps frame escalation in exposure over time.",
            "14_decade_damage_box.png",
        )
        insight("The impact page now has a more executive-dashboard rhythm: summary relationship, ranked outliers, mechanism view, and decade trend.")

    elif section == "Geographic Patterns":
        section_heading("Cyclone Analysis", "Where basin and landfall risk are concentrated")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Landfall Distribution by State",
                "Donut",
                "A quick geographic allocation view showing which coastal states repeatedly absorb cyclone landfall risk.",
                "11_landfall_donut.png",
            )
        with col2:
            show_chart(
                "Category Split by Basin",
                "Stacked Bar",
                "This is the important comparison chart for basin behavior and helps separate Bay of Bengal risk from Arabian Sea behavior.",
                "07_basin_category_stacked.png",
            )
        insight("Putting state exposure and basin composition side by side makes this module feel more like a decision dashboard than a notebook chapter.")

    elif section == "Correlations":
        section_heading("Cyclone Analysis", "Feature relationships and multivariate patterns")
        show_chart(
            "Correlation Matrix",
            "Heatmap",
            "A compact view of the strongest numerical relationships in the cyclone dataset and a good bridge toward any later predictive modeling work.",
            "09_correlation_heatmap.png",
        )
        show_chart(
            "Pairplot of Extreme Cyclone Indicators",
            "Pairplot",
            "This provides the fuller multivariate look and is especially useful for spotting basin-level clustering or variable separation.",
            "15_pairplot.png",
        )
        insight("This last section stays intentionally simple so the dashboard ends with analysis depth instead of visual clutter.")

elif dataset == "Heatwave / Coldwave Analysis":
    hw = hw_df[hw_df["event_type"] == "Heatwave"] if "event_type" in hw_df else pd.DataFrame()
    cw = hw_df[hw_df["event_type"] == "Coldwave"] if "event_type" in hw_df else pd.DataFrame()
    max_heat = hw["peak_temp_c"].max() if not hw.empty and "peak_temp_c" in hw else 0
    min_cold = cw["peak_temp_c"].min() if not cw.empty and "peak_temp_c" in cw else 0
    total_deaths = int(hw_df["estimated_deaths"].sum()) if "estimated_deaths" in hw_df else 0
    severe_events = int((hw_df["severity"] == "Severe").sum()) if "severity" in hw_df else 0
    red_alerts = int((hw_df["imd_alert"] == "Red").sum()) if "imd_alert" in hw_df else 0

    render_hero(
        "Heatwave and Coldwave Extremes",
        "A second analysis module focused on temperature-driven hazards across India. The page is structured to feel like part of the same project, with its own identity but the same dashboard system.",
        ["1980-2023", "613 events", "Heat + cold extremes", "15 visual outputs"],
        UI["hero_heat"],
    )

    cols = st.columns(5)
    with cols[0]:
        stat_card(len(hw_df), "Total Events", UI["heat"])
    with cols[1]:
        stat_card(f"{len(hw)} | {len(cw)}", "Heat | Cold", UI["cold"])
    with cols[2]:
        stat_card(f"{total_deaths:,}", "Deaths", UI["danger"])
    with cols[3]:
        stat_card(f"{max_heat}°C | {min_cold}°C", "Max Heat | Min Cold", UI["heat"])
    with cols[4]:
        stat_card(f"{severe_events} | {red_alerts}", "Severe | Red Alerts", UI["accent_2"])

    if section == "Overview":
        section_heading("Temperature Extremes", "Event mix and warning alignment")
        col1, col2 = st.columns([1, 1.45], gap="large")
        with col1:
            show_chart(
                "Heatwave vs Coldwave Split",
                "Donut",
                "A quick project-level orientation chart showing the balance between the two event types in the dataset.",
                "01_event_type_donut.png",
            )
        with col2:
            show_chart(
                "Severity vs IMD Alert Cross-tabulation",
                "Heatmap",
                "A useful operational chart that compares issued alert level with observed event severity and helps the analysis feel grounded in warning systems.",
                "09_severity_alert_heatmap.png",
            )
        insight("This overview page now acts like a proper module landing page: event composition on one side and alert-system framing on the other.")

    elif section == "Temporal Patterns":
        section_heading("Temperature Extremes", "Long-run timing and seasonality")
        show_chart(
            "Annual Heatwave and Coldwave Frequency",
            "Dual Line + Area",
            "The annual trend chart is the natural lead visual here because it establishes the broader climate signal before drilling into seasonality.",
            "02_yearly_frequency.png",
        )
        col1, col2 = st.columns([1.45, 1], gap="large")
        with col1:
            show_chart(
                "Year by Month Activity Heatmap",
                "Heatmap",
                "This chart shows the seasonal bands across decades and makes it easy to spot active windows and anomalous years.",
                "06_heatmap_year_month.png",
            )
        with col2:
            show_chart(
                "Monthly Seasonality",
                "Polar Chart",
                "The polar layout makes the opposing seasonality of heatwaves and coldwaves much more visually memorable.",
                "03_monthly_polar.png",
            )
        insight("The ordering here helps the reader move from macro trend to seasonal distribution to the exact year-month structure.")

    elif section == "Temperature Analysis":
        section_heading("Temperature Extremes", "Severity, anomalies, and duration")
        show_chart(
            "Peak Temperature Distribution by Severity",
            "Violin + Strip",
            "A strong distributional chart that shows how severe events sit relative to the broader event population for both heatwaves and coldwaves.",
            "04_temp_violin.png",
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Temperature Anomaly by Severity and Event Type",
                "Box Plot",
                "This chart adds interpretation beyond absolute temperature by focusing on deviation from normal conditions.",
                "10_anomaly_severity_box.png",
            )
        with col2:
            show_chart(
                "Event Duration Distribution",
                "Histogram + KDE",
                "Duration matters for stress accumulation, so this chart adds an important temporal exposure dimension to the module.",
                "11_duration_kde.png",
            )
        insight("This section now has a clearer analytical arc: distribution, anomaly framing, then duration behavior.")
    elif section == "Impact & Deaths":
        section_heading("Temperature Extremes", "Mortality burden and exposure")
        show_chart(
            "Deaths vs Temperature Anomaly",
            "Bubble Scatter",
            "This is the best anchor chart for impact because it combines lethality, abnormality, and duration in one place.",
            "05_deaths_anomaly_scatter.png",
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Top 10 Deadliest Events",
                "Ranked Bar",
                "A ranking chart makes the deadliest heatwave and coldwave events immediately legible to the audience.",
                "07_top10_deadliest.png",
            )
        with col2:
            show_chart(
                "Decade-wise Total Deaths",
                "Grouped Bar",
                "This view helps frame mortality shifts over time and adds historical structure to the impact narrative.",
                "12_decade_deaths_bar.png",
            )
        show_chart(
            "Districts Affected vs Deaths",
            "Hexbin",
            "A more nuanced relationship chart that helps show whether geographic spread translates directly into mortality.",
            "13_districts_deaths_hexbin.png",
        )
        insight("This section is now much easier to present: one main impact chart, two supporting comparisons, and one spread-vs-deaths relationship.")

    elif section == "State-wise Patterns":
        section_heading("Temperature Extremes", "Which states carry the event burden")
        show_chart(
            "Top 15 States for Heatwave and Coldwave Events",
            "Stacked Bar",
            "This chart works well on its own as the geographic module because it clearly compares total exposure and event-type mix by state.",
            "08_state_events_stacked.png",
        )
        insight("Keeping the state section intentionally focused gives it more impact and avoids overwhelming the page with too many competing geographic views.")

    elif section == "Correlations":
        section_heading("Temperature Extremes", "Numerical relationships and multivariate context")
        show_chart(
            "Correlation Matrix",
            "Heatmap",
            "A compact summary of feature coupling across the temperature-extremes dataset and a practical bridge toward modeling or feature selection.",
            "14_correlation_heatmap.png",
        )
        show_chart(
            "Pairplot of Key Indicators",
            "Pairplot",
            "This gives the broader multivariate picture and helps separate heatwave behavior from coldwave behavior across several dimensions.",
            "15_pairplot.png",
        )
        insight("The final section stays clean and technical, which is the right finish for a dashboard project like this.")


elif dataset == "Air Quality Analysis":
    total_records = f"{len(aqi_df):,}"
    stations = aqi_df["station"].nunique() if "station" in aqi_df else 0
    mean_aqi = round(aqi_df["aqi"].mean(), 1) if "aqi" in aqi_df else 0
    max_aqi = int(aqi_df["aqi"].max()) if "aqi" in aqi_df and len(aqi_df) else 0
    poor_pct = (
        round(aqi_df["category"].isin(["Poor", "Very Poor", "Severe"]).sum() / len(aqi_df) * 100, 1)
        if "category" in aqi_df and len(aqi_df)
        else 0
    )

    render_hero(
        "Air Quality Index Intelligence",
        "A focused AQI module for reading pollutant pressure, seasonal pollution cycles, monitoring-station differences, and category-level public health signals.",
        ["2015-2023", "AQI readings", "PM2.5 + PM10 + NO2", "12 visual outputs"],
        UI["hero_aqi"],
    )
    data_notice("10_air_quality_index_2015_2023.csv")

    cols = st.columns(5)
    with cols[0]:
        stat_card(total_records, "AQI Records", UI["accent"])
    with cols[1]:
        stat_card(stations, "Stations", UI["accent_2"])
    with cols[2]:
        stat_card(mean_aqi, "Mean AQI", UI["heat"])
    with cols[3]:
        stat_card(max_aqi, "Peak AQI", UI["danger"])
    with cols[4]:
        stat_card(f"{poor_pct}%", "Poor+ Days", UI["cold"])

    if section == "Overview":
        section_heading("Air Quality Analysis", "AQI category distribution and baseline burden")
        show_chart(
            "AQI Category Distribution",
            "Donut",
            "This overview chart shows how readings are distributed from Good to Severe and quickly establishes the chronic pollution baseline.",
            renderer=lambda: native_category_chart(aqi_df, "category", "greens"),
        )
        insight("The overview is the AQI module's landing page: it tells whether the dataset is dominated by clean days, moderate pollution, or public-health warning categories.")

    elif section == "Annual & Seasonal Trends":
        section_heading("Air Quality Analysis", "Long-run trend and seasonal pollution rhythm")
        col1, col2 = st.columns([1.45, 1], gap="large")
        with col1:
            show_chart(
                "Annual Average AQI Trend by Zone",
                "Line + Area",
                "This chart tracks the annual AQI signal by geographic zone and helps surface broad shifts such as lockdown-era drops or post-lockdown rebounds.",
                "02_annual_aqi_trend.png",
            )
        with col2:
            show_chart(
                "Monthly AQI Seasonality",
                "Polar Chart",
                "The polar chart makes the winter pollution spike and monsoon cleaning effect visually immediate.",
                renderer=lambda: native_month_chart(aqi_df, "month", "aqi", UI["accent"]),
            )
        show_chart(
            "Year by Month Mean AQI Heatmap",
            "Heatmap",
            "This chart reveals recurring winter bands, clean monsoon months, and unusually high or low pollution periods across years.",
            "06_year_month_heatmap.png",
        )
        insight("The temporal view is where AQI becomes environmental behavior rather than just a number: winter trapping, monsoon washout, and year-level disruption all show up together.")

    elif section == "Pollutant Analysis":
        section_heading("Air Quality Analysis", "Pollutants, categories, and AQI drivers")
        show_chart(
            "AQI Distribution by Category and Zone",
            "Violin + Strip",
            "This chart compares AQI spread across category and zone, showing whether certain regions consistently skew toward higher pollution.",
            "04_aqi_violin.png",
        )
        show_chart(
            "PM2.5 vs AQI",
            "Bubble Scatter",
            "A relationship chart for particulate pollution: PM2.5 tends to explain the high-AQI end of the dataset better than most other pollutants.",
            "05_pm25_aqi_bubble.png",
        )
        show_chart(
            "AQI Category vs Dominant Pollutant",
            "Cross-tab Heatmap",
            "This matrix connects AQI severity classes with the pollutants most often responsible for those conditions.",
            "09_category_pollutant_heatmap.png",
        )
        insight("This section is the diagnostic core of AQI analysis because it connects the AQI score to actual pollutant composition.")

    elif section == "Station & Geography":
        section_heading("Air Quality Analysis", "Station burden and state category mix")
        show_chart(
            "Top 15 Most Polluted Stations",
            "Ranked Bar",
            "A station-level ranking makes chronic pollution hotspots easier to identify than a broad state average.",
            renderer=lambda: native_bar_chart(aqi_df, "station", UI["accent"]),
        )
        show_chart(
            "State-wise AQI Category Breakdown",
            "Stacked Bar",
            "This chart compares how clean, moderate, and hazardous AQI categories distribute across states.",
            "08_state_category_stacked.png",
        )
        insight("Geographic AQI patterns are most useful when they name where intervention should happen, not just how polluted the average day is.")

    elif section == "Correlations":
        section_heading("Air Quality Analysis", "Pollutant distributions and numerical relationships")
        show_chart(
            "AQI Distribution by Year and Zone",
            "Grouped Boxplot",
            "This view captures the spread of AQI values by year and zone, not only the average trend.",
            "10_aqi_year_zone_box.png",
        )
        show_chart(
            "Pollutant Concentration Distribution",
            "KDE + Histogram",
            "Distribution curves reveal whether pollutant load is stable, skewed, or driven by rare high-concentration episodes.",
            "11_pollutant_kde.png",
        )
        show_chart(
            "Pollutant Correlation Matrix",
            "Correlation Heatmap",
            "This matrix summarizes which pollutants move with AQI and which behave independently or seasonally.",
            "12_pollutant_correlation.png",
        )
        insight("The correlation page is the bridge from EDA to modeling: it tells which pollutant signals are redundant, dominant, or worth treating separately.")


elif dataset == "Rainfall Analysis":
    total_records = f"{len(rain_df):,}"
    states = rain_df["state"].nunique() if "state" in rain_df else 0
    districts = rain_df["district"].nunique() if "district" in rain_df else 0
    mean_rain = round(rain_df["rainfall_mm"].mean(), 1) if "rainfall_mm" in rain_df else 0
    excess_pct = (
        round((rain_df["category"] == "Excess").sum() / len(rain_df) * 100, 1)
        if "category" in rain_df and len(rain_df)
        else 0
    )

    render_hero(
        "Monthly Rainfall Intelligence",
        "A rainfall module for exploring long-run monsoon variability, monthly departures, district/state exposure, and flood-versus-deficit patterns.",
        ["1901-2023", "Monthly records", "District rainfall", "15 visual outputs"],
        UI["hero_rain"],
    )
    data_notice("02_monthly_rainfall_district_1901_2023.csv")

    cols = st.columns(5)
    with cols[0]:
        stat_card(total_records, "Rainfall Records", UI["accent"])
    with cols[1]:
        stat_card(states, "States", UI["accent_2"])
    with cols[2]:
        stat_card(districts, "Districts", UI["cyclone"])
    with cols[3]:
        stat_card(f"{mean_rain} mm", "Mean Rainfall", UI["cold"])
    with cols[4]:
        stat_card(f"{excess_pct}%", "Excess Months", UI["heat"])

    if section == "Overview":
        section_heading("Rainfall Analysis", "Rainfall category distribution")
        show_chart(
            "Rainfall Category Split",
            "Donut",
            "This chart establishes how district-months divide across Excess, Normal, Deficient, and Scanty rainfall categories.",
            renderer=lambda: native_category_chart(rain_df, "category", "blues"),
        )
        insight("The category split is the right opening chart because it frames rainfall as both water availability and hazard risk.")

    elif section == "Annual & Seasonal Trends":
        section_heading("Rainfall Analysis", "Annual variability and monsoon seasonality")
        col1, col2 = st.columns([1.45, 1], gap="large")
        with col1:
            show_chart(
                "Annual Mean Monthly Rainfall",
                "Line + Area",
                "This long-run line chart is the rainfall module's historical anchor, showing how mean rainfall varies across decades.",
                "02_yearly_trend.png",
            )
        with col2:
            show_chart(
                "Monthly Rainfall Seasonality",
                "Polar Chart",
                "The polar view makes monsoon concentration obvious by showing the annual rainfall cycle as a calendar rhythm.",
                renderer=lambda: native_month_chart(rain_df, "month_num", "rainfall_mm", UI["accent_2"]),
            )
        show_chart(
            "Year by Month Mean Rainfall Heatmap",
            "Heatmap",
            "This heatmap shows drought-like rows, strong monsoon months, and unusual seasonal patterns across the historical timeline.",
            "06_heatmap_year_month.png",
        )
        insight("Rainfall is fundamentally seasonal, so this page moves from long-run annual variation into the exact monsoon months where most water arrives.")

    elif section == "Category & Departure":
        section_heading("Rainfall Analysis", "Rainfall category thresholds and departure behavior")
        show_chart(
            "Rainfall Distribution by Category",
            "Violin + Strip",
            "This chart shows how actual rainfall amounts spread within each IMD-style category.",
            "04_category_violin.png",
        )
        show_chart(
            "Departure Percentage vs Rainfall",
            "Bubble Scatter",
            "A relationship view for actual rainfall against percentage departure from normal, with rainy-day intensity encoded by bubble size.",
            "05_departure_scatter.png",
        )
        show_chart(
            "Departure Percentage by Month",
            "Grouped Boxplot",
            "Monthly boxes show which calendar months have the most volatile departures from normal.",
            "10_departure_month_box.png",
        )
        insight("Departure analysis is what turns rainfall from volume into anomaly: it reveals whether a month was unusual for that place and season.")

    elif section == "State & Zone Patterns":
        section_heading("Rainfall Analysis", "Where rainfall extremes concentrate")
        show_chart(
            "Top 10 Highest District Monthly Rainfall Records",
            "Ranked Bar",
            "This chart surfaces the most extreme district-month rainfall records and the states where they occurred.",
            "07_top10_rainfall.png",
        )
        show_chart(
            "Top 15 States by Rainfall Category Count",
            "Stacked Bar",
            "The stacked chart compares state exposure to Excess, Normal, Deficient, and Scanty records.",
            renderer=lambda: native_bar_chart(rain_df, "state", UI["accent_2"]),
        )
        show_chart(
            "Agro-zone vs Rainfall Category",
            "Cross-tab Heatmap",
            "This matrix connects rainfall categories with agro-ecological context, which is useful for drought and flood planning.",
            "09_agrozone_category_heatmap.png",
        )
        insight("The geography page gives rainfall consequences a location: flood exposure, deficit recurrence, and agro-zone sensitivity.")

    elif section == "Correlations":
        section_heading("Rainfall Analysis", "Distributions, decade shifts, and feature relationships")
        show_chart(
            "Rainy Days Distribution by Category",
            "KDE + Histogram",
            "This chart separates frequent low-rain months from high-rain months that may occur across fewer intense rainy days.",
            "11_rainy_days_kde.png",
        )
        show_chart(
            "Decade-wise Mean Monthly Rainfall by Agro-zone",
            "Grouped Bar",
            "This chart compares rainfall means across agro-zones over decades, making long-run shifts easier to read.",
            "12_decade_zone_bar.png",
        )
        col1, col2 = st.columns(2, gap="large")
        with col1:
            show_chart(
                "Departure Percentage vs Rainy Days",
                "Hexbin",
                "Hexbin density reveals the common center and rare extremes in departure-versus-rainy-days space.",
                "13_departure_rainydays_hexbin.png",
            )
        with col2:
            show_chart(
                "Rainfall Feature Correlation Matrix",
                "Correlation Heatmap",
                "This chart highlights redundant rainfall features and the strongest numerical relationships.",
                "14_correlation_heatmap.png",
            )
        show_chart(
            "Pairplot of Rainfall Indicators",
            "Pairplot",
            "A broader multivariate view of rainfall indicators colored by category.",
            "15_pairplot.png",
        )
        insight("The final rainfall page is intentionally analytical: distributions, decades, density, correlations, and pairwise relationships.")


else:
    data_map = load_mining_data()
    transactions = build_transactions(mining_dataset, data_map)
    all_items = sorted(set(item for transaction in transactions for item in transaction))

    render_hero(
        f"Association Mining: {mining_dataset}",
        "A rule-mining workspace for discovering repeated co-occurrence patterns in discretised weather records using Apriori, ECLAT, and FP-Growth implemented directly in Python.",
        [mining_algorithm, f"Support >= {min_sup:.2f}", f"Confidence >= {min_conf:.2f}", f"Max length {max_len}"],
        "linear-gradient(135deg, rgba(37,99,235,0.30), rgba(20,184,166,0.18), rgba(88,28,135,0.30))",
    )

    cols = st.columns(5)
    with cols[0]:
        stat_card(f"{len(transactions):,}", "Transactions", UI["accent"])
    with cols[1]:
        stat_card(len(all_items), "Unique Items", UI["accent_2"])
    with cols[2]:
        avg_size = np.mean([len(transaction) for transaction in transactions]) if transactions else 0
        stat_card(f"{avg_size:.1f}", "Avg Txn Size", UI["cyclone"])
    with cols[3]:
        stat_card(f"{min_sup:.2f}", "Min Support", UI["heat"])
    with cols[4]:
        stat_card(f"{min_conf:.2f}", "Min Confidence", UI["cold"])

    if not transactions:
        st.error(
            f"No transactions could be built for {mining_dataset}. Check that the required CSV exists in the project folder and has the expected columns."
        )
    else:
        section_heading("Association Mining", "Discretised transaction vocabulary")
        item_cols = st.columns(4)
        for idx, item in enumerate(all_items):
            item_cols[idx % 4].markdown(
                f"""
                <span style="display:inline-block;margin:0.2rem 0;padding:0.38rem 0.68rem;border-radius:999px;
                background:rgba(255,255,255,0.06);border:1px solid {UI["panel_border"]};
                color:{UI["text"]};font-size:0.78rem;font-weight:700;">{item}</span>
                """,
                unsafe_allow_html=True,
            )

        insight(
            f"{len(transactions):,} transactions with {len(all_items)} unique discretised items. The thresholds are applied to this basket-style representation of the selected weather dataset."
        )

        if mining_algorithm == "Compare All Three":
            section_heading("Association Mining", "Algorithm comparison")
            results = {}
            for algorithm in ["Apriori", "ECLAT", "FP-Growth"]:
                with st.spinner(f"Running {algorithm}..."):
                    rules_df, freq_df, elapsed = run_mining_cached(
                        mining_dataset, algorithm, min_sup, min_conf, max_len, transactions
                    )
                results[algorithm] = (rules_df, freq_df, elapsed)

            comparison = []
            for algorithm, (rules_df, freq_df, elapsed) in results.items():
                comparison.append(
                    {
                        "algorithm": algorithm,
                        "rules_found": len(rules_df),
                        "frequent_itemsets": len(freq_df),
                        "max_lift": round(rules_df["lift"].max(), 3) if not rules_df.empty else None,
                        "avg_confidence": round(rules_df["confidence"].mean(), 3) if not rules_df.empty else None,
                        "runtime_seconds": elapsed,
                    }
                )
            st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)
            insight(
                "All three methods use the same support, confidence, and lift definitions. Differences in runtime come from search strategy: Apriori generates candidates, ECLAT intersects transaction-id lists, and FP-Growth compresses common prefixes into a tree."
            )

            c1, c2, c3 = st.columns(3, gap="large")
            for column, algorithm in zip([c1, c2, c3], ["Apriori", "ECLAT", "FP-Growth"]):
                with column:
                    section_heading(algorithm, "Top rules by lift")
                    render_rules_table(results[algorithm][0], max_rows=8)
        else:
            with st.spinner(f"Running {mining_algorithm}..."):
                rules_df, freq_df, elapsed = run_mining_cached(
                    mining_dataset, mining_algorithm, min_sup, min_conf, max_len, transactions
                )

            section_heading("Association Mining", f"Results from {mining_algorithm}")
            metric_cols = st.columns(5)
            metric_cols[0].metric("Rules Found", len(rules_df))
            metric_cols[1].metric("Frequent Itemsets", len(freq_df))
            metric_cols[2].metric("Max Lift", f"{rules_df['lift'].max():.3f}" if not rules_df.empty else "0.000")
            metric_cols[3].metric(
                "Avg Confidence", f"{rules_df['confidence'].mean():.3f}" if not rules_df.empty else "0.000"
            )
            metric_cols[4].metric("Runtime", f"{elapsed:.3f}s")

            section_heading("Frequent Itemsets", "Top item combinations by support")
            left, right = st.columns([1, 1], gap="large")
            with left:
                render_frequent_items(freq_df, top_n=20)
            with right:
                if not freq_df.empty:
                    size_counts = freq_df.groupby("size").size().reset_index(name="count")
                    st.bar_chart(size_counts, x="size", y="count", use_container_width=True)

            section_heading("Association Rules", "Top rules sorted by lift")
            render_rules_table(rules_df, max_rows=25)

            if not rules_df.empty:
                section_heading("Lift Distribution", "Rule strength bands")
                lift_bins = pd.cut(
                    rules_df["lift"],
                    bins=[0, 1, 1.5, 2, 3, np.inf],
                    labels=["<=1.0", "1.0-1.5", "1.5-2.0", "2.0-3.0", ">3.0"],
                )
                lift_counts = lift_bins.value_counts().sort_index().reset_index()
                lift_counts.columns = ["lift_band", "rules"]
                st.bar_chart(lift_counts, x="lift_band", y="rules", use_container_width=True)

            if mining_dataset == "Cyclone":
                insight(
                    "For cyclones, high-lift rules usually connect category, wind, storm surge, landfall, and fatality bands. These rules validate how intensity labels and impact indicators move together."
                )
            elif mining_dataset == "Heatwave / Coldwave":
                insight(
                    "For temperature extremes, the strongest rules tend to combine event type, severity, alert level, duration, and deaths. This helps expose where warning categories align with observed impact."
                )
            elif mining_dataset == "Air Quality Index":
                insight(
                    "For AQI, winter season, PM2.5 dominance, and poor AQI bands often form the most interpretable patterns, especially for seasonal inversion and particulate buildup."
                )
            else:
                insight(
                    "For rainfall, monsoon season, agro-zone, departure class, and heavy-rainfall bands reveal flood and deficit-prone combinations across the long historical record."
                )


st.markdown(
    f"""
    <div style="margin-top:1rem;padding:1rem 0 0.4rem 0;color:{UI["subtle"]};font-size:0.84rem;text-align:center;">
        India Weather Extremes Dashboard Project - EDA + Association Mining - Streamlit presentation layer for your analysis notebooks
    </div>
    """,
    unsafe_allow_html=True,
)