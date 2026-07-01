import streamlit as st
import cv2
import mediapipe as mp
import time
import av
from threading import Lock
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from db import save_exercise_session, load_mobility_results_to_session
from ui import apply_style, bottom_nav
from accessibility import accessibility_settings_panel, speak
from movement_templates import MOVEMENT_TEMPLATES
from coaching_engine import get_template_angle, calculate_adaptive_accuracy

st.set_page_config(page_title="Live Session", layout="wide")
apply_style()

st.markdown("""
<style>
.live-page { padding: 34px; }

.live-hero {
    background: linear-gradient(135deg, #1f2421, #2d3530);
    border-radius: 28px;
    padding: 38px;
    margin-bottom: 24px;
}

.live-title {
    font-size: 48px;
    font-weight: 900;
    line-height: 1;
}

.live-subtitle {
    font-size: 18px;
    opacity: 0.82;
    margin-top: 12px;
}

.live-card {
    background: rgba(31,36,33,0.92);
    padding: 24px;
    border-radius: 22px;
    margin-bottom: 18px;
}

.instruction-step {
    background: rgba(159,185,212,0.14);
    border: 1px solid #9fb9d4;
    padding: 13px 16px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-weight: 700;
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

[data-testid="stVerticalBlock"] video {
    max-width: 430px !important;
    max-height: 320px !important;
    border-radius: 18px !important;
    margin: auto !important;
    display: block !important;
}
</style>
""", unsafe_allow_html=True)

user_id = st.session_state.get("user_id")
exercise_id = st.session_state.get("active_exercise_id")
exercise_name = st.session_state.get("active_exercise_name", "Selected Exercise")

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

st.markdown(f"""
<div class="live-page">
<div class="live-hero">
<div class="live-title">Live Exercise Session</div>
<div class="live-subtitle">
Current exercise: <b>{exercise_name}</b><br>
Follow the camera guidance and stay within your comfortable tested range.
</div>
</div>
</div>
""", unsafe_allow_html=True)

accessibility_settings_panel()

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

if saved_rom and saved_rom > 0:
    rep_threshold = max(8, saved_rom * 0.45)
    return_threshold = max(4, saved_rom * 0.18)
else:
    rep_threshold = 18
    return_threshold = 8

st.markdown(f"""
<div class="live-page">
<div class="live-card">
<h3>How to Use This Session</h3>
<div class="instruction-step">1. Select the side you are training.</div>
<div class="instruction-step">2. Press START on the camera box and allow camera permission.</div>
<div class="instruction-step">3. Hold still for a few seconds so the system can set your baseline.</div>
<div class="instruction-step">4. Move slowly within your comfortable range.</div>
<div class="instruction-step">5. Green means good range. Red means adjust your position or movement.</div>
<p><b>ROM used:</b> {saved_rom if saved_rom is not None else "General range"}°</p>
<p><b>Mobility result:</b> {mobility_key if mobility_key else "No matching test found"}</p>
<p><b>Rep target:</b> {round(rep_threshold, 1)}° movement from baseline</p>
</div>
</div>
""", unsafe_allow_html=True)

if st.button("Read Session Instructions", use_container_width=True):
    speak(
        f"Live exercise session for {exercise_name}. Select your side, start the camera, "
        "hold still for baseline, then move slowly within your comfortable range. "
        "Green means good movement. Red means adjust your position."
    )

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class ExerciseProcessor:
    def __init__(self):
        self.lock = Lock()

        try:
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                smooth_landmarks=False,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.pose_ready = True
        except Exception:
            self.pose = None
            self.pose_ready = False

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

        if not self.pose_ready or self.pose is None:
            cv2.rectangle(img, (10, 10), (620, 130), (0, 0, 0), -1)
            cv2.rectangle(img, (10, 10), (620, 130), (0, 0, 255), 3)
            cv2.putText(img, "POSE MODEL NOT AVAILABLE", (25, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

            with self.lock:
                self.status = "bad"
                self.last_feedback = "Pose model could not load."

            return av.VideoFrame.from_ndarray(img, format="bgr24")

        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                angle = get_template_angle(template, landmarks, mp_pose, side)

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

                            if len(self.baseline_samples) >= 30:
                                self.baseline_angle = sum(self.baseline_samples) / len(self.baseline_samples)
                                self.status = "neutral"
                                self.last_feedback = "Baseline set. Start moving."

                        else:
                            movement = abs(angle - self.baseline_angle)

                            if movement < 5:
                                movement = 0

                            self.last_movement = movement

                            unsafe = False

                            if saved_rom is not None and saved_rom > 0:
                                if movement > saved_rom + 12:
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
            display_angle = self.last_angle
            display_status = self.status
            baseline = self.baseline_angle
            movement = self.last_movement
            feedback = self.last_feedback

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

        cv2.rectangle(image, (10, 10), (620, 140), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (620, 140), border_colour, 3)

        cv2.putText(image, status_text, (25, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_colour, 2)

        cv2.putText(image, f"Reps: {counter} | Stage: {stage} | Time: {duration}s",
                    (25, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        if display_angle is not None:
            cv2.putText(image, f"Angle: {int(display_angle)} | Move: {int(movement)}",
                        (25, 94), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        if baseline is not None:
            cv2.putText(image, f"Base: {int(baseline)} | Target: {round(rep_threshold,1)}",
                        (25, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

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
                "width": {"ideal": 480},
                "height": {"ideal": 360},
                "frameRate": {"ideal": 12, "max": 15},
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
                {"top": rep_threshold, "bottom": return_threshold}
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