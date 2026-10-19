import pandas as pd
import yfinance as yf


def download_market_data(symbol, start_date, end_date):
    """
    Download historical market data from Yahoo Finance.
    """

    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError("Enter a valid ticker symbol.")

    data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError(
            f"No historical data was found for {symbol}."
        )

    # yfinance may return MultiIndex columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    available_columns = [
        column
        for column in required_columns
        if column in data.columns
    ]

    data = data[available_columns].copy()

    data["Date"] = pd.to_datetime(data["Date"])

    data = data.sort_values("Date")

    data = data.dropna(
        subset=["Close"]
    )

    data = data.reset_index(drop=True)

    return data


def load_csv(file):
    """
    Load historical data from an uploaded CSV.
    """

    data = pd.read_csv(file)

    required_columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            "CSV must contain: "
            + ", ".join(required_columns)
        )

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    data = data.dropna(
        subset=["Date", "Close"]
    )

    data = data.sort_values("Date")

    data = data.reset_index(drop=True)

    return data