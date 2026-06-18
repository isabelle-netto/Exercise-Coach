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


def speak(text):
    if not st.session_state.get("audio_feedback"):
        st.warning("Audio feedback is turned off. Enable it in Accessibility Settings.")
        return

    safe_text = json.dumps(text)
    unique_key = str(time.time()).replace(".", "")

    components.html(
        f"""
        <div id="speech-{unique_key}"></div>
        <script>
        setTimeout(() => {{
            const utterance = new SpeechSynthesisUtterance({safe_text});
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }}, 200);
        </script>
        """,
        height=1
    )


def speak_sequence(messages):
    if not st.session_state.get("audio_feedback"):
        st.warning("Audio feedback is turned off. Enable it in Accessibility Settings.")
        return

    safe_messages = json.dumps(messages)
    unique_key = str(time.time()).replace(".", "")

    components.html(
        f"""
        <div id="speech-sequence-{unique_key}"></div>
        <script>
        window.speechSynthesis.cancel();
        const messages = {safe_messages};

        messages.forEach((item) => {{
            setTimeout(() => {{
                const speech = new SpeechSynthesisUtterance(item.text);
                speech.rate = 0.9;
                speech.pitch = 1;
                speech.volume = 1;
                window.speechSynthesis.speak(speech);
            }}, item.delay);
        }});
        </script>
        """,
        height=1
    )


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1],
        a[0] - b[0]
    )

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

if "last_spoken_done" not in st.session_state:
    st.session_state["last_spoken_done"] = None


TESTS = {
    "Shoulder Flexion": {
        "instruction": "Lift your selected arm forward as high as comfortable and hold.",
        "result": "Shoulder_Flexion",
        "goal": "max"
    },
    "Shoulder Abduction": {
        "instruction": "Lift your selected arm out to the side as high as comfortable and hold.",
        "result": "Shoulder_Abduction",
        "goal": "max"
    },
    "Elbow Flexion": {
        "instruction": "Bend your selected elbow and bring your hand toward your shoulder.",
        "result": "Elbow_Flexion",
        "goal": "min"
    },
    "Hip Flexion": {
        "instruction": "Lift your selected knee upward toward your chest as high as comfortable.",
        "result": "Hip_Flexion",
        "goal": "min"
    },
    "Knee Flexion": {
        "instruction": "Bend your selected knee as much as comfortable.",
        "result": "Knee_Flexion",
        "goal": "min"
    },
    "Knee Extension": {
        "instruction": "Straighten your selected knee as much as comfortable.",
        "result": "Knee_Extension",
        "goal": "max"
    },
    "Ankle Mobility": {
        "instruction": "Move your selected foot through a comfortable toe point or toe lift position.",
        "result": "Ankle_Mobility",
        "goal": "max"
    },
}


st.markdown("""
<style>
.mobility-card {
    background: rgba(31,36,33,0.88);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
}

.mobility-card h3 {
    margin-top: 0;
    font-weight: 900;
}

.small-note {
    opacity: 0.75;
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
""", unsafe_allow_html=True)


top1, top2, top3 = st.columns(3)

with top1:
    test_position = st.radio(
        "How will you perform the test?",
        ["Seated", "Standing", "Supported / assisted"],
        horizontal=False
    )

with top2:
    selected_side = st.radio(
        "Which side do you want to test?",
        ["Right", "Left"],
        horizontal=False
    )

with top3:
    available_limbs = st.multiselect(
        "Which limbs can be tested today?",
        ["Right arm", "Left arm", "Right leg", "Left leg"],
        default=["Right arm", "Left arm", "Right leg", "Left leg"]
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

test_name = st.selectbox("Choose mobility test", possible_tests)
test = TESTS[test_name]

screen_reader_status(
    f"Selected test is {selected_side} {test_name}. {test['instruction']}"
)


class MobilityProcessor:
    def __init__(self):
        self.lock = Lock()

        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.45,
            min_tracking_confidence=0.45
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
            self.status = "Get ready. Recording starts in 6 seconds."

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
            if self.phase == "idle":
                self.status = "Ready. Press Start Measurement."

            elif self.phase == "countdown":
                elapsed = now - self.countdown_start
                remaining = max(0, 6 - int(elapsed))
                self.status = f"Get ready. Recording starts in {remaining} seconds."

                if elapsed >= 6:
                    self.phase = "recording"
                    self.recording_start = now
                    self.status = "Recording started. 8 seconds remaining."

            elif self.phase == "recording":
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
                        self.status = f"Test completed. Best result: {int(self.done_value)} degrees."
                    else:
                        self.status = "Test completed. No pose detected."

            elif self.phase == "done":
                if self.done_value is not None:
                    self.status = f"Test completed. Best result: {int(self.done_value)} degrees."
                else:
                    self.status = "Test completed. No pose detected."

            status_text = self.status
            current_value = self.current_value
            pose_detected = self.pose_detected

        if pose_detected:
            pose_text = "POSE DETECTED"
            pose_colour = (0, 255, 0)
        else:
            pose_text = "NO POSE DETECTED"
            pose_colour = (0, 0, 255)

        cv2.rectangle(image, (10, 10), (950, 210), (0, 0, 0), -1)

        cv2.putText(
            image,
            status_text[:60],
            (30, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (255, 255, 255),
            2
        )

        if len(status_text) > 60:
            cv2.putText(
                image,
                status_text[60:120],
                (30, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (255, 255, 255),
                2
            )

        cv2.putText(
            image,
            pose_text,
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            pose_colour,
            2
        )

        if current_value is not None:
            cv2.putText(
                image,
                f"Current angle: {int(current_value)} degrees",
                (30, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.68,
                (255, 255, 255),
                2
            )

        return av.VideoFrame.from_ndarray(image, format="rgb24")


RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})


left, right = st.columns([3, 2])

with left:
    st.markdown("### Camera")

    ctx = webrtc_streamer(
        key=f"mobility-test-{selected_side}-{test_name}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=MobilityProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480}
            },
            "audio": False
        },
        async_processing=True,
    )

    st.caption(
        "Click START inside the camera box first and allow browser camera permission."
    )

with right:
    st.markdown(f"""
    <div class="mobility-card">
        <h3>{selected_side} {test_name}</h3>
        <p><b>Instruction:</b> {test["instruction"]}</p>
        <p><b>Get ready time:</b> 6 seconds</p>
        <p><b>Recording time:</b> 8 seconds</p>
        <p><b>Scoring:</b> The system records your best angle across the full 8-second test, not only the final frame.</p>
        <p class="small-note">
            Make sure the tested limb is visible in the camera. Use good lighting and sit or stand slightly further away if pose detection does not appear.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Read Instructions Aloud", use_container_width=True):
        speak(
            f"{selected_side} {test_name}. "
            f"{test['instruction']} "
            "Recording starts after a six second countdown. "
            "The test will record for eight seconds. "
            "The system records your best angle across the full test."
        )

    start_pressed = st.button("Start Measurement", use_container_width=True)
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
        st.session_state["last_spoken_done"] = None
        speak("Measurement reset.")

    st.markdown("### Test Status")

    if ctx.video_processor:
        with ctx.video_processor.lock:
            status = ctx.video_processor.status
            done_value = ctx.video_processor.done_value
            phase = ctx.video_processor.phase
            pose_detected = ctx.video_processor.pose_detected
            current_value = ctx.video_processor.current_value

        if phase == "countdown":
            st.warning(status)
        elif phase == "recording":
            st.info(status)
        elif phase == "done":
            st.success(status)
        else:
            st.write(status)

        screen_reader_status(status)

        if pose_detected:
            st.success("Pose detected.")
        else:
            st.warning("No pose detected yet.")

        if current_value is not None:
            st.write(f"Current angle: **{int(current_value)} degrees**")

        if phase == "done":
            result_key = f"{selected_side}_{test['result']}"

            if done_value is not None:
                st.session_state["mobility_results"][result_key] = {
                    "value": int(done_value),
                    "unit": "degrees"
                }

                st.success(f"{result_key}: {int(done_value)} degrees")

                if st.session_state["last_spoken_done"] != result_key:
                    speak(
                        f"Test complete. Your best result is {int(done_value)} degrees."
                    )
                    st.session_state["last_spoken_done"] = result_key

            else:
                st.error(
                    "No pose was detected clearly enough. Try again with better lighting and more distance from the camera."
                )
    else:
        st.warning("Start the camera first before pressing Start Measurement.")


st.divider()

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