import streamlit as st
import mediapipe as mp
import numpy as np
import av
import time
from threading import Lock
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from ui import apply_style, bottom_nav
from accessibility import accessibility_settings_panel, speak, screen_reader_status

st.set_page_config(page_title="Mobility Test", layout="wide")
apply_style()

st.title("Adaptive Mobility Test")
accessibility_settings_panel()

mp_pose = mp.solutions.pose


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


def format_value(value, unit):
    if value is None:
        return "N/A"
    if unit == "score":
        return f"{int(value)}/100"
    return f"{int(value)} degrees"


if "mobility_results" not in st.session_state:
    st.session_state["mobility_results"] = {}

if "latest_result_message" not in st.session_state:
    st.session_state["latest_result_message"] = ""


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
    possible_tests += [
        "Shoulder Flexion",
        "Shoulder Abduction",
        "Elbow Flexion"
    ]

if leg_available:
    possible_tests += [
        "Hip Flexion",
        "Knee Flexion",
        "Knee Extension",
        "Ankle Mobility"
    ]

if not possible_tests:
    st.error("No available tests based on selected limb availability.")
    bottom_nav()
    st.stop()


TESTS = {
    "Shoulder Flexion": {
        "instruction": "Lift your selected arm forward as high as comfortable and hold.",
        "result": "Shoulder_Flexion",
        "goal": "max",
        "unit": "degrees"
    },
    "Shoulder Abduction": {
        "instruction": "Lift your selected arm out to the side as high as comfortable and hold.",
        "result": "Shoulder_Abduction",
        "goal": "max",
        "unit": "degrees"
    },
    "Elbow Flexion": {
        "instruction": "Bend your selected elbow and bring your hand toward your shoulder. Hold the most bent position.",
        "result": "Elbow_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Hip Flexion": {
        "instruction": "Lift your selected knee upward toward your chest as high as comfortable and hold.",
        "result": "Hip_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Knee Flexion": {
        "instruction": "Bend your selected knee as much as comfortable and hold.",
        "result": "Knee_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Knee Extension": {
        "instruction": "Straighten your selected knee as much as comfortable and hold.",
        "result": "Knee_Extension",
        "goal": "max",
        "unit": "degrees"
    },
    "Ankle Mobility": {
        "instruction": "Move your selected foot through a comfortable toe point or toe lift position and hold.",
        "result": "Ankle_Mobility",
        "goal": "max",
        "unit": "degrees"
    }
}

test_name = st.selectbox("Choose mobility test", possible_tests)
test = TESTS[test_name]

st.markdown(f"""
<div class="card">
    <h3>{selected_side} {test_name}</h3>
    <p><b>Instruction:</b> {test["instruction"]}</p>
    <p><b>Countdown:</b> After pressing Start Measurement, you will have 6 seconds to get ready.</p>
    <p><b>Recording:</b> The system records for 8 seconds.</p>
</div>
""", unsafe_allow_html=True)

screen_reader_status(f"Selected test is {selected_side} {test_name}. {test['instruction']}")

if st.button("Read Instructions Aloud", use_container_width=True):
    speak(f"{selected_side} {test_name}. {test['instruction']} Recording starts after a six second countdown.")


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


class MobilityProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.phase = "idle"
        self.countdown_start = None
        self.recording_start = None
        self.best_value = None
        self.current_value = None
        self.done_value = None
        self.status = "Ready"

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
            self.status = "Ready"

    def recv(self, frame):
        image = frame.to_ndarray(format="rgb24")
        results = self.pose.process(image)

        now = time.time()

        with self.lock:
            phase = self.phase

        if phase == "countdown":
            with self.lock:
                elapsed = now - self.countdown_start
                remaining = max(0, 6 - int(elapsed))
                self.status = f"Countdown. Recording starts in {remaining} seconds."

                if elapsed >= 6:
                    self.phase = "recording"
                    self.recording_start = now
                    self.status = "Start now. Recording started."

        elif phase == "recording":
            value = None

            if results.pose_landmarks:
                value = measure_test(
                    test_name,
                    results.pose_landmarks.landmark,
                    selected_side
                )

            with self.lock:
                elapsed = now - self.recording_start
                remaining = max(0, 8 - int(elapsed))

                if value is not None:
                    self.current_value = value

                    if self.best_value is None:
                        self.best_value = value
                    elif test["goal"] == "max":
                        self.best_value = max(self.best_value, value)
                    else:
                        self.best_value = min(self.best_value, value)

                self.status = f"Recording. Time left {remaining} seconds."

                if elapsed >= 8:
                    self.phase = "done"
                    self.done_value = self.best_value
                    self.status = "Test completed."

        elif phase == "done":
            with self.lock:
                if self.done_value is not None:
                    self.status = f"Test completed. Result {format_value(self.done_value, test['unit'])}."
                else:
                    self.status = "Test completed. No pose detected."

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

st.info("Click START on the camera box and allow camera permission.")

col1, col2, col3 = st.columns(3)

with col1:
    start_pressed = st.button("Start Measurement", use_container_width=True)

with col2:
    reset_pressed = st.button("Reset Measurement", use_container_width=True)

with col3:
    skip_pressed = st.button("Skip This Test", use_container_width=True)

if start_pressed and ctx.video_processor:
    ctx.video_processor.start_measurement()
    speak("Get ready. Six. Five. Four. Three. Two. One. Start now.")

if reset_pressed and ctx.video_processor:
    ctx.video_processor.reset()
    speak("Measurement reset.")

if skip_pressed:
    result_key = f"{selected_side}_{test['result']}"
    st.session_state["mobility_results"][result_key] = {
        "value": "Skipped",
        "unit": "skipped"
    }
    st.warning(f"{result_key} skipped.")

if ctx.video_processor:
    with ctx.video_processor.lock:
        status = ctx.video_processor.status
        done_value = ctx.video_processor.done_value
        phase = ctx.video_processor.phase

    st.info(status)
    screen_reader_status(status)

    if phase == "done" and done_value is not None:
        result_key = f"{selected_side}_{test['result']}"

        st.session_state["mobility_results"][result_key] = {
            "value": int(done_value),
            "unit": test["unit"]
        }

        message = f"{result_key}: {format_value(done_value, test['unit'])}"
        st.session_state["latest_result_message"] = message
        st.success(message)

st.subheader("Latest Result")

if st.session_state.get("latest_result_message"):
    st.success(st.session_state["latest_result_message"])
else:
    st.info("No completed result yet.")

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