from models.strategy import Strategy
from models.strategy_builder import StrategyStarter


def main() -> None:
    strategy_obj = Strategy(
        usdt=1000,
        start_price=26233.47,
        input_percents=[-0.0025, -0.005, -0.01],
        output_percents=[0.02, 0.03, 0.04],
    )
    start_strategy = StrategyStarter(strategy_obj)
    start_strategy.execute()


if __name__ == "__main__":
    main()
