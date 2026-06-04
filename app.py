import base64
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# =========================
# 基础配置
# =========================

st.set_page_config(
    page_title="青橙焕艺 | Glass Recycling AI Platform",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "glass_experiment_numeric_only.csv"
IMAGE_DIR = BASE_DIR / "images"
FIGURE_DIR = BASE_DIR / "figures"


# =========================
# 工具函数
# =========================

def img_to_uri(path: Path):
    if not path.exists():
        return ""
    mime = "image/jpeg" if path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


@st.cache_data
def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()


def section_title(tag, title, desc):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-tag">{tag}</div>
            <h2>{title}</h2>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def glass_card(icon, title, text):
    st.markdown(
        f"""
        <div class="glass-card reveal">
            <div class="icon">{icon}</div>
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def image_card(path, title, desc):
    uri = img_to_uri(path)
    if uri:
        st.markdown(
            f"""
            <div class="image-card reveal">
                <img src="{uri}" />
                <div class="image-mask">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="image-card image-missing reveal">
                <div>
                    <h3>{title}</h3>
                    <p>请将图片放入 images 文件夹：{path.name}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def recommend(product_type, material, target_effect, temp):
    if product_type == "花瓶":
        base_temp = "760℃ - 770℃"
        product_tip = "花瓶需要一定体积感，建议保持玻璃局部堆叠，不要完全熔平。"
    elif product_type == "灯具":
        base_temp = "755℃ - 765℃"
        product_tip = "灯具更重视透光度，建议使用透明玻璃或浅色玻璃搭配。"
    elif product_type == "装饰画":
        base_temp = "750℃ - 765℃"
        product_tip = "装饰画适合保留颗粒肌理，温度不宜过高。"
    elif product_type == "艺术摆件":
        base_temp = "760℃ - 775℃"
        product_tip = "艺术摆件可适当增强体积感，但要避免形态塌陷。"
    else:
        base_temp = "755℃ - 770℃"
        product_tip = "综合产品建议先做小样测试，再扩大成品尺寸。"

    if temp >= 790:
        risk = "当前温度偏高，容易导致玻璃过度熔融，颗粒感和体积感下降。建议明显降温。"
        score = 45
    elif 775 <= temp < 790:
        risk = "当前温度仍偏高，颗粒边界可能变弱，建议向 760℃ 附近调整。"
        score = 62
    elif 755 <= temp < 775:
        risk = "当前温度较适中，适合形成颗粒感、体积感和较好的透光表现。"
        score = 88
    else:
        risk = "当前温度可能偏低，玻璃融合度不足，成品牢固性可能下降。"
        score = 58

    if target_effect == "颗粒感明显":
        effect_tip = "应减少过度熔融，重点保留玻璃颗粒边界。"
    elif target_effect == "透光度强":
        effect_tip = "应选择透明或浅色玻璃，并避免颜色堆叠过厚。"
    elif target_effect == "体积感强":
        effect_tip = "应控制局部堆叠厚度，让玻璃融合但不完全摊平。"
    else:
        effect_tip = "建议平衡颗粒感、透光度和体积感，适合比赛展示。"

    if material == "透明玻璃":
        material_tip = "透明玻璃适合灯具、窗饰和透光艺术板。"
    elif material == "彩色玻璃":
        material_tip = "彩色玻璃视觉表现强，适合装饰画和艺术摆件。"
    elif material == "混合玻璃":
        material_tip = "混合玻璃层次丰富，但要注意颜色过杂。"
    else:
        material_tip = "建议先做小样实验，记录温度和最终效果。"

    return base_temp, risk, score, product_tip, effect_tip, material_tip


df = load_data()


# =========================
# 全局 CSS
# =========================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');

:root {
    --cyan: #25f4ee;
    --orange: #ff9f43;
    --dark: #06131f;
    --deep: #020711;
    --white: #f6fbff;
}

html, body, .stApp {
    font-family: 'Noto Sans SC', sans-serif;
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(circle at 8% 12%, rgba(37,244,238,0.28), transparent 26%),
        radial-gradient(circle at 88% 14%, rgba(255,159,67,0.24), transparent 24%),
        radial-gradient(circle at 50% 95%, rgba(37,244,238,0.16), transparent 35%),
        linear-gradient(135deg, #020711 0%, #071827 48%, #14101f 100%);
    color: var(--white);
}

.block-container {
    max-width: 1280px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

/* 弱化原来的线条分隔感 */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(37,244,238,0.25), rgba(255,159,67,0.25), transparent);
    margin: 3rem 0;
}

/* 顶部导航 */
.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 1.2rem;
    padding: 0.75rem 1.2rem;
    border-radius: 999px;
    background: rgba(6, 19, 31, 0.72);
    border: 1px solid rgba(255,255,255,0.13);
    backdrop-filter: blur(20px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 14px 42px rgba(0,0,0,0.25);
}

.nav-logo {
    font-weight: 900;
    font-size: 1.05rem;
    background: linear-gradient(90deg, var(--cyan), #fff, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links a {
    color: rgba(246,251,255,0.82) !important;
    text-decoration: none;
    margin-left: 1.2rem;
    font-size: 0.92rem;
    transition: 0.25s;
}

.nav-links a:hover {
    color: var(--cyan) !important;
    text-shadow: 0 0 14px rgba(37,244,238,0.6);
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    min-height: 650px;
    border-radius: 36px;
    padding: 5rem 3rem;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.13), rgba(255,159,67,0.12)),
        rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(18px);
    box-shadow: 0 28px 90px rgba(0,0,0,0.38);
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: linear-gradient(to bottom, rgba(0,0,0,0.9), transparent);
}

.hero::after {
    content: "";
    position: absolute;
    right: -130px;
    top: 55px;
    width: 520px;
    height: 520px;
    border-radius: 50%;
    background:
        radial-gradient(circle, rgba(37,244,238,0.34), rgba(255,159,67,0.16), transparent 68%);
    filter: blur(5px);
    animation: floatPlanet 7s ease-in-out infinite;
}

@keyframes floatPlanet {
    0%,100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(26px) scale(1.05); }
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 820px;
}

.hero-tag {
    display: inline-block;
    padding: 0.55rem 1rem;
    border-radius: 999px;
    color: var(--cyan);
    background: rgba(37,244,238,0.1);
    border: 1px solid rgba(37,244,238,0.32);
    font-weight: 800;
    letter-spacing: 0.12em;
    margin-bottom: 1.5rem;
}

.hero h1 {
    font-size: clamp(3rem, 7vw, 5.8rem);
    line-height: 1.02;
    margin: 0;
    font-weight: 900;
    background: linear-gradient(90deg, var(--cyan), #ffffff 48%, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero h2 {
    margin-top: 1.2rem;
    font-size: clamp(1.05rem, 2vw, 1.45rem);
    line-height: 1.85;
    color: rgba(246,251,255,0.82);
    font-weight: 500;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 2rem;
}

.hero-btn {
    padding: 0.9rem 1.3rem;
    border-radius: 16px;
    text-decoration: none !important;
    font-weight: 900;
    background: linear-gradient(135deg, var(--cyan), var(--orange));
    color: #04111f !important;
    transition: 0.28s;
}

.hero-btn-ghost {
    padding: 0.9rem 1.3rem;
    border-radius: 16px;
    text-decoration: none !important;
    font-weight: 900;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    color: #fff !important;
    transition: 0.28s;
}

.hero-btn:hover, .hero-btn-ghost:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 0 28px rgba(37,244,238,0.35);
}

/* 标题 */
.section-head {
    text-align: center;
    margin: 5rem auto 2rem;
    max-width: 860px;
}

.section-tag {
    color: var(--cyan);
    font-weight: 900;
    letter-spacing: 0.2em;
    font-size: 0.8rem;
}

.section-head h2 {
    margin: 0.35rem 0;
    font-size: clamp(2rem, 4vw, 2.8rem);
    font-weight: 900;
    background: linear-gradient(90deg, var(--cyan), #fff, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-head p {
    color: rgba(246,251,255,0.68);
    line-height: 1.8;
}

/* 卡片 */
.glass-card {
    height: 100%;
    min-height: 250px;
    padding: 1.5rem;
    border-radius: 28px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(20px);
    box-shadow: 0 18px 52px rgba(0,0,0,0.25);
    transition: 0.28s ease;
}

.glass-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(37,244,238,0.48);
    box-shadow: 0 0 32px rgba(37,244,238,0.22), 0 18px 52px rgba(0,0,0,0.35);
}

.icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}

.glass-card h3 {
    color: #fff;
    margin-bottom: 0.7rem;
    font-size: 1.25rem;
}

.glass-card p {
    color: rgba(246,251,255,0.72);
    line-height: 1.75;
}

/* 图片卡 */
.image-card {
    position: relative;
    height: 360px;
    border-radius: 30px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 24px 70px rgba(0,0,0,0.32);
    background: rgba(255,255,255,0.07);
    transition: 0.3s;
}

.image-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 0 36px rgba(255,159,67,0.22), 0 24px 70px rgba(0,0,0,0.4);
}

.image-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: 0.6s;
}

.image-card:hover img {
    transform: scale(1.08);
}

.image-mask {
    position: absolute;
    inset: auto 0 0 0;
    padding: 1.4rem;
    background: linear-gradient(to top, rgba(0,0,0,0.75), transparent);
}

.image-mask h3 {
    margin: 0;
    color: white;
}

.image-mask p {
    color: rgba(255,255,255,0.74);
    margin: 0.4rem 0 0;
}

.image-missing {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    border-style: solid;
}

/* 数据库太空区 */
.database-panel {
    padding: 1.4rem;
    border-radius: 32px;
    background:
        radial-gradient(circle at 10% 20%, rgba(37,244,238,0.20), transparent 28%),
        radial-gradient(circle at 88% 10%, rgba(255,159,67,0.20), transparent 25%),
        rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(20px);
    box-shadow: 0 24px 70px rgba(0,0,0,0.30);
}

.metric-box {
    padding: 1.2rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.13);
    text-align: center;
}

.metric-box h3 {
    color: var(--cyan);
    margin: 0;
    font-size: 2rem;
}

.metric-box p {
    color: rgba(246,251,255,0.68);
    margin: 0.3rem 0 0;
}

/* 推荐结果 */
.recommend-result {
    padding: 1.4rem;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.10));
    border: 1px solid rgba(255,255,255,0.16);
    margin-top: 1rem;
}

.recommend-result h3 {
    margin-top: 0;
    color: var(--cyan);
}

.recommend-result p {
    color: rgba(246,251,255,0.78);
    line-height: 1.7;
}

/* 联系我们 */
.contact-card {
    padding: 2.5rem;
    border-radius: 34px;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.14), rgba(255,159,67,0.14)),
        rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(20px);
    text-align: center;
    box-shadow: 0 24px 70px rgba(0,0,0,0.30);
}

.contact-card h2 {
    font-size: clamp(2rem, 5vw, 3rem);
    margin: 0;
    background: linear-gradient(90deg, var(--cyan), #fff, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.contact-card p {
    color: rgba(246,251,255,0.72);
    line-height: 1.8;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .navbar {
        border-radius: 20px;
        align-items: flex-start;
        flex-direction: column;
        gap: 0.6rem;
    }

    .nav-links a {
        margin-left: 0;
        margin-right: 0.8rem;
        font-size: 0.82rem;
    }

    .hero {
        min-height: auto;
        padding: 3rem 1.3rem;
        border-radius: 26px;
    }

    .hero h1 {
        font-size: 3rem;
    }

    .image-card {
        height: 270px;
    }
}
</style>
""",
    unsafe_allow_html=True
)


# =========================
# 顶部导航
# =========================

st.markdown(
    """
<div class="navbar">
    <div class="nav-logo">♻️ 青橙焕艺 Glass Recycling AI Platform</div>
    <div class="nav-links">
        <a href="#intro">项目简介</a>
        <a href="#database">工艺数据库</a>
        <a href="#gallery">图片展示</a>
        <a href="#recommend">产品推荐</a>
        <a href="#future">后期展望</a>
        <a href="#contact">联系我们</a>
    </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# Hero 首页
# =========================

banner_uri = img_to_uri(IMAGE_DIR / "banner.png")

st.markdown(
    f"""
<div class="hero">
    <div class="hero-content">
        <div class="hero-tag">GREEN DESIGN · AI DATA · GLASS ART</div>
        <h1>青橙焕艺</h1>
        <h2>
            面向废旧玻璃热熔再生的艺术设计与数据分析平台。
            项目将废旧玻璃回收、热熔工艺实验、艺术产品转化、数据可视化与 AI 推荐系统结合，
            为大学生创新创业大赛提供一个兼具环保价值、科技感和商业展示力的数字化平台。
        </h2>
        <div class="hero-buttons">
            <a class="hero-btn" href="#database">预览工艺数据库</a>
            <a class="hero-btn-ghost" href="#recommend">体验产品推荐</a>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# 项目简介
# =========================

st.markdown('<div id="intro"></div>', unsafe_allow_html=True)

section_title(
    "PROJECT INTRODUCTION",
    "项目简介",
    "不只是展示玻璃作品，而是建立一套从废弃材料、热熔实验、艺术设计到数据推荐的完整创新创业链路。"
)

c1, c2, c3 = st.columns(3)

with c1:
    glass_card(
        "♻️",
        "废旧玻璃再生",
        "以废弃玻璃、边角料玻璃、透明和彩色玻璃为基础材料，通过清洗、筛选、组合和热熔烧制，重新赋予废弃材料可展示、可销售、可设计的价值。"
    )

with c2:
    glass_card(
        "🔥",
        "热熔工艺实验",
        "围绕温度变化建立实验数据库，对 800℃、780℃、760℃ 等烧制条件下的颗粒感、体积感、透光度和综合效果进行结构化记录。"
    )

with c3:
    glass_card(
        "🤖",
        "AI 推荐与展示",
        "面向不同用户需求，输入产品类型、材料和目标效果后，系统给出推荐温度区间、风险提示和适合产品方向，提升项目的科技感与实用性。"
    )

c4, c5, c6 = st.columns(3)

with c4:
    glass_card(
        "🎨",
        "艺术产品转化",
        "将实验样品进一步转化为花瓶、灯具、装饰画、艺术摆件和校园文创产品，增强项目的审美表达和商业落地空间。"
    )

with c5:
    glass_card(
        "📊",
        "数据可视化分析",
        "将实验结果转化为可筛选、可统计、可分析的 CSV 数据，支持温度趋势、质量分变化、多指标对比和后续机器学习建模。"
    )

with c6:
    glass_card(
        "🚀",
        "创业比赛展示",
        "页面采用青色与橙色渐变、深色科技背景、毛玻璃卡片和动态图片展示，适合路演现场快速呈现项目亮点。"
    )


# =========================
# 数据库预览
# =========================

st.markdown('<div id="database"></div>', unsafe_allow_html=True)

section_title(
    "SPACE DATABASE PREVIEW",
    "预览玻璃热熔工艺数据库",
    "基于真实烧制记录整理，聚焦温度、实验轮次、颗粒感、体积感、透光度和综合质量分。"
)

st.markdown('<div class="database-panel">', unsafe_allow_html=True)

if df.empty:
    st.warning("没有找到 glass_experiment_numeric_only.csv，请将 CSV 放在 app.py 同级目录。")
else:
    temps = sorted(df["temperature_c"].dropna().unique()) if "temperature_c" in df.columns else []
    selected_temp = st.multiselect("选择温度", temps, default=temps)

    show_df = df.copy()
    if selected_temp and "temperature_c" in show_df.columns:
        show_df = show_df[show_df["temperature_c"].isin(selected_temp)]

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f'<div class="metric-box"><h3>{len(show_df)}</h3><p>实验记录</p></div>', unsafe_allow_html=True)

    with m2:
        avg_temp = round(show_df["temperature_c"].mean(), 1) if "temperature_c" in show_df.columns and len(show_df) else 0
        st.markdown(f'<div class="metric-box"><h3>{avg_temp}℃</h3><p>平均温度</p></div>', unsafe_allow_html=True)

    with m3:
        avg_quality = round(show_df["overall_quality_score_100"].mean(), 1) if "overall_quality_score_100" in show_df.columns and len(show_df) else 0
        st.markdown(f'<div class="metric-box"><h3>{avg_quality}</h3><p>平均质量分</p></div>', unsafe_allow_html=True)

    with m4:
        best_temp = "760℃"
        if "temperature_c" in show_df.columns and "overall_quality_score_100" in show_df.columns and len(show_df):
            best_temp = f"{int(show_df.groupby('temperature_c')['overall_quality_score_100'].mean().idxmax())}℃"
        st.markdown(f'<div class="metric-box"><h3>{best_temp}</h3><p>较优温度</p></div>', unsafe_allow_html=True)

    st.markdown("### 表格形式内容")
    st.dataframe(show_df, use_container_width=True, height=360)

    numeric_cols = [
        col for col in [
            "success_score",
            "particle_score",
            "volume_score",
            "transparency_score",
            "overheat_score",
            "overall_quality_score_100"
        ] if col in show_df.columns
    ]

    if "temperature_c" in show_df.columns and numeric_cols:
        st.markdown("### 按温度均值分析")
        mean_df = show_df.groupby("temperature_c")[numeric_cols].mean().round(2).reset_index()
        st.dataframe(mean_df, use_container_width=True)
        st.line_chart(mean_df.set_index("temperature_c"))

st.markdown("</div>", unsafe_allow_html=True)


# =========================
# 图片展示区
# =========================

st.markdown('<div id="gallery"></div>', unsafe_allow_html=True)

section_title(
    "DYNAMIC PHOTO WALL",
    "照片展示与动态滚动",
    "保留项目现场、材料、成品、数据分析和 AI 推荐等图片，让页面更有比赛展示感。"
)

carousel_paths = [
    IMAGE_DIR / "banner.png",
    IMAGE_DIR / "vase.png",
    IMAGE_DIR / "lamp.png",
    IMAGE_DIR / "art.jpg",
    IMAGE_DIR / "workshop.png",
    IMAGE_DIR / "analysis_bg.png",
    IMAGE_DIR / "ai_recommendation.jpg",
]

slides = [img_to_uri(p) for p in carousel_paths if img_to_uri(p)]

if slides:
    slide_html = "".join([f'<div class="slide"><img src="{uri}"></div>' for uri in slides])
    duplicated = slide_html + slide_html

    components.html(
        f"""
<style>
.scroll-wrapper {{
    width: 100%;
    overflow: hidden;
    border-radius: 32px;
    border: 1px solid rgba(255,255,255,0.16);
    background: rgba(255,255,255,0.06);
    box-shadow: 0 24px 70px rgba(0,0,0,0.35);
}}
.scroll-track {{
    display: flex;
    gap: 24px;
    width: max-content;
    padding: 24px;
    animation: scrollX 28s linear infinite;
}}
.scroll-wrapper:hover .scroll-track {{
    animation-play-state: paused;
}}
.slide {{
    width: 420px;
    height: 260px;
    flex: 0 0 auto;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 18px 50px rgba(0,0,0,0.35);
}}
.slide img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: 0.4s;
}}
.slide:hover img {{
    transform: scale(1.08);
}}
@keyframes scrollX {{
    from {{ transform: translateX(0); }}
    to {{ transform: translateX(-50%); }}
}}
@media(max-width: 768px) {{
    .slide {{
        width: 280px;
        height: 190px;
    }}
}}
</style>
<div class="scroll-wrapper">
    <div class="scroll-track">
        {duplicated}
    </div>
</div>
""",
        height=340
    )
else:
    st.info("请把图片放入 images 文件夹后，动态滚动照片墙会自动显示。")

section_title(
    "BEFORE & AFTER",
    "废品新旧对比：废玻璃变成新玻璃",
    "通过材料和成品对比，直观表达项目的环保价值、艺术价值和商业转化潜力。"
)

left, right = st.columns(2)

with left:
    image_card(
        IMAGE_DIR / "workshop.png",
        "废旧玻璃材料",
        "回收、清洗、分类后的玻璃材料，是项目的绿色再生起点。"
    )

with right:
    image_card(
        IMAGE_DIR / "vase.png",
        "再生玻璃成品",
        "通过热熔、组合和艺术设计，转化为花瓶、灯具与艺术装置。"
    )

g1, g2, g3 = st.columns(3)

with g1:
    image_card(IMAGE_DIR / "lamp.png", "灯具产品", "突出透光度和空间氛围。")

with g2:
    image_card(IMAGE_DIR / "art.jpg", "艺术装饰", "突出颗粒肌理和色彩组合。")

with g3:
    image_card(IMAGE_DIR / "analysis_bg.png", "数据分析", "将工艺实验转化为可视化数据。")


# =========================
# 项目优势
# =========================

section_title(
    "PROJECT ADVANTAGES",
    "项目优势",
    "从环保、工艺、设计、数据和商业五个维度提升项目完整度。"
)

a1, a2, a3, a4 = st.columns(4)

with a1:
    glass_card("🌱", "绿色低碳", "减少废旧玻璃浪费，体现循环经济和可持续设计理念。")

with a2:
    glass_card("🧪", "实验可复现", "通过 CSV 数据记录温度和效果，便于后续复盘和优化。")

with a3:
    glass_card("📈", "可视化强", "适合生成趋势图、雷达图、热力图和比赛展示图表。")

with a4:
    glass_card("🛍️", "产品可转化", "可延伸为灯具、花瓶、装饰画、摆件和校园文创。")


# =========================
# 产品推荐系统
# =========================

st.markdown('<div id="recommend"></div>', unsafe_allow_html=True)

section_title(
    "PRODUCT RECOMMENDATION",
    "为用户提供特定产品推荐",
    "用户先选择想制作的产品类型，再输入材料和目标效果，系统输出推荐工艺方案。"
)

r1, r2 = st.columns([1.1, 0.9])

with r1:
    product_type = st.selectbox(
        "请选择产品类型",
        ["花瓶", "灯具", "装饰画", "艺术摆件", "综合文创产品"]
    )

    material = st.selectbox(
        "请选择材料类型",
        ["透明玻璃", "彩色玻璃", "混合玻璃", "其他材料"]
    )

    target_effect = st.selectbox(
        "请选择目标效果",
        ["颗粒感明显", "透光度强", "体积感强", "综合艺术效果"]
    )

    temp = st.slider("计划烧制温度 / ℃", 700, 850, 760, 5)

    temp_range, risk, score, product_tip, effect_tip, material_tip = recommend(
        product_type, material, target_effect, temp
    )

    st.markdown(
        f"""
<div class="recommend-result">
    <h3>AI 推荐结果</h3>
    <p><b>用户选择产品：</b>{product_type}</p>
    <p><b>推荐工艺温度区间：</b>{temp_range}</p>
    <p><b>温度风险提示：</b>{risk}</p>
    <p><b>产品设计建议：</b>{product_tip}</p>
    <p><b>目标效果建议：</b>{effect_tip}</p>
    <p><b>材料建议：</b>{material_tip}</p>
    <p><b>综合推荐分：</b>{score} / 100</p>
</div>
""",
        unsafe_allow_html=True
    )

    st.progress(score / 100)

with r2:
    image_card(
        IMAGE_DIR / "ai_recommendation.jpg",
        "AI 工艺推荐",
        "面向不同产品类型输出温度区间、风险提示和设计方向。"
    )


# =========================
# 后期展望
# =========================

st.markdown('<div id="future"></div>', unsafe_allow_html=True)

section_title(
    "FUTURE VISION",
    "后期展望",
    "围绕数据规模、AI模型、产品体系和商业落地继续升级。"
)

with st.expander("01 建立更完整的玻璃热熔工艺数据库", expanded=True):
    st.write(
        "后续继续补充保温时间、升温曲线、玻璃厚度、颗粒大小、颜色组合、摆放方式等参数，让数据库从展示型数据逐步升级为可建模数据。"
    )

with st.expander("02 从规则推荐升级为机器学习推荐"):
    st.write(
        "当前系统基于真实实验规律和规则进行推荐，后续可使用回归模型或分类模型预测综合质量分，并自动生成最佳烧制方案。"
    )

with st.expander("03 扩展更多再生玻璃产品类型"):
    st.write(
        "产品可从花瓶、灯具、装饰画扩展到校园纪念品、公共艺术装置、家居软装和文旅文创产品。"
    )

with st.expander("04 打造校园绿色工坊和商业闭环"):
    st.write(
        "结合校园废玻璃回收、手作体验课程、线上展示平台和文创销售，形成环保教育、艺术体验和创业转化的闭环。"
    )


# =========================
# 联系我们
# =========================

st.markdown('<div id="contact"></div>', unsafe_allow_html=True)

section_title(
    "CONTACT US",
    "联系我们",
    "让废旧玻璃重新发光，让绿色材料进入艺术生活。"
)

st.markdown(
    """
<div class="contact-card">
    <h2>青橙焕艺</h2>
    <p>Glass Recycling AI Platform</p>
    <p>废旧玻璃热熔再生 · 艺术产品设计 · 工艺数据分析 · AI 推荐系统</p>
    <p>适用场景：大学生创新创业大赛 / 校园环保项目 / 文创产品孵化 / 艺术工坊展示</p>
    <p><b>团队：</b>青橙焕艺项目组　｜　<b>邮箱：</b>example@email.com</p>
</div>
""",
    unsafe_allow_html=True
)