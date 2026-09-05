import streamlit as st
import yaml


# =========================================================
# 页面设置
# =========================================================

st.set_page_config(
    page_title="PPWR 实施进展",
    page_icon="📌",
    layout="wide",
)


# =========================================================
# 读取现有 PPWR 核心数据
# =========================================================

@st.cache_data
def load_ppwr_core():

    with open(
        "data/ppwr_core.yaml",
        "r",
        encoding="utf-8"
    ) as file:

        data = yaml.safe_load(file)

    if isinstance(data, dict):
        if "articles" in data:
            return data["articles"]

    return data or []


articles = load_ppwr_core()


# =========================================================
# 辅助函数
# =========================================================

def normalize_articles(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        result = []

        for key, value in data.items():

            if isinstance(value, dict):

                item = value.copy()

                if "id" not in item:
                    item["id"] = key

                result.append(item)

        return result

    return []


def text_value(value):

    if value is None:
        return ""

    if isinstance(value, list):
        return "、".join(
            str(item)
            for item in value
        )

    return str(value)


def classify_status(article):

    status = text_value(
        article.get("status")
    ).lower()

    dependencies = article.get(
        "dependencies"
    )

    if dependencies:
        return "配套规则待完善"

    if any(
        word in status
        for word in [
            "待",
            "pending",
            "后续",
            "implementing",
            "delegated",
        ]
    ):
        return "配套规则待完善"

    if any(
        word in status
        for word in [
            "条件",
            "later",
            "whichever",
        ]
    ):
        return "起始时间有条件"

    return "法规要求已明确"

def collect_timeline_events(article_list):
    """
    从所有核心规则的 dates 字段中提取时间节点，
    并按年份整理。
    """

    import re

    events = []

    for article in article_list:

        article_label = article.get(
            "article",
            ""
        )

        title = article.get(
            "title_cn",
            article.get(
                "title_en",
                "相关规则"
            )
        )

        theme = article.get(
            "theme",
            ""
        )

        status = classify_status(
            article
        )

        dates = article.get(
            "dates",
            []
        )

        if not isinstance(
            dates,
            list
        ):
            continue

        for item in dates:

            if not isinstance(
                item,
                dict
            ):
                continue

            date_label = str(
                item.get(
                    "date",
                    ""
                )
            )

            event = item.get(
                "event",
                ""
            )

            if not date_label or not event:
                continue

            year_match = re.search(
                r"20\d{2}",
                date_label
            )

            if not year_match:
                continue

            year = int(
                year_match.group()
            )

            events.append(
                {
                    "year": year,
                    "date": date_label,
                    "event": event,
                    "article": article_label,
                    "title": title,
                    "theme": theme,
                    "status": status,
                }
            )

    return sorted(
        events,
        key=lambda item: item["year"]
    )
article_list = normalize_articles(
    articles
)
timeline_events = collect_timeline_events(
    article_list
)

# =========================================================
# 页面标题
# =========================================================

st.title(
    "PPWR 实施进展"
)
theme_options = [
    "全部",
    "可回收性",
    "再生含量",
    "EPR",
    "非欧盟材料与等效认定",
    "配套法案与方法",
]

selected_theme = st.selectbox(
    "关注主题",
    theme_options,
    index=0
)
# =========================================================
# 根据研究主题筛选时间节点
# =========================================================

# 默认显示全部时间节点
filtered_events = timeline_events

# 只有用户选择了具体主题时，才进行筛选
if selected_theme != "全部":

    filtered_events = []

    for item in timeline_events:

        searchable_text = (
            str(item.get("title", ""))
            + " "
            + str(item.get("theme", ""))
            + " "
            + str(item.get("event", ""))
            + " "
            + str(item.get("article", ""))
        ).lower()


        # -------------------------------------------------
        # 生产者责任延伸（EPR）
        # -------------------------------------------------

        if selected_theme == "生产者责任延伸（EPR）":

            if (
                "epr" in searchable_text
                or "生产者责任" in searchable_text
                or "延伸生产者责任" in searchable_text
            ):
                filtered_events.append(
                    item
                )


        # -------------------------------------------------
        # 非欧盟材料与等效认定
        # -------------------------------------------------

        elif selected_theme == "非欧盟材料与等效认定":

            if (
                "第三国" in searchable_text
                or "非欧盟" in searchable_text
                or "等效" in searchable_text
                or "third country" in searchable_text
                or "third-country" in searchable_text
                or "equivalence" in searchable_text
            ):
                filtered_events.append(
                    item
                )


        # -------------------------------------------------
        # 配套法案与方法
        # -------------------------------------------------

        elif selected_theme == "配套法案与方法":

            if (
                "方法" in searchable_text
                or "计算" in searchable_text
                or "核验" in searchable_text
                or "认证" in searchable_text
                or "授权法案" in searchable_text
                or "实施法案" in searchable_text
                or "delegated" in searchable_text
                or "implementing" in searchable_text
            ):
                filtered_events.append(
                    item
                )


        # -------------------------------------------------
        # 可回收性
        # -------------------------------------------------

        elif selected_theme == "可回收性":

            if (
                "可回收" in searchable_text
                or "recyclab" in searchable_text
                or "回收设计" in searchable_text
                or "规模化回收" in searchable_text
            ):
                filtered_events.append(
                    item
                )


        # -------------------------------------------------
        # 再生含量
        # -------------------------------------------------

        elif selected_theme == "再生含量":

            if (
                "再生含量" in searchable_text
                or "再生料" in searchable_text
                or "再生材料" in searchable_text
                or "再生塑料" in searchable_text
                or "recycled content" in searchable_text
                or "recycled plastic" in searchable_text
            ):
                filtered_events.append(
                    item
                )

st.write(
    "集中查看 PPWR 核心规则目前推进到什么程度，"
    "以及还需关注哪些配套规则和关键时间。"
)
from collections import defaultdict


events_by_year = defaultdict(list)

for item in filtered_events:

    events_by_year[
        item["year"]
    ].append(item)


timeline_years = sorted(
    events_by_year.keys()
)
if timeline_years:

    timeline_html = """
    <style>
    .ppwr-timeline {
        display: flex;
        overflow-x: auto;
        padding: 24px 4px 18px 4px;
        margin-bottom: 8px;
    }

    .ppwr-timeline-item {
        position: relative;
        min-width: 175px;
        padding-right: 22px;
    }

    .ppwr-timeline-line {
        position: absolute;
        top: 14px;
        left: 15px;
        right: 0;
        height: 2px;
        background: #CBD5E1;
    }

    .ppwr-timeline-dot {
        position: relative;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #31597C;
        margin-top: 9px;
        margin-bottom: 14px;
        z-index: 2;
    }

    .ppwr-timeline-year {
        font-size: 1.15rem;
        font-weight: 700;
        color: #17212B;
        margin-bottom: 7px;
    }

    .ppwr-timeline-event {
        font-size: 0.88rem;
        line-height: 1.45;
        color: #475569;
        margin-bottom: 4px;
    }
    </style>

    <div class="ppwr-timeline">
    """

    for year in timeline_years:

        year_events = events_by_year[
            year
        ]

        timeline_html += (
            '<div class="ppwr-timeline-item">'
        )

        timeline_html += (
            '<div class="ppwr-timeline-line"></div>'
        )

        timeline_html += (
            '<div class="ppwr-timeline-dot"></div>'
        )

        timeline_html += (
            f'<div class="ppwr-timeline-year">'
            f'{year}'
            f'</div>'
        )

        # 时间轴上只显示前两个事件，避免文字过多
        for item in year_events[:2]:

            event_text = str(
                item["event"]
            )

            if len(event_text) > 28:
                event_text = (
                    event_text[:28]
                    + "…"
                )

            timeline_html += (
                '<div class="ppwr-timeline-event">'
                + event_text
                + '</div>'
            )

        if len(year_events) > 2:

            timeline_html += (
                '<div class="ppwr-timeline-event">'
                f'另有 {len(year_events) - 2} 项'
                '</div>'
            )

        timeline_html += "</div>"

    timeline_html += "</div>"

    st.html(
        timeline_html
    )

else:

    st.info(
        "当前筛选条件下没有找到明确的时间节点。"
    )
if timeline_years:

    selected_year = st.selectbox(
        "查看年份",
        timeline_years,
        index=0
    )

    st.subheader(
        f"{selected_year} 年需要关注什么？"
    )

    selected_events = events_by_year[
        selected_year
    ]

    for item in selected_events:

        with st.container(
            border=True
        ):

            st.markdown(
                f"**{item['title']}**"
            )

            if item.get("article"):

                st.caption(
                    item["article"]
                )

            st.write(
                item["event"]
            )

            if item.get("status"):

                st.caption(
                    f"目前进展：{item['status']}"
                )

# =========================================================
# 顶部概览
# =========================================================

confirmed = []
pending = []
conditional = []

for article in article_list:

    category = classify_status(
        article
    )

    if category == "法规要求已明确":
        confirmed.append(article)

    elif category == "配套规则待完善":
        pending.append(article)

    elif category == "起始时间有条件":
        conditional.append(article)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "法规要求已明确",
        len(confirmed)
    )

with col2:
    st.metric(
        "配套规则待完善",
        len(pending)
    )

with col3:
    st.metric(
        "起始时间有条件",
        len(conditional)
    )


st.divider()


# =========================================================
# 重点研究主题
# =========================================================

st.subheader(
    "重点关注"
)

st.caption(
    "优先查看当前研究中影响较大的实施问题。"
)

focus_topics = [
    "再生含量",
    "第三国等效",
    "生产者责任延伸（EPR）",
    "可回收性",
    "计算和核验方法",
]

cols = st.columns(
    len(focus_topics)
)

for col, topic in zip(
    cols,
    focus_topics
):

    with col:
        st.markdown(
            f"**{topic}**"
        )


st.divider()


# =========================================================
# 待完善规则
# =========================================================

st.subheader(
    "还需关注的配套规则"
)

if not pending:

    st.info(
        "当前数据中还没有单独标记需要跟踪的配套规则。"
    )

else:

    for article in pending:

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

        status = text_value(
            article.get("status")
        )

        dates = article.get(
            "dates",
            []
        )

        dependencies = article.get(
            "dependencies"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {title}"
            )

            if article_label:
                st.caption(
                    article_label
                )

            if status:
                st.markdown(
                    "**目前进展**"
                )

                st.write(
                    status
                )

            if dependencies:

                st.markdown(
                    "**还需关注的配套规则**"
                )

                if isinstance(
                    dependencies,
                    list
                ):

                    for item in dependencies:

                        if isinstance(
                            item,
                            dict
                        ):

                            dep_title = item.get(
                                "title",
                                ""
                            )

                            dep_date = item.get(
                                "date",
                                ""
                            )

                            dep_summary = item.get(
                                "summary",
                                ""
                            )

                            if dep_title:
                                st.markdown(
                                    f"**{dep_title}**"
                                )

                            if dep_date:
                                st.caption(
                                    f"时间：{dep_date}"
                                )

                            if dep_summary:
                                st.write(
                                    dep_summary
                                )

                        else:
                            st.write(
                                f"• {item}"
                            )

                else:
                    st.write(
                        dependencies
                    )

            if dates:

                with st.expander(
                    "查看关键时间"
                ):

                    for item in dates:

                        if isinstance(
                            item,
                            dict
                        ):

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
                                    f"**{date_label}**"
                                )

                            if event:
                                st.write(
                                    event
                                )


st.divider()


# =========================================================
# 全部核心规则
# =========================================================

st.subheader(
    "全部核心规则"
)

for article in article_list:

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

    category = classify_status(
        article
    )

    with st.expander(
        f"{title} · {article_label}"
    ):

        st.markdown(
            f"**目前进展：** {category}"
        )

        status = text_value(
            article.get("status")
        )

        if status:
            st.write(
                status
            )