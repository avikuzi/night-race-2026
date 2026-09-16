// Demo Mode — V5 (11 weeks, flexible weekly)
(function() {
  const demoResults = [
    // Week 1 — Base
    { idx: 0, avi: { dist: 6.5, pace: '6:00', date: '2026-08-14' }, shachar: { dist: 6.5, pace: '5:56', date: '2026-08-13' } },
    { idx: 1, avi: { dist: 7.0, pace: '7:00', date: '2026-08-15' }, shachar: { dist: 7.0, pace: '6:55', date: '2026-08-16' } },
    { idx: 2, avi: { dist: 5.0, pace: '7:02', date: '2026-08-17' }, shachar: { dist: 5.2, pace: '6:48', date: '2026-08-18' } },
    // Week 2 — Base
    { idx: 3, avi: { dist: 7.0, pace: '5:52', date: '2026-08-21' }, shachar: { dist: 7.0, pace: '5:48', date: '2026-08-20' } },
    { idx: 4, avi: { dist: 8.0, pace: '7:05', date: '2026-08-22' }, shachar: { dist: 8.0, pace: '6:52', date: '2026-08-23' } },
    { idx: 5, avi: { dist: 5.5, pace: '7:00', date: '2026-08-24' }, shachar: { dist: 5.5, pace: '6:45', date: '2026-08-24' } },
    // Week 3 — Build
    { idx: 6, avi: { dist: 7.5, pace: '5:42', date: '2026-08-28' }, shachar: { dist: 7.2, pace: '5:38', date: '2026-08-27' } },
    { idx: 7, avi: { dist: 9.0, pace: '6:50', date: '2026-08-29' }, shachar: { dist: 9.0, pace: '6:55', date: '2026-08-30' } },
    { idx: 8, avi: { dist: 5.5, pace: '7:05', date: '2026-08-31' }, shachar: { dist: 5.5, pace: '6:48', date: '2026-08-31' } },
    // Week 4 partial
    { idx: 9, avi: { dist: 8.0, pace: '5:50', date: '2026-09-04' }, shachar: { dist: 8.0, pace: '5:45', date: '2026-09-03' } },
    { idx: 10, avi: { dist: null, pace: null, date: null }, shachar: { dist: 10.0, pace: '6:50', date: '2026-09-06' } },
    { idx: 11, avi: { dist: 5.5, pace: '7:00', date: '2026-09-07' }, shachar: { dist: 5.5, pace: '6:48', date: '2026-09-07' } },
  ];

  const DEMO_DATE = new Date(2026, 8, 8); // Sep 8

  function applyDemoData() {
    demoResults.forEach(r => {
      const e = window.TrainingData.trainingPlan[r.idx];
      if (e) {
        e.actualDistanceAvi = r.avi.dist; e.actualPaceAvi = r.avi.pace; e.actualDateAvi = r.avi.date;
        e.actualDistanceShachar = r.shachar.dist; e.actualPaceShachar = r.shachar.pace; e.actualDateShachar = r.shachar.date;
      }
    });
  }

  function clearDemoData() {
    window.TrainingData.trainingPlan.forEach(e => {
      e.actualDistanceAvi = null; e.actualPaceAvi = null; e.actualDateAvi = null;
      e.actualDistanceShachar = null; e.actualPaceShachar = null; e.actualDateShachar = null;
    });
  }

  const orig = {
    isPast: window.TrainingData.isPast,
    isToday: window.TrainingData.isToday,
    getCurrentWeek: window.TrainingData.getCurrentWeek,
    daysUntilRace: window.TrainingData.daysUntilRace,
    isWeekPast: window.TrainingData.isWeekPast,
    isWeekCurrent: window.TrainingData.isWeekCurrent,
  };

  let isDemoActive = false;

  window.toggleDemoMode = function() {
    isDemoActive = !isDemoActive;
    const btn = document.getElementById('demo-toggle');
    if (isDemoActive) {
      applyDemoData();
      const demoWeek = Math.min(11, Math.floor((DEMO_DATE - window.TrainingData.PLAN_START) / 864e5 / 7) + 1);
      window.TrainingData.isPast = (ds) => { if (!ds) return false; const d = window.TrainingData.parseDate(ds); return d < DEMO_DATE; };
      window.TrainingData.isToday = (ds) => { if (!ds) return false; const d = window.TrainingData.parseDate(ds); return d.toDateString() === DEMO_DATE.toDateString(); };
      window.TrainingData.getCurrentWeek = () => demoWeek;
      window.TrainingData.daysUntilRace = () => Math.max(0, Math.ceil((window.TrainingData.RACE_DATE - DEMO_DATE) / 864e5));
      window.TrainingData.isWeekPast = (w) => w < demoWeek;
      window.TrainingData.isWeekCurrent = (w) => w === demoWeek;
      btn.textContent = '⏹ יציאה ממצב הדגמה'; btn.classList.add('demo-active');
    } else {
      clearDemoData();
      Object.assign(window.TrainingData, orig);
      btn.textContent = '▶ מצב הדגמה'; btn.classList.remove('demo-active');
    }
    if (typeof renderAll === 'function') renderAll();
  };
})();
