from itertools import chain
from typing import List, Any, Optional, Dict, Tuple, Union

from pandas import DataFrame

from .chart_builder import TradingViewBuilder
from .data_extractor import DataLoader
from .strategy import Strategy


class StrategyCalculator:
    def __init__(self, strategy: Strategy, data: DataFrame):
        self.df = data
        self.start_price = strategy.start_price
        self.input_percents = strategy.input_percents
        self.output_percents = strategy.output_percents
        self.balance_usdt = strategy.usdt
        self.start_balance = strategy.usdt
        self.balance_crypto = strategy.crypto
        self.commission = strategy.commission
        self.allowed_deviation = strategy.deviation
        self.check_percents_length()

    def check_percents_length(self) -> None:
        if len(self.input_percents) != len(self.output_percents):
            raise ValueError(
                "The number of percentage values in the inputs must be "
                "equal to the number of percentage values in the outputs!\n"
                f"len({self.input_percents}) != len({self.output_percents})"
            )

    def get_buy_prices(self) -> List[float]:
        price = self.start_price
        return [
            round(price := self.calculate_price(price, buy_percent), 2)
            for buy_percent in self.input_percents
        ]

    def calculate_price(self, price: float, price_change: float) -> float:
        price = price + self.start_price * price_change
        return price

    def get_sell_prices(self) -> List[float]:
        buy_lst = self.get_buy_prices()
        return [
            round(buy_price * (1 + sell_percent), 2)
            for buy_price, sell_percent in zip(buy_lst, self.output_percents)
        ]

    def update_data_list(self) -> List[float | Any]:
        open_column = self.df["open"]
        high_column = self.df["high"]
        low_column = self.df["low"]
        close_column = self.df["close"]

        all_values = list(zip(open_column, high_column, low_column, close_column))
        cleared_list = list(chain(*all_values))
        start_val_index = cleared_list.index(self.start_price)
        cleared_list = cleared_list[start_val_index:]
        return cleared_list

    def make_transactions(
        self,
    ) -> Tuple[Dict[float, Dict[str, float]], Dict[float, Dict[str, float]]]:
        history_data = self.update_data_list()
        section_number = len(self.input_percents)
        successful_buy_orders = self.try_to_buy(history_data, section_number)
        min_sell_history_index = self.find_min_allowed_sell_index(successful_buy_orders)
        successful_sell_orders = self.try_to_sell(
            history_data, successful_buy_orders, min_sell_history_index
        )

        return successful_buy_orders, successful_sell_orders

    def try_to_buy(
        self, history_data: List[float], section_number: int
    ) -> Dict[int, Dict[str, float]]:
        all_buy_prices = self.get_buy_prices()
        successful_operations = {}
        order_price = self.balance_usdt / section_number
        for index, buy_price in enumerate(all_buy_prices):
            real_buy_price = self.find_closest_value(history_data, buy_price)
            if real_buy_price is not None:
                self.balance_usdt -= order_price
                temp = order_price / real_buy_price
                self.balance_crypto += temp
                successful_operations[index] = {
                    "buy_price": real_buy_price,
                    "crypto_amount": temp,
                    "history_index": history_data.index(real_buy_price),
                }

        return successful_operations

    def try_to_sell(
        self,
        history_data: List[float],
        successful_buy_orders: Dict[int, Dict[str, float]],
        min_index: int,
    ) -> Dict[int, Dict[str, float]]:
        all_sell_prices = self.get_sell_prices()
        successful_operations = {}
        for index_key in successful_buy_orders:
            real_sell_price = self.find_closest_value(
                history_data, all_sell_prices[index_key], min_sell_index=min_index
            )
            if real_sell_price is not None:
                self.balance_crypto -= successful_buy_orders[index_key]["crypto_amount"]
                temp = (
                    successful_buy_orders[index_key]["crypto_amount"] * real_sell_price
                )
                self.balance_usdt += (
                    successful_buy_orders[index_key]["crypto_amount"] * real_sell_price
                )
                successful_operations[index_key] = {
                    "sell_price": real_sell_price,
                    "usdt_amount": temp,
                    "history_index": history_data.index(real_sell_price),
                }

        return successful_operations

    def find_closest_value(
        self, lst: List[float], target: float, min_sell_index: int = -1
    ) -> Optional[float]:
        closest_value = None
        min_difference = float("inf")

        for value in lst:
            difference = abs(value - target)
            if difference < min_difference:
                min_difference = difference
                closest_value = value

        if min_sell_index != -1:
            closest_value_index = lst.index(closest_value)
            if closest_value_index >= min_sell_index:
                if target == closest_value or (
                    target * (1 - self.allowed_deviation)
                    <= closest_value
                    <= target * (1 + self.allowed_deviation)
                    and target not in lst[closest_value_index:]
                ):
                    return closest_value
            if min_sell_index != len(lst) - 1:
                return lst[min_sell_index + 1]
            return lst[-1]

        if (
            target * (1 - self.allowed_deviation)
            <= closest_value
            <= target * (1 + self.allowed_deviation)
        ):
            return closest_value

    def print_statistics(
        self,
        imitation_result: Tuple[
            Dict[float, Dict[str, float]], Dict[float, Dict[str, float]]
        ],
    ) -> None:
        order_price = self.start_balance / len(self.input_percents)
        print(f"Your wallet money content: {self.start_balance}")
        print(f"Strategy start price: {self.start_price}")
        print(
            f"Step percents for inputs: "
            f"{', '.join([str(self.printable_percents(value)) + '%' for value in self.input_percents])}"
        )
        print(
            f"Step percents for inputs: "
            f"{', '.join([str(self.printable_percents(value)) + '%' for value in self.output_percents])}\n"
        )

        print(f"You should place {len(imitation_result[0])} orders for buying.")
        for count, item in enumerate(imitation_result[0].values(), 1):
            print(
                f"Buy order price №{count} must be equal to {item['buy_price']}$ per coin. "
                f"You will get {item['crypto_amount']:.9f} crypto coins. "
                f"Price for that order will be equal to {order_price:.2f}$"
            )

        print(f"\nYou should place {len(imitation_result[1])} orders for selling.")
        successful_trades_counter = 0
        sells_lst = []
        for count, item in enumerate(imitation_result[1].values(), 1):
            if item["usdt_amount"] > order_price:
                successful_trades_counter += 1
            print(
                f"Sell order price №{count} must be equal to {item['sell_price']}$ per coin. "
                f"You will get {item['usdt_amount']:.2f} dollars."
            )
            sells_lst.append(item["usdt_amount"])

        print(f"\nNumber of profitable trades: {successful_trades_counter}")

        print(
            f"Your total profit will be equal "
            f"{self.balance_usdt:.2f}$ - {self.start_balance:.2f}$ = {self.balance_usdt - self.start_balance:.2f}$. "
            f"Or +{(self.balance_usdt * 100 / self.start_balance) - 100:.3f}%"
        )

        commission = (
            len(imitation_result[0]) * order_price + sum(sells_lst)
        ) * self.commission
        print(f"Commission for trades: {commission:.3f}$")
        print(
            f"Pure profit: {self.balance_usdt - commission}. "
            f"Or +{((self.balance_usdt - commission) * 100 / self.start_balance) - 100:.3f}%"
        )

    @staticmethod
    def printable_percents(percent: float):
        return abs(percent * 100)

    @staticmethod
    def find_min_allowed_sell_index(
        data: Dict[int, Dict[str, Union[float, int]]]
    ) -> int:
        min_allowed_sell_index = float("-inf")

        for key, value in data.items():
            history_index = value["history_index"]
            if history_index > min_allowed_sell_index:
                min_allowed_sell_index = history_index

        return min_allowed_sell_index


class StrategyStarter:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def execute(self) -> None:
        data = DataLoader()
        dataframe = data.load_data()

        trader = StrategyCalculator(self.strategy, dataframe)
        results = trader.make_transactions()
        trader.print_statistics(results)

        chart_view = TradingViewBuilder(dataframe)
        chart_view.build_view()
