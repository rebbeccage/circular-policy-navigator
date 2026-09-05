import streamlit as st
import yaml
from graphviz import Digraph


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Circular Policy Navigator",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        min-width: 315px;
        max-width: 315px;
        border-right: 1px solid #DDE3E9;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    h1 {
        font-size: 2.05rem !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.15rem !important;
    }

    h2 {
        margin-top: 1.2rem !important;
    }

    .eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #607080;
        margin-bottom: 0.35rem;
    }

    .policy-subtitle {
        font-size: 1rem;
        color: #5D6975;
        margin-bottom: 1rem;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #DDE3E9;
        border-radius: 10px;
        padding: 18px 20px;
        min-height: 125px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.025);
    }

    .kpi-title {
        font-size: 0.82rem;
        color: #66727E;
        margin-bottom: 9px;
    }

    .kpi-value {
        font-size: 1.9rem;
        line-height: 1.1;
        font-weight: 650;
        color: #17212B;
    }

    .kpi-foot {
        font-size: 0.76rem;
        color: #7B8792;
        margin-top: 10px;
    }

    .conclusion-box {
        background: #EAF1F7;
        border-left: 4px solid #31597C;
        border-radius: 6px;
        padding: 15px 18px;
        margin-top: 14px;
        margin-bottom: 16px;
    }

    .conclusion-title {
        font-size: 0.76rem;
        font-weight: 700;
        color: #31597C;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .conclusion-text {
        font-size: 1rem;
        font-weight: 550;
        color: #1B2936;
    }

    .timeline-card {
        background: #FFFFFF;
        border: 1px solid #DDE3E9;
        border-radius: 8px;
        padding: 13px 16px;
        margin-bottom: 9px;
    }

    .timeline-date {
        font-size: 0.78rem;
        font-weight: 700;
        color: #31597C;
    }

    .timeline-title {
        font-size: 0.96rem;
        font-weight: 650;
        color: #17212B;
        margin-top: 2px;
    }

    .timeline-description {
        font-size: 0.84rem;
        color: #66727E;
        margin-top: 4px;
    }

    .small-note {
        font-size: 0.8rem;
        color: #6D7883;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_policy():
    with open("data/ppwr.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


data = load_policy()

policy = data["policy"]
article = data["article_7"]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def kpi_card(title, value, foot=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def timeline_card(date, title, description, basis):
    st.markdown(
        f"""
        <div class="timeline-card">
            <div class="timeline-date">{date} · {basis}</div>
            <div class="timeline-title">{title}</div>
            <div class="timeline-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="eyebrow">情景分析</div>',
        unsafe_allow_html=True
    )

    st.header("告诉我你的包装情况")

    st.caption(
        "回答两个核心问题，工具将自动判断再生含量目标、"
        "第三国材料要求和需要准备的证据。"
    )

    category_options = {
        v["label"]: k
        for k, v in article["categories"].items()
    }

    selected_category_label = st.selectbox(
    "① 你的包装属于哪一类？",
    list(category_options.keys()),
    help="PPWR Article 7根据包装类型设置不同的2030和2040最低再生含量目标。"
)

    category_key = category_options[selected_category_label]
    category = article["categories"][category_key]


    source_options = {
        v["label"]: k
        for k, v in article["source_routes"].items()
    }

    selected_source_label = st.radio(
    "② 你使用的再生塑料来自哪里？",
    list(source_options.keys()),
    help="欧盟以外收集或再生的材料属于第三国情景，需要进一步判断等效性要求。"
)

    source_key = source_options[selected_source_label]
    source = article["source_routes"][source_key]


    st.divider()


    with st.expander(
        "我的包装是否属于特殊情况？",
        expanded=False
    ):

        st.caption(
             "大多数普通塑料包装无需展开。"
    "药品、医疗器械、可堆肥包装、危险品包装等特殊情形请进一步检查。"
        )

        exemption_options = {
            v["label"]: k
            for k, v in article["exemptions"].items()
        }

        selected_exemption_label = st.selectbox(
            "是否属于特殊包装？",
            list(exemption_options.keys())
        )

        exemption_key = exemption_options[selected_exemption_label]
        exemption = article["exemptions"][exemption_key]


        plastic_under_5 = st.radio(
            "塑料部分是否低于整个包装单元重量的5%？",
            ["否", "是"],
            horizontal=True
        )


        food_health_issue = st.radio(
            "食品接触包装是否存在Article 7(5)(a)所述健康/合规问题？",
            ["否", "是", "尚不确定"]
        )


    st.divider()

    st.caption(
        f'数据状态：{policy["status_as_of"]}'
    )

    st.caption(
        "当前版本聚焦 PPWR Article 7"
    )


# =========================================================
# APPLICABILITY ENGINE
# =========================================================

exempt_reason = None
review_needed = False


if exemption["exempt"]:

    exempt_reason = exemption["basis"]


elif plastic_under_5 == "是":

    exempt_reason = "Article 7(5)(b)"


elif food_health_issue == "是":

    exempt_reason = "Article 7(5)(a)"


elif food_health_issue == "尚不确定":

    review_needed = True


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="eyebrow">Circular Policy Navigator</div>',
    unsafe_allow_html=True
)

st.title("我的塑料包装需要多少再生料？")

st.markdown(
    '<div class="policy-subtitle">'
'判断你的包装适用多少再生塑料比例，以及第三国再生料需要满足什么条件'
'</div>',
    unsafe_allow_html=True
)


# =========================================================
# KEY CONCLUSION
# =========================================================

if exempt_reason:

    status = "豁免"
    status_foot = exempt_reason
    status_value = "豁免"

    conclusion = (
        f"当前情景触发 {exempt_reason}。"
        "Article 7(1)和7(2)规定的最低再生含量目标不适用。"
    )

elif review_needed:

    status = "待判断"
    status_foot = "Article 7(5)(a)"
    status_value = "待判断"

    conclusion = (
        "当前情景需要进一步确认食品接触安全条件；"
        "在确认前，不宜直接判断最低再生含量目标是否适用。"
    )

else:

    status = "适用"
    status_foot = category["basis_2030"]
    status_value = "适用"

    if source_key == "third_country":

        conclusion = (
            f"{category['label']}适用Article 7最低再生含量目标；"
            f"第三国来源再生塑料还需满足收集、再生及等效性核验要求。"
        )

    else:

        conclusion = (
            f"{category['label']}适用Article 7最低再生含量目标；"
            "同时需要按照统一核算方法和技术文件要求证明合规。"
        )


st.markdown(
    f"""
    <div class="conclusion-box">
        <div class="conclusion-title">你的分析结果</div>
        <div class="conclusion-text">{conclusion}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4 = st.columns(4)


with c1:

    kpi_card(
        "适用性",
        status_value,
        status_foot
    )


with c2:

    if exempt_reason:

        kpi_card(
            "2030最低再生含量",
            "—",
            "当前情景触发豁免"
        )

    else:

        kpi_card(
            "2030最低再生含量",
            f'{category["target_2030"]}%',
            category["basis_2030"]
        )


with c3:

    if exempt_reason:

        kpi_card(
            "2040最低再生含量",
            "—",
            "当前情景触发豁免"
        )

    else:

        kpi_card(
            "2040最低再生含量",
            f'{category["target_2040"]}%',
            category["basis_2040"]
        )


with c4:

    kpi_card(
        "再生料来源",
        "第三国" if source_key == "third_country" else "欧盟",
        source["label"]
    )


if not exempt_reason:

    st.caption(
        "2030要求适用时间："
        + article["calculation"]["target_date_2030"]
    )


st.divider()


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "政策图谱",
        "为什么这样判断",
        "实施路线图",
        "证据清单"
    ]
)


# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader("Article 7 · Policy Map")

    st.caption(
        "图谱只保留当前情景真正相关的政策节点。"
    )

    graph = Digraph()

    graph.attr(
        rankdir="TB",
        bgcolor="transparent",
        pad="0.2",
        nodesep="0.4",
        ranksep="0.48",
        splines="ortho"
    )

    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fontname="Arial",
        fontsize="11",
        margin="0.18,0.12",
        color="#C7D0D9",
        penwidth="1.1"
    )

    graph.attr(
        "edge",
        color="#7B8792",
        penwidth="1.0",
        arrowsize="0.65"
    )


    graph.node(
        "article",
        "PPWR · Article 7",
        fillcolor="#DCE8F2"
    )


    if exempt_reason:

        graph.node(
            "screen",
            "适用性筛查",
            fillcolor="#F3E9E9"
        )

        graph.node(
            "exempt",
            f"豁免\n{exempt_reason}",
            fillcolor="#F2DADA"
        )

        graph.edge(
            "article",
            "screen"
        )

        graph.edge(
            "screen",
            "exempt"
        )


    else:

        graph.node(
            "category",
            category["label"],
            fillcolor="#EEF2F6"
        )

        graph.node(
            "t2030",
            f'2030目标\n{category["target_2030"]}%',
            fillcolor="#E5EFE7"
        )

        graph.node(
            "t2040",
            f'2040目标\n{category["target_2040"]}%',
            fillcolor="#E5EFE7"
        )

        graph.node(
            "source",
            "第三国来源"
            if source_key == "third_country"
            else "欧盟来源",
            fillcolor="#F1EEE7"
        )


        graph.edge(
            "article",
            "category"
        )

        graph.edge(
            "category",
            "t2030"
        )

        graph.edge(
            "category",
            "t2040"
        )

        graph.edge(
            "article",
            "source"
        )


        if source_key == "third_country":

            graph.node(
                "collection",
                "分类收集等效",
                fillcolor="#F6EBD9"
            )

            graph.node(
                "recycling",
                "再生与环境绩效等效",
                fillcolor="#F6EBD9"
            )

            graph.node(
                "verification",
                "评估 · 核验 · 认证\n第三方审核",
                fillcolor="#F2DFC6"
            )

            graph.edge(
                "source",
                "collection"
            )

            graph.edge(
                "collection",
                "recycling"
            )

            graph.edge(
                "recycling",
                "verification"
            )

        else:

            graph.node(
                "evidence",
                "计算与核验\nTechnical documentation",
                fillcolor="#E9EEF3"
            )

            graph.edge(
                "source",
                "evidence"
            )


    st.graphviz_chart(
        graph,
        width="stretch"
    )


# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.subheader("判断逻辑")

    left, right = st.columns(
        [1, 1]
    )


    with left:

        st.markdown("#### 1 · 包装类型")

        st.write(
            category["label"]
        )

        st.caption(
            category["note"]
        )

        if not exempt_reason:

            st.write(
                f'2030：{category["basis_2030"]}'
            )

            st.write(
                f'2040：{category["basis_2040"]}'
            )


        st.markdown("#### 2 · 适用性筛查")

        if exempt_reason:

            st.error(
                f"触发豁免：{exempt_reason}"
            )

        elif review_needed:

            st.warning(
                "Article 7(5)(a)需进一步核实"
            )

        else:

            st.success(
                "当前输入未触发Article 7(4)或7(5)豁免"
            )


    with right:

        st.markdown("#### 3 · 材料来源")

        st.write(
            source["summary"]
        )

        for item in source["conditions"]:

            st.write(
                f"• {item}"
            )


# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.subheader("Article 7 · Regulatory Roadmap")

    st.caption(
        "不是所有要求都在法规正文公布时完全落地。"
        "这里单独展示Article 7仍依赖的实施规则与后续审查。"
    )

    for item in article["dependencies"]:

        timeline_card(
            item["date"],
            item["title"],
            item["description"],
            item["basis"]
        )


# =========================================================
# TAB 4
# =========================================================

with tab4:

    st.subheader("你需要准备什么证据？")

    st.caption(
        "以下清单将Article 7和Annex VII的要求转化为准备事项，"
        "用于政策研究和合规准备，不替代正式法律意见。"
    )


    col_a, col_b = st.columns(2)


    with col_a:

        st.markdown(
            "#### 一般技术文件"
        )

        for item in article["technical_documentation"]["general"]:

            st.checkbox(
                item,
                key=f"general_{item}"
            )


    with col_b:

        if source_key == "third_country":

            st.markdown(
                "#### 第三国来源额外证据"
            )

            for item in source["conditions"]:

                st.checkbox(
                    item,
                    key=f"third_country_{item}"
                )

        else:

            st.markdown(
                "#### 欧盟来源材料"
            )

            for item in source["conditions"]:

                st.checkbox(
                    item,
                    key=f"eu_{item}"
                )


    st.info(
        article["technical_documentation"]["article_7_note"]
    )


    st.markdown(
        "#### 法律依据"
    )

    st.write(
        "Article 7(1)–(3)：目标、核算边界及材料来源"
    )

    st.write(
        "Article 7(4)–(5)：豁免"
    )

    st.write(
        "Article 7(6)：制造商/进口商技术资料证明"
    )

    st.write(
        "Article 7(8)–(10)：计算核验、再生技术及第三国等效方法"
    )

    st.write(
        "Annex VII：Conformity assessment / Technical documentation"
    )


    st.link_button(
        "打开 EUR-Lex 官方 PPWR 原文",
        "https://eur-lex.europa.eu/eli/reg/2025/40/oj"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Circular Policy Navigator · PPWR Article 7 Prototype v0.4"
    "  |  Regulation (EU) 2025/40"
    "  |  Policy research tool — not legal advice"
)