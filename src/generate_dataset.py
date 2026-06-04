import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ========== 1. 生成虚拟数据 ==========
np.random.seed(42)

n = 300

temperature = np.random.randint(650, 950, n)
time = np.random.randint(10, 120, n)

# 模拟“工艺效果评分”（核心逻辑：存在最优区间）
effect = (
    100
    - np.abs(temperature - 820) * 0.12
    - np.abs(time - 60) * 0.18
    + np.random.normal(0, 5, n)
)

effect = np.clip(effect, 40, 100)

df = pd.DataFrame({
    "temperature": temperature,
    "time": time,
    "effect": effect
})

print("数据预览：")
print(df.head())

# ========== 2. 温度 vs 效果 ==========
temp_group = df.groupby("temperature")["effect"].mean()

plt.figure(figsize=(10,5))
plt.plot(temp_group.index, temp_group.values)
plt.title("Temperature vs Effect")
plt.xlabel("Temperature (°C)")
plt.ylabel("Effect Score")
plt.grid()
plt.show()

# ========== 3. 时间 vs 效果 ==========
time_group = df.groupby("time")["effect"].mean()

plt.figure(figsize=(10,5))
plt.bar(time_group.index, time_group.values)
plt.title("Time vs Effect")
plt.xlabel("Time (min)")
plt.ylabel("Effect Score")
plt.show()

# ========== 4. 热力图 ==========
pivot = df.pivot_table(
    values="effect",
    index="temperature",
    columns="time",
    aggfunc="mean"
)

plt.figure(figsize=(12,8))
sns.heatmap(pivot, cmap="YlOrRd")
plt.title("Temperature-Time Effect Heatmap")
plt.show()

# ========== 5. 保存数据 ==========
df.to_csv("glass_fake_data.csv", index=False)

print("完成：数据 + 可视化生成成功")