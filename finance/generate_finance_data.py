import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)

product_types = ["艺术摆件", "玻璃灯饰", "装饰板", "定制工艺品"]

start_date = datetime(2025, 1, 1)

data = []

for i in range(300):

    date = start_date + timedelta(days=np.random.randint(0, 240))
    product = random.choice(product_types)

    # ===== 成本结构（核心）=====
    material_cost = np.random.uniform(4, 25)
    labor_cost = np.random.uniform(3, 18)
    energy_cost = np.random.uniform(2, 12)

    unit_cost = material_cost + labor_cost + energy_cost

    # ===== 产品定价逻辑（市场策略）=====
    markup_map = {
        "艺术摆件": (1.5, 2.2),
        "玻璃灯饰": (1.8, 3.0),
        "装饰板": (1.3, 1.8),
        "定制工艺品": (2.0, 3.8)
    }

    markup = np.random.uniform(*markup_map[product])
    unit_price = unit_cost * markup

    # ===== 生产规模波动 =====
    quantity = int(np.random.normal(60, 25))
    quantity = max(5, quantity)

    revenue = unit_price * quantity
    total_cost = unit_cost * quantity
    profit = revenue - total_cost

    profit_margin = profit / revenue if revenue > 0 else 0
    roi = profit / total_cost if total_cost > 0 else 0

    data.append([
        date, product, unit_cost, unit_price,
        quantity, revenue, total_cost, profit,
        profit_margin, roi
    ])

df = pd.DataFrame(data, columns=[
    "date","product_type","unit_cost","unit_price",
    "quantity","revenue","total_cost","profit",
    "profit_margin","roi"
])

df.to_csv("finance/finance_data.csv", index=False)

print("Finance dataset generated:", df.shape)