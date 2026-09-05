import streamlit as st
from datetime import datetime

from const import HIDE_ST_STYLE


# ==============================
# ページ設定
# ==============================

st.set_page_config(
    page_title="お題箱",
    page_icon="📮",
    layout="centered",
)

# const.py のCSSを読み込み
st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


# ==============================
# データ
# ==============================

if "topics" not in st.session_state:
    st.session_state.topics = []


# ==============================
# タイトル
# ==============================

st.title("📮 お題箱")

st.write("みんなでお題を投稿しよう！")
st.write("投稿されたお題は、みんなが見ることができます。")


# ==============================
# 投稿フォーム
# ==============================

st.subheader("✏️ お題を投稿")

with st.form("topic_form"):

    topic = st.text_area(
        "お題",
        placeholder="例：最近ハマっているゲームを教えて！",
        max_chars=500,
    )

    submit = st.form_submit_button(
        "📮 投稿する",
        use_container_width=True,
    )


# ==============================
# 投稿処理
# ==============================

if submit:

    topic = topic.strip()

    if topic == "":
        st.error("お題を入力してください。")

    else:
        new_topic = {
            "text": topic,
            "date": datetime.now().strftime("%Y/%m/%d %H:%M"),
        }

        st.session_state.topics.insert(0, new_topic)

        st.success("お題を投稿しました！")

        # 画面を更新
        st.rerun()


# ==============================
# お題一覧
# ==============================

st.divider()

st.subheader(
    f"📋 みんなのお題（{len(st.session_state.topics)}件）"
)


if len(st.session_state.topics) == 0:

    st.info("まだお題がありません。")


else:

    for index, topic in enumerate(st.session_state.topics):

        with st.container(border=True):

            st.write(f"### 📮 お題 #{len(st.session_state.topics) - index}")

            st.write(topic["text"])

            st.caption(
                f"投稿日時：{topic['date']}"
            )