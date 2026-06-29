import streamlit as st
import cv2
import mediapipe as mp
import time
import av
from threading import Lock

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from db import save_exercise_session
try:
    from db import load_mobility_results_to_session
except Exception:
    load_mobility_results_to_session = None

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

st.markdown("""
<style>
[data-testid="stVerticalBlock"] video {
    max-width: 520px !important;
    max-height: 390px !important;
    border-radius: 18px !important;
    margin: auto !important;
    display: block !important;
}

.live-card {
    background: rgba(31,36,33,0.90);
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 16px;
}

.good-box {
    background: rgba(0, 150, 70, 0.25);
    border: 3px solid #00d46a;
    padding: 18px;
    border-radius: 16px;
    font-weight: 900;
}

.bad-box {
    background: rgba(190, 0, 0, 0.25);
    border: 3px solid #ff3333;
    padding: 18px;
    border-radius: 16px;
    font-weight: 900;
}

.neutral-box {
    background: rgba(120, 120, 120, 0.22);
    border: 3px solid #aaaaaa;
    padding: 18px;
    border-radius: 16px;
    font-weight: 900;
}
</style>
""", unsafe_allow_html=True)

user_id = st.session_state.get("user_id")
exercise_id = st.session_state.get("active_exercise_id")
exercise_name = st.session_state.get("active_exercise_name", "Selected Exercise")

st.title("Live Exercise Session")
st.write(f"Current Exercise: **{exercise_name}**")

if not user_id:
    st.warning("Please sign in before starting a session.")
    bottom_nav()
    st.stop()

if load_mobility_results_to_session:
    load_mobility_results_to_session(user_id)

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

st.markdown(f"""
<div class="live-card">
<h3>Adaptive Coaching Targets</h3>
<p><b>Movement template:</b> {template}</p>
<p><b>Top target:</b> {targets.get("top")}</p>
<p><b>Bottom target:</b> {targets.get("bottom")}</p>
<p>These targets use your saved mobility test results where available.</p>
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
        self.status = "neutral"
        self.good_frames = 0
        self.bad_frames = 0
        self.total_frames = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        angle = None
        feedback = "Position not detected clearly"
        status = "bad"

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                angle = get_template_angle(
                    template,
                    landmarks,
                    mp_pose,
                    side
                )

                if angle is not None:
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

                    top_target = targets.get("top")
                    bottom_target = targets.get("bottom")

                    status = "good"

                    if top_target is not None and bottom_target is not None:
                        upper = max(top_target, bottom_target) + 12
                        lower = min(top_target, bottom_target) - 12

                        if angle > upper or angle < lower:
                            status = "bad"
                            feedback = "Check form. Stay within your safe range."

                    bad_words = ["too", "wrong", "adjust", "unsafe", "stop", "not"]
                    if any(word in str(feedback).lower() for word in bad_words):
                        status = "bad"

                    with self.lock:
                        self.angles.append(angle)
                        self.last_angle = angle
                        self.counter = fake_state["counter"]
                        self.stage = fake_state["stage"]
                        self.last_feedback = feedback
                        self.status = status
                        self.total_frames += 1

                        if status == "good":
                            self.good_frames += 1
                        else:
                            self.bad_frames += 1

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            else:
                with self.lock:
                    self.last_feedback = "No pose detected. Adjust your camera."
                    self.status = "bad"
                    self.total_frames += 1
                    self.bad_frames += 1

        except Exception:
            with self.lock:
                self.last_feedback = "Position not detected clearly."
                self.status = "bad"

        with self.lock:
            duration = int(time.time() - self.session_start_time)
            counter = self.counter
            stage = self.stage
            display_feedback = self.last_feedback
            display_angle = self.last_angle
            display_status = self.status

        if display_status == "good":
            border_colour = (0, 180, 0)
            text_colour = (0, 255, 0)
            status_text = "GREEN: GOOD FORM"
        elif display_status == "bad":
            border_colour = (0, 0, 220)
            text_colour = (0, 0, 255)
            status_text = "RED: CHECK FORM"
        else:
            border_colour = (90, 90, 90)
            text_colour = (255, 255, 255)
            status_text = "READY"

        cv2.rectangle(image, (10, 10), (700, 160), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (700, 160), border_colour, 4)

        cv2.putText(image, status_text, (25, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, text_colour, 2)

        cv2.putText(image, f"Reps: {counter} | Stage: {stage} | Time: {duration}s",
                    (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        if display_angle is not None:
            cv2.putText(image, f"Angle: {int(display_angle)} deg",
                        (25, 108), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        cv2.putText(image, str(display_feedback)[:55],
                    (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.50, text_colour, 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

left, right = st.columns([3, 2])

with left:
    st.markdown("### Camera")

    ctx = webrtc_streamer(
        key=f"live-session-{exercise_id}-{template}-{side}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=ExerciseProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
            },
            "audio": False
        },
        async_processing=True,
    )

    st.caption("Click START on the camera box and allow browser camera permission.")

with right:
    st.markdown("### Live Session Data")

    if ctx.video_processor:
        with ctx.video_processor.lock:
            reps = ctx.video_processor.counter
            duration = int(time.time() - ctx.video_processor.session_start_time)
            angles = list(ctx.video_processor.angles)
            feedback = ctx.video_processor.last_feedback
            angle = ctx.video_processor.last_angle
            status = ctx.video_processor.status
            total_frames = ctx.video_processor.total_frames
            good_frames = ctx.video_processor.good_frames

        if total_frames > 0:
            live_score = int((good_frames / total_frames) * 100)
        else:
            live_score = 0

        if status == "good":
            st.markdown(f"<div class='good-box'>GREEN: {feedback}</div>", unsafe_allow_html=True)
        elif status == "bad":
            st.markdown(f"<div class='bad-box'>RED: {feedback}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='neutral-box'>{feedback}</div>", unsafe_allow_html=True)

        st.write(f"**Reps:** {reps}")
        st.write(f"**Duration:** {duration} seconds")
        st.write(f"**Live Score:** {live_score}%")

        if angle is not None:
            st.write(f"**Current Angle:** {int(angle)}°")

        if st.button("End Session & Save", use_container_width=True):
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