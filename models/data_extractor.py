import os
import pandas as pd

from pandas import DataFrame
from tvDatafeed import TvDatafeed, Interval

DEFAULT_CSV_NAME = "trading_data.csv"
DEFAULT_DATA_DIR_NAME = "data"


class DataLoader:
    def __init__(
        self, dirname: str = DEFAULT_DATA_DIR_NAME, filename: str = DEFAULT_CSV_NAME
    ):
        self.dirname = dirname
        self.path = os.path.join(dirname, filename)

    def load_data(self) -> DataFrame:
        self._get_data()
        df = pd.read_csv(self.path)
        return df

    def _get_data(self) -> None:
        if not os.path.exists(self.path):
            os.mkdir(self.dirname)
            self._store_trading_data()

    def _store_trading_data(self) -> None:
        tv = TvDatafeed()

        working_data = tv.get_hist(
            symbol="BTCUSDT",
            exchange="BINANCE",
            interval=Interval.in_15_minute,
            n_bars=672,  # 96 - 1 day, 672 - 1 week, 2688 - 1 month (in_15_minute)
        )
        working_data = working_data.drop(["symbol"], axis=1)
        working_data.reset_index(inplace=True)

        working_data.to_csv(
            self.path, header=["date", "open", "high", "low", "close", "volume"]
        )