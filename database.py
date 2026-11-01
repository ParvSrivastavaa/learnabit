"""SQLite persistence for the single-user Learnabit app."""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

import seed_db

DB_PATH = Path(__file__).with_name("learnabit.db")


@contextmanager
def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Personal',
                difficulty TEXT NOT NULL DEFAULT 'Standard',
                xp_reward INTEGER NOT NULL DEFAULT 20,
                active INTEGER NOT NULL DEFAULT 1,
                deleted INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                completed_on TEXT NOT NULL,
                completed_at TEXT,
                category TEXT,
                xp_earned INTEGER NOT NULL
            );
            """
        )
        for index in connection.execute("PRAGMA index_list(completions)").fetchall():
            if not index["unique"]:
                continue
            index_name = index["name"].replace('"', '""')
            columns = connection.execute(f'PRAGMA index_info("{index_name}")').fetchall()
            if [column["name"] for column in columns] == ["habit_id", "completed_on"]:
                connection.execute(
                    """CREATE TABLE completions_new (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                           completed_on TEXT NOT NULL,
                           completed_at TEXT,
                           category TEXT,
                           xp_earned INTEGER NOT NULL
                       )"""
                )
                connection.execute(
                    """INSERT INTO completions_new
                           (id, habit_id, completed_on, completed_at, category, xp_earned)
                       SELECT id, habit_id, completed_on, NULL, NULL, xp_earned FROM completions"""
                )
                connection.execute("DROP TABLE completions")
                connection.execute("ALTER TABLE completions_new RENAME TO completions")
                break

        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(completions)").fetchall()
        }
        if "completed_at" not in columns:
            connection.execute("ALTER TABLE completions ADD COLUMN completed_at TEXT")
        if "category" not in columns:
            connection.execute("ALTER TABLE completions ADD COLUMN category TEXT")
        connection.execute(
            """UPDATE completions SET category = (
                   SELECT category FROM habits WHERE habits.id = completions.habit_id
               ) WHERE category IS NULL"""
        )
        seed_db.apply_seed(connection)


def list_habits(active_only=False):
    query = "SELECT * FROM habits WHERE deleted = 0"
    if active_only:
        query += " AND active = 1"
    query += " ORDER BY active DESC, created_at, id"
    with connect() as connection:
        return connection.execute(query).fetchall()


def add_habit(name, category, difficulty, xp_reward):
    with connect() as connection:
        connection.execute(
            "INSERT INTO habits (name, category, difficulty, xp_reward) VALUES (?, ?, ?, ?)",
            (name.strip(), category, difficulty, xp_reward),
        )


def update_habit(habit_id, name, category, difficulty, xp_reward, active):
    with connect() as connection:
        connection.execute(
            """UPDATE habits SET name = ?, category = ?, difficulty = ?,
               xp_reward = ?, active = ? WHERE id = ?""",
            (name.strip(), category, difficulty, xp_reward, int(active), habit_id),
        )


def delete_habit(habit_id):
    with connect() as connection:
        connection.execute("UPDATE habits SET deleted = 1, active = 0 WHERE id = ?", (habit_id,))


def complete_habit(habit_id, xp_reward, completed_on=None):
    completed_on = (completed_on or date.today()).isoformat()
    completed_at = datetime.now().isoformat(timespec="seconds")
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO completions (habit_id, completed_on, completed_at, category, xp_earned)
               SELECT id, ?, ?, category, ? FROM habits WHERE id = ?""",
            (completed_on, completed_at, xp_reward, habit_id),
        )
        return cursor.rowcount == 1


def completed_habit_ids(completed_on=None):
    completed_on = (completed_on or date.today()).isoformat()
    with connect() as connection:
        rows = connection.execute(
            "SELECT habit_id FROM completions WHERE completed_on = ?", (completed_on,)
        ).fetchall()
    return {row["habit_id"] for row in rows}


def get_daily_completion_counts(completed_on=None):
    completed_on = (completed_on or date.today()).isoformat()
    with connect() as connection:
        rows = connection.execute(
            """SELECT habit_id, COUNT(*) AS completion_count
               FROM completions WHERE completed_on = ? GROUP BY habit_id""",
            (completed_on,),
        ).fetchall()
    return {row["habit_id"]: row["completion_count"] for row in rows}


def get_completion_categories():
    with connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM completions WHERE category IS NOT NULL"
        ).fetchall()
    return {row["category"] for row in rows}


def has_completion_before(cutoff):
    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM completions WHERE time(completed_at) < ? LIMIT 1", (cutoff,)
        ).fetchone()
    return row is not None


def has_completion_at_or_after(cutoff):
    with connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM completions WHERE time(completed_at) >= ? LIMIT 1", (cutoff,)
        ).fetchone()
    return row is not None


def get_max_daily_xp():
    with connect() as connection:
        row = connection.execute(
            """SELECT COALESCE(MAX(daily_xp), 0) AS max_xp FROM (
                   SELECT SUM(xp_earned) AS daily_xp FROM completions GROUP BY completed_on
               )"""
        ).fetchone()
    return row["max_xp"]


def get_max_daily_quest_completions():
    with connect() as connection:
        row = connection.execute(
            """SELECT COALESCE(MAX(completion_count), 0) AS max_count FROM (
                   SELECT COUNT(*) AS completion_count FROM completions
                   GROUP BY habit_id, completed_on
               )"""
        ).fetchone()
    return row["max_count"]


def get_totals():
    with connect() as connection:
        row = connection.execute(
            "SELECT COALESCE(SUM(xp_earned), 0) AS xp, COUNT(*) AS completions FROM completions"
        ).fetchone()
    return dict(row)


def get_completion_dates():
    with connect() as connection:
        rows = connection.execute(
            "SELECT DISTINCT completed_on FROM completions ORDER BY completed_on"
        ).fetchall()
    return [date.fromisoformat(row["completed_on"]) for row in rows]


def get_daily_xp(days=14):
    start = date.today() - timedelta(days=days - 1)
    with connect() as connection:
        rows = connection.execute(
            """SELECT completed_on, SUM(xp_earned) AS xp
               FROM completions WHERE completed_on >= ?
               GROUP BY completed_on ORDER BY completed_on""",
            (start.isoformat(),),
        ).fetchall()
    return {row["completed_on"]: row["xp"] for row in rows}


def get_recent_activity(limit=8):
    with connect() as connection:
        return connection.execute(
            """SELECT habits.name, habits.category, completions.completed_on,
                      completions.xp_earned
               FROM completions JOIN habits ON habits.id = completions.habit_id
               ORDER BY completions.completed_on DESC, completions.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
