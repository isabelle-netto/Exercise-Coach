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
    calculate_adaptive_accuracy,
    get_adaptive_targets
)

st.set_page_config(page_title="Live Session", layout="wide")
apply_style()

st.markdown("""
<style>
[data-testid="stVerticalBlock"] video {
    max-width: 500px !important;
    max-height: 370px !important;
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
    background: rgba(0,150,70,0.25);
    border: 3px solid #00d46a;
    padding: 16px;
    border-radius: 16px;
    font-weight: 900;
}
.bad-box {
    background: rgba(190,0,0,0.25);
    border: 3px solid #ff3333;
    padding: 16px;
    border-radius: 16px;
    font-weight: 900;
}
.neutral-box {
    background: rgba(120,120,120,0.22);
    border: 3px solid #aaaaaa;
    padding: 16px;
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


def get_mobility_key_for_template(template_name, exercise_name, side_label):
    text = f"{template_name} {exercise_name}".lower()

    if "shoulder" in text or "press" in text or "raise" in text:
        return f"{side_label}_Shoulder_Flexion"

    if "row" in text or "curl" in text or "bicep" in text or "tricep" in text:
        return f"{side_label}_Elbow_Flexion"

    if "squat" in text or "leg" in text or "knee" in text:
        return f"{side_label}_Knee_Flexion"

    if "hip" in text or "glute" in text:
        return f"{side_label}_Hip_Flexion"

    if "ankle" in text or "calf" in text:
        return f"{side_label}_Ankle_Mobility"

    return None


mobility_key = get_mobility_key_for_template(template, exercise_name, side_label)

saved_start = None
saved_limit = None
saved_rom = None
saved_direction = None

if mobility_key:
    saved_start = st.session_state.get(f"{mobility_key}_starting_angle")
    saved_limit = st.session_state.get(f"{mobility_key}_safe_limit_angle")
    saved_rom = st.session_state.get(f"{mobility_key}_rom")
    saved_direction = st.session_state.get(f"{mobility_key}_direction")

if saved_rom is not None:
    saved_rom = int(saved_rom)

st.markdown(f"""
<div class="live-card">
<h3>Adaptive Coaching Targets</h3>
<p><b>Exercise template:</b> {template}</p>
<p><b>Mobility result used:</b> {mobility_key if mobility_key else "General movement"}</p>
<p><b>Saved ROM:</b> {saved_rom if saved_rom is not None else "Not found"}°</p>
<p><b>Saved safe limit:</b> {saved_limit if saved_limit is not None else "Not found"}°</p>
<p>This session counts reps using your tested ROM, not a normal full-body range.</p>
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
        self.stage = "rest"
        self.session_start_time = time.time()
        self.angles = []
        self.baseline_samples = []
        self.baseline_angle = None
        self.last_angle = None
        self.last_feedback = "Ready"
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

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                angle = get_template_angle(
                    template,
                    landmarks,
                    mp_pose,
                    side
                )

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                if angle is not None:
                    with self.lock:
                        self.last_angle = angle
                        self.angles.append(angle)
                        self.total_frames += 1

                        if self.baseline_angle is None:
                            self.baseline_samples.append(angle)

                            if len(self.baseline_samples) >= 20:
                                self.baseline_angle = sum(self.baseline_samples) / len(self.baseline_samples)
                                self.last_feedback = "Baseline set. Start moving within your comfortable range."
                                self.status = "neutral"

                        else:
                            if saved_rom is not None and saved_rom > 0:
                                rep_threshold = max(5, saved_rom * 0.35)
                                return_threshold = max(3, saved_rom * 0.12)
                            else:
                                rep_threshold = 12
                                return_threshold = 5

                            if saved_direction == "decrease":
                                movement_amount = self.baseline_angle - angle
                            else:
                                movement_amount = angle - self.baseline_angle

                            movement_amount = max(0, movement_amount)

                            unsafe = False

                            if saved_limit is not None and saved_direction:
                                limit = int(saved_limit)
                                margin = 8

                                if saved_direction == "increase" and angle > limit + margin:
                                    unsafe = True

                                if saved_direction == "decrease" and angle < limit - margin:
                                    unsafe = True

                            if unsafe:
                                self.status = "bad"
                                self.bad_frames += 1
                                self.last_feedback = "Stop. You are beyond your tested safe range."

                            else:
                                self.status = "good"
                                self.good_frames += 1
                                self.last_feedback = "Good. Stay within your tested range."

                                if self.stage == "rest" and movement_amount >= rep_threshold:
                                    self.stage = "active"

                                elif self.stage == "active" and movement_amount <= return_threshold:
                                    self.stage = "rest"
                                    self.counter += 1
                                    self.last_feedback = f"Good rep. Total reps: {self.counter}"

            else:
                with self.lock:
                    self.status = "bad"
                    self.bad_frames += 1
                    self.total_frames += 1
                    self.last_feedback = "No pose detected. Adjust your camera."

        except Exception:
            with self.lock:
                self.status = "bad"
                self.last_feedback = "Position not detected clearly."

        with self.lock:
            duration = int(time.time() - self.session_start_time)
            counter = self.counter
            stage = self.stage
            feedback = self.last_feedback
            display_angle = self.last_angle
            display_status = self.status
            baseline = self.baseline_angle

        if display_status == "good":
            border_colour = (0, 180, 0)
            text_colour = (0, 255, 0)
            status_text = "GREEN: GOOD FORM"
        elif display_status == "bad":
            border_colour = (0, 0, 220)
            text_colour = (0, 0, 255)
            status_text = "RED: CHECK RANGE"
        else:
            border_colour = (90, 90, 90)
            text_colour = (255, 255, 255)
            status_text = "READY"

        cv2.rectangle(image, (10, 10), (650, 150), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (650, 150), border_colour, 3)

        cv2.putText(image, status_text, (25, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, text_colour, 2)

        cv2.putText(image, f"Reps: {counter} | Stage: {stage} | Time: {duration}s",
                    (25, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

        if display_angle is not None:
            cv2.putText(image, f"Angle: {int(display_angle)} deg",
                        (25, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

        if baseline is not None:
            cv2.putText(image, f"Baseline: {int(baseline)} deg | ROM target: {saved_rom if saved_rom else 'general'}",
                        (25, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        cv2.putText(image, str(feedback)[:55],
                    (25, 144), cv2.FONT_HERSHEY_SIMPLEX, 0.42, text_colour, 1)

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
            baseline = ctx.video_processor.baseline_angle

        live_score = int((good_frames / total_frames) * 100) if total_frames else 0

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

        if baseline is not None:
            st.write(f"**Baseline Angle:** {int(baseline)}°")

        st.write(f"**ROM Used:** {saved_rom if saved_rom is not None else 'General target'}")

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

    else:
        st.info("Start the camera to begin the session.")

bottom_nav()