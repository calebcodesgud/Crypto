import pandas as pd
import datetime as dt
import util
import cbpro
import numpy as np
from pandas import DataFrame as df, DatetimeIndex, date_range
from datetime import datetime
from util import util


class coinbase:

    def __init__(self, CB_GRANULARITY_CONST):
        self.CB_GRANULARITY_CONST = CB_GRANULARITY_CONST
        self.cb_client = cbpro.PublicClient()

    def CB_paginate_historic(self, symbol: str, minDate: datetime, maxDate: datetime) -> df:
        dates: DatetimeIndex = date_range(minDate, maxDate)
        result: df = df(index=dates, columns=["close"], data=np.nan, dtype=np.float)
        PAGE_SIZE = 250
        diff = maxDate - minDate
        if diff.days >= PAGE_SIZE:  # paginate request
            min_date_temp = minDate
            while diff.days >= PAGE_SIZE:
                max_date_temp = min_date_temp + dt.timedelta(PAGE_SIZE)
                result.update(self.CB_get_historic(symbol, min_date_temp, max_date_temp)["close"], overwrite=False)
                min_date_temp = min_date_temp + dt.timedelta(PAGE_SIZE)
                diff = maxDate - min_date_temp
            result.update(self.CB_get_historic(symbol, min_date_temp, maxDate)["close"], overwrite=False)
        else:
            result.update(self.CB_get_historic(symbol, minDate, maxDate)["close"], overwrite=False)
        result.rename(columns={"close": symbol}, inplace=True)
        print(f'Retrieved {int(result.notna().sum())} days of data for {symbol} from coinbase')
        return result

    def CB_get_historic(self, sym: str, min_date: datetime, max_date: datetime) -> df:
        min_date_ISO, max_date_ISO = util.ISO_date_reformat(min_date, max_date)
        response = pd.DataFrame(
            self.cb_client.get_product_historic_rates(sym + '-USD', min_date_ISO, max_date_ISO, self.CB_GRANULARITY_CONST),
            columns=["date", "low", "high", "open", "close", "volume"]
        )
        response["date"] = pd.to_datetime(response["date"], unit='s')
        response.set_index("date", inplace=True)
        response = response.sort_index()
        return response

    def check_if_available(self, sym: str) -> bool:
        return 'price' in self.cb_client.get_product_ticker(sym + '-USD')
