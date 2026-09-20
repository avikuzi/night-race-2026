// ============================================================
// מירוץ הלילה של שחר ואבי 2026 — Training Data
// Race: 15km Night Race — October 28, 2026
// Plan Start: August 13, 2026 (V5 — flexible weekly)
// ============================================================

const RACE_DATE = new Date(2026, 9, 28); // Oct 28, 2026
const PLAN_START = new Date(2026, 7, 13); // Aug 13, 2026
const TODAY = new Date();
const LAST_SYNC = '20/09/2026, 11:19';

// Workout type classification
const WorkoutType = {
  EASY: 'ריצה קלה',
  VOLUME: 'נפח',
  QUALITY_FARTLEK: 'איכות - פרטלק',
  QUALITY_TEMPO: 'איכות - טמפו',
  QUALITY_INTERVALS: 'איכות - אינטרוולים',
  RACE: 'מירוץ',
};

// Workout slot within a week
const Slot = {
  QUALITY: 'quality',   // quality run — any weekday
  VOLUME: 'volume',     // volume run — Friday or Saturday
  EASY: 'easy',         // easy run — any weekday
};

const DAY_HINT_LABELS = {
  quality: 'אמצע שבוע',
  volume: 'שישי/שבת',
  easy: 'אמצע שבוע',
};

// Training phases
const Phase = {
  BASE: { id: 'base', label: 'בסיס', labelEn: 'Base', weeks: [1, 2] },
  BUILD: { id: 'build', label: 'בנייה', labelEn: 'Build', weeks: [3, 4, 5, 6] },
  PEAK: { id: 'peak', label: 'שיא', labelEn: 'Peak', weeks: [7, 8, 9] },
  TAPER: { id: 'taper', label: 'הפחתה', labelEn: 'Taper', weeks: [10, 11] },
};

function getPhaseForWeek(week) {
  for (const phase of Object.values(Phase)) {
    if (phase.weeks.includes(week)) return phase;
  }
  return Phase.BASE;
}

// ============================================================
// Workout Detail Descriptions
// ============================================================
const workoutDetails = {
  'נפח': {
    title: 'ריצת נפח',
    icon: '🏃',
    description: 'ריצה ארוכה בקצב נוח — בניית בסיס אירובי ועמידות.',
    structure: [
      { segment: 'חימום', duration: '10 דק\'', detail: 'הליכה מהירה + ריצה קלה מאוד' },
      { segment: 'גוף האימון', duration: 'עיקר המרחק', detail: 'ריצה רציפה בקצב נוח ומבוקר' },
      { segment: 'שחרור', duration: '5 דק\'', detail: 'ריצה איטית + הליכה + מתיחות' },
    ],
    tips: 'אל תנסו להרשים — הקצב צריך לאפשר שיחה. זה אימון של סבלנות.',
  },
  'איכות - פרטלק': {
    title: 'אימון פרטלק',
    icon: '⚡',
    description: 'ריצה עם שינויי קצב חופשיים — בונה מהירות ויכולת אירובית.',
    structure: [
      { segment: 'חימום', duration: '2 ק"מ', detail: 'ריצה קלה בקצב נמוך' },
      { segment: 'פרטלק', duration: 'עיקר המרחק', detail: 'החלפות בין קצב מהיר (1-3 דק\') לריצה קלה (1-2 דק\')' },
      { segment: 'שחרור', duration: '1 ק"מ', detail: 'Cool down — ריצה קלה' },
    ],
    tips: 'הפרטלק הוא "משחק מהירויות" — תנו לגוף להנחות אתכם. אין צורך בדיוק של שניות.',
  },
  'איכות - טמפו': {
    title: 'ריצת טמפו',
    icon: '🔥',
    description: 'ריצה בקצב סף אנאירובי ("קצב נוח-קשה") — בונה עמידות במהירות.',
    structure: [
      { segment: 'חימום', duration: '2 ק"מ', detail: 'ריצה קלה' },
      { segment: 'טמפו', duration: 'עיקר המרחק', detail: 'ריצה רציפה בקצב טמפו — "נוח-קשה", אפשר לדבר במשפטים קצרים' },
      { segment: 'שחרור', duration: '1 ק"מ', detail: 'Cool down' },
    ],
    tips: 'הטמפו צריך להרגיש "מאתגר אבל בר-קיימא". אם אתם מתנשפים — איטיים מדי.',
  },
  'איכות - אינטרוולים': {
    title: 'אימון אינטרוולים',
    icon: '💥',
    description: 'חזרות מהירות עם מנוחה — בונה VO2max ומהירות מירוצית.',
    structure: [
      { segment: 'חימום', duration: '2 ק"מ', detail: 'ריצה קלה + תרגילי ריצה' },
      { segment: 'אינטרוולים', duration: 'לפי התוכנית', detail: 'חזרות מהירות (800-1000מ\') עם מנוחה (ריצה קלה/הליכה)' },
      { segment: 'שחרור', duration: '1.5 ק"מ', detail: 'Cool down + מתיחות' },
    ],
    tips: 'מנוחה פעילה (ריצה קלה) עדיפה על עצירה מלאה. שמרו על טכניקת ריצה גם בעייפות.',
  },
  'ריצה קלה': {
    title: 'ריצה קלה / שיקום',
    icon: '🌿',
    description: 'ריצת שיקום בקצב איטי — מטרתה שיקום פעיל בין אימוני איכות.',
    structure: [
      { segment: 'ריצה קלה', duration: 'כל המרחק', detail: 'קצב נמוך ונוח. לשמור על דופק נמוך ולהרגיש קל.' },
    ],
    tips: 'זה יום שיקום! אין בושה ללכת קטעים. הקצב חייב להיות קל באמת.',
  },
  'מירוץ': {
    title: '🏁 מירוץ הלילה 15 ק"מ!',
    icon: '🏆',
    description: 'היום הגדול! 15 ק"מ מירוץ הלילה. כל הבלוק הוביל לכאן.',
    structure: [
      { segment: 'לפני המירוץ', duration: '30 דק\'', detail: 'הגעה מוקדמת, חימום קל 10 דק\' ריצה + תרגילי ריצה' },
      { segment: 'ק"מ 1-3', duration: 'סבלני', detail: 'התחילו קצת מתחת לקצב היעד — אל תצאו מהר מדי!' },
      { segment: 'ק"מ 4-12', duration: 'קצב מירוץ', detail: 'שמרו על קצב יעד עקבי. תהנו מהאווירה.' },
      { segment: 'ק"מ 13-15', duration: 'לדחוף!', detail: 'הגיע הזמן לתת את מה שנשאר! Negative split 💪' },
    ],
    tips: 'תאכלו 3 שעות לפני. קחו ג\'ל בק"מ 8. אל תנסו נעליים חדשות ביום המירוץ!',
  },
};

// ============================================================
// Full Training Plan (11 weeks × 3 sessions/week)
// V5 — Flexible weekly structure (no fixed dates)
// Order within week: Quality → Volume → Easy
// ============================================================
const trainingPlan = [
  // === Week 1 — Base (13/8 — 16/8) ===
  { week: 1, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 7.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '5:55-6:15',
    actualDistanceAvi: 7.02, actualPaceAvi: '6:41', actualDateAvi: '2026-08-15',
    actualDistanceShachar: 7.01, actualPaceShachar: '6:05', actualDateShachar: '2026-08-14',
    notes: 'פתיחת בלוק!' },

  // === Week 2 — Base ===
  { week: 2, slot: 'quality', type: WorkoutType.QUALITY_FARTLEK, distancePlanned: 7.0,
    targetPaceAvi: '5:45-6:00', targetPaceShachar: '5:25-5:40',
    actualDistanceAvi: 7.02, actualPaceAvi: '6:35', actualDateAvi: '2026-08-18',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור עקב מחלה 🤒' },
  { week: 2, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 5.5,
    targetPaceAvi: '6:50-7:15', targetPaceShachar: '6:10-6:30',
    actualDistanceAvi: 5.02, actualPaceAvi: '6:57', actualDateAvi: '2026-08-21',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור עקב מחלה 🤒' },
  { week: 2, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 8.0,
    targetPaceAvi: '6:40-7:10', targetPaceShachar: '5:50-6:10',
    actualDistanceAvi: 8.02, actualPaceAvi: '7:22', actualDateAvi: '2026-08-22',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור עקב מחלה 🤒' },

  // === Week 3 — Build ===
  { week: 3, slot: 'quality', type: WorkoutType.QUALITY_INTERVALS, distancePlanned: 7.5,
    targetPaceAvi: '5:30-5:50', targetPaceShachar: '5:15-5:30',
    actualDistanceAvi: 7.21, actualPaceAvi: '6:24', actualDateAvi: '2026-08-26',
    actualDistanceShachar: 4.64, actualPaceShachar: '6:48', actualDateShachar: '2026-08-26',
    notes: '6×800מ' },
  { week: 3, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 5.5,
    targetPaceAvi: '6:50-7:15', targetPaceShachar: '6:05-6:25',
    actualDistanceAvi: 5.51, actualPaceAvi: '7:32', actualDateAvi: '2026-08-28',
    actualDistanceShachar: 5.51, actualPaceShachar: '6:16', actualDateShachar: '2026-08-24',
    notes: 'שחר: חזרה מתונה ממחלה' },
  { week: 3, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 9.0,
    targetPaceAvi: '6:35-7:05', targetPaceShachar: '5:45-6:05',
    actualDistanceAvi: 9.02, actualPaceAvi: '6:53', actualDateAvi: '2026-08-29',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור נפח — התאוששות ממחלה 🤒' },

  // === Week 4 — Build ===
  { week: 4, slot: 'quality', type: WorkoutType.QUALITY_TEMPO, distancePlanned: 8.0,
    targetPaceAvi: '5:40-5:55', targetPaceShachar: '5:25-5:40',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    statusAvi: 'exempt',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'אבי: עקירה כירורגית 🦷 | שחר: מחלה 🤒' },
  { week: 4, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 5.5,
    targetPaceAvi: '7:00-7:30', targetPaceShachar: '6:20-6:45',
    actualDistanceAvi: 5.02, actualPaceAvi: '6:55', actualDateAvi: '2026-09-03',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור עקב מחלה 🤒' },
  { week: 4, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 10.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '6:05-6:30',
    actualDistanceAvi: 10.02, actualPaceAvi: '6:46', actualDateAvi: '2026-09-05',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור עקב מחלה 🤒' },

  // === Week 5 — Build ===
  { week: 5, slot: 'quality', type: WorkoutType.QUALITY_FARTLEK, distancePlanned: 8.0,
    targetPaceAvi: '5:35-5:50', targetPaceShachar: '5:20-5:35',
    actualDistanceAvi: 6.26, actualPaceAvi: '7:23', actualDateAvi: '2026-09-10',
    actualDistanceShachar: 6.24, actualPaceShachar: '6:43', actualDateShachar: '2026-09-08',
    notes: 'שחר: חזרה לאיכות (פרטלק) 💪' },
  { week: 5, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 6.0,
    targetPaceAvi: '7:00-7:30', targetPaceShachar: '6:20-6:45',
    actualDistanceAvi: 5.01, actualPaceAvi: '7:09', actualDateAvi: '2026-09-08',
    actualDistanceShachar: 6.01, actualPaceShachar: '6:43', actualDateShachar: '2026-09-13',
    notes: 'שחר: ריצת חג ראש השנה (נרשם על שבוע 5 🍎)' },
  { week: 5, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 11.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '6:05-6:30',
    actualDistanceAvi: 11.02, actualPaceAvi: '6:38', actualDateAvi: '2026-09-12',
    statusShachar: 'illness',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שחר: ויתור נפח — חזרה מתונה ממחלה' },

  // === Week 6 — Build / Recovery ===
  { week: 6, slot: 'quality', type: WorkoutType.QUALITY_TEMPO, distancePlanned: 7.0,
    targetPaceAvi: '5:40-5:50', targetPaceShachar: '5:25-5:35',
    actualDistanceAvi: 7.02, actualPaceAvi: '6:20', actualDateAvi: '2026-09-17',
    actualDistanceShachar: 5.72, actualPaceShachar: '5:48', actualDateShachar: '2026-09-15',
    notes: 'שבוע שחרור חלקי' },
  { week: 6, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 5.0,
    targetPaceAvi: '7:05-7:35', targetPaceShachar: '6:25-6:50',
    actualDistanceAvi: 5.02, actualPaceAvi: '7:22', actualDateAvi: '2026-09-15',
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },
  { week: 6, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 9.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '6:10-6:30',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },

  // === Week 7 — Peak ===
  { week: 7, slot: 'quality', type: WorkoutType.QUALITY_INTERVALS, distancePlanned: 9.0,
    targetPaceAvi: '5:30-5:45', targetPaceShachar: '5:15-5:30',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '5×1000מ' },
  { week: 7, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 6.0,
    targetPaceAvi: '7:00-7:30', targetPaceShachar: '6:20-6:45',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },
  { week: 7, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 12.0,
    targetPaceAvi: '6:40-7:10', targetPaceShachar: '6:00-6:25',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'ריצת השיא' },

  // === Week 8 — Peak ===
  { week: 8, slot: 'quality', type: WorkoutType.QUALITY_TEMPO, distancePlanned: 9.0,
    targetPaceAvi: '5:35-5:50', targetPaceShachar: '5:20-5:35',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '35 דק\' טמפו' },
  { week: 8, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 6.0,
    targetPaceAvi: '7:00-7:30', targetPaceShachar: '6:20-6:45',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },
  { week: 8, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 13.0,
    targetPaceAvi: '6:35-7:05', targetPaceShachar: '5:55-6:20',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },

  // === Week 9 — Peak / Recovery ===
  { week: 9, slot: 'quality', type: WorkoutType.QUALITY_FARTLEK, distancePlanned: 8.0,
    targetPaceAvi: '5:35-5:50', targetPaceShachar: '5:20-5:35',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שבוע שחרור חלקי' },
  { week: 9, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 5.0,
    targetPaceAvi: '7:05-7:35', targetPaceShachar: '6:25-6:50',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },
  { week: 9, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 10.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '6:05-6:30',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },

  // === Week 10 — Taper ===
  { week: 10, slot: 'quality', type: WorkoutType.QUALITY_INTERVALS, distancePlanned: 7.0,
    targetPaceAvi: '5:30-5:45', targetPaceShachar: '5:15-5:30',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '4×1000מ חדות' },
  { week: 10, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 4.5,
    targetPaceAvi: '7:05-7:35', targetPaceShachar: '6:25-6:50',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },
  { week: 10, slot: 'volume', type: WorkoutType.VOLUME, distancePlanned: 8.0,
    targetPaceAvi: '6:45-7:15', targetPaceShachar: '6:10-6:30',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '' },

  // === Week 11 — Taper / Race Week ===
  { week: 11, slot: 'quality', type: WorkoutType.EASY, distancePlanned: 4.0,
    targetPaceAvi: '7:00-7:30', targetPaceShachar: '6:20-6:45',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שייקאאוט קל + 4 מתגברות (פתיחת צעדים וחדות)' },
  { week: 11, slot: 'easy', type: WorkoutType.EASY, distancePlanned: 3.0,
    targetPaceAvi: '7:15-7:45', targetPaceShachar: '6:35-7:00',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: 'שייקאאוט קצרצר לפני המירוץ' },
  { week: 11, slot: 'volume', type: WorkoutType.RACE, distancePlanned: 15.0,
    fixedDate: '2026-10-28',
    targetPaceAvi: '6:05', targetPaceShachar: '5:45',
    actualDistanceAvi: null, actualPaceAvi: null, actualDateAvi: null,
    actualDistanceShachar: null, actualPaceShachar: null, actualDateShachar: null,
    notes: '🏁 מירוץ הלילה 15 ק"מ!' },
];

// ============================================================
// Helper Functions
// ============================================================

/** Parse a "M:SS" pace string to total seconds */
function paceToSeconds(paceStr) {
  if (!paceStr) return null;
  if (paceStr.includes('-')) {
    const parts = paceStr.split('-');
    const low = paceToSeconds(parts[0].trim());
    const high = paceToSeconds(parts[1].trim());
    if (low !== null && high !== null) return (low + high) / 2;
    return low || high;
  }
  const match = paceStr.match(/(\d+):(\d+)/);
  if (!match) return null;
  return parseInt(match[1]) * 60 + parseInt(match[2]);
}

function secondsToPace(totalSec) {
  if (totalSec == null) return '—';
  const min = Math.floor(totalSec / 60);
  const sec = Math.round(totalSec % 60);
  return `${min}:${sec.toString().padStart(2, '0')}`;
}

function parseDate(dateStr) {
  if (!dateStr) return null;
  return new Date(dateStr + 'T00:00:00');
}

function formatDateHebrew(dateStr) {
  if (!dateStr) return '—';
  const d = parseDate(dateStr);
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function formatDateFull(dateStr) {
  if (!dateStr) return '—';
  const d = parseDate(dateStr);
  const days = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];
  return `יום ${days[d.getDay()]}, ${d.getDate()}/${d.getMonth() + 1}`;
}

function daysUntilRace() {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const race = new Date(RACE_DATE);
  race.setHours(0, 0, 0, 0);
  return Math.max(0, Math.ceil((race - now) / (1000 * 60 * 60 * 24)));
}

const WEEK_DATE_RANGES = {
  1: '13/8 — 15/8',
  2: '16/8 — 22/8',
  3: '23/8 — 29/8',
  4: '30/8 — 5/9',
  5: '6/9 — 12/9',
  6: '13/9 — 19/9',
  7: '20/9 — 26/9',
  8: '27/9 — 3/10',
  9: '4/10 — 10/10',
  10: '11/10 — 17/10',
  11: '18/10 — 28/10',
};

const WEEK_BOUNDARIES = [
  { week: 1, start: new Date(2026, 7, 13), end: new Date(2026, 7, 15, 23, 59, 59) },
  { week: 2, start: new Date(2026, 7, 16), end: new Date(2026, 7, 22, 23, 59, 59) },
  { week: 3, start: new Date(2026, 7, 23), end: new Date(2026, 7, 29, 23, 59, 59) },
  { week: 4, start: new Date(2026, 7, 30), end: new Date(2026, 8, 5, 23, 59, 59) },
  { week: 5, start: new Date(2026, 8, 6), end: new Date(2026, 8, 12, 23, 59, 59) },
  { week: 6, start: new Date(2026, 8, 13), end: new Date(2026, 8, 19, 23, 59, 59) },
  { week: 7, start: new Date(2026, 8, 20), end: new Date(2026, 8, 26, 23, 59, 59) },
  { week: 8, start: new Date(2026, 8, 27), end: new Date(2026, 9, 3, 23, 59, 59) },
  { week: 9, start: new Date(2026, 9, 4), end: new Date(2026, 9, 10, 23, 59, 59) },
  { week: 10, start: new Date(2026, 9, 11), end: new Date(2026, 9, 17, 23, 59, 59) },
  { week: 11, start: new Date(2026, 9, 18), end: new Date(2026, 9, 28, 23, 59, 59) },
];

function getWeekDateRange(weekNum) {
  return WEEK_DATE_RANGES[weekNum] || '';
}

function getCurrentWeek() {
  const now = new Date();
  for (const wb of WEEK_BOUNDARIES) {
    if (now >= wb.start && now <= wb.end) return wb.week;
  }
  if (now < WEEK_BOUNDARIES[0].start) return 0;
  return 11;
}

/** Check if a training week is in the past */
function isWeekPast(weekNum) {
  const wb = WEEK_BOUNDARIES.find(b => b.week === weekNum);
  if (!wb) return false;
  return new Date() > wb.end;
}

/** Check if a training week is the current week */
function isWeekCurrent(weekNum) {
  return getCurrentWeek() === weekNum;
}

/** For backward compat — checks if a date string is past */
function isPast(dateStr) {
  if (!dateStr) return false;
  const d = parseDate(dateStr);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return d < now;
}

function isToday(dateStr) {
  if (!dateStr) return false;
  const d = parseDate(dateStr);
  const now = new Date();
  return d.getFullYear() === now.getFullYear() &&
         d.getMonth() === now.getMonth() &&
         d.getDate() === now.getDate();
}

function getWorkoutStatus(entry, person) {
  if (person === 'avi' && entry.statusAvi) return entry.statusAvi;
  if (person === 'shachar' && entry.statusShachar) return entry.statusShachar;

  const actualDist = person === 'avi' ? entry.actualDistanceAvi : entry.actualDistanceShachar;
  const actualPace = person === 'avi' ? entry.actualPaceAvi : entry.actualPaceShachar;
  const targetPace = person === 'avi' ? entry.targetPaceAvi : entry.targetPaceShachar;

  // Week-based: if the week hasn't passed yet, it's pending
  if (!isWeekPast(entry.week) && !isWeekCurrent(entry.week)) return 'pending';

  // If no actual data
  if (actualDist === null && actualPace === null) {
    return isWeekPast(entry.week) ? 'skipped' : 'pending';
  }

  const targetParts = targetPace.split('-');
  const targetLow = paceToSeconds(targetParts[0].trim());
  const targetHigh = targetParts.length > 1 ? paceToSeconds(targetParts[1].trim()) : targetLow + 15;
  const actualSec = paceToSeconds(actualPace);

  if (actualSec === null) return 'pending';

  const distOk = actualDist >= entry.distancePlanned * 0.85;
  const isQuality = entry.type.includes('איכות') || entry.slot === 'quality';

  // For quality workouts (Intervals/Fartlek/Tempo), the target pace is for the main exercise
  // while overall activity average includes warmup (2km), cooldown (1km), and recoveries.
  if (isQuality && distOk) {
    // If completed the planned distance, the structured intervals were executed
    return 'on-track';
  }

  // For regular runs (volume, easy, race)
  const isGoodPace = actualSec <= targetHigh + 15;
  const isClosePace = actualSec <= targetHigh + 35;

  if (distOk && isGoodPace) return 'on-track';
  if (distOk && isClosePace) return 'warning';
  return 'off-track';
}

function getWorkoutTypeClass(type) {
  if (type.includes('קלה')) return 'easy';
  if (type.includes('נפח')) return 'volume';
  if (type.includes('איכות')) return 'quality';
  if (type.includes('מירוץ')) return 'race';
  return 'easy';
}

/** Get workout detail for a given type */
function getWorkoutDetail(type) {
  return workoutDetails[type] || null;
}

/** Get the display date for a workout entry */
function getDisplayDate(entry, person) {
  if (person === 'avi' && entry.actualDateAvi) return formatDateFull(entry.actualDateAvi);
  if (person === 'shachar' && entry.actualDateShachar) return formatDateFull(entry.actualDateShachar);
  // If either has a date, show it
  if (entry.actualDateAvi) return formatDateFull(entry.actualDateAvi);
  if (entry.actualDateShachar) return formatDateFull(entry.actualDateShachar);
  // If entry is the race or has a fixed date
  if (entry.fixedDate) return formatDateFull(entry.fixedDate);
  if (entry.type === WorkoutType.RACE || entry.type.includes('מירוץ')) return 'יום ד\', 28/10';
  // Otherwise show the slot hint
  return DAY_HINT_LABELS[entry.slot] || '—';
}

function computeKPIs(filter) {
  const currentWeek = getCurrentWeek();
  // A workout is "past" if its week is fully past
  const pastWorkouts = trainingPlan.filter(w => isWeekPast(w.week));
  const totalPast = pastWorkouts.length;

  let completedAvi = 0, completedShachar = 0;
  let exemptAvi = 0, exemptShachar = 0;
  let kmAvi = 0, kmShachar = 0;

  pastWorkouts.forEach(w => {
    if (w.statusAvi === 'exempt' || w.statusAvi === 'illness') exemptAvi++;
    else if (w.actualDistanceAvi !== null) { completedAvi++; kmAvi += w.actualDistanceAvi; }

    if (w.statusShachar === 'exempt' || w.statusShachar === 'illness') exemptShachar++;
    else if (w.actualDistanceShachar !== null) { completedShachar++; kmShachar += w.actualDistanceShachar; }
  });

  // Also count current week completed workouts
  const currentWorkouts = trainingPlan.filter(w => w.week === currentWeek);
  currentWorkouts.forEach(w => {
    if (w.statusAvi === 'exempt' || w.statusAvi === 'illness') exemptAvi++;
    else if (w.actualDistanceAvi !== null) { completedAvi++; kmAvi += w.actualDistanceAvi; }

    if (w.statusShachar === 'exempt' || w.statusShachar === 'illness') exemptShachar++;
    else if (w.actualDistanceShachar !== null) { completedShachar++; kmShachar += w.actualDistanceShachar; }
  });

  const totalPlannedSoFar = totalPast + currentWorkouts.length;
  const totalPlannedAvi = Math.max(1, totalPlannedSoFar - exemptAvi);
  const totalPlannedShachar = Math.max(1, totalPlannedSoFar - exemptShachar);
  const totalPlannedKm = trainingPlan.reduce((s, w) => s + w.distancePlanned, 0);

  return {
    daysLeft: daysUntilRace(),
    currentWeek,
    totalWorkouts: trainingPlan.length,
    pastWorkouts: totalPast,
    totalPlannedSoFar,
    completedAvi,
    completedShachar,
    completionRateAvi: totalPlannedAvi > 0 ? Math.round((completedAvi / totalPlannedAvi) * 100) : 0,
    completionRateShachar: totalPlannedShachar > 0 ? Math.round((completedShachar / totalPlannedShachar) * 100) : 0,
    kmAvi: kmAvi.toFixed(1),
    kmShachar: kmShachar.toFixed(1),
    totalPlannedKmAvi: totalPlannedKm.toFixed(0),
    totalPlannedKmShachar: totalPlannedKm.toFixed(0),
  };
}


function getWeekLongRunDistance(weekNum) {
  const volumeRun = trainingPlan.find(w => w.week === weekNum &&
    (w.type.includes('נפח') || w.type === WorkoutType.RACE));
  return volumeRun ? volumeRun.distancePlanned : null;
}

// Export
window.TrainingData = {
  trainingPlan,
  workoutDetails,
  WorkoutType,
  Slot,
  DAY_HINT_LABELS,
  Phase,
  getPhaseForWeek,
  paceToSeconds,
  secondsToPace,
  parseDate,
  formatDateHebrew,
  formatDateFull,
  daysUntilRace,
  getCurrentWeek,
  isWeekPast,
  isWeekCurrent,
  isPast,
  isToday,
  getWorkoutStatus,
  getWorkoutTypeClass,
  getWorkoutDetail,
  getDisplayDate,
  computeKPIs,
  getWeekDateRange,
  getWeekLongRunDistance,
  RACE_DATE,
  PLAN_START,
  LAST_SYNC,
  TOTAL_WEEKS: 11,
};
