import numpy as np


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def get_point(landmarks, pose, name):
    landmark = getattr(pose.PoseLandmark, name)
    item = landmarks[landmark.value]
    return [item.x, item.y]


def get_side_points(landmarks, pose, side="RIGHT"):
    return {
        "shoulder": get_point(landmarks, pose, f"{side}_SHOULDER"),
        "elbow": get_point(landmarks, pose, f"{side}_ELBOW"),
        "wrist": get_point(landmarks, pose, f"{side}_WRIST"),
        "hip": get_point(landmarks, pose, f"{side}_HIP"),
        "knee": get_point(landmarks, pose, f"{side}_KNEE"),
        "ankle": get_point(landmarks, pose, f"{side}_ANKLE"),
        "foot": get_point(landmarks, pose, f"{side}_FOOT_INDEX"),
    }


def get_user_limit(session_state, side_label, key_name):
    possible_keys = [
        f"{side_label}_{key_name}",
        key_name,
    ]

    for key in possible_keys:
        value = session_state.get(key)
        if isinstance(value, (int, float)):
            return value

    return None


def get_adaptive_targets(template, session_state, side_label="Right"):
    # Defaults are general ranges.
    targets = {
        "top": 45,
        "bottom": 160,
        "min": 45,
        "max": 160,
        "hold_target": 10,
    }

    elbow_limit = get_user_limit(session_state, side_label, "Elbow_Flexion")
    shoulder_flexion = get_user_limit(session_state, side_label, "Shoulder_Flexion")
    shoulder_abduction = get_user_limit(session_state, side_label, "Shoulder_Abduction")
    knee_flexion = get_user_limit(session_state, side_label, "Knee_Flexion")
    knee_extension = get_user_limit(session_state, side_label, "Knee_Extension")
    hip_flexion = get_user_limit(session_state, side_label, "Hip_Flexion")

    if template == "elbow_flexion":
        if elbow_limit:
            targets["top"] = elbow_limit + 10
        targets["bottom"] = 150

    elif template == "elbow_extension":
        targets["top"] = 160
        targets["bottom"] = 70

    elif template in ["shoulder_press", "lateral_raise"]:
        if shoulder_flexion:
            targets["top"] = max(70, shoulder_flexion - 10)
        elif shoulder_abduction:
            targets["top"] = max(70, shoulder_abduction - 10)
        else:
            targets["top"] = 130
        targets["bottom"] = 60

    elif template in ["squat", "lunge", "step_up"]:
        if knee_flexion:
            targets["bottom"] = knee_flexion + 10
        else:
            targets["bottom"] = 95
        if knee_extension:
            targets["top"] = min(170, knee_extension)
        else:
            targets["top"] = 160

    elif template == "knee_extension":
        if knee_extension:
            targets["top"] = min(170, knee_extension)
        else:
            targets["top"] = 160
        targets["bottom"] = 90

    elif template == "knee_flexion":
        if knee_flexion:
            targets["bottom"] = knee_flexion + 10
        else:
            targets["bottom"] = 90
        targets["top"] = 160

    elif template in ["hip_hinge", "hip_bridge"]:
        if hip_flexion:
            targets["bottom"] = hip_flexion + 10
        else:
            targets["bottom"] = 120
        targets["top"] = 160

    return targets


def get_template_angle(template, landmarks, pose, side="RIGHT"):
    pts = get_side_points(landmarks, pose, side)

    if template in [
        "elbow_flexion", "elbow_extension",
        "shoulder_press", "chest_press", "lateral_raise",
        "row", "pull_up"
    ]:
        return calculate_angle(pts["shoulder"], pts["elbow"], pts["wrist"])

    if template in [
        "squat", "lunge", "step_up", "knee_extension", "knee_flexion",
        "squat_press", "marching", "leg_raise"
    ]:
        return calculate_angle(pts["hip"], pts["knee"], pts["ankle"])

    if template in [
        "hip_hinge", "hip_bridge", "hip_abduction", "hip_extension"
    ]:
        return calculate_angle(pts["shoulder"], pts["hip"], pts["knee"])

    if template == "calf_raise":
        return calculate_angle(pts["knee"], pts["ankle"], pts["foot"])

    return None


def update_rep_state(template, angle, session_state, targets):
    if angle is None:
        return "Position not detected", 0

    feedback = "Keep moving slowly"

    if template in ["elbow_flexion", "row", "pull_up"]:
        if angle > targets["bottom"]:
            session_state["stage"] = "down"
            feedback = "Good extension"

        elif angle < targets["top"] and session_state.get("stage") == "down":
            session_state["stage"] = "up"
            session_state["counter"] += 1
            feedback = "Good rep"

        elif angle > targets["top"]:
            feedback = "Curl or pull a little further if comfortable"

    elif template in ["elbow_extension", "chest_press", "shoulder_press"]:
        if angle < targets["bottom"]:
            session_state["stage"] = "down"
            feedback = "Ready to press"

        elif angle > targets["top"] and session_state.get("stage") == "down":
            session_state["stage"] = "up"
            session_state["counter"] += 1
            feedback = "Good press"

        else:
            feedback = "Press smoothly"

    elif template in ["squat", "lunge", "step_up", "knee_flexion", "squat_press"]:
        if angle > targets["top"]:
            session_state["stage"] = "up"
            feedback = "Standing position"

        elif angle < targets["bottom"] and session_state.get("stage") == "up":
            session_state["stage"] = "down"
            session_state["counter"] += 1
            feedback = "Good controlled bend"

        else:
            feedback = "Bend slowly and stay controlled"

    elif template == "knee_extension":
        if angle < targets["bottom"]:
            session_state["stage"] = "down"
            feedback = "Ready to straighten"

        elif angle > targets["top"] and session_state.get("stage") == "down":
            session_state["stage"] = "up"
            session_state["counter"] += 1
            feedback = "Good extension"

        else:
            feedback = "Straighten slowly"

    elif template in ["hip_hinge", "hip_bridge", "hip_abduction", "hip_extension", "calf_raise", "leg_raise", "marching"]:
        if angle > targets["top"]:
            session_state["stage"] = "up"

        elif angle < targets["bottom"] and session_state.get("stage") == "up":
            session_state["stage"] = "down"
            session_state["counter"] += 1
            feedback = "Good rep"

        else:
            feedback = "Move slowly and stay controlled"

    elif template in ["hold", "core_rotation", "core_rep", "full_body", "lateral_movement"]:
        feedback = "Hold steady or move with control"

    return feedback, 1


def calculate_adaptive_accuracy(template, angles, targets):
    if not angles:
        return 0, 0

    max_angle = max(angles)
    min_angle = min(angles)

    if template in ["hold", "core_rotation", "core_rep", "full_body", "lateral_movement"]:
        return 80, 0

    top_error = abs(min_angle - targets.get("top", min_angle))
    bottom_error = abs(max_angle - targets.get("bottom", max_angle))

    avg_error = round((top_error + bottom_error) / 2, 2)
    accuracy = max(0, 100 - avg_error)

    return round(accuracy, 1), avg_error