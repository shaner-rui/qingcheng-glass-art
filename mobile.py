from pathlib import Path
import base64
from io import BytesIO

import pandas as pd
import streamlit as st
from PIL import Image


# =========================================================
# 手机端基础配置
# =========================================================

st.set_page_config(
    page_title="青橙焕艺 | 手机展示版",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# 路径配置
# =========================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent if APP_DIR.name.lower() == "src" else APP_DIR

IMAGE_DIR = PROJECT_DIR / "images"

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

    for suffix in [".png", ".jpg", ".jpeg", ".webp"]:
        candidate = IMAGE_DIR / f"{name}{suffix}"
        if candidate.exists():
            return candidate

    return raw


@st.cache_data(ttl=300)
def load_data(path: str):
    csv_path = Path(path)

    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df


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
def get_image_path_or_none(path_str: str, max_width: int = 1000, quality: int = 78) -> str:
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
    st.markdown(code.strip(), unsafe_allow_html=True)


def section(title: str, subtitle: str = ""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    html(
        f"""
<div class="section-title">
    <h2>{title}</h2>
    {sub}
</div>
"""
    )


def card(title: str, text: str, icon: str = ""):
    html(
        f"""
<div class="mobile-card">
    <h3>{icon} {title}</h3>
    <p>{text}</p>
</div>
"""
    )


def metric_card(value: str, label: str):
    html(
        f"""
<div class="metric-card">
    <h3>{value}</h3>
    <p>{label}</p>
</div>
"""
    )


def show_img(name: str, title: str, desc: str = "", maker: str = ""):
    path = resolve_image(name)

    if path.exists():
        optimized_path = get_image_path_or_none(str(path), max_width=1000, quality=78)
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
        risk = "当前温度偏高，容易导致玻璃过度熔融，颗粒感和体积感下降，建议明显降温。"
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
# CSS
# =========================================================

html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap');

html, body, .stApp {
    font-family: 'Noto Sans SC', sans-serif;
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
}

.hero {
    padding: 2.2rem 1.25rem;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.11)),
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
    color: rgba(246,251,255,0.80);
    line-height: 1.75;
    font-size: 0.98rem;
}

.quick-nav {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.55rem;
}

.quick-nav a {
    text-align: center;
    padding: 0.7rem 0.4rem;
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

.section-title h2 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #25f4ee, #ffffff, #ff9f43);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-title p {
    color: rgba(246,251,255,0.68);
    line-height: 1.7;
    margin-top: 0.5rem;
    font-size: 0.94rem;
}

.mobile-card,
.metric-card,
.img-caption,
.recommend-result,
.contact-box {
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

.mobile-card p {
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

.recommend-result {
    padding: 1.1rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(37,244,238,0.12), rgba(255,159,67,0.10));
    margin-top: 1rem;
}

.recommend-result h3 {
    color: #25f4ee;
    margin-top: 0;
}

.recommend-result p {
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
.stRadio label {
    color: rgba(246,251,255,0.84) !important;
    font-weight: 800 !important;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
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
    <div class="hero-tag">MOBILE VERSION · QINGXI CREATION</div>
    <h1>青橙焕艺</h1>
    <p>
        青汐造物依托青汐工坊开展废旧玻璃热熔再生、艺术设计与工艺数据分析。
        本页面为手机扫码展示版，保留滚动展示、行业产品图、AI 推荐与轻量交互折线图。
    </p>
    <div class="quick-nav">
        <a href="#intro">项目简介</a>
        <a href="#gallery">烧制对比</a>
        <a href="#industry">行业产品</a>
        <a href="#recommend">产品推荐</a>
        <a href="#database">数据摘要</a>
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
    "项目简介",
    "从废旧玻璃回收、热熔实验、烧制记录到艺术产品转化，形成绿色材料再生与数字化展示平台。"
)

card(
    "废旧玻璃再生",
    "以废弃玻璃、边角料玻璃、透明和彩色玻璃为基础材料，通过清洗、筛选、组合和热熔烧制，重新赋予废弃材料展示价值与产品价值。",
    "♻️"
)

card(
    "青汐工坊实验",
    "围绕800℃、780℃、760℃等烧制条件记录颗粒感、体积感、透光度和综合质量分，为后续工艺优化提供数据依据。",
    "🔥"
)

card(
    "艺术产品转化",
    "将热熔玻璃实验样品进一步转化为花瓶、灯具、装饰画、艺术摆件和校园文创产品，提升项目审美表达和商业落地能力。",
    "🎨"
)

card(
    "AI工艺推荐",
    "根据用户选择的产品类型、材料和目标效果，输出推荐温度区间、风险提示和产品设计建议。",
    "🤖"
)


# =========================================================
# 烧制前后展示
# =========================================================

html('<div id="gallery"></div>')

section(
    "烧制前后对比",
    "保留滚动动画，同时使用压缩图加载，提升手机端稳定性。"
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

temp_choice = st.radio(
    "选择展示温度",
    ["760℃", "780℃", "800℃"],
    horizontal=True
)

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
# 玻璃行业产品展示
# =========================================================

html('<div id="industry"></div>')

section(
    "玻璃行业产品展示",
    "保留1/2/3/4/5五张行业参考图，但转为压缩图加载，适配手机端。"
)

industry_items = [
    ("1", "家居器皿方向", "展示玻璃材料在家居器皿、桌面陈设和生活收纳中的行业应用可能。"),
    ("2", "透光灯具方向", "展示玻璃材料在灯具、氛围照明和空间装饰中的行业化应用。"),
    ("3", "花器摆件方向", "展示玻璃材料在花瓶、花器、家居软装和陈列摆件中的产品形态。"),
    ("4", "文创饰品方向", "展示玻璃色彩、珠状元素和轻量化饰品在文创产品中的延展空间。"),
    ("5", "生活器物方向", "展示玻璃材料在烛台、香薰容器、桌面器物等生活场景中的商业化方向。"),
]

for image_name, title, desc in industry_items:
    show_img(image_name, title, desc)


# =========================================================
# 项目优势
# =========================================================

html('<div id="advantage"></div>')

section(
    "项目优势",
    "从环保、工艺、展示和产品转化四个维度体现青汐造物的项目价值。"
)

card("绿色低碳", "减少废旧玻璃浪费，体现循环经济、环保教育和可持续设计理念。", "🌱")
card("工坊实验可复现", "记录温度、实验轮次和效果评分，便于后续复盘、优化和扩展。", "🧪")
card("对比展示直观", "烧制前后照片能够直观展示温度变化对玻璃形态、颗粒感和体积感的影响。", "📷")
card("产品可转化", "结合玻璃行业产品形态，可延伸为灯具、花瓶、装饰画、摆件和校园文创。", "🛍️")


# =========================================================
# 产品推荐系统
# =========================================================

html('<div id="recommend"></div>')

section(
    "产品推荐",
    "用户选择产品类型、材料和目标效果后，系统输出推荐工艺方案。"
)

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

html(
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
"""
)

st.progress(score / 100)


# =========================================================
# 数据摘要 + 轻量交互折线图
# =========================================================

html('<div id="database"></div>')

section(
    "工艺数据摘要",
    "保留数据库摘要与交互折线图，但折线图仅单指标显示，减少手机端渲染压力。"
)

if df.empty:
    st.warning(f"没有找到 glass_experiment_numeric_only.csv。当前尝试路径：{DATA_PATH}")
else:
    show_df = df.copy()

    if "temperature_c" in show_df.columns:
        temps = sorted(show_df["temperature_c"].dropna().unique())
        selected_temp = st.multiselect("选择温度", temps, default=temps)

        if selected_temp:
            show_df = show_df[show_df["temperature_c"].isin(selected_temp)]

    c1, c2 = st.columns(2)

    with c1:
        metric_card(str(len(show_df)), "实验记录")

    with c2:
        if "temperature_c" in show_df.columns and len(show_df):
            metric_card(f"{round(show_df['temperature_c'].mean(), 1)}℃", "平均温度")
        else:
            metric_card("暂无", "平均温度")

    c3, c4 = st.columns(2)

    with c3:
        if "overall_quality_score_100" in show_df.columns and len(show_df):
            metric_card(str(round(show_df["overall_quality_score_100"].mean(), 1)), "平均质量分")
        else:
            metric_card("暂无", "平均质量分")

    with c4:
        best_temp = "暂无"
        if (
            "temperature_c" in show_df.columns
            and "overall_quality_score_100" in show_df.columns
            and len(show_df)
        ):
            best_temp = f"{int(show_df.groupby('temperature_c')['overall_quality_score_100'].mean().idxmax())}℃"
        metric_card(best_temp, "较优温度")

    display_cols = [
        col for col in [
            "record_id",
            "temperature_c",
            "experiment_round",
            "particle_score",
            "volume_score",
            "transparency_score",
            "success_score",
            "overall_quality_score_100"
        ] if col in show_df.columns
    ]

    st.markdown("### 实验数据预览")
    st.dataframe(show_df[display_cols].head(30), use_container_width=True, height=280)

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
        st.markdown("### 按温度均值统计")
        mean_df = show_df.groupby("temperature_c")[numeric_cols].mean().round(2).reset_index()
        st.dataframe(mean_df, use_container_width=True, height=180)

        metric_map = {
            "综合质量分": "overall_quality_score_100",
            "成功度": "success_score",
            "颗粒感": "particle_score",
            "体积感": "volume_score",
            "透光度": "transparency_score",
            "过熔程度": "overheat_score",
        }

        valid_metric_map = {
            k: v for k, v in metric_map.items()
            if v in mean_df.columns
        }

        if valid_metric_map:
            selected_metric_label = st.selectbox(
                "选择折线图指标",
                list(valid_metric_map.keys())
            )

            selected_col = valid_metric_map[selected_metric_label]

            chart_df = mean_df[["temperature_c", selected_col]].copy()
            chart_df = chart_df.rename(
                columns={
                    "temperature_c": "温度",
                    selected_col: selected_metric_label
                }
            )

            st.markdown("### 轻量交互折线图")
            st.line_chart(
                chart_df.set_index("温度"),
                height=240
            )

        if "overall_quality_score_100" in mean_df.columns and len(mean_df):
            best_row = mean_df.loc[mean_df["overall_quality_score_100"].idxmax()]
            best_temp = int(best_row["temperature_c"])
            best_score = round(best_row["overall_quality_score_100"], 1)

            card(
                "温度趋势结论",
                f"当前数据中，{best_temp}℃ 的平均综合质量分较高，平均综合质量分为 {best_score}。手机端采用单指标轻量折线图，减少卡顿。",
                "📊"
            )


# =========================================================
# 后期展望
# =========================================================

html('<div id="future"></div>')

section(
    "后期展望",
    "围绕数据规模、AI模型、产品体系和商业落地继续升级再生玻璃艺术平台。"
)

card(
    "建立完整工艺数据库",
    "后续将补充保温时间、升温曲线、玻璃厚度、颗粒大小、颜色组合和摆放方式等参数，让数据库从展示型数据升级为可建模数据。",
    "01"
)

card(
    "升级机器学习推荐",
    "当前系统基于实验规律和规则推荐，后续可使用回归模型或分类模型预测综合质量分，并自动生成最佳烧制方案。",
    "02"
)

card(
    "扩展再生玻璃产品",
    "后续可进一步拓展校园纪念品、公共艺术装置、家居软装和文旅文创产品。",
    "03"
)

card(
    "打造体验与商业闭环",
    "结合校园废玻璃回收、青汐工坊手作体验课程、线上展示平台和文创销售，形成环保教育、艺术体验和创业转化闭环。",
    "04"
)


# =========================================================
# 联系我们
# =========================================================

html('<div id="contact"></div>')

section(
    "联系我们",
    "让废旧玻璃重新发光，让绿色材料进入艺术生活。"
)

html(
    """
<div class="contact-box">
    <h2>青汐造物</h2>
    <p>青汐工坊 · Glass Recycling AI Platform</p>
    <p>废旧玻璃热熔再生 · 艺术产品设计 · AI推荐系统展示</p>
</div>
"""
)