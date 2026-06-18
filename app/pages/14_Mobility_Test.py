import streamlit as st
import mediapipe as mp
import numpy as np
import av
import time
import cv2
import json
from threading import Lock
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import streamlit.components.v1 as components

from ui import apply_style, bottom_nav
from accessibility import accessibility_settings_panel, screen_reader_status

st.set_page_config(page_title="Mobility Test", layout="wide")
apply_style()

st.title("Adaptive Mobility Test")
accessibility_settings_panel()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def speak_sequence(messages):
    if not st.session_state.get("audio_feedback"):
        return

    safe_messages = json.dumps(messages)

    components.html(f"""
    <script>
    window.speechSynthesis.cancel();

    const messages = {safe_messages};

    messages.forEach((item) => {{
        setTimeout(() => {{
            const speech = new SpeechSynthesisUtterance(item.text);
            speech.rate = 0.85;
            speech.volume = 1;
            window.speechSynthesis.speak(speech);
        }}, item.delay);
    }});
    </script>
    """, height=0)


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def get_landmark(landmarks, landmark):
    point = landmarks[landmark.value]
    return [point.x, point.y]


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


def measure_test(test_name, landmarks, side):
    pts = get_side_points(landmarks, side)

    if test_name in ["Shoulder Flexion", "Shoulder Abduction"]:
        return calculate_angle(pts["hip"], pts["shoulder"], pts["elbow"])

    if test_name == "Elbow Flexion":
        return calculate_angle(pts["shoulder"], pts["elbow"], pts["wrist"])

    if test_name == "Hip Flexion":
        return calculate_angle(pts["shoulder"], pts["hip"], pts["knee"])

    if test_name in ["Knee Flexion", "Knee Extension"]:
        return calculate_angle(pts["hip"], pts["knee"], pts["ankle"])

    if test_name == "Ankle Mobility":
        return calculate_angle(pts["knee"], pts["ankle"], pts["foot"])

    return None


if "mobility_results" not in st.session_state:
    st.session_state["mobility_results"] = {}

test_position = st.radio(
    "How will you perform the test?",
    ["Seated", "Standing", "Supported / assisted"],
    horizontal=True
)

available_limbs = st.multiselect(
    "Which limbs can be tested today?",
    ["Right arm", "Left arm", "Right leg", "Left leg"],
    default=["Right arm", "Left arm", "Right leg", "Left leg"]
)

selected_side = st.radio(
    "Which side do you want to test?",
    ["Right", "Left"],
    horizontal=True
)

if selected_side == "Right":
    arm_available = "Right arm" in available_limbs
    leg_available = "Right leg" in available_limbs
else:
    arm_available = "Left arm" in available_limbs
    leg_available = "Left leg" in available_limbs

possible_tests = []

if arm_available:
    possible_tests += ["Shoulder Flexion", "Shoulder Abduction", "Elbow Flexion"]

if leg_available:
    possible_tests += ["Hip Flexion", "Knee Flexion", "Knee Extension", "Ankle Mobility"]

if not possible_tests:
    st.error("No available tests based on selected limb availability.")
    bottom_nav()
    st.stop()

TESTS = {
    "Shoulder Flexion": {"instruction": "Lift your selected arm forward as high as comfortable and hold.", "result": "Shoulder_Flexion", "goal": "max"},
    "Shoulder Abduction": {"instruction": "Lift your selected arm out to the side as high as comfortable and hold.", "result": "Shoulder_Abduction", "goal": "max"},
    "Elbow Flexion": {"instruction": "Bend your selected elbow and bring your hand toward your shoulder.", "result": "Elbow_Flexion", "goal": "min"},
    "Hip Flexion": {"instruction": "Lift your selected knee upward toward your chest as high as comfortable.", "result": "Hip_Flexion", "goal": "min"},
    "Knee Flexion": {"instruction": "Bend your selected knee as much as comfortable.", "result": "Knee_Flexion", "goal": "min"},
    "Knee Extension": {"instruction": "Straighten your selected knee as much as comfortable.", "result": "Knee_Extension", "goal": "max"},
    "Ankle Mobility": {"instruction": "Move your selected foot through a comfortable toe point or toe lift position.", "result": "Ankle_Mobility", "goal": "max"},
}

test_name = st.selectbox("Choose mobility test", possible_tests)
test = TESTS[test_name]

st.markdown(f"""
<div class="card">
    <h3>{selected_side} {test_name}</h3>
    <p><b>Instruction:</b> {test["instruction"]}</p>
    <p><b>Get ready:</b> 6 seconds</p>
    <p><b>Recording:</b> 8 seconds</p>
</div>
""", unsafe_allow_html=True)

screen_reader_status(f"Selected test is {selected_side} {test_name}. {test['instruction']}")


class MobilityProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.phase = "idle"
        self.countdown_start = None
        self.recording_start = None
        self.best_value = None
        self.current_value = None
        self.done_value = None
        self.status = "Ready. Press Start Measurement."
        self.pose_detected = False

    def start_measurement(self):
        with self.lock:
            self.phase = "countdown"
            self.countdown_start = time.time()
            self.recording_start = None
            self.best_value = None
            self.current_value = None
            self.done_value = None
            self.status = "Get ready."

    def reset(self):
        with self.lock:
            self.phase = "idle"
            self.countdown_start = None
            self.recording_start = None
            self.best_value = None
            self.current_value = None
            self.done_value = None
            self.status = "Ready. Press Start Measurement."
            self.pose_detected = False

    def recv(self, frame):
        image = frame.to_ndarray(format="rgb24")
        image = cv2.flip(image, 1)

        results = self.pose.process(image)
        now = time.time()

        if results.pose_landmarks:
            self.pose_detected = True
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )
        else:
            self.pose_detected = False

        with self.lock:
            phase = self.phase

            if phase == "idle":
                self.status = "Ready. Press Start Measurement."

            elif phase == "countdown":
                elapsed = now - self.countdown_start
                remaining = max(0, 6 - int(elapsed))

                self.status = f"Get ready. Recording starts in {remaining} seconds."

                if elapsed >= 6:
                    self.phase = "recording"
                    self.recording_start = now
                    self.status = "Recording started."

            elif phase == "recording":
                elapsed = now - self.recording_start
                remaining = max(0, 8 - int(elapsed))

                if results.pose_landmarks:
                    value = measure_test(
                        test_name,
                        results.pose_landmarks.landmark,
                        selected_side
                    )

                    if value is not None:
                        self.current_value = value

                        if self.best_value is None:
                            self.best_value = value
                        elif test["goal"] == "max":
                            self.best_value = max(self.best_value, value)
                        else:
                            self.best_value = min(self.best_value, value)

                self.status = f"Recording. Time left: {remaining} seconds."

                if elapsed >= 8:
                    self.phase = "done"
                    self.done_value = self.best_value

                    if self.done_value is not None:
                        self.status = f"Test completed. Result: {int(self.done_value)} degrees."
                    else:
                        self.status = "Test completed. No pose detected."

            elif phase == "done":
                if self.done_value is not None:
                    self.status = f"Test completed. Result: {int(self.done_value)} degrees."
                else:
                    self.status = "Test completed. No pose detected."

            status_text = self.status
            current_value = self.current_value
            pose_detected = self.pose_detected

        if pose_detected:
            pose_text = "Pose detected"
        else:
            pose_text = "No pose detected"

        cv2.rectangle(image, (20, 20), (760, 120), (0, 0, 0), -1)
        cv2.putText(image, status_text, (35, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(image, pose_text, (35, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if current_value is not None:
            cv2.putText(image, f"Current angle: {int(current_value)} degrees", (35, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(image, format="rgb24")


RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

ctx = webrtc_streamer(
    key=f"mobility-test-{selected_side}-{test_name}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=MobilityProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

st.info("Click START on the camera box first, allow camera permission, then press Start Measurement.")

col1, col2 = st.columns(2)

with col1:
    start_pressed = st.button("Start Measurement", use_container_width=True)

with col2:
    reset_pressed = st.button("Reset Measurement", use_container_width=True)

if start_pressed and ctx.video_processor:
    ctx.video_processor.start_measurement()

    speak_sequence([
        {"text": "Get ready. Recording starts in six seconds.", "delay": 0},
        {"text": "Six", "delay": 1000},
        {"text": "Five", "delay": 2000},
        {"text": "Four", "delay": 3000},
        {"text": "Three", "delay": 4000},
        {"text": "Two", "delay": 5000},
        {"text": "One. Start now.", "delay": 6000},
        {"text": "Recording. Eight seconds remaining.", "delay": 7000},
        {"text": "Seven", "delay": 8000},
        {"text": "Six", "delay": 9000},
        {"text": "Five", "delay": 10000},
        {"text": "Four", "delay": 11000},
        {"text": "Three", "delay": 12000},
        {"text": "Two", "delay": 13000},
        {"text": "One", "delay": 14000},
        {"text": "Test completed.", "delay": 15000},
    ])

if reset_pressed and ctx.video_processor:
    ctx.video_processor.reset()
    speak_sequence([{"text": "Measurement reset.", "delay": 0}])

if ctx.video_processor:
    with ctx.video_processor.lock:
        status = ctx.video_processor.status
        done_value = ctx.video_processor.done_value
        phase = ctx.video_processor.phase
        pose_detected = ctx.video_processor.pose_detected

    st.subheader("Test Status")
    st.info(status)

    if pose_detected:
        st.success("Pose detected.")
    else:
        st.warning("No pose detected yet. Make sure your full body or tested limb is visible.")

    if phase == "done":
        result_key = f"{selected_side}_{test['result']}"

        if done_value is not None:
            st.session_state["mobility_results"][result_key] = {
                "value": int(done_value),
                "unit": "degrees"
            }

            st.success(f"{result_key}: {int(done_value)} degrees")
        else:
            st.error("No pose was detected clearly enough. Try again with better lighting and more distance from the camera.")

st.subheader("Saved Mobility Results")

if not st.session_state["mobility_results"]:
    st.info("No saved mobility results yet.")
else:
    for key, result in st.session_state["mobility_results"].items():
        st.write(f"**{key}:** {result['value']} {result['unit']}")

if st.button("Save All Mobility Results", use_container_width=True):
    for key, result in st.session_state["mobility_results"].items():
        st.session_state[key] = result["value"]

    st.success("Mobility results saved.")

bottom_nav()