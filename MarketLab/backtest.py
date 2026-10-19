import pandas as pd


def backtest_strategy(
    data,
    initial_capital=10000,
    transaction_cost=0.001
):
    """
    Simple long-only historical backtest.
    """

    df = data.copy()

    df["Market_Return"] = (
        df["Close"]
        .pct_change()
        .fillna(0)
    )

    # Shift signal so that today's signal
    # affects the following day's return.
    df["Strategy_Return"] = (
        df["Signal"]
        .shift(1)
        .fillna(0)
        *
        df["Market_Return"]
    )

    trades = (
        df["Signal"]
        .diff()
        .abs()
        .fillna(0)
    )

    df["Transaction_Cost"] = (
        trades *
        transaction_cost
    )

    df["Strategy_Return"] -= (
        df["Transaction_Cost"]
    )

    df["Strategy_Equity"] = (
        initial_capital
        *
        (1 + df["Strategy_Return"])
        .cumprod()
    )

    df["Benchmark_Equity"] = (
        initial_capital
        *
        (1 + df["Market_Return"])
        .cumprod()
    )

    running_max = (
        df["Strategy_Equity"]
        .cummax()
    )

    df["Drawdown"] = (
        df["Strategy_Equity"]
        /
        running_max
        -
        1
    )

    return df


def extract_trades(data):
    """
    Convert strategy entry/exit signals
    into a trade-history table.
    """

    trades = []

    entry_price = None
    entry_date = None

    for _, row in data.iterrows():

        if row["Position"] == 1:

            entry_price = row["Close"]

            entry_date = row["Date"]

        elif (
            row["Position"] == -1
            and entry_price is not None
        ):

            exit_price = row["Close"]

            exit_date = row["Date"]

            return_pct = (
                exit_price
                /
                entry_price
                -
                1
            )

            trades.append({
                "Entry Date": entry_date,
                "Entry Price": entry_price,
                "Exit Date": exit_date,
                "Exit Price": exit_price,
                "Return %": return_pct * 100
            })

            entry_price = None
            entry_date = None

    # Handle still-open final trade
    if (
        entry_price is not None
        and len(data) > 0
    ):

        final_row = data.iloc[-1]

        exit_price = final_row["Close"]

        return_pct = (
            exit_price
            /
            entry_price
            -
            1
        )

        trades.append({
            "Entry Date": entry_date,
            "Entry Price": entry_price,
            "Exit Date": final_row["Date"],
            "Exit Price": exit_price,
            "Return %": return_pct * 100
        })

    return pd.DataFrame(trades)