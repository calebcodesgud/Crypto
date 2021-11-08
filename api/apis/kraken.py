import krakenex
from pykrakenapi import KrakenAPI
from pandas import DataFrame as df, date_range
from datetime import datetime
from pykrakenapi.pykrakenapi import KrakenAPIError


class kraken:

    def __init__(self):
        api = krakenex.API()
        self.k = KrakenAPI(api)
        self.k.retry = 0

    def get_historical_data(self, symbol: str, minDate: datetime, maxDate: datetime) -> df:
        result = df(index=date_range(minDate, maxDate), columns=["close"])
        result.update(self.k.get_ohlc_data(f'{symbol}USD', interval=1440)[0]['close'], overwrite=False)
        result.rename(columns={"close": symbol}, inplace=True)
        print(f'Retrieved {int(result.notna().sum())} days of data for {symbol} from kraken')
        return result

    def check_if_available(self, symbol):
        try:
            self.k.get_ticker_information(f'{symbol}USD')
            return True
        except KrakenAPIError as err:
            return False
