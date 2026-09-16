"""
Upload Fartlek Workout (Week 2 - Quality) to Shachar's Garmin Connect Account
with Shachar's customized target pace (5:25 - 5:40 min/km)
and schedule it on Garmin Connect calendar for today.
"""

import sys
import json
from datetime import datetime
from sync_garmin import connect_garmin

def main():
    print("=" * 55)
    print("⚡ העלאת אימון פרטלק (שבוע 2) לחשבון Garmin של שחר")
    print("=" * 55)

    client = connect_garmin("shachar")
    if not client:
        print("❌ לא הצלחנו להתחבר לחשבון של שחר")
        return

    # Shachar's Pace calculations (meters per second)
    # 5:25 min/km = 325 sec/km -> 1000 / 325 = 3.076923 m/s (Fast pace)
    # 5:40 min/km = 340 sec/km -> 1000 / 340 = 2.941176 m/s (Slow pace threshold)
    # Target zone: 5:25-5:40 min/km

    workout_data = {
        "workoutName": "אימון פרטלק 7 ק\"מ — שבוע 2",
        "description": "חימום 2 ק\"מ + 8 חזרות פרטלק (2 דק' קצב מהיר @ 5:25-5:40 + 1 דק' קלה) + שחרור 1 ק\"מ",
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
                    # 2. Repeat Group: 8 iterations of (2 min fast @ 5:25-5:40 + 1 min easy)
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
                            # 2a. Fast Interval (2 min @ 5:25 - 5:40 min/km)
                            {
                                "type": "ExecutableStepDTO",
                                "stepOrder": 3,
                                "stepType": {
                                    "stepTypeId": 3,
                                    "stepTypeKey": "interval",
                                    "displayOrder": 3
                                },
                                "description": "פרטלק — קצב מהיר (5:25-5:40)",
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
                                "targetValueOne": 2.941176,  # 5:40 min/km (min speed)
                                "targetValueTwo": 3.076923,  # 5:25 min/km (max speed)
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

        print("\n✨ בוצע! האימון זמין כעת באפליקציית Garmin Connect ובשעון של שחר (תחת Workouts / אימונים).")
    except Exception as e:
        print(f"❌ שגיאה בהעלאת האימון: {e}")

if __name__ == "__main__":
    main()
