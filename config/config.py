import datetime as dt
import json
from typing import Dict, List

_jsonFile = open('resources/config.json')
_configDict: Dict = json.load(_jsonFile)
_jsonFile.close()

# furthest back date for backtesting
_dateStr: str = _configDict["MAX_LOOKBACK_DATE"]
_dateStrSplit: List[str] = _dateStr.split('-')
MAX_LOOKBACK_DATE = dt.datetime(int(_dateStrSplit[0]), int(_dateStrSplit[1]), int(_dateStrSplit[2]))

# how far back to go for the optimization window
OPTIMIZE_BACK_PERIOD_DAYS = _configDict["OPTIMIZE_BACK_PERIOD_DAYS"]

# cryptos to consider allocations for (must include BTC)
PORTFOLIO = _configDict["PORTFOLIO"]

RISK_FREE_RATE_APY = _configDict["RISK_FREE_RATE_APY"]  # rate for dai deposit on Compound.finance
