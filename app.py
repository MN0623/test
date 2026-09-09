import av
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

from checker import OrigamiChecker
from tu import STEPS

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

if "step" not in st.session_state:
    st.session_state.step = 1


# =========================================
# VideoProcessor クラス
# =========================================
class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.result = False
        self.current_step = 1
        self.checker = OrigamiChecker()

    def update_step(self, step):
        if self.current_step != step:
            self.current_step = step
            self.checker.true_count = 0  # ステップが変わったらカウントをリセット

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)  # 鏡像反転

        # 折り紙判定ロジックを呼び出し
        self.result, processed_img = self.checker.process_frame(
            img, self.current_step
        )

        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")


# =========================================
# UI レイアウト
# =========================================
cols = st.columns([2, 1], gap="medium")

# --- カメラエリア ---
with cols[0]:
    st.subheader("Camera")
    ctx = webrtc_streamer(
        key="origami-camera",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 1280},
                "height": {"ideal": 720},
                "aspectRatio": {"ideal": 16 / 9},
            },
            "audio": False,
        },
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
    )

    # 現在のセッションの Step を Processor 側に常に更新・同期
    if ctx.video_processor:
        ctx.video_processor.update_step(st.session_state.step)

        # クリア判定時の画面更新
        if ctx.video_processor.result:
            if st.session_state.step <= len(STEPS):
                st.session_state.step += 1
                ctx.video_processor.result = False  # 連打防止のため即時リセット
                st.rerun()

# --- 手順表示エリア ---
with cols[1]:
    st.subheader("Step Guide")
    current_idx = st.session_state.step - 1

    if current_idx < len(STEPS):
        step_info = STEPS[current_idx]
        st.markdown(f"""
        ### Step {step_info['step']} / {len(STEPS)}
        
        **{step_info['instruction']}**
        
        ---
        💡 *カメラに向かって折り紙をかざしてください。連続して検出されると自動で次のステップへ進みます。*
        """)
    else:
        st.markdown("""
        ### 🎉 Complete!
        
        すべての手順が完了しました！
        """)

st.divider()

if st.session_state.step > len(STEPS):
    st.success("Your origami heart is complete! 🎉")
else:
    st.info(f"現在 Step {st.session_state.step} を実行中です。")
