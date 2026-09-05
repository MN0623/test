import sqlite3
from datetime import datetime

import streamlit as st

from const import HIDE_ST_STYLE


# ==========================================
# 設定
# ==========================================

DB_FILE = "topics.db"


# ==========================================
# ページ設定
# ==========================================

st.set_page_config(
    page_title="お題箱",
    page_icon="📮",
    layout="centered",
)

# const.py のCSSを反映
st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)


# ==========================================
# データベース
# ==========================================

def get_connection():
    """SQLiteに接続する"""
    conn = sqlite3.connect(
        DB_FILE,
        timeout=10,
    )

    conn.row_factory = sqlite3.Row

    # 複数アクセス時の安定性を上げる
    conn.execute("PRAGMA journal_mode=WAL")

    return conn


def init_db():
    """テーブルを作成する"""
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def get_topics():
    """お題を取得する"""
    conn = get_connection()

    topics = conn.execute(
        """
        SELECT id, text, created_at
        FROM topics
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return topics


def add_topic(text):
    """お題を追加する"""
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO topics (text, created_at)
        VALUES (?, ?)
        """,
        (
            text,
            datetime.now().strftime("%Y/%m/%d %H:%M"),
        ),
    )

    conn.commit()
    conn.close()


def delete_topic(topic_id):
    """お題を削除する"""
    conn = get_connection()

    conn.execute(
        """
        DELETE FROM topics
        WHERE id = ?
        """,
        (topic_id,),
    )

    conn.commit()
    conn.close()


# アプリ起動時にDBを初期化
init_db()


# ==========================================
# お題一覧を表示する部分
# ==========================================

@st.fragment(run_every="3s")
def topic_list():

    topics = get_topics()

    st.subheader(
        f"📋 みんなのお題（{len(topics)}件）"
    )

    if not topics:
        st.info(
            "まだお題がありません。\n\n"
            "最初のお題を投稿してみよう！"
        )
        return

    for topic in topics:

        with st.container(border=True):

            # お題
            st.markdown(
                f"### 📮 お題 #{topic['id']}"
            )

            st.write(topic["text"])

            # 投稿日時
            st.caption(
                f"投稿日時：{topic['created_at']}"
            )

            # 削除ボタン
            if st.button(
                "🗑️ このお題を削除",
                key=f"delete_{topic['id']}",
                use_container_width=True,
            ):
                delete_topic(topic["id"])

                st.toast("お題を削除しました")

                # 一覧を即時更新
                st.rerun(scope="fragment")


# ==========================================
# タイトル
# ==========================================

st.title("📮 お題箱")

st.write(
    "みんなでお題を投稿しよう！"
)

st.caption(
    "投稿されたお題はみんなで見ることができます。"
)


# ==========================================
# 投稿フォーム
# ==========================================

st.subheader("✏️ お題を投稿")

with st.form(
    "topic_form",
    clear_on_submit=True,
):

    topic = st.text_area(
        "お題",
        placeholder="例：最近ハマっているゲームを教えて！",
        max_chars=500,
        height=120,
    )

    submit = st.form_submit_button(
        "📮 投稿する",
        use_container_width=True,
    )


# ==========================================
# 投稿処理
# ==========================================

if submit:

    topic = topic.strip()

    if not topic:

        st.error(
            "お題を入力してください。"
        )

    else:

        add_topic(topic)

        st.success(
            "お題を投稿しました！"
        )

        st.rerun()


# ==========================================
# お題一覧
# ==========================================

st.divider()

topic_list()


# ==========================================
# フッター
# ==========================================

st.divider()

st.caption(
    "📮 みんなのお題箱"
)
