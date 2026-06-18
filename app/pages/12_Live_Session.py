import streamlit as st
import cv2
import mediapipe as mp
import time
import av
import json
from threading import Lock
import streamlit.components.v1 as components

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from db import save_exercise_session
from ui import apply_style, bottom_nav
from accessibility import accessibility_settings_panel, screen_reader_status
from movement_templates import MOVEMENT_TEMPLATES
from coaching_engine import (
    get_template_angle,
    update_rep_state,
    calculate_adaptive_accuracy,
    get_adaptive_targets
)

st.set_page_config(page_title="Live Session", layout="wide")
apply_style()

st.title("Live Exercise Session")
accessibility_settings_panel()


def speak(text):
    if not st.session_state.get("audio_feedback"):
        return

    safe_text = json.dumps(text)
    key = str(time.time()).replace(".", "")

    components.html(
        f"""
        <div id="speech-{key}"></div>
        <script>
        setTimeout(() => {{
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance({safe_text});
            msg.rate = 0.9;
            msg.volume = 1;
            window.speechSynthesis.speak(msg);
        }}, 100);
        </script>
        """,
        height=1,
    )


user_id = st.session_state.get("user_id")
exercise_id = st.session_state.get("active_exercise_id")
exercise_name = st.session_state.get("active_exercise_name", "Selected Exercise")

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

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

st.markdown(
    """
<style>
.live-header {
    background: rgba(31,36,33,0.88);
    border-radius: 22px;
    padding: 24px 28px;
    margin-bottom: 22px;
}

.live-title {
    font-size: 34px;
    font-weight: 900;
    margin-bottom: 8px;
}

.live-subtitle {
    opacity: 0.78;
    font-size: 16px;
}

.session-card {
    background: rgba(31,36,33,0.88);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
}

.session-card h3 {
    margin-top: 0;
    font-weight: 900;
}

.status-good {
    background: rgba(0, 140, 60, 0.25);
    border: 3px solid #00d46a;
    border-radius: 16px;
    padding: 18px;
    font-weight: 900;
}

.status-bad {
    background: rgba(190, 0, 0, 0.25);
    border: 3px solid #ff3333;
    border-radius: 16px;
    padding: 18px;
    font-weight: 900;
}

.status-neutral {
    background: rgba(120, 120, 120, 0.22);
    border: 3px solid #aaaaaa;
    border-radius: 16px;
    padding: 18px;
    font-weight: 900;
}

.metric-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 14px;
}

.metric-box {
    flex: 1;
    min-width: 120px;
    background: rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 14px;
    text-align: center;
}

.metric-number {
    font-size: 28px;
    font-weight: 900;
}

.metric-label {
    opacity: 0.75;
    font-size: 13px;
}

.small-note {
    opacity: 0.75;
    font-size: 14px;
}

[data-testid="stVerticalBlock"] video {
    max-width: 500px !important;
    max-height: 375px !important;
    border-radius: 18px !important;
    margin: auto !important;
    display: block !important;
}

button {
    font-weight: 800 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="live-header">
    <div class="live-title">{exercise_name}</div>
    <div class="live-subtitle">
        Live AI coaching with pose detection, rep counting, safety feedback, and adaptive movement targets.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

side_col, target_col = st.columns([1, 2])

with side_col:
    side_label = st.radio(
        "Which side are you training?",
        ["Right", "Left"],
        horizontal=True
    )

side = "RIGHT" if side_label == "Right" else "LEFT"

targets = get_adaptive_targets(template, st.session_state, side_label)

with target_col:
    st.markdown(
        f"""
        <div class="session-card">
            <h3>Adaptive Coaching Targets</h3>
            <p><b>Movement template:</b> {template}</p>
            <p><b>Top target:</b> {targets.get("top")}</p>
            <p><b>Bottom target:</b> {targets.get("bottom")}</p>
            <p class="small-note">
                These values use mobility test results if available. If no mobility result exists, the app uses general exercise ranges.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


class ExerciseProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.counter = 0
        self.stage = "down"
        self.session_start_time = None
        self.active = False

        self.angles = []
        self.last_feedback = "Ready. Start the session when prepared."
        self.last_angle = None
        self.pose_detected = False

        self.good_frames = 0
        self.bad_frames = 0
        self.total_frames = 0
        self.status_colour = "neutral"

    def start_session(self):
        with self.lock:
            self.counter = 0
            self.stage = "down"
            self.session_start_time = time.time()
            self.active = True
            self.angles = []
            self.last_feedback = "Session started. Move with control."
            self.last_angle = None
            self.good_frames = 0
            self.bad_frames = 0
            self.total_frames = 0
            self.status_colour = "neutral"

    def stop_session(self):
        with self.lock:
            self.active = False
            self.last_feedback = "Session stopped. You may save your results."
            self.status_colour = "neutral"

    def reset_session(self):
        with self.lock:
            self.counter = 0
            self.stage = "down"
            self.session_start_time = None
            self.active = False
            self.angles = []
            self.last_feedback = "Reset complete. Start again when ready."
            self.last_angle = None
            self.good_frames = 0
            self.bad_frames = 0
            self.total_frames = 0
            self.status_colour = "neutral"

    def get_latest_result(self):
        with self.lock:
            if self.session_start_time:
                duration = int(time.time() - self.session_start_time)
            else:
                duration = 0

            if self.total_frames > 0:
                live_score = int((self.good_frames / self.total_frames) * 100)
            else:
                live_score = 0

            return {
                "counter": self.counter,
                "stage": self.stage,
                "duration": duration,
                "angles": list(self.angles),
                "feedback": self.last_feedback,
                "angle": self.last_angle,
                "pose_detected": self.pose_detected,
                "status_colour": self.status_colour,
                "live_score": live_score,
                "active": self.active,
            }

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)

        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        angle = None
        pose_detected = False

        try:
            if results.pose_landmarks:
                pose_detected = True
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

                with self.lock:
                    self.pose_detected = True

                    if angle is not None:
                        self.last_angle = angle

                        if self.active:
                            self.angles.append(angle)
                            self.total_frames += 1

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

                            old_counter = self.counter
                            self.counter = fake_state["counter"]
                            self.stage = fake_state["stage"]
                            self.last_feedback = feedback

                            target_top = targets.get("top")
                            target_bottom = targets.get("bottom")

                            is_good = True

                            if target_top is not None and target_bottom is not None:
                                margin = 12
                                upper_bound = max(target_top, target_bottom) + margin
                                lower_bound = min(target_top, target_bottom) - margin

                                if angle > upper_bound or angle < lower_bound:
                                    is_good = False

                            bad_words = [
                                "too high",
                                "too low",
                                "adjust",
                                "not detected",
                                "unsafe",
                                "wrong",
                                "stop"
                            ]

                            if any(word in str(feedback).lower() for word in bad_words):
                                is_good = False

                            if is_good:
                                self.good_frames += 1
                                self.status_colour = "good"
                            else:
                                self.bad_frames += 1
                                self.status_colour = "bad"

                            if self.counter > old_counter:
                                self.last_feedback = f"Good rep. Total reps: {self.counter}"

                    elif self.active:
                        self.last_feedback = "Move into camera view clearly."
                        self.status_colour = "bad"
                        self.bad_frames += 1
                        self.total_frames += 1

            else:
                with self.lock:
                    self.pose_detected = False

                    if self.active:
                        self.last_feedback = "No pose detected. Adjust your camera."
                        self.status_colour = "bad"
                        self.bad_frames += 1
                        self.total_frames += 1

        except Exception:
            with self.lock:
                self.pose_detected = False
                self.last_feedback = "Position not detected clearly."
                self.status_colour = "bad"

        with self.lock:
            if self.session_start_time:
                duration = int(time.time() - self.session_start_time)
            else:
                duration = 0

            counter = self.counter
            stage = self.stage
            feedback = self.last_feedback
            display_angle = self.last_angle
            status_colour = self.status_colour
            active = self.active
            pose_now = self.pose_detected

        if status_colour == "good":
            border_colour = (0, 180, 0)
            indicator_text = "GREEN: GOOD FORM"
            indicator_colour = (0, 255, 0)
        elif status_colour == "bad":
            border_colour = (0, 0, 220)
            indicator_text = "RED: CHECK FORM"
            indicator_colour = (0, 0, 255)
        else:
            border_colour = (80, 80, 80)
            indicator_text = "READY"
            indicator_colour = (255, 255, 255)

        cv2.rectangle(image, (0, 0), (820, 185), (0, 0, 0), -1)
        cv2.rectangle(image, (0, 0), (820, 185), border_colour, 5)

        cv2.putText(
            image,
            indicator_text,
            (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            indicator_colour,
            2
        )

        cv2.putText(
            image,
            f"REPS: {counter} | STAGE: {stage} | TIME: {duration}s",
            (15, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        if display_angle is not None:
            cv2.putText(
                image,
                f"ANGLE: {int(display_angle)} degrees",
                (15, 112),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

        pose_text = "POSE DETECTED" if pose_now else "NO POSE DETECTED"
        pose_colour = (0, 255, 0) if pose_now else (0, 0, 255)

        cv2.putText(
            image,
            pose_text,
            (15, 148),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            pose_colour,
            2
        )

        cv2.putText(
            image,
            str(feedback)[:65],
            (15, 175),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            indicator_colour,
            2
        )

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
                "height": {"ideal": 480}
            },
            "audio": False
        },
        async_processing=True,
    )

    st.caption("Click START on the camera box and allow browser camera permission.")

with right:
    st.markdown(
        f"""
        <div class="session-card">
            <h3>Session Controls</h3>
            <p><b>Current Exercise:</b> {exercise_name}</p>
            <p><b>Training Side:</b> {side_label}</p>
            <p><b>Movement Template:</b> {template}</p>
            <p><b>Green:</b> Good movement within target range.</p>
            <p><b>Red:</b> Check your form, camera position, or movement range.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Read Session Instructions Aloud", use_container_width=True):
        speak(
            f"Live session for {exercise_name}. "
            f"You are training your {side_label.lower()} side. "
            "Green means good form. Red means check your form. "
            "Press start session when ready."
        )

    start_col, stop_col = st.columns(2)

    with start_col:
        start_session = st.button("Start Session", use_container_width=True)

    with stop_col:
        stop_session = st.button("Stop Session", use_container_width=True)

    reset_session = st.button("Reset Session", use_container_width=True)

    if start_session:
        if ctx.video_processor:
            ctx.video_processor.start_session()
            speak("Session started. Follow the green and red feedback on screen.")
        else:
            st.warning("Start the camera first.")

    if stop_session:
        if ctx.video_processor:
            ctx.video_processor.stop_session()
            speak("Session stopped. You can now save your result.")
        else:
            st.warning("Start the camera first.")

    if reset_session:
        if ctx.video_processor:
            ctx.video_processor.reset_session()
            speak("Session reset.")
        else:
            st.warning("Start the camera first.")

    st.markdown("### Live Feedback")

    if ctx.video_processor:
        latest = ctx.video_processor.get_latest_result()

        feedback = latest["feedback"]
        status_colour = latest["status_colour"]

        if status_colour == "good":
            st.markdown(
                f"<div class='status-good'>GREEN: {feedback}</div>",
                unsafe_allow_html=True
            )
        elif status_colour == "bad":
            st.markdown(
                f"<div class='status-bad'>RED: {feedback}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='status-neutral'>{feedback}</div>",
                unsafe_allow_html=True
            )

        screen_reader_status(feedback)

        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-number">{latest["counter"]}</div>
                    <div class="metric-label">Reps</div>
                </div>
                <div class="metric-box">
                    <div class="metric-number">{latest["duration"]}</div>
                    <div class="metric-label">Seconds</div>
                </div>
                <div class="metric-box">
                    <div class="metric-number">{latest["live_score"]}%</div>
                    <div class="metric-label">Live Score</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if latest["angle"] is not None:
            st.write(f"Current angle: **{int(latest['angle'])}°**")

        if latest["pose_detected"]:
            st.success("Pose detected.")
        else:
            st.warning("No pose detected yet.")

    else:
        st.info("Start the camera to begin the session.")

st.divider()

if st.button("End Session & Save", use_container_width=True):
    if ctx.video_processor:
        latest = ctx.video_processor.get_latest_result()

        reps = latest["counter"]
        duration = latest["duration"]
        angles = latest["angles"]

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

        speak("Session saved successfully.")
    else:
        st.warning("Start the camera before saving.")

bottom_nav()