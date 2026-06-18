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


def measure_angle(test_name, landmarks, side):
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


TESTS = {
    "Shoulder Flexion": {
        "instruction": "Start with your arm relaxed. When recording begins, lift your arm forward as high as comfortable.",
        "result": "Shoulder_Flexion",
        "direction": "increase",
    },
    "Shoulder Abduction": {
        "instruction": "Start with your arm relaxed. When recording begins, lift your arm out to the side as high as comfortable.",
        "result": "Shoulder_Abduction",
        "direction": "increase",
    },
    "Elbow Flexion": {
        "instruction": "Start with your arm relaxed. When recording begins, bend your elbow toward your shoulder.",
        "result": "Elbow_Flexion",
        "direction": "decrease",
    },
    "Hip Flexion": {
        "instruction": "Start in a relaxed seated or standing position. When recording begins, lift your knee upward.",
        "result": "Hip_Flexion",
        "direction": "decrease",
    },
    "Knee Flexion": {
        "instruction": "Start with your leg relaxed. When recording begins, bend your knee as much as comfortable.",
        "result": "Knee_Flexion",
        "direction": "decrease",
    },
    "Knee Extension": {
        "instruction": "Start with your knee slightly bent. When recording begins, straighten your knee as much as comfortable.",
        "result": "Knee_Extension",
        "direction": "increase",
    },
    "Ankle Mobility": {
        "instruction": "Start with your foot relaxed. When recording begins, move your foot through a comfortable toe point or toe lift.",
        "result": "Ankle_Mobility",
        "direction": "increase",
    },
}

if "mobility_results" not in st.session_state:
    st.session_state["mobility_results"] = {}

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

top1, top2, top3 = st.columns(3)

with top1:
    test_position = st.radio(
        "How will you perform the test?",
        ["Seated", "Standing", "Supported / assisted"],
    )

with top2:
    selected_side = st.radio(
        "Which side do you want to test?",
        ["Right", "Left"],
    )

with top3:
    available_limbs = st.multiselect(
        "Which limbs can be tested today?",
        ["Right arm", "Left arm", "Right leg", "Left leg"],
        default=["Right arm", "Left arm", "Right leg", "Left leg"],
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
            min_tracking_confidence=0.45,
        )

        self.phase = "idle"
        self.countdown_start = None
        self.recording_start = None

        self.baseline_samples = []
        self.starting_angle = None
        self.current_angle = None
        self.safe_limit_angle = None
        self.rom = None
        self.done_result = None

        self.pose_detected = False
        self.status = "Ready. Start the camera, then press Start Measurement."

    def start_measurement(self):
        with self.lock:
            self.phase = "countdown"
            self.countdown_start = time.time()
            self.recording_start = None

            self.baseline_samples = []
            self.starting_angle = None
            self.current_angle = None
            self.safe_limit_angle = None
            self.rom = None
            self.done_result = None

            self.status = "Get ready. Stay still for baseline reading."

    def reset(self):
        with self.lock:
            self.phase = "idle"
            self.countdown_start = None
            self.recording_start = None

            self.baseline_samples = []
            self.starting_angle = None
            self.current_angle = None
            self.safe_limit_angle = None
            self.rom = None
            self.done_result = None

            self.pose_detected = False
            self.status = "Ready. Start the camera, then press Start Measurement."

    def get_latest_result(self):
        with self.lock:
            return {
                "phase": self.phase,
                "status": self.status,
                "pose_detected": self.pose_detected,
                "starting_angle": self.starting_angle,
                "current_angle": self.current_angle,
                "safe_limit_angle": self.safe_limit_angle,
                "rom": self.rom,
                "done_result": self.done_result,
            }

    def recv(self, frame):
        image = frame.to_ndarray(format="rgb24")
        image = cv2.flip(image, 1)

        results = self.pose.process(image)
        now = time.time()

        detected_angle = None

        if results.pose_landmarks:
            self.pose_detected = True
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
            )

            detected_angle = measure_angle(
                test_name,
                results.pose_landmarks.landmark,
                selected_side,
            )
        else:
            self.pose_detected = False

        with self.lock:
            direction = test["direction"]

            if self.phase == "idle":
                self.status = "Ready. Press Start Measurement."

            elif self.phase == "countdown":
                elapsed = now - self.countdown_start
                remaining = max(0, 6 - int(elapsed))

                self.status = f"Stay still. Baseline reading. Test starts in {remaining} seconds."

                if detected_angle is not None:
                    self.baseline_samples.append(detected_angle)

                    if len(self.baseline_samples) > 30:
                        self.baseline_samples = self.baseline_samples[-30:]

                if elapsed >= 6:
                    if self.baseline_samples:
                        self.starting_angle = float(np.median(self.baseline_samples))
                        self.safe_limit_angle = self.starting_angle
                        self.rom = 0
                        self.phase = "recording"
                        self.recording_start = now
                        self.status = "Recording. Move now."
                    else:
                        self.phase = "done"
                        self.status = "No pose detected during baseline. Please retake the test."

            elif self.phase == "recording":
                elapsed = now - self.recording_start
                remaining = max(0, 8 - int(elapsed))

                if detected_angle is not None and self.starting_angle is not None:
                    self.current_angle = detected_angle

                    if direction == "increase":
                        movement = detected_angle - self.starting_angle

                        if movement > 8:
                            if self.safe_limit_angle is None:
                                self.safe_limit_angle = detected_angle
                            else:
                                self.safe_limit_angle = max(self.safe_limit_angle, detected_angle)

                            self.rom = max(0, self.safe_limit_angle - self.starting_angle)

                    elif direction == "decrease":
                        movement = self.starting_angle - detected_angle

                        if movement > 8:
                            if self.safe_limit_angle is None:
                                self.safe_limit_angle = detected_angle
                            else:
                                self.safe_limit_angle = min(self.safe_limit_angle, detected_angle)

                            self.rom = max(0, self.starting_angle - self.safe_limit_angle)

                self.status = f"Recording. Move now. Time left: {remaining} seconds."

                if elapsed >= 8:
                    self.phase = "done"

                    if self.starting_angle is not None and self.safe_limit_angle is not None and self.rom is not None:
                        self.done_result = {
                            "starting_angle": int(self.starting_angle),
                            "safe_limit_angle": int(self.safe_limit_angle),
                            "rom": int(self.rom),
                            "direction": direction,
                        }

                        self.status = (
                            f"Test completed. ROM: {int(self.rom)} degrees. "
                            f"Safe limit: {int(self.safe_limit_angle)} degrees."
                        )
                    else:
                        self.status = "Test completed. No clear movement detected."

            elif self.phase == "done":
                if self.done_result:
                    self.status = (
                        f"Test completed. ROM: {self.done_result['rom']} degrees. "
                        f"Safe limit: {self.done_result['safe_limit_angle']} degrees."
                    )

            status_text = self.status
            pose_detected = self.pose_detected
            starting_angle = self.starting_angle
            current_angle = self.current_angle
            safe_limit_angle = self.safe_limit_angle
            rom = self.rom

        if pose_detected:
            pose_text = "POSE DETECTED"
            pose_colour = (0, 255, 0)
        else:
            pose_text = "NO POSE DETECTED"
            pose_colour = (0, 0, 255)

        cv2.rectangle(image, (10, 10), (970, 265), (0, 0, 0), -1)

        cv2.putText(image, status_text[:60], (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        if len(status_text) > 60:
            cv2.putText(image, status_text[60:120], (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        cv2.putText(image, pose_text, (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.72, pose_colour, 2)

        if starting_angle is not None:
            cv2.putText(image, f"Starting angle: {int(starting_angle)} degrees", (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)

        if current_angle is not None:
            cv2.putText(image, f"Current angle: {int(current_angle)} degrees", (30, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)

        if safe_limit_angle is not None:
            cv2.putText(image, f"Safe limit: {int(safe_limit_angle)} degrees", (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)

        if rom is not None:
            cv2.putText(image, f"ROM: {int(rom)} degrees", (520, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)

        return av.VideoFrame.from_ndarray(image, format="rgb24")


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

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
                "height": {"ideal": 480},
            },
            "audio": False,
        },
        async_processing=True,
    )

    st.caption("Click START inside the camera box first and allow browser camera permission.")

with right:
    st.markdown(
        f"""
    <div class="mobility-card">
        <h3>{selected_side} {test_name}</h3>
        <p><b>Instruction:</b> {test["instruction"]}</p>
        <p><b>Step 1:</b> Stay still during the 6-second baseline reading.</p>
        <p><b>Step 2:</b> Move only when the screen says “Recording. Move now.”</p>
        <p><b>Saved output:</b> Starting angle, safe limit angle, and ROM.</p>
        <p class="small-note">
            This data is used as the user's safe range of motion limit for future exercise guidance.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Read Instructions Aloud", use_container_width=True):
        speak(
            f"{selected_side} {test_name}. {test['instruction']} "
            "Stay still during the six second baseline reading. "
            "Move only when the screen says recording. Move now. "
            "The system will save your safe range of motion."
        )

    start_pressed = st.button("Start Measurement", use_container_width=True)
    reset_pressed = st.button("Reset Measurement", use_container_width=True)

    if start_pressed:
        if ctx.video_processor:
            ctx.video_processor.start_measurement()
            speak("Measurement started. Stay still for baseline. Move only when the screen says recording.")
        else:
            st.warning("Start the camera first.")

    if reset_pressed:
        if ctx.video_processor:
            ctx.video_processor.reset()
            speak("Measurement reset.")
        else:
            st.warning("Start the camera first.")

    st.markdown("### Test Status")

    if ctx.video_processor:
        latest = ctx.video_processor.get_latest_result()

        status = latest["status"]
        phase = latest["phase"]
        pose_detected = latest["pose_detected"]
        starting_angle = latest["starting_angle"]
        current_angle = latest["current_angle"]
        safe_limit_angle = latest["safe_limit_angle"]
        rom = latest["rom"]
        done_result = latest["done_result"]

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

        if starting_angle is not None:
            st.write(f"Starting angle: **{int(starting_angle)}°**")

        if current_angle is not None:
            st.write(f"Current angle: **{int(current_angle)}°**")

        if safe_limit_angle is not None:
            st.write(f"Safe limit angle: **{int(safe_limit_angle)}°**")

        if rom is not None:
            st.write(f"ROM: **{int(rom)}°**")

        if phase == "done" and done_result:
            st.success(
                f"Latest result: ROM **{done_result['rom']}°**, safe limit **{done_result['safe_limit_angle']}°**"
            )

    else:
        st.warning("Start the camera first before pressing Start Measurement.")

st.divider()

if st.button("Save Latest Test Result", use_container_width=True):
    if ctx.video_processor:
        latest = ctx.video_processor.get_latest_result()
        done_result = latest["done_result"]
        phase = latest["phase"]

        if phase != "done":
            st.warning("The test is not completed yet. Please wait until it finishes.")

        elif not done_result:
            st.error("No clear ROM result was detected. Please retake the test.")

        else:
            result_key = f"{selected_side}_{test['result']}"

            st.session_state["mobility_results"][result_key] = {
                "starting_angle": done_result["starting_angle"],
                "safe_limit_angle": done_result["safe_limit_angle"],
                "rom": done_result["rom"],
                "direction": done_result["direction"],
            }

            st.success(
                f"Saved {result_key}: ROM {done_result['rom']}°, safe limit {done_result['safe_limit_angle']}°."
            )

            speak(f"Saved result. Range of motion {done_result['rom']} degrees.")
    else:
        st.warning("Start the camera first.")

st.subheader("Saved Mobility Results")

if not st.session_state["mobility_results"]:
    st.info("No saved mobility results yet.")
else:
    for key, result in st.session_state["mobility_results"].items():
        st.write(
            f"**{key}:** ROM {result['rom']}°, "
            f"Start {result['starting_angle']}°, "
            f"Safe Limit {result['safe_limit_angle']}°"
        )

if st.button("Save All Mobility Results", use_container_width=True):
    for key, result in st.session_state["mobility_results"].items():
        st.session_state[f"{key}_starting_angle"] = result["starting_angle"]
        st.session_state[f"{key}_safe_limit_angle"] = result["safe_limit_angle"]
        st.session_state[f"{key}_rom"] = result["rom"]
        st.session_state[f"{key}_direction"] = result["direction"]

    st.success("Mobility ROM data saved for exercise guidance.")

bottom_nav()