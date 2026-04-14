from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Stock Market Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from main import get_stock_data

data = get_stock_data()

def format_currency(value):
    return f"${value:,.2f}"


def format_percent(value):
    return f"{value * 100:+.2f}%"


def get_value_class(value):
    return "negative" if value < 0 else "positive"


def render_kpi_card(label, ticker, value, modifier_class=""):
    value_class = modifier_class or get_value_class(value)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-name">{ticker}</div>
            <div class="metric-value {value_class}">{format_percent(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_price_chart(filtered_chart_df, selected_ticker):
    return {
        "height": 360,
        "title": {"text": f"{selected_ticker} closing price", "anchor": "start"},
        "layer": [
            {
                "mark": {
                    "type": "area",
                    "line": {"color": "#00d26a", "strokeWidth": 2.2},
                    "color": {
                        "gradient": "linear",
                        "x1": 1,
                        "y1": 0,
                        "x2": 1,
                        "y2": 1,
                        "stops": [
                            {"offset": 0, "color": "#00d26a"},
                            {"offset": 1, "color": "#0f2317"},
                        ],
                    },
                    "opacity": 0.30,
                },
                "encoding": {
                    "x": {
                        "field": "date",
                        "type": "temporal",
                        "axis": {
                            "title": None,
                            "format": "%b %d",
                            "labelColor": "#7e8b82",
                            "domainColor": "#1f2621",
                            "gridColor": "#181d1a",
                            "tickColor": "#1f2621",
                        },
                    },
                    "y": {
                        "field": "close",
                        "type": "quantitative",
                        "axis": {
                            "title": None,
                            "format": "$,.0f",
                            "labelColor": "#7e8b82",
                            "domainColor": "#1f2621",
                            "gridColor": "#181d1a",
                            "tickColor": "#1f2621",
                        },
                    },
                },
            },
            {
                "params": [
                    {
                        "name": "hover",
                        "select": {
                            "type": "point",
                            "fields": ["date"],
                            "nearest": True,
                            "on": "mouseover",
                            "clear": "mouseout",
                        },
                    }
                ],
                "mark": {"type": "point", "opacity": 0},
                "encoding": {
                    "x": {"field": "date", "type": "temporal"},
                    "y": {"field": "close", "type": "quantitative"},
                },
            },
            {
                "mark": {
                    "type": "point",
                    "filled": True,
                    "size": 95,
                    "color": "#00d26a",
                    "stroke": "#eef3ee",
                    "strokeWidth": 1.6,
                },
                "encoding": {
                    "x": {"field": "date", "type": "temporal"},
                    "y": {"field": "close", "type": "quantitative"},
                    "opacity": {
                        "condition": {"param": "hover", "empty": False, "value": 1},
                        "value": 0,
                    },
                    "tooltip": [
                        {"field": "ticker", "type": "nominal", "title": "Ticker"},
                        {"field": "date", "type": "temporal", "title": "Date"},
                        {
                            "field": "close",
                            "type": "quantitative",
                            "title": "Close",
                            "format": "$,.2f",
                        },
                    ],
                },
            },
        ],
        "config": {
            "background": "transparent",
            "title": {"color": "#eef3ee", "fontSize": 16, "fontWeight": 500},
            "view": {"stroke": None},
        },
    }


def load_stylesheet():
    stylesheet = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{stylesheet}</style>", unsafe_allow_html=True)


load_stylesheet()

st.markdown(
    """
    <div class="header-utility">
        <div class="header-signature">© 2026 Rahim Shahzad</div>
        <a class="header-link-button" href="https://github.com/RahimSh04/stock_market_dashboard" target="_blank" rel="noopener noreferrer">
            View GitHub Repo
        </a>
        <div class="header-tech">
            <span class="header-tech-label">Built with</span>
            <span class="header-tech-badge" title="Python" aria-label="Python">
                <img src="https://cdn.simpleicons.org/python/3776AB" alt="Python">
            </span>
            <span class="header-tech-badge" title="SQL" aria-label="SQL">
                <img src="https://cdn.simpleicons.org/sqlite/003B57" alt="SQLite">
            </span>
            <span class="header-tech-badge" title="Streamlit" aria-label="Streamlit">
                <img src="https://cdn.simpleicons.org/streamlit/FF4B4B" alt="Streamlit">
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="page-title">Stock Market Dashboard</h1>', unsafe_allow_html=True)
st.markdown(
    """
    <p class="page-subtitle">
        Daily closing prices for 5 tracked stocks. Choose from the below filter, which stock you would like to view.
    </p>
    """,
    unsafe_allow_html=True,
)

kpi_cols = st.columns(3, gap="large")
with kpi_cols[0]:
    render_kpi_card("Best performer (100 days)", data["best_ticker"], data["best_return"])
with kpi_cols[1]:
    render_kpi_card("Worst performer (100 days)", data["worst_ticker"], data["worst_return"], "negative")
with kpi_cols[2]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Average return (100 days)</div>
            <div class="metric-name">Across tracked stocks</div>
            <div class="metric-value {get_value_class(data["average_return"])}">{format_percent(data["average_return"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

toolbar_cols = st.columns([3.2, 1], gap="large")
with toolbar_cols[0]:
    st.markdown(
        """
        <div class="section-kicker">Market view</div>
        <h2 class="section-title">Closing price movement</h2>
        <p class="section-note">
            Single-stock view with the selected ticker applied to both the chart and the performance panel.
        </p>
        """,
        unsafe_allow_html=True,
    )
with toolbar_cols[1]:
    st.markdown('<div class="section-kicker">Filter</div>', unsafe_allow_html=True)
    selected_ticker = st.selectbox(
        "Choose stock",
        data["tickers"],
        key="stock_filter",
        label_visibility="collapsed",
    )

filtered_chart_df = data["chart_df"].loc[data["chart_df"]["ticker"] == selected_ticker].copy()
filtered_chart_df["date"] = pd.to_datetime(filtered_chart_df["date"])
filtered_chart_df = filtered_chart_df.sort_values("date")
selected_stock_row = data["performance_df"].loc[
    data["performance_df"]["ticker"] == selected_ticker
].iloc[0]
selected_chart = build_price_chart(filtered_chart_df, selected_ticker)

chart_start = filtered_chart_df["date"].min().strftime("%b %d")
chart_end = filtered_chart_df["date"].max().strftime("%b %d")
chart_sessions = len(filtered_chart_df)

main_cols = st.columns([2.25, 1], gap="large")
with main_cols[0]:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="chart-context">
                <div class="chart-context-title">{selected_ticker}</div>
                <div class="chart-context-meta">{chart_start} to {chart_end} · {chart_sessions} sessions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.vega_lite_chart(filtered_chart_df, selected_chart, use_container_width=True)

with main_cols[1]:
    st.markdown(
        f"""
        <div class="section-shell">
            <div class="section-kicker">Performance</div>
            <h2 class="section-title">{selected_ticker}</h2>
            <p class="section-note">Latest snapshot for the currently selected stock.</p>
            <div class="panel-price">{format_currency(selected_stock_row["latest_close"])}</div>
            <div class="panel-meta">
                Latest close as of {(pd.Timestamp.today().normalize() - timedelta(days=1)).strftime("%b %d, %Y")}
            </div>
            <div class="detail-grid">
                <div class="detail-box">
                    <div class="detail-label">7-day return</div>
                    <div class="detail-value {get_value_class(selected_stock_row["return_7d"])}">{format_percent(selected_stock_row["return_7d"])}</div>
                </div>
                <div class="detail-box">
                    <div class="detail-label">30-day return</div>
                    <div class="detail-value {get_value_class(selected_stock_row["return_30d"])}">{format_percent(selected_stock_row["return_30d"])}</div>
                </div>
                <div class="detail-box">
                    <div class="detail-label">Average daily return</div>
                    <div class="detail-value {get_value_class(selected_stock_row["average_daily_return"])}">{format_percent(selected_stock_row["average_daily_return"])}</div>
                </div>
                <div class="detail-box">
                    <div class="detail-label">Coverage</div>
                    <div class="detail-value neutral">30-session return window</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
