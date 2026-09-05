import streamlit as st
from datetime import datetime
from const import HIDE_ST_STYLE


# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="お題箱",
    page_icon="📮",
    layout="centered",
)

# const.py のCSSを反映
st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


# =========================
# データ管理
# =========================

if "topics" not in st.session_state:
    st.session_state.topics = []


# =========================
# CSS
# =========================

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 2rem;
    }

    .topic-card {
        padding: 1.2rem;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        margin-bottom: 1rem;
        background-color: #ffffff;
    }

    .topic-number {
        color: #888;
        font-size: 0.8rem;
        margin-bottom: 0.4rem;
    }

    .topic-text {
        font-size: 1.1rem;
        line-height: 1.6;
    }

    .topic-date {
        color: #999;
        font-size: 0.75rem;
        margin-top: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# ヘッダー
# =========================

st.markdown(
    '<div class="title">お題箱</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">みんなでお題を投稿して、みんなで見よう！</div>',
    unsafe_allow_html=True,
)


# =========================
# お題投稿
# =========================

with st.form("topic_form", clear_on_submit=True):
    topic = st.text_area(
        "お題を入力",
        placeholder="例：最近ハマっていることを教えて！",
        height=120,
    )

    submitted = st.form_submit_button(
        "お題を投稿する",
        use_container_width=True,
    )

    if submitted:
        topic = topic.strip()

        if not topic:
            st.warning("お題を入力してください。")
        elif len(topic) > 500:
            st.warning("お題は500文字以内で入力してください。")
        else:
            st.session_state.topics.insert(
                0,
                {
                    "text": topic,
                    "created_at": datetime.now().strftime(
                        "%Y/%m/%d %H:%M"
                    ),
                },
            )

            st.success("お題を投稿しました！")


st.divider()


# =========================
# 投稿されたお題
# =========================

st.subheader(
    f"📋 投稿されたお題（{len(st.session_state.topics)}件）"
)


if not st.session_state.topics:
    st.info(
        "まだお題がありません。\n\n"
        "最初のお題を投稿してみよう！"
    )

else:
    for i, item in enumerate(st.session_state.topics, start=1):
        st.markdown(
            f"""
            <div class="topic-card">
                <div class="topic-number">
                    お題 #{len(st.session_state.topics) - i + 1}
                </div>

                <div class="topic-text">
                    {item["text"]}
                </div>

                <div class="topic-date">
                    投稿日時：{item["created_at"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================
# フッター
# =========================

st.divider()

st.caption("📮 みんなのお題箱")
