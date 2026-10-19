import numpy as np
import pandas as pd


def moving_average_strategy(
    data,
    short_window=20,
    long_window=50
):
    """
    Moving-average crossover strategy.

    Buy:
        Short MA moves above long MA.

    Sell:
        Short MA moves below long MA.
    """

    df = data.copy()

    df["Short_MA"] = (
        df["Close"]
        .rolling(short_window)
        .mean()
    )

    df["Long_MA"] = (
        df["Close"]
        .rolling(long_window)
        .mean()
    )

    df["Signal"] = 0

    df.loc[
        df["Short_MA"] > df["Long_MA"],
        "Signal"
    ] = 1

    df["Position"] = (
        df["Signal"]
        .diff()
        .fillna(0)
    )

    return df


def calculate_rsi(series, period=14):
    """
    Calculate Relative Strength Index.
    """

    delta = series.diff()

    gains = delta.clip(lower=0)

    losses = -delta.clip(upper=0)

    average_gain = (
        gains
        .rolling(period)
        .mean()
    )

    average_loss = (
        losses
        .rolling(period)
        .mean()
    )

    rs = average_gain / average_loss

    rsi = (
        100
        -
        (100 / (1 + rs))
    )

    return rsi


def rsi_strategy(
    data,
    period=14,
    oversold=30,
    overbought=70
):
    """
    RSI strategy.

    Enter long when RSI falls below oversold level.
    Exit when RSI rises above overbought level.
    """

    df = data.copy()

    df["RSI"] = calculate_rsi(
        df["Close"],
        period
    )

    position = 0

    signals = []

    positions = []

    for rsi in df["RSI"]:

        previous_position = position

        if pd.notna(rsi):

            if rsi < oversold:
                position = 1

            elif rsi > overbought:
                position = 0

        signals.append(position)

        positions.append(
            position -
            previous_position
        )

    df["Signal"] = signals

    df["Position"] = positions

    return df


def buy_and_hold_strategy(data):
    """
    Benchmark strategy.
    """

    df = data.copy()

    df["Signal"] = 1

    df["Position"] = 0

    if len(df) > 0:
        df.loc[
            df.index[0],
            "Position"
        ] = 1

    return df