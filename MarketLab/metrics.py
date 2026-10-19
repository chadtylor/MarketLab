import numpy as np


TRADING_DAYS = 252


def calculate_metrics(
    data,
    initial_capital
):
    """
    Calculate performance statistics.
    """

    if data.empty:
        return {}


    ending_value = (
        data["Strategy_Equity"]
        .iloc[-1]
    )

    benchmark_value = (
        data["Benchmark_Equity"]
        .iloc[-1]
    )


    total_return = (
        ending_value
        /
        initial_capital
        -
        1
    )


    benchmark_return = (
        benchmark_value
        /
        initial_capital
        -
        1
    )


    strategy_returns = (
        data["Strategy_Return"]
        .dropna()
    )


    volatility = (
        strategy_returns.std()
        *
        np.sqrt(TRADING_DAYS)
    )


    if (
        strategy_returns.std() != 0
        and len(strategy_returns) > 1
    ):

        sharpe_ratio = (
            strategy_returns.mean()
            /
            strategy_returns.std()
            *
            np.sqrt(TRADING_DAYS)
        )

    else:

        sharpe_ratio = 0


    max_drawdown = (
        data["Drawdown"]
        .min()
    )


    days = (
        data["Date"].iloc[-1]
        -
        data["Date"].iloc[0]
    ).days


    years = (
        days / 365.25
    )


    if years > 0:

        cagr = (
            (
                ending_value
                /
                initial_capital
            )
            **
            (1 / years)
            -
            1
        )

    else:

        cagr = 0


    return {
        "ending_value":
            ending_value,

        "total_return":
            total_return,

        "benchmark_return":
            benchmark_return,

        "cagr":
            cagr,

        "volatility":
            volatility,

        "sharpe_ratio":
            sharpe_ratio,

        "max_drawdown":
            max_drawdown
    }


def calculate_trade_metrics(
    trades
):
    """
    Trade-level statistics.
    """

    if trades.empty:

        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "average_trade": 0,
            "best_trade": 0,
            "worst_trade": 0
        }


    winners = trades[
        trades["Return %"] > 0
    ]

    losers = trades[
        trades["Return %"] < 0
    ]


    return {
        "total_trades":
            len(trades),

        "winning_trades":
            len(winners),

        "losing_trades":
            len(losers),

        "win_rate":
            (
                len(winners)
                /
                len(trades)
            )
            *
            100,

        "average_trade":
            trades[
                "Return %"
            ].mean(),

        "best_trade":
            trades[
                "Return %"
            ].max(),

        "worst_trade":
            trades[
                "Return %"
            ].min()
    }