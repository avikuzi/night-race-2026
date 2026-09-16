"""
Upload all 10 Quality Workouts (Weeks 2-11) to both Avi and Shachar's Garmin Connect accounts
with exact customized pace targets and structured intervals/tempo/fartlek steps.
"""

import sys
import json
import time
from sync_garmin import connect_garmin

def pace_to_speeds(pace_str: str) -> tuple[float, float]:
    """Convert pace string 'M:SS-M:SS' to (min_speed_mps, max_speed_mps).
    Note: Lower speed = slower pace (min), Higher speed = faster pace (max).
    """
    parts = pace_str.split("-")
    def p2s(p):
        m, s = p.strip().split(":")
        sec = int(m) * 60 + int(s)
        return 1000.0 / sec

    speed_slow = p2s(parts[1]) if len(parts) > 1 else p2s(parts[0]) * 0.95
    speed_fast = p2s(parts[0])
    return round(speed_slow, 6), round(speed_fast, 6)

QUALITY_WORKOUTS_DEF = [
    {
        "week": 2,
        "type": "פרטלק",
        "title": "אימון פרטלק 7 ק\"מ — שבוע 2",
        "desc": "חימום 2 ק\"מ + 8 חזרות פרטלק (2 דק' מהיר + 1 דק' קלה) + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "fartlek",
        "iterations": 8,
        "fast_sec": 120.0,
        "rec_sec": 60.0,
        "pace_avi": "5:45-6:00",
        "pace_shachar": "5:25-5:40",
    },
    {
        "week": 3,
        "type": "אינטרוולים",
        "title": "אינטרוולים 6x800מ (7.5 ק\"מ) — שבוע 3",
        "desc": "חימום 2 ק\"מ + 6 חזרות של 800מ אינטרוול (התאוששות 90 שנ') + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "intervals_dist",
        "iterations": 6,
        "fast_m": 800.0,
        "rec_sec": 90.0,
        "pace_avi": "5:30-5:50",
        "pace_shachar": "5:15-5:30",
    },
    {
        "week": 4,
        "type": "טמפו",
        "title": "ריצת טמפו 8 ק\"מ — שבוע 4",
        "desc": "חימום 2 ק\"מ + 5 ק\"מ טמפו רצוף בקצב יעד + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "tempo",
        "tempo_m": 5000.0,
        "pace_avi": "5:40-5:55",
        "pace_shachar": "5:20-5:35",
    },
    {
        "week": 5,
        "type": "פרטלק",
        "title": "אימון פרטלק 8 ק\"מ — שבוע 5",
        "desc": "חימום 2 ק\"מ + 10 חזרות פרטלק (2 דק' מהיר + 1 דק' קלה) + שחרור 1.5 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1500.0,
        "kind": "fartlek",
        "iterations": 10,
        "fast_sec": 120.0,
        "rec_sec": 60.0,
        "pace_avi": "5:35-5:50",
        "pace_shachar": "5:15-5:30",
    },
    {
        "week": 6,
        "type": "טמפו",
        "title": "ריצת טמפו 7 ק\"מ — שבוע 6",
        "desc": "שבוע שחרור חלקי: חימום 2 ק\"מ + 4 ק\"מ טמפו רצוף + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "tempo",
        "tempo_m": 4000.0,
        "pace_avi": "5:40-5:50",
        "pace_shachar": "5:20-5:35",
    },
    {
        "week": 7,
        "type": "אינטרוולים",
        "title": "אינטרוולים 5x1000מ (9 ק\"מ) — שבוע 7",
        "desc": "אימון שיא: חימום 2 ק\"מ + 5 חזרות של 1000מ (התאוששות 2 דק') + שחרור 2 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 2000.0,
        "kind": "intervals_dist",
        "iterations": 5,
        "fast_m": 1000.0,
        "rec_sec": 120.0,
        "pace_avi": "5:25-5:40",
        "pace_shachar": "5:05-5:20",
    },
    {
        "week": 8,
        "type": "טמפו",
        "title": "ריצת טמפו 9 ק\"מ — שבוע 8",
        "desc": "חימום 2 ק\"מ + 6 ק\"מ טמפו רצוף (35 דק') + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "tempo",
        "tempo_m": 6000.0,
        "pace_avi": "5:30-5:45",
        "pace_shachar": "5:10-5:25",
    },
    {
        "week": 9,
        "type": "פרטלק",
        "title": "אימון פרטלק 8 ק\"מ — שבוע 9",
        "desc": "חימום 2 ק\"מ + 10 חזרות פרטלק חופשי (2 דק' מהיר + 1 דק' קלה) + שחרור 1.5 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1500.0,
        "kind": "fartlek",
        "iterations": 10,
        "fast_sec": 120.0,
        "rec_sec": 60.0,
        "pace_avi": "5:25-5:40",
        "pace_shachar": "5:10-5:25",
    },
    {
        "week": 10,
        "type": "אינטרוולים",
        "title": "אינטרוולים 4x1000מ חדות (7 ק\"מ) — שבוע 10",
        "desc": "טייפר וחדות: חימום 2 ק\"מ + 4 חזרות 1000מ (התאוששות 2 דק') + שחרור 1 ק\"מ",
        "warmup_m": 2000.0,
        "cooldown_m": 1000.0,
        "kind": "intervals_dist",
        "iterations": 4,
        "fast_m": 1000.0,
        "rec_sec": 120.0,
        "pace_avi": "5:20-5:35",
        "pace_shachar": "5:00-5:15",
    },
    {
        "week": 11,
        "type": "טמפו",
        "title": "שמירה על חדות 5 ק\"מ — שבוע 11",
        "desc": "שבוע המירוץ: חימום 1.5 ק\"מ + 2.5 ק\"מ טמפו קל / חדות + שחרור 1 ק\"מ",
        "warmup_m": 1500.0,
        "cooldown_m": 1000.0,
        "kind": "tempo",
        "tempo_m": 2500.0,
        "pace_avi": "5:30-5:40",
        "pace_shachar": "5:10-5:25",
    },
]

def build_workout_payload(w_def: dict, person: str) -> dict:
    pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]
    speed_slow, speed_fast = pace_to_speeds(pace_str)

    steps = []
    order = 1

    # 1. Warmup
    steps.append({
        "type": "ExecutableStepDTO",
        "stepOrder": order,
        "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
        "description": "חימום — ריצה קלה בקצב נמוך",
        "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
        "endConditionValue": float(w_def["warmup_m"]),
        "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
    })
    order += 1

    # 2. Main part
    kind = w_def["kind"]
    if kind == "fartlek":
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": order,
            "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
            "numberOfIterations": w_def["iterations"],
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": order + 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
                    "description": f"פרטלק מהיר ({pace_str})",
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
                    "endConditionValue": float(w_def["fast_sec"]),
                    "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
                    "targetValueOne": speed_slow,
                    "targetValueTwo": speed_fast,
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": order + 2,
                    "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
                    "description": "התאוששות קלה",
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
                    "endConditionValue": float(w_def["rec_sec"]),
                    "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
                }
            ],
            "skipLastRestStep": False,
            "smartRepeat": False
        })
        order += 3

    elif kind == "intervals_dist":
        steps.append({
            "type": "RepeatGroupDTO",
            "stepOrder": order,
            "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
            "numberOfIterations": w_def["iterations"],
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": order + 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
                    "description": f"אינטרוול {int(w_def['fast_m'])}מ ({pace_str})",
                    "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
                    "endConditionValue": float(w_def["fast_m"]),
                    "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
                    "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
                    "targetValueOne": speed_slow,
                    "targetValueTwo": speed_fast,
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": order + 2,
                    "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
                    "description": "התאוששות — ריצה קלה/הליכה",
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
                    "endConditionValue": float(w_def["rec_sec"]),
                    "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
                }
            ],
            "skipLastRestStep": False,
            "smartRepeat": False
        })
        order += 3

    elif kind == "tempo":
        steps.append({
            "type": "ExecutableStepDTO",
            "stepOrder": order,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
            "description": f"ריצת טמפו ({pace_str})",
            "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
            "endConditionValue": float(w_def["tempo_m"]),
            "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
            "targetType": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
            "targetValueOne": speed_slow,
            "targetValueTwo": speed_fast,
        })
        order += 1

    # 3. Cooldown
    steps.append({
        "type": "ExecutableStepDTO",
        "stepOrder": order,
        "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
        "description": "שחרור — Cool down",
        "endCondition": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
        "endConditionValue": float(w_def["cooldown_m"]),
        "preferredEndConditionUnit": {"unitId": 2, "unitKey": "kilometer", "factor": 100000.0},
        "targetType": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
    })

    return {
        "workoutName": w_def["title"],
        "description": f"{w_def['desc']} | קצב יעד: {pace_str}",
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
    print(f"🚀 מעלה את כל 10 אימוני האיכות עבור {name_display}...")
    print("=" * 60)

    client = connect_garmin(person)
    if not client:
        print(f"❌ שגיאה בהתחברות עבור {person}")
        return

    success_count = 0
    # Fetch existing to avoid duplicates if title matches
    existing_workouts = client.get_workouts(limit=100)
    existing_names = {w.get("workoutName") for w in existing_workouts if isinstance(w, dict)}

    for w_def in QUALITY_WORKOUTS_DEF:
        title = w_def["title"]
        if title in existing_names:
            print(f"   ⏩ אימון שבוע {w_def['week']} ({w_def['type']}) כבר קיים בחשבון, מדלג...")
            success_count += 1
            continue

        payload = build_workout_payload(w_def, person)
        pace_str = w_def["pace_avi"] if person == "avi" else w_def["pace_shachar"]
        print(f"   📤 מעלה שבוע {w_def['week']}: {title} (קצב: {pace_str})...", end="", flush=True)

        try:
            res = client.upload_workout(payload)
            w_id = res.get("workoutId") if isinstance(res, dict) else None
            print(f" ✅ הושלם! (ID: {w_id})")
            success_count += 1
            time.sleep(1.0)  # Gentle rate limiting
        except Exception as e:
            print(f" ❌ שגיאה: {e}")

    print(f"\n✨ סה\"כ הועלו בהצלחה: {success_count}/{len(QUALITY_WORKOUTS_DEF)} אימונים עבור {person}!")

def main():
    print("============================================================")
    print("⚡ העלאת כל אימוני האיכות (שבועות 2 עד 11) ל-Garmin Connect")
    print("============================================================")

    upload_all_for_person("avi")
    upload_all_for_person("shachar")

    print("\n" + "=" * 60)
    print("🎉 כל אימוני האיכות סונכרנו בהצלחה לשני החשבונות!")
    print("=" * 60)

if __name__ == "__main__":
    main()
