import sqlite3
import pandas as pd
from data_exploration import clean_data
import streamlit as st

@st.cache_data
def load_stock_data():
    conn = sqlite3.connect("stock_analysis.db")

    df = clean_data()
    df.to_sql("stock", conn, if_exists="replace", index=False)
    conn.commit()

    chart_query = """
    SELECT 
        ticker,
        date,
        close
    FROM
        stock
    ORDER BY date ASC
    """

    kpi_query = """
    WITH ranking AS (
    SELECT 
        ticker,
        date,
        close,
        ROW_NUMBER() OVER (
        PARTITION BY ticker
        ORDER BY date desc) AS row_num
    FROM
        stock
    ), 
    performance_base AS (
    SELECT
        ticker,
        MAX(CASE WHEN row_num = 1 THEN close END) AS latest_close,
        MAX(CASE WHEN row_num = 31 THEN close END) AS prior_close
    FROM 
        ranking
    WHERE row_num IN (1, 31)
    GROUP BY ticker
    ),
    performance AS(
    SELECT 
        ticker,
        latest_close,
        prior_close,
        ((latest_close - prior_close) / prior_close) AS return_30d
    FROM 
        performance_base
    )
    SELECT
        (SELECT ticker FROM performance ORDER BY return_30d DESC LIMIT 1) AS best_ticker,
        (SELECT return_30d FROM performance ORDER BY return_30d DESC LIMIT 1) AS best_return,
        (SELECT ticker FROM performance ORDER BY return_30d ASC LIMIT 1) AS worst_ticker,
        (SELECT return_30d FROM performance ORDER BY return_30d ASC LIMIT 1) AS worst_return,
        AVG(return_30d) AS average_return
    FROM performance
    LIMIT 1;
    """

    performance_query = """
    WITH ranking as (
    SELECT 
        ticker,
        date,
        close,
        ROW_NUMBER() OVER (
        PARTITION BY ticker
        ORDER BY date desc) AS row_num
    FROM
        stock
    ), 
    performance_base AS (
    SELECT
        ticker,
        MAX(CASE WHEN row_num = 1 THEN close END) AS latest_close,
        MAX(CASE WHEN row_num = 31 THEN close END) AS prior_close,
        MAX(CASE WHEN row_num = 8 THEN close END) AS seven_day_close
    FROM 
        ranking
    WHERE row_num BETWEEN 1 AND 31
    GROUP BY ticker
    ),
    performance AS(
    SELECT 
        ticker,
        latest_close,
        prior_close,
        seven_day_close,
        ((latest_close - prior_close) / prior_close) AS return_30d,
        ((latest_close - seven_day_close) / seven_day_close) AS return_7d
    FROM 
        performance_base
    ),
    daily_return_base AS (
    SELECT
        ticker,
        close,
        LEAD(close) OVER (
        PARTITION BY ticker
        ORDER BY date DESC
        ) AS previous_close
    FROM ranking
    WHERE row_num BETWEEN 1 AND 31
    ),
    daily_return AS (
    SELECT
        ticker,
        close,
        previous_close,
        ((close - previous_close) / previous_close) AS daily_return
    FROM 
        daily_return_base
    ),
    average_daily_return AS (
    SELECT
        ticker,
        AVG(daily_return) AS average_daily_return
    FROM daily_return
    GROUP BY ticker
    )
    SELECT
        performance.ticker AS ticker,
        latest_close,
        return_7d,
        return_30d,
        average_daily_return
    FROM 
        performance
    JOIN average_daily_return
        ON performance.ticker = average_daily_return.ticker;
"""

    chart_df = pd.read_sql_query(chart_query, conn)
    kpi_df = pd.read_sql_query(kpi_query, conn)
    performance_df = pd.read_sql_query(performance_query, conn)

    conn.close()

    return chart_df, kpi_df, performance_df

def get_stock_data():
    chart_df, kpi_df, performance_df = load_stock_data()

    ticker_options = sorted(chart_df["ticker"].unique())

    tickers = ticker_options
    best_ticker = kpi_df.loc[0, "best_ticker"]
    best_return = kpi_df.loc[0, "best_return"]
    worst_ticker = kpi_df.loc[0, "worst_ticker"]
    worst_return = kpi_df.loc[0, "worst_return"]
    average_return = kpi_df.loc[0, "average_return"]
    return {
        "tickers": tickers,
        "best_ticker": best_ticker,
        "best_return": best_return,
        "worst_ticker": worst_ticker,
        "worst_return": worst_return,
        "average_return": average_return,
        "chart_df": chart_df,
        "performance_df": performance_df
    }

