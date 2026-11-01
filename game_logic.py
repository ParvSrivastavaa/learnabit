"""Small, readable rules for Learnabit's progression system."""

from datetime import date, timedelta

DIFFICULTY_XP = {"Easy": 10, "Standard": 20, "Medium": 20, "Hard": 35}

ACHIEVEMENTS = [
    {"id": "first_quest", "title": "First Steps", "detail": "Complete your first quest.", "icon": "✦"},
    {"id": "quest_starter", "title": "Quest Starter", "detail": "Complete 5 quests.", "icon": "⚔"},
    {"id": "quest_collector_25", "title": "Quest Collector", "detail": "Complete 25 quests.", "icon": "◈"},
    {"id": "century", "title": "Century Club", "detail": "Complete 100 quests.", "icon": "💯"},
    {"id": "quest_collector_250", "title": "Legendary Collector", "detail": "Complete 250 quests.", "icon": "🏆"},
    {"id": "three_day_streak", "title": "Three-Day Groove", "detail": "Complete quests on 3 consecutive days.", "icon": "✧"},
    {"id": "week_streak", "title": "Seven-Day Spark", "detail": "Reach a 7-day streak.", "icon": "🔥"},
    {"id": "comeback", "title": "Comeback Win", "detail": "Complete a quest after a day off.", "icon": "↗"},
    {"id": "well_rounded", "title": "Well-Rounded", "detail": "Complete quests from 3 categories.", "icon": "✺"},
    {"id": "early_bird", "title": "Early Bird", "detail": "Complete a quest before 9 a.m.", "icon": "🌅"},
    {"id": "night_owl", "title": "Night Owl", "detail": "Complete a quest at or after 8 p.m.", "icon": "🌙"},
    {"id": "big_xp_day", "title": "Big XP Energy", "detail": "Earn 100 XP in one day.", "icon": "⚡"},
    {"id": "quest_marathon", "title": "Quest Marathon", "detail": "Complete one quest 5 times in a day.", "icon": "🏃"},
    {"id": "level_5", "title": "Level Up", "detail": "Reach level 5.", "icon": "⬆"},
    {"id": "level_10", "title": "Double Digits", "detail": "Reach level 10.", "icon": "⚡"},
    {"id": "level_25", "title": "Level Legend", "detail": "Reach level 25.", "icon": "👑"},
]


def get_level(xp):
    level = xp // 100 + 1
    progress_xp = xp % 100
    return level, progress_xp, 100


def get_streaks(completion_dates, today=None):
    """Return current and longest streaks from unique completion dates."""
    today = today or date.today()
    days = set(completion_dates)
    if not days:
        return 0, 0

    ordered = sorted(days)
    longest = run = 1
    for previous, current in zip(ordered, ordered[1:]):
        if current == previous + timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    anchor = today if today in days else today - timedelta(days=1)
    current_streak = 0
    while anchor in days:
        current_streak += 1
        anchor -= timedelta(days=1)
    return current_streak, longest


def achievement_progress(
    total_completions,
    level,
    longest_streak,
    completion_dates=(),
    completion_categories=(),
    completed_before_9=False,
    completed_at_or_after_20=False,
    max_daily_xp=0,
    max_daily_quest_completions=0,
):
    ordered_dates = sorted(set(completion_dates))
    has_comeback = any(
        (current - previous).days > 1
        for previous, current in zip(ordered_dates, ordered_dates[1:])
    )
    categories_count = len(set(completion_categories))
    targets = {
        "first_quest": (total_completions, 1),
        "quest_starter": (total_completions, 5),
        "quest_collector_25": (total_completions, 25),
        "century": (total_completions, 100),
        "quest_collector_250": (total_completions, 250),
        "three_day_streak": (longest_streak, 3),
        "week_streak": (longest_streak, 7),
        "comeback": (int(has_comeback), 1),
        "well_rounded": (categories_count, 3),
        "early_bird": (int(completed_before_9), 1),
        "night_owl": (int(completed_at_or_after_20), 1),
        "big_xp_day": (max_daily_xp, 100),
        "quest_marathon": (max_daily_quest_completions, 5),
        "level_5": (level, 5),
        "level_10": (level, 10),
        "level_25": (level, 25),
    }
    return {
        achievement_id: (min(max(current, 0), target), target)
        for achievement_id, (current, target) in targets.items()
    }


def unlocked_achievements(*args, **kwargs):
    progress = achievement_progress(*args, **kwargs)
    return {
        achievement_id
        for achievement_id, (current, target) in progress.items()
        if current >= target
    }
