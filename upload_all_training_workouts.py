"""
Upload all Easy and Volume workouts for both Avi and Shachar to Garmin Connect
so they can choose ANY workout from their Garmin watch library freely at any time.
"""

import time
from sync_garmin import connect_garmin

def pace_to_speeds(pace_str: str) -> tuple[float, float]:
    parts = pace_str.split("-")
    def p2s(p):
        m, s = p.strip().split(":")
        sec = int(m) * 60 + int(s)
        return 1000.0 / sec

    speed_slow = p2s(parts[1]) if len(parts) > 1 else p2s(parts[0]) * 0.95
    speed_fast = p2s(parts[0])
    return round(speed_slow, 6), round(speed_fast, 6)

ADDITIONAL_WORKOUTS = [
    # === Week 2 ===
    {"week": 2, "slot": "easy", "title": "ריצה קלה 5.5 ק\"מ — שבוע 2", "dist_m": 5500.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:10-6:30", "desc": "ריצת התאוששות קלה ונוחה"},
    {"week": 2, "slot": "volume", "title": "ריצת נפח 8 ק\"מ — שבוע 2", "dist_m": 8000.0, "pace_avi": "6:40-7:10", "pace_shachar": "5:50-6:10", "desc": "ריצת נפח אירובית בסוף השבוע"},

    # === Week 3 ===
    {"week": 3, "slot": "easy", "title": "ריצה קלה 5.5 ק\"מ — שבוע 3", "dist_m": 5500.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:05-6:25", "desc": "ריצת שיקום והתאוששות קלה"},
    {"week": 3, "slot": "volume", "title": "ריצת נפח 9 ק\"מ — שבוע 3", "dist_m": 9000.0, "pace_avi": "6:35-7:05", "pace_shachar": "5:45-6:05", "desc": "ריצת נפח אירובית בסוף השבוע"},

    # === Week 4 ===
    {"week": 4, "slot": "easy", "title": "ריצה קלה 5.5 ק\"מ — שבוע 4", "dist_m": 5500.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:05-6:25", "desc": "ריצת שיקום והתאוששות קלה"},
    {"week": 4, "slot": "volume", "title": "ריצת נפח 10 ק\"מ — שבוע 4", "dist_m": 10000.0, "pace_avi": "6:30-7:00", "pace_shachar": "5:45-6:05", "desc": "ריצת נפח דו-ספרתית ראשונה"},

    # === Week 5 ===
    {"week": 5, "slot": "easy", "title": "ריצה קלה 6 ק\"מ — שבוע 5", "dist_m": 6000.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:05-6:25", "desc": "ריצה קלה"},
    {"week": 5, "slot": "volume", "title": "ריצת נפח 11 ק\"מ — שבוע 5", "dist_m": 11000.0, "pace_avi": "6:30-7:00", "pace_shachar": "5:40-6:00", "desc": "ריצת נפח ארוכה"},

    # === Week 6 ===
    {"week": 6, "slot": "easy", "title": "ריצה קלה 5 ק\"מ — שבוע 6", "dist_m": 5000.0, "pace_avi": "7:00-7:20", "pace_shachar": "6:15-6:35", "desc": "שבוע שחרור — ריצה קלה"},
    {"week": 6, "slot": "volume", "title": "ריצת נפח 9 ק\"מ — שבוע 6", "dist_m": 9000.0, "pace_avi": "6:40-7:10", "pace_shachar": "5:50-6:10", "desc": "שבוע שחרור — נפח מבוקר"},

    # === Week 7 ===
    {"week": 7, "slot": "easy", "title": "ריצה קלה 6 ק\"מ — שבוע 7", "dist_m": 6000.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:05-6:25", "desc": "ריצה קלה"},
    {"week": 7, "slot": "volume", "title": "ריצת נפח 12 ק\"מ — שבוע 7", "dist_m": 12000.0, "pace_avi": "6:25-6:55", "pace_shachar": "5:40-6:00", "desc": "ריצת השיא 1"},

    # === Week 8 ===
    {"week": 8, "slot": "easy", "title": "ריצה קלה 6 ק\"מ — שבוע 8", "dist_m": 6000.0, "pace_avi": "6:50-7:15", "pace_shachar": "6:05-6:25", "desc": "ריצה קלה"},
    {"week": 8, "slot": "volume", "title": "ריצת נפח 13 ק\"מ — שבוע 8", "dist_m": 13000.0, "pace_avi": "6:20-6:50", "pace_shachar": "5:35-5:55", "desc": "ריצת הנפח הארוכה ביותר בבלוק"},

    # === Week 9 ===
    {"week": 9, "slot": "easy", "title": "ריצה קלה 5 ק\"מ — שבוע 9", "dist_m": 5000.0, "pace_avi": "7:00-7:20", "pace_shachar": "6:15-6:35", "desc": "ריצה קלה"},
    {"week": 9, "slot": "volume", "title": "ריצת נפח 10 ק\"מ — שבוע 9", "dist_m": 10000.0, "pace_avi": "6:30-7:00", "pace_shachar": "5:45-6:05", "desc": "ריצת נפח מתונה"},

    # === Week 10 ===
    {"week": 10, "slot": "easy", "title": "ריצה קלה 4.5 ק\"מ — שבוע 10", "dist_m": 4500.0, "pace_avi": "7:00-7:20", "pace_shachar": "6:15-6:35", "desc": "טייפר — ריצה קלה"},
    {"week": 10, "slot": "volume", "title": "ריצת נפח 8 ק\"מ — שבוע 10", "dist_m": 8000.0, "pace_avi": "6:40-7:10", "pace_shachar": "5:50-6:10", "desc": "טייפר — ריצת נפח קצרה"},

    # === Week 11 ===
    {"week": 11, "slot": "easy", "title": "שייקאאוט קל 3 ק\"מ — שבוע 11", "dist_m": 3000.0, "pace_avi": "7:00-7:20", "pace_shachar": "6:15-6:35", "desc": "שבוע המירוץ — שייקאאוט קצרצר"},
    {"week": 11, "slot": "volume", "title": "🏁 מירוץ הלילה 15 ק\"מ!", "dist_m": 15000.0, "pace_avi": "5:40", "pace_shachar": "5:20", "desc": "היום הגדול! מירוץ הלילה 15 ק\"מ"},
]

def build_run_payload(w_def: dict, person: str) -> dict:
    pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]
    speed_slow, speed_fast = pace_to_speeds(pace_str)

    steps = [
        {
            "type": "ExecutableStepDTO",
            "stepOrder": 1,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"{w_def['desc']} | קצב יעד: {pace_str}",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["dist_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        }
    ]

    return {
        "workoutName": w_def["title"],
        "description": f"{w_def['desc']} | מרחק: {w_def['dist_m']/1000} ק\"מ | קצב יעד: {pace_str}",
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
                "workoutSteps": steps
            }
        ]
    }

def upload_all_for_person(person: str):
    name_display = "אבי (Avikuzi)" if person == "avi" else "שחר (Shahar Tal)"
    print("\n" + "=" * 60)
    print(f"🚀 מעלה את אימוני הריצה הקלה והנפח עבור {name_display}...")
    print("=" * 60)

    client = connect_garmin(person)
    if not client:
        print(f"❌ שגיאה בהתחברות עבור {person}")
        return

    existing = client.get_workouts(limit=100)
    existing_names = {w.get("workoutName") for w in existing if isinstance(w, dict)}
    success = 0

    for w_def in ADDITIONAL_WORKOUTS:
        title = w_def["title"]
        if title in existing_names:
            print(f"   ⏩ {title} כבר קיים בחשבון, מדלג...")
            success += 1
            continue

        payload = build_run_payload(w_def, person)
        pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]
        print(f"   📤 מעלה {title} (קצב: {pace_str})...", end="", flush=True)

        try:
            res = client.upload_workout(payload)
            w_id = res.get("workoutId") if isinstance(res, dict) else None
            print(f" ✅ הושלם! (ID: {w_id})")
            success += 1
            time.sleep(1.0)
        except Exception as e:
            print(f" ❌ שגיאה: {e}")

    print(f"\n✨ סה\"כ {success}/{len(ADDITIONAL_WORKOUTS)} אימונים זמינים עבור {person}!")

def main():
    print("============================================================")
    print("🏃 העלאת כל אימוני הריצה הקלה והנפח ל-Garmin Connect")
    print("============================================================")

    upload_all_for_person("shachar")
    upload_all_for_person("avi")

if __name__ == "__main__":
    main()
