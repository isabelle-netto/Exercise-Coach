import streamlit as st
import cv2
import mediapipe as mp
import time
import av
from threading import Lock

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from db import save_exercise_session
from ui import apply_style, bottom_nav
from movement_templates import MOVEMENT_TEMPLATES
from coaching_engine import (
    get_template_angle,
    update_rep_state,
    calculate_adaptive_accuracy,
    get_adaptive_targets
)

st.set_page_config(page_title="Live Session", layout="wide")
apply_style()

user_id = st.session_state.get("user_id")
exercise_id = st.session_state.get("active_exercise_id")
exercise_name = st.session_state.get("active_exercise_name", "Selected Exercise")

st.title("Live Exercise Session")
st.write(f"Current Exercise: **{exercise_name}**")

if not user_id:
    st.warning("Please sign in before starting a session.")
    bottom_nav()
    st.stop()

if not exercise_id:
    st.warning("Please select an exercise first.")
    if st.button("Go to Exercises"):
        st.switch_page("pages/08_Exercises.py")
    bottom_nav()
    st.stop()

template = MOVEMENT_TEMPLATES.get(exercise_name, "general")

side_label = st.radio("Which side are you training?", ["Right", "Left"], horizontal=True)
side = "RIGHT" if side_label == "Right" else "LEFT"

targets = get_adaptive_targets(template, st.session_state, side_label)

st.info(f"Movement template detected: **{template}**")

st.markdown(f"""
<div class="card">
    <h3>Adaptive Coaching Targets</h3>
    <p><b>Top target:</b> {targets.get("top")}</p>
    <p><b>Bottom target:</b> {targets.get("bottom")}</p>
    <p>These values use your mobility test results if available. If no mobility result exists, the app uses general exercise ranges.</p>
</div>
""", unsafe_allow_html=True)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class ExerciseProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.counter = 0
        self.stage = "down"
        self.session_start_time = time.time()
        self.angles = []
        self.last_feedback = "Ready"
        self.last_angle = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        angle = None

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                angle = get_template_angle(
                    template,
                    landmarks,
                    mp_pose,
                    side
                )

                with self.lock:
                    if angle is not None:
                        self.angles.append(angle)
                        self.last_angle = angle

                        fake_state = {
                            "counter": self.counter,
                            "stage": self.stage
                        }

                        feedback, _ = update_rep_state(
                            template,
                            angle,
                            fake_state,
                            targets
                        )

                        self.counter = fake_state["counter"]
                        self.stage = fake_state["stage"]
                        self.last_feedback = feedback

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

        except Exception:
            with self.lock:
                self.last_feedback = "Position not detected clearly"

        with self.lock:
            duration = int(time.time() - self.session_start_time)
            counter = self.counter
            stage = self.stage
            feedback = self.last_feedback
            display_angle = self.last_angle

        cv2.rectangle(image, (0, 0), (720, 130), (0, 0, 0), -1)

        cv2.putText(image, f"REPS: {counter}", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(image, f"STAGE: {stage}", (180, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(image, f"TIME: {duration}s", (390, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if display_angle is not None:
            cv2.putText(image, f"ANGLE: {int(display_angle)}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(image, f"FEEDBACK: {feedback}", (10, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

ctx = webrtc_streamer(
    key=f"live-session-{exercise_id}-{template}-{side}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=ExerciseProcessor,
    media_stream_constraints={
        "video": True,
        "audio": False
    },
    async_processing=True,
)

st.write("Click **START** on the camera box and allow browser camera permission.")

if ctx.video_processor:
    with ctx.video_processor.lock:
        reps = ctx.video_processor.counter
        duration = int(time.time() - ctx.video_processor.session_start_time)
        angles = list(ctx.video_processor.angles)
        feedback = ctx.video_processor.last_feedback

    st.markdown(f"""
    <div class="card">
        <h3>Live Session Data</h3>
        <p><b>Reps:</b> {reps}</p>
        <p><b>Duration:</b> {duration} seconds</p>
        <p><b>Latest Feedback:</b> {feedback}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("End Session & Save"):
        accuracy_score, avg_angle_error = calculate_adaptive_accuracy(
            template,
            angles,
            targets
        )

        session_id = save_exercise_session(
            user_id=user_id,
            exercise_id=exercise_id,
            reps_completed=reps,
            duration=duration,
            accuracy_score=accuracy_score,
            avg_angle_error=avg_angle_error
        )

        st.success(f"Session saved successfully. Session ID: {session_id}")
        st.info(
            f"Exercise: {exercise_name} | Reps: {reps} | "
            f"Duration: {duration} seconds | Accuracy: {accuracy_score}%"
        )

else:
    st.info("Start the camera to begin the session.")

bottom_nav()