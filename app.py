import base64
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 基础配置
# =========================================================

st.set_page_config(
    page_title="青橙焕艺 | Glass Recycling AI Platform",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# 路径兼容
# =========================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent if APP_DIR.name.lower() == "src" else APP_DIR

IMAGE_DIR = PROJECT_DIR / "images"
FIGURE_DIR = PROJECT_DIR / "figures"

DATA_CANDIDATES = [
    PROJECT_DIR / "glass_experiment_numeric_only.csv",
    APP_DIR / "glass_experiment_numeric_only.csv",
    PROJECT_DIR / "notebook-keshihua" / "glass_experiment_numeric_only.csv",
]


def find_data_path():
    for path in DATA_CANDIDATES:
        if path.exists():
            return path
    return DATA_CANDIDATES[0]


DATA_PATH = find_data_path()


# =========================================================
# 工具函数
# =========================================================

def resolve_image(name: str) -> Path:
    raw = IMAGE_DIR / name

    if raw.exists():
        return raw

    suffixes = [".png", ".jpg", ".jpeg", ".webp"]
    for suffix in suffixes:
        candidate = IMAGE_DIR / f"{name}{suffix}"
        if candidate.exists():
            return candidate

    return raw


def img_to_uri(path: Path) -> str:
    if not path.exists():
        return ""

    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in [".jpg", ".jpeg"] else "image/png"

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


@st.cache_data
def load_data(path: str):
    csv_path = Path(path)
    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df


def section_title(tag: str, title: str, desc: str):
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


def glass_card(icon: str, title: str, text: str):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="icon">{icon}</div>
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def advantage_card(icon: str, title: str, text: str):
    st.markdown(
        f"""
        <div class="advantage-card">
            <div class="advantage-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def contact_card(icon: str, title: str, line1: str, line2: str, line3: str):
    st.markdown(
        f"""
        <div class="contact-item-card">
            <div class="contact-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{line1}</p>
            <p>{line2}</p>
            <p>{line3}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def image_card(
    path: Path,
    title: str,
    desc: str,
    maker: str = "",
    note_label: str = "制作人员"
):
    uri = img_to_uri(path)

    maker_html = ""
    if maker:
        maker_html = f'<div class="maker">{note_label}：{maker}</div>'

    if uri:
        st.markdown(
            f"""
            <div class="image-card">
                <img src="{uri}" alt="{title}" />
                <div class="image-mask">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                    {maker_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="image-card image-missing">
                <div>
                    <h3>{title}</h3>
                    <p>缺少图片：{path.name}</p>
                    <small>请确认该图片已放入 images 文件夹</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def before_after_pair(temp: int, before_name: str, after_name: str, maker: str, result_desc: str):
    st.markdown(
        f"""
        <div class="pair-title">
            <span>{temp}℃</span>
            <p>{result_desc}</p>
            <div>制作人员：{maker}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        image_card(
            resolve_image(before_name),
            f"{temp}℃ · 烧制前",
            f"{temp}qian：热熔前的玻璃颗粒与材料组合状态。",
            maker
        )

    with col2:
        image_card(
            resolve_image(after_name),
            f"{temp}℃ · 烧制后",
            f"{temp}hou：经过热熔后的成型状态与视觉效果。",
            maker
        )


def recommend(product_type: str, material: str, target_effect: str, temp: int):
    if product_type == "花瓶":
        base_temp = "760℃ - 770℃"
        product_tip = "花瓶需要保留局部体积感，建议玻璃融合但不要完全摊平。"
    elif product_type == "灯具":
        base_temp = "755℃ - 765℃"
        product_tip = "灯具更重视透光度，建议使用透明玻璃或浅色玻璃组合。"
    elif product_type == "装饰画":
        base_temp = "750℃ - 765℃"
        product_tip = "装饰画适合保留颗粒边界和色彩层次，温度不宜过高。"
    elif product_type == "艺术摆件":
        base_temp = "760℃ - 775℃"
        product_tip = "艺术摆件可适当增强体积感，但要避免温度过高造成形态塌陷。"
    else:
        base_temp = "755℃ - 770℃"
        product_tip = "综合文创产品建议先做小样测试，再根据成品效果扩大尺寸。"

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
        material_tip = "混合玻璃层次丰富，但需要注意颜色过杂。"
    else:
        material_tip = "建议先做小样实验，记录温度和最终效果。"

    return base_temp, risk, score, product_tip, effect_tip, material_tip


df = load_data(str(DATA_PATH))


# =========================================================
# 全局 CSS
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');

:root {
    --cyan: #25f4ee;
    --orange: #ff9f43;
    --white: #f6fbff;
}

html, body, .stApp {
    font-family: 'Noto Sans SC', sans-serif;
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(circle at 8% 10%, rgba(37,244,238,0.28), transparent 25%),
        radial-gradient(circle at 88% 13%, rgba(255,159,67,0.25), transparent 25%),
        radial-gradient(circle at 50% 95%, rgba(37,244,238,0.16), transparent 35%),
        linear-gradient(135deg, #020711 0%, #071827 48%, #14101f 100%);
    color: var(--white);
}

.block-container {
    max-width: 1280px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(37,244,238,0.22), rgba(255,159,67,0.22), transparent);
    margin: 3rem 0;
}

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
    max-width: 850px;
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

.section-head {
    text-align: center;
    margin: 5rem auto 2rem;
    max-width: 880px;
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

.glass-card {
    height: 100%;
    min-height: 260px;
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

.advantage-card {
    height: 280px;
    padding: 1.45rem;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.09), rgba(255,159,67,0.08)),
        rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(20px);
    box-shadow: 0 18px 52px rgba(0,0,0,0.25);
    transition: 0.28s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.advantage-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(255,159,67,0.48);
    box-shadow: 0 0 32px rgba(255,159,67,0.20), 0 18px 52px rgba(0,0,0,0.35);
}

.advantage-icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}

.advantage-card h3 {
    color: #fff;
    margin: 0 0 0.8rem 0;
    font-size: 1.22rem;
}

.advantage-card p {
    color: rgba(246,251,255,0.72);
    line-height: 1.7;
    margin: 0;
}

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
    padding: 1.35rem;
    background: linear-gradient(to top, rgba(0,0,0,0.82), rgba(0,0,0,0.20), transparent);
}

.image-mask h3 {
    margin: 0;
    color: white;
}

.image-mask p {
    color: rgba(255,255,255,0.78);
    margin: 0.35rem 0 0;
    line-height: 1.55;
}

.maker {
    margin-top: 0.5rem;
    color: #ffcf9a;
    font-weight: 800;
    font-size: 0.92rem;
}

.image-missing {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    border-style: solid;
    color: rgba(246,251,255,0.82);
}

.image-missing small {
    color: rgba(246,251,255,0.55);
}

.pair-title {
    margin: 2.2rem 0 1rem;
    padding: 1.2rem 1.4rem;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.10)),
        rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(16px);
}

.pair-title span {
    font-size: 1.75rem;
    font-weight: 900;
    color: var(--cyan);
}

.pair-title p {
    margin: 0.35rem 0;
    color: rgba(246,251,255,0.78);
    line-height: 1.7;
}

.pair-title div {
    color: #ffcf9a;
    font-weight: 800;
}

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

.contact-shell {
    padding: 2.8rem 2.2rem;
    border-radius: 34px;
    background:
        radial-gradient(circle at 15% 10%, rgba(37,244,238,0.20), transparent 28%),
        radial-gradient(circle at 86% 20%, rgba(255,159,67,0.18), transparent 28%),
        linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.12)),
        rgba(255,255,255,0.065);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(20px);
    text-align: center;
    box-shadow: 0 24px 70px rgba(0,0,0,0.30);
    margin-top: 1rem;
}

.contact-shell h2 {
    font-size: clamp(2rem, 5vw, 3rem);
    margin: 0;
    background: linear-gradient(90deg, var(--cyan), #fff, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.contact-shell p {
    color: rgba(246,251,255,0.72);
    margin-top: 0.6rem;
}

.contact-item-card {
    min-height: 190px;
    padding: 1.4rem;
    border-radius: 24px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 16px 42px rgba(0,0,0,0.22);
    transition: 0.25s ease;
    text-align: center;
}

.contact-item-card:hover {
    transform: translateY(-6px);
    border-color: rgba(37,244,238,0.48);
    box-shadow: 0 0 28px rgba(37,244,238,0.18);
}

.contact-icon {
    font-size: 2rem;
    margin-bottom: 0.6rem;
}

.contact-item-card h3 {
    margin: 0 0 0.6rem 0;
    color: var(--cyan);
    font-size: 1.15rem;
}

.contact-item-card p {
    margin: 0.25rem 0;
    color: rgba(246,251,255,0.72);
    line-height: 1.55;
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.14);
}

.stSlider label,
.stSelectbox label,
.stMultiSelect label {
    color: rgba(246,251,255,0.82) !important;
    font-weight: 800 !important;
}

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

    .nav-links {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .nav-links a {
        margin-left: 0;
        margin-right: 0.4rem;
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

    .advantage-card {
        height: auto;
        min-height: 230px;
    }
}
</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 顶部导航
# =========================================================

st.markdown(
    """
<div class="navbar">
    <div class="nav-logo">♻️ 青橙焕艺 | 青汐造物</div>
    <div class="nav-links">
        <a href="#intro">项目简介</a>
        <a href="#database">工艺数据库</a>
        <a href="#gallery">烧制对比</a>
        <a href="#industry">行业产品</a>
        <a href="#advantage">项目优势</a>
        <a href="#recommend">产品推荐</a>
        <a href="#future">后期展望</a>
        <a href="#contact">联系我们</a>
    </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# Hero 首页
# =========================================================

st.markdown(
    """
<div class="hero">
    <div class="hero-content">
        <div class="hero-tag">GREEN DESIGN · AI DATA · GLASS ART · QINGXI CREATION</div>
        <h1>青橙焕艺</h1>
        <h2>
            由青汐造物打造，依托青汐工坊开展废旧玻璃热熔再生、艺术设计与工艺数据分析。
            项目将废旧玻璃回收、热熔工艺实验、烧制前后对比、艺术产品转化、
            数据可视化与 AI 推荐系统结合，为大学生创新创业大赛提供一个兼具环保价值、
            科技感和商业展示力的数字化平台。
        </h2>
        <div class="hero-buttons">
            <a class="hero-btn" href="#database">预览工艺数据库</a>
            <a class="hero-btn-ghost" href="#gallery">查看烧制对比</a>
            <a class="hero-btn-ghost" href="#recommend">体验产品推荐</a>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# 项目简介
# =========================================================

st.markdown('<div id="intro"></div>', unsafe_allow_html=True)

section_title(
    "PROJECT INTRODUCTION",
    "项目简介",
    "青汐造物以青汐工坊为线下实验与艺术转化空间，建立从废弃材料、热熔实验、烧制前后记录、艺术设计到数据推荐的完整创新创业链路。"
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
        "青汐工坊实验",
        "依托青汐工坊开展热熔工艺实验，对 800℃、780℃、760℃ 等烧制条件下的颗粒感、体积感、透光度和综合效果进行结构化记录。"
    )

with c3:
    glass_card(
        "📷",
        "烧制前后对比",
        "通过 760℃、780℃、800℃ 三组烧制前后照片，直观展示温度变化对玻璃融合程度、颗粒保留和视觉效果的影响。"
    )

c4, c5, c6 = st.columns(3)

with c4:
    glass_card(
        "🎨",
        "艺术产品转化",
        "青汐造物将实验样品进一步转化为花瓶、灯具、装饰画、艺术摆件和校园文创产品，增强项目的审美表达和商业落地空间。"
    )

with c5:
    glass_card(
        "📊",
        "数据可视化分析",
        "将实验结果转化为可筛选、可统计、可分析的 CSV 数据，支持温度趋势、质量分变化、多指标对比和后续机器学习建模。"
    )

with c6:
    glass_card(
        "🤖",
        "AI 工艺推荐",
        "面向用户选择的产品类型、材料和目标效果，输出推荐温度区间、风险提示和产品设计建议，提高项目科技感与交互性。"
    )


# =========================================================
# 工艺数据库
# =========================================================

st.markdown('<div id="database"></div>', unsafe_allow_html=True)

section_title(
    "SPACE DATABASE PREVIEW",
    "预览玻璃热熔工艺数据库",
    "基于青汐工坊真实烧制记录整理，聚焦温度、实验轮次、颗粒感、体积感、透光度和综合质量分。"
)

st.markdown('<div class="database-panel">', unsafe_allow_html=True)

if df.empty:
    st.warning(f"没有找到 glass_experiment_numeric_only.csv。当前尝试路径：{DATA_PATH}")
else:
    temps = sorted(df["temperature_c"].dropna().unique()) if "temperature_c" in df.columns else []
    selected_temp = st.multiselect("选择温度", temps, default=temps)

    show_df = df.copy()

    if selected_temp and "temperature_c" in show_df.columns:
        show_df = show_df[show_df["temperature_c"].isin(selected_temp)]

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f'<div class="metric-box"><h3>{len(show_df)}</h3><p>实验记录</p></div>',
            unsafe_allow_html=True
        )

    with m2:
        avg_temp = round(show_df["temperature_c"].mean(), 1) if "temperature_c" in show_df.columns and len(show_df) else 0
        st.markdown(
            f'<div class="metric-box"><h3>{avg_temp}℃</h3><p>平均温度</p></div>',
            unsafe_allow_html=True
        )

    with m3:
        avg_quality = round(show_df["overall_quality_score_100"].mean(), 1) if "overall_quality_score_100" in show_df.columns and len(show_df) else 0
        st.markdown(
            f'<div class="metric-box"><h3>{avg_quality}</h3><p>平均质量分</p></div>',
            unsafe_allow_html=True
        )

    with m4:
        best_temp = "暂无"
        if "temperature_c" in show_df.columns and "overall_quality_score_100" in show_df.columns and len(show_df):
            best_temp = f"{int(show_df.groupby('temperature_c')['overall_quality_score_100'].mean().idxmax())}℃"
        st.markdown(
            f'<div class="metric-box"><h3>{best_temp}</h3><p>较优温度</p></div>',
            unsafe_allow_html=True
        )

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


# =========================================================
# 烧制前后动态滚动照片
# =========================================================

st.markdown('<div id="gallery"></div>', unsafe_allow_html=True)

section_title(
    "FIRING COMPARISON",
    "烧制前后照片展示",
    "围绕 760℃、780℃、800℃ 三组温度，将烧制前 qian 与烧制后 hou 进行动态展示，突出不同温度下玻璃状态的变化。"
)

scroll_items = [
    {"path": resolve_image("760qian"), "title": "760℃ · 烧制前", "desc": "760qian", "maker": "李雨豪、芦子晴、刘鑫悦等"},
    {"path": resolve_image("760hou"), "title": "760℃ · 烧制后", "desc": "760hou", "maker": "李雨豪、芦子晴、刘鑫悦等"},
    {"path": resolve_image("780qian"), "title": "780℃ · 烧制前", "desc": "780qian", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"path": resolve_image("780hou"), "title": "780℃ · 烧制后", "desc": "780hou", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"path": resolve_image("800qian"), "title": "800℃ · 烧制前", "desc": "800qian", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"path": resolve_image("800hou"), "title": "800℃ · 烧制后", "desc": "800hou", "maker": "芦子晴、刘鑫悦、刘关伟等"},
]

slide_html = ""

for item in scroll_items:
    uri = img_to_uri(item["path"])
    if uri:
        slide_html += f"""
        <div class="slide">
            <img src="{uri}">
            <div class="slide-caption">
                <strong>{item["title"]}</strong>
                <span>{item["desc"]}</span>
                <em>制作人员：{item["maker"]}</em>
            </div>
        </div>
        """

if slide_html:
    components.html(
        f"""
<style>
.scroll-wrapper {{
    width: 100%;
    overflow: hidden;
    border-radius: 32px;
    border: 1px solid rgba(255,255,255,0.16);
    background:
        radial-gradient(circle at 10% 20%, rgba(37,244,238,0.18), transparent 30%),
        radial-gradient(circle at 90% 15%, rgba(255,159,67,0.16), transparent 28%),
        rgba(255,255,255,0.06);
    box-shadow: 0 24px 70px rgba(0,0,0,0.35);
}}
.scroll-track {{
    display: flex;
    gap: 24px;
    width: max-content;
    padding: 24px;
    animation: scrollX 30s linear infinite;
}}
.scroll-wrapper:hover .scroll-track {{
    animation-play-state: paused;
}}
.slide {{
    position: relative;
    width: 420px;
    height: 280px;
    flex: 0 0 auto;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 18px 50px rgba(0,0,0,0.35);
    background: rgba(255,255,255,0.08);
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
.slide-caption {{
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 18px;
    background: linear-gradient(to top, rgba(0,0,0,0.84), rgba(0,0,0,0.18), transparent);
    color: white;
}}
.slide-caption strong {{
    display: block;
    font-size: 18px;
    margin-bottom: 4px;
}}
.slide-caption span {{
    display: block;
    color: rgba(255,255,255,0.78);
    font-size: 14px;
}}
.slide-caption em {{
    display: block;
    color: #ffcf9a;
    font-style: normal;
    font-size: 13px;
    margin-top: 5px;
    font-weight: 700;
}}
@keyframes scrollX {{
    from {{ transform: translateX(0); }}
    to {{ transform: translateX(-50%); }}
}}
@media(max-width: 768px) {{
    .slide {{
        width: 280px;
        height: 210px;
    }}
}}
</style>
<div class="scroll-wrapper">
    <div class="scroll-track">
        {slide_html}
        {slide_html}
    </div>
</div>
""",
        height=350
    )
else:
    st.info("请确认 images 文件夹中存在 760qian、760hou、780qian、780hou、800qian、800hou。")


# =========================================================
# 烧制前后对比
# =========================================================

section_title(
    "BEFORE & AFTER",
    "烧制前后的对比",
    "根据图片文件名中的数字识别温度，qian 表示烧制前，hou 表示烧制后。用户可以直观看到不同温度对玻璃热熔状态的影响。"
)

tab760, tab780, tab800 = st.tabs(["760℃ 对比", "780℃ 对比", "800℃ 对比"])

with tab760:
    before_after_pair(
        760,
        "760qian",
        "760hou",
        "李雨豪、芦子晴、刘鑫悦、刘关伟、闫续、高艺萌等",
        "760℃ 组整体表现较好，多次出现“温度适中，颗粒感明显”，后期也出现“透光度强，有明显体积感”的结果。"
    )

with tab780:
    before_after_pair(
        780,
        "780qian",
        "780hou",
        "芦子晴、刘鑫悦、刘关伟、田思雨、高艺丹等",
        "780℃ 组仍表现出温度偏高问题，部分样品出现颗粒感和体积感不足，个别样品透光效果一般。"
    )

with tab800:
    before_after_pair(
        800,
        "800qian",
        "800hou",
        "芦子晴、刘鑫悦、刘关伟、田思雨、高艺丹、李若冰等",
        "800℃ 组温度过高，多次出现“没有颗粒感和体积感”，说明过度熔融会削弱玻璃颗粒肌理。"
    )


# =========================================================
# 玻璃行业产品展示
# =========================================================

st.markdown('<div id="industry"></div>', unsafe_allow_html=True)

section_title(
    "GLASS INDUSTRY PRODUCTS",
    "玻璃行业产品展示",
    "以下图片用于展示玻璃行业常见产品形态与市场应用方向，作为青汐造物后续产品设计参考；图片不代表青汐工坊原创实物。"
)

p1, p2, p3 = st.columns(3)

with p1:
    image_card(
        resolve_image("1"),
        "家居器皿方向",
        "展示玻璃材料在家居器皿、桌面陈设和生活收纳中的行业应用可能。",
        "行业产品参考，非原创实物",
        note_label="说明"
    )

with p2:
    image_card(
        resolve_image("2"),
        "透光灯具方向",
        "展示玻璃材料在灯具、氛围照明和空间装饰中的行业化应用。",
        "行业产品参考，非原创实物",
        note_label="说明"
    )

with p3:
    image_card(
        resolve_image("3"),
        "花器摆件方向",
        "展示玻璃材料在花瓶、花器、家居软装和陈列摆件中的产品形态。",
        "行业产品参考，非原创实物",
        note_label="说明"
    )

p4, p5 = st.columns(2)

with p4:
    image_card(
        resolve_image("4"),
        "文创饰品方向",
        "展示玻璃色彩、珠状元素和轻量化饰品在文创产品中的延展空间。",
        "行业产品参考，非原创实物",
        note_label="说明"
    )

with p5:
    image_card(
        resolve_image("5"),
        "生活器物方向",
        "展示玻璃材料在烛台、香薰容器、桌面器物等生活场景中的商业化方向。",
        "行业产品参考，非原创实物",
        note_label="说明"
    )


# =========================================================
# 项目优势
# =========================================================

st.markdown('<div id="advantage"></div>', unsafe_allow_html=True)

section_title(
    "PROJECT ADVANTAGES",
    "项目优势",
    "从环保、工艺、展示和产品转化四个维度体现青汐造物的项目价值。"
)

a1, a2, a3, a4 = st.columns(4)

with a1:
    advantage_card(
        "🌱",
        "绿色低碳",
        "减少废旧玻璃浪费，体现循环经济、环保教育和可持续设计理念。"
    )

with a2:
    advantage_card(
        "🧪",
        "工坊实验可复现",
        "依托青汐工坊记录温度、实验轮次和效果评分，便于后续复盘、优化和扩展。"
    )

with a3:
    advantage_card(
        "📷",
        "对比展示直观",
        "烧制前后照片能够直观展示温度变化对玻璃形态、颗粒感和体积感的影响。"
    )

with a4:
    advantage_card(
        "🛍️",
        "产品可转化",
        "结合玻璃行业产品形态，可延伸为灯具、花瓶、装饰画、摆件和校园文创。"
    )


# =========================================================
# 产品推荐系统
# =========================================================

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

recommend_img = resolve_image("22")
if not recommend_img.exists():
    recommend_img = resolve_image("11")

with r2:
    image_card(
        recommend_img,
        "推荐效果参考",
        "该图用于辅助展示热熔玻璃的发光、透光和材料转化效果，适合放在产品推荐系统旁作为视觉引导。",
        "行业视觉参考，非原创实物",
        note_label="说明"
    )


# =========================================================
# 后期展望
# =========================================================

st.markdown('<div id="future"></div>', unsafe_allow_html=True)

section_title(
    "FUTURE VISION",
    "后期展望",
    "围绕数据规模、AI模型、产品体系和商业落地继续升级青汐造物的再生玻璃艺术平台。"
)

with st.expander("01 建立更完整的玻璃热熔工艺数据库", expanded=True):
    st.write(
        "青汐工坊后续将继续补充保温时间、升温曲线、玻璃厚度、颗粒大小、颜色组合、摆放方式等参数，让数据库从展示型数据逐步升级为可建模数据。"
    )

with st.expander("02 从规则推荐升级为机器学习推荐"):
    st.write(
        "当前系统基于真实实验规律和规则进行推荐，后续青汐造物可使用回归模型或分类模型预测综合质量分，并自动生成最佳烧制方案。"
    )

with st.expander("03 扩展更多再生玻璃产品类型"):
    st.write(
        "产品可参考玻璃行业现有器皿、灯具、花器、饰品和生活器物形态，进一步扩展到校园纪念品、公共艺术装置、家居软装和文旅文创产品。"
    )

with st.expander("04 打造青汐工坊体验与商业闭环"):
    st.write(
        "结合校园废玻璃回收、青汐工坊手作体验课程、线上展示平台和文创销售，形成环保教育、艺术体验和创业转化的闭环。"
    )


# =========================================================
# 联系我们
# =========================================================

st.markdown('<div id="contact"></div>', unsafe_allow_html=True)

section_title(
    "CONTACT US",
    "联系我们",
    "让废旧玻璃重新发光，让绿色材料进入艺术生活。"
)

st.markdown(
    """
    <div class="contact-shell">
        <h2>青汐造物</h2>
        <p>青汐工坊 · Glass Recycling AI Platform</p>
    </div>
    """,
    unsafe_allow_html=True
)

cc1, cc2, cc3 = st.columns(3)

with cc1:
    contact_card(
        "♻️",
        "公司定位",
        "青汐造物",
        "废旧玻璃热熔再生",
        "艺术产品设计"
    )

with cc2:
    contact_card(
        "🏛️",
        "艺术中心",
        "青汐工坊",
        "校园环保项目",
        "艺术工坊展示"
    )

with cc3:
    contact_card(
        "🤖",
        "平台方向",
        "青橙焕艺项目",
        "绿色材料再生",
        "AI 推荐系统展示"
    )