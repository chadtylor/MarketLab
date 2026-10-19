# MarketLab

MarketLab is a Python financial market analysis and backtesting application.

It downloads historical market data, applies trading strategies, evaluates their performance, and visualises results through an interactive Streamlit dashboard.

## Features

- Download historical market data using Yahoo Finance
- Upload your own OHLC market data using CSV
- Moving Average Crossover strategy
- RSI trading strategy
- Buy & Hold benchmark
- Buy and sell signal visualisation
- Portfolio equity curve
- Benchmark comparison
- Maximum drawdown analysis
- CAGR calculation
- Sharpe ratio
- Annualised volatility
- Trade win rate
- Best and worst trade analysis
- Transaction cost simulation
- Trade history table
- Downloadable backtest results

## Built With

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- yfinance

## Project Structure

```text
MarketLab/
├── app.py
├── data.py
├── strategies.py
├── backtest.py
├── metrics.py
├── requirements.txt
└── README.md
