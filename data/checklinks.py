import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\n========== EXERCISE AND EQUIPMENT LINKS ==========\n")

    query = """
    SELECT 
        e.ExerciseName,
        GROUP_CONCAT(eq.EquipmentName, ', ') AS EquipmentList
    FROM Exercise e
    LEFT JOIN ExerciseEquipment ee 
        ON e.ExerciseID = ee.ExerciseID
    LEFT JOIN Equipment eq
        ON ee.EquipmentID = eq.EquipmentID
    GROUP BY e.ExerciseID
    ORDER BY e.ExerciseName;
    """

    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        print("No exercises found. Did seedexercises.py run?")
        conn.close()
        return

    for exercise, equipment in rows:
        print(f"Exercise: {exercise}")
        print(f"Equipment: {equipment}")
        print("----------------------------------")

    print("\nCheck complete.")
    conn.close()


if __name__ == "__main__":
    main()