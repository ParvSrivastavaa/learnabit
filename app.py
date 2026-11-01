"""Learnabit: a local gamified habit tracker built with Streamlit."""

from datetime import date, datetime, timedelta
from html import escape

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

import database as db
from game_logic import ACHIEVEMENTS, DIFFICULTY_XP, achievement_progress, get_level, get_streaks


st.set_page_config(page_title="Learnabit | Level up your life", page_icon="✦", layout="wide")
db.init_db()

THEME_PALETTES = {
    "Dark": {
        "ink": "#f2f4ff",
        "muted": "#929ab5",
        "line": "#282e43",
        "cyan": "#51e2db",
        "violet": "#9c83ff",
        "lime": "#c6f36b",
        "page_background": "radial-gradient(ellipse at 85% 0%, #202242 0%, #101421 45%, #0b0e17 100%)",
        "sidebar_background": "#101421",
        "card_background": "linear-gradient(145deg, #191f32, #131827)",
        "card_surface": "#151a2b",
        "button_background": "#211e3a",
        "button_border": "#454267",
        "progress_track": "#292f43",
        "meter_background": "#090d17",
        "meter_border": "#39415e",
        "primary_button_text": "#ffffff",
        "chart_text": "#dce1f2",
        "chart_grid": "#282e43",
        "heatmap_empty": "#20263a",
        "selector_background": "#151a2b",
        "selector_active": "#51e2db",
        "selector_text": "#f2f4ff",
        "selector_shadow": "#282e43",
    },
    "Light": {
        "ink": "#1d2939",
        "muted": "#58677e",
        "line": "#cbd5e1",
        "cyan": "#087f8c",
        "violet": "#7654d7",
        "lime": "#c6f36b",
        "page_background": "radial-gradient(ellipse at 85% 0%, #ddf5f2 0%, #eef2ff 45%, #f8fafc 100%)",
        "sidebar_background": "#e8edf6",
        "card_background": "linear-gradient(145deg, #ffffff, #f0f4fa)",
        "card_surface": "#ffffff",
        "button_background": "#e9e7f7",
        "button_border": "#b9b5d4",
        "progress_track": "#d9e1ec",
        "meter_background": "#d3ddea",
        "meter_border": "#aebbd0",
        "primary_button_text": "#ffffff",
        "chart_text": "#263348",
        "chart_grid": "#d6deea",
        "heatmap_empty": "#e1e8f0",
        "selector_background": "#ffffff",
        "selector_active": "#087f8c",
        "selector_text": "#1d2939",
        "selector_shadow": "#cbd5e1",
    },
    "Parv": {
        "ink": "#f2f5ff",
        "muted": "#a8b7d4",
        "line": "#304363",
        "cyan": "#48f5d2",
        "violet": "#ff5cf4",
        "lime": "#f3ff52",
        "page_background": "#0d1526",
        "sidebar_background": "#0b111f",
        "card_background": "#141f34",
        "card_surface": "#101a2d",
        "button_background": "#48f5d2",
        "button_border": "#05070c",
        "progress_track": "#26334a",
        "meter_background": "#09101e",
        "meter_border": "#e8edff",
        "primary_button_text": "#05070c",
        "chart_text": "#e8edff",
        "chart_grid": "#304363",
        "heatmap_empty": "#1f2b3e",
        "selector_background": "#101a2d",
        "selector_active": "#ff5cf4",
        "selector_text": "#f2f5ff",
        "selector_shadow": "#304363",
    },
    "adithyan": {
        "ink": "#000000",
        "muted": "#3d4653",
        "line": "#000000",
        "cyan": "#47e5c3",
        "violet": "#d1b3ff",
        "lime": "#ccff00",
        "page_background": "#fcfaf5",
        "sidebar_background": "#ffffff",
        "card_background": "#ffffff",
        "card_surface": "#ffffff",
        "button_background": "#ccff00",
        "button_border": "#000000",
        "progress_track": "#3b3f4e",
        "meter_background": "#20222a",
        "meter_border": "#f8f9fa",
        "primary_button_text": "#000000",
        "chart_text": "#000000",
        "chart_grid": "#dcd8c0",
        "heatmap_empty": "#e0e0e0",
        "selector_background": "#ffb3ba",
        "selector_active": "#ff5757",
        "selector_text": "#17202a",
        "selector_shadow": "#000000",
    },
}
st.session_state.setdefault("learnabit_theme", "Dark")
theme_palette = THEME_PALETTES[st.session_state["learnabit_theme"]]

st.markdown(
    """
    <style>
    :root {
        --ink: #f2f4ff;
        --muted: #929ab5;
        --line: #282e43;
        --cyan: #51e2db;
        --violet: #9c83ff;
        --lime: #c6f36b;
        --card: linear-gradient(145deg, #191f32, #131827);
        --surface: #151a2b;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 85% 0%, #202242 0%, #101421 45%, #0b0e17 100%);
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: #101421;
        border-right: 1px solid var(--line);
    }
    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }
    h1, h2, h3, [data-testid="stSidebar"] h1 {
        font-family: "Press Start 2P", monospace;
        color: var(--ink);
        line-height: 1.7;
    }
    h1 { font-size: 1.15rem; }
    h2 { font-size: .82rem; }
    h3 { font-size: .68rem; }
    .brand {
        font: 1.05rem "Press Start 2P", monospace;
        color: var(--ink);
    }
    .brand span { color: var(--cyan); }
    .eyebrow {
        color: var(--cyan);
        font: .55rem "Press Start 2P", monospace;
        text-transform: uppercase;
    }
    .subtle, .quest-meta { color: var(--muted); }
    .stat-card, .quest-card, .achievement-card, .xp-console {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 9px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }
    .stat-label {
        color: var(--muted);
        font: .48rem "Press Start 2P", monospace;
    }
    .stat-value {
        color: var(--ink);
        font: .72rem "Press Start 2P", monospace;
        margin-top: 8px;
    }
    .stat-note { color: var(--cyan); font-size: .78rem; margin-top: 5px; }
    .quest-title { color: var(--ink); font-weight: 700; }
    .xp-console-head, .xp-console-foot {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        color: var(--muted);
        font: .48rem "Press Start 2P", monospace;
    }
    .xp-level-badge {
        background: var(--lime);
        color: #0b1019;
        padding: 7px 10px;
        border-radius: 3px;
    }
    .xp-next { color: var(--cyan); }
    .xp-track {
        height: 22px;
        margin: 14px 0 10px;
        overflow: hidden;
        border: 1px solid #39415e;
        border-radius: 4px;
        background: #090d17;
    }
    .xp-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--violet), #3c9af5 62%, var(--cyan));
    }
    .achievement-card { min-height: 142px; }
    .achievement-icon { font-size: 1.55rem; color: var(--cyan); }
    .achievement-progress-track {
        height: 6px;
        margin-top: 12px;
        overflow: hidden;
        border-radius: 4px;
        background: #292f43;
    }
    .achievement-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--violet), var(--cyan));
    }
    .locked { opacity: .48; filter: grayscale(.7); }
    .stButton > button {
        border: 1px solid #454267;
        border-radius: 7px;
        background: #211e3a;
        color: var(--ink);
        font-weight: 600;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg, var(--violet), var(--cyan));
        color: white;
        border: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state["learnabit_theme"] == "adithyan":
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        [data-testid="stAppViewContainer"] {
            background-color: #fcfaf5 !important;
            background-image: radial-gradient(#dcd8c0 1px, transparent 1px) !important;
            background-size: 20px 20px !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 3px solid #000000 !important;
        }
        [data-testid="stHeader"] { background-color: transparent !important; }
        h1, h2, h3, p, span, label, .stMarkdown {
            color: #000000 !important;
        }
        h1, h2, h3, .brand, .eyebrow, .stat-label, .stat-value,
        .xp-console-head, .xp-console-foot {
            font-family: "Press Start 2P", cursive !important;
        }
        .stat-card, .quest-card, .achievement-card, .xp-console,
        [data-testid="stMetric"] {
            background: #ffffff !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: 4px 4px 0 #000000 !important;
        }
        .stat-card, .quest-card, .achievement-card, .xp-console {
            padding: 14px 16px !important;
        }
        .stat-label, .eyebrow { color: #000000 !important; }
        .stat-note, .quest-meta, .subtle { color: #263238 !important; }
        .stButton > button {
            background: #ccff00 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: 4px 4px 0 #000000 !important;
            font-family: "Press Start 2P", cursive !important;
            font-size: .55rem !important;
            font-weight: 400 !important;
        }
        .stButton > button:active {
            transform: translate(4px, 4px);
            box-shadow: none !important;
        }
        .stButton > button[kind="primary"] {
            background: #ccff00 !important;
            color: #000000 !important;
        }
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea,
        .stTextInput input {
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            color: #000000 !important;
        }
        div[role="radiogroup"] label {
            padding: 10px 8px !important;
            border: 2px solid #000000 !important;
            border-radius: 8px !important;
            box-shadow: 4px 4px 0 #000000 !important;
        }
        div[role="radiogroup"] label p {
            color: #000000 !important;
            font-family: "Press Start 2P", cursive !important;
            font-size: .48rem !important;
            overflow-wrap: anywhere;
        }
        div[role="radiogroup"] label:nth-child(1) { background: #ffb3ba !important; }
        div[role="radiogroup"] label:nth-child(2) { background: #bae1ff !important; }
        div[role="radiogroup"] label:nth-child(3) { background: #baffc9 !important; }
        div[role="radiogroup"] label:nth-child(4) { background: #ffffba !important; }
        div[role="radiogroup"] label[aria-checked="true"] {
            outline: 3px solid #d1b3ff !important;
        }
        .achievement-card {
            text-align: center;
            min-height: 142px;
            color: #17202a !important;
        }
        .achievement-card h3, .achievement-card .subtle,
        .achievement-card .quest-meta, .achievement-card .eyebrow {
            color: #17202a !important;
        }
        .achievement-card:nth-child(6n + 1) { background: #ffb3ba !important; }
        .achievement-card:nth-child(6n + 2) { background: #bae1ff !important; }
        .achievement-card:nth-child(6n + 3) { background: #baffc9 !important; }
        .achievement-card:nth-child(6n + 4) { background: #ffffba !important; }
        .achievement-card:nth-child(6n + 5) { background: #f4c2f4 !important; }
        .achievement-card:nth-child(6n + 6) { background: #c9f2e3 !important; }
        .achievement-card.locked { filter: saturate(.58); opacity: .74; }
        .achievement-card.unlocked { opacity: 1; }
        div[data-baseweb="slider"] div[role="slider"] {
            border-radius: 0 !important;
            background-color: #ccff00 !important;
            border: 2px solid #000000 !important;
            box-shadow: 3px 3px 0 #000000 !important;
            width: 22px !important;
            height: 22px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <style>
    :root {{
        --ink: {theme_palette['ink']};
        --muted: {theme_palette['muted']};
        --line: {theme_palette['line']};
        --cyan: {theme_palette['cyan']};
        --violet: {theme_palette['violet']};
        --lime: {theme_palette['lime']};
        --card: {theme_palette['card_background']};
        --surface: {theme_palette['card_surface']};
        --progress-track: {theme_palette['progress_track']};
        --meter-background: {theme_palette['meter_background']};
        --meter-border: {theme_palette['meter_border']};
    }}
    [data-testid="stAppViewContainer"] {{ background: {theme_palette['page_background']} !important; }}
    [data-testid="stSidebar"] {{ background: {theme_palette['sidebar_background']} !important; }}
    .stat-card, .quest-card, .achievement-card, .xp-console {{ background: var(--card) !important; border-color: var(--line) !important; }}
    .stButton > button {{ background: {theme_palette['button_background']} !important; border-color: {theme_palette['button_border']} !important; color: var(--ink) !important; }}
    .stButton > button[kind="primary"] {{ background: linear-gradient(100deg, var(--violet), var(--cyan)) !important; color: {theme_palette['primary_button_text']} !important; }}
    .xp-track {{ background: var(--meter-background) !important; border-color: var(--meter-border) !important; }}
    .achievement-progress-track {{ background: var(--progress-track) !important; }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] {{
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label {{
        min-height: 52px;
        margin: 0 !important;
        padding: 10px 8px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 2px solid var(--line) !important;
        border-radius: 8px !important;
        box-shadow: 3px 3px 0 var(--line);
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label p {{
        margin: 0 !important;
        font-size: .48rem !important;
        overflow-wrap: anywhere;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label[aria-checked="true"] {{
        outline: 3px solid var(--cyan);
        outline-offset: 2px;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"],
    div[class*="st-key-learnabit_page"] [role="radiogroup"] {{
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label,
    div[class*="st-key-learnabit_page"] [role="radiogroup"] label {{
        min-height: 68px;
        margin: 0 !important;
        padding: 14px 10px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 2px solid {theme_palette['selector_shadow']} !important;
        border-radius: 9px !important;
        background: {theme_palette['selector_background']} !important;
        box-shadow: 4px 4px 0 {theme_palette['selector_shadow']} !important;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label p,
    div[class*="st-key-learnabit_page"] [role="radiogroup"] label p {{
        margin: 0 !important;
        color: {theme_palette['selector_text']} !important;
        font-family: "Press Start 2P", monospace !important;
        font-size: .68rem !important;
        line-height: 1.7 !important;
        overflow-wrap: anywhere;
    }}
    div[class*="st-key-learnabit_theme"] [role="radiogroup"] label[aria-checked="true"],
    div[class*="st-key-learnabit_page"] [role="radiogroup"] label[aria-checked="true"] {{
        background: {theme_palette['selector_active']} !important;
        outline: 2px solid {theme_palette['selector_shadow']} !important;
        outline-offset: 2px;
    }}
    div[class*="st-key-learnabit_page"] [role="radiogroup"] {{
        grid-template-columns: 1fr;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state["learnabit_theme"] == "adithyan":
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #fcfaf5 !important;
            background-image: radial-gradient(#dcd8c0 1px, transparent 1px) !important;
            background-size: 20px 20px !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 3px solid #000000 !important;
        }
        .stat-card, .quest-card, .achievement-card, .xp-console {
            background: #ffffff !important;
            border: 2px solid #000000 !important;
            box-shadow: 4px 4px 0 #000000 !important;
        }
        .stButton > button {
            background: #ccff00 !important;
            color: #000000 !important;
            border: 2px solid #000000 !important;
            box-shadow: 4px 4px 0 #000000 !important;
        }
        .stButton > button[kind="primary"] {
            background: #ccff00 !important;
            color: #000000 !important;
        }
        .xp-track {
            background: #20222a !important;
            border-color: #000000 !important;
        }
        .achievement-progress-track { background: #3b3f4e !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_profile():
    totals = db.get_totals()
    level, progress_xp, next_level_xp = get_level(totals["xp"])
    current_streak, longest_streak = get_streaks(db.get_completion_dates())
    return totals, level, progress_xp, next_level_xp, current_streak, longest_streak


def get_daily_xp_by_habit():
    """Return recent XP grouped by date and task."""
    if hasattr(db, "get_daily_xp_by_habit"):
        return db.get_daily_xp_by_habit(14)

    start = date.today() - timedelta(days=13)
    with db.connect() as connection:
        rows = connection.execute(
            """SELECT completions.completed_on, completions.habit_id,
                      habits.name, SUM(completions.xp_earned) AS xp
               FROM completions
               JOIN habits ON habits.id = completions.habit_id
               WHERE completions.completed_on >= ?
               GROUP BY completions.completed_on, completions.habit_id, habits.name
               ORDER BY completions.completed_on, habits.name""",
            (start.isoformat(),),
        ).fetchall()

    daily_xp = {}
    for row in rows:
        daily_xp.setdefault(row["completed_on"], {})[row["habit_id"]] = {
            "name": row["name"],
            "xp": row["xp"],
        }
    return daily_xp


def render_stat(label, value, note):
    st.markdown(
        f'<div class="stat-card"><div class="stat-label">{escape(label)}</div>'
        f'<div class="stat-value">{escape(value)}</div>'
        f'<div class="stat-note">{escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def circular_text_markup(first_text, second_text):
    badges = []
    for badge_id, text, color in (
        ("parv-ring", first_text, theme_palette["cyan"]),
        ("adithyan-ring", second_text, theme_palette["violet"]),
    ):
        safe_text = escape(text)
        badges.append(
            f'<div class="badge" aria-label="{safe_text}"><svg viewBox="0 0 150 150">'
            f'<defs><path id="{badge_id}" d="M 75,12 A 63,63 0 1,1 75,138 A 63,63 0 1,1 75,12"/></defs>'
            f'<text fill="{color}" font-family="monospace" font-size="12" textLength="390">'
            f'<textPath href="#{badge_id}" startOffset="50%" text-anchor="middle">{safe_text}</textPath>'
            f'</text></svg></div>'
        )
    return f"""
    <style>
    .badge-pair {{ display:flex; justify-content:flex-end; height:150px; }}
    .badge {{ width:144px; height:144px; cursor:grab; }}
    .badge svg {{ width:100%; height:100%; animation:spin 20s linear infinite; }}
    .badge:hover svg {{ animation-duration:5s; }}
    @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
    </style>
    <div class="badge-pair">{''.join(badges)}</div>
    <script>
    document.querySelectorAll('.badge').forEach((badge) => {{
        badge.addEventListener('pointerdown', () => badge.style.opacity = '0.7');
        badge.addEventListener('pointerup', () => badge.style.opacity = '1');
    }});
    </script>
    """


def render_quest(habit, completion_counts):
    completion_count = completion_counts.get(habit["id"], 0)
    with st.container(border=True):
        marker = "✓" if completion_count else "○"
        completion_label = (
            f"Completed {completion_count} time"
            f"{'s' if completion_count != 1 else ''} today"
            if completion_count else "Not completed today"
        )
        st.markdown(
            f'<div class="quest-card"><div class="quest-title">{marker} '
            f'{escape(habit["name"])}</div><div class="quest-meta">'
            f'{escape(habit["category"])} · {escape(habit["difficulty"])} quest · '
            f'+{habit["xp_reward"]} XP<br>{escape(completion_label)}</div></div>',
            unsafe_allow_html=True,
        )

        button_label = "Complete again" if completion_count else "Complete quest"
        if st.button(
            button_label,
            key=f"dashboard_complete_{habit['id']}",
            type="primary",
            use_container_width=True,
        ):
            award_quest_xp(habit)


def award_quest_xp(habit):
    was_level = get_level(db.get_totals()["xp"])[0]
    if db.complete_habit(habit["id"], habit["xp_reward"]):
        new_level = get_level(db.get_totals()["xp"])[0]
        st.toast(f"Quest complete! +{habit['xp_reward']} XP", icon="✨")
        if new_level > was_level:
            st.balloons()
            st.success(f"Level up! You reached level {new_level}.")
        st.rerun()


def seconds_until_midnight():
    now = datetime.now()
    next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
    return max(1, (next_midnight - now).total_seconds())


@st.fragment(run_every=seconds_until_midnight())
def render_dashboard():
    totals, level, progress_xp, next_level_xp, current_streak, longest_streak = get_profile()
    habits = db.list_habits(active_only=True)
    completion_counts = db.get_daily_completion_counts()
    completed_quest_count = sum(
        completion_counts.get(habit["id"], 0) > 0 for habit in habits
    )
    percent = int(completed_quest_count / len(habits) * 100) if habits else 0

    st.markdown('<div class="eyebrow">Your next small win starts here</div>', unsafe_allow_html=True)
    st.title("Make today count.")
    today_label = date.today().strftime("%A, %B ") + str(date.today().day)
    st.markdown(
        f'<p class="subtle">{today_label} · One quest at a time.</p>',
        unsafe_allow_html=True,
    )

    components.html(
        circular_text_markup(
            "Parv Srivastava - 26BYB0245",
            "Adithyan A. Nair - 26BYB0253",
        ),
        height=154,
        scrolling=False,
    )

    columns = st.columns(4)
    with columns[0]:
        render_stat(
            "CURRENT LEVEL",
            f"{level:02}",
            f"{progress_xp} / {next_level_xp} XP to next level",
        )
    with columns[1]:
        render_stat("TOTAL XP", f"{totals['xp']:,}", "Every little win adds up")
    with columns[2]:
        render_stat(
            "CURRENT STREAK",
            f"{current_streak} days",
            f"Longest: {longest_streak} days",
        )
    with columns[3]:
        render_stat(
            "TODAY'S PROGRESS",
            f"{percent}%",
            f"{completed_quest_count} of {len(habits)} quests",
        )

    progress_percent = progress_xp / next_level_xp * 100
    st.markdown(
        f'<div class="xp-console"><div class="xp-console-head">'
        f'<span class="xp-level-badge">LV {level}</span>'
        f'<span class="xp-next">{next_level_xp - progress_xp} XP TO LEVEL {level + 1}</span>'
        f'</div><div class="xp-track"><div class="xp-fill" '
        f'style="width:{progress_percent:.1f}%"></div></div>'
        f'<div class="xp-console-foot"><span>{progress_xp} / {next_level_xp} XP</span>'
        f'<span>NEXT RANK: LV {level + 1}</span></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<h2>Today\'s quests</h2>', unsafe_allow_html=True)
    if not habits:
        st.info("Your quest board is empty. Add a habit in My Quests to get started.")
    else:
        quest_columns = st.columns(3)
        for index, habit in enumerate(habits):
            with quest_columns[index % len(quest_columns)]:
                render_quest(habit, completion_counts)

    st.markdown('<h2>Recent activity</h2>', unsafe_allow_html=True)
    activity = db.get_recent_activity(9)
    if not activity:
        st.markdown('<p class="subtle">Your wins will show up here.</p>', unsafe_allow_html=True)
    else:
        activity_columns = st.columns(3)
        for index, item in enumerate(activity):
            with activity_columns[index % len(activity_columns)]:
                st.markdown(
                    f'<div class="quest-card"><div class="quest-title">'
                    f'{escape(item["name"])}</div><div class="quest-meta">'
                    f'{date.fromisoformat(item["completed_on"]).strftime("%b %d")} '
                    f'· +{item["xp_earned"]} XP</div></div>',
                    unsafe_allow_html=True,
                )


def render_quests():
    st.markdown('<div class="eyebrow">Build your daily rhythm</div>', unsafe_allow_html=True)
    st.title("My Quests")
    st.markdown(
        '<p class="subtle">Small, repeatable actions are how you gain XP.</p>',
        unsafe_allow_html=True,
    )

    with st.expander("＋ Create a quest", expanded=not db.list_habits()):
        with st.form("add_habit_form", clear_on_submit=True):
            name = st.text_input("Quest name", placeholder="e.g. Read for 20 minutes")
            first, second = st.columns(2)
            category = first.selectbox(
                "Category", ["Learning", "Wellness", "Creative", "Life", "Personal"]
            )
            difficulty = second.selectbox("Difficulty", list(DIFFICULTY_XP))
            st.caption(f"Reward: {DIFFICULTY_XP[difficulty]} XP")
            submitted = st.form_submit_button("Add quest", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Give your quest a name first.")
                else:
                    db.add_habit(name, category, difficulty, DIFFICULTY_XP[difficulty])
                    st.toast("Quest added to your board.", icon="✨")
                    st.rerun()

    st.subheader("Quest board")
    habits = db.list_habits()
    completion_counts = db.get_daily_completion_counts()
    if not habits:
        st.info("No quests yet. Create your first one above.")

    for habit in habits:
        with st.container(border=True):
            title_col, meta_col, toggle_col = st.columns([3, 2, 1])
            title_col.write(habit["name"])
            meta_col.caption(
                f"{habit['category']} · {habit['difficulty']} · {habit['xp_reward']} XP"
            )
            completion_count = completion_counts.get(habit["id"], 0)
            if completion_count:
                meta_col.caption(f"{completion_count} completed today")
            toggle_col.caption("Active" if habit["active"] else "Paused")

            with st.expander(f"Edit {habit['name']}"):
                with st.form(f"edit_{habit['id']}"):
                    edit_name = st.text_input(
                        "Name", value=habit["name"], key=f"name_{habit['id']}"
                    )
                    cols = st.columns(3)
                    categories = ["Learning", "Wellness", "Creative", "Life", "Personal"]
                    category = cols[0].selectbox(
                        "Category",
                        categories,
                        index=categories.index(habit["category"]),
                        key=f"category_{habit['id']}",
                    )
                    difficulty = cols[1].selectbox(
                        "Difficulty",
                        list(DIFFICULTY_XP),
                        index=list(DIFFICULTY_XP).index(habit["difficulty"]),
                        key=f"difficulty_{habit['id']}",
                    )
                    active = cols[2].checkbox(
                        "Active",
                        value=bool(habit["active"]),
                        key=f"active_{habit['id']}",
                    )
                    save, delete = st.columns([1, 1])
                    save_clicked = save.form_submit_button("Save changes", type="primary")
                    delete_clicked = delete.form_submit_button("Delete quest")
                    if save_clicked and edit_name.strip():
                        db.update_habit(
                            habit["id"],
                            edit_name,
                            category,
                            difficulty,
                            DIFFICULTY_XP[difficulty],
                            active,
                        )
                        st.toast("Quest updated.", icon="✅")
                        st.rerun()
                    if save_clicked and not edit_name.strip():
                        st.error("Quest name cannot be empty.")
                    if delete_clicked:
                        db.delete_habit(habit["id"])
                        st.toast("Quest deleted.")
                        st.rerun()


def render_achievements():
    totals, level, _, _, _, longest_streak = get_profile()
    progress_by_id = achievement_progress(
        totals["completions"],
        level,
        longest_streak,
        completion_dates=db.get_completion_dates(),
        completion_categories=db.get_completion_categories(),
        completed_before_9=db.has_completion_before("09:00"),
        completed_at_or_after_20=db.has_completion_at_or_after("20:00"),
        max_daily_xp=db.get_max_daily_xp(),
        max_daily_quest_completions=db.get_max_daily_quest_completions(),
    )
    unlocked = {
        achievement_id
        for achievement_id, (current, target) in progress_by_id.items()
        if current >= target
    }

    st.markdown('<div class="eyebrow">Little wins, permanently yours</div>', unsafe_allow_html=True)
    st.title("Achievements")
    st.markdown(
        f'<p class="subtle">{len(unlocked)} of {len(ACHIEVEMENTS)} unlocked</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for index, achievement in enumerate(ACHIEVEMENTS):
        current, target = progress_by_id[achievement["id"]]
        is_unlocked = achievement["id"] in unlocked
        with cols[index % 2]:
            status = "UNLOCKED" if is_unlocked else "LOCKED"
            class_name = "achievement-card" if is_unlocked else "achievement-card locked"
            progress_html = ""
            if not is_unlocked:
                percent = current / target * 100
                progress_html = (
                    f'<div class="achievement-progress-track"><div '
                    f'class="achievement-progress-fill" style="width:{percent:.1f}%"></div>'
                    f'</div><div class="quest-meta">{current} / {target}</div>'
                )
            st.markdown(
                f'<div class="{class_name}"><div class="achievement-icon">'
                f'{achievement["icon"]}</div><div class="eyebrow">{status}</div>'
                f'<h3>{escape(achievement["title"])}</h3>'
                f'<div class="subtle">{escape(achievement["detail"])}</div>'
                f'{progress_html}</div>',
                unsafe_allow_html=True,
            )


def render_statistics():
    chart_colors = [
        theme_palette["cyan"],
        theme_palette["violet"],
        theme_palette["lime"],
        "#ff8a65",
        "#64b5f6",
        "#ba68c8",
        "#81c784",
        "#ffb74d",
    ]
    totals, _, _, _, current_streak, longest_streak = get_profile()
    st.caption("Your effort, made visible")
    st.title("Statistics")
    st.write("A look at how your consistency is adding up.")

    first, second, third = st.columns(3)
    first.metric("Quests completed", totals["completions"])
    second.metric("Current streak", f"{current_streak} days")
    third.metric("Longest streak", f"{longest_streak} days")

    xp_by_habit = get_daily_xp_by_habit()
    days = [date.today() - timedelta(days=offset) for offset in reversed(range(14))]
    tasks = {}
    for daily_tasks in xp_by_habit.values():
        for habit_id, task in daily_tasks.items():
            tasks[habit_id] = task["name"]

    chart = go.Figure()
    sorted_tasks = sorted(tasks.items(), key=lambda item: item[1].lower())
    for index, (habit_id, task_name) in enumerate(sorted_tasks):
        values = [
            xp_by_habit.get(day.isoformat(), {}).get(habit_id, {}).get("xp", 0)
            for day in days
        ]
        chart.add_trace(
            go.Bar(
                name=task_name,
                x=days,
                y=values,
                marker_color=chart_colors[index % len(chart_colors)],
                hovertemplate=(
                    f"{task_name}<br>%{{x|%b %d}}<br>%{{y}} XP<extra></extra>"
                ),
            )
        )
    chart.update_layout(
        title="XP earned · last 14 days",
        height=320,
        margin=dict(l=10, r=10, t=55, b=10),
        xaxis=dict(showgrid=False, tickformat="%b %d"),
        yaxis=dict(title="XP", gridcolor=theme_palette["chart_grid"]),
        barmode="stack",
        legend=dict(title="Tasks"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme_palette["chart_text"]),
    )
    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    st.subheader("Activity calendar")
    today = date.today()
    calendar_start = today - timedelta(days=today.weekday() + 77)
    calendar_days = [calendar_start + timedelta(days=offset) for offset in range(84)]
    active_dates = set(db.get_completion_dates())
    rows = []
    date_labels = []
    for week in range(12):
        week_values = []
        week_dates = []
        for weekday in range(7):
            day = calendar_days[week * 7 + weekday]
            week_values.append(1 if day in active_dates else 0)
            week_dates.append(day.strftime("%A, %B ") + str(day.day) + day.strftime(", %Y"))
        rows.append(week_values)
        date_labels.append(week_dates)

    heatmap = go.Figure(
        go.Heatmap(
            z=rows,
            x=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            y=[f"Week {index + 1}" for index in range(12)],
            colorscale=[[0, theme_palette["heatmap_empty"]], [1, theme_palette["cyan"]]],
            showscale=False,
            customdata=date_labels,
            xgap=4,
            ygap=4,
            hovertemplate="%{customdata}<extra></extra>",
        )
    )
    heatmap.update_layout(
        height=260,
        margin=dict(l=5, r=5, t=5, b=5),
        yaxis=dict(showticklabels=False, gridcolor=theme_palette["chart_grid"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme_palette["chart_text"]),
    )
    st.plotly_chart(heatmap, use_container_width=True, config={"displayModeBar": False})


with st.sidebar:
    st.markdown('<div class="brand">learnabit<span>.</span></div>', unsafe_allow_html=True)
    st.caption("Learn a little. Level up.")
    st.radio("Theme", list(THEME_PALETTES), key="learnabit_theme")
    page = st.radio(
        "Navigate",
        ["Dashboard", "My Quests", "Achievements", "Statistics"],
        key="learnabit_page",
    )
    st.divider()
    totals, level, _, _, current_streak, _ = get_profile()
    st.write(f"**LEVEL {level}** · {totals['xp']} XP")
    st.caption(f"🔥 {current_streak}-day streak")
    st.caption("Your progress is saved on this device.")


if page == "Dashboard":
    render_dashboard()
elif page == "My Quests":
    render_quests()
elif page == "Achievements":
    render_achievements()
else:
    render_statistics()
