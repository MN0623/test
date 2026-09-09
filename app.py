# import streamlit as st
# import cv2
# import numpy as np
# from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
# import av

# from tu import STEPS, OrigamiTutor
# import demo

# st.set_page_config(page_title="折り紙チューター：ハート", layout="wide")

# # ---------------------------------------------------------
# # セッション状態の初期化
# # ---------------------------------------------------------
# if "tutor" not in st.session_state:
#     st.session_state.tutor = OrigamiTutor(STEPS)

# if "is_correct" not in st.session_state:
#     st.session_state.is_correct = False

# tutor = st.session_state.tutor

# st.title("折り紙チューター：ハートの折り方")

# # 完了時の表示
# if tutor.is_finished():
#     st.balloons()
#     st.success("🎉 おめでとうございます！ハートの折り紙が完成しました！")
#     if st.button("最初からやり直す"):
#         st.session_state.tutor = OrigamiTutor(STEPS)
#         st.session_state.is_correct = False
#         st.rerun()

# else:
#     current_step_data = tutor.get_current_step()
#     step_num = tutor.get_current_step_number()
#     instruction = current_step_data["instruction"]
#     total_steps = len(STEPS)

#     st.subheader(f"Step {step_num} / {total_steps}")
#     st.info(f"**指示:** {instruction}")

#     col1, col2 = st.columns([1, 1])

#     # ---------------------------------------------------------
#     # 左カラム: カメラ入力 (WebRTC) と CV判定
#     # ---------------------------------------------------------
#     with col1:

#         # 映像フレームを1コマずつ処理するクラス
#         class OrigamiProcessor(VideoTransformerBase):
#             def __init__(self):
#                 self.step_num = step_num

#             def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
#                 # WebRTC のフレームを OpenCV 形式 (BGR) に変換
#                 img = frame.to_ndarray(format="bgr24")

#                 # demo.py による判定
#                 try:
#                     is_ok = demo.check_origami(img, self.step_num)
#                 except Exception:
#                     is_ok = False

#                 # 結果を画面上の映像内に描画 (緑 = OK, 赤 = NG)
#                 color = (0, 255, 0) if is_ok else (0, 0, 255)
#                 text = f"Step {self.step_num}: {'OK' if is_ok else 'NG'}"
#                 cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

#                 return av.VideoFrame.from_ndarray(img, format="bgr24")

#         # WebRTC ストリーマーの起動
#         ctx = webrtc_streamer(
#             key=f"origami-step-{step_num}",  # ステップ切り替え時にリセットするためキーにステップ番号を含める
#             mode=WebRtcMode.SENDRECV,
#             video_processor_factory=OrigamiProcessor,
#             media_stream_constraints={
#             "video": {
#                 "width": {"ideal": 1280},
#                 "height": {"ideal": 720},
#                 "aspectRatio": {"ideal": 16 / 9},
#             },
#             async_processing=True,
#         )

#         # 判定が通った場合の進行用 UI
#         st.write("---")
#         if st.button("正しく折れたらここをクリックして次へ"):
#             tutor.receive_cv_result(True)
#             st.rerun()

#     # ---------------------------------------------------------
#     # 右カラム: 手動コントロール
#     # ---------------------------------------------------------
#     with col2:
#         st.write("### 手動コントロール")
#         st.write(f"現在のステップインデックス: {tutor.current_step}")

#         if st.button("強制的に次のステップへ"):
#             tutor.next_step()
#             st.rerun()

#         if st.button("前のステップに戻る"):
#             if tutor.current_step > 0:
#                 tutor.current_step -= 1
#                 tutor.finished = False
#                 st.rerun()

import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import av

from tu import STEPS, OrigamiTutor
import demo

st.set_page_config(page_title="折り紙チューター：ハート", layout="wide")

# ---------------------------------------------------------
# セッション状態の初期化
# ---------------------------------------------------------
if "tutor" not in st.session_state:
    st.session_state.tutor = OrigamiTutor(STEPS)

tutor = st.session_state.tutor

st.title("折り紙チューター：ハートの折り方")

# ---------------------------------------------------------
# 映像処理クラス (Step 番号を外部から変更可能にする)
# ---------------------------------------------------------
class OrigamiProcessor(VideoProcessorBase):
    def __init__(self):
        self.step_num = 1
        self.is_ok = False

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        # demo.py による判定
        try:
            self.is_ok = demo.check_origami(img, self.step_num)
        except Exception:
            self.is_ok = False

        # 結果を映像内に描画
        color = (0, 255, 0) if self.is_ok else (0, 0, 255)
        text = f"Step {self.step_num}: {'OK' if self.is_ok else 'NG'}"
        cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

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
    # 左カラム: カメラ入力 (キーを固定して切断を防ぐ)
    # ---------------------------------------------------------
    with col1:
        st.write("### リアルタイム判定")

        # key を固定値にすることで、st.rerun() されても WebRTC セッションを維持する
        ctx = webrtc_streamer(
                    key="origami-cam",
                    mode=WebRtcMode.SENDRECV,
                    video_processor_factory=OrigamiProcessor,
                    media_stream_constraints={
                        "video": {
                            "width": {"ideal": 1280},
                            "height": {"ideal": 720},
                            "aspectRatio": {"ideal": 16 / 9},
                        },
                        "audio": False,
                    },  # <-- 中括弧 } で辞書を閉じました
                    async_processing=True,
                )

        # 起動中のプロセッサへ「現在のステップ番号」を渡す
        if ctx.video_processor:
            ctx.video_processor.step_num = step_num

        st.write("---")
        if st.button("正しく折れたらここをクリックして次へ"):
            tutor.receive_cv_result(True)
            st.rerun()

    # ---------------------------------------------------------
    # 右カラム: 手動コントロール
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
