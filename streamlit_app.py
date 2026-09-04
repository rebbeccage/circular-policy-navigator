import streamlit as st
import yaml


# ============================================================
# 1. 页面设置
# ============================================================

st.set_page_config(
    page_title="Circular Policy Navigator",
    page_icon="🧭",
    layout="wide"
)


# ============================================================
# 2. 读取 PPWR 数据
# ============================================================

@st.cache_data
def load_policy():
    with open("data/ppwr.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


data = load_policy()

policy = data["policy"]
article = data["article_7"]


# ============================================================
# 3. 页面标题
# ============================================================

st.title("Circular Policy Navigator")

st.caption(
    "将复杂循环经济政策转化为结构化要求、关键节点与行动路径"
)

st.divider()


# ============================================================
# 4. PPWR 概览
# ============================================================

st.subheader("PPWR · Policy Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "政策",
        policy["short_name"]
    )

with col2:
    st.metric(
        "法域",
        policy["jurisdiction"]
    )

with col3:
    st.metric(
        "开始适用",
        policy["application_date"]
    )

with col4:
    st.metric(
        "状态",
        policy["status"]
    )


st.info(
    f'**{article["article"]} · {article["title_cn"]}**\n\n'
    f'{article["core_message"]}'
)


# ============================================================
# 5. 用户选择情景
# ============================================================

st.subheader("① 选择你的政策情景")

left, right = st.columns(2)


# 包装类型
category_options = {
    value["label"]: key
    for key, value in article["categories"].items()
}

with left:
    selected_category_label = st.selectbox(
        "你的塑料包装属于哪一类？",
        list(category_options.keys())
    )


# 再生材料来源
source_options = {
    value["label"]: key
    for key, value in article["source_routes"].items()
}

with right:
    selected_source_label = st.radio(
        "再生塑料来自哪里？",
        list(source_options.keys())
    )


category_key = category_options[selected_category_label]
source_key = source_options[selected_source_label]

category = article["categories"][category_key]
source = article["source_routes"][source_key]


# ============================================================
# 6. 自动生成政策结果
# ============================================================

st.divider()

st.subheader("② 政策要求")

result1, result2, result3 = st.columns(3)


with result1:
    st.metric(
        "2030最低再生含量",
        f'{category["target_2030"]}%'
    )
    st.caption(
        f'法律依据：{category["basis_2030"]}'
    )


with result2:
    st.metric(
        "2040最低再生含量",
        f'{category["target_2040"]}%'
    )
    st.caption(
        f'法律依据：{category["basis_2040"]}'
    )


with result3:
    st.metric(
        "核算边界",
        "生产厂 × 年度"
    )
    st.caption(
        "按包装类型和形式计算"
    )


st.write(
    f'**当前选择：** {category["label"]}'
)

st.caption(
    category["note"]
)


# ============================================================
# 7. 核算逻辑
# ============================================================

st.subheader("③ 如何核算？")

calc1, calc2 = st.columns(2)


with calc1:

    st.markdown("#### 核算对象")

    st.write(
        article["calculation"]["material"]
    )

    st.markdown("#### 核算方式")

    st.write(
        article["calculation"]["basis"]
    )


with calc2:

    st.markdown("#### 合规责任主体")

    st.write(
        article["calculation"]["compliance_actor"]
    )

    st.markdown("#### 合规证明")

    st.write(
        article["calculation"]["evidence"]
    )


# ============================================================
# 8. 材料来源要求
# ============================================================

st.subheader("④ 再生材料来源要求")

if source_key == "third_country":

    st.warning(
        "你选择的是第三国来源再生塑料：除再生含量目标外，"
        "还需要关注收集、再生以及等效性核验要求。"
    )

else:

    st.success(
        "你选择的是欧盟境内来源再生塑料。"
    )


st.write(
    source["summary"]
)


for condition in source["conditions"]:

    st.write(
        f"• {condition}"
    )


# ============================================================
# 9. 简化政策路径图
# ============================================================

st.subheader("⑤ Policy Path")

path1, path2, path3, path4, path5 = st.columns(5)


with path1:
    st.markdown(
        """
        ### 1
        **PPWR**

        Article 7
        """
    )


with path2:
    st.markdown(
        f"""
        ### 2
        **包装类型**

        {category["label"]}
        """
    )


with path3:
    st.markdown(
        f"""
        ### 3
        **2030目标**

        **{category["target_2030"]}%**
        """
    )


with path4:
    st.markdown(
        f"""
        ### 4
        **材料来源**

        {source["label"]}
        """
    )


with path5:

    if source_key == "third_country":

        st.markdown(
            """
            ### 5
            **额外关注**

            第三国等效性
            """
        )

    else:

        st.markdown(
            """
            ### 5
            **合规证明**

            Technical documentation
            """
        )


st.caption(
    "PPWR → 包装类型 → 再生含量目标 → 材料来源 → 合规要求"
)


# ============================================================
# 10. 时间线
# ============================================================

st.subheader("⑥ 关键时间节点")


for event in article["timeline"]:

    date_col, event_col = st.columns(
        [1, 4]
    )

    with date_col:

        st.markdown(
            f'**{event["date"]}**'
        )

    with event_col:

        st.write(
            event["title"]
        )


# ============================================================
# 11. Pending Rules
# ============================================================

st.subheader("⑦ 尚待落地的规则")


for rule in article["pending_rules"]:

    with st.expander(
        f'{rule["item"]} · {rule["basis"]}'
    ):

        st.write(
            f'截止日期：{rule["date"]}'
        )

        st.write(
            f'数据库状态：{rule["status"]}'
        )


# ============================================================
# 12. Action Checklist
# ============================================================

st.subheader("⑧ Action Checklist")

st.caption(
    "将政策要求转换为实际准备事项。当前版本为政策研究工具，不替代法律意见。"
)


actions = list(
    article["actions"]["general"]
)


if source_key == "third_country":

    actions += article["actions"]["third_country"]


for index, action in enumerate(actions):

    st.checkbox(
        action,
        key=f"action_{index}_{source_key}"
    )


# ============================================================
# 13. 法律依据
# ============================================================

with st.expander(
    "查看法律依据与数据说明"
):

    st.write(
        f'法规：{policy["full_name"]}'
    )

    st.write(
        f'CELEX：{policy["celex"]}'
    )

    st.write(
        f'分析条款：{article["article"]}'
    )

    st.write(
        f'数据更新时间：{policy["status_as_of"]}'
    )

    st.write(
        "当前原型聚焦PPWR Article 7。"
        "后续实施法案出台后，需要同步更新数据库。"
    )


st.divider()

st.caption(
    "Circular Policy Navigator · PPWR Prototype v0.2"
)