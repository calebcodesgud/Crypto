from typing import List, Tuple
import numpy as np
from pandas import DataFrame as df, date_range
from config import config
import matplotlib.pyplot as plt
import scipy.optimize as spo
from datetime import datetime, timedelta

ANNUALIZER_CONST = 252
ANNUALIZED_RFR_CONST = ((1 + config.RISK_FREE_RATE_APY) ** (1 / ANNUALIZER_CONST)) - 1


def _portfolioValueAndDailyReturns(prices: df, allocs: np.ndarray) -> Tuple[df, df]:
    normed_prices = prices / prices.iloc[0]
    alloced_prices = normed_prices * allocs
    portfolio_value = alloced_prices.sum(axis=1)
    daily_returns = portfolio_value.copy()
    daily_returns[1:] = (portfolio_value.iloc[1:] / portfolio_value.iloc[:-1].values) - 1
    daily_returns.iloc[0] = 0
    return portfolio_value, daily_returns


def _sharpe_ratio(allocs: np.ndarray, prices: df) -> np.float:
    """
    Calculates the sharpe ratio of a portfolio given a set of allocations.

    @params
    allocs: np.ndarray - the allocations. Should have length = the number of columns in prices.
    prices: dataframe - historical prices. Should have a column per asset, index by dates

    @returns
    sharpe ratio as a np.float
    """
    _, daily_returns = _portfolioValueAndDailyReturns(prices, allocs)
    return np.sqrt(ANNUALIZER_CONST) * ((np.mean(daily_returns) - ANNUALIZED_RFR_CONST) / np.std(daily_returns))


def _neg_portfolio_sharpe_ratio(allocs: np.ndarray, prices: df) -> np.float:
    """
    Calculates the negative sharpe ratio of a portfolio given a set of allocations.

    @params
    allocs: np.ndarray - the allocations. Should have length = the number of columns in prices.
    prices: dataframe - historical prices. Should have a column per asset, index by dates

    @returns
    returns negative sharpe ratio as a np.float
    """
    return -1 * _sharpe_ratio(allocs, prices)


class Optimizer(object):

    def __init__(self, windowSizeDays: int):
        self.windowSizeDays = windowSizeDays

    def optimizePortfolio(self,
                          symbols: List[str],
                          data: df,
                          endDate: datetime = datetime.today() - timedelta(1),
                          gen_plot: bool = False,
                          bmSymbol: str = None):

        start = endDate - timedelta(self.windowSizeDays)
        startDate = datetime(start.year, start.month, start.day)
        sliceOfData: df = df(index=date_range(startDate, endDate))
        sliceOfData[list(data.columns)] = np.nan
        sliceOfData.update(data, overwrite=False)
        prices = sliceOfData[symbols]

        if bmSymbol is not None:
            prices_BM = sliceOfData[bmSymbol]

        equal_allocs = np.asarray([1 / len(symbols) for i in symbols])  # start with equal allocation
        equal_portfolio_value, equal_daily_returns = _portfolioValueAndDailyReturns(prices, equal_allocs)

        result = spo.minimize(_neg_portfolio_sharpe_ratio, equal_allocs, args=prices, method='SLSQP',
                              bounds=[(0, 1) for i in symbols], constraints={
                'type': 'eq',
                'fun': lambda input: 1 - np.sum(input)
            })
        allocs = result.x

        portfolio_value, daily_returns = _portfolioValueAndDailyReturns(prices, allocs)

        cr = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1

        if gen_plot:
            figure, axis = plt.subplots(ncols=2, sharey=True, sharex=True, figsize=(10, 5))

            portfolio_value.name = 'Portfolio'
            portfolio_value.plot(legend=True, ax=axis[0])
            if bmSymbol is not None:
                BM_value = prices_BM / prices_BM.iloc[0]
                BM_value.plot(legend=True, ax=axis[0])
            equal_portfolio_value.name = 'Equal Weight'
            equal_portfolio_value.plot(legend=True, ax=axis[0])
            axis[0].set_ylabel('Return')
            axis[0].set_xlabel('Dates')
            if bmSymbol is not None:
                axis[0].set_title(f'Daily Portfolio gains vs equal alloc vs {bmSymbol}')
            else:
                axis[0].set_title(f'Daily Portfolio gains vs equal alloc')

            for symbol in symbols:
                asset = prices[symbol] / prices[symbol].iloc[0]
                asset.name = symbol
                asset.plot(legend=True, ax=axis[1])

            axis[1].set_ylabel('Return')
            axis[1].set_xlabel('Dates')
            axis[1].set_title('Return for all considered assets')
            plt.draw()

        return allocs, cr, np.mean(daily_returns), np.std(daily_returns), _sharpe_ratio(allocs, prices)
