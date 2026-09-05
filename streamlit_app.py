import streamlit as st
from pathlib import Path
import yaml
from graphviz import Digraph


# =========================================================
# GLOBAL CONFIG
# =========================================================

st.set_page_config(
    page_title="Circular Policy Navigator",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SHARED STYLE
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1320px;
        padding-top: 2.4rem;
        padding-bottom: 4rem;
    }

    .eyebrow {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #607080;
        margin-bottom: 0.35rem;
    }

    .intro {
        font-size: 1.05rem;
        color: #4F5D69;
        line-height: 1.7;
        max-width: 900px;
    }

    .result-box {
        background: #EAF1F7;
        border-left: 4px solid #31597C;
        border-radius: 7px;
        padding: 18px 20px;
        margin-top: 15px;
        margin-bottom: 18px;
    }

    .result-label {
        color: #31597C;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin-bottom: 7px;
    }

    .result-text {
        color: #17212B;
        font-size: 1.06rem;
        font-weight: 600;
        line-height: 1.65;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    # =====================================================
    # SEARCH ACTION
    # =====================================================

    def go_to_explorer(query_text):
        query_text = (query_text or "").strip()

        if not query_text:
            st.warning(
                "请输入你要查的关键词或年份。"
            )
            return

        # 把首页输入暂存起来，带到政策检索页
        st.session_state["ppwr_prefill_query"] = query_text

        st.switch_page(
            explorer
        )

    # =====================================================
    # HERO
    # =====================================================

    st.caption("PPWR 政策检索器")

    st.title(
        "一键查询"
    )

    st.write(
        "不需要输入具体第几条法规条款。"
        "输入问题、产品、年份或政策主题即可查找。"
    )

    # =====================================================
    # MAIN SEARCH
    # =====================================================

    st.write("")

    with st.form(
        "home_search_form",
        clear_on_submit=False,
    ):

        home_query = st.text_input(
            "搜索 PPWR",
            placeholder=(
                "例如：2030 年有哪些要求？"
                "第三国再生塑料能否计入？"
                "药品包装是否豁免？"
            ),
            label_visibility="collapsed",
        )

        search_clicked = st.form_submit_button(
            "查找相关规则",
            type="primary",
            use_container_width=True,
        )

        if search_clicked:
            go_to_explorer(
                home_query
            )

    st.caption(
        "可以直接输入完整问题，也支持中文、英文、年份和条款编号。"
    )

    st.markdown("---")

    # =====================================================
    # DEEP ANALYSIS
    # =====================================================

    st.markdown(
        "## 已经有一个具体包装问题？"
    )

    st.caption(
        "选择对应工具，直接判断你的具体情况。"
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # RECYCLABILITY
    # -----------------------------------------------------

    with col1:

        with st.container(
            border=True
        ):

            st.caption(
                "包装可回收性"
            )

            st.markdown(
                "### 我的包装未来还能进入欧盟市场吗？"
            )

            st.write(
                "查看 2030、2035、2038 "
                "不同阶段需要达到的可回收性要求。"
            )

            if st.button(
                "开始判断",
                key="home_recyclability",
                type="primary",
                use_container_width=True,
            ):
                st.switch_page(
                    recyclability
                )

    # -----------------------------------------------------
    # RECYCLED CONTENT
    # -----------------------------------------------------

    with col2:

        with st.container(
            border=True
        ):

            st.caption(
                "再生含量"
            )

            st.markdown(
                "### 我的塑料包装需要多少再生料？"
            )

            st.write(
                "查看 2030、2040 "
                "最低比例，以及豁免和第三国材料要求。"
            )

            if st.button(
                "开始判断",
                key="home_recycled_content",
                type="primary",
                use_container_width=True,
            ):
                st.switch_page(
                    recycled_content
                )

    st.write("")

    st.caption(
        "当前重点覆盖 PPWR 核心规则检索、包装可回收性和塑料包装再生含量。"
    )
@st.cache_data
def load_article6():

    with open(
        "data/article6.yaml",
        "r",
        encoding="utf-8"
    ) as file:

        return yaml.safe_load(file)["article_6"]


# =========================================================
# ARTICLE 6 ANALYZER
# =========================================================

def recyclability_page():

    article = load_article6()


    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.markdown(
        '<div class="eyebrow">PPWR · 可回收性专题分析</div>',
        unsafe_allow_html=True
    )

    st.title(
        "我的包装未来还能否在欧盟市场销售？"
    )

    st.write(
        "基于PPWR Article 6，判断包装未来需要达到的"
        "可回收性门槛、关键时间节点，以及企业现在可以准备什么。"
    )

    st.info(
        "现阶段工具不会直接给具体包装判定A/B/C等级。"
        "PPWR已经确定等级制度，但具体Design for Recycling标准、"
        "包装类别参数及等级评估方法仍依赖后续授权法案。"
    )


    # -----------------------------------------------------
    # SCENARIO INPUT
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "① 告诉我你的包装情况"
    )

    st.caption(
        "先回答三个基础问题；创新包装可进一步展开。"
    )


    input1, input2, input3 = st.columns(
        [1, 1, 1.25]
    )


    with input1:

        material = st.selectbox(
            "你的包装主要是什么材料？",
            [
                "塑料",
                "纸 / 纸板",
                "玻璃",
                "金属",
                "复合材料",
                "木材",
                "其他"
            ],
            help=(
                "Article 6原则上适用于所有包装。"
                "材料信息主要用于描述当前情景。"
            )
        )


    with input2:

        target_period = st.selectbox(
            "你想判断哪个时间点？",
            [
                "当前（2026）",
                "2030",
                "2035",
                "2038及以后"
            ]
        )


    exemption_options = {
        value["label"]: key
        for key, value
        in article["exemptions"].items()
    }


    with input3:

        selected_exemption_label = st.selectbox(
            "是否属于特殊包装？",
            list(exemption_options.keys()),
            help=(
                "部分药品、医疗器械、危险品运输包装等"
                "在Article 6下存在特殊豁免。"
            )
        )


    exemption_key = exemption_options[
        selected_exemption_label
    ]

    exemption = article[
        "exemptions"
    ][exemption_key]


    with st.expander(
        "是否属于创新包装？",
        expanded=False
    ):

        st.caption(
            "Article 6(10)为符合条件的创新包装设置了"
            "有限期特别路径，但并不是自动豁免。"
        )

        innovative = st.radio(
            "你的包装是否准备按照创新包装路径处理？",
            [
                "否",
                "是",
                "尚不确定"
            ],
            horizontal=True
        )


    # -----------------------------------------------------
    # STAGE ENGINE
    # -----------------------------------------------------

    stage_map = {

        "当前（2026）": "current",

        "2030": "2030",

        "2035": "2035",

        "2038及以后": "2038"

    }


    stage_key = stage_map[
        target_period
    ]


    stage = article[
        "stages"
    ][stage_key]


    # -----------------------------------------------------
    # DECISION ENGINE
    # -----------------------------------------------------

    if exemption["exempt"]:

        if exemption["partial"]:

            result_status = "部分豁免"

            result_text = (
                f"当前情景属于 {exemption['basis']} 所列特殊包装。"
                "Article 6主体可回收性要求原则上不适用；"
                "但Article 6(8)关于EPR费用调节的规定仍适用。"
            )

        else:

            result_status = "豁免"

            result_text = (
                f"当前情景触发 {exemption['basis']}。"
                "Article 6主体可回收性要求不适用于该包装。"
            )


    elif (
        innovative == "是"
        and stage_key != "current"
    ):

        result_status = "创新包装特别路径"

        result_text = (
            "当前包装可能进入Article 6(10)创新包装特别路径。"
            "这不等于自动合规：需要在投放市场前通知主管机关，"
            "提交证明包装创新性的技术资料，"
            "并提供达到recycled-at-scale要求的时间表。"
        )


    elif innovative == "尚不确定":

        result_status = "需要进一步判断"

        result_text = (
            f"{target_period}情景下仍应首先按照正常Article 6"
            "可回收性路径准备。"
            "如果未来拟使用创新包装特别路径，"
            "需要再判断是否满足Article 6(10)条件。"
        )


    else:

        if stage_key == "current":

            result_status = "规则落地中"

        elif stage_key == "2030":

            result_status = "A/B/C准入阶段"

        elif stage_key == "2035":

            result_status = "规模化再生准入阶段"

        else:

            result_status = "A/B级准入阶段"


        result_text = (
            f"{target_period}情景下："
            f"{stage['headline']}。 "
            f"{stage['requirement']}"
        )


    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "② 你的分析结果"
    )


    st.markdown(
    f"""
<div class="result-box">
<div class="result-label">你的分析结果</div>
<div class="result-text">{result_text}</div>
</div>
""",
    unsafe_allow_html=True
)


    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "判断状态",
            result_status
        )


    with c2:

        st.metric(
            "判断时间点",
            target_period
        )


    with c3:

        if exemption["exempt"]:

            grade_text = "—"

        elif stage_key == "current":

            grade_text = "方法待细化"

        elif stage_key in [
            "2030",
            "2035"
        ]:

            grade_text = "A / B / C"

        else:

            grade_text = "仅 A / B"


        st.metric(
            "可回收等级门槛",
            grade_text
        )


    with c4:

        if exemption["exempt"]:

            scale_text = "—"

        elif stage_key in [
            "2035",
            "2038"
        ]:

            scale_text = "纳入准入"

        elif stage_key == "2030":

            scale_text = "后续叠加"

        else:

            scale_text = "方法待出台"


        st.metric(
            "规模化再生",
            scale_text
        )


    if not exemption["exempt"]:

        st.caption(
            f'当前主要法律依据：{stage["basis"]}'
        )


    # -----------------------------------------------------
    # TWO-LAYER LOGIC
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "③ PPWR如何判断“可回收”？"
    )

    st.caption(
        "Article 6并不只问材料理论上能不能回收，而是设置两层要求。"
    )


    left, right = st.columns(2)


    with left:

        with st.container(border=True):

            st.caption(
                "第一层 · 设计端"
            )

            st.markdown(
                "### Design for Recycling"
            )

            st.write(
                "包装应当从设计阶段就能够进入材料再生流程，"
                "并使产生的二次原料具有足够质量，"
                "能够替代原生材料。"
            )

            st.caption(
                "Article 6(2)(a) · Article 6(4)"
            )


    with right:

        with st.container(border=True):

            st.caption(
                "第二层 · 现实系统"
            )

            st.markdown(
                "### Recycled at Scale"
            )

            st.write(
                "包装成为废弃物后，还需要能够被分类收集、"
                "进入特定分选流，并在现实系统中实现规模化再生。"
            )

            st.caption(
                "Article 6(2)(b) · Article 6(5)"
            )


    st.info(
        "因此，“技术上可以回收”并不自动等于"
        "PPWR意义上的“可回收包装”。"
        "法规同时关注设计可回收性和实际收集、分选、"
        "规模化再生条件。"
    )


    # -----------------------------------------------------
    # ANALYSIS TABS
    # -----------------------------------------------------

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "市场准入路线图",
            "特殊包装与创新包装",
            "尚待出台的规则",
            "企业现在可以准备什么"
        ]
    )


    # =====================================================
    # TAB 1 — ROADMAP
    # =====================================================

    with tab1:

        st.subheader(
            "Article 6 市场准入路线"
        )


        if exemption["exempt"]:

            graph = Digraph()

            graph.attr(
                rankdir="LR",
                bgcolor="transparent"
            )

            graph.attr(
                "node",
                shape="box",
                style="rounded,filled",
                fontname="Arial",
                color="#C7D0D9"
            )

            graph.node(
                "a",
                "PPWR\nArticle 6",
                fillcolor="#DCE8F2"
            )

            graph.node(
                "b",
                "特殊包装判断",
                fillcolor="#F2EEE5"
            )

            graph.node(
                "c",
                f'{result_status}\n'
                f'{exemption["basis"]}',
                fillcolor="#F0E2DC"
            )

            graph.edge(
                "a",
                "b"
            )

            graph.edge(
                "b",
                "c"
            )


            st.graphviz_chart(
                graph,
                width="stretch"
            )


        else:

            graph = Digraph()

            graph.attr(
                rankdir="LR",
                bgcolor="transparent",
                nodesep="0.35",
                ranksep="0.55"
            )

            graph.attr(
                "node",
                shape="box",
                style="rounded,filled",
                fontname="Arial",
                fontsize="10",
                color="#C7D0D9"
            )

            graph.attr(
                "edge",
                color="#7B8792",
                arrowsize="0.6"
            )


            graph.node(
                "a",
                "Article 6\n所有包装原则上须可回收",
                fillcolor="#DCE8F2"
            )

            graph.node(
                "b",
                "Design for\nRecycling",
                fillcolor="#E5EFE7"
            )

            graph.node(
                "c",
                "2030阶段\nA / B / C",
                fillcolor="#E5EFE7"
            )

            graph.node(
                "d",
                "2035阶段\nRecycled at Scale",
                fillcolor="#F2EEE5"
            )

            graph.node(
                "e",
                "2038\n仅 A / B",
                fillcolor="#F0E2DC"
            )


            graph.edge(
                "a",
                "b"
            )

            graph.edge(
                "b",
                "c"
            )

            graph.edge(
                "c",
                "d"
            )

            graph.edge(
                "d",
                "e"
            )


            st.graphviz_chart(
                graph,
                width="stretch"
            )


            st.warning(
                "2030和2035均存在条件触发机制，"
                "不能简单理解为固定日历日期。"
                "具体适用时间与后续授权法案或实施法案的"
                "实际生效时间挂钩。"
            )


    # =====================================================
    # TAB 2 — EXEMPTIONS
    # =====================================================

    with tab2:

        st.subheader(
            "哪些包装存在特殊处理？"
        )


        if exemption["exempt"]:

            st.warning(
                f"你的当前选择对应 {exemption['basis']}。"
            )


        st.markdown(
            "#### Article 6(11) 特定豁免"
        )


        for key, item in article[
            "exemptions"
        ].items():

            if key == "none":
                continue


            if item["partial"]:

                type_label = "部分豁免"

            else:

                type_label = "豁免"


            st.write(
                f'• **{item["label"]}** '
                f'— {type_label} · {item["basis"]}'
            )


        st.markdown(
            "#### Article 6(10) 创新包装特别路径"
        )

        st.write(
            article[
                "innovative_packaging"
            ]["summary"]
        )


        for condition in article[
            "innovative_packaging"
        ]["conditions"]:

            st.write(
                f"• {condition}"
            )


    # =====================================================
    # TAB 3 — DEPENDENCIES
    # =====================================================

    with tab3:

        st.subheader(
            "哪些关键规则还没有完全落地？"
        )

        st.caption(
            "这是当前无法可靠地为具体包装直接计算A/B/C等级的主要原因。"
        )


        for item in article[
            "dependencies"
        ]:

            with st.container(
                border=True
            ):

                st.caption(
                    f'{item["date"]}'
                    f' · {item["basis"]}'
                )

                st.markdown(
                    f'**{item["title"]}**'
                )

                st.write(
                    item["description"]
                )

                st.caption(
                    item["instrument"]
                )


    # =====================================================
    # TAB 4 — EVIDENCE
    # =====================================================

    with tab4:

        st.subheader(
            "企业现在可以开始准备什么？"
        )

        st.caption(
            "即使最终DfR评估方法尚待出台，"
            "企业也可以提前建立数据和技术资料基础。"
        )


        left_check, right_check = st.columns(2)


        with left_check:

            st.markdown(
                "#### 包装设计与技术资料"
            )

            for index, item in enumerate(
                article[
                    "evidence"
                ]["general"]
            ):

                st.checkbox(
                    item,
                    key=(
                        f"article6_general_"
                        f"{stage_key}_"
                        f"{index}"
                    )
                )


        with right_check:

            st.markdown(
                "#### 规模化再生与数据链"
            )

            for index, item in enumerate(
                article[
                    "evidence"
                ]["recycled_at_scale"]
            ):

                st.checkbox(
                    item,
                    key=(
                        f"article6_scale_"
                        f"{stage_key}_"
                        f"{index}"
                    )
                )


        st.info(
            "Article 6(9)要求通过Annex VII技术文件"
            "证明Article 6(2)和Article 6(3)相关要求的合规。"
        )


    # -----------------------------------------------------
    # WHY NO A/B/C NOW
    # -----------------------------------------------------

    st.divider()


    with st.expander(
        "为什么现在不能直接告诉我具体包装是A、B还是C？"
    ):

        st.write(
            "PPWR正文已经建立A/B/C等级制度和未来市场准入门槛，"
            "但具体Design for Recycling标准、"
            "不同包装类别的评估参数以及等级计算方法，"
            "仍需要Article 6(4)授权法案进一步确定。"
        )

        st.write(
            "因此目前最可靠的工具输出是："
            "适用范围、未来准入门槛、法规依赖和企业准备事项，"
            "而不是自行创造一个尚无法依法计算的A/B/C评级。"
        )


    st.caption(
        "Source · Regulation (EU) 2025/40 · Article 6"
        "  |  Policy research tool — not legal advice"
    )


# =========================================================
# PAGE DEFINITIONS
# =========================================================

home = st.Page(
    home_page,
    title="首页",
    icon=":material/home:",
    default=True
)


explorer = st.Page(
    "pages/1_PPWR_Core_Explorer.py",
    title="PPWR 核心政策导航",
    icon=":material/search:"
)

implementation_tracker = st.Page(
    "pages/4_PPWR_Implementation_Tracker.py",
    title="PPWR 实施进展",
    icon=":material/update:"
)

recyclability = st.Page(
    recyclability_page,
    title="包装可回收性分析",
    icon=":material/recycling:"
)


recycled_content = st.Page(
    "pages/2_Article_7_Analyzer.py",
    title="再生含量情景分析",
    icon=":material/account_tree:"
)


# =========================================================
# NAVIGATION
# =========================================================

pg = st.navigation(
    {

        "开始": [
            home
        ],

        "政策导航": [
            explorer,
    implementation_tracker
        ],

        "专题分析": [
            recyclability,
            recycled_content
        ]

    },
    position="sidebar"
)


# =========================================================
# RUN
# =========================================================

pg.run()