# Learnabit Project Instructions

Learnabit is a single-user habit tracker built with Python, Streamlit, SQLite, and Plotly.

## Project Structure

- `app.py` contains the Streamlit pages, UI interactions, and styling.
- `database.py` owns SQLite persistence. Keep database queries parameterized and preserve earned completion history when quests are archived.
- `game_logic.py` contains XP, level, streak, and achievement rules.
- `requirements.txt` lists runtime dependencies. Avoid adding dependencies for features covered by the current stack.

## Development

- Keep the Python code readable for a student learning application development.
- Run locally with `streamlit run app.py` after installing `requirements.txt`.
- The local database is `learnabit.db`; do not commit personal progress data.
- Project scaffold, core features, and README are in place. Runtime validation is pending because Python is not installed or available on PATH in the current environment.