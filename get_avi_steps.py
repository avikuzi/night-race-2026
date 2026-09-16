import datetime
from sync_garmin import connect_garmin

client = connect_garmin('avi')
today = datetime.date.today()

days_heb = {
    'Sunday': 'ראשון',
    'Monday': 'שני',
    'Tuesday': 'שלישי',
    'Wednesday': 'רביעי',
    'Thursday': 'חמישי',
    'Friday': 'שישי',
    'Saturday': 'שבת'
}

print(f"=== נתוני צעדים שבועיים עבור אבי (עד {today}) ===")

total_steps = 0
results = []

# Fetch last 7 days starting from Sunday of this week (30/08/2026) to today (04/09/2026)
for d in range(7):
    day = today - datetime.timedelta(days=d)
    day_str = day.isoformat()
    try:
        stats = client.get_user_summary(day_str)
        steps = stats.get('totalSteps', 0) or 0
        goal = stats.get('dailyStepGoal', 0) or 0
        dist = (stats.get('totalDistanceMeters', 0) or 0) / 1000.0
        floors = stats.get('floorsClimbed', 0) or 0
        calories = stats.get('activeKilocalories', 0) or 0
        day_name = days_heb.get(day.strftime('%A'), day.strftime('%A'))
        
        results.append({
            'date': day_str,
            'day_name': day_name,
            'steps': steps,
            'goal': goal,
            'dist': dist,
            'floors': floors,
            'calories': calories
        })
        total_steps += steps
    except Exception as e:
        print(f"שגיאה במשיכת יום {day_str}: {e}")

# Print in chronological order
results.reverse()
for r in results:
    pct = round((r['steps'] / r['goal'] * 100)) if r['goal'] else 0
    star = "🌟" if r['steps'] >= r['goal'] and r['goal'] > 0 else "🚶"
    print(f"{r['date']} (יום {r['day_name']}): {r['steps']:,} צעדים ({star} {pct}% מהיעד) | {r['dist']:.2f} ק\"מ | {r['calories']} קלוריות פעילות")

avg_steps = round(total_steps / len(results)) if results else 0
print(f"\n📊 סיכום שבועי:")
print(f"• סה\"כ צעדים: {total_steps:,}")
print(f"• ממוצע יומי: {avg_steps:,} צעדים ליום")
