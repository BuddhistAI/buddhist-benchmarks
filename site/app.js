// Overview cards: switch the ranking between the mean and each model.
document.querySelectorAll('.lb-card .tabs').forEach((tabs) => {
  tabs.addEventListener('click', (ev) => {
    const b = ev.target.closest('button');
    if (!b) return;
    const lists = tabs.parentElement.querySelectorAll('ol.rank');
    tabs.querySelectorAll('button').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
    lists.forEach((l, i) => { l.hidden = String(i) !== b.dataset.i; });
  });
});

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
  const shortModel = (m) => D.models[m].name.replace('Claude ', '');
  const allModels = Object.keys(D.models).sort(byTier);

  const state = { version: D.versions[0], split: 'all', view: allModels.length > 1 ? 'mean' : allModels[0], reference: true };
  const KEY = 'lb:' + D.task.id + ':' + D.language;
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (saved.split) state.split = saved.split;
    if (saved.view && (saved.view === 'mean' || D.models[saved.view])) state.view = saved.view;
    if (typeof saved.reference === 'boolean') state.reference = saved.reference;
  } catch (e) { /* storage unavailable */ }
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify({ split: state.split, view: state.view, reference: state.reference })); } catch (e) { /* ignore */ }
  };

  const splits = Object.keys(D.rows[0].scores).sort((a, b) => (a === 'all' ? -1 : b === 'all' ? 1 : 0));
  if (!splits.includes(state.split)) state.split = 'all';
  const views = (allModels.length > 1 ? [['mean', 'Mean of models']] : []).concat(allModels.map((m) => [m, D.models[m].name]));

  function tabs(id, items, current, onpick) {
    const el = $(id);
    el.innerHTML = items.map(([k, label]) => `<button role="tab" data-k="${esc(k)}" aria-selected="${k === current}">${esc(label)}</button>`).join('');
    el.onclick = (ev) => {
      const b = ev.target.closest('button');
      if (!b) return;
      el.querySelectorAll('button').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
      onpick(b.dataset.k);
    };
  }
  tabs('t-view', views, state.view, (k) => { state.view = k; save(); render(); });
  tabs('t-split', splits.map((s) => [s, splitName(s)]), state.split, (k) => { state.split = k; save(); render(); });
  if (D.versions.length > 1) {
    $('f-version-wrap').hidden = false;
    $('f-version').innerHTML = D.versions.map((v) => `<option value="${esc(v)}">${esc(D.benchmarks[v].name)}</option>`).join('');
    $('f-version').onchange = (ev) => { state.version = ev.target.value; render(); };
  }
  $('f-reference').checked = state.reference;
  $('f-reference').onchange = (ev) => { state.reference = ev.target.checked; save(); render(); };

  const skill = (v) => D.skills[v] || {};
  const nameOf = (v) => skill(v).name || v;
  const idNote = (v) => (skill(v).name ? ` <span class="code small">${esc(v)}</span>` : '');
  const badge = (v) => {
    const st = skill(v).status;
    return st ? `<span class="badge ${esc(st)}">${st === 'promoted' ? 'best skill' : esc(st)}</span>` : '';
  };
  const cost = (c) => (c == null ? '<span class="muted">not recorded</span>' : '$' + c.toFixed(2));
  const pm = (m) => (m && m.runs && m.runs.length > 1 ? `± ${m.std.toFixed(3)}` : '');
  const fmt = (m) => (m ? m.mean.toFixed(3) + (pm(m) ? `<div class="sub">${pm(m)}</div>` : '') : '–');

  function renderBenchmark() {
    const b = D.benchmarks[state.version];
    const subsets = Object.entries(b.subsets).map(([k, n]) => `${n} ${esc(splitName(k).toLowerCase())}`).join(', ');
    $('benchmark').innerHTML = `<p class="kicker">Benchmark</p><h2><a href="${esc(b.url)}">${esc(b.name)}</a></h2>
<p>${b.purpose ? esc(b.purpose) : ''}</p>
<dl class="facts">
<div><dt>Data set</dt><dd><a href="${esc(b.url)}"><code>${esc(b.folder)}</code></a></dd></div>
<div><dt>Version</dt><dd>${esc(b.version)} <span class="muted">(tag <code>${esc(b.tag)}</code>)</span></dd></div>
<div><dt>Items</dt><dd>${b.items != null ? esc(b.items) : '–'}${subsets ? ` <span class="muted">(${subsets})</span>` : ''}</dd></div>
<div><dt>Scorer</dt><dd>${esc(b.scorer_version.join(', '))}, headline <code>${esc(HL)}</code></dd></div>
</dl>${b.note ? `<p class="sub">${esc(b.note)}</p>` : ''}`;
  }

  function render() {
    renderBenchmark();
    const rows = D.rows.filter((r) => r.data_version === state.version && (state.reference || skill(r.variant).status !== 'reference'));
    const models = [...new Set(rows.map((r) => r.model))].sort(byTier);
    const get = (v, m) => rows.find((r) => r.variant === v && r.model === m);
    const sc = (r, split = state.split) => (r && r.scores[split] && r.scores[split][HL]) || null;
    const variants = [...new Set(rows.map((r) => r.variant))];
    const score = (v) => {
      if (state.view === 'mean') {
        const xs = models.map((m) => sc(get(v, m))).filter(Boolean).map((x) => x.mean);
        return xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;
      }
      const x = sc(get(v, state.view));
      return x ? x.mean : null;
    };
    const BASE = D.baseline;
    const list = variants.map((v) => ({ v, s: score(v) })).filter((x) => x.s != null)
      .sort((a, b) => (a.v === BASE) - (b.v === BASE) || b.s - a.s);
    const baseScore = (list.find((x) => x.v === BASE) || {}).s;
    const gain = (v, x) => (v === BASE ? '<span class="gain">before</span>' : baseScore == null ? '–'
      : `<span class="gain ${x - baseScore >= 0 ? 'up' : 'down'}">${(x - baseScore >= 0 ? '+' : '') + (x - baseScore).toFixed(3)}</span>`);
    const lo = Math.min(...list.map((x) => x.s)) - 0.05, hi = Math.max(...list.map((x) => x.s));
    const width = (x) => (hi === lo ? 100 : 12 + 88 * (x - lo) / (hi - lo));

    const mean = state.view === 'mean';
    let h = '<thead><tr><th class="num">Rank</th><th>Skill</th><th>' + esc(metricName(HL)) + `<div class="sub">${esc(splitName(state.split))}${mean ? ', mean of models' : ''}</div></th>` + (BASE ? '<th class="num">Gain<div class="sub">vs. no skill</div></th>' : '');
    h += mean ? models.map((m) => `<th class="num">${esc(shortModel(m))}</th>`).join('')
      : '<th class="num">Std. dev.</th>' + Object.keys(rows[0].scores.all).filter((k) => k !== HL).map((k) => `<th class="num">${esc(metricName(k))}<div class="sub">All</div></th>`).join('') + '<th class="num">Repeats</th><th>Run</th>';
    h += '<th>Made by</th></tr></thead><tbody>';
    let rank = 0;
    list.forEach(({ v, s }) => {
      const isBase = v === BASE;
      const ref = skill(v).status === 'reference' || isBase;
      if (!ref) rank += 1;
      const any = rows.find((r) => r.variant === v);
      const r = mean ? null : get(v, state.view);
      h += `<tr class="${isBase ? 'base' : ref ? 'ref' : 'r' + (rank <= 3 ? rank : '')}">
<td class="num"><span class="pos" title="${ref ? 'Reference run: not ranked, it can\'t ship as this task\'s skill' : ''}">${ref ? '–' : rank}</span></td>
<td><a class="skill" href="${esc(skill(v).skill_md || '#skill-' + v)}" title="Open the skill as tested">${esc(nameOf(v))}</a> <span class="muted">${esc(any.skill_version)}</span>${badge(v)} <a class="open" href="#skill-${esc(v)}" title="About this skill">ⓘ</a></td>
<td class="scorecell"><span class="big">${s.toFixed(3)}</span><span class="bar"><i style="width:${width(s).toFixed(0)}%"></i></span></td>` + (BASE ? `<td class="num">${gain(v, s)}</td>` : '');
      h += mean ? models.map((m) => `<td class="num">${sc(get(v, m)) ? sc(get(v, m)).mean.toFixed(3) : '–'}</td>`).join('')
        : `<td class="num muted nowrap">${pm(sc(r)) || '–'}</td>` + Object.keys(r.scores.all).filter((k) => k !== HL).map((k) => `<td class="num">${r.scores[state.split] && r.scores[state.split][k] ? r.scores[state.split][k].mean.toFixed(3) : '–'}</td>`).join('') +
          `<td class="num">${esc(r.repeats)}</td><td><a href="${esc(r.run_url)}">run</a></td>`;
      h += `<td class="sub">${esc(skill(v).made_by || any.by || '')}</td></tr>`;
    });
    if (!list.length) h += '<tr><td colspan="9" class="muted">No runs match.</td></tr>';
    $('ranked').innerHTML = h + '</tbody>';
    $('ranked-caption').textContent = `${list.filter((x) => x.v !== BASE).length} skills on ${D.benchmarks[state.version].name}. Higher is better. ` +
      (mean ? `Each model's score is the mean over its runs; the ranking uses the mean of ${models.map(shortModel).join(' and ')}.` : `Mean over ${shortModel(state.view)}'s repeats.`) +
      ' Gain is the score minus the no-skill baseline (the "before" row) on the same models and passages. Reference runs are shown for comparison but not ranked.';

    // Every metric and run, per model
    let out = '';
    models.forEach((m) => {
      const mrows = rows.filter((r) => r.model === m).sort((a, b) => (sc(b, 'all') || { mean: -1 }).mean - (sc(a, 'all') || { mean: -1 }).mean);
      const metrics = Object.keys(mrows[0].scores.all);
      out += `<h3>${esc(D.models[m].name)} <span class="code">${esc(m)}</span></h3><div class="table-scroll"><table class="board"><thead><tr><th>Skill</th>` +
        splits.map((s) => `<th class="num">${esc(metricName(HL))}<div class="sub">${esc(splitName(s))}</div></th>`).join('') +
        metrics.filter((k) => k !== HL).map((k) => `<th class="num">${esc(metricName(k))}<div class="sub">All</div></th>`).join('') +
        '<th>Cost</th><th>Date</th><th>Skill ref</th><th>Run</th></tr></thead><tbody>';
      mrows.forEach((r) => {
        out += `<tr><td><strong>${esc(nameOf(r.variant))}</strong> <span class="muted">${esc(r.skill_version)}</span>${idNote(r.variant)}</td>` +
          splits.map((s) => `<td class="num">${fmt(r.scores[s] && r.scores[s][HL])}</td>`).join('') +
          metrics.filter((k) => k !== HL).map((k) => `<td class="num">${fmt(r.scores.all[k])}</td>`).join('') +
          `<td>${cost(r.cost_usd)}</td><td class="nowrap">${esc(r.date)}</td><td><code class="small">${esc(r.skill_ref)}</code></td><td><a href="${esc(r.run_url)}">run</a></td></tr>`;
      });
      out += '</tbody></table></div>';
    });
    $('per-model').innerHTML = out;
  }

  // Skill cards (static)
  const order = { promoted: 0, challenger: 1, reference: 2, baseline: 3 };
  $('skills').innerHTML = Object.entries(D.skills).filter(([, s]) => !s.hidden).sort((a, b) => (order[a[1].status] ?? 9) - (order[b[1].status] ?? 9)).map(([v, s]) => {
    const versions = [...new Set(D.rows.filter((r) => r.variant === v).map((r) => r.skill_version))].join(', ');
    return `<div class="card" id="skill-${esc(v)}"><h3>${esc(nameOf(v))} <span class="muted">${esc(versions)}</span>${badge(v)}</h3>${skill(v).name ? `<p class="sub">Variant <code>${esc(v)}</code></p>` : ''}
<p>${esc(s.approach || '')}</p>
<p class="sub">${s.ships ? 'Can ship as this task\'s skill.' : 'Can\'t ship as it is; shown for comparison.'}${s.made_by ? ' Made by ' + esc(s.made_by) + '.' : ''}</p>
<p class="small">${s.skill_md ? `<a class="btn" href="${esc(s.skill_md)}">Open SKILL.md</a> ` : ''}${s.source ? `<a href="${esc(s.source)}">Folder at the tested commit</a>` : ''}${D.promoted && D.promoted.variant === v ? ` · <a href="${esc(D.promoted.skill)}">Installed version</a>` : ''}</p></div>`;
  }).join('');

  $('splits').innerHTML = Object.entries(D.splits).map(([s, d]) => `<dt>${esc(splitName(s))}</dt><dd>${esc(d)}</dd>`).join('');
  render();
})();
