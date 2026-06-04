import pandas as pd

df = pd.read_csv("finance/finance_data.csv")
df["date"] = pd.to_datetime(df["date"])

# ================= KPI =================
def get_kpis(df):
    return {
        "total_revenue": df["revenue"].sum(),
        "total_profit": df["profit"].sum(),
        "avg_margin": df["profit_margin"].mean(),
        "avg_roi": df["roi"].mean(),
        "best_product": df.groupby("product_type")["profit"].sum().idxmax()
    }

# ================= 月度趋势 =================
def monthly_trend(df):
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month")[["revenue","total_cost","profit"]].sum()

# ================= 产品分析 =================
def product_analysis(df):
    return df.groupby("product_type").agg({
        "revenue":"sum",
        "profit":"sum",
        "roi":"mean"
    }).reset_index()