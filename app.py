import streamlit as st
import cv2
import numpy as np

# 1. 既存ファイルをそのままインポート
from tu import STEPS
import demo

# Streamlit の基本ページ設定
st.set_page_config(page_title="折り紙チューター：ハート", layout="wide")

# ---------------------------------------------------------
# セッション状態の初期化
# ---------------------------------------------------------
if "step_index" not in st.session_state:
    st.session_state.step_index = 0  # 0からスタート
if "is_finished" not in st.session_state:
    st.session_state.is_finished = False

# ---------------------------------------------------------
# サイドバー／ヘッダー表示
# ---------------------------------------------------------
st.title("折り紙チューター：ハートの折り方")

# 全ステップ数
total_steps = len(STEPS)

if st.session_state.is_finished:
    st.balloons()
    st.success("🎉 おめでとうございます！ハートの折り紙が完成しました！")
    if st.button("最初からやり直す"):
        st.session_state.step_index = 0
        st.session_state.is_finished = False
        st.rerun()
else:
    current_step_data = STEPS[st.session_state.step_index]
    step_num = current_step_data["step"]
    instruction = current_step_data["instruction"]

    st.subheader(f"Step {step_num} / {total_steps}")
    st.info(f"**指示:** {instruction}")

    col1, col2 = st.columns([1, 1])

    # ---------------------------------------------------------
    # 左カラム: カメラ入力と判定処理
    # ---------------------------------------------------------
    with col1:
        st.write("### リアルタイム判定")
        img_file = st.camera_input("現在の折った状態を撮影してください")

        if img_file is not None:
            # OpenCV 形式 (BGR) に変換
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # -------------------------------------------------
            # demo.py の判定処理を呼び出し
            # ※ demo.py 内の関数名・仕様に合わせて調整してください
            # 例: check_origami(frame, step_num) や main 処理等
            # -------------------------------------------------
            try:
                # demo.py の判定関数を実行 (例: check_step(frame, step_num))
                is_correct = demo.check_origami(frame, step_num)
            except AttributeError:
                # 関数名が異なる場合のフォールバック（画面上での手動スキップ等）
                st.warning("`demo.py` 内の判定関数の呼び出し名を確認してください。")
                is_correct = False

            # 判定結果に応じた表示とステップ更新
            if is_correct:
                st.success("⭕ 正しく折れています！")
                if st.button("次のステップへ進む"):
                    if st.session_state.step_index + 1 < total_steps:
                        st.session_state.step_index += 1
                    else:
                        st.session_state.is_finished = True
                    st.rerun()
            else:
                st.error("❌ まだ正しく折れていないようです。もう一度確認してください。")

    # ---------------------------------------------------------
    # 右カラム: 手動コントロール（テスト・デバッグ用）
    # ---------------------------------------------------------
    with col2:
        st.write("### 進捗コントロール")
        st.write(f"現在の内部インデックス: {st.session_state.step_index}")

        if st.button("強制的に次のステップへ"):
            if st.session_state.step_index + 1 < total_steps:
                st.session_state.step_index += 1
            else:
                st.session_state.is_finished = True
            st.rerun()

        if st.button("前のステップに戻る"):
            if st.session_state.step_index > 0:
                st.session_state.step_index -= 1
                st.session_state.is_finished = False
            st.rerun()
