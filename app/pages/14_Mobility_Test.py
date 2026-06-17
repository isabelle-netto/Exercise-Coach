import streamlit as st
import cv2
import mediapipe as mp
import av
import time
from threading import Lock

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from ui import apply_style, bottom_nav
from accessibility import (
    accessibility_settings_panel,
    speak,
    screen_reader_status,
    voice_control_box
)

st.set_page_config(page_title="Adaptive Mobility Test", layout="wide")
apply_style()

st.title("Adaptive Mobility Assessment")
st.write("This assessment supports seated, standing, supported, left-side, right-side, and skipped tests.")

accessibility_settings_panel()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    import numpy as np

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def get_landmark(landmarks, landmark):
    return [landmarks[landmark.value].x, landmarks[landmark.value].y]


def horizontal_distance(a, b):
    return abs(a[0] - b[0])


def format_value(value, unit):
    if value == "Skipped":
        return "Skipped"
    if value is None:
        return "N/A"
    if unit == "score":
        return f"{int(value)}/100"
    return f"{int(value)} degrees"


def format_value_short(value, unit):
    if value == "Skipped":
        return "Skipped"
    if value is None:
        return "N/A"
    if unit == "score":
        return f"{int(value)}/100"
    return f"{int(value)}°"


# ---------------- SETUP ----------------

st.subheader("Step 1: Accessibility Setup")

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
    possible_tests.extend([
        "Shoulder Flexion",
        "Shoulder Abduction",
        "Horizontal Adduction",
        "Horizontal Abduction",
        "Elbow Flexion"
    ])

if leg_available:
    possible_tests.extend([
        "Hip Flexion",
        "Hip Abduction",
        "Hip Adduction",
        "Knee Flexion",
        "Knee Extension",
        "Ankle Mobility"
    ])

if not possible_tests:
    st.error("No available tests based on the selected limb availability.")
    bottom_nav()
    st.stop()


TESTS = {
    "Shoulder Flexion": {
        "seated": "Sit upright. Keep one arm straight. Slowly lift your selected arm forward, like reaching for something in front of you. Lift as high as comfortable and hold.",
        "standing": "Stand sideways if possible. Keep one arm straight. Slowly lift your selected arm forward as high as comfortable and hold.",
        "position": "Shoulder, elbow, wrist, and hip should be visible.",
        "result": "Shoulder_Flexion",
        "goal": "max",
        "unit": "degrees"
    },
    "Shoulder Abduction": {
        "seated": "Sit facing the camera. Keep one arm straight. Slowly lift your selected arm out to the side, like making half of a star shape. Hold your highest comfortable position.",
        "standing": "Stand facing the camera. Keep one arm straight. Slowly lift your selected arm out to the side as high as comfortable and hold.",
        "position": "Shoulders, arms, and upper body should be visible.",
        "result": "Shoulder_Abduction",
        "goal": "max",
        "unit": "degrees"
    },
    "Horizontal Adduction": {
        "seated": "Sit facing the camera. Lift your selected arm in front of your chest. Move it across your chest toward the opposite shoulder and hold.",
        "standing": "Stand facing the camera. Lift your selected arm in front of your chest. Move it across your chest toward the opposite shoulder and hold.",
        "position": "Both shoulders and the selected wrist should be visible.",
        "result": "Horizontal_Adduction",
        "goal": "max",
        "unit": "score"
    },
    "Horizontal Abduction": {
        "seated": "Sit facing the camera. Start with your selected arm in front of your chest. Open the arm outward to the side like opening a door and hold.",
        "standing": "Stand facing the camera. Start with your selected arm in front of your chest. Open the arm outward to the side and hold.",
        "position": "Both shoulders and the selected wrist should be visible.",
        "result": "Horizontal_Abduction",
        "goal": "max",
        "unit": "score"
    },
    "Elbow Flexion": {
        "seated": "Sit facing the camera. Keep your upper arm still. Start with your arm straight, then bend your elbow and bring your hand toward your shoulder. Hold the most bent position.",
        "standing": "Stand or sit facing the camera. Keep your upper arm still. Bend your elbow like doing a bicep curl and hold.",
        "position": "Shoulder, elbow, and wrist should be visible.",
        "result": "Elbow_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Hip Flexion": {
        "seated": "Sit upright. Slowly lift your selected knee upward toward your chest as high as comfortable. Hold the highest position.",
        "standing": "Stand sideways if possible. Slowly lift your selected knee upward toward your chest as high as comfortable and hold.",
        "position": "Hip and knee should be visible. Full leg visibility is better.",
        "result": "Hip_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Hip Abduction": {
        "seated": "Sit upright. Move your selected knee outward to the side as far as comfortable. Hold the furthest position.",
        "standing": "Stand facing the camera. Move your selected leg out to the side as far as comfortable and hold.",
        "position": "Hips, knees, and ankles should be visible if possible.",
        "result": "Hip_Abduction",
        "goal": "max",
        "unit": "degrees"
    },
    "Hip Adduction": {
        "seated": "Sit upright. Move your selected knee inward toward the middle of your body. Hold the furthest comfortable position.",
        "standing": "Stand facing the camera. Move your selected leg inward across the middle of your body and hold.",
        "position": "Hips, knees, and ankles should be visible if possible.",
        "result": "Hip_Adduction",
        "goal": "max",
        "unit": "degrees"
    },
    "Knee Flexion": {
        "seated": "Sit sideways to the camera if possible. Slowly bend your selected knee by moving your lower leg backward as much as comfortable. Hold the deepest bend.",
        "standing": "Stand sideways to the camera. Slowly bend your selected knee or do a small comfortable squat. Hold the deepest comfortable bend.",
        "position": "Hip, knee, and ankle should be visible.",
        "result": "Knee_Flexion",
        "goal": "min",
        "unit": "degrees"
    },
    "Knee Extension": {
        "seated": "Sit sideways to the camera. Slowly straighten your selected knee as much as possible. Hold the straightest comfortable position.",
        "standing": "Stand sideways to the camera. Straighten your selected knee as much as possible and hold.",
        "position": "Hip, knee, and ankle should be visible.",
        "result": "Knee_Extension",
        "goal": "max",
        "unit": "degrees"
    },
    "Ankle Mobility": {
        "seated": "Sit with your selected foot visible. Slowly point your toes away from you, then lift them back toward you. Hold your strongest comfortable position.",
        "standing": "Stand sideways to the camera. Slowly rise onto your toes as high as possible without jumping. Hold the highest toe-rise position.",
        "position": "Knee, ankle, and foot should be visible.",
        "result": "Ankle_Mobility",
        "goal": "max",
        "unit": "degrees"
    }
}


test_name = st.selectbox("Choose mobility test", possible_tests)
test = TESTS[test_name]
instruction = test["seated"] if test_position == "Seated" else test["standing"]

instruction_text = (
    f"{selected_side} {test_name}. "
    f"{instruction}. "
    f"Camera guidance: {test['position']}. "
    "After pressing start measurement, you will hear a countdown from six to one. "
    "Start moving after you hear start now. The recording lasts eight seconds."
)

st.markdown(f"""
<div class="card">
    <h3>{selected_side} {test_name}</h3>
    <p><b>What to do:</b> {instruction}</p>
    <p><b>Camera guidance:</b> {test["position"]}</p>
    <p><b>Countdown:</b> You will hear 6, 5, 4, 3, 2, 1, then “Start now”.</p>
    <p><b>Recording:</b> The system records for 8 seconds. Move slowly and hold your furthest comfortable position near the end.</p>
    <p><b>Skip:</b> If this test is not possible for your body, skip it.</p>
</div>
""", unsafe_allow_html=True)

screen_reader_status(f"Selected test is {selected_side} {test_name}. {instruction}")

if st.button("Read Instructions Aloud", use_container_width=True):
    st.session_state["speech_nonce"] = st.session_state.get("speech_nonce", 0) + 1
    speak(instruction_text)


# ---------------- STATE ----------------

if "mobility_results" not in st.session_state:
    st.session_state["mobility_results"] = {}

if "latest_result_message" not in st.session_state:
    st.session_state["latest_result_message"] = ""

if "spoken_countdown_step" not in st.session_state:
    st.session_state["spoken_countdown_step"] = None

if "spoken_recording_step" not in st.session_state:
    st.session_state["spoken_recording_step"] = None

if "spoken_test_done" not in st.session_state:
    st.session_state["spoken_test_done"] = False


# ---------------- VOICE CONTROL ----------------

voice_command = voice_control_box()

voice_start = voice_command in ["start test", "start measurement", "begin test", "begin measurement"]
voice_read = voice_command in ["read instructions", "repeat instructions"]
voice_reset = voice_command in ["reset test", "reset measurement"]
voice_skip = voice_command in ["skip test", "skip this test"]
voice_save = voice_command in ["save results", "save result", "save all results"]

if voice_read:
    speak(instruction_text)


# ---------------- LANDMARKS ----------------

def side_landmarks(landmarks, side):
    if side == "Right":
        return {
            "shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER),
            "elbow": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW),
            "wrist": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST),
            "hip": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_HIP),
            "knee": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_KNEE),
            "ankle": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE),
            "foot": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_FOOT_INDEX),
            "opposite_shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER)
        }

    return {
        "shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER),
        "elbow": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW),
        "wrist": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_WRIST),
        "hip": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_HIP),
        "knee": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_KNEE),
        "ankle": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_ANKLE),
        "foot": get_landmark(landmarks, mp_pose.PoseLandmark.LEFT_FOOT_INDEX),
        "opposite_shoulder": get_landmark(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER)
    }


def measure_selected_test(test_name, landmarks, side):
    pts = side_landmarks(landmarks, side)

    if test_name in ["Shoulder Flexion", "Shoulder Abduction"]:
        return calculate_angle(pts["hip"], pts["shoulder"], pts["elbow"])

    if test_name == "Horizontal Adduction":
        shoulder_width = horizontal_distance(pts["shoulder"], pts["opposite_shoulder"])
        if shoulder_width == 0:
            return None
        distance_to_opposite = horizontal_distance(pts["wrist"], pts["opposite_shoulder"])
        score = max(0, 100 - ((distance_to_opposite / shoulder_width) * 100))
        return min(score, 100)

    if test_name == "Horizontal Abduction":
        shoulder_width = horizontal_distance(pts["shoulder"], pts["opposite_shoulder"])
        if shoulder_width == 0:
            return None
        outward_distance = horizontal_distance(pts["wrist"], pts["shoulder"])
        score = (outward_distance / shoulder_width) * 100
        return min(score, 100)

    if test_name == "Elbow Flexion":
        return calculate_angle(pts["shoulder"], pts["elbow"], pts["wrist"])

    if test_name == "Hip Flexion":
        return calculate_angle(pts["shoulder"], pts["hip"], pts["knee"])

    if test_name in ["Hip Abduction", "Hip Adduction"]:
        return calculate_angle(pts["shoulder"], pts["hip"], pts["knee"])

    if test_name in ["Knee Flexion", "Knee Extension"]:
        return calculate_angle(pts["hip"], pts["knee"], pts["ankle"])

    if test_name == "Ankle Mobility":
        return calculate_angle(pts["knee"], pts["ankle"], pts["foot"])

    return None


class MobilityProcessor:
    def __init__(self):
        self.lock = Lock()
        self.pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self.phase = "idle"
        self.countdown_start = None
        self.recording_start = None
        self.current_value = None
        self.best_value = None
        self.done_value = None
        self.status = "Ready"

    def start_measurement(self):
        with self.lock:
            self.phase = "countdown"
            self.countdown_start = time.time()
            self.recording_start = None
            self.current_value = None
            self.best_value = None
            self.done_value = None
            self.status = "Get ready"

    def reset(self):
        with self.lock:
            self.phase = "idle"
            self.countdown_start = None
            self.recording_start = None
            self.current_value = None
            self.best_value = None
            self.done_value = None
            self.status = "Ready"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

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

            cv2.putText(image, f"Get ready: {remaining}", (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        elif phase == "recording":
            value = None

            if results.pose_landmarks:
                value = measure_selected_test(test_name, results.pose_landmarks.landmark, selected_side)

            with self.lock:
                elapsed = now - self.recording_start
                remaining = max(0, 8 - int(elapsed))

                if value is not None:
                    self.current_value = value

                    if self.best_value is None:
                        self.best_value = value
                    else:
                        if test["goal"] == "max":
                            self.best_value = max(self.best_value, value)
                        else:
                            self.best_value = min(self.best_value, value)

                self.status = f"Recording. Time left {remaining} seconds."

                if elapsed >= 8:
                    self.phase = "done"
                    self.done_value = self.best_value
                    self.status = "Test completed."

                current_display = self.current_value
                best_display = self.best_value

            cv2.putText(image, f"Time: {remaining}s", (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            if current_display is not None:
                cv2.putText(image, f"Current: {format_value_short(current_display, test['unit'])}", (20, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

            if best_display is not None:
                cv2.putText(image, f"Best: {format_value_short(best_display, test['unit'])}", (20, 125),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 0), 2)

        elif phase == "done":
            with self.lock:
                done = self.done_value

            cv2.putText(image, "Test completed", (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            if done is not None:
                cv2.putText(image, f"Result: {format_value_short(done, test['unit'])}", (20, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 0), 2)

        else:
            cv2.putText(image, "Press Start Measurement", (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(image, format="bgr24")


RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

ctx = webrtc_streamer(
    key=f"mobility-{selected_side}-{test_name}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=MobilityProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

st.write("Click **START** on the camera box and allow camera permission.")

col1, col2, col3 = st.columns(3)

with col1:
    start_pressed = st.button("Start Measurement", use_container_width=True) or voice_start

with col2:
    reset_pressed = st.button("Reset Measurement", use_container_width=True) or voice_reset

with col3:
    skip_pressed = st.button("Skip This Test", use_container_width=True) or voice_skip


if start_pressed:
    if ctx.video_processor:
        ctx.video_processor.start_measurement()
        st.session_state["spoken_countdown_step"] = None
        st.session_state["spoken_recording_step"] = None
        st.session_state["spoken_test_done"] = False
        speak("Get ready. Countdown begins now.")

if reset_pressed:
    if ctx.video_processor:
        ctx.video_processor.reset()
        st.session_state["spoken_countdown_step"] = None
        st.session_state["spoken_recording_step"] = None
        st.session_state["spoken_test_done"] = False
        speak("Measurement reset.")

if skip_pressed:
    result_key = f"{selected_side}_{test['result']}"
    st.session_state["mobility_results"][result_key] = {
        "value": "Skipped",
        "unit": "skipped"
    }
    st.warning(f"{result_key} marked as skipped.")
    speak(f"{selected_side} {test_name} skipped.")


if ctx.video_processor:
    with ctx.video_processor.lock:
        status = ctx.video_processor.status
        done_value = ctx.video_processor.done_value
        phase = ctx.video_processor.phase
        countdown_start = ctx.video_processor.countdown_start
        recording_start = ctx.video_processor.recording_start

    st.info(status)
    screen_reader_status(status)

    now = time.time()

    if phase == "countdown" and countdown_start:
        remaining = max(0, 6 - int(now - countdown_start))

        if st.session_state.get("spoken_countdown_step") != remaining:
            st.session_state["spoken_countdown_step"] = remaining

            if remaining > 0:
                speak(str(remaining))
            else:
                speak("Start now.")

    if phase == "recording" and recording_start:
        remaining = max(0, 8 - int(now - recording_start))

        if remaining in [5, 3, 1] and st.session_state.get("spoken_recording_step") != remaining:
            st.session_state["spoken_recording_step"] = remaining
            speak(f"{remaining} seconds remaining.")

    if phase == "done" and done_value is not None:
        result_key = f"{selected_side}_{test['result']}"
        st.session_state["mobility_results"][result_key] = {
            "value": int(done_value),
            "unit": test["unit"]
        }

        result_message = f"{selected_side} {test_name} recorded: {format_value(done_value, test['unit'])}"
        st.session_state["latest_result_message"] = result_message

        st.success(result_message)
        screen_reader_status(result_message)

        if not st.session_state.get("spoken_test_done"):
            speak(f"Test complete. {result_message}.")
            st.session_state["spoken_test_done"] = True


st.subheader("Latest Result")

if st.session_state.get("latest_result_message"):
    st.success(st.session_state["latest_result_message"])
else:
    st.info("No completed test result yet.")


st.subheader("Saved Mobility Results")

if not st.session_state["mobility_results"]:
    st.info("No mobility results saved yet.")
else:
    for key, result in st.session_state["mobility_results"].items():
        st.write(f"**{key}:** {format_value(result['value'], result['unit'])}")


if st.button("Save All Mobility Results", use_container_width=True) or voice_save:
    for key, result in st.session_state["mobility_results"].items():
        st.session_state[key] = result["value"]

    st.success("All mobility results saved into the current profile session.")
    speak("All mobility results have been saved.")

bottom_nav()