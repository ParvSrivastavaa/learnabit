# Learnabit

Learn a little. Build a habit. Level up your life.

Learnabit is a single-user habit tracker built with Python, Streamlit, SQLite, and Plotly. Completing a quest awards XP, adds to your streak, and can unlock achievements. Your progress is stored locally in `learnabit.db`.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies and start Learnabit:

   ```powershell
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

Streamlit will print the local address to open in your browser. The database is created automatically the first time the app runs.

## Project files

- `app.py`: Streamlit pages, interactions, and styling.
- `database.py`: SQLite schema and data operations.
- `seed_db.py`: Initial quests, completion history, and badge seed data.
- `game_logic.py`: XP, level, streak, and achievement rules.
- `requirements.txt`: Python dependencies.

## Notes

This first version is intentionally local and single-user. On the next startup, the database is replaced once with the data in `seed_db.py`; subsequent startups preserve changes made in the app. Quests can be completed multiple times per day, earning XP for every completion. The current streak remains active through today or yesterday, so missing one day does not immediately erase it. Deleting a quest archives it from the board without removing its earned XP or history. Delete `learnabit.db` only if you intentionally want to reset all saved progress.

The `adithyan` theme incorporates the retro pixel UI and styling from [Adithyan's Learnabit repository](https://github.com/a8i-0/Learnabit), including its patterned background, offset-shadow cards, lime buttons, pastel controls, and achievement colors.
