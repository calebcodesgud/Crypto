from typing import List
from datetime import datetime
from pandas import DataFrame as df, read_csv, date_range, Series
from api.ApiHub import ApiHub
from config import config
import numpy as np


class DataLoader(object):

    def __init__(self, symbols: List[str], minDate: datetime, maxDate: datetime):
        self.apiHub = ApiHub()
        allDataBounded: df = df(index=date_range(config.MAX_LOOKBACK_DATE, maxDate))
        self.allData: df = read_csv(f'data/cryptoData/historic.csv', index_col="date", parse_dates=True, na_values=["nan"])
        allDataBounded[list(self.allData.columns)] = np.nan
        allDataBounded.update(self.allData, overwrite=False)
        self.allData = allDataBounded
        wantedDates: df = df(index=date_range(minDate, maxDate), columns=symbols)
        wantedDates.update(self.allData, overwrite=False)  # get only dates wanted
        self.wantedDates = wantedDates

    def getDataFromCSV(self) -> df:
        return self.wantedDates

    def enhanceWithApiData(self, data: df) -> df:
        symbols: List[str] = list(data.columns)
        for symbol in symbols:
            countNan: int = (data[symbol].isna()).sum()
            print(f'{symbol} is missing {countNan} days')
            if countNan > 0:
                if symbol == 'CCi30':
                    exchangeData: df = self.apiHub.getCCi30()
                else:
                    exchangeData: df = self.apiHub.aggregateFromExhanges(symbol)
                if exchangeData is not None:
                    if symbol not in list(self.allData.columns):
                        self.allData[symbol] = np.nan
                    self.allData.update(exchangeData, overwrite=False)
        data.update(self.allData)
        return data

    def fillna(self, data: df) -> df:
        data.fillna(method="ffill", inplace=True)
        data.fillna(method="bfill", inplace=True)
        self.allData.update(data, overwrite=False)
        return data

    def saveAllData(self):
        self.allData.to_csv('data/cryptoData/historic.csv', index_label='date')
