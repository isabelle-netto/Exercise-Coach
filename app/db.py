import sqlite3
from pathlib import Path
import random
import string
from datetime import datetime, timedelta
import bcrypt

DB_PATH = Path(__file__).parent.parent / "data" / "exercisecoach.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def is_bcrypt_hash(value):
    return isinstance(value, str) and value.startswith("$2")


def verify_password(password, stored_password):
    if not stored_password:
        return False

    if is_bcrypt_hash(stored_password):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))
        except Exception:
            return False

    return password == stored_password


def create_user(full_name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    email = email.strip().lower()
    full_name = full_name.strip()
    hashed_password = hash_password(password.strip())

    try:
        cur.execute("""
            INSERT INTO User (FullName, Email, Password)
            VALUES (?, ?, ?)
        """, (full_name, email, hashed_password))

        conn.commit()
        return cur.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    cur = conn.cursor()

    email = email.strip().lower()
    password = password.strip()

    cur.execute("""
        SELECT UserID, FullName, Password
        FROM User
        WHERE LOWER(Email) = ?
    """, (email,))

    user = cur.fetchone()

    if not user:
        conn.close()
        return None

    user_id, full_name, stored_password = user

    if verify_password(password, stored_password):
        if not is_bcrypt_hash(stored_password):
            cur.execute("""
                UPDATE User SET Password = ?
                WHERE UserID = ?
            """, (hash_password(password), user_id))
            conn.commit()

        conn.close()
        return (user_id, full_name)

    conn.close()
    return None


def save_profile(user_id, limitation_category, fitness_goals):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO Profile (UserID, LimitationCategory, FitnessGoals)
        VALUES (?, ?, ?)
        ON CONFLICT(UserID) DO UPDATE SET
            LimitationCategory = excluded.LimitationCategory,
            FitnessGoals = excluded.FitnessGoals,
            ProfileUpdatedAt = CURRENT_TIMESTAMP
    """, (user_id, limitation_category, fitness_goals))

    conn.commit()
    conn.close()


def get_user_profile(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT LimitationCategory
        FROM Profile
        WHERE UserID = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_user_goals(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT FitnessGoals
        FROM Profile
        WHERE UserID = ?
    """, (user_id,))

    row = cur.fetchone()
    conn.close()

    if row and row[0]:
        return row[0].split(", ")
    return []


def get_all_equipment():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT EquipmentName, EquipmentGroup
        FROM Equipment
        ORDER BY EquipmentGroup, EquipmentName
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def save_user_equipment(user_id, equipment_list):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM UserEquipment WHERE UserID = ?", (user_id,))

    for equipment_name in equipment_list:
        cur.execute("""
            INSERT OR IGNORE INTO UserEquipment (UserID, EquipmentID)
            SELECT ?, EquipmentID
            FROM Equipment
            WHERE EquipmentName = ?
        """, (user_id, equipment_name))

    conn.commit()
    conn.close()


def get_user_equipment(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.EquipmentName
        FROM UserEquipment ue
        JOIN Equipment e ON ue.EquipmentID = e.EquipmentID
        WHERE ue.UserID = ?
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_all_exercises():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT ExerciseID, ExerciseName, TargetArea, Difficulty, IsSeatedFriendly
        FROM Exercise
        ORDER BY ExerciseName
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_exercise_details(exercise_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT ExerciseName, TargetArea, Instructions, Difficulty, IsSeatedFriendly
        FROM Exercise
        WHERE ExerciseID = ?
    """, (exercise_id,))

    row = cur.fetchone()
    conn.close()
    return row


def get_exercises_with_equipment():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            ex.ExerciseID,
            ex.ExerciseName,
            ex.TargetArea,
            ex.Difficulty,
            ex.IsSeatedFriendly,
            eq.EquipmentName
        FROM Exercise ex
        LEFT JOIN ExerciseEquipment ee ON ex.ExerciseID = ee.ExerciseID
        LEFT JOIN Equipment eq ON ee.EquipmentID = eq.EquipmentID
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_recommended_exercises(user_id):
    import streamlit as st

    if not user_id:
        return []

    user_equipment = get_user_equipment(user_id)
    limitation = get_user_profile(user_id)
    rows = get_exercises_with_equipment()

    shoulder_flexion = st.session_state.get("shoulder_flexion", None)

    exercise_dict = {}

    for row in rows:
        ex_id, name, target_area, difficulty, seated, equipment_name = row

        if ex_id not in exercise_dict:
            exercise_dict[ex_id] = {
                "name": name,
                "target_area": target_area,
                "difficulty": difficulty,
                "seated": seated,
                "equipment": set()
            }

        if equipment_name:
            exercise_dict[ex_id]["equipment"].add(equipment_name)

    recommendations = []

    for ex_id, ex in exercise_dict.items():
        score = 0

        if any(eq in user_equipment for eq in ex["equipment"]):
            score += 5
        elif "No equipment" in ex["equipment"]:
            score += 4
        else:
            continue

        if ex["difficulty"] == "Beginner":
            score += 3
        elif ex["difficulty"] == "Intermediate":
            score += 2
        elif ex["difficulty"] == "Advanced":
            score += 1

        if limitation == "Lower-body limitation":
            if ex["seated"] == 1:
                score += 3
            if ex["target_area"] == "Lower Body":
                score -= 2

        elif limitation == "Upper-body limitation":
            if ex["target_area"] == "Upper Body":
                score -= 2
            if ex["seated"] == 1:
                score += 1

        elif limitation == "Upper + lower limitation":
            if ex["seated"] == 1:
                score += 4
            if ex["difficulty"] == "Advanced":
                score -= 3

        elif limitation == "Balance / stability limitation":
            if ex["seated"] == 1:
                score += 4
            if ex["difficulty"] == "Advanced":
                score -= 3

        elif limitation == "No major limitation":
            score += 1

        if shoulder_flexion is not None:
            if shoulder_flexion < 70:
                if ex["target_area"] == "Upper Body":
                    score -= 4
                if ex["difficulty"] == "Advanced":
                    score -= 3

            elif 70 <= shoulder_flexion < 120:
                if ex["target_area"] == "Upper Body":
                    score -= 1
                if ex["difficulty"] == "Advanced":
                    score -= 2

            elif shoulder_flexion >= 120:
                if ex["target_area"] == "Upper Body":
                    score += 2
                if ex["difficulty"] == "Advanced":
                    score += 1

        recommendations.append((
            score,
            ex_id,
            ex["name"],
            ex["target_area"],
            ex["difficulty"],
            ex["seated"]
        ))

    recommendations.sort(reverse=True, key=lambda x: x[0])
    return recommendations[:6]


def save_diary_entry(user_id, note):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO DiaryEntry (UserID, PersonalNote)
        VALUES (?, ?)
    """, (user_id, note))

    conn.commit()
    conn.close()


def get_diary_entries(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT CreatedAt, PersonalNote
        FROM DiaryEntry
        WHERE UserID = ?
        ORDER BY CreatedAt DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def save_exercise_session(user_id, exercise_id, reps_completed, duration, accuracy_score=0, avg_angle_error=0):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    end_time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")

    cur.execute("""
        INSERT INTO ExerciseSession (
            ExerciseID, UserID, StartTime, EndTime, Date, Duration
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (exercise_id, user_id, start_time, end_time, date, duration))

    session_id = cur.lastrowid

    cur.execute("""
        INSERT INTO SessionResult (
            SessionID, RepsCompleted, AccuracyScore, AvgAngleError
        )
        VALUES (?, ?, ?, ?)
    """, (session_id, reps_completed, accuracy_score, avg_angle_error))

    conn.commit()
    conn.close()

    return session_id


def get_user_session_results(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            es.Date,
            ex.ExerciseName,
            es.Duration,
            sr.RepsCompleted,
            sr.AccuracyScore
        FROM ExerciseSession es
        JOIN Exercise ex ON es.ExerciseID = ex.ExerciseID
        JOIN SessionResult sr ON es.SessionID = sr.SessionID
        WHERE es.UserID = ?
        ORDER BY es.SessionID DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def generate_reset_code():
    return ''.join(random.choices(string.digits, k=6))


def save_reset_code(email, code):
    conn = get_connection()
    cur = conn.cursor()

    email = email.strip().lower()
    expiry = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS PasswordReset (
            Email TEXT,
            Code TEXT,
            Expiry TEXT
        )
    """)

    cur.execute("DELETE FROM PasswordReset WHERE Email = ?", (email,))
    cur.execute("""
        INSERT INTO PasswordReset (Email, Code, Expiry)
        VALUES (?, ?, ?)
    """, (email, code, expiry))

    conn.commit()
    conn.close()


def verify_reset_code(email, code):
    conn = get_connection()
    cur = conn.cursor()

    email = email.strip().lower()

    cur.execute("""
        SELECT Expiry FROM PasswordReset
        WHERE Email = ? AND Code = ?
    """, (email, code.strip()))

    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    expiry = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    return datetime.now() < expiry


def update_password(email, new_password):
    conn = get_connection()
    cur = conn.cursor()

    email = email.strip().lower()
    hashed_password = hash_password(new_password.strip())

    cur.execute("""
        UPDATE User SET Password = ?
        WHERE LOWER(Email) = ?
    """, (hashed_password, email))

    conn.commit()
    conn.close()