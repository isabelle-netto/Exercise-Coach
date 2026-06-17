import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    SELECT ExerciseID, ExerciseName, TargetArea, Difficulty, IsSeatedFriendly
    FROM Exercise
    ORDER BY ExerciseName;
""")

rows = cur.fetchall()
conn.close()

print("Exercises in database:")

for row in rows:
    print(row)