"""
Author: Caleb Woy

"""

import datetime as dt
import matplotlib.pyplot as plt
from pandas import DataFrame as df

from config import config
from data.DataLoader import DataLoader
from optimizer.Optimizer import Optimizer

if __name__ == "__main__":
    end_date = dt.datetime.now() - dt.timedelta(1)
    start_date = config.MAX_LOOKBACK_DATE
    print(f"Total Data range: {start_date} - {end_date}")

    symbols = config.PORTFOLIO

    dataLoader = DataLoader(symbols, start_date, end_date)
    data: df = dataLoader.getDataFromCSV()
    data: df = dataLoader.enhanceWithApiData(data)
    data: df = dataLoader.fillna(data)
    dataLoader.saveAllData()
    print(data.tail())

    optimizer = Optimizer(config.OPTIMIZE_BACK_PERIOD_DAYS)

    # Assess the portfolio
    allocations, cumReturn, avgDailyReturn, stdDailyReturn, sharpeRatio = optimizer.optimizePortfolio(symbols,
                                                                                                      data,
                                                                                                      gen_plot=True,
                                                                                                      bmSymbol='CCi30')

    # Print statistics
    print()
    print("Allocations:")
    allocationsString = ["{:.2f}".format(alloc) for alloc in allocations]
    for i, sym in enumerate(symbols):
        print(f'{sym} {allocationsString[i]}')
    print()
    print(f"Sharpe Ratio: {sharpeRatio}")
    print(f"Volatility (stdev of daily returns): {stdDailyReturn}")
    print(f"Average Daily Return: {avgDailyReturn}")
    print(f"Cumulative Return: {cumReturn}")
    plt.show()
