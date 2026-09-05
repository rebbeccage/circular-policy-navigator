import streamlit as st
import yaml
from graphviz import Digraph


st.set_page_config(
    page_title="快速查找 PPWR 规则",
    layout="wide"
)
import re


# =========================================================
# QUICK FIND
# 用户不需要知道 Article 编号，也可以直接搜索自己的问题
# =========================================================

SEARCH_ALIASES = {
    "可回收": [
        "可回收", "可回收性", "回收设计", "设计可回收",
        "recyclable", "recyclability", "design for recycling", "dfr",
        "a级", "b级", "c级"
    ],
    "再生含量": [
        "再生含量", "再生塑料", "再生料", "再生材料",
        "pcr", "recycled content", "recycled plastic",
        "再生塑料比例"
    ],
    "第三国": [
        "第三国", "欧盟以外", "进口再生料", "中国再生料",
        "third country", "third-country", "equivalence", "等效"
    ],
    "包装减量": [
        "包装减量", "减量", "过度包装", "包装重量",
        "包装体积", "空隙率", "minimisation", "minimization"
    ],
    "复用": [
        "复用", "重复使用", "可重复使用", "reuse", "re-use",
        "refill", "补充装", "重新灌装"
    ],
    "标签": [
        "标签", "标识", "二维码", "label", "labelling",
        "labeling", "qr"
    ],
    "生产者责任": [
        "生产者责任", "epr", "延伸生产者责任",
        "producer responsibility", "生产者责任组织"
    ],
    "押金返还": [
        "押金返还", "押金制", "drs", "deposit return",
        "deposit and return"
    ],
    "可堆肥": [
        "可堆肥", "生物降解", "compostable", "composting"
    ],
}


def normalize_search_text(value):
    """把不同字段统一变成可搜索文本。"""
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(normalize_search_text(x) for x in value)

    if isinstance(value, dict):
        return " ".join(
            f"{normalize_search_text(k)} {normalize_search_text(v)}"
            for k, v in value.items()
        )

    return str(value)


def expand_query(query):
    """
    把用户的自然语言扩展成相关政策关键词。
    例如搜索“中国再生料”，同时帮助匹配“第三国、equivalence”等。
    """
    query_lower = query.lower().strip()

    expanded = {query_lower}

    for _, aliases in SEARCH_ALIASES.items():
        aliases_lower = [x.lower() for x in aliases]

        if any(
            alias in query_lower or query_lower in alias
            for alias in aliases_lower
        ):
            expanded.update(aliases_lower)

    return expanded


def search_articles(articles, query):
    """
    搜索 Article 编号、标题、主题、关键词、摘要、关键点、日期等字段。
    返回匹配度较高的结果。
    """
    if not query.strip():
        return []

    query_terms = expand_query(query)
    results = []

    for article in articles:

        searchable_parts = [
            article.get("id"),
            article.get("article"),
            article.get("title_cn"),
            article.get("title_en"),
            article.get("theme"),
            article.get("actors"),
            article.get("status"),
            article.get("keywords"),
            article.get("summary"),
            article.get("key_points"),
            article.get("dates"),
        ]

        searchable_text = normalize_search_text(
            searchable_parts
        ).lower()

        score = 0
        matched_terms = []

        for term in query_terms:
            if term and term in searchable_text:
                matched_terms.append(term)

                # Article、标题、关键词匹配权重更高
                headline_text = normalize_search_text(
                    [
                        article.get("article"),
                        article.get("title_cn"),
                        article.get("title_en"),
                        article.get("keywords"),
                    ]
                ).lower()

                if term in headline_text:
                    score += 3
                else:
                    score += 1

        # 支持直接输入 Article 6 / art 6 / 第6条
        article_number = re.search(
            r"(?:article|art\.?|第)?\s*(\d+)",
            query.lower()
        )

        if article_number:
            number = article_number.group(1)
            article_label = str(article.get("article", "")).lower()

            if number in article_label:
                score += 8

        if score > 0:
            results.append(
                {
                    "article": article,
                    "score": score,
                    "matched_terms": matched_terms,
                }
            )

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )
# =========================================================
# ANSWER CARD
# 把“搜索结果”转换成普通用户更容易理解的答案
# =========================================================

USER_QUESTIONS = {
    "art6": "我的包装未来还能否满足欧盟的可回收性要求？",
    "art7": "我的塑料包装需要使用多少再生塑料？",
    "art8": "生物基塑料未来会受到什么要求？",
    "art9": "哪些包装可以或必须使用可堆肥材料？",
    "art10": "我的包装是否需要进一步减量？",
    "art11": "什么样的包装才能被认定为可重复使用？",
    "art12": "我的包装未来需要使用什么标签？",
    "art28": "哪些场景需要提供补充装或复用选择？",
    "art29": "企业需要达到哪些包装复用目标？",
    "art43": "谁需要承担生产者责任？",
    "art44": "生产者需要在哪里登记？",
    "art45": "生产者责任体系需要承担哪些义务？",
    "art50": "哪些包装需要押金返还系统？",
    "art52": "包装废弃物需要达到哪些回收目标？",
}

# =========================================================
# ANSWER CARD HELPERS
# =========================================================

def get_article_key(article):
    """
    将 Article 6、art6 等格式统一成 art6。
    """
    raw_text = " ".join(
        [
            str(article.get("id", "")),
            str(article.get("article", "")),
        ]
    )

    numbers = re.findall(r"\d+", raw_text)

    if numbers:
        return f"art{numbers[0]}"

    return ""


def get_user_question(article):
    """
    把法规条款转换成普通用户真正会问的问题。
    """
    article_key = get_article_key(article)

    questions = {
        "art5": "包装中的化学物质和有害物质受到什么限制？",
        "art6": "我的包装未来还能否满足欧盟的可回收性要求？",
        "art7": "我的塑料包装需要使用多少再生塑料？",
        "art8": "生物基塑料包装未来会有什么要求？",
        "art9": "哪些包装可以或必须采用可堆肥设计？",
        "art10": "我的包装是否需要进一步减少重量和体积？",
        "art11": "什么样的包装才能被认定为可重复使用？",
        "art12": "我的包装未来需要使用什么标签和标识？",
        "art28": "哪些场景需要提供补充装或复用选择？",
        "art29": "企业需要达到哪些包装复用目标？",
        "art43": "谁需要承担生产者责任？",
        "art44": "生产者需要完成哪些登记？",
        "art45": "生产者责任体系具体要求企业做什么？",
        "art50": "哪些包装需要进入押金返还系统？",
        "art52": "包装废弃物需要达到哪些回收目标？",
    }

    return questions.get(
        article_key,
        "这条规则可能与你搜索的问题有关。"
    )


def short_text(value, max_length=180):
    """
    控制卡片中文字长度。
    """
    text = normalize_search_text(value).strip()

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "……"


def format_dates(article):
    """
    把 YAML 中的时间数据转成用户容易理解的形式。
    """
    dates = article.get("dates")

    if not dates:
        return []

    formatted = []

    if isinstance(dates, list):

        for item in dates:

            if isinstance(item, dict):

                raw_date = str(
                    item.get("date", "")
                ).strip()

                event = str(
                    item.get(
                        "event",
                        item.get("description", "")
                    )
                ).strip()

                year_match = re.search(
                    r"20\d{2}",
                    raw_date
                )

                if year_match:
                    year = year_match.group()

                    if "conditional" in raw_date.lower():
                        display_date = f"{year} · 条件生效"
                    else:
                        display_date = year
                else:
                    display_date = raw_date

                if display_date or event:
                    formatted.append(
                        {
                            "date": display_date,
                            "event": event,
                        }
                    )

            else:
                formatted.append(
                    {
                        "date": "",
                        "event": str(item),
                    }
                )

    elif isinstance(dates, dict):

        for key, value in dates.items():
            formatted.append(
                {
                    "date": str(key),
                    "event": normalize_search_text(value),
                }
            )

    else:
        formatted.append(
            {
                "date": "",
                "event": str(dates),
            }
        )

    return formatted[:5]


def render_answer_card(
    article,
    rank=1,
    query="",
    is_primary=False
):
    """
    将搜索结果显示成面向用户的答案卡。
    """

    article_label = article.get(
        "article",
        "相关条款"
    )

    title = article.get(
        "title_cn",
        article.get(
            "title_en",
            "相关政策"
        )
    )

    summary = short_text(
        article.get("summary"),
        180
    )

    user_question = get_user_question(
        article
    )

    dates = format_dates(
        article
    )

    article_key = get_article_key(
        article
    )

    if is_primary:
        st.markdown("#### 建议先看")

    with st.container(border=True):

        st.markdown(
            f"### {title}"
        )

        st.caption(
            article_label
        )

        st.markdown(
            f"**如果你想知道：** {user_question}"
        )

        if summary:
            st.markdown(
                "**一句话看懂**"
            )
            st.write(
                summary
            )

        if dates:
            st.markdown(
                "**关键时间**"
            )

            for item in dates:

                date_label = item.get(
                    "date",
                    ""
                )

                event = item.get(
                    "event",
                    ""
                )

                if date_label:
                    st.markdown(
                        f"**{date_label}**  \n{event}"
                    )
                elif event:
                    st.write(
                        event
                    )

        if article_key == "art6":

            st.info(
                "想判断具体包装在不同年份需要满足什么要求，"
                "请进入左侧栏的「包装可回收性分析」。"
            )

        elif article_key == "art7":

            st.info(
                "如果你想知道具体塑料包装在 2030 / 2040 年"
                "需要达到多少再生含量，请进入左侧的"
                "「再生含量情景分析」。"
            )

        with st.expander(
    "查看更多政策信息"
        ):

            key_points = article.get(
                "key_points"
            )

            if key_points:

                st.markdown(
                    "**具体要求**"
                )

                if isinstance(
                    key_points,
                    list
                ):

                    for point in key_points:
                        st.write(
                            f"• {normalize_search_text(point)}"
                        )

                else:
                    st.write(
                        normalize_search_text(
                            key_points
                        )
                    )

            status = article.get(
                "status"
            )

            if status:

                st.markdown(
                    "**规则状态**"
                )

                st.write(
                    normalize_search_text(
                        status
                    )
                )

            evidence = article.get(
                "evidence"
            )

            if evidence:

                st.markdown(
                    "**可能需要关注的证明材料**"
                )

                if isinstance(
                    evidence,
                    list
                ):

                    for item in evidence:
                        st.write(
                            f"• {normalize_search_text(item)}"
                        )

                else:
                    st.write(
                        normalize_search_text(
                            evidence
                        )
                    )
    """
    显示一张用户导向的政策答案卡。
    """

    article_label = article.get(
        "article",
        "相关条款"
    )

    title = article.get(
        "title_cn",
        article.get("title_en", "相关政策")
    )

    summary = short_text(
        article.get("summary"),
        180
    )

    user_question = get_user_question(article)

    dates = format_dates(article)

    if is_primary:
        st.markdown("#### 最相关")

    with st.container(border=True):

        st.markdown(
            f"### {title}"
        )

        st.caption(article_label)

        st.markdown(
            f"**如果你想知道：**  {user_question}"
        )

        if summary:
            st.markdown("**核心要求**")
            st.write(summary)

        if dates:
            st.markdown("**关键时间**")

            for item in dates:
                date_label = item.get(
                    "date",
                    ""
                )

                event = item.get(
                    "event",
                    ""
                )

                if date_label:
                    st.markdown(
                        f"**{date_label}**  \n{event}"
                    )
                else:
                    st.write(event)

        article_key = get_article_key(article)

        # 对目前已有专题分析器的规则，给用户明确下一步
        if article_key == "art6":
            st.info(
                "想了解具体包装在不同年份需要满足什么要求，"
                "请进入左侧的「包装可回收性分析」。"
            )

        elif article_key == "art7":
            st.info(
                "想知道具体包装在 2030 / 2040 年需要多少再生塑料，"
                "请进入左侧的「再生含量情景分析」。"
            )

        with st.expander("查看更多政策信息"):

            key_points = article.get(
                "key_points"
            )

            if key_points:
                st.markdown("**具体要求**")

                if isinstance(key_points, list):
                    for point in key_points:
                        st.write(
                            f"• {normalize_search_text(point)}"
                        )
                else:
                    st.write(
                        normalize_search_text(key_points)
                    )

            status = article.get("status")

            if status:
                st.markdown("**目前到什么程度**")
                st.write(
                    normalize_search_text(status)
                )

            evidence = article.get("evidence")

            if evidence:
                st.markdown("**可能需要准备的材料**")

                if isinstance(evidence, list):
                    for item in evidence:
                        st.write(
                            f"• {normalize_search_text(item)}"
                        )
                else:
                    st.write(
                        normalize_search_text(evidence)
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

st.title("快速查找 PPWR 规则")
st.markdown(
    """
    <div style="
        margin-top: 0.4rem;
        margin-bottom: 0.3rem;
        font-size: 1.05rem;
        color: #5B6573;
    ">
    输入产品、政策要求、年份或你关心的问题，快速找到相关规则和关键信息。
    </div>
    """,
    unsafe_allow_html=True,
)# =========================================================
# 接收首页带过来的搜索内容
# =========================================================

incoming_query = st.session_state.pop(
    "ppwr_prefill_query",
    None
)

if incoming_query is not None:
    st.session_state[
        "ppwr_quick_query"
    ] = incoming_query

quick_query = st.text_input(
    "快速找政策",
    key="ppwr_quick_query",
    placeholder=(
        "例如：可回收性、第三国再生塑料、"
        "2030、药品包装、Article 7……"
    ),
    label_visibility="collapsed",
)

st.caption(
    "支持中文、英文、政策条款编号或年份搜索，也可以直接输入一个问题。。"
)
# =========================================================
# YEAR SNAPSHOT
# 当用户直接搜索年份时，
# 显示这一年有哪些重要 PPWR 规则变化
# =========================================================

def detect_year_query(query):
    """
    判断用户是否直接查询一个年份。
    支持：
    2030
    2030年
    """

    if not query:
        return None

    cleaned = query.strip()

    match = re.fullmatch(
        r"(20\d{2})年?",
        cleaned
    )

    if match:
        return match.group(1)

    return None


def collect_year_events(articles, year):
    """
    从所有核心条款中提取指定年份的政策事件。
    """

    events = []

    for article in articles:

        article_dates = format_dates(article)

        for item in article_dates:

            date_label = str(
                item.get("date", "")
            )

            event_text = str(
                item.get("event", "")
            )

            if year in date_label:

                events.append(
                    {
                        "article": article,
                        "date": date_label,
                        "event": event_text,
                        "conditional": (
                            "开始时间有条件" in date_label
                        ),
                    }
                )

    return events


def render_year_snapshot(articles, year):
    """
    将某一年的政策变化显示成用户容易理解的年度快照。
    """

    events = collect_year_events(
        articles,
        year
    )

    st.markdown("---")

    st.markdown(
        f"# {year} 年政策快照"
    )

    st.write(
        "快速查看这一年前后需要重点关注的 PPWR 规则变化。"
    )

    if not events:

        st.info(
            f"当前核心政策数据中没有找到 {year} 年的明确时间节点。"
        )

        st.caption(
            "这不代表这一年没有相关要求，"
            "你也可以尝试搜索具体主题或 Article 编号。"
        )

        return

    # 统计涉及多少个 Article
    article_keys = set()

    for item in events:

        article_key = get_article_key(
            item["article"]
        )

        if article_key:
            article_keys.add(
                article_key
            )

    conditional_count = sum(
        1
        for item in events
        if item["conditional"]
    )

    # ---------------------------------------------
    # 顶部概览
    # ---------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "关键变化",
            len(events)
        )

    with col2:
        st.metric(
            "涉及规则",
            len(article_keys)
        )

    with col3:
        st.metric(
            "条件生效",
            conditional_count
        )

    if conditional_count > 0:

        st.caption(
            "部分要求虽然已经写入 PPWR，"
            "但实际开始适用的时间还取决于后续法案何时出台。"
        )

    st.markdown(
        "### 重点事项"
    )

    # ---------------------------------------------
    # 逐项显示年度变化
    # ---------------------------------------------

    for item in events:

        article = item["article"]

        title = article.get(
            "title_cn",
            article.get(
                "title_en",
                "相关规则"
            )
        )

        article_label = article.get(
            "article",
            ""
        )

        event_text = item.get(
            "event",
            ""
        )

        user_question = get_user_question(
            article
        )

        article_key = get_article_key(
            article
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {title}"
            )

            if item["conditional"]:
                st.caption(
                    f"{article_label} · 条件生效"
                )
            else:
                st.caption(
                    f"{article_label} · {year}"
                )

            if event_text:
                st.markdown(
                    f"**发生什么？**  \n{event_text}"
                )

            st.markdown(
                f"**你可能关心：** {user_question}"
            )

            if article_key == "art6":

                st.info(
                    "需要判断具体包装吗？"
                    "请进入左侧「包装可回收性分析」。"
                )

            elif article_key == "art7":

                st.info(
                    "需要判断具体再生含量吗？"
                    "请进入左侧「再生含量情景分析」。"
                )

    st.caption(
        "以上仅汇总当前工具已收录的 PPWR 核心条款，"
        "不代表法规全文的全部时间节点。"
    )
# =========================================================
# QUICK FIND RESULTS
# =========================================================

if quick_query:

    # ---------------------------------------------
    # 情况 1：用户直接搜索年份
    # ---------------------------------------------
    year_query = detect_year_query(
        quick_query
    )

    if year_query:

        render_year_snapshot(
            articles,
            year_query
        )

    # ---------------------------------------------
    # 情况 2：普通关键词 / 问题 / Article 搜索
    # ---------------------------------------------
    else:

        quick_results = search_articles(
            articles,
            quick_query
        )

        if not quick_results:

            st.warning(
                "暂时没有找到直接相关的核心规则。"
            )

            st.caption(
                "可以尝试更简单的关键词，例如："
                "「再生塑料」「2030」「可回收性」"
                "「复用」「标签」。"
            )

        else:

            st.markdown("---")

            st.markdown(
                f"### 找到 {len(quick_results)} 项相关规则"
            )

            st.caption(
                "已按与你搜索内容的相关程度排序。"
            )

            # 最相关结果
            primary_result = (
                quick_results[0]["article"]
            )

            render_answer_card(
                primary_result,
                rank=1,
                query=quick_query,
                is_primary=True,
            )

            # 其他相关结果
            if len(quick_results) > 1:

                st.markdown(
                    "### 你还可以看看"
                )

                for index, item in enumerate(
                    quick_results[1:5],
                    start=2
                ):

                    render_answer_card(
                        item["article"],
                        rank=index,
                        query=quick_query,
                        is_primary=False,
                    )
# =========================================================
# YEAR SNAPSHOT
# 当用户搜索一个年份时，不再只返回 Article 列表，
# 而是直接告诉用户这一年有哪些重要政策变化。
# =========================================================

def detect_year_query(query):
    """
    判断用户是不是在直接查询一个年份。
    支持：
    2030
    2030年
    """
    if not query:
        return None

    cleaned = query.strip()

    match = re.fullmatch(
        r"(20\d{2})年?",
        cleaned
    )

    if match:
        return match.group(1)

    return None


def collect_year_events(articles, year):
    """
    从所有 Article 的 dates 字段中提取某一年的事件。
    """
    events = []

    for article in articles:

        article_dates = format_dates(article)

        for item in article_dates:

            date_label = str(
                item.get("date", "")
            )

            event_text = str(
                item.get("event", "")
            )

            if year in date_label:

                events.append(
                    {
                        "article": article,
                        "date": date_label,
                        "event": event_text,
                        "conditional": (
                            "条件生效" in date_label
                        ),
                    }
                )

    return events


def render_year_snapshot(
    articles,
    year
):
    """
    显示面向普通用户的年度政策快照。
    """

    events = collect_year_events(
        articles,
        year
    )

    st.markdown("---")

    st.markdown(
        f"# {year} 年需要关注什么"
    )

    st.write(
        "快速查看这一年前后需要重点关注的 PPWR 规则变化。"
    )

    if not events:

        st.info(
            f"当前核心政策数据中没有找到 {year} 年的明确时间节点。"
        )

        st.caption(
            "这不代表这一年没有相关要求，"
            "你也可以尝试搜索具体主题或 Article 编号。"
        )

        return

    # 去重统计 Article 数量
    article_keys = set()

    for item in events:
        article_keys.add(
            get_article_key(
                item["article"]
            )
        )

    conditional_count = sum(
        1
        for item in events
        if item["conditional"]
    )

    # 顶部三个简单指标
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "关键变化",
            len(events)
        )

    with col2:
        st.metric(
            "涉及条款",
            len(article_keys)
        )

    with col3:
        st.metric(
            "生效时间有条件",
            conditional_count
        )

    st.caption(
        "“条件生效”表示法规已经确定方向，"
        "但实际起始时间仍受后续法案发布时间影响。"
    )

    st.markdown("### 重点变化")

    for number, item in enumerate(
        events,
        start=1
    ):

        article = item["article"]

        title = article.get(
            "title_cn",
            article.get(
                "title_en",
                "相关规则"
            )
        )

        article_label = article.get(
            "article",
            ""
        )

        event_text = item["event"]

        date_label = item["date"]

        user_question = get_user_question(
            article
        )

        with st.container(border=True):

            col_left, col_right = st.columns(
                [5, 1.4]
            )

            with col_left:

                st.markdown(
                    f"### {title}"
                )

                st.caption(
                    article_label
                )

            with col_right:

                if item["conditional"]:
                    st.markdown(
                        "**条件生效**"
                    )
                else:
                    st.markdown(
                        f"**{year}**"
                    )

            st.markdown(
                f"**重点变化：** {event_text}"
            )

            st.caption(
                f"你可能关心：{user_question}"
            )

            article_key = get_article_key(
                article
            )

            if article_key == "art6":
                st.info(
                    "需要判断具体包装吗？"
                    "请进入左侧「包装可回收性分析」。"
                )

            elif article_key == "art7":

                st.info(
                    "需要计算具体再生含量吗？"
                    "请进入左侧「再生含量情景分析」。"
                )

    st.caption(
        "以上内容来自当前 Navigator 已收录的 PPWR 核心条款，"
        "并非对法规全文所有日期的穷尽式检索。"
    )

# =========================================================
# PANORAMA MAP
# =========================================================

st.divider()

st.subheader("PPWR 实施全景")

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
            "重复使用、EPR、标签、减量..."
        )
    )


with path_col:

    selected_path = st.selectbox(
        "实施路径",
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