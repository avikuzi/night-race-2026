"""
🏃 Garmin Connect Sync — מירוץ הלילה 2026
Pulls running activities from Garmin Connect for Avi & Shachar,
matches them to the training plan, updates data.js, and redeploys.

Usage:
  python sync_garmin.py --login       # First-time login for both accounts
  python sync_garmin.py               # Sync both accounts
  python sync_garmin.py --deploy      # Sync + deploy to Firebase
"""

import os
import sys
import json
import re
import time
import socket
from datetime import datetime, timedelta
from pathlib import Path

# DNS override — resolve Garmin domains via Google DNS (8.8.8.8)
# Fixes issues when local DNS can't resolve sso.garmin.com
_original_getaddrinfo = socket.getaddrinfo
_dns_cache = {}

def _resolve_via_google_dns(host):
    """Resolve hostname using Google DNS (8.8.8.8) via nslookup."""
    if host in _dns_cache:
        return _dns_cache[host]
    try:
        import subprocess
        result = subprocess.run(
            ["nslookup", host, "8.8.8.8"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("Address") and "8.8.8.8" not in line and "#" not in line:
                ip = line.split(":")[-1].strip()
                if ip and not ip.startswith("::"):
                    _dns_cache[host] = ip
                    return ip
    except Exception:
        pass
    return None

def _patched_getaddrinfo(host, port, *args, **kwargs):
    garmin_domains = ["sso.garmin.com", "connect.garmin.com",
                      "mobile.integration.garmin.com", "apis.garmin.com"]
    if host in garmin_domains:
        ip = _resolve_via_google_dns(host)
        if ip:
            return _original_getaddrinfo(ip, port, *args, **kwargs)
    return _original_getaddrinfo(host, port, *args, **kwargs)

socket.getaddrinfo = _patched_getaddrinfo

from garminconnect import Garmin

# ============================================================
# Configuration
# ============================================================
BASE_DIR = Path(__file__).parent
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_JS_PATH = DASHBOARD_DIR / "data.js"
TOKENS_DIR = BASE_DIR / ".garmin_tokens"

PLAN_START = datetime(2026, 8, 13)
RACE_DATE = datetime(2026, 10, 28)
TOTAL_WEEKS = 11

# Credentials (used only for first login, tokens saved for future use)
ACCOUNTS = {
    "avi": {"email": "kuziostar@gmail.com", "password": "Azarazar12"},
    "shachar": {"email": "gsjcdx@gmail.com", "password": "N8!u?8V53:S5bpE"},
}

# Training plan V5 — 11 weeks, slot-based (no fixed dates)
# Each entry: (week, slot, type_keyword, planned_km)
TRAINING_PLAN = [
    # Week 1 — Base (13/8 — 16/8)
    {"week": 1, "slot": "volume", "type": "נפח", "dist": 7.0},
    # Week 2 — Base
    {"week": 2, "slot": "quality", "type": "איכות - פרטלק", "dist": 7.0},
    {"week": 2, "slot": "easy", "type": "ריצה קלה", "dist": 5.5},
    {"week": 2, "slot": "volume", "type": "נפח", "dist": 8.0},
    # Week 3 — Build
    {"week": 3, "slot": "quality", "type": "איכות - אינטרוולים", "dist": 7.5},
    {"week": 3, "slot": "easy", "type": "ריצה קלה", "dist": 5.5},
    {"week": 3, "slot": "volume", "type": "נפח", "dist": 9.0},
    # Week 4 — Build
    {"week": 4, "slot": "quality", "type": "איכות - טמפו", "dist": 8.0},
    {"week": 4, "slot": "easy", "type": "ריצה קלה", "dist": 5.5},
    {"week": 4, "slot": "volume", "type": "נפח", "dist": 10.0},
    # Week 5 — Build
    {"week": 5, "slot": "quality", "type": "איכות - פרטלק", "dist": 8.0},
    {"week": 5, "slot": "easy", "type": "ריצה קלה", "dist": 6.0},
    {"week": 5, "slot": "volume", "type": "נפח", "dist": 11.0},
    # Week 6 — Build / Recovery
    {"week": 6, "slot": "quality", "type": "איכות - טמפו", "dist": 7.0},
    {"week": 6, "slot": "easy", "type": "ריצה קלה", "dist": 5.0},
    {"week": 6, "slot": "volume", "type": "נפח", "dist": 9.0},
    # Week 7 — Peak
    {"week": 7, "slot": "quality", "type": "איכות - אינטרוולים", "dist": 9.0},
    {"week": 7, "slot": "easy", "type": "ריצה קלה", "dist": 6.0},
    {"week": 7, "slot": "volume", "type": "נפח", "dist": 12.0},
    # Week 8 — Peak
    {"week": 8, "slot": "quality", "type": "איכות - טמפו", "dist": 9.0},
    {"week": 8, "slot": "easy", "type": "ריצה קלה", "dist": 6.0},
    {"week": 8, "slot": "volume", "type": "נפח", "dist": 13.0},
    # Week 9 — Peak / Recovery
    {"week": 9, "slot": "quality", "type": "איכות - פרטלק", "dist": 8.0},
    {"week": 9, "slot": "easy", "type": "ריצה קלה", "dist": 5.0},
    {"week": 9, "slot": "volume", "type": "נפח", "dist": 10.0},
    # Week 10 — Taper
    {"week": 10, "slot": "quality", "type": "איכות - אינטרוולים", "dist": 7.0},
    {"week": 10, "slot": "easy", "type": "ריצה קלה", "dist": 4.5},
    # Week 11 — Taper / Race
    {"week": 11, "slot": "quality", "type": "ריצה קלה", "dist": 4.0},
    {"week": 11, "slot": "easy", "type": "ריצה קלה", "dist": 3.0},
    {"week": 11, "slot": "volume", "type": "מירוץ", "dist": 15.0},
]


# ============================================================
# Week helpers
# ============================================================
WEEK_RANGES = [
    (1, datetime(2026, 8, 13), datetime(2026, 8, 15)),
    (2, datetime(2026, 8, 16), datetime(2026, 8, 22)),
    (3, datetime(2026, 8, 23), datetime(2026, 8, 29)),
    (4, datetime(2026, 8, 30), datetime(2026, 9, 5)),
    (5, datetime(2026, 9, 6), datetime(2026, 9, 12)),
    (6, datetime(2026, 9, 13), datetime(2026, 9, 19)),
    (7, datetime(2026, 9, 20), datetime(2026, 9, 26)),
    (8, datetime(2026, 9, 27), datetime(2026, 10, 3)),
    (9, datetime(2026, 10, 4), datetime(2026, 10, 10)),
    (10, datetime(2026, 10, 11), datetime(2026, 10, 17)),
    (11, datetime(2026, 10, 18), datetime(2026, 10, 28)),
]

def get_week_for_date(date) -> int:
    """Return the week number (1-11) for a given date.

    Returns 0 if the date is before the plan starts,
    or -1 if the date is after the plan ends.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    for week_num, start_dt, end_dt in WEEK_RANGES:
        if start_dt.date() <= date.date() <= end_dt.date():
            return week_num
    if date < WEEK_RANGES[0][1]:
        return 0
    return -1


def get_week_entries(week: int) -> list:
    """Return all TRAINING_PLAN entries for a given week number."""
    return [e for e in TRAINING_PLAN if e["week"] == week]


# ============================================================
# Activity Classification
# ============================================================
def classify_activity(name: str, distance_km: float, day_of_week: int, week_plan_entries: list) -> str:
    """Classify a Garmin activity by its name into a slot type.

    Args:
        name: Activity name from Garmin
        distance_km: Distance in km
        day_of_week: 0=Monday ... 6=Sunday
        week_plan_entries: planned entries for this week

    Returns: 'quality', 'volume', 'easy', or None if unclassifiable
    """
    name_lower = name.lower().strip()

    # Pattern matching by activity name (Hebrew + English)
    volume_patterns = ['נפח', 'ארוכה', 'long', 'volume', 'ריצה ארוכה', 'long run']
    tempo_patterns = ['טמפו', 'tempo', 'threshold', 'סף']
    fartlek_patterns = ['פרטלק', 'fartlek']
    interval_patterns = ['אינטרוולים', 'interval', 'repeats', 'חזרות', '×', 'x800', 'x1000']
    easy_patterns = ['קלה', 'easy', 'recovery', 'שיקום', 'שחרור', 'נוחה']
    race_patterns = ['מירוץ', 'race', 'מירוץ הלילה']

    # Check race first
    for p in race_patterns:
        if p in name_lower:
            return 'volume'  # race is in the volume slot

    # Check quality patterns
    for p in tempo_patterns + fartlek_patterns + interval_patterns:
        if p in name_lower:
            return 'quality'

    # Check volume patterns
    for p in volume_patterns:
        if p in name_lower:
            return 'volume'

    # Check easy patterns
    for p in easy_patterns:
        if p in name_lower:
            return 'easy'

    # Fallback: use distance + day of week heuristics
    volume_entry = next((e for e in week_plan_entries if e['slot'] == 'volume'), None)
    volume_dist = volume_entry['dist'] if volume_entry else 8.0

    # Friday (4) or Saturday (5) with long distance → volume
    if day_of_week in (4, 5) and distance_km >= volume_dist * 0.75:
        return 'volume'

    # Short distance with no quality indicators → easy
    if distance_km <= 6.0:
        return 'easy'

    # Default → quality
    return 'quality'


# ============================================================
# Garmin Connect Auth
# ============================================================
def get_token_file(person: str) -> Path:
    return TOKENS_DIR / f"{person}_tokens.json"


def connect_garmin(person: str) -> Garmin:
    """Connect to Garmin, using saved tokens if available."""
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    token_file = get_token_file(person)
    account = ACCOUNTS[person]

    # Try loading from saved tokens first
    if token_file.exists():
        try:
            print(f"   🔄 {person}: טוען token שמור...")
            tokenstore = token_file.read_text(encoding="utf-8")
            client = Garmin()
            client.login(tokenstore)
            name = client.get_full_name()
            print(f"   ✅ {person}: מחובר ({name})")
            # Re-save refreshed tokens
            try:
                token_file.write_text(client.client.dumps(), encoding="utf-8")
            except Exception:
                pass
            return client
        except Exception as e:
            print(f"   ⚠️  Token פג תוקף, מתחבר מחדש... ({e})")

    # Fresh login
    try:
        print(f"   🔐 {person}: מתחבר עם אימייל וסיסמה...")
        client = Garmin(account["email"], account["password"])
        client.login()
        # Save tokens for future use
        token_data = client.client.dumps()
        token_file.write_text(token_data, encoding="utf-8")
        name = client.get_full_name()
        print(f"   ✅ {person}: מחובר ({name}) — token נשמר")
        return client
    except Exception as e:
        print(f"   ❌ {person}: שגיאה בהתחברות — {e}")
        return None


# ============================================================
# Fetch Activities
# ============================================================
def fetch_running_activities(client: Garmin, person: str, start: str, end: str) -> list:
    """Fetch running activities within date range."""
    print(f"   📥 {person}: מושך ריצות {start} — {end}...")

    try:
        activities = client.get_activities_by_date(start, end, "running")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")
        return []

    results = []
    for act in activities:
        act_date = str(act.get("startTimeLocal", ""))[:10]
        distance_m = act.get("distance", 0) or 0
        distance_km = round(distance_m / 1000, 2)
        duration_sec = act.get("duration", 0) or 0

        if distance_km < 1.0:
            continue  # Skip very short activities

        avg_pace_sec = (duration_sec / distance_km) if distance_km > 0 else 0
        pace_min = int(avg_pace_sec // 60)
        pace_sec = int(avg_pace_sec % 60)
        pace_str = f"{pace_min}:{pace_sec:02d}"

        results.append({
            "date": act_date,
            "distance_km": distance_km,
            "pace": pace_str,
            "name": act.get("activityName", ""),
            "id": act.get("activityId", ""),
        })

    print(f"   📊 {person}: נמצאו {len(results)} ריצות")
    return results


# ============================================================
# Match Activities → Training Plan
# ============================================================
def match_activities(activities: list, plan: list, person: str = "") -> dict:
    """Match a list of activities to the planned workouts.

    Algorithm:
      1. For each activity, determine its week.
      2. Classify the activity into a slot ('quality', 'volume', 'easy').
      3. Match to the planned workout in that week with the same slot.
      4. Track used slots per week to avoid duplicates.

    Returns: dict mapping plan_index -> activity_dict
    """
    matches = {}
    # Track used slots per week: {week_num: set of used slot names}
    used_slots = {}

    for act in sorted(activities, key=lambda a: a["date"]):
        act_date = datetime.strptime(act["date"], "%Y-%m-%d")
        week = get_week_for_date(act_date)
        if week <= 0:
            continue  # Before plan or after plan

        # Special holiday rollover handling:
        # Shachar ran on Sunday night 13/09 (Rosh Hashana Day 2), count towards Week 5 easy slot
        if person == "shachar" and act["date"] == "2026-09-13" and "easy" not in used_slots.get(5, set()):
            week = 5

        week_entries = get_week_entries(week)
        if not week_entries:
            continue

        day_of_week = act_date.weekday()  # 0=Monday ... 6=Sunday
        slot = classify_activity(act["name"], act["distance_km"], day_of_week, week_entries)
        if slot is None:
            continue

        # Find the plan entry for this week + slot
        plan_entry = None
        plan_index = None
        for i, entry in enumerate(plan):
            if entry["week"] == week and entry["slot"] == slot:
                plan_entry = entry
                plan_index = i
                break

        if plan_entry is None:
            continue

        # Check if this slot is already used for this week
        week_used = used_slots.setdefault(week, set())
        if slot in week_used:
            continue

        week_used.add(slot)
        matches[plan_index] = act

    return matches


# ============================================================
# Update data.js
# ============================================================
def update_data_js(avi_matches: dict, shachar_matches: dict):
    """Update actual values in data.js."""
    content = DATA_JS_PATH.read_text(encoding="utf-8")
    updates = 0

    plan_start = content.find("const trainingPlan = [")
    if plan_start == -1:
        print("❌ לא נמצא trainingPlan ב-data.js!")
        return 0

    entry_pattern = re.compile(r'\{\s*week:\s*\d+,\s*slot:')
    entries = list(entry_pattern.finditer(content, plan_start))

    # Process in reverse order to preserve indices
    for workout_idx in sorted(set(list(avi_matches.keys()) + list(shachar_matches.keys())), reverse=True):
        if workout_idx >= len(entries):
            continue

        entry_start = entries[workout_idx].start()
        # Find entry end
        brace_depth = 0
        entry_end = entry_start
        for ci in range(entry_start, len(content)):
            if content[ci] == '{':
                brace_depth += 1
            elif content[ci] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    entry_end = ci + 1
                    break

        entry_text = content[entry_start:entry_end]

        # Update Avi
        avi_act = avi_matches.get(workout_idx)
        if avi_act:
            entry_text = re.sub(
                r'actualDistanceAvi:\s*(null|[\d.]+)',
                f'actualDistanceAvi: {avi_act["distance_km"]}',
                entry_text
            )
            entry_text = re.sub(
                r"actualPaceAvi:\s*(null|'[^']*')",
                f"actualPaceAvi: '{avi_act['pace']}'",
                entry_text
            )
            entry_text = re.sub(
                r"actualDateAvi:\s*(null|'[^']*')",
                f"actualDateAvi: '{avi_act['date']}'",
                entry_text
            )
            updates += 1

        # Update Shachar
        shachar_act = shachar_matches.get(workout_idx)
        if shachar_act:
            entry_text = re.sub(
                r'actualDistanceShachar:\s*(null|[\d.]+)',
                f'actualDistanceShachar: {shachar_act["distance_km"]}',
                entry_text
            )
            entry_text = re.sub(
                r"actualPaceShachar:\s*(null|'[^']*')",
                f"actualPaceShachar: '{shachar_act['pace']}'",
                entry_text
            )
            entry_text = re.sub(
                r"actualDateShachar:\s*(null|'[^']*')",
                f"actualDateShachar: '{shachar_act['date']}'",
                entry_text
            )
            updates += 1

        content = content[:entry_start] + entry_text + content[entry_end:]

    # Update LAST_SYNC timestamp
    now_str = datetime.now().strftime("%d/%m/%Y, %H:%M")
    content = re.sub(r"const LAST_SYNC = '[^']*';", f"const LAST_SYNC = '{now_str}';", content)

    DATA_JS_PATH.write_text(content, encoding="utf-8")
    print(f"\n✏️  עודכנו {updates} רשומות ב-data.js")
    return updates


# ============================================================
# Firebase Deploy
# ============================================================
def deploy_firebase():
    # Automatically bump cache-busting timestamp in index.html
    index_html_path = DASHBOARD_DIR / "index.html"
    if index_html_path.exists():
        html = index_html_path.read_text(encoding="utf-8")
        ts = int(time.time())
        html = re.sub(r'(\.(?:js|css))\?v=[^"\'\s>]+', rf'\1?v={ts}', html)
        index_html_path.write_text(html, encoding="utf-8")

    print("\n🚀 פורס ל-Firebase...")
    exit_code = os.system(
        'powershell -Command "'
        "$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
        "[System.Environment]::GetEnvironmentVariable('Path','User'); "
        'firebase deploy --only hosting --project night-race-2026"'
    )
    if exit_code == 0:
        print("✅ הפריסה הושלמה!")
        print("🔗 https://night-race-2026.web.app")
    else:
        print("❌ שגיאה בפריסה")


# ============================================================
# Main
# ============================================================
def main():
    args = sys.argv[1:]

    print("=" * 50)
    print("🌙 Garmin Connect Sync — מירוץ הלילה 2026")
    print("=" * 50)

    # Determine date range
    today = datetime.now()
    start = PLAN_START
    end = min(today, RACE_DATE)

    if today < start:
        print(f"\n⏳ התוכנית מתחילה ב-{start.strftime('%d/%m/%Y')}.")
        if "--login" not in args:
            print("   הרץ עם --login כדי להתחבר מראש.")
            return

    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    # Connect both accounts
    print("\n" + "─" * 40)
    print("👤 אבי:")
    avi_client = connect_garmin("avi")

    time.sleep(2)

    print("\n👤 שחר:")
    shachar_client = connect_garmin("shachar")

    if "--login" in args:
        if avi_client and shachar_client:
            print("\n✅ שני החשבונות מחוברים! Tokens נשמרו.")
        return

    if today < start:
        return

    # Fetch activities
    print("\n" + "─" * 40)
    avi_activities = []
    shachar_activities = []

    if avi_client:
        avi_activities = fetch_running_activities(avi_client, "אבי", start_str, end_str)

    if shachar_client:
        shachar_activities = fetch_running_activities(shachar_client, "שחר", start_str, end_str)

    # Match to plan
    print("\n" + "─" * 40)
    print("🔄 מתאים ריצות לתוכנית...")

    avi_matches = match_activities(avi_activities, TRAINING_PLAN, "avi")
    shachar_matches = match_activities(shachar_activities, TRAINING_PLAN, "shachar")

    print(f"   אבי: {len(avi_matches)} אימונים מותאמים")
    print(f"   שחר: {len(shachar_matches)} אימונים מותאמים")

    # Show matches
    if avi_matches or shachar_matches:
        print("\n📋 אימונים שנמצאו:")
        for plan_idx, entry in enumerate(TRAINING_PLAN):
            avi = avi_matches.get(plan_idx)
            shachar = shachar_matches.get(plan_idx)
            if avi or shachar:
                print(f"   שבוע {entry['week']} | {entry['slot']} | {entry['type']}")
                if avi:
                    print(f"      🟣 אבי: {avi['distance_km']} ק\"מ @ {avi['pace']} ({avi['date']})")
                if shachar:
                    print(f"      🩷 שחר: {shachar['distance_km']} ק\"מ @ {shachar['pace']} ({shachar['date']})")

        update_data_js(avi_matches, shachar_matches)
    else:
        print("\n⚠️  לא נמצאו ריצות להתאמה")

    # Deploy
    if "--deploy" in args:
        deploy_firebase()
    else:
        print("\n💡 הוסף --deploy כדי לפרוס ל-Firebase")

    print("\n✨ סיום!")


if __name__ == "__main__":
    main()
