from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import (
    download_market_data,
    load_csv
)

from strategies import (
    moving_average_strategy,
    rsi_strategy,
    buy_and_hold_strategy
)

from backtest import (
    backtest_strategy,
    extract_trades
)

from metrics import (
    calculate_metrics,
    calculate_trade_metrics
)


st.set_page_config(
    page_title="MarketLab",
    page_icon="📈",
    layout="wide"
)


st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        max-width: 1500px;
    }

    .main-title {
        font-size: 3.4rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .disclaimer {
        padding: 12px;
        border-radius: 8px;
        background: rgba(255, 166, 0, 0.08);
        font-size: 0.8rem;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="main-title">
        MarketLab
    </div>

    <div class="subtitle">
        Historical market analysis and strategy backtesting platform
    </div>
    """,
    unsafe_allow_html=True
)


with st.sidebar:

    st.header(
        "Market settings"
    )

    source = st.radio(
        "Data source",
        [
            "Yahoo Finance",
            "Upload CSV"
        ]
    )


    symbol = st.text_input(
        "Ticker symbol",
        value="AAPL"
    )


    default_end = date.today()

    default_start = (
        default_end
        -
        timedelta(days=365 * 5)
    )


    start_date = st.date_input(
        "Start date",
        value=default_start
    )


    end_date = st.date_input(
        "End date",
        value=default_end
    )


    uploaded_file = None

    if source == "Upload CSV":

        uploaded_file = (
            st.file_uploader(
                "Upload OHLC CSV",
                type=["csv"]
            )
        )


    st.divider()


    st.header(
        "Strategy"
    )


    strategy_name = st.selectbox(
        "Select strategy",
        [
            "Moving Average Crossover",
            "RSI Strategy",
            "Buy & Hold"
        ]
    )


    short_window = 20
    long_window = 50

    rsi_period = 14
    oversold = 30
    overbought = 70


    if (
        strategy_name
        ==
        "Moving Average Crossover"
    ):

        short_window = st.number_input(
            "Short moving average",
            min_value=2,
            max_value=200,
            value=20
        )

        long_window = st.number_input(
            "Long moving average",
            min_value=3,
            max_value=400,
            value=50
        )


    elif (
        strategy_name
        ==
        "RSI Strategy"
    ):

        rsi_period = st.number_input(
            "RSI period",
            min_value=2,
            max_value=100,
            value=14
        )

        oversold = st.number_input(
            "Oversold",
            min_value=1,
            max_value=49,
            value=30
        )

        overbought = st.number_input(
            "Overbought",
            min_value=51,
            max_value=99,
            value=70
        )


    st.divider()


    st.header(
        "Backtest"
    )


    initial_capital = st.number_input(
        "Initial capital (£)",
        min_value=100,
        value=10000,
        step=1000
    )


    transaction_cost = st.number_input(
        "Transaction cost",
        min_value=0.0,
        max_value=0.05,
        value=0.001,
        step=0.0005,
        format="%.4f"
    )


    run_button = st.button(
        "Run analysis",
        use_container_width=True,
        type="primary"
    )


if run_button:

    try:

        if source == "Yahoo Finance":

            data = download_market_data(
                symbol,
                start_date,
                end_date
            )

        else:

            if uploaded_file is None:

                st.warning(
                    "Upload a CSV file first."
                )

                st.stop()

            data = load_csv(
                uploaded_file
            )


        if (
            strategy_name
            ==
            "Moving Average Crossover"
        ):

            if (
                short_window
                >=
                long_window
            ):

                st.error(
                    "The short moving average must be smaller than the long moving average."
                )

                st.stop()


            strategy_data = (
                moving_average_strategy(
                    data,
                    short_window,
                    long_window
                )
            )


        elif (
            strategy_name
            ==
            "RSI Strategy"
        ):

            strategy_data = (
                rsi_strategy(
                    data,
                    rsi_period,
                    oversold,
                    overbought
                )
            )


        else:

            strategy_data = (
                buy_and_hold_strategy(
                    data
                )
            )


        results = backtest_strategy(
            strategy_data,
            initial_capital,
            transaction_cost
        )


        trades = extract_trades(
            results
        )


        metrics = calculate_metrics(
            results,
            initial_capital
        )


        trade_metrics = (
            calculate_trade_metrics(
                trades
            )
        )


        st.subheader(
            f"{symbol.upper()} analysis"
        )


        col1, col2, col3, col4 = (
            st.columns(4)
        )


        col1.metric(
            "Ending portfolio",
            f"£{metrics['ending_value']:,.2f}"
        )


        col2.metric(
            "Strategy return",
            f"{metrics['total_return'] * 100:.2f}%"
        )


        col3.metric(
            "Buy & hold",
            f"{metrics['benchmark_return'] * 100:.2f}%"
        )


        col4.metric(
            "Sharpe ratio",
            f"{metrics['sharpe_ratio']:.2f}"
        )


        col5, col6, col7, col8 = (
            st.columns(4)
        )


        col5.metric(
            "CAGR",
            f"{metrics['cagr'] * 100:.2f}%"
        )


        col6.metric(
            "Max drawdown",
            f"{metrics['max_drawdown'] * 100:.2f}%"
        )


        col7.metric(
            "Annual volatility",
            f"{metrics['volatility'] * 100:.2f}%"
        )


        col8.metric(
            "Number of trades",
            trade_metrics[
                "total_trades"
            ]
        )


        st.divider()


        st.subheader(
            "Price & trading signals"
        )


        price_chart = (
            go.Figure()
        )


        price_chart.add_trace(
            go.Scatter(
                x=results["Date"],
                y=results["Close"],
                name="Close",
                mode="lines"
            )
        )


        if (
            "Short_MA"
            in results.columns
        ):

            price_chart.add_trace(
                go.Scatter(
                    x=results["Date"],
                    y=results["Short_MA"],
                    name=f"MA {short_window}",
                    mode="lines"
                )
            )


            price_chart.add_trace(
                go.Scatter(
                    x=results["Date"],
                    y=results["Long_MA"],
                    name=f"MA {long_window}",
                    mode="lines"
                )
            )


        buys = results[
            results["Position"] == 1
        ]


        sells = results[
            results["Position"] == -1
        ]


        price_chart.add_trace(
            go.Scatter(
                x=buys["Date"],
                y=buys["Close"],
                name="Buy",
                mode="markers",
                marker=dict(
                    symbol="triangle-up",
                    size=11
                )
            )
        )


        price_chart.add_trace(
            go.Scatter(
                x=sells["Date"],
                y=sells["Close"],
                name="Sell",
                mode="markers",
                marker=dict(
                    symbol="triangle-down",
                    size=11
                )
            )
        )


        price_chart.update_layout(
            height=520,
            xaxis_title="Date",
            yaxis_title="Price",
            legend_orientation="h",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            )
        )


        st.plotly_chart(
            price_chart,
            use_container_width=True
        )


        if (
            strategy_name
            ==
            "RSI Strategy"
        ):

            st.subheader(
                "RSI"
            )


            rsi_chart = (
                go.Figure()
            )


            rsi_chart.add_trace(
                go.Scatter(
                    x=results["Date"],
                    y=results["RSI"],
                    name="RSI"
                )
            )


            rsi_chart.add_hline(
                y=oversold,
                line_dash="dash"
            )


            rsi_chart.add_hline(
                y=overbought,
                line_dash="dash"
            )


            rsi_chart.update_layout(
                height=300
            )


            st.plotly_chart(
                rsi_chart,
                use_container_width=True
            )


        st.subheader(
            "Portfolio performance"
        )


        performance_chart = (
            go.Figure()
        )


        performance_chart.add_trace(
            go.Scatter(
                x=results["Date"],
                y=results[
                    "Strategy_Equity"
                ],
                name="Strategy"
            )
        )


        performance_chart.add_trace(
            go.Scatter(
                x=results["Date"],
                y=results[
                    "Benchmark_Equity"
                ],
                name="Buy & Hold"
            )
        )


        performance_chart.update_layout(
            height=450,
            xaxis_title="Date",
            yaxis_title="Portfolio value"
        )


        st.plotly_chart(
            performance_chart,
            use_container_width=True
        )


        st.subheader(
            "Drawdown"
        )


        drawdown_chart = (
            go.Figure()
        )


        drawdown_chart.add_trace(
            go.Scatter(
                x=results["Date"],
                y=(
                    results["Drawdown"]
                    *
                    100
                ),
                fill="tozeroy",
                name="Drawdown"
            )
        )


        drawdown_chart.update_layout(
            height=300,
            yaxis_title="Drawdown %"
        )


        st.plotly_chart(
            drawdown_chart,
            use_container_width=True
        )


        st.subheader(
            "Trade statistics"
        )


        trade_col1, trade_col2, trade_col3, trade_col4 = (
            st.columns(4)
        )


        trade_col1.metric(
            "Win rate",
            f"{trade_metrics['win_rate']:.1f}%"
        )


        trade_col2.metric(
            "Average trade",
            f"{trade_metrics['average_trade']:.2f}%"
        )


        trade_col3.metric(
            "Best trade",
            f"{trade_metrics['best_trade']:.2f}%"
        )


        trade_col4.metric(
            "Worst trade",
            f"{trade_metrics['worst_trade']:.2f}%"
        )


        st.subheader(
            "Trade history"
        )


        if trades.empty:

            st.info(
                "No completed trades were generated during this period."
            )

        else:

            display_trades = (
                trades.copy()
            )


            display_trades[
                "Entry Price"
            ] = display_trades[
                "Entry Price"
            ].round(2)


            display_trades[
                "Exit Price"
            ] = display_trades[
                "Exit Price"
            ].round(2)


            display_trades[
                "Return %"
            ] = display_trades[
                "Return %"
            ].round(2)


            st.dataframe(
                display_trades,
                use_container_width=True,
                hide_index=True
            )


        st.subheader(
            "Historical data"
        )


        st.dataframe(
            results.tail(100),
            use_container_width=True,
            hide_index=True
        )


        downloadable = (
            results.to_csv(
                index=False
            )
        )


        st.download_button(
            "Download backtest results",
            downloadable,
            file_name=(
                f"{symbol.lower()}_backtest.csv"
            ),
            mime="text/csv"
        )


        st.markdown(
            """
            <div class="disclaimer">
                <strong>Important:</strong>
                MarketLab is an educational backtesting application.
                Historical performance does not predict future results,
                and the output is not investment advice.
            </div>
            """,
            unsafe_allow_html=True
        )


    except Exception as error:

        st.error(
            str(error)
        )


else:

    st.info(
        "Configure a market and strategy in the sidebar, then click Run analysis."
    )


    st.markdown(
        """
        ### What MarketLab can analyse

        - Historical OHLC market data
        - Daily percentage returns
        - Moving-average crossover strategies
        - RSI trading strategies
        - Buy-and-hold benchmarks
        - Portfolio equity curves
        - Maximum drawdown
        - CAGR
        - Sharpe ratio
        - Annualised volatility
        - Trade win rate
        - Transaction costs
        """
    )