"""
Upload Fartlek Workout (Week 2 - Quality) to Avi's Garmin Connect Account
and schedule it on Garmin Connect calendar for today.
"""

import sys
import json
from datetime import datetime
from sync_garmin import connect_garmin

def main():
    print("=" * 55)
    print("⚡ העלאת אימון פרטלק (שבוע 2) לחשבון Garmin של אבי")
    print("=" * 55)

    client = connect_garmin("avi")
    if not client:
        print("❌ לא הצלחנו להתחבר לחשבון של אבי")
        return

    # Pace calculations (meters per second)
    # 5:45 min/km = 345 sec/km -> 1000 / 345 = 2.89855 m/s (Fast pace)
    # 6:00 min/km = 360 sec/km -> 1000 / 360 = 2.77778 m/s (Slow pace threshold)
    # Target zone: 5:45-6:00 min/km

    workout_data = {
        "workoutName": "אימון פרטלק 7 ק\"מ — שבוע 2",
        "description": "חימום 2 ק\"מ + 8 חזרות פרטלק (2 דק' קצב מהיר @ 5:45-6:00 + 1 דק' קלה) + שחרור 1 ק\"מ",
        "sportType": {
            "sportTypeId": 1,
            "sportTypeKey": "running",
            "displayOrder": 1
        },
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {
                    "sportTypeId": 1,
                    "sportTypeKey": "running",
                    "displayOrder": 1
                },
                "workoutSteps": [
                    # 1. Warmup: 2.0 km
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {
                            "stepTypeId": 1,
                            "stepTypeKey": "warmup",
                            "displayOrder": 1
                        },
                        "description": "חימום — ריצה קלה בקצב נמוך",
                        "endCondition": {
                            "conditionTypeId": 3,
                            "conditionTypeKey": "distance",
                            "displayOrder": 3,
                            "displayable": True
                        },
                        "endConditionValue": 2000.0,
                        "preferredEndConditionUnit": {
                            "unitId": 2,
                            "unitKey": "kilometer",
                            "factor": 100000.0
                        },
                        "targetType": {
                            "workoutTargetTypeId": 1,
                            "workoutTargetTypeKey": "no.target",
                            "displayOrder": 1
                        }
                    },
                    # 2. Repeat Group: 8 iterations of (2 min fast @ 5:45-6:00 + 1 min easy)
                    {
                        "type": "RepeatGroupDTO",
                        "stepOrder": 2,
                        "stepType": {
                            "stepTypeId": 6,
                            "stepTypeKey": "repeat",
                            "displayOrder": 6
                        },
                        "numberOfIterations": 8,
                        "workoutSteps": [
                            # 2a. Fast Interval (2 min @ 5:45 - 6:00 min/km)
                            {
                                "type": "ExecutableStepDTO",
                                "stepOrder": 3,
                                "stepType": {
                                    "stepTypeId": 3,
                                    "stepTypeKey": "interval",
                                    "displayOrder": 3
                                },
                                "description": "פרטלק — קצב מהיר (5:45-6:00)",
                                "endCondition": {
                                    "conditionTypeId": 2,
                                    "conditionTypeKey": "time",
                                    "displayOrder": 2,
                                    "displayable": True
                                },
                                "endConditionValue": 120.0,
                                "targetType": {
                                    "workoutTargetTypeId": 6,
                                    "workoutTargetTypeKey": "pace.zone",
                                    "displayOrder": 6
                                },
                                "targetValueOne": 2.777778,  # 6:00 min/km (min speed)
                                "targetValueTwo": 2.898551,  # 5:45 min/km (max speed)
                            },
                            # 2b. Recovery (1 min easy)
                            {
                                "type": "ExecutableStepDTO",
                                "stepOrder": 4,
                                "stepType": {
                                    "stepTypeId": 4,
                                    "stepTypeKey": "recovery",
                                    "displayOrder": 4
                                },
                                "description": "התאוששות — ריצה קלה",
                                "endCondition": {
                                    "conditionTypeId": 2,
                                    "conditionTypeKey": "time",
                                    "displayOrder": 2,
                                    "displayable": True
                                },
                                "endConditionValue": 60.0,
                                "targetType": {
                                    "workoutTargetTypeId": 1,
                                    "workoutTargetTypeKey": "no.target",
                                    "displayOrder": 1
                                }
                            }
                        ],
                        "skipLastRestStep": False,
                        "smartRepeat": False
                    },
                    # 3. Cooldown: 1.0 km
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 5,
                        "stepType": {
                            "stepTypeId": 2,
                            "stepTypeKey": "cooldown",
                            "displayOrder": 2
                        },
                        "description": "שחרור — Cool down",
                        "endCondition": {
                            "conditionTypeId": 3,
                            "conditionTypeKey": "distance",
                            "displayOrder": 3,
                            "displayable": True
                        },
                        "endConditionValue": 1000.0,
                        "preferredEndConditionUnit": {
                            "unitId": 2,
                            "unitKey": "kilometer",
                            "factor": 100000.0
                        },
                        "targetType": {
                            "workoutTargetTypeId": 1,
                            "workoutTargetTypeKey": "no.target",
                            "displayOrder": 1
                        }
                    }
                ]
            }
        ]
    }

    print("\n📤 מעלה את האימון ל-Garmin Connect...")
    try:
        res = client.upload_workout(workout_data)
        workout_id = res.get("workoutId") if isinstance(res, dict) else None
        print(f"✅ האימון נוצר בהצלחה! (מזהה אימון: {workout_id})")
        print(f"   שם האימון: {workout_data['workoutName']}")

        # Schedule to today in Garmin calendar
        if workout_id:
            today_str = datetime.now().strftime("%Y-%m-%d")
            print(f"\n📅 מתזמן את האימון ליומן Garmin לתאריך היום ({today_str})...")
            try:
                client.schedule_workout(workout_id, today_str)
                print(f"✅ האימון שובץ ביומן של היום בהצלחה!")
            except Exception as se:
                print(f"ℹ️  הערה לגבי שיבוץ ביומן: {se}")

        print("\n✨ בוצע! האימון זמין כעת באפליקציית Garmin Connect ובשעון שלך (תחת Workouts / אימונים).")
    except Exception as e:
        print(f"❌ שגיאה בהעלאת האימון: {e}")

if __name__ == "__main__":
    main()
