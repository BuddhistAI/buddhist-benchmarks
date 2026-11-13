// Renders a task page from the JSON embedded in it (built by scripts/build_leaderboards.py).
(function () {
  const node = document.getElementById('data');
  if (!node) return;
  const D = JSON.parse(node.textContent);
  const HL = D.headline;
  const SPLITS = { all: 'All', 'same-book': 'Same book', 'held-out-book': 'Held-out book' };
  const splitName = (s) => SPLITS[s] || s.replace(/-/g, ' ');
  const byTier = (a, b) => D.models[a].tier - D.models[b].tier;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = (id) => document.getElementById(id);
  const metricName = (k) => k.replace(/_/g, ' ');

  const state = { version: D.versions[0], split: 'all', models: new Set(Object.keys(D.models)), reference: true };
  try {
    const saved = JSON.parse(localStorage.getItem('lb:' + D.task.id + ':' + D.language) || '{}');
    if (saved.split) state.split = saved.split;
    if (typeof saved.reference === 'boolean') state.reference = saved.reference;
  } catch (e) { /* storage unavailable */ }
  const save = () => {
    try { localStorage.setItem('lb:' + D.task.id + ':' + D.language, JSON.stringify({ split: state.split, reference: state.reference })); } catch (e) { /* ignore */ }
  };

  // Controls
  $('f-version').innerHTML = D.versions.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
  const splits = Object.keys(D.rows[0].scores).sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : 0));
  if (!splits.includes(state.split)) state.split = 'all';
  $('f-split').innerHTML = splits.map((s) => `<option value="${esc(s)}"${s === state.split ? ' selected' : ''}>${esc(splitName(s))}</option>`).join('');
  $('f-models').insertAdjacentHTML('beforeend', Object.keys(D.models).sort(byTier).map((m) =>
    `<label><input type="checkbox" value="${esc(m)}" checked> ${esc(D.models[m].name)}</label>`).join(''));
  $('f-reference').checked = state.reference;
  $('f-version').onchange = (ev) => { state.version = ev.target.value; render(); };
  $('f-split').onchange = (ev) => { state.split = ev.target.value; save(); render(); };
  $('f-reference').onchange = (ev) => { state.reference = ev.target.checked; save(); render(); };
  $('f-models').onchange = (ev) => {
    if (ev.target.checked) state.models.add(ev.target.value); else state.models.delete(ev.target.value);
    render();
  };

  const skill = (v) => D.skills[v] || {};
  const badge = (v) => {
    const st = skill(v).status;
    return st ? `<span class="badge ${esc(st)}">${esc(st)}</span>` : '';
  };
  const cell = (m, best) => {
    if (!m) return '<span class="muted">–</span>';
    const pct = Math.max(0, Math.min(100, m.mean * 100));
    return `<div class="score">${m.mean.toFixed(3)}${m.runs && m.runs.length > 1 ? ` <span class="pm">± ${m.std.toFixed(3)}</span>` : ''}</div><div class="bar"><i style="width:${pct}%"></i></div>`;
  };
  const cost = (c) => (c == null ? '<span class="muted">not recorded</span>' : '$' + c.toFixed(2));

  function visibleRows() {
    return D.rows.filter((r) => r.data_version === state.version && state.models.has(r.model) &&
      (state.reference || skill(r.variant).status !== 'reference'));
  }

  function render() {
    const rows = visibleRows();
    const models = [...new Set(rows.map((r) => r.model))].sort(byTier);
    const variants = [...new Set(rows.map((r) => r.variant))];
    const get = (v, m) => rows.find((r) => r.variant === v && r.model === m);
    const val = (r) => (r && r.scores[state.split] && r.scores[state.split][HL] ? r.scores[state.split][HL].mean : null);
    const avg = (v) => {
      const xs = models.map((m) => val(get(v, m))).filter((x) => x != null);
      return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : -1;
    };
    variants.sort((a, b) => avg(b) - avg(a));
    const bestPer = {};
    models.forEach((m) => { bestPer[m] = Math.max(...variants.map((v) => val(get(v, m)) ?? -1)); });

    // Matrix
    $('matrix-caption').textContent = `${metricName(HL)} on the ${splitName(state.split).toLowerCase()} split, data ${state.version}. Mean ± standard deviation over each run's repeats; best per model in green. Sorted by the mean over the models shown.`;
    let h = '<thead><tr><th>Skill</th>' + models.map((m) => `<th>${esc(D.models[m].name)}</th>`).join('') +
      (models.length > 1 ? '<th class="num">Mean</th>' : '') + '</tr></thead><tbody>';
    if (!variants.length) h += `<tr><td colspan="${models.length + 2}" class="muted">No runs match these filters.</td></tr>`;
    variants.forEach((v) => {
      const any = rows.find((r) => r.variant === v);
      h += `<tr><td><strong>${esc(v)}</strong> <span class="muted">${esc(any.skill_version)}</span>${badge(v)}</td>`;
      models.forEach((m) => {
        const r = get(v, m);
        const x = val(r);
        h += `<td class="cell${x != null && x === bestPer[m] ? ' best' : ''}">${cell(r && r.scores[state.split] && r.scores[state.split][HL], false)}</td>`;
      });
      if (models.length > 1) h += `<td class="num">${avg(v) >= 0 ? avg(v).toFixed(3) : '–'}</td>`;
      h += '</tr>';
    });
    $('matrix').innerHTML = h + '</tbody>';

    // Per-model tables
    let pm = '';
    models.forEach((m) => {
      const mrows = rows.filter((r) => r.model === m).sort((a, b) => (val(b) ?? -1) - (val(a) ?? -1));
      const metrics = Object.keys(mrows[0].scores.all);
      pm += `<div class="permodel"><h3>${esc(D.models[m].name)} <span class="code">${esc(m)}</span></h3><div class="table-scroll"><table class="board"><thead><tr><th class="num">Rank</th><th>Skill</th>` +
        splits.map((s) => `<th class="num">${esc(metricName(HL))}<div class="sub">${esc(splitName(s))}</div></th>`).join('') +
        metrics.filter((k) => k !== HL).map((k) => `<th class="num">${esc(metricName(k))}<div class="sub">All</div></th>`).join('') +
        '<th>Cost</th><th>Repeats</th><th>Date</th><th>Run</th></tr></thead><tbody>';
      mrows.forEach((r, i) => {
        pm += `<tr><td class="num">${i + 1}</td><td><strong>${esc(r.variant)}</strong> <span class="muted">${esc(r.skill_version)}</span>${badge(r.variant)}<div class="sub"><code>${esc(r.skill_ref)}</code></div></td>` +
          splits.map((s) => `<td class="num">${r.scores[s] && r.scores[s][HL] ? fmt(r.scores[s][HL]) : '–'}</td>`).join('') +
          metrics.filter((k) => k !== HL).map((k) => `<td class="num">${fmt(r.scores.all[k])}</td>`).join('') +
          `<td>${cost(r.cost_usd)}</td><td class="num">${esc(r.repeats)}</td><td class="nowrap">${esc(r.date)}</td><td><a href="${esc(r.run_url)}">run</a></td></tr>`;
      });
      pm += '</tbody></table></div></div>';
    });
    $('per-model').innerHTML = pm || '<p class="muted">No runs match these filters.</p>';
  }
  const fmt = (m) => m.mean.toFixed(3) + (m.runs && m.runs.length > 1 ? `<div class="sub">± ${m.std.toFixed(3)}</div>` : '');

  // Skill cards (static)
  const order = { promoted: 0, challenger: 1, baseline: 2, reference: 3 };
  $('skills').innerHTML = Object.entries(D.skills).sort((a, b) => (order[a[1].status] ?? 9) - (order[b[1].status] ?? 9)).map(([v, s]) => {
    const versions = [...new Set(D.rows.filter((r) => r.variant === v).map((r) => r.skill_version))].join(', ');
    return `<div class="card"><h3>${esc(v)} <span class="muted">${esc(versions)}</span>${badge(v)}</h3>
<p>${esc(s.approach || '')}</p>
<p class="sub">${s.ships ? 'Can ship as this task\'s skill.' : 'Can\'t ship as it is; shown for comparison.'}${s.made_by ? ' Made by ' + esc(s.made_by) + '.' : ''}</p>
<p class="small">${s.source ? `<a href="${esc(s.source)}">Source at the tested commit</a>` : ''}${D.promoted && D.promoted.variant === v ? ` · <a href="${esc(D.promoted.skill)}">Installed version</a>` : ''}</p></div>`;
  }).join('');

  $('splits').innerHTML = Object.entries(D.splits).map(([s, d]) => `<dt>${esc(splitName(s))}</dt><dd>${esc(d)}</dd>`).join('');
  render();
})();
