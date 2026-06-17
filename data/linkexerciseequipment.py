import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"

LINKS = {
    "Push-ups": ["No equipment"],
    "Pike Push-ups": ["No equipment"],
    "Wall Push-ups": ["No equipment"],
    "Tricep dips (chair/bench)": ["No equipment", "Adjustable Bench"],
    "Plank shoulder taps": ["No equipment"],

    "Squats": ["No equipment", "Dumbbell / kettlebell", "Smith Machine"],
    "Lunges": ["No equipment", "Dumbbell / kettlebell", "Smith Machine"],
    "Step-ups": ["No equipment", "Adjustable Bench"],
    "Glute bridges": ["No equipment"],
    "Calf raises": ["No equipment", "Smith Machine", "Leg Press Machine"],

    "Plank": ["No equipment"],
    "Side plank": ["No equipment"],
    "Mountain climbers": ["No equipment"],
    "Bicycle crunches": ["No equipment"],
    "Leg raises": ["No equipment"],
    "Russian twists (bodyweight)": ["No equipment"],

    "Burpees": ["No equipment"],
    "Jump squats": ["No equipment"],
    "High knees": ["No equipment"],
    "Bear crawl": ["No equipment"],
    "Skaters": ["No equipment"],

    "Band rows": ["Resistance band"],
    "Band chest press": ["Resistance band"],
    "Band shoulder press": ["Resistance band"],
    "Band lateral raises": ["Resistance band"],
    "Band bicep curls": ["Resistance band"],
    "Band tricep extensions": ["Resistance band"],
    "Face pulls": ["Resistance band"],
    "Band squats": ["Resistance band"],
    "Lateral band walks": ["Resistance band"],
    "Glute kickbacks": ["Resistance band"],
    "Hip thrusts with band": ["Resistance band"],
    "Hamstring curls (band)": ["Resistance band"],
    "Monster walks": ["Resistance band"],
    "Pallof press": ["Resistance band"],
    "Band woodchoppers": ["Resistance band"],
    "Standing anti-rotation hold": ["Resistance band"],

    "Dumbbell bench press": ["Dumbbell / kettlebell", "Bench Press", "Adjustable Bench"],
    "Shoulder press": ["Dumbbell / kettlebell", "Shoulder Press Machine"],
    "Lateral raises": ["Dumbbell / kettlebell", "Lateral Raises Machine"],
    "Bent-over rows": ["Dumbbell / kettlebell"],
    "Bicep curls": ["Dumbbell / kettlebell", "Resistance band"],
    "Hammer curls": ["Dumbbell / kettlebell"],
    "Tricep kickbacks": ["Dumbbell / kettlebell"],
    "Goblet squat": ["Dumbbell / kettlebell"],
    "Romanian deadlift": ["Dumbbell / kettlebell"],
    "Walking lunges": ["Dumbbell / kettlebell"],
    "Sumo squats": ["Dumbbell / kettlebell"],
    "Russian twists (weighted)": ["Dumbbell / kettlebell", "Medicine ball"],
    "Renegade rows": ["Dumbbell / kettlebell"],
    "Weighted sit-ups": ["Dumbbell / kettlebell", "Medicine ball"],
    "Farmer’s carry": ["Dumbbell / kettlebell"],
    "Kettlebell swings": ["Dumbbell / kettlebell"],
    "Clean and press": ["Dumbbell / kettlebell"],
    "Thrusters": ["Dumbbell / kettlebell"],
    "Turkish get-ups": ["Dumbbell / kettlebell"],

    "Sit-ups with ball": ["Medicine ball"],
    "Woodchoppers (medicine ball)": ["Medicine ball"],
    "Push-ups on medicine ball": ["Medicine ball"],
    "Squat to press": ["Medicine ball"],
    "Rotational throws": ["Medicine ball"],
    "Lunge with rotation": ["Medicine ball"],

    "Pull-ups": ["Pull-Up Bar"],
    "Chin-ups": ["Pull-Up Bar"],
    "Hanging leg raises": ["Pull-Up Bar"],
    "Dead hangs": ["Pull-Up Bar"],
    "Smith machine squats": ["Smith Machine"],
    "Incline press (smith)": ["Smith Machine", "Incline Bench Press"],
    "Hip thrusts (smith)": ["Smith Machine", "Adjustable Bench"],
    "Lat pulldown": ["Lat Pull Down Machine"],
    "Seated rows": ["Row Machine"],
    "Abdominal bench sit-ups": ["Abdominal Bench"],
    "Leg press": ["Leg Press Machine"],
    "Leg extension": ["Leg Extension Machine"],
    "Seated Leg curl": ["Leg Curl Machine (Seated)"],
    "Lying Leg curl": ["Leg Curl Machine (Lying)"],
    "Hip abduction": ["Leg Abduction Machine"],
}


def get_id(cur, table, id_col, name_col, value):
    cur.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = ?", (value,))
    row = cur.fetchone()
    return row[0] if row else None


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("DELETE FROM ExerciseEquipment;")

    missing_exercises = []
    missing_equipment = []
    total_links = 0

    for exercise_name, equipment_list in LINKS.items():
        exercise_id = get_id(cur, "Exercise", "ExerciseID", "ExerciseName", exercise_name)

        if exercise_id is None:
            missing_exercises.append(exercise_name)
            continue

        for equipment_name in equipment_list:
            equipment_id = get_id(cur, "Equipment", "EquipmentID", "EquipmentName", equipment_name)

            if equipment_id is None:
                missing_equipment.append(equipment_name)
                continue

            cur.execute("""
                INSERT OR IGNORE INTO ExerciseEquipment (ExerciseID, EquipmentID)
                VALUES (?, ?)
            """, (exercise_id, equipment_id))

            total_links += 1

    conn.commit()
    conn.close()

    print("Exercise-equipment linking completed.")
    print(f"Total links inserted: {total_links}")

    if missing_exercises:
        print("\nMissing exercises:")
        for item in sorted(set(missing_exercises)):
            print("-", item)

    if missing_equipment:
        print("\nMissing equipment:")
        for item in sorted(set(missing_equipment)):
            print("-", item)


if __name__ == "__main__":
    main()