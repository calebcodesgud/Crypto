import numpy as np
from typing import List

from api.apis.coinbase import coinbase
from api.apis.kraken import kraken
from api.apis.cci30 import cci30
from config import config
from datetime import datetime
from pandas import DataFrame as df, date_range, DatetimeIndex, Series


class ApiHub(object):
    COIN: str = 'COIN'
    KRKN: str = 'KRKN'

    def __init__(self):
        CB_GRANULARITY_CONST = 86400
        self.cb = coinbase(CB_GRANULARITY_CONST)
        self.krkn = kraken()

    def aggregateFromExhanges(self, symbol: str) -> df:
        """
        Retrieves closing data for the symbol from crypto currency exchanges until there is no missing
        data within the time frame.

        :param symbol: the string, a crypto currency symbol.

        :return: a dataframe containing the price history, with one column by the name of the symbol, indexed by datetime

        """
        minDate: datetime = config.MAX_LOOKBACK_DATE
        maxDate: datetime = datetime.today()
        exchangeSymbolOn: List[str] = []

        if self.cb.check_if_available(symbol):
            exchangeSymbolOn.append(self.COIN)
        if self.krkn.check_if_available(symbol):
            exchangeSymbolOn.append(self.KRKN)
        if len(exchangeSymbolOn) == 0:
            return df()

        print(f'{symbol}: is on {exchangeSymbolOn}')

        dates: DatetimeIndex = date_range(minDate, maxDate)
        results: df = df(index=dates, columns=[symbol], data=np.nan, dtype=np.float)

        if self.COIN in exchangeSymbolOn:
            response = self.cb.CB_paginate_historic(symbol, minDate, maxDate)
            results.update(response, overwrite=False)
        if self.KRKN in exchangeSymbolOn and (results[symbol].isna()).sum() != 0:
            response = self.krkn.get_historical_data(symbol, minDate, maxDate)
            results.update(response, overwrite=False)
        return results

    def getCCi30(self) -> df:
        resultDf: df = df(cci30().getIndexPrices())
        resultDf = resultDf.reindex(index=resultDf.index[::-1])
        return resultDf




