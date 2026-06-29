import streamlit as st
import cv2
import mediapipe as mp
import time
import av
from threading import Lock
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from db import save_exercise_session, load_mobility_results_to_session
from ui import apply_style, bottom_nav
from movement_templates import MOVEMENT_TEMPLATES
from coaching_engine import get_template_angle, calculate_adaptive_accuracy

st.set_page_config(page_title="Live Session", layout="wide")
apply_style()

st.markdown("""
<style>
[data-testid="stVerticalBlock"] video {
    max-width: 480px !important;
    max-height: 360px !important;
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


def get_mobility_key(template_name, exercise_name, side_label):
    text = f"{template_name} {exercise_name}".lower()

    if "shoulder" in text or "press" in text or "raise" in text:
        return f"{side_label}_Shoulder_Flexion"

    if "curl" in text or "bicep" in text or "tricep" in text or "row" in text:
        return f"{side_label}_Elbow_Flexion"

    if "squat" in text or "leg" in text or "knee" in text:
        return f"{side_label}_Knee_Flexion"

    if "hip" in text or "glute" in text:
        return f"{side_label}_Hip_Flexion"

    if "calf" in text or "ankle" in text:
        return f"{side_label}_Ankle_Mobility"

    return None


mobility_key = get_mobility_key(template, exercise_name, side_label)

saved_rom = None
saved_limit = None
saved_direction = None

if mobility_key:
    saved_rom = st.session_state.get(f"{mobility_key}_rom")
    saved_limit = st.session_state.get(f"{mobility_key}_safe_limit_angle")
    saved_direction = st.session_state.get(f"{mobility_key}_direction")

try:
    saved_rom = int(saved_rom) if saved_rom is not None else None
except Exception:
    saved_rom = None

try:
    saved_limit = int(saved_limit) if saved_limit is not None else None
except Exception:
    saved_limit = None

if not saved_direction:
    saved_direction = "increase"

# IMPORTANT:
# Rep threshold must be LOW enough for limited-ROM users.
# If saved ROM is 20°, threshold becomes 6°.
# If no ROM exists, it still counts using 12°.
if saved_rom and saved_rom > 0:
    rep_threshold = max(4, saved_rom * 0.30)
    return_threshold = max(2, saved_rom * 0.10)
else:
    rep_threshold = 12
    return_threshold = 5

st.markdown(f"""
<div class="live-card">
<h3>Adaptive ROM Settings Used</h3>
<p><b>Movement template:</b> {template}</p>
<p><b>Mobility result used:</b> {mobility_key if mobility_key else "No matching mobility test found"}</p>
<p><b>Saved ROM:</b> {saved_rom if saved_rom is not None else "Not found"}°</p>
<p><b>Safe limit:</b> {saved_limit if saved_limit is not None else "Not found"}°</p>
<p><b>Rep threshold:</b> {round(rep_threshold, 1)}°</p>
<p><b>Return threshold:</b> {round(return_threshold, 1)}°</p>
<p>This means the system counts reps based on your tested range, not a normal full range.</p>
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
        self.last_movement = 0

        self.last_feedback = "Camera ready. Hold still briefly for baseline."
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

                            if len(self.baseline_samples) >= 15:
                                self.baseline_angle = sum(self.baseline_samples) / len(self.baseline_samples)
                                self.status = "neutral"
                                self.last_feedback = "Baseline set. Start moving."

                        else:
                            if saved_direction == "decrease":
                                movement = self.baseline_angle - angle
                            else:
                                movement = angle - self.baseline_angle

                            movement = max(0, movement)
                            self.last_movement = movement

                            unsafe = False

                            if saved_limit is not None:
                                margin = 10

                                if saved_direction == "increase" and angle > saved_limit + margin:
                                    unsafe = True

                                if saved_direction == "decrease" and angle < saved_limit - margin:
                                    unsafe = True

                            if unsafe:
                                self.status = "bad"
                                self.bad_frames += 1
                                self.last_feedback = "Stop. Beyond tested safe range."

                            else:
                                self.status = "good"
                                self.good_frames += 1

                                if self.stage == "rest" and movement >= rep_threshold:
                                    self.stage = "active"
                                    self.last_feedback = "Good. Now return slowly."

                                elif self.stage == "active" and movement <= return_threshold:
                                    self.stage = "rest"
                                    self.counter += 1
                                    self.last_feedback = f"Rep counted. Total reps: {self.counter}"

                                else:
                                    self.last_feedback = "Good. Stay controlled."

                else:
                    with self.lock:
                        self.status = "bad"
                        self.bad_frames += 1
                        self.total_frames += 1
                        self.last_feedback = "Angle not detected. Adjust position."

            else:
                with self.lock:
                    self.status = "bad"
                    self.bad_frames += 1
                    self.total_frames += 1
                    self.last_feedback = "No pose detected. Adjust camera."

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
            movement = self.last_movement

        if display_status == "good":
            border_colour = (0, 180, 0)
            text_colour = (0, 255, 0)
            status_text = "GREEN: GOOD"
        elif display_status == "bad":
            border_colour = (0, 0, 220)
            text_colour = (0, 0, 255)
            status_text = "RED: CHECK"
        else:
            border_colour = (90, 90, 90)
            text_colour = (255, 255, 255)
            status_text = "READY"

        cv2.rectangle(image, (10, 10), (650, 155), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (650, 155), border_colour, 3)

        cv2.putText(image, status_text, (25, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, text_colour, 2)

        cv2.putText(image, f"Reps: {counter} | Stage: {stage} | Time: {duration}s",
                    (25, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

        if display_angle is not None:
            cv2.putText(image, f"Angle: {int(display_angle)} deg | Move: {int(movement)} deg",
                        (25, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2)

        if baseline is not None:
            cv2.putText(image, f"Base: {int(baseline)} | Rep target: {round(rep_threshold,1)} deg",
                        (25, 122), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        cv2.putText(image, str(feedback)[:55],
                    (25, 146), cv2.FONT_HERSHEY_SIMPLEX, 0.42, text_colour, 1)

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
            movement = ctx.video_processor.last_movement
            stage = ctx.video_processor.stage

        live_score = int((good_frames / total_frames) * 100) if total_frames else 0

        if status == "good":
            st.markdown(f"<div class='good-box'>GREEN: {feedback}</div>", unsafe_allow_html=True)
        elif status == "bad":
            st.markdown(f"<div class='bad-box'>RED: {feedback}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='neutral-box'>{feedback}</div>", unsafe_allow_html=True)

        st.write(f"**Reps:** {reps}")
        st.write(f"**Stage:** {stage}")
        st.write(f"**Duration:** {duration} seconds")
        st.write(f"**Live Score:** {live_score}%")
        st.write(f"**ROM Used:** {saved_rom if saved_rom is not None else 'General'}")
        st.write(f"**Rep Target:** {round(rep_threshold, 1)}°")

        if angle is not None:
            st.write(f"**Current Angle:** {int(angle)}°")

        if baseline is not None:
            st.write(f"**Baseline Angle:** {int(baseline)}°")

        st.write(f"**Movement From Baseline:** {int(movement)}°")

        if st.button("End Session & Save", use_container_width=True):
            accuracy_score, avg_angle_error = calculate_adaptive_accuracy(
                template,
                angles,
                {
                    "top": rep_threshold,
                    "bottom": return_threshold
                }
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