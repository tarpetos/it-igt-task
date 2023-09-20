# Trading Simulation Software

## Overview

This software provides a trading simulation platform for conducting trading strategy simulations on the Binance exchange. It allows users to implement and test their trading strategies using historical data in a CSV format. The simulation is based on the specified strategy and provides a trading view for analysis.

## Features
- Strategy Simulation: users can define and implement their trading strategies within the simulation environment.
- Binance Integration: integration with Binance enables realistic trading simulations using Binance historical data.
- Trading View: the software offers a trading view that allows users to analyze simulated trades and results.

## Requirements
- Python 3.11

## Setup
1. **Clone the repository or download the source code.**
2. **Install the required dependencies using pip:** ```pip install -r requirements.txt```
3. **Install separately *tvdatafeed*:** ```pip install --upgrade --no-cache-dir git+https://github.com/rongardF/tvdatafeed.git```

## Usage
Run the program by executing the main script: ```python3 main.py```

## Example
Import the modules and initialize with your amount of money and the strategy that will be used for trading.
```python
from models.strategy import Strategy
from models.strategy_builder import StrategyStarter

strategy_obj = Strategy(
    usdt=1000,
    start_price=26233.47,
    input_percents=[-0.0025, -0.005, -0.01],
    output_percents=[0.02, 0.03, 0.04],
)
start_strategy = StrategyStarter(strategy_obj)
start_strategy.execute()
```
---
![img.png](images/img.png)
![img_1.png](images/img_1.png)