import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"

MAIN_EQUIPMENT = [
    "No equipment",
    "Resistance band",
    "Dumbbell / kettlebell",
    "Medicine ball",
    "Gym equipment"
]

GYM_EQUIPMENT = [
    "Pull-Up Bar",
    "Smith Machine",
    "Seated Chest Press Machine",
    "Bench Press",
    "Incline Bench Press",
    "Adjustable Bench",
    "Shoulder Press Machine",
    "Lateral Raises Machine",
    "Lat Pull Down Machine",
    "Row Machine",
    "Abdominal Bench",
    "Leg Press Machine",
    "Leg Extension Machine",
    "Leg Curl Machine (Seated)",
    "Leg Curl Machine (Lying)",
    "Leg Abduction Machine"
]


def insert_equipment(conn, names, group_name):
    cur = conn.cursor()

    for name in names:
        cur.execute("""
            INSERT OR IGNORE INTO Equipment (EquipmentName, EquipmentGroup)
            VALUES (?, ?)
        """, (name, group_name))


def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        insert_equipment(conn, MAIN_EQUIPMENT, "Main")
        insert_equipment(conn, GYM_EQUIPMENT, "Gym")
        conn.commit()

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Equipment;")
        total = cur.fetchone()[0]

        print(f"Equipment seeded. Total equipment records: {total}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()