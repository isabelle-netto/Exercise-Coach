import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "exercisecoach.db"


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Drop tables first so database resets cleanly during development
    cur.execute("DROP TABLE IF EXISTS SessionResult;")
    cur.execute("DROP TABLE IF EXISTS ExerciseSession;")
    cur.execute("DROP TABLE IF EXISTS ExerciseEquipment;")
    cur.execute("DROP TABLE IF EXISTS UserEquipment;")
    cur.execute("DROP TABLE IF EXISTS Exercise;")
    cur.execute("DROP TABLE IF EXISTS Equipment;")
    cur.execute("DROP TABLE IF EXISTS Profile;")
    cur.execute("DROP TABLE IF EXISTS DiaryEntry;")
    cur.execute("DROP TABLE IF EXISTS User;")
    

    cur.execute("""
    CREATE TABLE User (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL,
        Email TEXT NOT NULL UNIQUE,
        Password TEXT NOT NULL,
        CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE Profile (
        ProfileID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL UNIQUE,
        LimitationCategory TEXT NOT NULL,
        FitnessGoals TEXT NOT NULL,

        Upper_FlexionMax REAL,
        Upper_AbductionMax REAL,
        Upper_HorizAdductionMax REAL,
        Upper_HorizAbductionMax REAL,

        Lower_KneeExtensionMax REAL,
        Lower_KneeFlexionMax REAL,
        Lower_HipAbductionMax REAL,
        Lower_AnkleMobilityScore REAL,

        ProfileUpdatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
        LastAssessmentAt TEXT,

        FOREIGN KEY (UserID) REFERENCES User(UserID)
    );
    """)

    cur.execute("""
    CREATE TABLE Equipment (
        EquipmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        EquipmentName TEXT NOT NULL UNIQUE,
        EquipmentGroup TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE UserEquipment (
        UserID INTEGER NOT NULL,
        EquipmentID INTEGER NOT NULL,
        PRIMARY KEY (UserID, EquipmentID),
        FOREIGN KEY (UserID) REFERENCES User(UserID),
        FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID)
    );
    """)

    cur.execute("""
    CREATE TABLE Exercise (
        ExerciseID INTEGER PRIMARY KEY AUTOINCREMENT,
        ExerciseName TEXT NOT NULL UNIQUE,
        TargetArea TEXT NOT NULL,
        Instructions TEXT NOT NULL,
        Difficulty TEXT,
        IsSeatedFriendly INTEGER DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE ExerciseEquipment (
        ExerciseID INTEGER NOT NULL,
        EquipmentID INTEGER NOT NULL,
        PRIMARY KEY (ExerciseID, EquipmentID),
        FOREIGN KEY (ExerciseID) REFERENCES Exercise(ExerciseID),
        FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID)
    );
    """)

    cur.execute("""
    CREATE TABLE ExerciseSession (
        SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
        ExerciseID INTEGER NOT NULL,
        UserID INTEGER NOT NULL,
        StartTime TEXT,
        EndTime TEXT,
        Date TEXT,
        Duration INTEGER,
        FOREIGN KEY (ExerciseID) REFERENCES Exercise(ExerciseID),
        FOREIGN KEY (UserID) REFERENCES User(UserID)
    );
    """)

    cur.execute("""
    CREATE TABLE SessionResult (
        ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
        SessionID INTEGER NOT NULL UNIQUE,
        RepsCompleted INTEGER DEFAULT 0,
        AccuracyScore REAL DEFAULT 0,
        AvgAngleError REAL DEFAULT 0,
        FOREIGN KEY (SessionID) REFERENCES ExerciseSession(SessionID)
    );
    """)

    conn.commit()

    cur.execute("""
    CREATE TABLE DiaryEntry (
        DiaryID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        MovementFeeling TEXT,
        FlexibilityFeeling TEXT,
        EaseOfMovement TEXT,
        ConfidenceScore INTEGER,
        DiscomfortLevel TEXT,
        PersonalNote TEXT,
        CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES User(UserID)
    );
    """)


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    try:
        create_tables(conn)
        print("Database created successfully at:", DB_PATH)
    finally:
        conn.close()


if __name__ == "__main__":
    main()