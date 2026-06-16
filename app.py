import base64
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 基础配置
# =========================================================

st.set_page_config(
    page_title="倾城幻艺 | 青橙焕艺玻璃再生AI平台",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent if APP_DIR.name.lower() == "src" else APP_DIR
IMAGE_DIR = PROJECT_DIR / "images"

DATA_CANDIDATES = [
    PROJECT_DIR / "glass_experiment_numeric_only.csv",
    APP_DIR / "glass_experiment_numeric_only.csv",
    PROJECT_DIR / "notebook-keshihua" / "glass_experiment_numeric_only.csv",
]


# =========================================================
# Session State
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "vip_unlocked" not in st.session_state:
    st.session_state.vip_unlocked = False

if "vip_level" not in st.session_state:
    st.session_state.vip_level = "未开通"

if "factory_orders" not in st.session_state:
    st.session_state.factory_orders = []


# =========================================================
# 工具函数
# =========================================================

def find_data_path() -> Path:
    for path in DATA_CANDIDATES:
        if path.exists():
            return path
    return DATA_CANDIDATES[0]


DATA_PATH = find_data_path()


def resolve_image(name: str) -> Path:
    raw = IMAGE_DIR / name
    if raw.exists():
        return raw

    for suffix in [".png", ".jpg", ".jpeg", ".webp"]:
        candidate = IMAGE_DIR / f"{name}{suffix}"
        if candidate.exists():
            return candidate

    return raw


def img_to_uri(path: Path) -> str:
    if not path.exists():
        return ""

    suffix = path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


@st.cache_data(ttl=300)
def load_data(path: str) -> pd.DataFrame:
    csv_path = Path(path)

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except Exception:
                pass
        return df

    demo_data = [
        {
            "temperature_c": 760,
            "success_score": 88,
            "particle_score": 90,
            "volume_score": 86,
            "transparency_score": 82,
            "overheat_score": 12,
            "overall_quality_score_100": 88
        },
        {
            "temperature_c": 760,
            "success_score": 86,
            "particle_score": 88,
            "volume_score": 84,
            "transparency_score": 85,
            "overheat_score": 15,
            "overall_quality_score_100": 86
        },
        {
            "temperature_c": 780,
            "success_score": 74,
            "particle_score": 68,
            "volume_score": 70,
            "transparency_score": 76,
            "overheat_score": 35,
            "overall_quality_score_100": 73
        },
        {
            "temperature_c": 780,
            "success_score": 70,
            "particle_score": 64,
            "volume_score": 67,
            "transparency_score": 73,
            "overheat_score": 42,
            "overall_quality_score_100": 69
        },
        {
            "temperature_c": 800,
            "success_score": 55,
            "particle_score": 40,
            "volume_score": 42,
            "transparency_score": 78,
            "overheat_score": 72,
            "overall_quality_score_100": 54
        },
        {
            "temperature_c": 800,
            "success_score": 52,
            "particle_score": 36,
            "volume_score": 39,
            "transparency_score": 75,
            "overheat_score": 78,
            "overall_quality_score_100": 51
        },
    ]

    return pd.DataFrame(demo_data)


def safe_markdown(html: str):
    st.markdown(str(html).strip(), unsafe_allow_html=True)


def add_to_cart(name: str, price: float, quantity: int, category: str):
    st.session_state.cart.append(
        {
            "商品名称": name,
            "分类": category,
            "单价": price,
            "数量": quantity,
            "小计": round(price * quantity, 2),
            "加入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


def section_title(tag: str, title: str, desc: str = ""):
    desc_html = f"<p>{desc}</p>" if desc else ""
    safe_markdown(
        f"""
<div class="section-head">
    <div class="section-tag">{tag}</div>
    <h2>{title}</h2>
    {desc_html}
</div>
"""
    )


def glass_card(icon: str, title: str, text: str):
    safe_markdown(
        f"""
<div class="glass-card">
    <div class="icon">{icon}</div>
    <h3>{title}</h3>
    <p>{text}</p>
</div>
"""
    )


def metric_box(value: str, label: str):
    safe_markdown(
        f"""
<div class="metric-box">
    <h3>{value}</h3>
    <p>{label}</p>
</div>
"""
    )


def info_panel(title: str, body: str):
    safe_markdown(
        f"""
<div class="info-panel">
    <h3>{title}</h3>
    <p>{body}</p>
</div>
"""
    )


def image_card(path: Path, title: str, desc: str, note_label: str = "", note_text: str = ""):
    uri = img_to_uri(path)

    if not uri:
        safe_markdown(
            f"""
<div class="missing-img">
    <h3>{title}</h3>
    <p>缺少图片：{path.name}</p>
    <small>请将图片放入项目 images 文件夹；如果没有该图片，也不会影响系统运行。</small>
</div>
"""
        )
        return

    note_html = ""
    if note_label and note_text:
        note_html = f'<div class="image-note"><span>{note_label}：</span>{note_text}</div>'

    components.html(
        f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    margin: 0;
    background: transparent;
    font-family: "Noto Sans SC", Arial, sans-serif;
}}

.image-card {{
    position: relative;
    height: 350px;
    border-radius: 28px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow: 0 24px 70px rgba(0,0,0,0.35);
    background: rgba(255,255,255,0.08);
    transition: 0.28s ease;
}}

.image-card:hover {{
    transform: translateY(-7px);
    box-shadow: 0 0 34px rgba(255,159,67,0.24), 0 24px 70px rgba(0,0,0,0.42);
}}

.image-card img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: 0.6s ease;
}}

.image-card:hover img {{
    transform: scale(1.06);
}}

.image-mask {{
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 1.25rem;
    background: linear-gradient(to top, rgba(0,0,0,0.88), rgba(0,0,0,0.45), transparent);
}}

.image-mask h3 {{
    margin: 0;
    color: white;
    font-size: 1.35rem;
    font-weight: 900;
}}

.image-mask p {{
    color: rgba(255,255,255,0.86);
    margin: 0.45rem 0 0;
    line-height: 1.55;
    font-size: 0.96rem;
    font-weight: 700;
}}

.image-note {{
    margin-top: 0.55rem;
    color: #ffcf9a;
    font-weight: 900;
    font-size: 0.9rem;
}}

.image-note span {{
    color: #ffe4c4;
}}
</style>
</head>
<body>
<div class="image-card">
    <img src="{uri}" alt="{title}">
    <div class="image-mask">
        <h3>{title}</h3>
        <p>{desc}</p>
        {note_html}
    </div>
</div>
</body>
</html>
""",
        height=370
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
    elif product_type == "公共艺术装置":
        base_temp = "760℃ - 775℃"
        product_tip = "公共艺术装置需要兼顾强度、造型和视觉冲击力，建议先小样验证再放大制作。"
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
        risk = "当前温度仍偏高，颗粒边界可能变弱，建议向760℃附近调整。"
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
        effect_tip = "建议平衡颗粒感、透光度和体积感，适合比赛展示与商业样品。"

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

safe_markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');

:root {
    --cyan: #25f4ee;
    --orange: #ff9f43;
    --green: #80ff72;
    --white: #f6fbff;
    --muted: rgba(246,251,255,0.72);
}

html, body, .stApp {
    font-family: 'Noto Sans SC', sans-serif;
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(circle at 8% 10%, rgba(37,244,238,0.27), transparent 25%),
        radial-gradient(circle at 88% 13%, rgba(255,159,67,0.23), transparent 25%),
        radial-gradient(circle at 50% 96%, rgba(128,255,114,0.10), transparent 35%),
        linear-gradient(135deg, #020711 0%, #071827 48%, #14101f 100%);
    color: var(--white);
}

.block-container {
    max-width: 1320px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 1.25rem;
    padding: 0.75rem 1.2rem;
    border-radius: 999px;
    background: rgba(6, 19, 31, 0.76);
    border: 1px solid rgba(255,255,255,0.13);
    backdrop-filter: blur(20px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 14px 42px rgba(0,0,0,0.26);
}

.nav-logo {
    font-weight: 900;
    font-size: 1.05rem;
    background: linear-gradient(90deg, var(--cyan), #fff, var(--orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links a {
    color: rgba(246,251,255,0.84) !important;
    text-decoration: none;
    margin-left: 1.05rem;
    font-size: 0.9rem;
    transition: 0.25s;
}

.nav-links a:hover {
    color: var(--cyan) !important;
    text-shadow: 0 0 14px rgba(37,244,238,0.6);
}

.hero {
    position: relative;
    overflow: hidden;
    min-height: 640px;
    border-radius: 38px;
    padding: 5.2rem 3rem;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.13), rgba(255,159,67,0.12)),
        rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(18px);
    box-shadow: 0 28px 90px rgba(0,0,0,0.38);
}

.hero::after {
    content: "";
    position: absolute;
    right: -120px;
    top: -120px;
    width: 360px;
    height: 360px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,159,67,0.42), transparent 70%);
    filter: blur(4px);
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
    max-width: 980px;
    font-size: clamp(1.05rem, 2vw, 1.42rem);
    line-height: 1.9;
    color: rgba(246,251,255,0.83);
    font-weight: 500;
}

.hero-tag {
    display: inline-block;
    padding: 0.55rem 1rem;
    border-radius: 999px;
    color: var(--cyan);
    background: rgba(37,244,238,0.1);
    border: 1px solid rgba(37,244,238,0.32);
    font-weight: 900;
    letter-spacing: 0.12em;
    margin-bottom: 1.5rem;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 2rem;
}

.hero-btn,
.hero-btn-ghost {
    padding: 0.9rem 1.3rem;
    border-radius: 16px;
    text-decoration: none !important;
    font-weight: 900;
    transition: 0.28s;
}

.hero-btn {
    background: linear-gradient(135deg, var(--cyan), var(--orange));
    color: #04111f !important;
}

.hero-btn-ghost {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    color: #fff !important;
}

.hero-btn:hover,
.hero-btn-ghost:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 0 28px rgba(37,244,238,0.35);
}

.section-head {
    text-align: center;
    margin: 5rem auto 2rem;
    max-width: 940px;
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
    color: rgba(246,251,255,0.70);
    line-height: 1.85;
}

.glass-card,
.info-panel,
.contact-item-card {
    height: 100%;
    padding: 1.45rem;
    border-radius: 28px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    backdrop-filter: blur(20px);
    box-shadow: 0 18px 52px rgba(0,0,0,0.25);
    transition: 0.28s ease;
}

.glass-card {
    min-height: 245px;
}

.glass-card:hover,
.info-panel:hover,
.contact-item-card:hover {
    transform: translateY(-7px);
    border-color: rgba(37,244,238,0.48);
    box-shadow: 0 0 32px rgba(37,244,238,0.22), 0 18px 52px rgba(0,0,0,0.35);
}

.icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}

.glass-card h3,
.info-panel h3,
.contact-item-card h3 {
    color: #fff;
    margin-bottom: 0.7rem;
    font-size: 1.22rem;
    font-weight: 900;
}

.glass-card p,
.info-panel p,
.contact-item-card p {
    color: rgba(246,251,255,0.74);
    line-height: 1.75;
}

.metric-box {
    padding: 1.15rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.13);
    text-align: center;
    min-height: 120px;
}

.metric-box h3 {
    color: var(--cyan);
    margin: 0;
    font-size: 2rem;
    font-weight: 900;
}

.metric-box p {
    color: rgba(246,251,255,0.68);
    margin: 0.3rem 0 0;
}

.recommend-result,
.order-result,
.vip-panel,
.lock-panel {
    padding: 1.45rem;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.10));
    border: 1px solid rgba(255,255,255,0.16);
    margin-top: 1rem;
    box-shadow: 0 18px 52px rgba(0,0,0,0.22);
}

.lock-panel {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, rgba(255,159,67,0.13), rgba(37,244,238,0.08));
}

.recommend-result h3,
.order-result h3,
.vip-panel h3,
.lock-panel h3 {
    margin-top: 0;
    color: var(--cyan);
    font-weight: 900;
}

.recommend-result p,
.order-result p,
.vip-panel p,
.lock-panel p {
    color: rgba(246,251,255,0.78);
    line-height: 1.72;
}

.missing-img {
    height: 350px;
    border-radius: 28px;
    border: 1px dashed rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.06);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(246,251,255,0.78);
    text-align: center;
    padding: 1rem;
}

.contact-shell {
    padding: 2.8rem 2.2rem;
    border-radius: 34px;
    background: rgba(255,255,255,0.065);
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

.stSlider label,
.stSelectbox label,
.stMultiSelect label,
.stNumberInput label,
.stTextInput label,
.stTextArea label {
    color: rgba(246,251,255,0.84) !important;
    font-weight: 800 !important;
}

[data-testid="stMetricValue"] {
    color: #25f4ee;
}

hr {
    border-color: rgba(255,255,255,0.12);
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
}
</style>
""")


# =========================================================
# 顶部导航
# =========================================================

# 注意：普通用户看不到VIP高端商品，但可以看到“开通VIP通道”
safe_markdown(
    """
<div class="navbar">
    <div class="nav-logo">♻️ 倾城幻艺 · 青橙焕艺 AI平台</div>
    <div class="nav-links">
        <a href="#intro">项目简介</a>
        <a href="#factory">原料工厂</a>
        <a href="#database">工艺数据库</a>
        <a href="#recommend">AI推荐</a>
        <a href="#shop">产品商城</a>
        <a href="#vip">开通VIP</a>
        <a href="#finance">财务预测</a>
        <a href="#contact">联系我们</a>
    </div>
</div>
"""
)


# =========================================================
# Hero
# =========================================================

safe_markdown(
    """
<div class="hero">
    <div class="hero-content">
        <div class="hero-tag">GREEN LOW-CARBON · GLASS RECYCLING · AI DATABASE · ART PRODUCT</div>
        <h1>倾城幻艺 · 青橙焕艺</h1>
        <h2>
            面向高校创新创业大赛的新文科类绿色艺术项目。平台围绕废旧玻璃再生、热熔工艺实验、
            AI工艺数据库、公共艺术产品、高净值客户定制与VIP会员服务，形成从“上游原料采购”
            到“中游工坊设计生产”，再到“下游产品销售与会员增值服务”的商业闭环。
        </h2>
        <div class="hero-buttons">
            <a class="hero-btn" href="#factory">对接原料工厂</a>
            <a class="hero-btn-ghost" href="#database">查看工艺数据库</a>
            <a class="hero-btn-ghost" href="#vip">开通VIP服务</a>
        </div>
    </div>
</div>
"""
)


# =========================================================
# 项目简介
# =========================================================

safe_markdown('<div id="intro"></div>')

section_title(
    "PROJECT INTRODUCTION",
    "项目简介",
    "项目以废旧玻璃再生为基础，以AI工艺数据库和艺术设计能力为支撑，探索绿色材料、公共艺术和商业转化融合路径。"
)

c1, c2, c3 = st.columns(3)

with c1:
    glass_card(
        "♻️",
        "绿色低碳材料再生",
        "将废旧玻璃、边角料玻璃与回收玻璃重新导入艺术生产流程，减少资源浪费，符合绿色低碳、循环经济和可持续设计方向。"
    )

with c2:
    glass_card(
        "🔥",
        "青汐工坊热熔实验",
        "围绕760℃、780℃、800℃等温度开展烧制实验，记录颗粒感、体积感、透光度和过热风险，形成可解释的工艺经验。"
    )

with c3:
    glass_card(
        "🤖",
        "AI工艺数据库",
        "将实验记录、图片样例、温度参数和效果评分结构化，面向工艺推荐、产品设计、客户定制和技术服务平台进行延展。"
    )

c4, c5, c6 = st.columns(3)

with c4:
    glass_card(
        "🏛️",
        "公共艺术产品",
        "围绕校园、社区、商业空间、文旅场景设计玻璃公共艺术装置，提升项目从手工艺品到空间产品的商业高度。"
    )

with c5:
    glass_card(
        "🛍️",
        "产品销售闭环",
        "普通用户可购买文创产品，VIP客户可解锁高端定制产品，平台通过商品销售、会员服务和设计服务形成收入来源。"
    )

with c6:
    glass_card(
        "💼",
        "创新创业展示",
        "比赛展示重点从单一公益展示转向技术平台、产品体系、客户案例、盈利模型和未来3—5年增长规划。"
    )


# =========================================================
# 上游原料工厂对接
# =========================================================

safe_markdown('<div id="factory"></div>')

section_title(
    "UPSTREAM FACTORY CONNECTION",
    "上游原料工厂对接",
    "平台模拟对接原料工厂，完成废旧玻璃原料采购、质量筛选、用途匹配和成本估算，突出商业链路的上游基础。"
)

factory_col1, factory_col2 = st.columns([1.15, 0.85])

with factory_col1:
    st.markdown("### 原料采购交互")

    supplier = st.selectbox(
        "选择原料来源",
        [
            "城市玻璃回收站",
            "建筑玻璃边角料工厂",
            "酒瓶与饮料瓶回收企业",
            "彩色玻璃加工厂",
            "校园废玻璃回收点"
        ]
    )

    glass_type = st.selectbox(
        "选择玻璃类型",
        [
            "透明玻璃",
            "彩色玻璃",
            "混合玻璃",
            "建筑平板玻璃",
            "瓶罐玻璃",
            "实验小样材料包"
        ]
    )

    purity = st.selectbox(
        "原料等级",
        [
            "A级：杂质少，适合高端艺术产品",
            "B级：杂质可控，适合普通文创产品",
            "C级：需要二次筛选，适合实验与教学"
        ]
    )

    use_scene = st.selectbox(
        "采购用途",
        [
            "热熔实验",
            "文创产品量产",
            "灯具与透光产品",
            "公共艺术装置",
            "VIP高端定制"
        ]
    )

    weight = st.number_input("采购重量 / kg", min_value=1, max_value=10000, value=50, step=5)

    base_price_map = {
        "透明玻璃": 1.8,
        "彩色玻璃": 3.2,
        "混合玻璃": 2.4,
        "建筑平板玻璃": 1.5,
        "瓶罐玻璃": 1.2,
        "实验小样材料包": 6.8,
    }

    grade_factor = 1.45 if purity.startswith("A级") else 1.15 if purity.startswith("B级") else 0.85
    scene_factor = 1.35 if use_scene in ["公共艺术装置", "VIP高端定制"] else 1.0
    unit_price = base_price_map.get(glass_type, 2.0) * grade_factor * scene_factor
    raw_cost = round(unit_price * weight, 2)
    cleaning_cost = round(weight * 0.65, 2)
    transport_cost = round(80 + weight * 0.18, 2)
    total_cost = round(raw_cost + cleaning_cost + transport_cost, 2)

    safe_markdown(
        f"""
<div class="order-result">
    <h3>原料采购估算</h3>
    <p><b>供应来源：</b>{supplier}</p>
    <p><b>玻璃类型：</b>{glass_type}</p>
    <p><b>采购用途：</b>{use_scene}</p>
    <p><b>采购重量：</b>{weight} kg</p>
    <p><b>原料单价估算：</b>{unit_price:.2f} 元/kg</p>
    <p><b>原料成本：</b>{raw_cost:.2f} 元</p>
    <p><b>清洗筛选成本：</b>{cleaning_cost:.2f} 元</p>
    <p><b>物流成本：</b>{transport_cost:.2f} 元</p>
    <p><b>预计采购总成本：</b>{total_cost:.2f} 元</p>
</div>
"""
    )

    if st.button("提交原料采购需求", use_container_width=True):
        st.session_state.factory_orders.append(
            {
                "供应来源": supplier,
                "玻璃类型": glass_type,
                "原料等级": purity,
                "采购用途": use_scene,
                "重量kg": weight,
                "预计总成本": total_cost,
                "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        st.success("已提交原料采购需求，当前记录已加入平台采购台账。")

with factory_col2:
    info_panel(
        "为什么要展示上游原料工厂？",
        "创业组答辩不仅要讲作品，还要讲供应链。原料采购模块可以说明项目不是停留在手工展示，而是具备原料来源、成本控制、批量生产和后续盈利的商业基础。"
    )

    info_panel(
        "答辩表达建议",
        "可以表述为：我们将废旧玻璃来源分为城市回收、工厂边角料、校园回收和定向采购四类，并通过清洗、分级、筛选和热熔实验建立稳定的再生玻璃供应体系。"
    )

    if st.session_state.factory_orders:
        st.markdown("### 已提交采购记录")
        st.dataframe(pd.DataFrame(st.session_state.factory_orders), use_container_width=True, height=220)


# =========================================================
# 青汐工坊温度说明
# =========================================================

section_title(
    "FIRING TEMPERATURE KNOWLEDGE",
    "青汐工坊温度说明",
    "将你们自己的烧制经验展示出来，突出项目的工艺积累和可复现性。"
)

t1, t2, t3 = st.columns(3)

with t1:
    glass_card(
        "760℃",
        "推荐展示温度",
        "整体表现较稳定，颗粒感、体积感和透光度较均衡，适合花瓶、装饰画、灯具小样和比赛展示样品。"
    )

with t2:
    glass_card(
        "780℃",
        "偏高风险温度",
        "玻璃融合程度增强，但部分样品会出现颗粒边界变弱、体积感下降的问题，适合做对照实验。"
    )

with t3:
    glass_card(
        "800℃",
        "过热警示温度",
        "容易出现过度熔融，颗粒感和体积感明显减弱，可用于说明温度控制的重要性。"
    )


# =========================================================
# 工艺数据库
# =========================================================

safe_markdown('<div id="database"></div>')

section_title(
    "PROCESS DATABASE PREVIEW",
    "玻璃热熔工艺数据库",
    "数据库将实验温度、质量分、颗粒感、体积感、透光度和过热风险转化为可筛选、可分析、可推荐的数据资产。"
)

if df.empty:
    st.warning(f"没有找到数据文件，当前尝试路径：{DATA_PATH}")
else:
    temps = sorted(df["temperature_c"].dropna().unique()) if "temperature_c" in df.columns else []
    selected_temp = st.multiselect("选择温度", temps, default=temps)

    show_df = df.copy()

    if selected_temp and "temperature_c" in show_df.columns:
        show_df = show_df[show_df["temperature_c"].isin(selected_temp)]

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        metric_box(str(len(show_df)), "实验记录")

    with m2:
        avg_temp = round(show_df["temperature_c"].mean(), 1) if "temperature_c" in show_df.columns and len(show_df) else 0
        metric_box(f"{avg_temp}℃", "平均温度")

    with m3:
        avg_quality = round(show_df["overall_quality_score_100"].mean(), 1) if "overall_quality_score_100" in show_df.columns and len(show_df) else 0
        metric_box(str(avg_quality), "平均质量分")

    with m4:
        best_temp = "暂无"
        if "temperature_c" in show_df.columns and "overall_quality_score_100" in show_df.columns and len(show_df):
            best_temp = f"{int(show_df.groupby('temperature_c')['overall_quality_score_100'].mean().idxmax())}℃"
        metric_box(best_temp, "较优温度")

    st.markdown("### 实验记录表")
    st.dataframe(show_df, use_container_width=True, height=330)

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
        st.dataframe(mean_df, use_container_width=True, height=220)

        chart_col = "overall_quality_score_100"
        if chart_col in mean_df.columns:
            st.line_chart(mean_df.set_index("temperature_c")[chart_col])

        if "overall_quality_score_100" in mean_df.columns and len(mean_df):
            best_row = mean_df.loc[mean_df["overall_quality_score_100"].idxmax()]
            best_temp_value = int(best_row["temperature_c"])
            best_score = round(best_row["overall_quality_score_100"], 1)

            safe_markdown(
                f"""
<div class="recommend-result">
    <h3>温度趋势结论</h3>
    <p><b>较优温度：</b>{best_temp_value}℃</p>
    <p><b>平均综合质量分：</b>{best_score}</p>
    <p>从展示口径上，可以说明平台不是简单展示作品，而是将实验数据转化为后续AI推荐、客户定制和工艺服务的数据库基础。</p>
</div>
"""
            )


# =========================================================
# 烧制前后动态展示
# =========================================================

safe_markdown('<div id="gallery"></div>')

section_title(
    "BEFORE & AFTER DISPLAY",
    "烧制前后照片展示",
    "围绕760℃、780℃、800℃三组温度，将烧制前 qian 与烧制后 hou 进行动态展示。"
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
        slide_html += (
            f'<div class="slide">'
            f'<img src="{uri}">'
            f'<div class="slide-caption">'
            f'<strong>{item["title"]}</strong>'
            f'<span>{item["desc"]}</span>'
            f'<em>制作人员：{item["maker"]}</em>'
            f'</div>'
            f'</div>'
        )

if slide_html:
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
    animation: scrollX 34s linear infinite;
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
    st.info("请确认 images 文件夹中存在 760qian、760hou、780qian、780hou、800qian、800hou。没有图片也不会影响页面运行。")


# =========================================================
# 普通产品商城
# =========================================================

safe_markdown('<div id="shop"></div>')

section_title(
    "NORMAL PRODUCT SHOP",
    "普通产品购买区",
    "普通用户只能看到基础文创产品和普通商品，暂时看不到VIP高端商品。"
)

product_list = [
    {
        "name": "再生玻璃花器",
        "price": 168,
        "img": "1",
        "desc": "适合桌面陈设、花艺搭配和校园文创展示。"
    },
    {
        "name": "透光玻璃小夜灯",
        "price": 238,
        "img": "2",
        "desc": "利用透明玻璃和浅色玻璃形成柔和透光效果。"
    },
    {
        "name": "玻璃装饰画",
        "price": 198,
        "img": "3",
        "desc": "突出颗粒感、色彩层次和绿色再生材料的艺术表达。"
    },
    {
        "name": "玻璃文创饰品",
        "price": 88,
        "img": "4",
        "desc": "适合作为校园纪念品、伴手礼和活动周边。"
    },
]

product_cols = st.columns(4)

for idx, product in enumerate(product_list):
    with product_cols[idx]:
        image_card(
            resolve_image(product["img"]),
            product["name"],
            product["desc"],
            "价格",
            f"{product['price']} 元"
        )

        qty = st.number_input(
            f"{product['name']}数量",
            min_value=1,
            max_value=99,
            value=1,
            step=1,
            key=f"normal_qty_{idx}"
        )

        if st.button(f"加入购物车 · {product['name']}", key=f"add_normal_{idx}", use_container_width=True):
            add_to_cart(product["name"], product["price"], qty, "普通商品")
            st.success(f"已加入购物车：{product['name']} × {qty}")


# =========================================================
# AI 产品推荐
# =========================================================

safe_markdown('<div id="recommend"></div>')

section_title(
    "AI PRODUCT RECOMMENDATION",
    "AI工艺与产品推荐",
    "用户选择产品类型、材料和目标效果后，系统输出推荐温度区间、风险提示和产品设计建议。"
)

r1, r2 = st.columns([1.1, 0.9])

with r1:
    product_type = st.selectbox(
        "请选择产品类型",
        ["花瓶", "灯具", "装饰画", "艺术摆件", "公共艺术装置", "综合文创产品"]
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
        product_type,
        material,
        target_effect,
        temp
    )

    safe_markdown(
        f"""
<div class="recommend-result">
    <h3>AI推荐结果</h3>
    <p><b>用户选择产品：</b>{product_type}</p>
    <p><b>推荐工艺温度区间：</b>{temp_range}</p>
    <p><b>温度风险提示：</b>{risk}</p>
    <p><b>产品设计建议：</b>{product_tip}</p>
    <p><b>目标效果建议：</b>{effect_tip}</p>
    <p><b>材料建议：</b>{material_tip}</p>
    <p><b>综合推荐分：</b>{score} / 100</p>
</div>
"""
    )

    st.progress(score / 100)

with r2:
    # 不再依赖 images/11
    # 优先用 22，如果没有就用 5；如果都没有，也只显示占位提示
    recommend_img = resolve_image("22")
    if not recommend_img.exists():
        recommend_img = resolve_image("5")

    image_card(
        recommend_img,
        "推荐效果参考",
        "用于辅助展示热熔玻璃的发光、透光和材料转化效果，适合放在产品推荐系统旁作为视觉引导。"
    )


# =========================================================
# VIP开通页面
# =========================================================

safe_markdown('<div id="vip"></div>')

section_title(
    "VIP MEMBER CHANNEL",
    "VIP付费通道",
    "普通用户只能看到开通入口；只有购买VIP后，才会显示VIP专属产品和高端服务页面。"
)

if not st.session_state.vip_unlocked:
    safe_markdown(
        """
<div class="lock-panel">
    <h3>VIP专区当前未解锁</h3>
    <p>普通用户看不到VIP高端商品和VIP专属服务。请先开通VIP，系统才会显示下方VIP专区。</p>
</div>
"""
    )

    vip_col1, vip_col2, vip_col3 = st.columns(3)

    with vip_col1:
        glass_card(
            "⭐",
            "基础会员",
            "适合普通消费者，解锁基础定制咨询、部分工艺说明和普通产品优惠。展示价格：99元/月。"
        )

    with vip_col2:
        glass_card(
            "💎",
            "高级会员",
            "适合高净值客户和设计工作室，解锁高端产品购买、深度定制方案和优先排产。展示价格：299元/月。"
        )

    with vip_col3:
        glass_card(
            "🏛️",
            "机构会员",
            "适合学校、社区、商业空间和文旅项目，解锁公共艺术装置方案、批量设计服务和项目顾问支持。展示价格：999元/月。"
        )

    st.markdown("### 开通VIP")

    pay_col1, pay_col2 = st.columns([1, 1])

    with pay_col1:
        selected_vip = st.selectbox(
            "选择VIP类型",
            ["基础会员 / 99元", "高级会员 / 299元", "机构会员 / 999元"]
        )

        vip_price = 99
        if selected_vip.startswith("高级"):
            vip_price = 299
        elif selected_vip.startswith("机构"):
            vip_price = 999

        pay_name = st.text_input("购买人 / 单位名称", value="演示用户")
        pay_phone = st.text_input("联系电话", value="13800000000")

        safe_markdown(
            f"""
<div class="vip-panel">
    <h3>VIP订单预览</h3>
    <p><b>购买人：</b>{pay_name}</p>
    <p><b>联系电话：</b>{pay_phone}</p>
    <p><b>会员类型：</b>{selected_vip}</p>
    <p><b>支付金额：</b>{vip_price} 元</p>
    <p><b>说明：</b>此处为创新创业项目展示版，采用模拟支付逻辑。正式上线时可对接微信支付、支付宝或平台订单系统。</p>
</div>
"""
        )

        if st.button("模拟支付并开通VIP", use_container_width=True):
            st.session_state.vip_unlocked = True
            st.session_state.vip_level = selected_vip
            st.success(f"VIP已开通：{selected_vip}")
            st.rerun()

    with pay_col2:
        info_panel(
            "为什么设置VIP门槛？",
            "该模块用于展示平台模式和会员制盈利逻辑。普通用户只能浏览基础商品，VIP用户付费后才能进入高端产品、定制方案和公共艺术服务页面。"
        )

        info_panel(
            "答辩展示话术",
            "我们把平台用户分为普通用户和VIP用户。普通用户购买标准文创产品，VIP用户购买高端定制、公共艺术方案和深度工艺服务，从而形成分层收费模式。"
        )

else:
    safe_markdown(
        f"""
<div class="vip-panel">
    <h3>VIP专区已解锁</h3>
    <p><b>当前会员状态：</b>{st.session_state.vip_level}</p>
    <p>你已开通VIP，现在可以查看并购买VIP专属高端产品和定制服务。</p>
</div>
"""
    )

    if st.button("退出VIP演示状态", use_container_width=True):
        st.session_state.vip_unlocked = False
        st.session_state.vip_level = "未开通"
        st.rerun()


# =========================================================
# VIP高端产品区
# 关键逻辑：只有 st.session_state.vip_unlocked == True 时才会显示
# 普通用户完全看不到这一块的商品内容
# =========================================================

if st.session_state.vip_unlocked:
    section_title(
        "VIP PREMIUM PRODUCTS",
        "VIP高端产品购买区",
        "该区域只有购买VIP后才显示。普通用户无法看到这里的产品、价格和服务内容。"
    )

    premium_products = [
        {
            "name": "高端定制玻璃艺术摆件",
            "price": 1280,
            "img": "5",
            "desc": "面向高净值客户、办公室陈设和礼品场景，提供颜色、造型和主题定制。"
        },
        {
            "name": "再生玻璃公共艺术方案",
            "price": 6800,
            "img": "22",
            "desc": "适合校园、社区、商业空间展示，包含设计方案、材料建议和小样制作。"
        },
        {
            "name": "企业ESG绿色艺术礼盒",
            "price": 3980,
            "img": "3",
            "desc": "面向企业ESG活动、公益展示和客户礼品，突出绿色低碳与艺术价值。"
        },
    ]

    premium_cols = st.columns(3)

    for idx, product in enumerate(premium_products):
        with premium_cols[idx]:
            image_card(
                resolve_image(product["img"]),
                product["name"],
                product["desc"],
                "VIP价格",
                f"{product['price']} 元"
            )

            qty = st.number_input(
                f"{product['name']}数量",
                min_value=1,
                max_value=20,
                value=1,
                step=1,
                key=f"vip_qty_{idx}"
            )

            if st.button(f"VIP购买 · {product['name']}", key=f"add_vip_{idx}", use_container_width=True):
                add_to_cart(product["name"], product["price"], qty, "VIP高端商品")
                st.success(f"已加入购物车：{product['name']} × {qty}")

    section_title(
        "VIP DEEP SERVICE",
        "VIP深度服务申请",
        "VIP用户可以进一步提交定制需求，适合展示高净值客户合作、公共艺术项目和企业服务场景。"
    )

    service_col1, service_col2 = st.columns([1, 1])

    with service_col1:
        service_type = st.selectbox(
            "选择VIP服务类型",
            [
                "高端艺术摆件定制",
                "公共艺术装置设计",
                "企业ESG礼品方案",
                "校园环保艺术课程",
                "文旅空间玻璃艺术方案"
            ]
        )

        budget = st.selectbox(
            "预算区间",
            [
                "1000元 - 3000元",
                "3000元 - 8000元",
                "8000元 - 20000元",
                "20000元以上"
            ]
        )

        demand = st.text_area(
            "填写定制需求",
            placeholder="例如：希望使用蓝绿色玻璃，做一个适合公司前台展示的环保艺术装置。"
        )

        if st.button("提交VIP定制需求", use_container_width=True):
            st.success("VIP定制需求已提交。展示版不会真实发送数据，正式上线可对接后台订单系统。")

    with service_col2:
        info_panel(
            "VIP深度服务价值",
            "该模块可以在答辩中说明项目不仅销售小型文创产品，还可以进一步面向机构客户、商业空间和高净值客户提供定制化服务。"
        )

        info_panel(
            "商业赛道表达",
            "展示VIP服务时，可以重点强调高客单价、项目制收入、设计服务费和技术服务费，增强创业组的营收想象力。"
        )


# =========================================================
# 购物车
# =========================================================

section_title(
    "SHOPPING CART",
    "购物车与订单汇总",
    "汇总普通商品和VIP商品，便于展示平台从浏览、推荐、会员到购买的商业闭环。"
)

if st.session_state.cart:
    cart_df = pd.DataFrame(st.session_state.cart)
    total_amount = round(cart_df["小计"].sum(), 2)

    st.dataframe(cart_df, use_container_width=True, height=260)

    c_total1, c_total2, c_total3 = st.columns(3)

    with c_total1:
        metric_box(f"{len(cart_df)}", "订单条目")

    with c_total2:
        metric_box(f"{cart_df['数量'].sum()}", "商品总数量")

    with c_total3:
        metric_box(f"{total_amount:.2f}元", "订单总金额")

    remark = st.text_area(
        "订单备注",
        placeholder="例如：希望颜色偏蓝绿色；用于办公室陈设；需要开发票等。"
    )

    if st.button("提交订单", use_container_width=True):
        st.success("订单已提交。展示版不会产生真实支付，正式上线可对接订单后台与支付接口。")

    if st.button("清空购物车", use_container_width=True):
        st.session_state.cart = []
        st.rerun()

else:
    st.info("购物车暂无商品。可以在普通产品购买区加入商品；开通VIP后可以购买VIP高端商品。")


# =========================================================
# 平台模式
# =========================================================

section_title(
    "PLATFORM BUSINESS MODEL",
    "平台模式与商业闭环",
    "结合会议建议，将项目从单一作品展示升级为技术服务平台、会员平台和产品交易平台。"
)

b1, b2, b3 = st.columns(3)

with b1:
    glass_card(
        "🔗",
        "技术撮合交易",
        "平台一端连接原料工厂、回收渠道和设计师，另一端连接消费者、机构客户和空间项目方，形成技术与需求撮合。"
    )

with b2:
    glass_card(
        "🧠",
        "AI数据库服务",
        "常规数据开放用于展示，深度参数、工艺建议、批量方案和定制模型作为付费服务，增强技术壁垒。"
    )

with b3:
    glass_card(
        "💳",
        "会员制盈利",
        "通过基础会员、高级会员和机构会员分层收费，叠加商品销售、设计服务、公共艺术项目和企业ESG定制。"
    )


# =========================================================
# 财务预测
# =========================================================

safe_markdown('<div id="finance"></div>')

section_title(
    "FINANCIAL FORECAST",
    "财务预测展示",
    "根据会议内容，将2026年三大核心业务合计盈利40万元、单位成本下降20%、净利润率提升到30%以上作为展示目标。"
)

finance_data = pd.DataFrame(
    [
        {"业务类型": "再生玻璃文创产品", "预计收入万元": 55, "预计成本万元": 36, "预计利润万元": 19},
        {"业务类型": "VIP高端定制服务", "预计收入万元": 42, "预计成本万元": 27, "预计利润万元": 15},
        {"业务类型": "公共艺术与技术服务", "预计收入万元": 24, "预计成本万元": 18, "预计利润万元": 6},
    ]
)

finance_data["净利润率"] = (finance_data["预计利润万元"] / finance_data["预计收入万元"] * 100).round(1)

st.dataframe(finance_data, use_container_width=True, height=180)

f1, f2, f3, f4 = st.columns(4)

with f1:
    metric_box("121万", "2026年预计收入")

with f2:
    metric_box("40万", "2026年预计利润")

with f3:
    metric_box("20%", "单位成本下降目标")

with f4:
    metric_box("30%+", "目标净利润率")

st.bar_chart(finance_data.set_index("业务类型")[["预计收入万元", "预计利润万元"]])


# =========================================================
# 答辩建议
# =========================================================

section_title(
    "PITCH SUGGESTIONS",
    "答辩展示建议",
    "围绕会议纪要中的痛点、赛道选择和展示建议，对平台答辩内容进行强化。"
)

with st.expander("01 项目痛点如何讲", expanded=True):
    st.write(
        "建议从产品同质化、传播局限、认知壁垒三个角度展开。不要只说我们做了玻璃产品，而要强调传统玻璃再生产品缺少数据体系、设计转化和高端场景。"
    )

with st.expander("02 解决方案如何讲"):
    st.write(
        "可以表达为：我们以AI工艺数据库为核心，用实验数据降低工艺不确定性，用设计人才提升产品审美，用平台模式连接原料、工坊、设计师和客户。"
    )

with st.expander("03 创业组如何讲"):
    st.write(
        "创业组要突出主线产品、营收来源和规模化可能。建议主打：再生玻璃文创产品 + VIP高端定制 + 公共艺术/技术服务三条收入线。"
    )

with st.expander("04 展示内容如何调整"):
    st.write(
        "商业赛道展示时，应减少单纯社区服务内容，增加高净值客户合作、公共艺术案例、企业ESG定制和VIP会员服务，突出盈利能力。"
    )

with st.expander("05 近期待办"):
    st.write(
        "1. 回去与戴主任商量确定参赛方向；2. 给任老师传项目资料；3. 完善含商学院成员的团队；4. 进一步打磨答辩稿，减少口语化和不确定表述。"
    )


# =========================================================
# 联系我们
# =========================================================

safe_markdown('<div id="contact"></div>')

section_title(
    "CONTACT US",
    "联系我们",
    "让废旧玻璃重新发光，让绿色材料进入艺术生活。"
)

safe_markdown(
    """
<div class="contact-shell">
    <h2>倾城幻艺 · 青橙焕艺</h2>
    <p>青汐工坊 · Glass Recycling AI Platform · 绿色低碳艺术创业项目</p>
</div>
"""
)

cc1, cc2, cc3 = st.columns(3)

with cc1:
    safe_markdown(
        """
<div class="contact-item-card">
    <h3>公司定位</h3>
    <p>废旧玻璃再生</p>
    <p>艺术产品设计</p>
    <p>绿色低碳创业项目</p>
</div>
"""
    )

with cc2:
    safe_markdown(
        """
<div class="contact-item-card">
    <h3>平台方向</h3>
    <p>AI工艺数据库</p>
    <p>产品推荐系统</p>
    <p>技术服务平台</p>
</div>
"""
    )

with cc3:
    safe_markdown(
        """
<div class="contact-item-card">
    <h3>商业模式</h3>
    <p>文创产品销售</p>
    <p>VIP高端定制</p>
    <p>公共艺术服务</p>
</div>
"""
    )