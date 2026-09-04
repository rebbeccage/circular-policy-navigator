import streamlit as st
import yaml
from graphviz import Digraph


st.set_page_config(
    page_title="PPWR 核心政策导航",
    layout="wide"
)


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1380px;
        padding-top: 2.2rem;
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

    .summary-box {
        background: #EAF1F7;
        border-left: 4px solid #31597C;
        border-radius: 6px;
        padding: 16px 18px;
        margin: 12px 0 18px 0;
    }

    .user-question {
        font-size: 1.0rem;
        font-weight: 650;
        color: #31597C;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_core():
    with open("data/ppwr_core.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


data = load_core()
catalog = data["catalog"]
articles = data["articles"]


# =========================================================
# USER-FRIENDLY MAP
# 以后稳定后可移入 YAML
# =========================================================

USER_QUESTIONS = {

    "article_5":
        "我的包装材料中有哪些物质限制或关注物质要求？",

    "article_6":
        "我的包装未来还能否被认定为可回收并投放欧盟市场？",

    "article_7":
        "我的塑料包装需要使用多少再生塑料？",

    "article_8":
        "PPWR现在是否强制要求使用生物基塑料？",

    "article_9":
        "哪些包装应该走可堆肥路径，哪些仍应材料再生？",

    "article_10":
        "我的包装重量或体积是否超过功能真正需要的水平？",

    "article_11":
        "什么样的包装才能被认定为可复用包装？",

    "article_12":
        "我的包装什么时候需要统一标签或数字信息？",

    "article_28":
        "如果提供补充装 / refill，需要满足哪些运营要求？",

    "article_29":
        "我的运输包装、组合包装或饮料包装需要达到多少复用比例？",

    "article_43":
        "欧盟成员国需要把包装废弃物减少多少？",

    "article_44":
        "生产者需要在哪里登记，并报告什么？",

    "article_45":
        "谁承担EPR？跨境销售需要注意什么？",

    "article_50":
        "哪些饮料容器需要进入押金返还系统？",

    "article_52":
        "欧盟包装废弃物回收目标是多少？"
}


GOVERNANCE_PATHS = {

    "源头减量与材料安全": [
        "article_5",
        "article_10"
    ],

    "循环设计与材料循环": [
        "article_6",
        "article_7",
        "article_8",
        "article_9"
    ],

    "复用与补充装": [
        "article_11",
        "article_28",
        "article_29"
    ],

    "标签与市场信息": [
        "article_12"
    ],

    "废弃物管理与生产者责任": [
        "article_43",
        "article_44",
        "article_45",
        "article_50",
        "article_52"
    ]
}


def get_path(article_id):

    for path, ids in GOVERNANCE_PATHS.items():

        if article_id in ids:
            return path

    return "其他"


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="eyebrow">PPWR Policy Navigator</div>',
    unsafe_allow_html=True
)

st.title("PPWR 核心政策导航")

st.write(
    "不需要先知道Article编号。可以从治理问题、关键词或政策路径进入。"
)

st.caption(
    "当前覆盖经人工核验的核心条款，不是整部法规的全文搜索。"
)


# =========================================================
# PANORAMA MAP
# =========================================================

st.divider()

st.subheader("PPWR 治理路径全景")

st.caption(
    "从源头设计一直到废弃物管理，查看主要政策工具之间的关系。"
)


graph = Digraph()

graph.attr(
    rankdir="TB",
    bgcolor="transparent",
    nodesep="0.28",
    ranksep="0.52",
    splines="ortho"
)

graph.attr(
    "node",
    shape="box",
    style="rounded,filled",
    fontname="Arial",
    fontsize="10",
    color="#C7D0D9",
    penwidth="1"
)

graph.attr(
    "edge",
    color="#8B97A3",
    arrowsize="0.55"
)


graph.node(
    "PPWR",
    "PPWR\nRegulation (EU) 2025/40",
    fillcolor="#DCE8F2"
)


PATH_COLORS = {
    "源头减量与材料安全": "#EDF1F5",
    "循环设计与材料循环": "#E5EFE7",
    "复用与补充装": "#F2EEE5",
    "标签与市场信息": "#EBEEF5",
    "废弃物管理与生产者责任": "#F1EAE6"
}


article_lookup = {
    article["id"]: article
    for article in articles
}


for path_index, (path, article_ids) in enumerate(
    GOVERNANCE_PATHS.items()
):

    path_node = f"path_{path_index}"

    graph.node(
        path_node,
        path,
        fillcolor=PATH_COLORS[path]
    )

    graph.edge(
        "PPWR",
        path_node
    )

    for article_id in article_ids:

        if article_id not in article_lookup:
            continue

        article = article_lookup[article_id]

        node_id = f"node_{article_id}"

        graph.node(
            node_id,
            f'{article["article"]}\n{article["title_cn"]}',
            fillcolor="#FFFFFF"
        )

        graph.edge(
            path_node,
            node_id
        )


st.graphviz_chart(
    graph,
    width="stretch"
)


# =========================================================
# FILTER ENTRY
# =========================================================

st.divider()

st.subheader("从你的问题开始")

search_col, path_col = st.columns(
    [2.2, 1]
)


with search_col:

    search_term = st.text_input(
        "搜索政策问题或关键词",
        placeholder=(
            "例如：我的包装能否回收、再生料、第三国、"
            "reuse、EPR、标签、减量..."
        )
    )


with path_col:

    selected_path = st.selectbox(
        "治理路径",
        ["全部路径"]
        + list(GOVERNANCE_PATHS.keys())
    )


# =========================================================
# SEARCH ENGINE
# =========================================================

def article_matches(article, term):

    if not term:
        return True

    term = term.lower().strip()

    question = USER_QUESTIONS.get(
        article["id"],
        ""
    )

    path = get_path(
        article["id"]
    )

    searchable = " ".join(
        [
            article["article"],
            article["title_cn"],
            article["title_en"],
            article["theme"],
            article["summary"],
            question,
            path,
            " ".join(article["keywords"]),
            " ".join(article["key_points"])
        ]
    ).lower()

    return term in searchable


filtered_articles = []


for article in articles:

    path_match = (
        selected_path == "全部路径"
        or get_path(article["id"]) == selected_path
    )

    search_match = article_matches(
        article,
        search_term
    )

    if path_match and search_match:
        filtered_articles.append(article)


st.caption(
    f"找到 {len(filtered_articles)} 项相关核心条款"
)


# =========================================================
# SELECTED ARTICLE STATE
# =========================================================

if "selected_core_article" not in st.session_state:

    st.session_state.selected_core_article = "article_6"


filtered_ids = [
    article["id"]
    for article in filtered_articles
]


if (
    filtered_articles
    and st.session_state.selected_core_article
    not in filtered_ids
):

    st.session_state.selected_core_article = (
        filtered_articles[0]["id"]
    )


# =========================================================
# CARDS
# =========================================================

if not filtered_articles:

    st.warning(
        "没有找到匹配结果。"
        "可以尝试更宽泛的关键词。"
    )


else:

    cols = st.columns(3)

    for index, article in enumerate(
        filtered_articles
    ):

        with cols[index % 3]:

            with st.container(
                border=True
            ):

                st.caption(
                    f'{get_path(article["id"])} '
                    f'· {article["article"]}'
                )

                st.subheader(
                    article["title_cn"]
                )

                st.caption(
                    article["title_en"]
                )

                question = USER_QUESTIONS.get(
                    article["id"],
                    ""
                )

                st.markdown(
                    f"""
                    <div class="user-question">
                    {question}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.write(
                    article["summary"]
                )

                if st.button(
                    "查看政策分析",
                    key=f'open_{article["id"]}',
                    width="stretch"
                ):

                    st.session_state.selected_core_article = (
                        article["id"]
                    )

                    st.rerun()


# =========================================================
# STRUCTURED ANALYSIS
# =========================================================

selected_article = next(
    (
        article
        for article in articles
        if article["id"]
        == st.session_state.selected_core_article
    ),
    articles[0]
)


st.divider()

st.markdown(
    '<div class="eyebrow">Structured Analysis</div>',
    unsafe_allow_html=True
)

st.header(
    f'{selected_article["title_cn"]}'
)

st.caption(
    f'{selected_article["article"]} · '
    f'{selected_article["title_en"]}'
)


st.markdown(
    f"""
    <div class="summary-box">
        <b>这条政策解决什么问题？</b>
        <br><br>
        {USER_QUESTIONS.get(selected_article["id"], "")}
        <br><br>
        <b>核心判断</b>
        <br><br>
        {selected_article["summary"]}
    </div>
    """,
    unsafe_allow_html=True
)


m1, m2, m3 = st.columns(3)


with m1:

    st.metric(
        "政策路径",
        get_path(selected_article["id"])
    )


with m2:

    st.metric(
        "责任主体",
        " / ".join(
            selected_article["actors"][:2]
        )
    )


with m3:

    st.metric(
        "政策状态",
        selected_article["status"]
    )


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "核心要求",
        "时间节点",
        "证据准备",
        "关联规则"
    ]
)


with tab1:

    for point in selected_article["key_points"]:
        st.write(
            f"• {point}"
        )


with tab2:

    if not selected_article["dates"]:

        st.info(
            "当前结构化条目未设置单独时间节点。"
        )

    else:

        for item in selected_article["dates"]:

            with st.container(
                border=True
            ):

                st.caption(
                    item["date"]
                )

                st.write(
                    item["event"]
                )


with tab3:

    for evidence in selected_article["evidence"]:

        st.checkbox(
            evidence,
            key=(
                f'{selected_article["id"]}_'
                f'{evidence}'
            )
        )

    st.caption(
        "这是政策研究型准备清单，"
        "不替代正式法律意见。"
    )


with tab4:

    relation_graph = Digraph()

    relation_graph.attr(
        rankdir="LR",
        bgcolor="transparent"
    )

    relation_graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fontname="Arial",
        color="#C7D0D9"
    )

    relation_graph.node(
        "main",
        f'{selected_article["article"]}\n'
        f'{selected_article["title_cn"]}',
        fillcolor="#DCE8F2"
    )


    for i, related in enumerate(
        selected_article["related"]
    ):

        node_id = f"related_{i}"

        relation_graph.node(
            node_id,
            related,
            fillcolor="#EEF2F6"
        )

        relation_graph.edge(
            "main",
            node_id
        )


    st.graphviz_chart(
        relation_graph,
        width="stretch"
    )


# =========================================================
# DEEP ANALYZER NOTICE
# =========================================================

if selected_article["id"] == "article_6":

    st.info(
        "该主题已提供「包装可回收性分析」专题工具。"
        "请从左侧「专题分析」进入。"
    )


if selected_article["id"] == "article_7":

    st.info(
        "该主题已提供「再生含量情景分析」专题工具。"
        "请从左侧「专题分析」进入。"
    )


st.divider()

st.caption(
    f'Source: {catalog["policy"]} · '
    f'Updated {catalog["updated"]}'
)