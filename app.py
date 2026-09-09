import streamlit as st
import cv2
import numpy as np

# tu.py と demo.py を無変更でインポート
from tu import STEPS, OrigamiTutor
import demo

# Streamlit ページ設定
st.set_page_config(page_title="折り紙チューター：ハート", layout="wide")

# ---------------------------------------------------------
# セッション状態の初期化 (tu.pyのOrigamiTutorを保持)
# ---------------------------------------------------------
if "tutor" not in st.session_state:
    st.session_state.tutor = OrigamiTutor(STEPS)

tutor = st.session_state.tutor

# ---------------------------------------------------------
# ヘッダー表示
# ---------------------------------------------------------
st.title("折り紙チューター：ハートの折り方")

# 完了時の表示
if tutor.is_finished():
    st.balloons()
    st.success("🎉 おめでとうございます！ハートの折り紙が完成しました！")
    if st.button("最初からやり直す"):
        st.session_state.tutor = OrigamiTutor(STEPS)
        st.rerun()

else:
    current_step_data = tutor.get_current_step()
    step_num = tutor.get_current_step_number()
    instruction = current_step_data["instruction"]
    total_steps = len(STEPS)

    st.subheader(f"Step {step_num} / {total_steps}")
    st.info(f"**指示:** {instruction}")

    col1, col2 = st.columns([1, 1])

    # ---------------------------------------------------------
    # 左カラム: カメラ入力とCV判定
    # ---------------------------------------------------------
    with col1:
        st.write("### リアルタイム判定")
        img_file = st.camera_input("現在の折った状態を撮影してください")

        if img_file is not None:
            # カメラ画像を OpenCV 形式 (BGR) に変換
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # -------------------------------------------------
            # demo.py の判定ロジック呼び出し
            # ※ demo.py の実際の判定関数に合わせて書き換えてください
            # 例: check_origami(frame, step_num) / check_step(frame, step_num) など
            # -------------------------------------------------
            try:
                # 画面から取得した画像(frame)とステップ番号(step_num)をdemo.pyに送る
                is_correct = demo.check_origami(frame, step_num)
            except AttributeError:
                # demo.py 内の関数名が不一致の場合の仮処理
                st.warning("`demo.py` 内の判定関数名を確認してください。")
                is_correct = False

            # 判定結果を表示
            if is_correct:
                st.success("⭕ 正しく折れています！")
                if st.button("次のステップへ進む"):
                    tutor.receive_cv_result(True)
                    st.rerun()
            else:
                st.error("❌ まだ正しく折れていないようです。もう一度確認してください。")

    # ---------------------------------------------------------
    # 右カラム: 手動コントロール (テスト・スキップ用)
    # ---------------------------------------------------------
    with col2:
        st.write("### 手動コントロール")
        st.write(f"現在のステップインデックス: {tutor.current_step}")

        if st.button("強制的に次のステップへ"):
            tutor.next_step()
            st.rerun()

        if st.button("前のステップに戻る"):
            if tutor.current_step > 0:
                tutor.current_step -= 1
                tutor.finished = False
                st.rerun()
