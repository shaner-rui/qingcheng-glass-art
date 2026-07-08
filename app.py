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
    page_title="青承焕艺再生玻璃技术服务平台",
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
# 状态管理
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "vip_unlocked" not in st.session_state:
    st.session_state.vip_unlocked = False

if "vip_level" not in st.session_state:
    st.session_state.vip_level = "未开通"

if "factory_orders" not in st.session_state:
    st.session_state.factory_orders = []

if "service_orders" not in st.session_state:
    st.session_state.service_orders = []


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
            "temperature_c": 700,
            "success_score": 78,
            "particle_score": 82,
            "volume_score": 79,
            "transparency_score": 74,
            "overheat_score": 10,
            "overall_quality_score_100": 78
        },
        {
            "temperature_c": 720,
            "success_score": 82,
            "particle_score": 86,
            "volume_score": 82,
            "transparency_score": 78,
            "overheat_score": 14,
            "overall_quality_score_100": 82
        },
        {
            "temperature_c": 760,
            "success_score": 88,
            "particle_score": 90,
            "volume_score": 86,
            "transparency_score": 82,
            "overheat_score": 18,
            "overall_quality_score_100": 88
        },
        {
            "temperature_c": 760,
            "success_score": 86,
            "particle_score": 88,
            "volume_score": 84,
            "transparency_score": 85,
            "overheat_score": 20,
            "overall_quality_score_100": 86
        },
        {
            "temperature_c": 780,
            "success_score": 74,
            "particle_score": 68,
            "volume_score": 70,
            "transparency_score": 76,
            "overheat_score": 42,
            "overall_quality_score_100": 73
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


def metric_box(value: str, label: str, sub: str = ""):
    sub_html = f"<small>{sub}</small>" if sub else ""
    safe_markdown(
        f"""
<div class="metric-box">
    <h3>{value}</h3>
    <p>{label}</p>
    {sub_html}
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


def chain_step(num: str, title: str, text: str):
    safe_markdown(
        f"""
<div class="chain-step">
    <div class="chain-num">{num}</div>
    <h3>{title}</h3>
    <p>{text}</p>
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
    <small>请将图片放入项目 images 文件夹；该图片不存在时系统仍可运行。</small>
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
    font-family: "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif;
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


def recommend(product_type: str, material: str, target_effect: str, temp: int, thickness: str, particle: str):
    if product_type == "再生玻璃艺术板材":
        base_temp = "720℃ - 760℃"
        product_tip = "艺术板材需要稳定平整度与肌理层次，方案小样确定颜色分布后再放大生产。"
    elif product_type == "灯具":
        base_temp = "735℃ - 765℃"
        product_tip = "灯具更重视透光度，方案使用透明玻璃或浅色玻璃组合，避免颜色堆叠过厚。"
    elif product_type == "装饰画":
        base_temp = "720℃ - 760℃"
        product_tip = "装饰画适合保留颗粒边界和色彩层次，温度不宜过高。"
    elif product_type == "公共艺术装置":
        base_temp = "740℃ - 775℃"
        product_tip = "公共艺术装置需要兼顾强度、造型和视觉冲击力，方案先小样验证再放大制作。"
    elif product_type == "艺术摆件":
        base_temp = "745℃ - 775℃"
        product_tip = "艺术摆件可适当增强体积感，但要避免温度过高造成形态塌陷。"
    else:
        base_temp = "730℃ - 765℃"
        product_tip = "综合文创产品方案先做小样测试，再根据成品效果扩大尺寸。"

    if temp >= 795:
        risk = "当前温度偏高，容易导致玻璃过度熔融，颗粒感和体积感下降。方案明显降温。"
        score = 45
        risk_level = "高风险"
    elif 775 <= temp < 795:
        risk = "当前温度仍偏高，颗粒边界可能变弱，方案向760℃附近调整。"
        score = 64
        risk_level = "中高风险"
    elif 720 <= temp < 775:
        risk = "当前温度处于低温热熔较适宜区间，适合形成颗粒感、体积感和较好的透光表现。"
        score = 88
        risk_level = "较低风险"
    else:
        risk = "当前温度可能偏低，玻璃融合度不足，成品牢固性可能下降。"
        score = 58
        risk_level = "中风险"

    if target_effect == "颗粒感明显":
        effect_tip = "应减少过度熔融，重点保留玻璃颗粒边界。"
    elif target_effect == "透光度强":
        effect_tip = "应选择透明或浅色玻璃，并避免颜色堆叠过厚。"
    elif target_effect == "体积感强":
        effect_tip = "应控制局部堆叠厚度，让玻璃融合但不完全摊平。"
    else:
        effect_tip = "方案平衡颗粒感、透光度和体积感，适合商业样品。"

    if material == "透明玻璃":
        material_tip = "透明玻璃适合灯具、窗饰和透光艺术板。"
    elif material == "彩色玻璃":
        material_tip = "彩色玻璃视觉表现强，适合装饰画和艺术摆件。"
    elif material == "混合玻璃":
        material_tip = "混合玻璃层次丰富，但需要注意颜色过杂。"
    elif material == "建筑平板玻璃":
        material_tip = "建筑平板玻璃适合再生板材和空间材料，但需要重视边角预处理。"
    else:
        material_tip = "方案先做小样实验，记录温度和最终效果。"

    if thickness == "薄层 3-5mm":
        thickness_tip = "薄层适合装饰画、饰品和灯罩类产品，升温和降温应更平缓。"
    elif thickness == "中层 6-10mm":
        thickness_tip = "中层适合板材、摆件和桌面产品，兼顾结构稳定与肌理表现。"
    else:
        thickness_tip = "厚层适合公共艺术装置，但方案分层烧制，降低开裂风险。"

    if particle == "细颗粒":
        particle_tip = "细颗粒更容易融合，适合追求细腻质感。"
    elif particle == "中颗粒":
        particle_tip = "中颗粒综合表现较稳定，适合多数产品。"
    else:
        particle_tip = "粗颗粒视觉冲击力强，但需要更谨慎控制温度与保温时间。"

    hold_time = "28-35分钟" if score >= 80 else "20-28分钟" if temp < 720 else "方案重新调整温度后再设定"
    energy_compare = "相较传统高温工艺，展示模型按低温热熔路径估算，可显著降低能耗与试错损耗。"

    return {
        "base_temp": base_temp,
        "risk": risk,
        "score": score,
        "risk_level": risk_level,
        "product_tip": product_tip,
        "effect_tip": effect_tip,
        "material_tip": material_tip,
        "thickness_tip": thickness_tip,
        "particle_tip": particle_tip,
        "hold_time": hold_time,
        "energy_compare": energy_compare,
    }


df = load_data(str(DATA_PATH))


# =========================================================
# 全局 CSS
# =========================================================

safe_markdown("""
<style>
:root {
    --cyan: #25f4ee;
    --orange: #ff9f43;
    --green: #80ff72;
    --blue: #6aa8ff;
    --white: #f6fbff;
}

html, body, .stApp {
    font-family: "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif;
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
    max-width: 1360px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 1.25rem;
    padding: 0.78rem 1.2rem;
    border-radius: 999px;
    background: rgba(6, 19, 31, 0.78);
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
    min-height: 660px;
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
    width: 380px;
    height: 380px;
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
    max-width: 1020px;
    font-size: clamp(1.05rem, 2vw, 1.42rem);
    line-height: 1.9;
    color: rgba(246,251,255,0.84);
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

.hero-kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(130px, 1fr));
    gap: 1rem;
    max-width: 1020px;
    margin-top: 2.2rem;
}

.hero-kpi {
    padding: 1rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
}

.hero-kpi strong {
    display: block;
    color: var(--cyan);
    font-size: 1.55rem;
    font-weight: 900;
}

.hero-kpi span {
    display: block;
    color: rgba(246,251,255,0.72);
    margin-top: 0.25rem;
    line-height: 1.45;
}

.section-head {
    text-align: center;
    margin: 5rem auto 2rem;
    max-width: 980px;
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
.contact-item-card,
.chain-step {
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

.chain-step {
    min-height: 230px;
    position: relative;
    overflow: hidden;
}

.chain-step::after {
    content: "";
    position: absolute;
    right: -50px;
    bottom: -50px;
    width: 150px;
    height: 150px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(37,244,238,0.16), transparent 70%);
}

.glass-card:hover,
.info-panel:hover,
.contact-item-card:hover,
.chain-step:hover {
    transform: translateY(-7px);
    border-color: rgba(37,244,238,0.48);
    box-shadow: 0 0 32px rgba(37,244,238,0.22), 0 18px 52px rgba(0,0,0,0.35);
}

.icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}

.chain-num {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--cyan), var(--orange));
    color: #05111e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    margin-bottom: 1rem;
}

.glass-card h3,
.info-panel h3,
.contact-item-card h3,
.chain-step h3 {
    color: #fff;
    margin-bottom: 0.7rem;
    font-size: 1.22rem;
    font-weight: 900;
}

.glass-card p,
.info-panel p,
.contact-item-card p,
.chain-step p {
    color: rgba(246,251,255,0.74);
    line-height: 1.75;
}

.metric-box {
    padding: 1.15rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.13);
    text-align: center;
    min-height: 125px;
}

.metric-box h3 {
    color: var(--cyan);
    margin: 0;
    font-size: 2rem;
    font-weight: 900;
}

.metric-box p {
    color: rgba(246,251,255,0.70);
    margin: 0.3rem 0 0;
}

.metric-box small {
    color: rgba(255,207,154,0.95);
    display: block;
    margin-top: 0.35rem;
    line-height: 1.45;
}

.recommend-result,
.order-result,
.vip-panel,
.lock-panel,
.design-panel {
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
.lock-panel h3,
.design-panel h3 {
    margin-top: 0;
    color: var(--cyan);
    font-weight: 900;
}

.recommend-result p,
.order-result p,
.vip-panel p,
.lock-panel p,
.design-panel p {
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

@media (max-width: 900px) {
    .hero-kpis {
        grid-template-columns: repeat(2, minmax(130px, 1fr));
    }
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

    .hero-kpis {
        grid-template-columns: 1fr;
    }
}
</style>
""")


# =========================================================
# 顶部导航
# =========================================================

safe_markdown(
    """
<div class="navbar">
    <div class="nav-logo">♻️青承焕艺技术服务平台</div>
    <div class="nav-links">
        <a href="#intro">项目简介</a>
        <a href="#pain">行业痛点</a>
        <a href="#factory">原料工厂</a>
        <a href="#database">工艺数据库</a>
        <a href="#recommend">AI匹配</a>
        <a href="#shop">产品商城</a>
        <a href="#vip">VIP服务</a>
        <a href="#finance">财务模型</a>
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
        <div class="hero-tag">LOW-TEMPERATURE FUSION · AI DESIGN · B2B2C PLATFORM · GREEN MATERIAL</div>
        <h1>青承焕艺</h1>
        <h2>
            面向玻璃产业绿色转型的再生玻璃低温热熔技术服务平台。系统围绕工业玻璃废料回收、
            低温热熔工艺、AI智能设计、再生玻璃艺术板材、公共空间装置、文创销售与技术服务，
            构建从“废料处理”到“材料增值”的数字化商业闭环。
        </h2>
        <div class="hero-buttons">
            <a class="hero-btn" href="#factory">进入原料对接</a>
            <a class="hero-btn-ghost" href="#database">查看工艺数据</a>
            <a class="hero-btn-ghost" href="#recommend">体验AI匹配</a>
            <a class="hero-btn-ghost" href="#vip">开通VIP服务</a>
        </div>
        <div class="hero-kpis">
            <div class="hero-kpi"><strong>1400℃ → 700℃</strong><span>低温热熔路径，降低传统高温工艺门槛</span></div>
            <div class="hero-kpi"><strong>50+款</strong><span>家居、文创与公共空间产品开发基础</span></div>
            <div class="hero-kpi"><strong>80%-90%</strong><span>工业废料原料成本压缩展示模型</span></div>
            <div class="hero-kpi"><strong>B2B2C</strong><span>原料、生产、设计、销售与服务闭环</span></div>
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
    "以低温热熔再生玻璃技术为核心，以再生玻璃材料产品与技术服务平台为主营方向，连接废料回收、工艺研发、智能设计、板材生产、场景应用和数据服务。"
)

c1, c2, c3 = st.columns(3)

with c1:
    glass_card(
        "♻️",
        "工业废料高值转化",
        "将玻璃厂废料、建筑玻璃边角料和校园回收玻璃重新导入艺术生产流程，实现从低值废料到高附加值材料产品的转化。"
    )

with c2:
    glass_card(
        "🔥",
        "低温热熔工艺体系",
        "围绕700℃—800℃低温热熔区间进行参数控制，减少传统高温烧制带来的高能耗、高成本和高碳排放压力。"
    )

with c3:
    glass_card(
        "🤖",
        "AI智能设计模块",
        "围绕废料颜色、颗粒尺度、熔融温度、肌理效果和应用场景建立参数模型，辅助生成设计方案和工艺方案。"
    )

c4, c5, c6 = st.columns(3)

with c4:
    glass_card(
        "🏛️",
        "再生玻璃艺术板材",
        "主线产品面向家居建材、商业空间、企业展厅、文旅文创和公共艺术装置，强化产品可销售与可交付能力。"
    )

with c5:
    glass_card(
        "🔗",
        "技术服务平台",
        "向玻璃企业、设计机构、园区和环保运营方提供工艺包、配方数据库、样品打样、供应链撮合和专家诊断服务。"
    )

with c6:
    glass_card(
        "💼",
        "复合收入结构",
        "形成产品销售、技术服务、平台会员和定制交付协同增长的收入结构，增强项目持续经营能力。"
    )


# =========================================================
# 行业痛点
# =========================================================

safe_markdown('<div id="pain"></div>')

section_title(
    "INDUSTRY PAIN POINTS",
    "行业痛点与解决路径",
    "围绕高成本、高能耗、同质化、传播局限、上下游信息割裂和工艺试错风险，展示平台的实际切入点。"
)

p1, p2, p3 = st.columns(3)

with p1:
    glass_card(
        "⚠️",
        "高成本与高环境负荷",
        "废旧玻璃回收分拣、清洗、运输成本高，传统高温热熔依赖高能耗生产路径，压缩企业利润空间。"
    )

with p2:
    glass_card(
        "🎨",
        "产品同质化与美学缺失",
        "普通再生玻璃产品容易停留在低价、低识别度和基础器物层面，难以形成设计溢价和品牌价值。"
    )

with p3:
    glass_card(
        "🧩",
        "上下游信息割裂",
        "回收端、生产端、设计端和市场端缺少统一数据平台，工艺参数无法共享，生产试错依赖经验判断。"
    )

p4, p5, p6 = st.columns(3)

with p4:
    glass_card(
        "📉",
        "传播链条断裂",
        "消费者难以理解废料回收、低温热熔和艺术设计过程，产品价值容易被简化为普通玻璃制品。"
    )

with p5:
    glass_card(
        "🧠",
        "智能决策不足",
        "中小工坊缺少工艺数据库、参数匹配和风险预警工具，难以前置判断开裂、过熔、透光不足等风险。"
    )

with p6:
    glass_card(
        "✅",
        "平台化破局",
        "青承焕艺以工艺数据库、AI匹配、产品展示、原料对接和会员服务串联全链路，降低协作与试错成本。"
    )


# =========================================================
# B2B2C链路
# =========================================================

section_title(
    "B2B2C DIGITAL LOOP",
    "B2B2C数字化循环链路",
    "平台将B端玻璃厂废料、再生加工、设计服务与C端产品购买连成一体，形成可展示、可交易、可复用的数据闭环。"
)

s1, s2, s3, s4, s5 = st.columns(5)

with s1:
    chain_step("01", "上游废料进入", "玻璃工厂、回收站、校园回收点发布废料类型、重量、颜色、杂质等级和库存数据。")

with s2:
    chain_step("02", "平台估价分级", "根据玻璃类型、纯度、用途和采购重量估算原料成本、清洗成本和物流成本。")

with s3:
    chain_step("03", "AI工艺匹配", "输入材料、厚度、颗粒尺度和目标效果，匹配温度区间、保温时间与风险等级。")

with s4:
    chain_step("04", "工坊生产交付", "青汐工坊完成小样验证、板材热熔、产品打样、定制生产与质量记录。")

with s5:
    chain_step("05", "销售与数据回流", "普通商品、VIP高端商品和技术服务订单形成销售闭环，效果数据继续回流工艺库。")


# =========================================================
# 上游原料工厂对接
# =========================================================

safe_markdown('<div id="factory"></div>')

section_title(
    "UPSTREAM FACTORY CONNECTION",
    "上游原料工厂对接",
    "平台模拟原料供需对接，完成废旧玻璃原料采购、质量筛选、用途匹配和成本估算，突出供应链基础。"
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
            "再生玻璃板材",
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
    scene_factor = 1.38 if use_scene in ["公共艺术装置", "VIP高端定制", "再生玻璃板材"] else 1.0
    unit_price = base_price_map.get(glass_type, 2.0) * grade_factor * scene_factor
    raw_cost = round(unit_price * weight, 2)
    cleaning_cost = round(weight * 0.65, 2)
    transport_cost = round(80 + weight * 0.18, 2)
    total_cost = round(raw_cost + cleaning_cost + transport_cost, 2)
    estimated_new_material_cost = round(total_cost / 0.22, 2)
    saved_cost = round(max(estimated_new_material_cost - total_cost, 0), 2)

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
    <p><b>相较新料采购的成本优势展示：</b>约节省 {saved_cost:.2f} 元</p>
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
    metric_box("80%-90%", "原料成本压缩模型", "以工业废料直供替代高价原生材料")
    metric_box("12个月", "盈亏平衡展示目标", "以轻资产、代工、会员和服务收入提升周转")
    metric_box("2.5次/年", "资产周转展示目标", "轻资产平台化运营，提高资金效率")

    if st.session_state.factory_orders:
        st.markdown("### 已提交采购记录")
        st.dataframe(pd.DataFrame(st.session_state.factory_orders), use_container_width=True, height=220)


# =========================================================
# 温度工艺说明
# =========================================================

section_title(
    "FIRING TEMPERATURE KNOWLEDGE",
    "低温热熔工艺说明",
    "将项目自己的烧制经验展示出来，突出工艺积累、低温路径和参数可复现性。"
)

t1, t2, t3, t4 = st.columns(4)

with t1:
    glass_card(
        "700℃",
        "低温边界区",
        "适合初步熔结和小样探索，能保留较明显颗粒结构，但融合度和结构强度需要重点验证。"
    )

with t2:
    glass_card(
        "760℃",
        "推荐展示温度",
        "整体表现较稳定，颗粒感、体积感和透光度较均衡，适合花瓶、装饰画、灯具小样和商业样品。"
    )

with t3:
    glass_card(
        "780℃",
        "偏高风险温度",
        "玻璃融合程度增强，但部分样品会出现颗粒边界变弱、体积感下降的问题，适合做对照实验。"
    )

with t4:
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
    <p>平台将实验数据转化为后续AI匹配、客户定制和工艺服务的数据库基础。</p>
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
# AI 产品推荐
# =========================================================

safe_markdown('<div id="recommend"></div>')

section_title(
    "AI PROCESS MATCHING",
    "AI工艺与产品匹配",
    "用户选择产品类型、材料、厚度、颗粒尺度和目标效果后，系统输出推荐温度区间、风险提示和产品设计方案。"
)

r1, r2 = st.columns([1.1, 0.9])

with r1:
    product_type = st.selectbox(
        "请选择产品类型",
        ["再生玻璃艺术板材", "花瓶", "灯具", "装饰画", "艺术摆件", "公共艺术装置", "综合文创产品"]
    )

    material = st.selectbox(
        "请选择材料类型",
        ["透明玻璃", "彩色玻璃", "混合玻璃", "建筑平板玻璃", "其他材料"]
    )

    thickness = st.selectbox(
        "请选择材料厚度",
        ["薄层 3-5mm", "中层 6-10mm", "厚层 10mm以上"]
    )

    particle = st.selectbox(
        "请选择颗粒尺度",
        ["细颗粒", "中颗粒", "粗颗粒"]
    )

    target_effect = st.selectbox(
        "请选择目标效果",
        ["颗粒感明显", "透光度强", "体积感强", "综合艺术效果"]
    )

    temp = st.slider("计划烧制温度 / ℃", 680, 850, 760, 5)

    rec = recommend(
        product_type,
        material,
        target_effect,
        temp,
        thickness,
        particle
    )

    # 突出显示计划烧制温度和综合推荐分，综合推荐分略小于温度，且保持在同行显示
    safe_markdown(
        f"""
<div class="recommend-result">
    <h3>AI匹配结果</h3>
    <p><b>用户选择产品：</b>{product_type}</p>
    <p><b>匹配工艺温度区间：</b>{rec["base_temp"]}</p>
    <p style="font-size: 3.2rem; font-weight: 900; color: var(--cyan); margin: 0.4rem 0; line-height: 1.2;">
        计划烧制温度：{temp}℃
    </p>
    <p><b>方案保温时间：</b>{rec["hold_time"]}</p>
    <p><b>风险等级：</b>{rec["risk_level"]}</p>
    <p><b>温度风险提示：</b>{rec["risk"]}</p>
    <p><b>产品设计方案：</b>{rec["product_tip"]}</p>
    <p><b>目标效果方案：</b>{rec["effect_tip"]}</p>
    <p><b>材料方案：</b>{rec["material_tip"]}</p>
    <p><b>厚度方案：</b>{rec["thickness_tip"]}</p>
    <p><b>颗粒方案：</b>{rec["particle_tip"]}</p>
    <p><b>低温路径说明：</b>{rec["energy_compare"]}</p>
    <p style="font-size: 2.8rem; font-weight: 900; color: var(--orange); margin: 0.4rem 0; line-height: 1.2; white-space: nowrap;">
        综合推荐分：{rec["score"]} / 100
    </p>
</div>
"""
    )

    st.progress(rec["score"] / 100)

with r2:
    recommend_img = resolve_image("22")

    if not recommend_img.exists():
        recommend_img = resolve_image("5")

    image_card(
        recommend_img,
        "效果参考",
        "用于辅助展示热熔玻璃的发光、透光和材料转化效果，适合放在AI匹配系统旁作为视觉引导。"
    )


# =========================================================
# AI智能设计模拟
# =========================================================

section_title(
    "AI DESIGN SIMULATION",
    "AI智能设计模拟",
    "围绕废料颜色、场景需求和产品定位生成设计方向，展示参数输入、效果描述、工艺方案方案的产品化能力。"
)

d1, d2 = st.columns([1, 1])

with d1:
    theme = st.selectbox(
        "选择设计主题",
        ["冰川裂痕", "城市记忆", "海岸流光", "校园绿洲", "企业低碳展陈"]
    )

    color_style = st.selectbox(
        "选择色彩方向",
        ["蓝绿色", "琥珀橙色", "透明白色", "混合彩色", "黑白灰极简"]
    )

    scene = st.selectbox(
        "选择应用场景",
        ["家居软装", "商业空间", "企业展厅", "文旅文创", "公共艺术装置", "校园美育课程"]
    )

    size_level = st.selectbox(
        "选择产品尺度",
        ["小型饰品", "中型摆件", "板材样品", "空间装置"]
    )

    design_score = 82
    if scene in ["企业展厅", "公共艺术装置"]:
        design_score += 6
    if size_level in ["板材样品", "空间装置"]:
        design_score += 4
    if color_style in ["蓝绿色", "透明白色"]:
        design_score += 3
    design_score = min(design_score, 96)

with d2:
    safe_markdown(
        f"""
<div class="design-panel">
    <h3>智能设计方向</h3>
    <p><b>设计主题：</b>{theme}</p>
    <p><b>色彩方向：</b>{color_style}</p>
    <p><b>应用场景：</b>{scene}</p>
    <p><b>产品尺度：</b>{size_level}</p>
    <p><b>设计说明：</b>以“{theme}”为视觉叙事，将{color_style}废玻璃颗粒通过低温热熔形成自然流动肌理，适配{scene}场景中的展示、陈设与绿色传播需求。</p>
    <p><b>工艺方案：</b>先完成30cm小样打样，记录温度、保温时间、颗粒尺度和成品透光度，再进入放大生产。</p>
    <p><b>方案匹配度：</b>{design_score} / 100</p>
</div>
"""
    )
    st.progress(design_score / 100)


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
        "name": "再生玻璃板材样品",
        "price": 298,
        "img": "3",
        "desc": "突出颗粒感、色彩层次和绿色再生材料的艺术表达。"
    },
    {
        "name": "玻璃文创饰品",
        "price": 88,
        "img": "4",
        "desc": "适合作为校园纪念品、伴手礼和活动周边。"
    },
    {
        "name": "再生玻璃杯器",
        "price": 128,
        "img": "5",
        "desc": "适合生活美学场景，强调环保材料和日用价值。"
    },
]

product_cols = st.columns(5)

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
# VIP开通页面
# =========================================================

safe_markdown('<div id="vip"></div>')

section_title(
    "VIP MEMBER CHANNEL",
    "VIP付费通道",
    "普通用户只能看到开通入口；只有购买VIP后，才会显示VIP专属产品、深度参数服务和高端定制页面。"
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
            "用户分层逻辑",
            "平台将用户分为普通用户和VIP用户。普通用户购买标准文创产品，VIP用户购买高端定制、公共艺术方案和深度工艺服务，从而形成分层收费模式。"
        )

else:
    safe_markdown(
        f"""
<div class="vip-panel">
    <h3>VIP专区已解锁</h3>
    <p><b>当前会员状态：</b>{st.session_state.vip_level}</p>
    <p>你已开通VIP，现在可以查看并购买VIP专属高端产品、深度参数服务和定制服务。</p>
</div>
"""
    )

    if st.button("退出VIP演示状态", use_container_width=True):
        st.session_state.vip_unlocked = False
        st.session_state.vip_level = "未开通"
        st.rerun()


# =========================================================
# VIP高端产品区
# =========================================================

if st.session_state.vip_unlocked:
    section_title(
        "VIP PREMIUM PRODUCTS",
        "VIP高端产品与技术服务",
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
            "desc": "适合校园、社区、商业空间展示，包含设计方案、材料方案和小样制作。"
        },
        {
            "name": "企业ESG绿色艺术礼盒",
            "price": 3980,
            "img": "3",
            "desc": "面向企业ESG活动、绿色展厅和客户礼品，突出绿色低碳与艺术价值。"
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
        "TECH SERVICE APPLICATION",
        "技术服务申请",
        "VIP用户可以提交工艺数据包、企业诊断、样品打样、公共艺术和企业绿色展陈需求。"
    )

    service_col1, service_col2 = st.columns([1, 1])

    with service_col1:
        service_type = st.selectbox(
            "选择服务类型",
            [
                "低温热熔工艺数据包",
                "企业废料工艺诊断",
                "样品打样与小试服务",
                "公共艺术装置设计",
                "企业ESG绿色展厅方案",
                "校园环保艺术课程"
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
            "填写服务需求",
            placeholder="例如：企业有一批蓝绿色建筑玻璃边角料，希望开发一套用于展厅墙面的再生玻璃艺术板材。"
        )

        if st.button("提交技术服务需求", use_container_width=True):
            st.session_state.service_orders.append(
                {
                    "服务类型": service_type,
                    "预算区间": budget,
                    "需求描述": demand,
                    "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            st.success("技术服务需求已提交。展示版不会真实发送数据，正式上线可对接后台订单系统。")

    with service_col2:
        info_panel(
            "服务价值",
            "技术服务从单一商品销售升级为企业级解决方案，能够承接工艺改造、样品打样、数据包输出和空间项目交付。"
        )

        info_panel(
            "高价值来源",
            "重点强调高客单价、项目制收入、设计服务费、工艺咨询费和数据服务费，增强项目营收空间。"
        )

        if st.session_state.service_orders:
            st.markdown("### 已提交服务记录")
            st.dataframe(pd.DataFrame(st.session_state.service_orders), use_container_width=True, height=220)


# =========================================================
# 购物车
# =========================================================

section_title(
    "SHOPPING CART",
    "购物车与订单汇总",
    "汇总普通商品和VIP商品，展示平台从浏览、推荐、会员到购买的商业闭环。"
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
    "项目从单一作品展示升级为技术服务平台、会员平台、产品交易平台和数据资产平台。"
)

b1, b2, b3, b4 = st.columns(4)

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
        "常规数据开放用于展示，深度参数、工艺方案、批量方案和定制模型作为付费服务，增强技术壁垒。"
    )

with b3:
    glass_card(
        "💳",
        "会员制盈利",
        "通过基础会员、高级会员和机构会员分层收费，叠加商品销售、设计服务、公共艺术项目和企业ESG定制。"
    )

with b4:
    glass_card(
        "📦",
        "定制交付收入",
        "围绕企业展厅、文旅空间、公共艺术、校园课程和高端礼品进行项目制交付，提升客单价。"
    )


# =========================================================
# 财务模型
# =========================================================

safe_markdown('<div id="finance"></div>')

section_title(
    "FINANCIAL MODEL",
    "财务模型展示",
    "以文创产品销售、企业定制订单、设计版权授权、平台会员和技术服务为核心收入来源，展示项目的轻资产增长路径。"
)

finance_data = pd.DataFrame(
    [
        {"收入板块": "再生玻璃文创产品销售", "2026预计收入万元": 10, "收入占比%": 65},
        {"收入板块": "企业定制订单", "2026预计收入万元": 3, "收入占比%": 20},
        {"收入板块": "设计版权授权", "2026预计收入万元": 2, "收入占比%": 15},
    ]
)

st.dataframe(finance_data, use_container_width=True, height=180)

f1, f2, f3, f4 = st.columns(4)

with f1:
    metric_box("15万", "2026年预计营收", "三大收入板块联动")

with f2:
    metric_box("120%", "年度增长展示目标", "校企协同驱动现金流闭环")

with f3:
    metric_box("25万+", "2028年营收展示目标", "区域拓展与品牌溢价驱动")

with f4:
    metric_box("30%+", "中长期净利润率目标", "模块化生产后成本继续下降")

st.bar_chart(finance_data.set_index("收入板块")[["2026预计收入万元"]])



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
    <h2>青承焕艺</h2>
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
    <p>低温热熔工艺</p>
    <p>艺术材料产品</p>
</div>
"""
    )

with cc2:
    safe_markdown(
        """
<div class="contact-item-card">
    <h3>平台方向</h3>
    <p>AI工艺数据库</p>
    <p>产品匹配系统</p>
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