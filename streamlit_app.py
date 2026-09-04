import streamlit as st

st.set_page_config(
    page_title="Policy Navigator",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #172421;
        --muted: #6a7772;
        --paper: #f5f6f0;
        --panel: #ffffff;
        --line: #dce2d9;
        --mint: #cbe8d7;
        --green: #1f6b4f;
        --orange: #e77943;
        --soft-orange: #fff0e7;
    }

    .stApp { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #e8eee5;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    .block-container { max-width: 1380px; padding: 2.2rem 3.5rem 4rem; }
    .stMarkdown, .stTextInput, .stSelectbox, .stButton { font-family: 'Manrope', sans-serif; }
    h1, h2, h3, p { font-family: 'Manrope', sans-serif; }
    h1 { letter-spacing: -0.045em; line-height: 0.98; }
    h2 { letter-spacing: -0.03em; }
    .eyebrow, .mono, .metric-label, .tag { font-family: 'DM Mono', monospace; text-transform: uppercase; letter-spacing: 0.08em; }
    .eyebrow { color: var(--green); font-size: 0.72rem; font-weight: 500; margin-bottom: 1.25rem; }
    .hero { padding: 1.5rem 0 2rem; }
    .hero h1 { font-size: clamp(3.3rem, 6vw, 6.7rem); max-width: 850px; margin: 0 0 1.4rem; color: var(--ink); }
    .hero-copy { max-width: 570px; color: var(--muted); font-size: 1.05rem; line-height: 1.6; }
    .hero-mark { color: var(--orange); }
    .section-rule { border-top: 1px solid var(--line); margin: 1rem 0 2.2rem; }
    .section-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 1rem; }
    .section-note { color: var(--muted); font-size: 0.9rem; margin-top: -0.65rem; margin-bottom: 1.4rem; }
    .policy-card { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 1.45rem; min-height: 220px; position: relative; overflow: hidden; }
    .policy-card:after { content: ''; position: absolute; width: 80px; height: 80px; border: 1px solid var(--mint); border-radius: 50%; right: -25px; bottom: -28px; }
    .tag { display: inline-block; color: var(--green); background: var(--mint); border-radius: 2px; padding: 0.35rem 0.5rem; font-size: 0.63rem; }
    .policy-card h3 { font-size: 1.2rem; margin: 1rem 0 0.65rem; }
    .policy-card p { color: var(--muted); line-height: 1.55; font-size: 0.88rem; margin-bottom: 1.1rem; }
    .card-meta { color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.68rem; }
    .path-wrap { background: var(--ink); color: white; border-radius: 3px; padding: 1.6rem 1.8rem 1.8rem; margin-top: 2.5rem; }
    .path-wrap .section-title { color: white; }
    .path-wrap .section-note { color: #aabbb2; }
    .path-step { border-top: 1px solid #45554e; padding-top: 1rem; min-height: 135px; }
    .path-number { color: var(--orange); font-family: 'DM Mono', monospace; font-size: 0.75rem; }
    .path-step h3 { color: white; font-size: 1rem; margin: 0.7rem 0 0.45rem; }
    .path-step p { color: #aabbb2; font-size: 0.8rem; line-height: 1.5; }
    .metric-strip { display: flex; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 1.4rem 0; margin: 0.5rem 0 2.6rem; }
    .metric { flex: 1; border-right: 1px solid var(--line); padding-left: 1.3rem; }
    .metric:first-child { padding-left: 0; }
    .metric:last-child { border-right: none; }
    .metric-value { font-size: 1.7rem; font-weight: 700; letter-spacing: -0.04em; }
    .metric-label { color: var(--muted); font-size: 0.62rem; margin-top: 0.25rem; }
    .side-brand { color: var(--ink); font-family: 'Manrope', sans-serif; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.03em; padding: 0 1rem 2.3rem; }
    .side-brand span { color: var(--orange); }
    .side-caption { color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.65rem; line-height: 1.5; padding: 2rem 1rem 0; border-top: 1px solid #d3dcd1; }
    .stButton > button { border: 1px solid var(--line); background: transparent; border-radius: 2px; color: var(--ink); font-size: 0.78rem; }
    .stButton > button:hover { border-color: var(--green); color: var(--green); }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="side-brand">POLICY<span>•</span><br>NAVIGATOR</div>', unsafe_allow_html=True)
    st.radio("Explore", ["Overview", "Policy library", "Compare regions", "Action planner"], label_visibility="collapsed")
    st.markdown(
        '<div class="side-caption">A working index for people turning circular economy policy into practical decisions.<br><br>BUILD 01 / 2025</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="eyebrow">Circular economy intelligence / 01</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><h1>Make policy<br><span class="hero-mark">actionable.</span></h1><p class="hero-copy">A clear starting point for navigating the rules, signals and obligations shaping a circular economy.</p></div>',
    unsafe_allow_html=True,
)

query = st.text_input("Search the policy library", placeholder="Try: packaging waste, right to repair, textiles...", label_visibility="collapsed")

st.markdown(
    '<div class="metric-strip"><div class="metric"><div class="metric-value">48</div><div class="metric-label">Policies indexed</div></div><div class="metric"><div class="metric-value">12</div><div class="metric-label">Regions tracked</div></div><div class="metric"><div class="metric-value">06</div><div class="metric-label">Material systems</div></div><div class="metric"><div class="metric-value">2025</div><div class="metric-label">Latest update</div></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Start with a signal</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">The latest policy movements worth a closer look.</div>', unsafe_allow_html=True)

policies = [
    ("EUROPEAN UNION", "Packaging & Packaging Waste Regulation", "Recycled content, reuse targets and the redesign of packaging systems.", "In force · 2025"),
    ("UNITED KINGDOM", "Extended Producer Responsibility", "A shifting cost and data landscape for producers of packaging.", "Updated · 2024"),
    ("GLOBAL SIGNAL", "Right to Repair", "What repairability requirements mean for product teams and operators.", "Growing · 18 markets"),
]
if query:
    policies = [policy for policy in policies if query.lower() in " ".join(policy).lower()]

if policies:
    columns = st.columns(3, gap="medium")
    for column, (tag, title, description, meta) in zip(columns, policies):
        with column:
            st.markdown(
                f'<div class="policy-card"><span class="tag">{tag}</span><h3>{title}</h3><p>{description}</p><div class="card-meta">{meta} &nbsp; ↗</div></div>',
                unsafe_allow_html=True,
            )
else:
    st.info("No matching signals yet. Try a broader search term.")

st.markdown(
    '<div class="path-wrap"><div class="section-title">Your route through the policy landscape</div><div class="section-note">Move from the text of a policy to a confident next step.</div>',
    unsafe_allow_html=True,
)
path_columns = st.columns(3, gap="large")
for column, number, title, description in zip(
    path_columns,
    ["01", "02", "03"],
    ["Map the policy", "Read the impact", "Plan the response"],
    ["See the actors, materials and obligations in one view.", "Identify where requirements touch your operating model.", "Turn a regulatory signal into a practical workstream."],
):
    with column:
        st.markdown(f'<div class="path-step"><div class="path-number">{number}</div><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
