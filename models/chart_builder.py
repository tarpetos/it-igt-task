from lightweight_charts import Chart
from pandas import DataFrame


class TradingViewBuilder:
    def __init__(self, dataframe: DataFrame):
        self.df = dataframe
        self.chart = Chart()

    def build_view(self) -> None:
        self.chart.set(self.df)
        self.chart.show(block=True)