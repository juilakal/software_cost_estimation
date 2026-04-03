// ═══════════════════════════════════════════════════════════════
// CostEstimator Pro – Dashboard Script
// ═══════════════════════════════════════════════════════════════

// ── Auth Guard ─────────────────────────────────────────────────
const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

// Show username in navbar
const usernameEl = document.getElementById('nav-username');
if (usernameEl) usernameEl.textContent = localStorage.getItem('username') || 'User';


// ── Logout ─────────────────────────────────────────────────────
function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  window.location.href = '/login';
}


// ── Method Tab Switching ───────────────────────────────────────
let currentMethod = 'cocomo';

function switchMethod(method, btn) {
  currentMethod = method;

  // Update tab styles
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');

  // Toggle field visibility
  document.getElementById('cocomo-fields').style.display =
    method === 'cocomo' ? 'block' : 'none';
  document.getElementById('fpa-fields').style.display =
    method === 'fpa' ? 'block' : 'none';

  // Hide results & errors on switch
  document.getElementById('results-section').style.display = 'none';
  document.getElementById('error-box').style.display = 'none';
}


// ── Calculate Estimation ───────────────────────────────────────
let barChart = null;
let doughnutChart = null;

async function calculate() {
  const costInput = document.getElementById('cost_per_pm').value;
  const errBox = document.getElementById('error-box');
  errBox.style.display = 'none';

  // Validate common field
  if (!costInput || parseFloat(costInput) <= 0) {
    return showError('Please enter a valid cost per person-month.');
  }

  // Build payload
  let payload = { cost_per_pm: parseFloat(costInput) };
  let endpoint = '';

  if (currentMethod === 'cocomo') {
    const kloc = document.getElementById('kloc').value;
    if (!kloc || parseFloat(kloc) <= 0) return showError('Please enter a valid KLOC value.');
    payload.kloc = parseFloat(kloc);
    payload.project_type = document.getElementById('project_type').value;
    endpoint = '/estimate/cocomo';
  } else {
    const fp = document.getElementById('fp').value;
    if (!fp || parseFloat(fp) <= 0) return showError('Please enter valid Function Points.');
    payload.fp = parseFloat(fp);
    payload.language = document.getElementById('language').value;
    endpoint = '/estimate/fpa';
  }

  // Show loading state
  const btn = document.querySelector('.btn-calculate');
  btn.classList.add('loading');

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(payload)
    });

    btn.classList.remove('loading');

    if (res.status === 401) { logout(); return; }

    const data = await res.json();
    if (!res.ok) return showError(data.detail || 'Estimation failed.');

    // Display results
    displayResults(data);

  } catch (err) {
    btn.classList.remove('loading');
    showError('Connection error. Make sure the server is running.');
  }
}


// ── Display Results ────────────────────────────────────────────
function displayResults(data) {
  const section = document.getElementById('results-section');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Method label
  document.getElementById('result-method').textContent =
    currentMethod === 'cocomo' ? 'COCOMO Basic Model' : 'Function Point Analysis';

  // Stat values
  document.getElementById('res-effort').textContent = data.effort.toFixed(2);
  document.getElementById('res-time').textContent = data.time.toFixed(2);
  document.getElementById('res-cost').textContent = '₹ ' + data.cost.toLocaleString('en-IN');

  // Destroy existing charts
  if (barChart) barChart.destroy();
  if (doughnutChart) doughnutChart.destroy();

  // Bar Chart
  const barCtx = document.getElementById('barChart').getContext('2d');
  barChart = new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: ['Effort (PM)', 'Time (Months)', 'Cost (₹ thousands)'],
      datasets: [{
        label: 'Estimation',
        data: [data.effort, data.time, data.cost / 1000],
        backgroundColor: [
          'rgba(129, 140, 248, 0.7)',
          'rgba(52, 211, 153, 0.7)',
          'rgba(251, 191, 36, 0.7)',
        ],
        borderColor: ['#818cf8', '#34d399', '#fbbf24'],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1a1a3e',
          borderColor: '#818cf8',
          borderWidth: 1,
          titleFont: { family: 'Inter' },
          bodyFont: { family: 'Inter' },
        }
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
          grid: { color: 'rgba(148,163,184,0.08)' }
        },
        y: {
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
          grid: { color: 'rgba(148,163,184,0.08)' }
        }
      }
    }
  });

  // Doughnut Chart
  const doughCtx = document.getElementById('doughnutChart').getContext('2d');
  doughnutChart = new Chart(doughCtx, {
    type: 'doughnut',
    data: {
      labels: ['Effort', 'Time', 'Cost Factor'],
      datasets: [{
        data: [data.effort, data.time, data.cost / 1000],
        backgroundColor: [
          'rgba(129, 140, 248, 0.8)',
          'rgba(52, 211, 153, 0.8)',
          'rgba(251, 191, 36, 0.8)',
        ],
        borderColor: '#0f0f23',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#a5b4fc',
            font: { family: 'Inter', size: 11 },
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 10,
          }
        },
        tooltip: {
          backgroundColor: '#1a1a3e',
          borderColor: '#818cf8',
          borderWidth: 1,
          titleFont: { family: 'Inter' },
          bodyFont: { family: 'Inter' },
        }
      }
    }
  });
}


// ── Error Display ──────────────────────────────────────────────
function showError(msg) {
  const box = document.getElementById('error-box');
  box.textContent = '⚠️ ' + msg;
  box.style.display = 'block';
}


// ── Register Service Worker ────────────────────────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(function (err) {
    console.log('SW registration failed:', err);
  });
}