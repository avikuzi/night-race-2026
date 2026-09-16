"""
Update all Garmin workouts for Weeks 4 to 11 on both accounts (Avi and Shachar)
with calibrated paces and updated Week 11 structure (Shakeout + Strides instead of Tempo).
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

WORKOUT_DEFS = [
    # === Week 4 ===
    {
        "week": 4, "slot": "quality",
        "title": "ריצת טמפו 8 ק\"מ — שבוע 4",
        "desc": "2 ק\"מ חימום + 30 דק' טמפו רציף + 1 ק\"מ שחרור",
        "pace_avi": "5:40-5:55", "pace_shachar": "5:25-5:40",
        "structure": "tempo", "tempo_minutes": 30, "warmup_m": 2000, "cooldown_m": 1000,
    },
    {
        "week": 4, "slot": "easy",
        "title": "ריצה קלה 5.5 ק\"מ — שבוע 4",
        "desc": "ריצת התאוששות קלה",
        "pace_avi": "7:00-7:30", "pace_shachar": "6:20-6:45",
        "structure": "simple", "dist_m": 5500,
    },
    {
        "week": 4, "slot": "volume",
        "title": "ריצת נפח 10 ק\"מ — שבוע 4",
        "desc": "ריצת נפח דו-ספרתית ראשונה",
        "pace_avi": "6:45-7:15", "pace_shachar": "6:05-6:30",
        "structure": "simple", "dist_m": 10000,
    },

    # === Week 5 ===
    {
        "week": 5, "slot": "quality",
        "title": "אימון פרטלק 8 ק\"מ — שבוע 5",
        "desc": "2 ק\"מ חימום + 6 חזרות (2 דק' מהיר / 1:30 קל) + 1 ק\"מ שחרור",
        "pace_avi": "5:35-5:50", "pace_shachar": "5:20-5:35",
        "structure": "repeats", "warmup_m": 2000, "cooldown_m": 1000,
        "repeats": 6, "work_sec": 120, "rest_sec": 90,
    },
    {
        "week": 5, "slot": "easy",
        "title": "ריצה קלה 6 ק\"מ — שבוע 5",
        "desc": "ריצת שיקום והתאוששות",
        "pace_avi": "7:00-7:30", "pace_shachar": "6:20-6:45",
        "structure": "simple", "dist_m": 6000,
    },
    {
        "week": 5, "slot": "volume",
        "title": "ריצת נפח 11 ק\"מ — שבוע 5",
        "desc": "ריצת נפח ארוכה ומבוקרת",
        "pace_avi": "6:45-7:15", "pace_shachar": "6:05-6:30",
        "structure": "simple", "dist_m": 11000,
    },

    # === Week 6 ===
    {
        "week": 6, "slot": "quality",
        "title": "ריצת טמפו 7 ק\"מ — שבוע 6",
        "desc": "שבוע שחרור חלקי — 2 ק\"מ חימום + 25 דק' טמפו + 1 ק\"מ שחרור",
        "pace_avi": "5:40-5:50", "pace_shachar": "5:25-5:35",
        "structure": "tempo", "tempo_minutes": 25, "warmup_m": 2000, "cooldown_m": 1000,
    },
    {
        "week": 6, "slot": "easy",
        "title": "ריצה קלה 5 ק\"מ — שבוע 6",
        "desc": "ריצת שחרור והתאוששות",
        "pace_avi": "7:05-7:35", "pace_shachar": "6:25-6:50",
        "structure": "simple", "dist_m": 5000,
    },
    {
        "week": 6, "slot": "volume",
        "title": "ריצת נפח 9 ק\"מ — שבוע 6",
        "desc": "ריצת נפח מתונה לשבוע שחרור",
        "pace_avi": "6:45-7:15", "pace_shachar": "6:10-6:30",
        "structure": "simple", "dist_m": 9000,
    },

    # === Week 7 ===
    {
        "week": 7, "slot": "quality",
        "title": "אינטרוולים 5x1000מ (9 ק\"מ) — שבוע 7",
        "desc": "2 ק\"מ חימום + 5x1000מ (מנוחה 2:30) + 1.5 ק\"מ שחרור",
        "pace_avi": "5:30-5:45", "pace_shachar": "5:15-5:30",
        "structure": "intervals_dist", "warmup_m": 2000, "cooldown_m": 1500,
        "repeats": 5, "work_m": 1000, "rest_sec": 150,
    },
    {
        "week": 7, "slot": "easy",
        "title": "ריצה קלה 6 ק\"מ — שבוע 7",
        "desc": "ריצת התאוששות",
        "pace_avi": "7:00-7:30", "pace_shachar": "6:20-6:45",
        "structure": "simple", "dist_m": 6000,
    },
    {
        "week": 7, "slot": "volume",
        "title": "ריצת נפח 12 ק\"מ — שבוע 7",
        "desc": "ריצת שיא 1 — 12 ק\"מ נפח אירובי",
        "pace_avi": "6:40-7:10", "pace_shachar": "6:00-6:25",
        "structure": "simple", "dist_m": 12000,
    },

    # === Week 8 ===
    {
        "week": 8, "slot": "quality",
        "title": "ריצת טמפו 9 ק\"מ — שבוע 8",
        "desc": "2 ק\"מ חימום + 35 דק' טמפו + 1.5 ק\"מ שחרור",
        "pace_avi": "5:35-5:50", "pace_shachar": "5:20-5:35",
        "structure": "tempo", "tempo_minutes": 35, "warmup_m": 2000, "cooldown_m": 1500,
    },
    {
        "week": 8, "slot": "easy",
        "title": "ריצה קלה 6 ק\"מ — שבוע 8",
        "desc": "ריצת התאוששות",
        "pace_avi": "7:00-7:30", "pace_shachar": "6:20-6:45",
        "structure": "simple", "dist_m": 6000,
    },
    {
        "week": 8, "slot": "volume",
        "title": "ריצת נפח 13 ק\"מ — שבוע 8",
        "desc": "ריצת הנפח הארוכה ביותר בבלוק האימונים!",
        "pace_avi": "6:35-7:05", "pace_shachar": "5:55-6:20",
        "structure": "simple", "dist_m": 13000,
    },

    # === Week 9 ===
    {
        "week": 9, "slot": "quality",
        "title": "אימון פרטלק 8 ק\"מ — שבוע 9",
        "desc": "שבוע שחרור חלקי — 2 ק\"מ חימום + פרטלק מהנה + 1 ק\"מ שחרור",
        "pace_avi": "5:35-5:50", "pace_shachar": "5:20-5:35",
        "structure": "repeats", "warmup_m": 2000, "cooldown_m": 1000,
        "repeats": 6, "work_sec": 120, "rest_sec": 90,
    },
    {
        "week": 9, "slot": "easy",
        "title": "ריצה קלה 5 ק\"מ — שבוע 9",
        "desc": "ריצת שחרור",
        "pace_avi": "7:05-7:35", "pace_shachar": "6:25-6:50",
        "structure": "simple", "dist_m": 5000,
    },
    {
        "week": 9, "slot": "volume",
        "title": "ריצת נפח 10 ק\"מ — שבוע 9",
        "desc": "ריצת נפח מתונה",
        "pace_avi": "6:45-7:15", "pace_shachar": "6:05-6:30",
        "structure": "simple", "dist_m": 10000,
    },

    # === Week 10 ===
    {
        "week": 10, "slot": "quality",
        "title": "אינטרוולים 4x1000מ חדות (7 ק\"מ) — שבוע 10",
        "desc": "טייפר וחידוד — 2 ק\"מ חימום + 4x1000מ (מנוחה 2:00) + 1 ק\"מ שחרור",
        "pace_avi": "5:30-5:45", "pace_shachar": "5:15-5:30",
        "structure": "intervals_dist", "warmup_m": 2000, "cooldown_m": 1000,
        "repeats": 4, "work_m": 1000, "rest_sec": 120,
    },
    {
        "week": 10, "slot": "easy",
        "title": "ריצה קלה 4.5 ק\"מ — שבוע 10",
        "desc": "טייפר — ריצה קלה",
        "pace_avi": "7:05-7:35", "pace_shachar": "6:25-6:50",
        "structure": "simple", "dist_m": 4500,
    },
    {
        "week": 10, "slot": "volume",
        "title": "ריצת נפח 8 ק\"מ — שבוע 10",
        "desc": "טייפר — נפח מופחת",
        "pace_avi": "6:45-7:15", "pace_shachar": "6:10-6:30",
        "structure": "simple", "dist_m": 8000,
    },

    # === Week 11 — Race Week ===
    {
        "week": 11, "slot": "quality",
        "title": "שייקאאוט 4 ק\"מ + 4 מתגברות — שבוע 11",
        "desc": "שבוע מירוץ — 3 ק\"מ ריצה קלה + 4 מתגברות (20 שניות פתיחת צעדים) + 500 מ' שחרור",
        "pace_avi": "7:00-7:30", "pace_shachar": "6:20-6:45",
        "structure": "shakeout_strides", "easy_dist_m": 3200, "repeats": 4, "work_sec": 20, "rest_sec": 45,
    },
    {
        "week": 11, "slot": "easy",
        "title": "שייקאאוט קל 3 ק\"מ — שבוע 11",
        "desc": "שבוע מירוץ — שייקאאוט קצרצר יום לפני המירוץ",
        "pace_avi": "7:15-7:45", "pace_shachar": "6:35-7:00",
        "structure": "simple", "dist_m": 3000,
    },
    {
        "week": 11, "slot": "volume",
        "title": "🏁 מירוץ הלילה 15 ק\"מ!",
        "desc": "מירוץ הלילה 15 ק\"מ — יעד שיא!",
        "pace_avi": "6:05", "pace_shachar": "5:45",
        "structure": "simple", "dist_m": 15000,
    },
]

def build_workout_payload(w_def: dict, person: str) -> dict:
    pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]
    speed_slow, speed_fast = pace_to_speeds(pace_str)
    steps = []
    step_order = 1

    structure = w_def.get("structure", "simple")

    if structure == "simple":
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"{w_def['desc']} | קצב: {pace_str}",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["dist_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        })
    elif structure == "tempo":
        # Warmup
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
            "description": "חימום קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["warmup_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
        step_order += 1
        # Tempo segment
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"ריצת טמפו בקצב יעד {pace_str}",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["tempo_minutes"] * 60),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        })
        step_order += 1
        # Cooldown
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
            "description": "שחרור קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["cooldown_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
    elif structure == "intervals_dist":
        # Warmup
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
            "description": "חימום קל + תרגילים",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["warmup_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
        step_order += 1
        # Repeat group
        work_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 1,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"חזרה מהירה בקצב {pace_str}",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["work_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        }
        rest_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 2,
            "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
            "description": "התאוששות (הליכה / ריצה קלה מאוד)",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["rest_sec"]),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
        }
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
            "numberOfIterations": int(w_def["repeats"]),
            "workoutSteps": [work_step, rest_step]
        })
        step_order += 1
        # Cooldown
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
            "description": "שחרור קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["cooldown_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
    elif structure == "repeats":
        # Fartlek
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
            "description": "חימום קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["warmup_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
        step_order += 1
        work_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 1,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"הגברת קצב ({pace_str})",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["work_sec"]),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        }
        rest_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 2,
            "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
            "description": "ריצה קלה להתאוששות",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["rest_sec"]),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
        }
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
            "numberOfIterations": int(w_def["repeats"]),
            "workoutSteps": [work_step, rest_step]
        })
        step_order += 1
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
            "description": "שחרור קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["cooldown_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })
    elif structure == "shakeout_strides":
        # Shakeout with Strides (Week 11)
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"ריצה קלה ומשוחררת בקצב {pace_str}",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["easy_dist_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        })
        step_order += 1
        # 4 light strides (20s acceleration, 45s walk recovery)
        work_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 1,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": "מתגברת קלה (פתיחת צעדים נינוחה)",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["work_sec"]),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
        }
        rest_step = {
            "type": "ExecutableStepDTO",
            "stepOrder": 2,
            "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
            "description": "הליכה רגועה",
            "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
            "endConditionValue": float(w_def["rest_sec"]),
            "preferredEndConditionUnit": {"unitId": 1, "unitKey": "minute", "factor": 60.0},
        }
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
            "numberOfIterations": int(w_def["repeats"]),
            "workoutSteps": [work_step, rest_step]
        })
        step_order += 1
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": step_order,
            "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
            "description": "שחרור קל",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": 400.0,
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        })

    return {
        "workoutName": w_def["title"],
        "description": f"{w_def['desc']} | יעד: {pace_str}",
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
                "workoutSteps": steps
            }
        ]
    }

def update_garmin_account(person: str):
    name_display = "אבי (Avikuzi)" if person == "avi" else "שחר (Shahar Tal)"
    print("\n" + "=" * 60)
    print(f"🚀 מעדכן את אימוני Garmin עבור {name_display}...")
    print("=" * 60)

    client = connect_garmin(person)
    if not client:
        print(f"❌ שגיאה בהתחברות עבור {person}")
        return

    # Fetch existing workouts
    existing = client.get_workouts(limit=100)
    existing_map = {w.get("workoutName"): w.get("workoutId") for w in existing if isinstance(w, dict) and w.get("workoutName")}

    # Delete outdated Week 11 workout if present
    old_week11_names = ["שמירה על חדות 5 ק\"מ — שבוע 11", "טמפו 5 ק\"מ (5 ק\"מ) — שבוע 11", "איכות - טמפו 5 ק\"מ — שבוע 11"]
    for old_name in old_week11_names:
        if old_name in existing_map:
            old_id = existing_map[old_name]
            print(f"   🗑️ מוחק אימון ישן: {old_name} (ID: {old_id})...", end="")
            try:
                client.delete_workout(old_id)
                print(" ✅ נמחק!")
                time.sleep(0.5)
            except Exception as e:
                print(f" ⚠️ {e}")

    # Re-fetch after deletions
    existing = client.get_workouts(limit=100)
    existing_map = {w.get("workoutName"): w.get("workoutId") for w in existing if isinstance(w, dict) and w.get("workoutName")}

    success = 0
    for w_def in WORKOUT_DEFS:
        title = w_def["title"]
        pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]

        # If already exists, delete it first to upload the new calibrated version
        if title in existing_map:
            w_id = existing_map[title]
            print(f"   🔄 מעדכן אימון קיים: {title}...", end="", flush=True)
            try:
                client.delete_workout(w_id)
                time.sleep(0.5)
            except Exception as e:
                pass

        payload = build_workout_payload(w_def, person)
        print(f"   📤 מעלה {title} (קצב: {pace_str})...", end="", flush=True)
        try:
            res = client.upload_workout(payload)
            new_id = res.get("workoutId") if isinstance(res, dict) else None
            print(f" ✅ הושלם! (ID: {new_id})")
            success += 1
            time.sleep(1.0)
        except Exception as e:
            print(f" ❌ שגיאה: {e}")

    print(f"\n✨ סה\"כ עודכנו בהצלחה {success}/{len(WORKOUT_DEFS)} אימונים עבור {name_display}!")

def main():
    print("============================================================")
    print("🏃 עדכון מלא של אימוני Garmin Connect (שבועות 4–11)")
    print("============================================================")
    update_garmin_account("avi")
    update_garmin_account("shachar")

if __name__ == "__main__":
    main()
