import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="工艺分析模块")

st.title("🔥 玻璃热熔工艺分析系统")

# ================= 数据读取 =================
df = pd.read_csv("glass_fake_data.csv")

st.subheader("📄 数据预览")
st.dataframe(df.head())

# ================= 温度影响 =================
st.subheader("🌡️ 温度对效果影响")

if "temperature" in df.columns and "quality_score" in df.columns:
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x="temperature", y="quality_score", ax=ax)
    ax.set_title("Temperature vs Quality")
    st.pyplot(fig)

# ================= 时间影响 =================
st.subheader("⏱️ 时间对效果影响")

if "time" in df.columns and "quality_score" in df.columns:
    fig, ax = plt.subplots()
    sns.lineplot(data=df, x="time", y="quality_score", ax=ax)
    ax.set_title("Time Effect on Quality")
    st.pyplot(fig)

# ================= 热力图 =================
st.subheader("🔥 参数热力相关性")

fig, ax = plt.subplots()
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# ================= 图片展示 =================
st.subheader("📊 工艺可视化图")

st.image("figures/temperature_effect.png")
st.image("figures/time_effect.png")
st.image("figures/A heatmap.png")