# 🌙 מירוץ הלילה 2026 — דשבורד אימונים ומעקב ביצועים (אבי ושחר)

> **Apple Fitness & Apple Watch Edition · 15KM Night Race 2026**  
> 🌐 **Live Website:** [night-race-2026.web.app](https://night-race-2026.web.app)

---

## 🏃‍♂️ אודות הפרויקט
דשבורד מעקב וניתוח אימונים אינטראקטיבי בזמן אמת, המלווה את תוכנית האימונים (11 שבועות) של **אבי** ו**שחר** לקראת מירוץ הלילה 15 ק"מ (28 באוקטובר 2026).

המערכת פועלת באופן אוטונומי: מושכת את נתוני הריצה משעוני ה-Garmin, מסווגת את סוג האימון (טמפו, פרטלק, אינטרוולים, נפח, קלה), מנתחת עמידה ביעדי קצב ומסלול, ומעדכנת את האתר ישירות.

---

## ✨ תכונות ועיצוב (Apple Fitness UI/UX)
* **🖤 True Black Design:** רקע שחור עמוק (`#000000`), כרטיסים מעוגלים (`22px`) ללא מסגרות.
* **⚡ צבעי ניאון אישיים:**
  * 🔵 **אבי:** Electric Neon Cyan (`#00F0FF`).
  * 🟢 **שחר:** Apple Neon Green (`#30D158`).
* **⭕ טבעות פעילות (Apple Activity Rings):** טבעות SVG קונצנטריות חופפות למעקב אחוזי השלמה.
* **〰️ ציר זמן מינימליסטי (Horizontal Roadmap):** קו דק רציף עם נקודות שבועיות כאשר השבוע הנוכחי זוהר בפולס ניאון.
* **📈 גרפים חלקים (Spline & Rounded Bars):** עקומות קצב ללא קווי רשת ועמודות נפח מעוגלות קצוות.
* **📱 iOS Segmented Control:** בקר גלולה לסינון בין "שניהם", "אבי" ו"שחר".

---

## 🛠️ ארכיטקטורה וטכנולוגיות
* **Frontend:** Vanilla HTML5, CSS3 (Apple Fitness Design System), JavaScript (ES6+), Chart.js.
* **Hosting & CDN:** Google Firebase Hosting.
* **Automation & Backend:** Python 3.12, `garminconnect` API.
* **Scheduler:** Windows Task Scheduler / Background Daemon מסנכרן כל שעתיים.

---

## 🚀 הרצה וסנכרון מקומי
```bash
# סנכרון ריצות מ-Garmin Connect ופריסה ל-Firebase
python -X utf8 sync_garmin.py --deploy

# עדכון כל אימוני ה-Workouts ישירות לתוך שעוני ה-Garmin
python -X utf8 update_all_garmin_workouts.py
```

---
*נבנה באהבה לספורט ולטכנולוגיה לקראת מירוץ הלילה 2026! 🌙🏃‍♂️*
