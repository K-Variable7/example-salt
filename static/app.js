// Client-side helper utilities
function bufToHex(buffer) {
  return Array.prototype.map.call(new Uint8Array(buffer), x => ('00' + x.toString(16)).slice(-2)).join('');
}

function hexToBuf(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  return bytes;
}

function generateSalt(n = 16) {
  const b = new Uint8Array(n);
  crypto.getRandomValues(b);
  return b;
}

async function sha256Hex(strOrBuf) {
  let data;
  if (typeof strOrBuf === 'string') data = new TextEncoder().encode(strOrBuf);
  else data = strOrBuf;
  const digest = await crypto.subtle.digest('SHA-256', data);
  return bufToHex(digest);
}

function estimateEntropyBits(password) {
  if (!password) return 0;
  let charset = 0;
  if (/[a-z]/.test(password)) charset += 26;
  if (/[A-Z]/.test(password)) charset += 26;
  if (/[0-9]/.test(password)) charset += 10;
  if (/[^a-zA-Z0-9]/.test(password)) charset += 32; // rough symbol estimate
  // fallback
  if (charset === 0) charset = 26;
  const bitsPerChar = Math.log2(charset);
  return Math.round(bitsPerChar * password.length);
}

function prettyTimeSeconds(sec) {
  if (sec < 1) return `${(sec * 1000).toFixed(2)} ms`;
  const units = ['s','m','h','d','y'];
  const conv = [60,60,24,365];
  let i = 0;
  let val = sec;
  while (i < conv.length && val >= conv[i]) {
    val /= conv[i];
    i++;
  }
  return `${val.toFixed(2)} ${units[i]}`;
}

function humanizeBytes(bytes) {
  const units = ['B','KB','MB','GB','TB'];
  let i = 0, v = bytes;
  while (v >= 1024 && i < units.length -1) { v /= 1024; i++; }
  return `${v.toFixed(2)} ${units[i]}`;
}

// Simple password generator
function generatePassword(len = 16) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-=_+[]{}|;:,.<>?';
  const arr = new Uint32Array(len);
  crypto.getRandomValues(arr);
  return Array.from(arr).map((v,i) => chars[v % chars.length]).join('');
}

// Demo data
const sampleRainbow = ['password','123456','qwerty','letmein','12345678','password1'];

// Rainbow-table simulator data (loaded from data/common_passwords.txt)
let commonPasswords = [];
let rainbowMap = new Map(); // unsalted sha256 -> password
let rainbowChart = null;

// UI wiring
const passwordInput = document.getElementById('password');
const showPwd = document.getElementById('showPwd');
const showPwLabel = document.getElementById('showPwLabel');
const darkToggle = document.getElementById('darkToggle');
const generateBtn = document.getElementById('generate');

// Apply stored theme preference
(function applyStoredTheme(){
  try {
    const v = localStorage.getItem('saltDemo_dark');
    // Default to light mode unless user has explicitly set dark (v === '1')
    if (v === '1') {
      document.body.classList.add('dark');
      if (darkToggle) darkToggle.checked = true;
    } else {
      // ensure toggle unchecked by default
      if (darkToggle) darkToggle.checked = false;
      document.body.classList.remove('dark');
    }
  } catch(e){ /* ignore */ }
})();

// Toggle dark mode
if (darkToggle) darkToggle.addEventListener('change', (e) => {
  try {
    if (darkToggle.checked) {
      document.body.classList.add('dark');
      localStorage.setItem('saltDemo_dark', '1');
    } else {
      document.body.classList.remove('dark');
      localStorage.setItem('saltDemo_dark', '0');
    }
  } catch(e){ }
});

// Show password toggle
if (showPwd) showPwd.addEventListener('change', () => {
  passwordInput.type = showPwd.checked ? 'text' : 'password';
});
if (showPwLabel) showPwLabel.addEventListener('click', (e) => { if (e.target === showPwd) return; showPwd.checked = !showPwd.checked; showPwd.dispatchEvent(new Event('change')); });
const demoBtn = document.getElementById('demoBtn');
const localOnly = document.getElementById('localOnly');
const strengthValue = document.getElementById('strengthValue');
const demoResults = document.getElementById('demoResults');
const resultsDiv = document.getElementById('results');
const useArgonLocal = document.getElementById('useArgonLocal');
const useBcryptLocal = document.getElementById('useBcryptLocal');
const bcryptRounds = document.getElementById('bcryptRounds');
const useScryptLocal = document.getElementById('useScryptLocal');
const scryptN = document.getElementById('scryptN');
const scryptR = document.getElementById('scryptR');
const scryptP = document.getElementById('scryptP');
const kdfStatus = document.getElementById('kdfStatus');
const argonTime = document.getElementById('argonTime');
const argonMem = document.getElementById('argonMem');
const argonParallel = document.getElementById('argonParallel');
const argonStatus = document.getElementById('argonStatus');

// Global error handlers to surface client-side issues in the demo results area
window.addEventListener('error', (e) => {
  try {
    demoResults.style.display = 'block';
    demoResults.innerText = 'JS Error: ' + (e && e.message ? e.message : String(e));
  } catch (_) {}
  console.error(e);
});
window.addEventListener('unhandledrejection', (e) => {
  try {
    demoResults.style.display = 'block';
    demoResults.innerText = 'UnhandledRejection: ' + (e && e.reason && e.reason.message ? e.reason.message : String(e));
  } catch (_) {}
  console.error(e);
});

let _argonLoading = false;
async function loadArgon2() {
  if (window.argon2) return window.argon2;
  if (_argonLoading) {
    // wait until available
    while (!window.argon2) await new Promise(r => setTimeout(r, 50));
    return window.argon2;
  }
  _argonLoading = true;
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/argon2-browser/dist/argon2.min.js';
    s.onload = () => {
      // Wait until the library initializes and exposes `hash`
      let tries = 0;
      const iv = setInterval(() => {
        if (window.argon2 && typeof window.argon2.hash === 'function') {
          clearInterval(iv);
          _argonLoading = false;
          resolve(window.argon2);
        } else if (++tries > 400) { // increase wait to ~20s (400*50ms)
          clearInterval(iv);
          _argonLoading = false;
          reject(new Error('Argon2 loaded but did not initialize in time'));
        }
      }, 50);
    };
    s.onerror = (e) => {
      _argonLoading = false;
      reject(new Error('Failed to load Argon2 script'));
    };
    document.head.appendChild(s);
  });
}

// Lazy-load bcrypt.js (fast to load, pure JS) from CDN
let _bcryptLoading = false;
async function loadBcrypt() {
  if (window.bcrypt) return window.bcrypt;
  if (_bcryptLoading) {
    while (!window.bcrypt) await new Promise(r => setTimeout(r,50));
    return window.bcrypt;
  }
  _bcryptLoading = true;
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/bcryptjs@2.4.3/dist/bcrypt.min.js';
    s.onload = () => { _bcryptLoading = false; resolve(window.dcodeIO && window.dcodeIO.bcrypt ? window.dcodeIO.bcrypt : window.bcrypt); };
    s.onerror = (e) => { _bcryptLoading = false; reject(new Error('Failed to load bcrypt.js')); };
    document.head.appendChild(s);
  });
}

// Lazy-load scrypt-async (npm: scrypt-async) for demo scrypt computation
let _scryptLoading = false;
async function loadScrypt() {
  if (window.scrypt) return window.scrypt;
  if (_scryptLoading) {
    while (!window.scrypt) await new Promise(r => setTimeout(r,50));
    return window.scrypt;
  }
  _scryptLoading = true;
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/scrypt-async@2.0.3/scrypt-async.min.js';
    s.onload = () => { _scryptLoading = false; if (window.scrypt) resolve(window.scrypt); else resolve(window.scrypt); };
    s.onerror = (e) => { _scryptLoading = false; reject(new Error('Failed to load scrypt-async')); };
    document.head.appendChild(s);
  });
}

showPwd.addEventListener('change', () => {
  passwordInput.type = showPwd.checked ? 'text' : 'password';
});

generateBtn.addEventListener('click', (e) => {
  e.preventDefault();
  passwordInput.value = generatePassword(16);
  updateStrength();
});

passwordInput.addEventListener('input', updateStrength);

function updateStrength() {
  const pwd = passwordInput.value;
  const bits = estimateEntropyBits(pwd);
  let label = 'Very weak';
  if (bits > 80) label = 'Strong';
  else if (bits > 50) label = 'Moderate';
  else if (bits > 30) label = 'Weak';
  strengthValue.textContent = `${label} — ${bits} bits`;
}

// Demo runner
async function runDemo() {
  // Make sure results area is visible immediately
  demoResults.style.display = 'block';
  demoResults.innerHTML = '<em>Computing hashes...</em>';

  const pwd = passwordInput.value || '';
  let out = null;
  if (!pwd) {
    demoResults.innerHTML = '<em>Enter or generate a password first.</em>';
    return;
  }

  demoBtn.disabled = true;
  demoBtn.classList.add('is-loading');
  try {
    demoResults.innerHTML = '<em>Computing hashes...</em>';
    demoResults.classList.remove('hidden');
    demoResults.classList.add('show');
    // local client-side unsalted and salted
    const unsalted = await sha256Hex(pwd);
    const salt = generateSalt(16);
    const saltedBuf = new Uint8Array(salt.length + new TextEncoder().encode(pwd).length);
    saltedBuf.set(salt,0);
    saltedBuf.set(new TextEncoder().encode(pwd), salt.length);
    const saltedHex = await sha256Hex(saltedBuf);
    const saltHex = bufToHex(salt);

    // simulate multiple users with same password
    const users = 5;
    const unsaltedList = Array(users).fill(unsalted);
    const saltedList = Array.from({length: users}, () => {
      const s = generateSalt(16);
      const b = new Uint8Array(s.length + new TextEncoder().encode(pwd).length);
      b.set(s,0);
      b.set(new TextEncoder().encode(pwd), s.length);
      return { salt_hex: bufToHex(s), salted_sha: null, salt: s };
    });
    for (let u of saltedList) {
      u.salted_sha = await sha256Hex(new Uint8Array([...u.salt, ...new TextEncoder().encode(pwd)]));
    }

    // Rainbow table simulation: precomputed unsalted table for sample passwords
    const rainbowMap = new Map();
    for (const pw of sampleRainbow) rainbowMap.set(await sha256Hex(pw), pw);
    const rainbowHit = rainbowMap.has(unsalted);

    // Crack time estimation (brute force based on entropy)
    const entropyBits = estimateEntropyBits(pwd);
    const guesses = Math.pow(2, entropyBits);
    const attackerSpeed = 1e9; // guesses per second (example)
    const timeSec = guesses / attackerSpeed;

    // Build UI
    out = document.createElement('div');
    out.innerHTML = `
      <h4>Computed</h4>
      <p><strong>Unsalted SHA-256:</strong> <code>${unsalted}</code></p>
      <p><strong>Salt (hex):</strong> <code>${saltHex}</code></p>
      <p><strong>Salted SHA-256:</strong> <code>${saltedHex}</code></p>
      <p><strong>Estimated crack time (brute-force @ 1e9 guesses/s):</strong> ${prettyTimeSeconds(timeSec)}</p>
      <h4>Simulation: ${users} users with same password</h4>
      <p>Unique unsalted hashes: <strong>${new Set(unsaltedList).size}</strong></p>
      <p>Unique salted hashes: <strong>${new Set(saltedList.map(s=>s.salted_sha)).size}</strong></p>
      <h4>Rainbow-table demo</h4>
      <p>${rainbowHit ? '<strong style="color:red">Unsalted hash found in precomputed table (instant crack)</strong>' : 'Not found in small demo rainbow table.'}</p>
    `;

    // Client-side KDFs: Argon2, bcrypt, scrypt (when Local-only is enabled and selected)
    if (localOnly.checked && ( (useArgonLocal && useArgonLocal.checked) || (useBcryptLocal && useBcryptLocal.checked) || (useScryptLocal && useScryptLocal.checked) )) {
      try {
        // Argon2 branch
        if (useArgonLocal && useArgonLocal.checked) {
          const argTime = Math.max(1, parseInt(argonTime.value || '2', 10));
          const argMem = Math.max(8, parseInt(argonMem.value || '65536', 10));
          const argParallel = Math.max(1, parseInt(argonParallel.value || '1', 10));
          const warnMemKB = 262144;
          if (argMem > warnMemKB) {
            const ok = await showConfirmModal(`Argon2 memory set to ${humanizeBytes(argMem*1024)} which is high and may make your browser unresponsive. Proceed?`);
            if (!ok) {
              out.innerHTML += `<p style="color:orange">Argon2 cancelled by user due to high resource request.</p>`;
              argonStatus.textContent = 'Argon2 cancelled by user';
              updateCharts(timeSec, new Set(unsaltedList).size, new Set(saltedList.map(s=>s.salted_sha)).size);
              demoResults.innerHTML = '';
              demoResults.appendChild(out);
              return;
            }
          }
          argonStatus.textContent = 'Loading Argon2...';
          const argon = await loadArgon2();
          argonStatus.textContent = 'Computing Argon2...';
          const startA = performance.now();
          const argRes = await argon.hash({ pass: pwd, salt: hexToBuf(saltHex), time: argTime, mem: argMem, parallelism: argParallel, hashLen: 32, type: argon.ArgonType.Argon2id });
          const endA = performance.now();
          const argonSec = (endA - startA) / 1000;
          argonStatus.textContent = `Argon2 computed in ${argonSec.toFixed(2)}s`;
          out.innerHTML += `<p><strong>Local Argon2 (encoded):</strong> <pre>${argRes.encoded || ''}</pre></p>`;
          out.innerHTML += `<p><strong>Local Argon2 (hex):</strong> <pre>${argRes.hashHex || (argRes.hash ? bufToHex(argRes.hash) : '')}</pre></p>`;
          const guessesArgon = Math.pow(2, estimateEntropyBits(pwd) || 1);
          const timeSecArgon = guessesArgon * argonSec;
          out.innerHTML += `<p><strong>Estimated crack time (using Argon2 per-guess cost):</strong> ${prettyTimeSeconds(timeSecArgon)}</p>`;
          updateCharts(timeSecArgon, new Set(unsaltedList).size, new Set(saltedList.map(s=>s.salted_sha)).size);
        }

        // bcrypt branch
        if (useBcryptLocal && useBcryptLocal.checked) {
          try {
            kdfStatus.textContent = 'Loading bcrypt...';
            const bcrypt = await loadBcrypt();
            kdfStatus.textContent = 'Computing bcrypt...';
            const rounds = Math.max(4, Math.min(15, parseInt(bcryptRounds.value || '10', 10)));
            const startB = performance.now();
            const hashed = await new Promise((resolve, reject) => {
              bcrypt.hash(pwd, rounds, (err, hash) => { if (err) reject(err); else resolve(hash); });
            });
            const endB = performance.now();
            const bcryptSec = (endB - startB) / 1000;
            kdfStatus.textContent = `bcrypt computed in ${bcryptSec.toFixed(2)}s (rounds=${rounds})`;
            out.innerHTML += `<p><strong>Local bcrypt:</strong> <pre>${hashed}</pre></p>`;
            const guessesBcrypt = Math.pow(2, estimateEntropyBits(pwd) || 1);
            out.innerHTML += `<p><strong>Estimated crack time (bcrypt per-guess cost):</strong> ${prettyTimeSeconds(guessesBcrypt * bcryptSec)}</p>`;
            updateCharts(guessesBcrypt * bcryptSec, new Set(unsaltedList).size, new Set(saltedList.map(s=>s.salted_sha)).size);
          } catch (e) {
            kdfStatus.textContent = 'bcrypt failed: ' + e;
            out.innerHTML += `<p style="color:orange">bcrypt error: ${e}</p>`;
          }
        }

        // scrypt branch
        if (useScryptLocal && useScryptLocal.checked) {
          try {
            kdfStatus.textContent = 'Loading scrypt...';
            await loadScrypt();
            kdfStatus.textContent = 'Computing scrypt...';
            const N = Math.max(1024, parseInt(scryptN.value || '16384', 10));
            const r = Math.max(1, parseInt(scryptR.value || '8', 10));
            const p = Math.max(1, parseInt(scryptP.value || '1', 10));
            const startS = performance.now();
            const saltBuf = hexToBuf(saltHex);
            const dkLen = 32;
            const scryptAsync = window.scrypt;
            const derived = await new Promise((resolve, reject) => {
              try {
                scryptAsync(pwd, saltBuf, { N: N, r: r, p: p, dkLen: dkLen }, (derivedKey) => {
                  resolve(derivedKey);
                });
              } catch (err) { reject(err); }
            });
            const endS = performance.now();
            const scryptSec = (endS - startS) / 1000;
            kdfStatus.textContent = `scrypt computed in ${scryptSec.toFixed(2)}s (N=${N}, r=${r}, p=${p})`;
            let hex = '';
            if (derived && derived.length) {
              hex = bufToHex(derived instanceof Uint8Array ? derived : new Uint8Array(derived));
            }
            out.innerHTML += `<p><strong>Local scrypt (hex):</strong> <pre>${hex}</pre></p>`;
            const guessesScrypt = Math.pow(2, estimateEntropyBits(pwd) || 1);
            out.innerHTML += `<p><strong>Estimated crack time (scrypt per-guess cost):</strong> ${prettyTimeSeconds(guessesScrypt * scryptSec)}</p>`;
            updateCharts(guessesScrypt * scryptSec, new Set(unsaltedList).size, new Set(saltedList.map(s=>s.salted_sha)).size);
          } catch (e) {
            kdfStatus.textContent = 'scrypt failed: ' + e;
            out.innerHTML += `<p style="color:orange">scrypt error: ${e}</p>`;
          }
        }

        // show result with animation
        out.classList.add('fade-in');
      } catch (e) {
        out.innerHTML += `<p style="color:orange">KDF computation failed: ${e}</p>`;
      }
    } else {
      // fallback: show server Argon2 if local-only is disabled
      if (!localOnly.checked) {
        try {
          const res = await fetch('/api/hash', {
            method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ passwords: [pwd] })
          });
          const j = await res.json();
          const a = j[0].argon2_hash;
          out.innerHTML += `<p><strong>Server Argon2 (server-side):</strong> <pre>${a}</pre></p>`;
        } catch (e) {
          out.innerHTML += `<p style="color:orange">Failed to fetch server Argon2: ${e}</p>`;
        }
      } else {
        out.innerHTML += `<p><em>Local-only mode: no plaintext sent to server.</em></p>`;
      }
      updateCharts(timeSec, new Set(unsaltedList).size, new Set(saltedList.map(s=>s.salted_sha)).size);
    }
  } finally {
    demoBtn.disabled = false;
    demoBtn.classList.remove('is-loading');
  }

  try {
    demoResults.innerHTML = '';
    demoResults.appendChild(out);
  } catch (e) {
    console.error('Failed to display results:', e);
    demoResults.style.display = 'block';
    demoResults.innerText = 'Error displaying results: ' + e;
  }
}

// Hook demo button
demoBtn.addEventListener('click', (e) => { e.preventDefault(); runDemo(); });

// Export button
const exportBtn = document.getElementById('exportBtn');
exportBtn.addEventListener('click', (e) => {
  e.preventDefault();
  exportDemoData();
});

// CSV export & PNG download
const exportCsvBtn = document.getElementById('exportCsvBtn');
const downloadPngBtn = document.getElementById('downloadPngBtn');
exportCsvBtn.addEventListener('click', (e) => { e.preventDefault(); exportChartsCSV(); });
downloadPngBtn.addEventListener('click', (e) => { e.preventDefault(); downloadChartsPNG(); });

function exportChartsCSV() {
  try {
    const rows = [];
    // crack chart
    if (crackChart) {
      rows.push(['Crack time labels', ...crackChart.data.labels]);
      crackChart.data.datasets.forEach(ds => rows.push([ds.label, ...ds.data]));
      rows.push([]);
    }
    // collision chart
    if (collisionChart) {
      rows.push(['Collision labels', ...collisionChart.data.labels]);
      collisionChart.data.datasets.forEach(ds => rows.push([ds.label, ...ds.data]));
    }
    const csv = rows.map(r => r.map(v => `"${String(v).replace(/"/g,'""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salt-demo-charts-${(new Date()).toISOString()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert('CSV export failed: ' + e);
  }
}

function downloadChartsPNG() {
  try {
    // Download each chart separately
    const charts = [ {el: document.getElementById('crackTimeChart'), name: 'crack-time'}, {el: document.getElementById('collisionChart'), name: 'collision'} ];
    charts.forEach(c => {
      const dataUrl = c.el.toDataURL && c.el.toDataURL('image/png');
      if (dataUrl) {
        const a = document.createElement('a');
        a.href = dataUrl;
        a.download = `salt-demo-${c.name}-${(new Date()).toISOString()}.png`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    });
  } catch (e) {
    alert('PNG export failed: ' + e);
  }
}

// Modal wiring
const confirmModal = document.getElementById('confirmModal');
const modalText = document.getElementById('modalText');
const cancelModal = document.getElementById('cancelModal');
const confirmModalBtn = document.getElementById('confirmModalBtn');
let _modalResolve = null;

cancelModal.addEventListener('click', () => {
  confirmModal.style.display = 'none';
  if (_modalResolve) _modalResolve(false);
});
confirmModalBtn.addEventListener('click', () => {
  confirmModal.style.display = 'none';
  if (_modalResolve) _modalResolve(true);
});

async function showConfirmModal(text) {
  modalText.textContent = text;
  confirmModal.style.display = 'flex';
  return await new Promise((resolve) => { _modalResolve = resolve; });
}

// Export logic
function exportDemoData() {
  try {
    // Collect demo output: read from DOM and charts
    const out = {
      timestamp: new Date().toISOString(),
      password: passwordInput.value,
      strength: document.getElementById('strengthValue').textContent,
      charts: {
        crack: crackChart ? { data: crackChart.data.datasets[0].data, labels: crackChart.data.labels } : null,
        collision: collisionChart ? { data: collisionChart.data.datasets[0].data, labels: collisionChart.data.labels } : null
      },
      resultsHTML: demoResults.innerHTML
    };
    const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `salt-demo-${(new Date()).toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert('Export failed: ' + e);
  }
}

// Charts
let crackChart = null;
let collisionChart = null;

function initCharts() {
  const c1 = document.getElementById('crackTimeChart').getContext('2d');
  crackChart = new Chart(c1, {
    type: 'bar',
    data: {
      labels: ['Crack time (s @1e9 guesses/s)'],
      datasets: [{ label: 'Seconds', data: [1], backgroundColor: ['#4e79a7'] }]
    },
    options: {
      scales: {
        y: { type: 'logarithmic', beginAtZero: false, title: { display: true, text: 'Seconds (log scale)' } }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const sec = ctx.raw;
              return `${prettyTimeSeconds(sec)} (${sec.toExponential(2)} s)`;
            }
          }
        }
      }
    }
  });

  const c2 = document.getElementById('collisionChart').getContext('2d');
  collisionChart = new Chart(c2, {
    type: 'bar',
    data: {
      labels: ['Unsalted', 'Salted'],
      datasets: [{ label: 'Unique hashes among simulated users', data: [1,1], backgroundColor: ['#e15759','#59a14f'] }]
    },
    options: {
      indexAxis: 'y',
      scales: { x: { beginAtZero: true, precision: 0 } }
    }
  });
}

function updateCharts(crackSec, uniqueUnsalted, uniqueSalted) {
  if (!crackChart || !collisionChart) initCharts();
  // guard tiny values
  const secVal = Math.max(1e-6, crackSec);
  crackChart.data.datasets[0].data = [secVal];
  crackChart.update();

  collisionChart.data.datasets[0].data = [uniqueUnsalted, uniqueSalted];
  collisionChart.update();
}

// Rainbow-table simulator: load common passwords and precompute unsalted map
async function loadCommonPasswords() {
  try {
    const res = await fetch('/data/common_passwords.txt');
    if (!res.ok) throw new Error('Failed to load common passwords');
    const txt = await res.text();
    commonPasswords = txt.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
    // Precompute unsalted sha256 map
    rainbowMap.clear();
    for (const pw of commonPasswords) {
      // Fire-and-forget: compute sha256 but don't block UI
      sha256Hex(pw).then(h => rainbowMap.set(h, pw)).catch(e => console.error('sha err', e));
    }
    console.info('Loaded common passwords:', commonPasswords.length);
  } catch (e) {
    console.warn('Could not load common passwords:', e);
    commonPasswords = [];
  }
}

function initRainbowChart() {
  const el = document.getElementById('rainbowChart');
  if (!el) return;
  const ctx = el.getContext('2d');
  rainbowChart = new Chart(ctx, {
    type: 'bar',
    data: { labels: ['Cracked users'], datasets: [ { label: 'Unsalted (instant)', data: [0], backgroundColor: ['#e15759'] }, { label: 'Salted (needs per-salt brute)', data: [0], backgroundColor: ['#59a14f'] } ] },
    options: { indexAxis: 'y', scales: { x: { beginAtZero: true } } }
  });
}

async function runRainbowSimulator() {
  const btn = document.getElementById('rainbowBtn');
  const users = Math.max(1, parseInt(document.getElementById('rainbowUsers').value || '100', 10));
  const usePre = !!document.getElementById('rainbowUsePrecomputed').checked;
  const out = document.getElementById('rainbowResults');
  btn.disabled = true;
  try {
    out.innerHTML = '<em>Running rainbow-table simulation...</em>';
    // ensure rainbowMap loaded
    if (usePre && rainbowMap.size === 0) {
      await loadCommonPasswords();
      // small wait for pending hashes
      await new Promise(r => setTimeout(r, 100));
    }

    // Simulate: for each common password, assume `users` users share it
    // Unsalted: attacker with precomputed table can instantly map unsalted hash -> password
    // Salted: per-user salt prevents direct table lookup; attacker would need per-salt brute force

    const totalPasswords = commonPasswords.length || sampleRainbow.length;
    const totalUsers = totalPasswords * users;

    // Count instantly cracked users under unsalted storage: any password present in rainbowMap
    let crackedUnsaltedUsers = 0;
    let crackedSaltedUsers = 0; // expected to be 0 for precomputed-only attacker

    const tableMap = usePre ? rainbowMap : new Map();
    const pwList = commonPasswords.length ? commonPasswords : sampleRainbow;

    for (const pw of pwList) {
      const h = await sha256Hex(pw);
      if (tableMap.has(h)) {
        crackedUnsaltedUsers += users; // all users with this password would be cracked via rainbow table
      }
      // salted: assume attacker has no per-salt table; so none cracked instantly
    }

    // Update UI
    out.innerHTML = `<p>Total simulated users: <strong>${totalUsers}</strong></p>
      <p><strong style="color:red">Unsalted (instant cracks):</strong> ${crackedUnsaltedUsers}</p>
      <p><strong style="color:green">Salted (instant cracks using precomputed table):</strong> ${crackedSaltedUsers}</p>
      <p><small>${usePre ? 'Using precomputed list of common passwords.' : 'Not using precomputed table (no instant cracks).'}</small></p>`;

    if (!rainbowChart) initRainbowChart();
    rainbowChart.data.datasets[0].data = [crackedUnsaltedUsers];
    rainbowChart.data.datasets[1].data = [crackedSaltedUsers];
    rainbowChart.update();
  } catch (e) {
    out.innerHTML = `<p style="color:orange">Simulation failed: ${e}</p>`;
  } finally {
    btn.disabled = false;
  }
}

// Wire simulator button
const rainbowBtn = document.getElementById('rainbowBtn');
if (rainbowBtn) rainbowBtn.addEventListener('click', (e) => { e.preventDefault(); runRainbowSimulator(); });

// Load common passwords on startup
loadCommonPasswords();

// Also wire in a quick 'paste-list' capability if present (maintain backwards compatibility)
const oldForm = document.getElementById('hashForm');
if (oldForm) {
  oldForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const textarea = document.getElementById('pwlist');
    const passwords = textarea.value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
    if (!passwords.length) return;
    const res = await fetch('/api/hash', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ passwords })
    });
    const data = await res.json();
    resultsDiv.innerHTML = '';

    const table = document.createElement('table');
    const thead = document.createElement('thead');
    thead.innerHTML = '<tr><th>Password</th><th>Unsalted SHA256</th><th>Salt (hex)</th><th>Salted SHA256</th><th>Argon2</th></tr>';
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    data.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><code>${row.password}</code></td>
        <td><pre>${row.unsalted_sha256}</pre></td>
        <td><pre>${row.salted.salt_hex}</pre></td>
        <td><pre>${row.salted.salted_sha256}</pre></td>
        <td><pre>${row.argon2_hash}</pre></td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    resultsDiv.appendChild(table);
  });
}

// Init
updateStrength();