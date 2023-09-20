from dataclasses import dataclass
from typing import List


@dataclass
class Strategy:
    start_price: float
    input_percents: List[float]
    output_percents: List[float]
    usdt: float
    crypto: float = 0
    commission: float = 0.00075
    deviation: float = 0.001
