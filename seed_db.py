"""Seed data for Learnabit's initial local database."""


SEED_VERSION = "2026-10-30-v1"

HABITS = [
    ("Read 20 pages", "Learning", "Easy", 10),
    ("Drink 2L Water", "Wellness", "Easy", 10),
    ("Gym Session", "Wellness", "Hard", 30),
    ("Draw a sketch", "Creative", "Medium", 20),
    ("Organize desk", "Life", "Easy", 10),
    ("Meditate", "Personal", "Medium", 20),
    ("Study for 1 hour", "Learning", "Medium", 20),
    ("Do the laundry", "Life", "Easy", 10),
]

COMPLETIONS = [
    ("Read 20 pages", 10, "2026-10-25"),
    ("Drink 2L Water", 10, "2026-10-25"),
    ("Drink 2L Water", 10, "2026-10-26"),
    ("Gym Session", 30, "2026-10-26"),
    ("Study for 1 hour", 20, "2026-10-26"),
    ("Read 20 pages", 10, "2026-10-27"),
    ("Drink 2L Water", 10, "2026-10-27"),
    ("Draw a sketch", 20, "2026-10-27"),
    ("Gym Session", 30, "2026-10-28"),
    ("Do the laundry", 10, "2026-10-28"),
    ("Read 20 pages", 10, "2026-10-29"),
    ("Drink 2L Water", 10, "2026-10-29"),
    ("Organize desk", 10, "2026-10-29"),
    ("Read 20 pages", 10, "2026-10-30"),
    ("Gym Session", 30, "2026-10-30"),
    ("Meditate", 20, "2026-10-30"),
    ("Study for 1 hour", 20, "2026-10-30"),
]

UNLOCKED_BADGES = [
    ("First Quest Done", "Badge"),
    ("3-Day Streak", "Badge"),
    ("Level 2 Reached", "Badge"),
]


def apply_seed(connection):
    """Replace Learnabit data with the supplied seed data once."""
    connection.execute(
        """CREATE TABLE IF NOT EXISTS app_metadata (
               key TEXT PRIMARY KEY,
               value TEXT NOT NULL
           )"""
    )
    existing = connection.execute(
        "SELECT value FROM app_metadata WHERE key = 'seed_version'"
    ).fetchone()
    if existing and existing["value"] == SEED_VERSION:
        return False

    connection.execute("DELETE FROM completions")
    connection.execute("DELETE FROM habits")
    connection.execute(
        """CREATE TABLE IF NOT EXISTS unlocked_badges (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               badge_name TEXT NOT NULL,
               icon TEXT NOT NULL
           )"""
    )
    connection.execute("DELETE FROM unlocked_badges")

    connection.executemany(
        """INSERT INTO habits
               (name, category, difficulty, xp_reward, active, deleted)
           VALUES (?, ?, ?, ?, 1, 0)""",
        HABITS,
    )

    habit_ids = {
        row["name"]: row["id"]
        for row in connection.execute("SELECT id, name FROM habits").fetchall()
    }
    categories = {
        name: category for name, category, _, _ in HABITS
    }
    connection.executemany(
        """INSERT INTO completions
               (habit_id, completed_on, completed_at, category, xp_earned)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (
                habit_ids[name],
                completed_on,
                f"{completed_on}T12:00:00",
                categories[name],
                xp_earned,
            )
            for name, xp_earned, completed_on in COMPLETIONS
        ],
    )
    connection.executemany(
        "INSERT INTO unlocked_badges (badge_name, icon) VALUES (?, ?)",
        UNLOCKED_BADGES,
    )
    connection.execute(
        """INSERT INTO app_metadata (key, value) VALUES ('seed_version', ?)
           ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
        (SEED_VERSION,),
    )
    return True
