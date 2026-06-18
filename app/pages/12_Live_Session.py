import streamlit as st
import mediapipe as mp
import numpy as np
import av
import cv2
import time
import json
from threading import Lock
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components

from ui import apply_style, bottom_nav
from accessibility import accessibility_settings_panel, screen_reader_status
from db import get_all_exercises, get_exercise_details, save_exercise_session

st.set_page_config(page_title="Live Exercise Session", layout="wide")
apply_style()

st.title("Live Exercise Session")
accessibility_settings_panel()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


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


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1],
        a[0] - b[0],
    )

    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def get_landmark(landmarks, landmark):
    p = landmarks[landmark.value]
    return [p.x, p.y]


def get_side_points(landmarks, side):
    if side == "Right":
        return {
            "shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER),
            "elbow": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW),
            "wrist": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST),
            "hip": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_HIP),
            "knee": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_KNEE),
            "ankle": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE),
            "foot": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX),
        }

    return {
        "shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER),
        "elbow": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW),
        "wrist": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_WRIST),
        "hip": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_HIP),
        "knee": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_KNEE),
        "ankle": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_ANKLE),
        "foot": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_FOOT_INDEX),
    }


MOVEMENTS = {
    "Shoulder Flexion": {
        "result_key": "Shoulder_Flexion",
        "direction": "increase",
        "instruction": "Raise your arm forward only within your safe tested range.",
    },
    "Shoulder Abduction": {
        "result_key": "Shoulder_Abduction",
        "direction": "increase",
        "instruction": "Raise your arm out to the side only within your safe tested range.",
    },
    "Elbow Flexion": {
        "result_key": "Elbow_Flexion",
        "direction": "decrease",
        "instruction": "Bend your elbow toward your shoulder with control.",
    },
    "Hip Flexion": {
        "result_key": "Hip_Flexion",
        "direction": "decrease",
        "instruction": "Lift your knee upward with control.",
    },
    "Knee Flexion": {
        "result_key": "Knee_Flexion",
        "direction": "decrease",
        "instruction": "Bend your knee only within your safe tested range.",
    },
    "Knee Extension": {
        "result_key": "Knee_Extension",
        "direction": "increase",
        "instruction": "Straighten your knee only within your safe tested range.",
    },
    "Ankle Mobility": {
        "result_key": "Ankle_Mobility",
        "direction": "increase",
        "instruction": "Move your foot through a controlled comfortable range.",
    },
}


def measure_angle(movement_name, landmarks, side):
    pts = get_side_points(landmarks, side)

    if movement_name in ["Shoulder Flexion", "Shoulder Abduction"]:
        return calculate_angle(pts["hip"], pts["shoulder"], pts["elbow"])

    if movement_name == "Elbow Flexion":
        return calculate_angle(pts["shoulder"], pts["elbow"], pts["wrist"])

    if movement_name == "Hip Flexion":
        return calculate_angle(pts["shoulder"], pts["hip"], pts["knee"])

    if movement_name in ["Knee Flexion", "Knee Extension"]:
        return calculate_angle(pts["hip"], pts["knee"], pts["ankle"])

    if movement_name == "Ankle Mobility":
        return calculate_angle(pts["knee"], pts["ankle"], pts["foot"])

    return None


def get_saved_rom(side, movement_name):
    result_key = MOVEMENTS[movement_name]["result_key"]
    full_key = f"{side}_{result_key}"

    starting_angle = st.session_state.get(f"{full_key}_starting_angle")
    safe_limit_angle = st.session_state.get(f"{full_key}_safe_limit_angle")
    rom = st.session_state.get(f"{full_key}_rom")
    direction = st.session_state.get(f"{full_key}_direction")

    return starting_angle, safe_limit_angle, rom, direction


st.markdown(
    """
<style>
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
    background: rgba(0, 140, 60, 0.22);
    border: 2px solid #00cc66;
    border-radius: 14px;
    padding: 16px;
    font-weight: 900;
}

.status-bad {
    background: rgba(180, 0, 0, 0.22);
    border: 2px solid #ff3333;
    border-radius: 14px;
    padding: 16px;
    font-weight: 900;
}

.status-neutral {
    background: rgba(120, 120, 120, 0.22);
    border: 2px solid #aaaaaa;
    border-radius: 14px;
    padding: 16px;
    font-weight: 900;
}

.small-note {
    opacity: 0.78;
    font-size: 14px;
}

[data-testid="stVerticalBlock"] video {
    max-width: 520px !important;
    max-height: 390px !important;
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


user_id = st.session_state.get("user_id")

if not user_id:
    st.error("Please sign in first.")
    if st.button("Back to Sign In"):
        st.switch_page("pages/02_Sign_In.py")
    st.stop()


exercises = get_all_exercises()

if not exercises:
    st.error("No exercises found in the database.")
    bottom_nav()
    st.stop()

exercise_labels = {
    f"{row[1]} | {row[2]} | {row[3]}": row[0]
    for row in exercises
}

selected_exercise_label = st.selectbox(
    "Choose Exercise",
    list(exercise_labels.keys())
)

exercise_id = exercise_labels[selected_exercise_label]
exercise_details = get_exercise_details(exercise_id)

if exercise_details:
    exercise_name, target_area, instructions, difficulty, seated_friendly = exercise_details
else:
    exercise_name = selected_exercise_label
    target_area = "General"
    instructions = "Follow the movement safely and stay within your tested range."
    difficulty = "Beginner"
    seated_friendly = 0


top1, top2 = st.columns(2)

with top1:
    selected_side = st.radio(
        "Side to monitor",
        ["Right", "Left"],
        horizontal=True,
    )

with top2:
    movement_name = st.selectbox(
        "Movement to monitor",
        list(MOVEMENTS.keys()),
    )

movement = MOVEMENTS[movement_name]
starting_angle_saved, safe_limit_saved, rom_saved, saved_direction = get_saved_rom(
    selected_side,
    movement_name,
)

if safe_limit_saved is not None:
    safe_limit_saved = int(safe_limit_saved)

if rom_saved is not None:
    rom_saved = int(rom_saved)


class LiveSessionProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.45,
            min_tracking_confidence=0.45,
        )

        self.active = False
        self.session_start = None
        self.duration = 0

        self.baseline_samples = []
        self.baseline_angle = None
        self.current_angle = None

        self.reps = 0
        self.stage = "rest"

        self.pose_detected = False
        self.feedback = "Start the camera, then begin session."
        self.status_colour = "neutral"

        self.good_frames = 0
        self.bad_frames = 0
        self.total_pose_frames = 0
        self.unsafe_events = 0
        self.angle_errors = []

    def start_session(self):
        with self.lock:
            self.active = True
            self.session_start = time.time()
            self.duration = 0

            self.baseline_samples = []
            self.baseline_angle = None
            self.current_angle = None

            self.reps = 0
            self.stage = "rest"

            self.good_frames = 0
            self.bad_frames = 0
            self.total_pose_frames = 0
            self.unsafe_events = 0
            self.angle_errors = []

            self.feedback = "Session started. Hold still briefly, then move with control."
            self.status_colour = "neutral"

    def stop_session(self):
        with self.lock:
            self.active = False
            self.feedback = "Session stopped. You can save the session result now."
            self.status_colour = "neutral"

    def reset_session(self):
        with self.lock:
            self.active = False
            self.session_start = None
            self.duration = 0

            self.baseline_samples = []
            self.baseline_angle = None
            self.current_angle = None

            self.reps = 0
            self.stage = "rest"

            self.pose_detected = False
            self.feedback = "Reset complete. Start again when ready."
            self.status_colour = "neutral"

            self.good_frames = 0
            self.bad_frames = 0
            self.total_pose_frames = 0
            self.unsafe_events = 0
            self.angle_errors = []

    def get_latest_result(self):
        with self.lock:
            if self.total_pose_frames > 0:
                accuracy = int((self.good_frames / self.total_pose_frames) * 100)
            else:
                accuracy = 0

            if self.angle_errors:
                avg_angle_error = round(sum(self.angle_errors) / len(self.angle_errors), 2)
            else:
                avg_angle_error = 0

            return {
                "active": self.active,
                "duration": int(self.duration),
                "baseline_angle": self.baseline_angle,
                "current_angle": self.current_angle,
                "reps": self.reps,
                "stage": self.stage,
                "pose_detected": self.pose_detected,
                "feedback": self.feedback,
                "status_colour": self.status_colour,
                "accuracy": accuracy,
                "avg_angle_error": avg_angle_error,
                "unsafe_events": self.unsafe_events,
            }

    def recv(self, frame):
        image = frame.to_ndarray(format="rgb24")
        image = cv2.flip(image, 1)

        results = self.pose.process(image)
        detected_angle = None

        if results.pose_landmarks:
            self.pose_detected = True

            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
            )

            detected_angle = measure_angle(
                movement_name,
                results.pose_landmarks.landmark,
                selected_side,
            )
        else:
            self.pose_detected = False

        now = time.time()

        with self.lock:
            if self.active and self.session_start:
                self.duration = now - self.session_start

            direction = movement["direction"]

            if not self.pose_detected:
                self.feedback = "No pose detected. Adjust your camera or lighting."
                self.status_colour = "bad"

            elif detected_angle is not None:
                self.current_angle = detected_angle

                if self.active:
                    self.total_pose_frames += 1

                    if self.baseline_angle is None:
                        self.baseline_samples.append(detected_angle)

                        if len(self.baseline_samples) >= 20:
                            self.baseline_angle = float(np.median(self.baseline_samples))
                            self.feedback = "Baseline set. Begin moving with control."
                            self.status_colour = "neutral"
                    else:
                        unsafe = False
                        error = 0

                        if safe_limit_saved is not None:
                            if direction == "increase" and detected_angle > safe_limit_saved + 8:
                                unsafe = True
                                error = detected_angle - safe_limit_saved

                            if direction == "decrease" and detected_angle < safe_limit_saved - 8:
                                unsafe = True
                                error = safe_limit_saved - detected_angle

                        if unsafe:
                            self.bad_frames += 1
                            self.unsafe_events += 1
                            self.angle_errors.append(abs(error))
                            self.feedback = "STOP. You are going beyond your tested safe range."
                            self.status_colour = "bad"
                        else:
                            self.good_frames += 1
                            self.feedback = "Good form. Stay controlled and within your safe range."
                            self.status_colour = "good"

                        if direction == "increase":
                            movement_amount = detected_angle - self.baseline_angle
                        else:
                            movement_amount = self.baseline_angle - detected_angle

                        if rom_saved is not None and rom_saved > 0:
                            rep_threshold = max(10, min(35, rom_saved * 0.35))
                        else:
                            rep_threshold = 18

                        down_threshold = rep_threshold * 0.35

                        if self.stage == "rest" and movement_amount >= rep_threshold:
                            self.stage = "active"

                        elif self.stage == "active" and movement_amount <= down_threshold:
                            self.stage = "rest"
                            self.reps += 1

            active = self.active
            duration = int(self.duration)
            reps = self.reps
            feedback = self.feedback
            status_colour = self.status_colour
            current_angle = self.current_angle
            baseline_angle = self.baseline_angle
            pose_detected = self.pose_detected
            unsafe_events = self.unsafe_events

        if status_colour == "good":
            box_colour = (0, 150, 0)
            indicator_text = "GOOD"
        elif status_colour == "bad":
            box_colour = (0, 0, 200)
            indicator_text = "CHECK FORM"
        else:
            box_colour = (60, 60, 60)
            indicator_text = "READY"

        cv2.rectangle(image, (10, 10), (970, 255), (0, 0, 0), -1)
        cv2.rectangle(image, (10, 10), (970, 255), box_colour, 5)

        cv2.putText(
            image,
            indicator_text,
            (30, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            box_colour,
            3,
        )

        cv2.putText(
            image,
            feedback[:58],
            (30, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        if len(feedback) > 58:
            cv2.putText(
                image,
                feedback[58:116],
                (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

        pose_text = "POSE DETECTED" if pose_detected else "NO POSE DETECTED"
        pose_colour = (0, 255, 0) if pose_detected else (0, 0, 255)

        cv2.putText(
            image,
            pose_text,
            (30, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            pose_colour,
            2,
        )

        cv2.putText(
            image,
            f"Reps: {reps} | Time: {duration}s | Unsafe: {unsafe_events}",
            (30, 210),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        if current_angle is not None:
            cv2.putText(
                image,
                f"Angle: {int(current_angle)} degrees",
                (30, 245),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
            )

        return av.VideoFrame.from_ndarray(image, format="rgb24")


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

left, right = st.columns([3, 2])

with left:
    st.markdown("### Camera")

    ctx = webrtc_streamer(
        key=f"live-session-{exercise_id}-{selected_side}-{movement_name}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=LiveSessionProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
            },
            "audio": False,
        },
        async_processing=True,
    )

    st.caption("Click START inside the camera box and allow browser camera permission.")

with right:
    st.markdown(
        f"""
        <div class="session-card">
            <h3>{exercise_name}</h3>
            <p><b>Target Area:</b> {target_area}</p>
            <p><b>Difficulty:</b> {difficulty}</p>
            <p><b>Movement monitored:</b> {selected_side} {movement_name}</p>
            <p><b>Instruction:</b> {instructions}</p>
            <p><b>Safety cue:</b> {movement["instruction"]}</p>
            <p class="small-note">
                Green means the movement is within the safe tested range. Red means the user may be outside their tested ROM or the pose is not detected.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if safe_limit_saved is not None and rom_saved is not None:
        st.success(
            f"Using saved ROM: Safe limit {safe_limit_saved}°, ROM {rom_saved}°."
        )
    else:
        st.warning(
            "No saved ROM found for this movement. The session will still run, but safety checking is less personalised."
        )

    if st.button("Read Exercise Instructions Aloud", use_container_width=True):
        speak(
            f"{exercise_name}. {instructions}. "
            f"The system is monitoring your {selected_side.lower()} {movement_name.lower()}. "
            "Green means good. Red means check your form or stop if uncomfortable."
        )

    start_session = st.button("Start Session", use_container_width=True)
    stop_session = st.button("Stop Session", use_container_width=True)
    reset_session = st.button("Reset Session", use_container_width=True)

    if start_session:
        if ctx.video_processor:
            ctx.video_processor.start_session()
            speak("Session started. Follow the on-screen feedback. Stay within your safe range.")
        else:
            st.warning("Start the camera first.")

    if stop_session:
        if ctx.video_processor:
            ctx.video_processor.stop_session()
            speak("Session stopped. You can now save your session result.")
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
            st.markdown(f"<div class='status-good'>GREEN: {feedback}</div>", unsafe_allow_html=True)
        elif status_colour == "bad":
            st.markdown(f"<div class='status-bad'>RED: {feedback}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-neutral'>{feedback}</div>", unsafe_allow_html=True)

        screen_reader_status(feedback)

        st.write(f"Reps completed: **{latest['reps']}**")
        st.write(f"Duration: **{latest['duration']} seconds**")
        st.write(f"Accuracy score: **{latest['accuracy']}%**")
        st.write(f"Unsafe movement events: **{latest['unsafe_events']}**")

        if latest["current_angle"] is not None:
            st.write(f"Current angle: **{int(latest['current_angle'])}°**")

        if latest["baseline_angle"] is not None:
            st.write(f"Baseline angle: **{int(latest['baseline_angle'])}°**")

    else:
        st.warning("Start the camera first before beginning the session.")

st.divider()

if st.button("Save Session Result", use_container_width=True):
    if not ctx.video_processor:
        st.warning("Start the camera first.")

    else:
        latest = ctx.video_processor.get_latest_result()

        reps_completed = latest["reps"]
        duration = latest["duration"]
        accuracy_score = latest["accuracy"]
        avg_angle_error = latest["avg_angle_error"]

        if duration <= 0:
            st.warning("Start and stop a session before saving.")

        else:
            save_exercise_session(
                user_id=user_id,
                exercise_id=exercise_id,
                reps_completed=reps_completed,
                duration=duration,
                accuracy_score=accuracy_score,
                avg_angle_error=avg_angle_error,
            )

            st.success(
                f"Session saved. Reps: {reps_completed}, Duration: {duration}s, Accuracy: {accuracy_score}%."
            )

            speak("Session saved successfully.")

bottom_nav()