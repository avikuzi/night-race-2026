// ============================================================
// Dashboard Application — app.js (Apple Fitness Redesign)
// Pure Black (#000000), Dark Gray (#1C1C1E), Neon Cyan & Green
// ============================================================

const D = window.TrainingData;
let currentFilter = 'both'; // 'avi', 'shachar', 'both'
let pacingChart = null;
let volumeChart = null;

// ============================================================
// Initialization
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initFilterButtons();
  initModal();
  renderAll();
  startCountdownTimer();
});

function renderAll() {
  renderKPIs();
  renderTimeline();
  renderPacingChart();
  renderVolumeChart();
  renderStatusTable();
  updateLastSyncDisplay();
}

// ============================================================
// Filter Controls (iOS Segmented Control)
// ============================================================
function initFilterButtons() {
  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderAll();
    });
  });
}

// ============================================================
// Workout Detail Modal (Apple Sheet Style)
// ============================================================
function initModal() {
  const modal = document.getElementById('workout-modal');
  const overlay = document.getElementById('modal-overlay');
  if (!modal || !overlay) return;

  overlay.addEventListener('click', closeModal);
  document.getElementById('modal-close')?.addEventListener('click', closeModal);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
}

function openWorkoutModal(index) {
  const entry = D.trainingPlan[index];
  if (!entry) return;

  const detail = D.getWorkoutDetail(entry.type);
  const phase = D.getPhaseForWeek(entry.week);
  const statusAvi = D.getWorkoutStatus(entry, 'avi');
  const statusShachar = D.getWorkoutStatus(entry, 'shachar');

  let html = `
    <div style="margin-bottom:20px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
        <span class="node-phase-badge ${phase.id}">${phase.label}</span>
        <span style="color:var(--text-secondary);font-size:0.8rem;font-weight:600">שבוע ${entry.week} · ${D.getDisplayDate(entry, 'avi')}</span>
      </div>
      <h2 style="font-size:1.6rem;font-weight:900;color:var(--text-primary);letter-spacing:-0.02em">${detail ? detail.title : entry.type}</h2>
      <p style="color:var(--text-secondary);font-size:0.9rem;margin-top:4px">${detail ? detail.description : ''}</p>
    </div>

    <!-- Stats Quick Strip -->
    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;background:var(--bg-app);padding:14px;border-radius:16px;margin-bottom:20px;text-align:center">
      <div>
        <div style="font-size:0.72rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase">מרחק מתוכנן</div>
        <div style="font-size:1.3rem;font-weight:800;color:var(--text-primary);margin-top:2px">${entry.distancePlanned} <span style="font-size:0.8rem;color:var(--text-secondary)">ק"מ</span></div>
      </div>
      <div>
        <div style="font-size:0.72rem;font-weight:700;color:var(--neon-avi);text-transform:uppercase">יעד אבי</div>
        <div style="font-size:1.3rem;font-weight:800;color:var(--neon-avi);font-family:var(--font-mono);margin-top:2px">${entry.targetPaceAvi}</div>
      </div>
      <div>
        <div style="font-size:0.72rem;font-weight:700;color:var(--neon-shachar);text-transform:uppercase">יעד שחר</div>
        <div style="font-size:1.3rem;font-weight:800;color:var(--neon-shachar);font-family:var(--font-mono);margin-top:2px">${entry.targetPaceShachar}</div>
      </div>
    </div>
  `;

  // Performance Section
  html += `<div style="margin-bottom:20px">
    <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;color:var(--text-secondary);letter-spacing:0.05em;margin-bottom:10px">ביצוע בפועל</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <!-- Avi Card -->
      <div style="background:var(--bg-app);padding:14px;border-radius:14px;border-right:3px solid var(--neon-avi)">
        <div style="font-size:0.8rem;font-weight:800;color:var(--neon-avi);margin-bottom:6px">אבי</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--text-primary)">
          ${entry.actualDistanceAvi ? `${entry.actualDistanceAvi} ק"מ @ ${entry.actualPaceAvi}` : '<span style="color:var(--text-muted)">— טרם בוצע</span>'}
        </div>
        <div style="margin-top:6px">${renderStatusBadge(statusAvi)}</div>
      </div>

      <!-- Shachar Card -->
      <div style="background:var(--bg-app);padding:14px;border-radius:14px;border-right:3px solid var(--neon-shachar)">
        <div style="font-size:0.8rem;font-weight:800;color:var(--neon-shachar);margin-bottom:6px">שחר</div>
        <div style="font-size:1.1rem;font-weight:800;color:var(--text-primary)">
          ${entry.actualDistanceShachar ? `${entry.actualDistanceShachar} ק"מ @ ${entry.actualPaceShachar}` : '<span style="color:var(--text-muted)">— טרם בוצע</span>'}
        </div>
        <div style="margin-top:6px">${renderStatusBadge(statusShachar)}</div>
      </div>
    </div>
  </div>`;

  // Structure table if exists
  if (detail && detail.structure) {
    html += `
      <div style="margin-bottom:20px">
        <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;color:var(--text-secondary);letter-spacing:0.05em;margin-bottom:10px">מבנה האימון</div>
        <div style="background:var(--bg-app);border-radius:14px;padding:8px 14px">
    `;
    detail.structure.forEach(s => {
      html += `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--bg-pill)">
          <div>
            <div style="font-weight:700;font-size:0.85rem;color:var(--text-primary)">${s.segment}</div>
            <div style="font-size:0.78rem;color:var(--text-secondary)">${s.detail}</div>
          </div>
          <span style="font-size:0.82rem;font-weight:700;color:var(--text-primary);font-family:var(--font-mono)">${s.duration}</span>
        </div>
      `;
    });
    html += `</div></div>`;
  }

  if (detail && detail.tips) {
    html += `
      <div style="background:rgba(255,214,10,0.08);border-radius:14px;padding:12px 14px;color:var(--neon-yellow);font-size:0.82rem;line-height:1.5">
        💡 <strong>טיפ מאמן:</strong> ${detail.tips}
      </div>
    `;
  }

  const modalBody = document.getElementById('modal-body');
  const modal = document.getElementById('workout-modal');
  const overlay = document.getElementById('modal-overlay');

  if (modalBody && modal && overlay) {
    modalBody.innerHTML = html;
    modal.classList.add('active');
    overlay.classList.add('active');
  }
}

function closeModal() {
  document.getElementById('workout-modal')?.classList.remove('active');
  document.getElementById('modal-overlay')?.classList.remove('active');
}

// ============================================================
// KPI Scorecards & Apple Activity Rings
// ============================================================
function renderKPIs() {
  const kpis = D.computeKPIs(currentFilter);

  // 1. Countdown
  const countdownEl = document.getElementById('kpi-countdown');
  if (countdownEl) countdownEl.textContent = kpis.daysLeft;

  // 2. Completion Rate & Activity Rings
  const compDisplay = document.getElementById('completion-display');
  const compDetail = document.getElementById('kpi-completion-detail');
  const ringsContainer = document.getElementById('activity-rings-container');

  const rateAvi = kpis.completionRateAvi;
  const rateShachar = kpis.completionRateShachar;

  if (compDisplay) {
    if (currentFilter === 'avi') {
      compDisplay.innerHTML = `<div class="kpi-hero-number avi">${rateAvi}%</div>`;
      if (compDetail) compDetail.textContent = `${kpis.completedAvi} מתוך ${kpis.totalPlannedSoFar} אימונים שהושלמו`;
    } else if (currentFilter === 'shachar') {
      compDisplay.innerHTML = `<div class="kpi-hero-number shachar">${rateShachar}%</div>`;
      if (compDetail) compDetail.textContent = `${kpis.completedShachar} מתוך ${kpis.totalPlannedSoFar} אימונים שהושלמו`;
    } else {
      compDisplay.innerHTML = `
        <div class="metric-pair">
          <div class="metric-row">
            <span class="dot-indicator dot-avi"></span>
            <span class="metric-val" style="color:var(--neon-avi)">${rateAvi}%</span>
            <span class="metric-user-label" style="color:var(--neon-avi)">אבי</span>
          </div>
          <div class="metric-row">
            <span class="dot-indicator dot-shachar"></span>
            <span class="metric-val" style="color:var(--neon-shachar)">${rateShachar}%</span>
            <span class="metric-user-label" style="color:var(--neon-shachar)">שחר</span>
          </div>
        </div>
      `;
      if (compDetail) compDetail.textContent = `שבוע ${kpis.currentWeek} מתוך ${D.TOTAL_WEEKS}`;
    }
  }

  // Activity Rings SVG
  if (ringsContainer) {
    ringsContainer.innerHTML = buildActivityRingsSVG(rateAvi, rateShachar, currentFilter);
  }

  // 3. Cumulative Distance (KM)
  const kmDisplay = document.getElementById('km-display');
  const kmDetail = document.getElementById('kpi-km-detail');
  if (kmDisplay) {
    if (currentFilter === 'avi') {
      kmDisplay.innerHTML = `<div class="kpi-hero-number avi">${kpis.kmAvi} <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:600">ק"מ</span></div>`;
      if (kmDetail) kmDetail.textContent = `מתוך ${kpis.totalPlannedKmAvi} ק"מ מתוכננים`;
    } else if (currentFilter === 'shachar') {
      kmDisplay.innerHTML = `<div class="kpi-hero-number shachar">${kpis.kmShachar} <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:600">ק"מ</span></div>`;
      if (kmDetail) kmDetail.textContent = `מתוך ${kpis.totalPlannedKmShachar} ק"מ מתוכננים`;
    } else {
      kmDisplay.innerHTML = `
        <div class="metric-pair">
          <div class="metric-row">
            <span class="dot-indicator dot-avi"></span>
            <span class="metric-val" style="color:var(--neon-avi)">${kpis.kmAvi}</span>
            <span style="font-size:0.75rem;color:var(--text-secondary)">ק"מ</span>
          </div>
          <div class="metric-row">
            <span class="dot-indicator dot-shachar"></span>
            <span class="metric-val" style="color:var(--neon-shachar)">${kpis.kmShachar}</span>
            <span style="font-size:0.75rem;color:var(--text-secondary)">ק"מ</span>
          </div>
        </div>
      `;
      if (kmDetail) kmDetail.textContent = `יעד כולל: ${kpis.totalPlannedKmAvi} ק"מ`;
    }
  }

  // 4. Workouts Done Count
  const workoutsDisplay = document.getElementById('workouts-count-display');
  const workoutsDetail = document.getElementById('kpi-workouts-detail');
  if (workoutsDisplay) {
    if (currentFilter === 'avi') {
      workoutsDisplay.innerHTML = `<div class="kpi-hero-number avi">${kpis.completedAvi} <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:600">/ ${kpis.totalWorkouts}</span></div>`;
      if (workoutsDetail) workoutsDetail.textContent = `הושלמו עד כה בהצלחה`;
    } else if (currentFilter === 'shachar') {
      workoutsDisplay.innerHTML = `<div class="kpi-hero-number shachar">${kpis.completedShachar} <span style="font-size:1.1rem;color:var(--text-secondary);font-weight:600">/ ${kpis.totalWorkouts}</span></div>`;
      if (workoutsDetail) workoutsDetail.textContent = `הושלמו עד כה בהצלחה`;
    } else {
      workoutsDisplay.innerHTML = `
        <div class="metric-pair">
          <div class="metric-row">
            <span class="dot-indicator dot-avi"></span>
            <span class="metric-val" style="color:var(--neon-avi)">${kpis.completedAvi}</span>
            <span style="font-size:0.75rem;color:var(--text-secondary)">/ ${kpis.totalWorkouts} אימונים</span>
          </div>
          <div class="metric-row">
            <span class="dot-indicator dot-shachar"></span>
            <span class="metric-val" style="color:var(--neon-shachar)">${kpis.completedShachar}</span>
            <span style="font-size:0.75rem;color:var(--text-secondary)">/ ${kpis.totalWorkouts} אימונים</span>
          </div>
        </div>
      `;
      if (workoutsDetail) workoutsDetail.textContent = `סה"כ ${kpis.totalWorkouts} אימונים בתוכנית`;
    }
  }
}

/**
 * Build Apple Watch Activity Rings SVG (Concentric or Single)
 */
function buildActivityRingsSVG(pctAvi, pctShachar, filter) {
  const size = 90;
  const center = size / 2;

  // Outer Ring (Avi - Cyan)
  const rOuter = 34;
  const cOuter = 2 * Math.PI * rOuter;
  const offsetOuter = cOuter - (Math.min(100, Math.max(0, pctAvi)) / 100) * cOuter;

  // Inner Ring (Shachar - Green)
  const rInner = 22;
  const cInner = 2 * Math.PI * rInner;
  const offsetInner = cInner - (Math.min(100, Math.max(0, pctShachar)) / 100) * cInner;

  if (filter === 'avi') {
    return `
      <svg class="rings-svg" viewBox="0 0 ${size} ${size}">
        <circle class="ring-bg ring-avi-bg" cx="${center}" cy="${center}" r="30" stroke-width="10" />
        <circle class="ring-progress ring-avi-fg" cx="${center}" cy="${center}" r="30" stroke-width="10"
          stroke-dasharray="${2 * Math.PI * 30}" stroke-dashoffset="${(2 * Math.PI * 30) - (Math.min(100, pctAvi)/100)*(2 * Math.PI * 30)}" />
      </svg>
    `;
  }

  if (filter === 'shachar') {
    return `
      <svg class="rings-svg" viewBox="0 0 ${size} ${size}">
        <circle class="ring-bg ring-shachar-bg" cx="${center}" cy="${center}" r="30" stroke-width="10" />
        <circle class="ring-progress ring-shachar-fg" cx="${center}" cy="${center}" r="30" stroke-width="10"
          stroke-dasharray="${2 * Math.PI * 30}" stroke-dashoffset="${(2 * Math.PI * 30) - (Math.min(100, pctShachar)/100)*(2 * Math.PI * 30)}" />
      </svg>
    `;
  }

  // Both concentric rings
  return `
    <svg class="rings-svg" viewBox="0 0 ${size} ${size}">
      <!-- Outer Ring: Avi -->
      <circle class="ring-bg ring-avi-bg" cx="${center}" cy="${center}" r="${rOuter}" stroke-width="8" />
      <circle class="ring-progress ring-avi-fg" cx="${center}" cy="${center}" r="${rOuter}" stroke-width="8"
        stroke-dasharray="${cOuter}" stroke-dashoffset="${offsetOuter}" />
      
      <!-- Inner Ring: Shachar -->
      <circle class="ring-bg ring-shachar-bg" cx="${center}" cy="${center}" r="${rInner}" stroke-width="8" />
      <circle class="ring-progress ring-shachar-fg" cx="${center}" cy="${center}" r="${rInner}" stroke-width="8"
        stroke-dasharray="${cInner}" stroke-dashoffset="${offsetInner}" />
    </svg>
  `;
}

function startCountdownTimer() {
  setInterval(() => {
    const el = document.getElementById('kpi-countdown');
    if (el) el.textContent = D.daysUntilRace();
  }, 60000);
}

// ============================================================
// Minimalist Horizontal Timeline (Roadmap)
// ============================================================
function renderTimeline() {
  const nodesContainer = document.getElementById('timeline-nodes');
  const progressBar = document.getElementById('timeline-progress-bar');
  if (!nodesContainer) return;

  const currentWeek = D.getCurrentWeek();
  const totalWeeks = D.TOTAL_WEEKS;

  // Set progress line width (percentage up to current week)
  if (progressBar) {
    const pct = Math.min(100, Math.max(0, ((currentWeek - 0.5) / (totalWeeks - 1)) * 100));
    progressBar.style.width = `${pct}%`;
  }

  let html = '';

  for (let w = 1; w <= totalWeeks; w++) {
    const phase = D.getPhaseForWeek(w);
    const dateRange = D.getWeekDateRange(w);
    const longRunDist = D.getWeekLongRunDistance(w);
    const isPast = D.isWeekPast(w);
    const isCurrent = D.isWeekCurrent(w);
    const isRace = w === totalWeeks;

    let nodeClass = '';
    if (isRace) nodeClass += ' race';
    else if (isCurrent) nodeClass += ' current';
    else if (isPast) nodeClass += ' past';

    html += `
      <div class="timeline-node ${nodeClass}" title="שבוע ${w} (${dateRange})" onclick="scrollToWeek(${w})">
        <div class="node-dot"></div>
        <div class="node-week-num">${isRace ? '🏁' : `שב' ${w}`}</div>
        <div class="node-dates">${dateRange}</div>
        <div class="node-phase-badge ${phase.id}">${phase.label}</div>
        ${longRunDist ? `<div class="node-milestone-km">${isRace ? '15 ק"מ' : `${longRunDist}k`}</div>` : ''}
      </div>
    `;
  }

  nodesContainer.innerHTML = html;
}

function scrollToWeek(weekNum) {
  const rows = document.querySelectorAll(`.status-table tbody tr`);
  for (const row of rows) {
    if (row.dataset.week === String(weekNum)) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      row.style.background = 'var(--bg-card-elevated)';
      setTimeout(() => { row.style.background = ''; }, 1500);
      break;
    }
  }
}

// ============================================================
// Pacing Spline Chart (Apple Fitness Spline)
// ============================================================
function renderPacingChart() {
  const canvas = document.getElementById('pacing-canvas');
  if (!canvas) return;

  const qualityWorkouts = D.trainingPlan.filter(w =>
    w.type.includes('איכות') || w.type.includes('טמפו') || w.type.includes('פרטלק') || w.type.includes('אינטרוולים') || w.type === D.WorkoutType.RACE
  );

  const labels = qualityWorkouts.map(w => {
    return w.actualDateAvi ? D.formatDateHebrew(w.actualDateAvi) : (w.actualDateShachar ? D.formatDateHebrew(w.actualDateShachar) : `שב' ${w.week}`);
  });

  const targetAvi = qualityWorkouts.map(w => D.paceToSeconds(w.targetPaceAvi));
  const actualAvi = qualityWorkouts.map(w => D.paceToSeconds(w.actualPaceAvi));
  const targetShachar = qualityWorkouts.map(w => D.paceToSeconds(w.targetPaceShachar));
  const actualShachar = qualityWorkouts.map(w => D.paceToSeconds(w.actualPaceShachar));

  const datasets = [];

  if (currentFilter !== 'shachar') {
    datasets.push({
      label: 'יעד אבי',
      data: targetAvi,
      borderColor: 'rgba(0, 240, 255, 0.4)',
      borderWidth: 2,
      borderDash: [5, 5],
      tension: 0.4,
      pointRadius: 0,
      fill: false,
    });
    datasets.push({
      label: 'בפועל אבי',
      data: actualAvi,
      borderColor: '#00F0FF',
      backgroundColor: 'rgba(0, 240, 255, 0.08)',
      borderWidth: 3,
      tension: 0.4,
      pointRadius: 5,
      pointBackgroundColor: '#00F0FF',
      pointBorderColor: '#000000',
      pointBorderWidth: 2,
      pointHoverRadius: 7,
      fill: true,
    });
  }

  if (currentFilter !== 'avi') {
    datasets.push({
      label: 'יעד שחר',
      data: targetShachar,
      borderColor: 'rgba(48, 209, 88, 0.4)',
      borderWidth: 2,
      borderDash: [5, 5],
      tension: 0.4,
      pointRadius: 0,
      fill: false,
    });
    datasets.push({
      label: 'בפועל שחר',
      data: actualShachar,
      borderColor: '#30D158',
      backgroundColor: 'rgba(48, 209, 88, 0.08)',
      borderWidth: 3,
      tension: 0.4,
      pointRadius: 5,
      pointBackgroundColor: '#30D158',
      pointBorderColor: '#000000',
      pointBorderWidth: 2,
      pointHoverRadius: 7,
      fill: true,
    });
  }

  if (pacingChart) pacingChart.destroy();

  pacingChart = new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          rtl: true,
          labels: {
            color: '#8E8E93',
            font: { family: "-apple-system, sans-serif", size: 11, weight: '600' },
            usePointStyle: true,
            boxWidth: 8,
          }
        },
        tooltip: {
          backgroundColor: '#1C1C1E',
          titleColor: '#FFFFFF',
          bodyColor: '#8E8E93',
          borderColor: '#2C2C2E',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 12,
          rtl: true,
          textDirection: 'rtl',
          callbacks: {
            label: function(c) {
              return `${c.dataset.label}: ${D.secondsToPace(c.parsed.y)} דק'/ק"מ`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#636366', font: { family: "-apple-system, sans-serif", size: 10 } }
        },
        y: {
          reverse: true, // Lower seconds = faster pace at top!
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: {
            color: '#636366',
            font: { family: "JetBrains Mono, monospace", size: 10 },
            callback: v => D.secondsToPace(v)
          }
        }
      }
    }
  });
}

// ============================================================
// Volume Bar Chart (Apple Fitness Rounded Bars)
// ============================================================
function renderVolumeChart() {
  const canvas = document.getElementById('volume-canvas');
  if (!canvas) return;

  const totalWeeks = D.TOTAL_WEEKS;
  const weeks = [];

  for (let w = 1; w <= totalWeeks; w++) {
    const workouts = D.trainingPlan.filter(e => e.week === w);
    const plannedKm = workouts.reduce((s, e) => s + e.distancePlanned, 0);
    const actualKmAvi = workouts.reduce((s, e) => s + (e.actualDistanceAvi || 0), 0);
    const actualKmShachar = workouts.reduce((s, e) => s + (e.actualDistanceShachar || 0), 0);
    weeks.push({ week: w, plannedKm, actualKmAvi, actualKmShachar });
  }

  const labels = weeks.map(w => `שב' ${w.week}`);
  const datasets = [{
    label: 'מתוכנן',
    data: weeks.map(w => w.plannedKm),
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 8,
    borderSkipped: false,
    barPercentage: 0.85,
    categoryPercentage: 0.8,
  }];

  if (currentFilter !== 'shachar') {
    datasets.push({
      label: 'אבי',
      data: weeks.map(w => w.actualKmAvi || null),
      backgroundColor: '#00F0FF',
      borderRadius: 8,
      borderSkipped: false,
      barPercentage: 0.85,
      categoryPercentage: 0.8,
    });
  }

  if (currentFilter !== 'avi') {
    datasets.push({
      label: 'שחר',
      data: weeks.map(w => w.actualKmShachar || null),
      backgroundColor: '#30D158',
      borderRadius: 8,
      borderSkipped: false,
      barPercentage: 0.85,
      categoryPercentage: 0.8,
    });
  }

  if (volumeChart) volumeChart.destroy();

  volumeChart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          rtl: true,
          labels: {
            color: '#8E8E93',
            font: { family: "-apple-system, sans-serif", size: 11, weight: '600' },
            usePointStyle: true,
            boxWidth: 8,
          }
        },
        tooltip: {
          backgroundColor: '#1C1C1E',
          titleColor: '#FFFFFF',
          bodyColor: '#8E8E93',
          borderColor: '#2C2C2E',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 12,
          rtl: true,
          textDirection: 'rtl',
          callbacks: {
            label: function(c) {
              return `${c.dataset.label}: ${c.parsed.y} ק"מ`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#636366', font: { family: "-apple-system, sans-serif", size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: {
            color: '#636366',
            font: { family: "JetBrains Mono, monospace", size: 10 },
            callback: v => v + ' ק"מ'
          }
        }
      }
    }
  });
}

// ============================================================
// Status Table (Apple Fitness Card List)
// ============================================================
function renderStatusTable() {
  const tbody = document.getElementById('status-table-body');
  if (!tbody) return;

  let html = '';
  let prevWeek = null;

  D.trainingPlan.forEach((entry, idx) => {
    const isNewWeek = entry.week !== prevWeek;
    prevWeek = entry.week;

    const phase = D.getPhaseForWeek(entry.week);
    const typeClass = D.getWorkoutTypeClass(entry.type);
    const statusAvi = D.getWorkoutStatus(entry, 'avi');
    const statusShachar = D.getWorkoutStatus(entry, 'shachar');
    const showAvi = currentFilter !== 'shachar';
    const showShachar = currentFilter !== 'avi';

    const isPastWeek = D.isWeekPast(entry.week);
    const rowClass = `${isNewWeek ? 'week-start ' : ''}${isPastWeek ? 'past-week-row ' : ''}`.trim();
    const hasToday = (entry.actualDateAvi && D.isToday(entry.actualDateAvi)) || (entry.actualDateShachar && D.isToday(entry.actualDateShachar));
    const todayStyle = hasToday ? 'style="background:rgba(0,240,255,0.06)"' : '';
    const hasDetail = D.getWorkoutDetail(entry.type) !== null;

    html += `<tr class="${rowClass}" data-week="${entry.week}" ${todayStyle} onclick="openWorkoutModal(${idx})" title="לחץ לפירוט האימון">`;

    if (isNewWeek) {
      const weekWorkouts = D.trainingPlan.filter(w => w.week === entry.week);
      const dateRange = D.getWeekDateRange(entry.week);
      html += `<td rowspan="${weekWorkouts.length}" style="vertical-align:middle;text-align:center;font-weight:800;font-size:1.1rem;background:var(--bg-card);border-left:1px solid var(--bg-pill)">
        ${entry.week}
        <div style="margin-top:4px"><span class="node-phase-badge ${phase.id}">${phase.label}</span></div>
        <div style="margin-top:6px;font-size:0.7rem;font-weight:600;color:var(--text-secondary);font-family:var(--font-mono);direction:ltr;white-space:nowrap">${dateRange}</div>
      </td>`;
    }

    const displayPerson = currentFilter === 'shachar' ? 'shachar' : 'avi';
    const dateDisplay = D.getDisplayDate(entry, displayPerson);
    html += `<td style="color:var(--text-secondary)">${dateDisplay}</td>`;
    html += `<td><span class="workout-type ${typeClass}">${entry.type}</span>${hasDetail ? ' <span style="font-size:0.7rem;opacity:0.6">ℹ️</span>' : ''}</td>`;
    html += `<td style="text-align:center;font-family:var(--font-mono);direction:ltr;font-weight:700;color:var(--text-primary)">${entry.distancePlanned}</td>`;

    if (showAvi) {
      html += `<td class="pace-cell" style="color:var(--text-secondary)">${entry.targetPaceAvi}</td>`;
      html += `<td style="text-align:center;font-family:var(--font-mono);direction:ltr;color:var(--neon-avi);font-weight:700">${entry.actualDistanceAvi ?? '<span class="empty-cell">—</span>'}</td>`;
      const aviCls = statusAvi === 'on-track' ? 'actual-good' : statusAvi === 'warning' ? 'actual-warning' : statusAvi === 'off-track' ? 'actual-bad' : '';
      html += `<td class="pace-cell ${aviCls}">${entry.actualPaceAvi ?? '<span class="empty-cell">—</span>'}</td>`;
      html += `<td>${renderStatusBadge(statusAvi)}</td>`;
    }

    if (showShachar) {
      html += `<td class="pace-cell" style="color:var(--text-secondary)">${entry.targetPaceShachar}</td>`;
      html += `<td style="text-align:center;font-family:var(--font-mono);direction:ltr;color:var(--neon-shachar);font-weight:700">${entry.actualDistanceShachar ?? '<span class="empty-cell">—</span>'}</td>`;
      const shCls = statusShachar === 'on-track' ? 'actual-good' : statusShachar === 'warning' ? 'actual-warning' : statusShachar === 'off-track' ? 'actual-bad' : '';
      html += `<td class="pace-cell ${shCls}">${entry.actualPaceShachar ?? '<span class="empty-cell">—</span>'}</td>`;
      html += `<td>${renderStatusBadge(statusShachar)}</td>`;
    }

    html += `<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;color:var(--text-secondary);font-size:0.78rem">${entry.notes || ''}</td>`;
    html += `</tr>`;
  });

  tbody.innerHTML = html;
  renderTableHeader();
}

function renderTableHeader() {
  const thead = document.getElementById('status-table-head');
  if (!thead) return;

  const showAvi = currentFilter !== 'shachar';
  const showShachar = currentFilter !== 'avi';

  let html = '<tr>';
  html += '<th>שבוע</th><th>תאריך</th><th>סוג אימון</th><th>יעד ק"מ</th>';

  if (showAvi) {
    html += '<th style="color:var(--neon-avi)">יעד אבי</th>';
    html += '<th style="color:var(--neon-avi)">ק"מ בפועל</th>';
    html += '<th style="color:var(--neon-avi)">קצב בפועל</th>';
    html += '<th style="color:var(--neon-avi)">סטטוס אבי</th>';
  }
  if (showShachar) {
    html += '<th style="color:var(--neon-shachar)">יעד שחר</th>';
    html += '<th style="color:var(--neon-shachar)">ק"מ בפועל</th>';
    html += '<th style="color:var(--neon-shachar)">קצב בפועל</th>';
    html += '<th style="color:var(--neon-shachar)">סטטוס שחר</th>';
  }

  html += '<th>הערות</th></tr>';
  thead.innerHTML = html;
}

function renderStatusBadge(status) {
  const map = {
    'on-track': { label: '✓ בטווח', class: 'on-track' },
    'warning': { label: '⚠ חריגה קלה', class: 'warning' },
    'off-track': { label: '✗ חריגה', class: 'off-track' },
    'skipped': { label: '— לא בוצע', class: 'skipped' },
    'exempt': { label: '🦷 עקירה כירורגית', class: 'exempt' },
    'illness': { label: '🤒 מחלה', class: 'illness' },
    'pending': { label: '⏳ ממתין', class: 'pending' },
  };
  const s = map[status] || map['pending'];
  return `<span class="status-badge ${s.class}">${s.label}</span>`;
}

// ============================================================
// Garmin Sync Controls
// ============================================================
function updateLastSyncDisplay() {
  const syncTimeEl = document.getElementById('last-sync-time');
  if (syncTimeEl && D.LAST_SYNC) {
    syncTimeEl.textContent = D.LAST_SYNC;
  }
}

async function triggerGarminSync() {
  const btn = document.getElementById('sync-btn');
  if (btn) btn.classList.add('spinning');

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const resp = await fetch('http://localhost:5055/sync', { method: 'POST', signal: controller.signal });
    clearTimeout(timeoutId);
    if (resp.ok) {
      setTimeout(() => { forceReloadNoCache(); }, 2500);
      return;
    }
  } catch (e) {}

  setTimeout(() => {
    if (btn) btn.classList.remove('spinning');
    openSyncModal();
  }, 500);
}

function openSyncModal() {
  let modal = document.getElementById('sync-info-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'sync-info-modal';
    modal.className = 'modal-backdrop';
    modal.style.position = 'fixed';
    modal.style.inset = '0';
    modal.style.zIndex = '1000';
    modal.style.background = 'rgba(0,0,0,0.8)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.padding = '20px';
    modal.style.backdropFilter = 'blur(16px)';

    modal.innerHTML = `
      <div style="background:var(--bg-card);border-radius:24px;max-width:440px;width:100%;padding:28px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.8)">
        <div style="font-size:2.4rem;margin-bottom:12px">🔄</div>
        <h3 style="margin-bottom:8px;font-size:1.3rem;font-weight:800;color:var(--text-primary)">סנכרון Garmin Connect</h3>
        <p style="color:var(--text-secondary);font-size:0.88rem;margin-bottom:18px">
          סנכרון אחרון: <strong style="color:var(--neon-avi)">${D.LAST_SYNC || '23/08/2026, 18:36'}</strong>
        </p>
        
        <div style="background:var(--bg-app);border-radius:14px;padding:16px;margin-bottom:20px;text-align:right;font-size:0.82rem;line-height:1.7;color:var(--text-secondary)">
          <div>• <strong>סנכרון מהשעון לטלפון:</strong> ודאו שפתחתם את אפליקציית Garmin Connect.</div>
          <div>• <strong>עדכון רקע אוטומטי:</strong> המחשב מסנכרן ומעדכן את האתר כל שעתיים.</div>
          <div>• <strong>סנכרון מיידי מהמחשב:</strong> לחצו על <code>sync.bat</code>.</div>
        </div>

        <div style="display:flex;gap:10px;justify-content:center">
          <button class="sync-btn-header" style="padding:10px 20px;font-size:0.88rem" onclick="forceReloadNoCache()">🔄 רענן נתונים עכשיו</button>
          <button class="filter-btn" style="padding:10px 18px" onclick="closeSyncModal()">סגור</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeSyncModal();
    });
  }
  modal.style.display = 'flex';
}

function closeSyncModal() {
  const modal = document.getElementById('sync-info-modal');
  if (modal) modal.style.display = 'none';
}

function forceReloadNoCache() {
  const url = new URL(window.location.href);
  url.searchParams.set('t', Date.now());
  window.location.href = url.toString();
}
