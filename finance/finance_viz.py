import matplotlib.pyplot as plt
import seaborn as sns

def plot_profit_trend(monthly_df):
    fig, ax = plt.subplots()
    ax.plot(monthly_df.index.astype(str), monthly_df["profit"])
    ax.set_title("Monthly Profit Trend")
    plt.xticks(rotation=45)
    return fig


def plot_cost_structure(df):
    cost = [
        df["unit_cost"].sum() * 0.4,
        df["unit_cost"].sum() * 0.35,
        df["unit_cost"].sum() * 0.25
    ]

    labels = ["Material", "Labor", "Energy"]

    fig, ax = plt.subplots()
    ax.pie(cost, labels=labels, autopct="%1.1f%%")
    ax.set_title("Cost Structure")
    return fig


def plot_product_profit(df):
    fig, ax = plt.subplots()
    sns.barplot(data=df, x="product_type", y="profit", ax=ax)
    ax.set_title("Product Profit Comparison")
    plt.xticks(rotation=30)
    return fig