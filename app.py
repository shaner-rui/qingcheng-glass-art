import streamlit as st

st.set_page_config(
    page_title="青橙焕艺",
    page_icon="♻️",
    layout="wide"
)

# ==========================
# 首页Banner
# ==========================

st.image(
    "images/banner.png",
    use_container_width=True
)

st.title("♻️ 青橙焕艺")

st.subheader(
    "废旧玻璃热熔再生与数字化分析平台"
)

st.markdown("---")

# ==========================
# 项目简介
# ==========================

st.header("📖 项目简介")

col1, col2 = st.columns([2,1])

with col1:

    st.write("""
    **青橙焕艺** 致力于废旧玻璃资源循环利用。

    通过玻璃热熔工艺，将废弃彩色玻璃加工成：

    - 热熔花瓶
    - 艺术灯具
    - 创意摆件
    - 文创艺术产品

    项目融合：

    - 环保循环经济
    - 艺术设计
    - 数据分析
    - AI辅助决策

    构建玻璃热熔工艺数据库与智能分析平台，
    推动传统手工艺数字化升级。
    """)

with col2:

    st.image(
        "images/workshop.png",
        caption="玻璃热熔工坊",
        use_container_width=True
    )

st.markdown("---")

# ==========================
# 产品展示
# ==========================

st.header("🎨 产品展示")

col1, col2, col3 = st.columns(3)

with col1:
    st.image(
        "images/vase.png",
        caption="热熔艺术花瓶",
        use_container_width=True
    )

with col2:
    st.image(
        "images/lamp.png",
        caption="艺术灯具",
        use_container_width=True
    )

with col3:
    st.image(
        "images/art.jpg",
        caption="玻璃艺术摆件",
        use_container_width=True
    )

st.markdown("---")

# ==========================
# 工艺数据库
# ==========================

st.header("🗄️ 玻璃热熔工艺数据库")

st.success("""
数据库建设内容：

✔ 实验编号管理

✔ 玻璃类型管理

✔ 温度参数记录

✔ 时间参数记录

✔ 工艺分类管理

✔ 效果评分体系

✔ 产品图片库

✔ 工艺案例库
""")

st.markdown("---")

# ==========================
# 数据分析
# ==========================

st.header("📊 数据分析平台")

st.image(
    "images/analysis_bg.png",
    caption="玻璃热熔工艺数据分析平台",
    use_container_width=True
)

try:

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            "figures/temperature_effect.png",
            caption="温度-效果分析"
        )

        st.image(
            "figures/time_effect.png",
            caption="时间-效果分析"
        )

    with col2:
        st.image(
            "figures/heatmap.png",
            caption="温度-时间热力图"
        )

except:
    st.warning("等待实验数据接入...")

st.markdown("---")

# ==========================
# AI规划
# ==========================

st.header("🤖 AI智能工艺推荐系统")

col1, col2 = st.columns([2,1])

with col1:

    st.write("""
    未来计划构建智能工艺推荐系统。

    输入参数：

    - 玻璃类型
    - 热熔温度
    - 热熔时间

    系统输出：

    - 效果预测
    - 工艺推荐
    - 风险预警
    - 历史案例匹配

    最终实现：

    **玻璃热熔工艺数字化与智能化决策。**
    """)

with col2:

    st.image(
        "images/ai_recommendation.jpg",
        use_container_width=True
    )

st.markdown("---")

# ==========================
# 项目优势
# ==========================

st.header("🚀 项目优势")

st.metric(
    label="资源循环利用",
    value="100%"
)

st.metric(
    label="数字化工艺管理",
    value="已启动"
)

st.metric(
    label="AI辅助决策",
    value="规划中"
)

st.markdown("---")

# ==========================
# 联系我们
# ==========================

st.header("📞 联系我们")

st.info("""
🏫 沈阳大学

♻️ 青橙焕艺团队

🌱 环保循环经济 × 艺术设计 × 数据分析 × AI辅助决策
""")