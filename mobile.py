from pathlib import Path
from datetime import datetime
from io import BytesIO
import base64

import pandas as pd
import streamlit as st
from PIL import Image


# =========================================================
# 手机端基础配置：尽量与网页版功能一致
# =========================================================

st.set_page_config(
    page_title="青橙焕艺 | 移动端数字化服务平台",
    page_icon="♻️",
    layout="centered",
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
# 状态管理：与网页版一致
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

    # 找不到 CSV 时提供演示数据，保证页面可运行
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


@st.cache_data(ttl=3600)
def image_to_data_uri(path_str: str, max_width: int = 900, quality: int = 72) -> str:
    path = Path(path_str)

    if not path.exists():
        return ""

    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size

        if w > max_width:
            new_h = int(h * max_width / w)
            img = img.resize((max_width, new_h))

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{data}"
    except Exception:
        return ""


@st.cache_data(ttl=3600)
def get_optimized_image(path_str: str, max_width: int = 1000, quality: int = 78) -> str:
    path = Path(path_str)

    if not path.exists():
        return ""

    try:
        temp_dir = PROJECT_DIR / ".mobile_cache"
        temp_dir.mkdir(exist_ok=True)

        out_path = temp_dir / f"{path.stem}_mobile.jpg"

        if out_path.exists():
            return str(out_path)

        img = Image.open(path).convert("RGB")
        w, h = img.size

        if w > max_width:
            new_h = int(h * max_width / w)
            img = img.resize((max_width, new_h))

        img.save(out_path, format="JPEG", quality=quality, optimize=True)
        return str(out_path)
    except Exception:
        return str(path)


def html(code: str):
    st.markdown(str(code).strip(), unsafe_allow_html=True)


def section(tag: str, title: str, subtitle: str = ""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    html(
        f"""
<div class="section-title">
    <div class="section-tag">{tag}</div>
    <h2>{title}</h2>
    {sub}
</div>
"""
    )


def card(title: str, text: str, icon: str = ""):
    icon_html = f"<span>{icon}</span>" if icon else ""
    html(
        f"""
<div class="mobile-card">
    <h3>{icon_html}{title}</h3>
    <p>{text}</p>
</div>
"""
    )


def metric_card(value: str, label: str, sub: str = ""):
    sub_html = f"<small>{sub}</small>" if sub else ""
    html(
        f"""
<div class="metric-card">
    <h3>{value}</h3>
    <p>{label}</p>
    {sub_html}
</div>
"""
    )


def chain_card(num: str, title: str, text: str):
    html(
        f"""
<div class="chain-card">
    <div class="chain-num">{num}</div>
    <h3>{title}</h3>
    <p>{text}</p>
</div>
"""
    )


def show_img(name: str, title: str, desc: str = "", maker: str = ""):
    path = resolve_image(name)

    if path.exists():
        optimized_path = get_optimized_image(str(path), max_width=1000, quality=78)
        st.image(optimized_path, use_container_width=True)
    else:
        st.warning(f"缺少图片：{path.name}")

    maker_line = f"<p class='maker'>制作人员：{maker}</p>" if maker else ""

    html(
        f"""
<div class="img-caption">
    <h3>{title}</h3>
    <p>{desc}</p>
    {maker_line}
</div>
"""
    )


def scroll_gallery(items):
    slides = ""

    for item in items:
        path = resolve_image(item["name"])
        uri = image_to_data_uri(str(path), max_width=700, quality=68)

        if not uri:
            continue

        slides += f"""
<div class="slide">
    <img src="{uri}" alt="{item['title']}">
    <div class="slide-mask">
        <strong>{item['title']}</strong>
        <span>{item['desc']}</span>
        <em>{item['maker']}</em>
    </div>
</div>
"""

    if not slides:
        st.info("请确认 images 文件夹中存在对应图片。")
        return

    html(
        f"""
<div class="scroll-box">
    <div class="scroll-track">
        {slides}
        {slides}
    </div>
</div>
"""
    )


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


def recommend(product_type: str, material: str, target_effect: str, temp: int, thickness: str, particle: str):
    if product_type == "再生玻璃艺术板材":
        base_temp = "720℃ - 760℃"
        product_tip = "艺术板材需要稳定平整度与肌理层次，可先完成小样测试，再放大生产。"
    elif product_type == "花瓶":
        base_temp = "760℃ - 770℃"
        product_tip = "花瓶需要保留局部体积感，玻璃应融合但不要完全摊平。"
    elif product_type == "灯具":
        base_temp = "735℃ - 765℃"
        product_tip = "灯具更重视透光度，适合透明玻璃或浅色玻璃组合，避免颜色堆叠过厚。"
    elif product_type == "装饰画":
        base_temp = "720℃ - 760℃"
        product_tip = "装饰画适合保留颗粒边界和色彩层次，温度不宜过高。"
    elif product_type == "公共艺术装置":
        base_temp = "740℃ - 775℃"
        product_tip = "公共艺术装置需要兼顾强度、造型和视觉冲击力，可先小样验证再放大制作。"
    elif product_type == "艺术摆件":
        base_temp = "745℃ - 775℃"
        product_tip = "艺术摆件可适当增强体积感，但要避免温度过高造成形态塌陷。"
    else:
        base_temp = "730℃ - 765℃"
        product_tip = "综合文创产品适合小样测试后再根据成品效果扩大尺寸。"

    if temp >= 795:
        risk = "当前温度偏高，容易导致玻璃过度熔融，颗粒感和体积感下降，需要明显降温。"
        score = 45
        risk_level = "高风险"
    elif 775 <= temp < 795:
        risk = "当前温度仍偏高，颗粒边界可能变弱，可向760℃附近调整。"
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
        effect_tip = "平衡颗粒感、透光度和体积感，更适合商业样品展示。"

    if material == "透明玻璃":
        material_tip = "透明玻璃适合灯具、窗饰和透光艺术板。"
    elif material == "彩色玻璃":
        material_tip = "彩色玻璃视觉表现强，适合装饰画和艺术摆件。"
    elif material == "混合玻璃":
        material_tip = "混合玻璃层次丰富，但需要注意颜色过杂。"
    elif material == "建筑平板玻璃":
        material_tip = "建筑平板玻璃适合再生板材和空间材料，但要重视边角预处理。"
    else:
        material_tip = "可先做小样实验，记录温度和最终效果。"

    if thickness == "薄层 3-5mm":
        thickness_tip = "薄层适合装饰画、饰品和灯罩类产品，升温和降温应更平缓。"
    elif thickness == "中层 6-10mm":
        thickness_tip = "中层适合板材、摆件和桌面产品，兼顾结构稳定与肌理表现。"
    else:
        thickness_tip = "厚层适合公共艺术装置，但宜分层烧制，降低开裂风险。"

    if particle == "细颗粒":
        particle_tip = "细颗粒更容易融合，适合追求细腻质感。"
    elif particle == "中颗粒":
        particle_tip = "中颗粒综合表现较稳定，适合多数产品。"
    else:
        particle_tip = "粗颗粒视觉冲击力强，但需要更谨慎控制温度与保温时间。"

    hold_time = "28-35分钟" if score >= 80 else "20-28分钟" if temp < 720 else "调整温度后再设定"
    energy_compare = "相较传统高温工艺，低温热熔路径可降低能耗与试错损耗。"

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
# CSS：移动端与网页版统一深色科技风
# =========================================================

html(
    """
<style>
html, body, .stApp {
    font-family: "Microsoft YaHei", "Noto Sans SC", Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(37,244,238,0.22), transparent 26%),
        radial-gradient(circle at 90% 15%, rgba(255,159,67,0.20), transparent 26%),
        linear-gradient(135deg, #020711 0%, #071827 55%, #14101f 100%);
    color: #f6fbff;
}

.block-container {
    padding-top: 0.8rem;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: 4rem;
    max-width: 760px;
}

.hero {
    padding: 2.35rem 1.25rem;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.13), rgba(255,159,67,0.12)),
        rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow: 0 18px 46px rgba(0,0,0,0.30);
}

.hero-tag {
    display: inline-block;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    color: #25f4ee;
    background: rgba(37,244,238,0.10);
    border: 1px solid rgba(37,244,238,0.28);
    font-size: 0.72rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

.hero h1 {
    margin: 0;
    font-size: 3rem;
    line-height: 1.05;
    font-weight: 900;
    background: linear-gradient(90deg, #25f4ee, #ffffff 48%, #ff9f43);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    margin-top: 1rem;
    color: rgba(246,251,255,0.82);
    line-height: 1.75;
    font-size: 0.98rem;
}

.hero-kpis {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.65rem;
}

.hero-kpi {
    padding: 0.85rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
}

.hero-kpi strong {
    display: block;
    color: #25f4ee;
    font-size: 1.1rem;
    font-weight: 900;
}

.hero-kpi span {
    display: block;
    color: rgba(246,251,255,0.70);
    margin-top: 0.25rem;
    line-height: 1.45;
    font-size: 0.78rem;
}

.quick-nav {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.55rem;
}

.quick-nav a {
    text-align: center;
    padding: 0.72rem 0.4rem;
    border-radius: 16px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 800;
    font-size: 0.86rem;
}

.section-title {
    margin: 3rem auto 1.2rem;
    text-align: center;
}

.section-tag {
    color: #25f4ee;
    font-weight: 900;
    letter-spacing: 0.14em;
    font-size: 0.72rem;
    margin-bottom: 0.3rem;
}

.section-title h2 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #25f4ee, #ffffff, #ff9f43);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-title p {
    color: rgba(246,251,255,0.70);
    line-height: 1.7;
    margin-top: 0.5rem;
    font-size: 0.94rem;
}

.mobile-card,
.metric-card,
.img-caption,
.recommend-result,
.contact-box,
.chain-card,
.order-result,
.vip-panel,
.lock-panel,
.design-panel {
    background: rgba(255,255,255,0.075);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 14px 36px rgba(0,0,0,0.22);
}

.mobile-card {
    padding: 1.1rem;
    border-radius: 22px;
    margin-bottom: 0.85rem;
}

.mobile-card h3 {
    color: #ffffff;
    margin: 0 0 0.5rem;
    font-size: 1.08rem;
    font-weight: 900;
}

.mobile-card h3 span {
    margin-right: 0.35rem;
}

.mobile-card p {
    color: rgba(246,251,255,0.76);
    line-height: 1.7;
    margin: 0;
    font-size: 0.94rem;
}

.chain-card {
    padding: 1.1rem;
    border-radius: 22px;
    margin-bottom: 0.85rem;
    position: relative;
    overflow: hidden;
}

.chain-num {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    background: linear-gradient(135deg, #25f4ee, #ff9f43);
    color: #04111f;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    margin-bottom: 0.85rem;
}

.chain-card h3 {
    color: #ffffff;
    margin: 0 0 0.45rem;
    font-size: 1.08rem;
    font-weight: 900;
}

.chain-card p {
    color: rgba(246,251,255,0.74);
    line-height: 1.7;
    margin: 0;
    font-size: 0.94rem;
}

.metric-card {
    padding: 0.95rem;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 0.75rem;
    min-height: 110px;
}

.metric-card h3 {
    color: #25f4ee;
    margin: 0;
    font-size: 1.55rem;
    font-weight: 900;
}

.metric-card p {
    color: rgba(246,251,255,0.70);
    margin: 0.25rem 0 0;
    font-size: 0.85rem;
}

.metric-card small {
    color: #ffcf9a;
    display: block;
    margin-top: 0.3rem;
    line-height: 1.4;
    font-size: 0.72rem;
}

[data-testid="stImage"] img {
    border-radius: 22px;
    box-shadow: 0 16px 42px rgba(0,0,0,0.30);
}

.img-caption {
    margin-top: 0.65rem;
    margin-bottom: 1.35rem;
    padding: 0.95rem 1rem;
    border-radius: 18px;
}

.img-caption h3 {
    color: #ffffff;
    margin: 0 0 0.4rem;
    font-size: 1.05rem;
    font-weight: 900;
}

.img-caption p {
    margin: 0;
    color: rgba(246,251,255,0.74);
    line-height: 1.65;
    font-size: 0.9rem;
}

.img-caption .maker {
    color: #ffcf9a;
    font-weight: 900;
    margin-top: 0.5rem;
}

.scroll-box {
    width: 100%;
    overflow: hidden;
    border-radius: 24px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 16px 42px rgba(0,0,0,0.28);
    margin-bottom: 1.3rem;
}

.scroll-track {
    display: flex;
    gap: 14px;
    width: max-content;
    padding: 14px;
    animation: scrollX 28s linear infinite;
}

.slide {
    position: relative;
    width: 260px;
    height: 180px;
    flex: 0 0 auto;
    border-radius: 18px;
    overflow: hidden;
    background: rgba(255,255,255,0.08);
}

.slide img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.slide-mask {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    padding: 0.8rem;
    background: linear-gradient(to top, rgba(0,0,0,0.84), rgba(0,0,0,0.2), transparent);
}

.slide-mask strong {
    display: block;
    color: #fff;
    font-size: 0.95rem;
    font-weight: 900;
}

.slide-mask span {
    display: block;
    color: rgba(255,255,255,0.78);
    font-size: 0.78rem;
    margin-top: 0.15rem;
}

.slide-mask em {
    display: block;
    color: #ffcf9a;
    font-style: normal;
    font-size: 0.72rem;
    margin-top: 0.2rem;
    font-weight: 700;
}

@keyframes scrollX {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

.recommend-result,
.order-result,
.vip-panel,
.lock-panel,
.design-panel {
    padding: 1.1rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.10));
    margin-top: 1rem;
    margin-bottom: 1rem;
}

.recommend-result h3,
.order-result h3,
.vip-panel h3,
.lock-panel h3,
.design-panel h3 {
    color: #25f4ee;
    margin-top: 0;
    font-weight: 900;
}

.recommend-result p,
.order-result p,
.vip-panel p,
.lock-panel p,
.design-panel p {
    color: rgba(246,251,255,0.78);
    line-height: 1.65;
    margin: 0.4rem 0;
}

.contact-box {
    padding: 1.6rem 1rem;
    border-radius: 26px;
    text-align: center;
}

.contact-box h2 {
    margin: 0;
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #25f4ee, #ffffff, #ff9f43);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.contact-box p {
    color: rgba(246,251,255,0.72);
    line-height: 1.7;
}

.stSlider label,
.stSelectbox label,
.stMultiSelect label,
.stRadio label,
.stNumberInput label,
.stTextInput label,
.stTextArea label {
    color: rgba(246,251,255,0.84) !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

hr {
    border-color: rgba(255,255,255,0.12);
}
</style>
"""
)


# =========================================================
# Hero
# =========================================================

html(
    """
<div class="hero">
    <div class="hero-tag">MOBILE VERSION · B2B2C PLATFORM · GREEN MATERIAL</div>
    <h1>青橙焕艺</h1>
    <p>
        面向玻璃产业绿色转型的再生玻璃低温热熔技术服务平台。系统围绕工业玻璃废料回收、
        低温热熔工艺、AI智能设计、再生玻璃艺术板材、文创销售与技术服务，构建从“废料处理”
        到“材料增值”的移动端展示入口。
    </p>
    <div class="hero-kpis">
        <div class="hero-kpi"><strong>1400℃→700℃</strong><span>低温热熔路径</span></div>
        <div class="hero-kpi"><strong>50+款</strong><span>产品开发基础</span></div>
        <div class="hero-kpi"><strong>80%-90%</strong><span>成本压缩模型</span></div>
        <div class="hero-kpi"><strong>B2B2C</strong><span>平台化闭环</span></div>
    </div>
    <div class="quick-nav">
        <a href="#intro">项目简介</a>
        <a href="#chain">链路闭环</a>
        <a href="#factory">原料工厂</a>
        <a href="#database">工艺数据</a>
        <a href="#gallery">烧制对比</a>
        <a href="#recommend">AI推荐</a>
        <a href="#shop">产品商城</a>
        <a href="#vip">VIP服务</a>
        <a href="#finance">财务模型</a>
        <a href="#contact">联系我们</a>
    </div>
</div>
"""
)


# =========================================================
# 项目简介
# =========================================================

html('<div id="intro"></div>')

section(
    "PROJECT INTRODUCTION",
    "项目简介",
    "以低温热熔再生玻璃技术为核心，以再生玻璃材料产品与技术服务平台为主营方向，连接废料回收、工艺研发、智能设计、板材生产、场景应用和数据服务。"
)

card("工业废料高值转化", "将玻璃厂废料、建筑玻璃边角料和校园回收玻璃重新导入艺术生产流程，实现从低值废料到高附加值材料产品的转化。", "♻️")
card("低温热熔工艺体系", "围绕700℃—800℃低温热熔区间进行参数控制，减少传统高温烧制带来的高能耗、高成本和高碳排放压力。", "🔥")
card("AI智能设计模块", "围绕废料颜色、颗粒尺度、熔融温度、肌理效果和应用场景建立参数模型，辅助生成设计方案和工艺方案。", "🤖")
card("再生玻璃艺术板材", "主线产品面向家居建材、商业空间、企业展厅、文旅文创和公共艺术装置，强化产品可销售与可交付能力。", "🏛️")
card("技术服务平台", "向玻璃企业、设计机构、园区和环保运营方提供工艺包、配方数据库、样品打样、供应链撮合和专家诊断服务。", "🔗")
card("复合收入结构", "形成产品销售、技术服务、平台会员和定制交付协同增长的收入结构，增强项目持续经营能力。", "💼")


# =========================================================
# 行业痛点与解决路径
# =========================================================

html('<div id="pain"></div>')

section(
    "INDUSTRY PAIN POINTS",
    "行业痛点与解决路径",
    "围绕高成本、高能耗、同质化、传播局限、上下游信息割裂和工艺试错风险，展示平台切入点。"
)

card("高成本与高环境负荷", "废旧玻璃回收分拣、清洗、运输成本高，传统高温热熔依赖高能耗生产路径，压缩企业利润空间。", "⚠️")
card("产品同质化与美学缺失", "普通再生玻璃产品容易停留在低价、低识别度和基础器物层面，难以形成设计溢价和品牌价值。", "🎨")
card("上下游信息割裂", "回收端、生产端、设计端和市场端缺少统一数据平台，工艺参数无法共享，生产试错依赖经验判断。", "🧩")
card("平台化破局", "青橙焕艺以工艺数据库、AI推荐、产品展示、原料对接和会员服务串联全链路，降低协作与试错成本。", "✅")


# =========================================================
# B2B2C数字化循环链路
# =========================================================

html('<div id="chain"></div>')

section(
    "B2B2C DIGITAL LOOP",
    "B2B2C数字化循环链路",
    "平台将B端玻璃厂废料、再生加工、设计服务与C端产品购买连成一体，形成可展示、可交易、可复用的数据闭环。"
)

chain_card("01", "上游废料进入", "玻璃工厂、回收站、校园回收点发布废料类型、重量、颜色、杂质等级和库存数据。")
chain_card("02", "平台估价分级", "根据玻璃类型、纯度、用途和采购重量估算原料成本、清洗成本和物流成本。")
chain_card("03", "AI工艺匹配", "输入材料、厚度、颗粒尺度和目标效果，匹配温度区间、保温时间与风险等级。")
chain_card("04", "工坊生产交付", "完成小样验证、板材热熔、产品打样、定制生产与质量记录。")
chain_card("05", "销售与数据回流", "普通商品、VIP高端商品和技术服务订单形成销售闭环，效果数据继续回流工艺库。")


# =========================================================
# 上游原料工厂对接
# =========================================================

html('<div id="factory"></div>')

section(
    "UPSTREAM FACTORY CONNECTION",
    "上游原料工厂对接",
    "模拟原料供需对接，完成废旧玻璃原料采购、质量筛选、用途匹配和成本估算。"
)

supplier = st.selectbox(
    "选择原料来源",
    ["城市玻璃回收站", "建筑玻璃边角料工厂", "酒瓶与饮料瓶回收企业", "彩色玻璃加工厂", "校园废玻璃回收点"]
)

glass_type = st.selectbox(
    "选择玻璃类型",
    ["透明玻璃", "彩色玻璃", "混合玻璃", "建筑平板玻璃", "瓶罐玻璃", "实验小样材料包"]
)

purity = st.selectbox(
    "原料等级",
    ["A级：杂质少，适合高端艺术产品", "B级：杂质可控，适合普通文创产品", "C级：需要二次筛选，适合实验与教学"]
)

use_scene = st.selectbox(
    "采购用途",
    ["热熔实验", "再生玻璃板材", "文创产品量产", "灯具与透光产品", "公共艺术装置", "VIP高端定制"]
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

html(
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

if st.session_state.factory_orders:
    st.markdown("### 已提交采购记录")
    st.dataframe(pd.DataFrame(st.session_state.factory_orders), use_container_width=True, height=220)


# =========================================================
# 低温热熔工艺说明
# =========================================================

section(
    "FIRING TEMPERATURE KNOWLEDGE",
    "低温热熔工艺说明",
    "展示烧制经验、低温路径和参数可复现性。"
)

card("700℃低温边界区", "适合初步熔结和小样探索，能保留较明显颗粒结构，但融合度和结构强度需要重点验证。", "700℃")
card("760℃推荐展示温度", "整体表现较稳定，颗粒感、体积感和透光度较均衡，适合花瓶、装饰画、灯具小样和商业样品。", "760℃")
card("780℃偏高风险温度", "玻璃融合程度增强，但部分样品会出现颗粒边界变弱、体积感下降的问题，适合做对照实验。", "780℃")
card("800℃过热警示温度", "容易出现过度熔融，颗粒感和体积感明显减弱，可用于说明温度控制的重要性。", "800℃")


# =========================================================
# 工艺数据库
# =========================================================

html('<div id="database"></div>')

section(
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

    c1, c2 = st.columns(2)

    with c1:
        metric_card(str(len(show_df)), "实验记录")

    with c2:
        avg_temp = round(show_df["temperature_c"].mean(), 1) if "temperature_c" in show_df.columns and len(show_df) else 0
        metric_card(f"{avg_temp}℃", "平均温度")

    c3, c4 = st.columns(2)

    with c3:
        avg_quality = round(show_df["overall_quality_score_100"].mean(), 1) if "overall_quality_score_100" in show_df.columns and len(show_df) else 0
        metric_card(str(avg_quality), "平均质量分")

    with c4:
        best_temp = "暂无"
        if "temperature_c" in show_df.columns and "overall_quality_score_100" in show_df.columns and len(show_df):
            best_temp = f"{int(show_df.groupby('temperature_c')['overall_quality_score_100'].mean().idxmax())}℃"
        metric_card(best_temp, "较优温度")

    st.markdown("### 实验记录表")
    st.dataframe(show_df.head(30), use_container_width=True, height=300)

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

        metric_map = {
            "综合质量分": "overall_quality_score_100",
            "成功度": "success_score",
            "颗粒感": "particle_score",
            "体积感": "volume_score",
            "透光度": "transparency_score",
            "过熔程度": "overheat_score",
        }

        valid_metric_map = {k: v for k, v in metric_map.items() if v in mean_df.columns}

        if valid_metric_map:
            selected_metric_label = st.selectbox("选择折线图指标", list(valid_metric_map.keys()))
            selected_col = valid_metric_map[selected_metric_label]

            chart_df = mean_df[["temperature_c", selected_col]].copy()
            chart_df = chart_df.rename(columns={"temperature_c": "温度", selected_col: selected_metric_label})

            st.markdown("### 轻量交互折线图")
            st.line_chart(chart_df.set_index("温度"), height=240)

        if "overall_quality_score_100" in mean_df.columns and len(mean_df):
            best_row = mean_df.loc[mean_df["overall_quality_score_100"].idxmax()]
            best_temp_value = int(best_row["temperature_c"])
            best_score = round(best_row["overall_quality_score_100"], 1)

            card(
                "温度趋势结论",
                f"当前数据中，{best_temp_value}℃ 的平均综合质量分较高，平均综合质量分为 {best_score}。移动端采用单指标轻量折线图，减少卡顿。",
                "📊"
            )


# =========================================================
# 烧制前后展示
# =========================================================

html('<div id="gallery"></div>')

section(
    "BEFORE & AFTER DISPLAY",
    "烧制前后照片展示",
    "围绕760℃、780℃、800℃三组温度，将烧制前 qian 与烧制后 hou 进行动态展示。"
)

scroll_items = [
    {"name": "760qian", "title": "760℃ · 烧制前", "desc": "760qian", "maker": "李雨豪、芦子晴、刘鑫悦等"},
    {"name": "760hou", "title": "760℃ · 烧制后", "desc": "760hou", "maker": "李雨豪、芦子晴、刘鑫悦等"},
    {"name": "780qian", "title": "780℃ · 烧制前", "desc": "780qian", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"name": "780hou", "title": "780℃ · 烧制后", "desc": "780hou", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"name": "800qian", "title": "800℃ · 烧制前", "desc": "800qian", "maker": "芦子晴、刘鑫悦、刘关伟等"},
    {"name": "800hou", "title": "800℃ · 烧制后", "desc": "800hou", "maker": "芦子晴、刘鑫悦、刘关伟等"},
]

scroll_gallery(scroll_items)

temp_choice = st.radio("选择展示温度", ["760℃", "780℃", "800℃"], horizontal=True)

if temp_choice == "760℃":
    show_img("760qian", "760℃ · 烧制前", "热熔前的玻璃颗粒与材料组合状态。", "李雨豪、芦子晴、刘鑫悦等")
    show_img("760hou", "760℃ · 烧制后", "经过热熔后的成型状态与视觉效果。", "李雨豪、芦子晴、刘鑫悦等")
    card("760℃实验观察", "760℃组整体表现较好，多次出现温度适中、颗粒感明显的结果，后期也出现透光度强、有明显体积感的成品表现。", "✅")

elif temp_choice == "780℃":
    show_img("780qian", "780℃ · 烧制前", "热熔前的玻璃颗粒与材料组合状态。", "芦子晴、刘鑫悦、刘关伟等")
    show_img("780hou", "780℃ · 烧制后", "经过热熔后的成型状态与视觉效果。", "芦子晴、刘鑫悦、刘关伟等")
    card("780℃实验观察", "780℃组仍表现出温度偏高问题，部分样品颗粒感和体积感不足，个别样品透光效果一般。", "⚠️")

else:
    show_img("800qian", "800℃ · 烧制前", "热熔前的玻璃颗粒与材料组合状态。", "芦子晴、刘鑫悦、刘关伟等")
    show_img("800hou", "800℃ · 烧制后", "经过热熔后的成型状态与视觉效果。", "芦子晴、刘鑫悦、刘关伟等")
    card("800℃实验观察", "800℃组温度过高，多次出现颗粒感和体积感不足，说明过度熔融会削弱玻璃颗粒肌理。", "🔥")


# =========================================================
# AI 产品推荐
# =========================================================

html('<div id="recommend"></div>')

section(
    "AI PROCESS RECOMMENDATION",
    "AI工艺与产品推荐",
    "用户选择产品类型、材料、厚度、颗粒尺度和目标效果后，系统输出推荐温度区间、风险提示和产品设计方案。"
)

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

rec = recommend(product_type, material, target_effect, temp, thickness, particle)

html(
    f"""
<div class="recommend-result">
    <h3>AI推荐结果</h3>
    <p><b>用户选择产品：</b>{product_type}</p>
    <p><b>推荐工艺温度区间：</b>{rec["base_temp"]}</p>
    <p><b>推荐保温时间：</b>{rec["hold_time"]}</p>
    <p><b>风险等级：</b>{rec["risk_level"]}</p>
    <p><b>温度风险提示：</b>{rec["risk"]}</p>
    <p><b>产品设计方案：</b>{rec["product_tip"]}</p>
    <p><b>目标效果说明：</b>{rec["effect_tip"]}</p>
    <p><b>材料说明：</b>{rec["material_tip"]}</p>
    <p><b>厚度说明：</b>{rec["thickness_tip"]}</p>
    <p><b>颗粒说明：</b>{rec["particle_tip"]}</p>
    <p><b>低温路径说明：</b>{rec["energy_compare"]}</p>
    <p><b>综合推荐分：</b>{rec["score"]} / 100</p>
</div>
"""
)

st.progress(rec["score"] / 100)

recommend_img = resolve_image("22")
if not recommend_img.exists():
    recommend_img = resolve_image("5")
if recommend_img.exists():
    show_img("22" if resolve_image("22").exists() else "5", "推荐效果参考", "用于辅助展示热熔玻璃的发光、透光和材料转化效果。")


# =========================================================
# AI智能设计模拟
# =========================================================

section(
    "AI DESIGN SIMULATION",
    "AI智能设计模拟",
    "围绕废料颜色、场景需求和产品定位生成设计方向，展示参数输入、效果描述、工艺方案的产品化能力。"
)

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

html(
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

html('<div id="shop"></div>')

section(
    "NORMAL PRODUCT SHOP",
    "普通产品购买区",
    "普通用户只能看到基础文创产品和普通商品，暂时看不到VIP高端商品。"
)

product_list = [
    {"name": "再生玻璃花器", "price": 168, "img": "1", "desc": "适合桌面陈设、花艺搭配和校园文创展示。"},
    {"name": "透光玻璃小夜灯", "price": 238, "img": "2", "desc": "利用透明玻璃和浅色玻璃形成柔和透光效果。"},
    {"name": "再生玻璃板材样品", "price": 298, "img": "3", "desc": "突出颗粒感、色彩层次和绿色再生材料的艺术表达。"},
    {"name": "玻璃文创饰品", "price": 88, "img": "4", "desc": "适合作为校园纪念品、伴手礼和活动周边。"},
    {"name": "再生玻璃杯器", "price": 128, "img": "5", "desc": "适合生活美学场景，强调环保材料和日用价值。"},
]

for idx, product in enumerate(product_list):
    show_img(product["img"], product["name"], product["desc"])
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

html('<div id="vip"></div>')

section(
    "VIP MEMBER CHANNEL",
    "VIP付费通道",
    "普通用户只能看到开通入口；只有购买VIP后，才会显示VIP专属产品、深度参数服务和高端定制页面。"
)

if not st.session_state.vip_unlocked:
    html(
        """
<div class="lock-panel">
    <h3>VIP专区当前未解锁</h3>
    <p>普通用户看不到VIP高端商品和VIP专属服务。请先开通VIP，系统才会显示下方VIP专区。</p>
</div>
"""
    )

    card("基础会员", "适合普通消费者，解锁基础定制咨询、部分工艺说明和普通产品优惠。展示价格：99元/月。", "⭐")
    card("高级会员", "适合高净值客户和设计工作室，解锁高端产品购买、深度定制方案和优先排产。展示价格：299元/月。", "💎")
    card("机构会员", "适合学校、社区、商业空间和文旅项目，解锁公共艺术装置方案、批量设计服务和项目顾问支持。展示价格：999元/月。", "🏛️")

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

    html(
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

else:
    html(
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

if st.session_state.vip_unlocked:
    section(
        "VIP PREMIUM PRODUCTS",
        "VIP高端产品与技术服务",
        "该区域只有购买VIP后才显示。普通用户无法看到这里的产品、价格和服务内容。"
    )

    premium_products = [
        {"name": "高端定制玻璃艺术摆件", "price": 1280, "img": "5", "desc": "面向高净值客户、办公室陈设和礼品场景，提供颜色、造型和主题定制。"},
        {"name": "再生玻璃公共艺术方案", "price": 6800, "img": "22", "desc": "适合校园、社区、商业空间展示，包含设计方案、材料建议和小样制作。"},
        {"name": "企业ESG绿色艺术礼盒", "price": 3980, "img": "3", "desc": "面向企业ESG活动、绿色展厅和客户礼品，突出绿色低碳与艺术价值。"},
    ]

    for idx, product in enumerate(premium_products):
        show_img(product["img"], product["name"], product["desc"])
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

    section(
        "TECH SERVICE APPLICATION",
        "技术服务申请",
        "VIP用户可以提交工艺数据包、企业诊断、样品打样、公共艺术和企业绿色展陈需求。"
    )

    service_type = st.selectbox(
        "选择服务类型",
        ["低温热熔工艺数据包", "企业废料工艺诊断", "样品打样与小试服务", "公共艺术装置设计", "企业ESG绿色展厅方案", "校园环保艺术课程"]
    )

    budget = st.selectbox(
        "预算区间",
        ["1000元 - 3000元", "3000元 - 8000元", "8000元 - 20000元", "20000元以上"]
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

    if st.session_state.service_orders:
        st.markdown("### 已提交服务记录")
        st.dataframe(pd.DataFrame(st.session_state.service_orders), use_container_width=True, height=220)


# =========================================================
# 购物车
# =========================================================

section(
    "SHOPPING CART",
    "购物车与订单汇总",
    "汇总普通商品和VIP商品，展示平台从浏览、推荐、会员到购买的商业闭环。"
)

if st.session_state.cart:
    cart_df = pd.DataFrame(st.session_state.cart)
    total_amount = round(cart_df["小计"].sum(), 2)

    st.dataframe(cart_df, use_container_width=True, height=260)

    c_total1, c_total2 = st.columns(2)

    with c_total1:
        metric_card(f"{len(cart_df)}", "订单条目")

    with c_total2:
        metric_card(f"{cart_df['数量'].sum()}", "商品总数量")

    metric_card(f"{total_amount:.2f}元", "订单总金额")

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

section(
    "PLATFORM BUSINESS MODEL",
    "平台模式与商业闭环",
    "项目从单一作品展示升级为技术服务平台、会员平台、产品交易平台和数据资产平台。"
)

card("技术撮合交易", "平台一端连接原料工厂、回收渠道和设计师，另一端连接消费者、机构客户和空间项目方，形成技术与需求撮合。", "🔗")
card("AI数据库服务", "常规数据开放用于展示，深度参数、工艺方案、批量方案和定制模型作为付费服务，增强技术壁垒。", "🧠")
card("会员制盈利", "通过基础会员、高级会员和机构会员分层收费，叠加商品销售、设计服务、公共艺术项目和企业ESG定制。", "💳")
card("定制交付收入", "围绕企业展厅、文旅空间、公共艺术、校园课程和高端礼品进行项目制交付，提升客单价。", "📦")


# =========================================================
# 财务模型
# =========================================================

html('<div id="finance"></div>')

section(
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

f1, f2 = st.columns(2)

with f1:
    metric_card("15万", "2026年预计营收", "三大收入板块联动")

with f2:
    metric_card("120%", "年度增长展示目标", "校企协同驱动现金流闭环")

f3, f4 = st.columns(2)

with f3:
    metric_card("25万+", "2028年营收展示目标", "区域拓展与品牌溢价驱动")

with f4:
    metric_card("30%+", "中长期净利润率目标", "模块化生产后成本继续下降")

st.bar_chart(finance_data.set_index("收入板块")[["2026预计收入万元"]])


# =========================================================
# 联系我们
# =========================================================

html('<div id="contact"></div>')

section(
    "CONTACT US",
    "联系我们",
    "让废旧玻璃重新发光，让绿色材料进入艺术生活。"
)

html(
    """
<div class="contact-box">
    <h2>青橙焕艺</h2>
    <p>青汐工坊 · Glass Recycling AI Platform · 绿色低碳艺术创业项目</p>
    <p>废旧玻璃再生 · 低温热熔工艺 · 艺术材料产品 · AI工艺数据库</p>
</div>
"""
)
