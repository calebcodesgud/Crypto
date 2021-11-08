import requests
from pandas import DataFrame as df, read_csv, Series, to_datetime
from io import StringIO
import numpy as np


class cci30(object):

    def __init__(self):
        self._CCI30_INDEX_PRICE_URL = "https://cci30.com/ajax/getIndexHistory.php"
        self._CCI30_CONSTITUENTS_URL = "https://cci30.com/ajax/getMonthlyPropWeightHistoryProd.php"

    def getIndexPrices(self) -> Series:
        """
        Retrieves and returns CCi30 index value for every day.

        :return: Series, the index value.

        :raise Exception: if the get request fails
        """
        response = requests.get(self._CCI30_INDEX_PRICE_URL)
        if response.status_code == 200:
            cci30Series = read_csv(StringIO(response.text), sep=',', index_col='Date')['Close']
            cci30Series.index = to_datetime(cci30Series.index)
            cci30Series = cci30Series.rename("CCi30")
            return cci30Series
        else:
            raise Exception('Getting index value failed!')

    def getIndexConstituents(self) -> df:
        """
        Retrieves and returns CCi30 index constituents and their weights for each month.

        :return: DataFrame, the index weights.

        :raise Exception: if the get request fails
        """
        response = requests.get(self._CCI30_CONSTITUENTS_URL)
        if response.status_code == 200:
            cci30Df: df = read_csv(StringIO(response.text), sep=',')
            cci30Df['Weight in Index'] = cci30Df['Weight in Index'].apply(
                lambda weightStr: np.float(weightStr.replace('%', '')) / 100
            )
            cci30Df = cci30Df.pivot(index='Date', columns='Coin', values='Weight in Index')
            cci30Df.index = to_datetime(cci30Df.index)
            cci30Df.fillna(value=0.0)
            return cci30Df
        else:
            raise Exception('Getting index constituents failed!')
