#!/usr/bin/env python3
"""CIVID HTML dashboard generator (standard-library only).

Reads exports/ and writes exports/civid_dashboard.html: a single, self-contained
dashboard (Chart.js + Leaflet from CDN) with:
  - filters: country / phase / date / role / age group / verification status
  - summary cards (totals + aggregate counts: killed, children, women, doctors,
    journalists, commanders, arrests/detentions)
  - charts: timeline, verification, role breakdown, news metrics
  - a map (Leaflet) using any lat/lon present in events (optional)
  - famous personalities gallery (images + bios) -- empty until populated
  - news section with authentic source-linked stories
  - responsive layout (desktop + mobile)

No data is fabricated: every number links to exports/ (and therefore to sources.csv).
Run:  python scripts/generate_html_dashboard.py
"""
from __future__ import annotations
import csv
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS = os.path.join(REPO, "exports")
OUT = os.path.join(EXPORTS, "civid_dashboard.html")


def load_csv(name):
    path = os.path.join(EXPORTS, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [ {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                 for row in csv.DictReader(fh) ]


def j(val):
    # safe JSON-embed for JS
    return json.dumps(val, ensure_ascii=False)


def main():
    events = load_csv("civid_events_all.csv")
    persons = load_csv("civid_persons_all.csv")
    famous = load_csv("civid_famous_victims_all.csv")
    news = load_csv("civid_news_intelligence_all.csv")
    leaders = load_csv("civid_leaders_all.csv")
    dmeta = load_csv("civid_dashboard_metadata_all.csv")
    # index metadata by phase for quick lookup
    meta_by_phase = {}
    for d in dmeta:
        ph = d.get("phase") or "_global"
        meta_by_phase.setdefault(ph, {})[d.get("meta_key")] = d.get("meta_value")
    agg = {}
    apath = os.path.join(EXPORTS, "news_aggregates.json")
    if os.path.exists(apath):
        agg = json.load(open(apath, encoding="utf-8"))

    summary = {}
    spath = os.path.join(EXPORTS, "summary.json")
    if os.path.exists(spath):
        summary = json.load(open(spath, encoding="utf-8")).get("totals", {})

    # ---- derive chart data ----
    by_phase = {}
    for e in events:
        by_phase[e.get("phase", "?")] = by_phase.get(e.get("phase", "?"), 0) + 1
    by_verif = {}
    for e in events:
        by_verif[e.get("verification_status", "?")] = by_verif.get(e.get("verification_status", "?"), 0) + 1
    by_role = {}
    for p in persons:
        r = p.get("victim_role") or "unknown"
        by_role[r] = by_role.get(r, 0) + 1

    news_stories = [n for n in news if (n.get("news_headline") or "").strip()]
    metrics_rows = [n for n in news if (n.get("metric") or "").strip() and not (n.get("news_headline") or "").strip()]

    # timeline (events by month)
    by_month = {}
    for e in events:
        m = e.get("derived_month") or (e.get("event_date") or "")[:7]
        if m:
            by_month[m] = by_month.get(m, 0) + 1
    months = sorted(by_month.keys())
    month_counts = [by_month[m] for m in months]

    famous_cards = []
    for f in famous:
        famous_cards.append({
            "name": f.get("victim_name"),
            "role": f.get("victim_role"),
            "bio": f.get("summary_brief") or f.get("death_context") or "",
            "date": f.get("event_date"),
            "place": f.get("location"),
            "img": f.get("image_url"),
            "src": f.get("source_url"),
            "verified_by": f.get("verified_by"),
        })

    data_js = j({
        "events": events, "persons": persons, "famous": famous,
        "news": news_stories, "metrics": metrics_rows, "leaders": leaders,
        "by_phase": by_phase, "by_verif": by_verif, "by_role": by_role,
        "months": months, "month_counts": month_counts,
        "agg": agg, "summary": summary, "meta_by_phase": meta_by_phase,
    })

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>CIVID — Civilian Impact Verified Incident Dataset</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root{--bg:#0f1419;--card:#1a212b;--ink:#e6edf3;--muted:#9aa7b4;--accent:#4C72B0;--green:#55A868;--red:#C44E52;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink)}
  header{padding:18px 20px;border-bottom:1px solid #232c38;position:sticky;top:0;background:var(--bg);z-index:10}
  h1{margin:0;font-size:20px} .sub{color:var(--muted);font-size:13px}
  .wrap{padding:16px 20px;max-width:1200px;margin:0 auto}
  .filters{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
  .filters select,.filters input{padding:8px 10px;border-radius:8px;border:1px solid #2b3543;background:var(--card);color:var(--ink)}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:14px 0}
  .card{background:var(--card);border-radius:12px;padding:14px}
  .card .n{font-size:24px;font-weight:700}
  .card .l{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  @media(max-width:820px){.grid2{grid-template-columns:1fr}}
  .panel{background:var(--card);border-radius:12px;padding:14px;margin:12px 0}
  .panel h3{margin:0 0 10px;font-size:15px}
  .news-item{border-left:3px solid var(--accent);padding:8px 10px;margin:8px 0;background:#141b24;border-radius:6px}
  .news-item a{color:var(--accent);text-decoration:none}
  .famous{display:flex;gap:14px;flex-wrap:wrap}
  .fam{width:220px;background:#141b24;border-radius:10px;padding:10px}
  .fam img{width:100%;height:140px;object-fit:cover;border-radius:8px;background:#222}
  .fam .nm{font-weight:600;margin-top:6px}
  .fam .rl{color:var(--muted);font-size:12px}
  #map{height:320px;border-radius:12px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #232c38}
  .tag{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;background:#232c38;color:var(--muted)}
  footer{color:var(--muted);font-size:12px;padding:20px;text-align:center}
  .empty{color:var(--muted);font-style:italic}
</style>
</head>
<body>
<header>
  <h1>CIVID — Civilian Impact Verified Incident Dataset</h1>
  <div class="sub">Research & education only. Every figure links to a cited source. Verify against the primary source before publication.</div>
  <div class="sub" id="lastUpdated" style="margin-top:4px"></div>
</header>
<div class="wrap">
  <div class="filters">
    <select id="f-phase"><option value="">All phases</option></select>
    <select id="f-country"><option value="">All countries</option></select>
    <select id="f-verify"><option value="">All verification</option><option value="verified">verified</option><option value="estimated">estimated</option><option value="unverified">unverified</option><option value="disputed">disputed</option></select>
    <select id="f-role"><option value="">All roles</option></select>
    <select id="f-age"><option value="">All ages</option><option value="child">child</option><option value="adult">adult</option></select>
    <input id="f-date" type="date" placeholder="from date"/>
  </div>

  <div class="cards" id="cards"></div>

  <div class="grid2">
    <div class="panel"><h3>Events timeline (by month)</h3><canvas id="cTimeline"></canvas></div>
    <div class="panel"><h3>Verification status</h3><canvas id="cVerif"></canvas></div>
  </div>
  <div class="grid2">
    <div class="panel"><h3>Events by phase</h3><canvas id="cPhase"></canvas></div>
    <div class="panel"><h3>Victim roles (persons)</h3><canvas id="cRole"></canvas></div>
  </div>

  <div class="panel"><h3>Aggregate intelligence</h3><canvas id="cNews"></canvas>
    <div id="newsMetricsTable"></div>
  </div>

  <div class="panel"><h3>News & updates (source-linked)</h3><div id="newsList"></div></div>

  <div class="panel" id="famousPanel"><h3>Famous personalities / victims</h3><div class="famous" id="famousList"></div></div>

  <div class="panel"><h3>Verified leaders — confirmed deaths</h3><div class="sub" id="leaderRefresh" style="margin-bottom:8px"></div><div class="famous" id="leaderList"></div></div>

  <div class="panel" id="mapPanel" style="display:none"><h3>Map (where coordinates are available)</h3><div id="map"></div>
    <div class="sub" style="margin-top:8px">Location names are stored as text; add lat/lon to events to enable precise plotting.</div>
  </div>
</div>
<footer>CIVID — code MIT (© Muhammad Farhan); underlying data per each publisher. No victim imagery. No identifiable images of minors unless public, relevant, and ethically safe.</footer>

<script>
const DATA = __DATA__;
const fmt = n => (n==null?'0':String(n));
function fillSelect(sel, vals){ vals.forEach(v=>{ if(v){const o=document.createElement('option');o.value=v;o.textContent=v;sel.appendChild(o);} }); }
fillSelect(document.getElementById('f-phase'), Object.keys(DATA.by_phase));
fillSelect(document.getElementById('f-country'), [...new Set(DATA.events.map(e=>e.country).filter(Boolean))]);
fillSelect(document.getElementById('f-role'), Object.keys(DATA.by_role));

function summaryCards(){
  const s = DATA.summary||{}; const a = DATA.agg||{};
  const cards = [
    ['Events', fmt(s.events)],
    ['Verified', fmt(s.events_verified)],
    ['Needs review', fmt(s.needs_review)],
    ['Total killed', fmt(a.total_killed)],
    ['Children killed', fmt(a.children_killed)],
    ['Women killed', fmt(a.women_killed)],
    ['Doctors killed', fmt(a.doctors_killed)],
    ['Journalists killed', fmt(a.journalists_killed)],
    ['Commanders killed', fmt(a.commanders_killed)],
    ['Arrests', fmt(a.arrests)],
    ['Detentions', fmt(a.detentions)],
    ['Persons', fmt(s.persons)],
    ['Verified leaders (deaths)', fmt(s.leaders)],
  ];
  document.getElementById('cards').innerHTML = cards.map(c=>`<div class="card"><div class="n">${c[1]}</div><div class="l">${c[0]}</div></div>`).join('');
}

function filters(){
  const ph=document.getElementById('f-phase').value;
  const co=document.getElementById('f-country').value;
  const vf=document.getElementById('f-verify').value;
  const rl=document.getElementById('f-role').value;
  const ag=document.getElementById('f-age').value;
  const dt=document.getElementById('f-date').value;
  return DATA.events.filter(e=>{
    if(ph && e.phase!==ph) return false;
    if(co && e.country!==co) return false;
    if(vf && e.verification_status!==vf) return false;
    if(dt && (e.event_date||'') < dt) return false;
    return true;
  });
}

function drawCharts(){
  const evs = filters();
  const byPh={}, byVer={}, months={}, roles={};
  evs.forEach(e=>{ byPh[e.phase]=(byPh[e.phase]||0)+1; byVer[e.verification_status]=(byVer[e.verification_status]||0)+1;
    const m=e.derived_month||(e.event_date||'').slice(0,7); if(m) months[m]=(months[m]||0)+1; });
  DATA.persons.filter(p=>{ if(ag){const isChild=(p.child_flag==='true'||p.child_flag===true); if(ag==='child'&&!isChild)return false; if(ag==='adult'&&isChild)return false;} if(rl && p.victim_role!==rl) return false; return true;})
    .forEach(p=>{ const r=p.victim_role||'unknown'; roles[r]=(roles[r]||0)+1; });
  const ms=Object.keys(months).sort();
  new Chart(document.getElementById('cTimeline'),{type:'line',data:{labels:ms,datasets:[{label:'events',data:ms.map(m=>months[m]),borderColor:'#4C72B0',fill:false}]},options:{responsive:true}});
  new Chart(document.getElementById('cVerif'),{type:'doughnut',data:{labels:Object.keys(byVer),datasets:[{data:Object.values(byVer),backgroundColor:['#55A868','#DD8452','#C44E52','#8172B2']}]},options:{responsive:true}});
  new Chart(document.getElementById('cPhase'),{type:'bar',data:{labels:Object.keys(byPh),datasets:[{label:'events',data:Object.values(byPh),backgroundColor:'#64B5CD'}]},options:{responsive:true}});
  const rk=Object.keys(roles);
  new Chart(document.getElementById('cRole'),{type:'bar',data:{labels:rk,datasets:[{label:'persons',data:rk.map(r=>roles[r]),backgroundColor:'#8172B2'}]},options:{responsive:true}});
  const mk=DATA.metrics||[];
  new Chart(document.getElementById('cNews'),{type:'bar',data:{labels:mk.map(m=>m.metric),datasets:[{label:'value',data:mk.map(m=>m.value||0),backgroundColor:'#C44E52'}]},options:{responsive:true}});
  document.getElementById('newsMetricsTable').innerHTML = '<table><tr><th>Metric</th><th>Value</th><th>Category</th><th>Status</th></tr>'+
    mk.map(m=>`<tr><td>${m.metric}</td><td>${m.value||0}</td><td><span class="tag">${m.news_category||''}</span></td><td>${m.verification_status||''}</td></tr>`).join('')+'</table>';
}

function newsList(){
  const n=DATA.news||[];
  document.getElementById('newsList').innerHTML = n.length
    ? n.map(x=>`<div class="news-item"><b>${x.news_headline||'(untitled)'}</b> <span class="tag">${x.news_category||''}</span><br>${x.news_summary||''}<br>${x.news_source_url?`<a href="${x.news_source_url}" target="_blank" rel="noopener">source</a>`:''} <span class="sub">${x.news_date||''}</span></div>`).join('')
    : '<div class="empty">No curated news stories yet. Add source-linked rows to each phase\\'s news_intelligence.csv.</div>';
}

function famousList(){
  const f=DATA.famous||[];
  document.getElementById('famousList').innerHTML = f.length
    ? f.map(x=>`<div class="fam"><img src="${x.img||''}" alt="" onerror="this.style.display='none'"/><div class="nm">${x.name||'Unknown'}</div><div class="rl">${x.role||''}</div><div class="sub">${x.bio||''}</div>${x.src?`<a href="${x.src}" target="_blank" rel="noopener">source</a>`:''}</div>`).join('')
    : '<div class="empty">Famous-persons section is intentionally empty. Named individuals are added only via the verified, multi-source pipeline (docs/famous_victims_policy.md).</div>';
}

function leadersList(){
  const L=DATA.leaders||[];
  if(!L.length){ document.getElementById('leaderList').innerHTML='<div class="empty">No verified leader-death records yet.</div>'; return; }
  document.getElementById('leaderList').innerHTML = L.map(x=>{
    const img = (x.image_available==='true' && x.image_url)
      ? `<img src="${x.image_url}" alt="${x.leader_name}" style="width:100%;height:180px;object-fit:cover;border-radius:8px;background:#222" onerror="this.style.display='none'"/>`
      : '';
    return `<div class="fam" style="width:280px"><div>${img}</div><div class="nm">${x.leader_name||'Unknown'}</div><div class="rl">${x.organization||''} &middot; ${x.role||''}</div><div class="sub">${x.bio||''}</div><div class="sub" style="margin-top:6px">Died: ${x.death_date||'?'}${x.death_location?` — ${x.death_location}`:''} (${x.death_cause||''})<br>Verification: ${x.verification_status||''} / ${x.confidence_level||''}<br>${x.image_license?`Image: ${x.image_license} (${x.image_source||'Wikimedia Commons'})`:''}</div>${x.source_url?`<a href="${x.source_url}" target="_blank" rel="noopener">source</a>`:''}</div>`;
  }).join('');
}

function applyMeta(){
  const m = DATA.meta_by_phase || {};
  // global last_updated = latest across phases
  let latest = '';
  for (const ph in m){ const v = m[ph].last_updated; if (v && v > latest) latest = v; }
  if (latest) document.getElementById('lastUpdated').textContent = 'Data last updated: ' + latest + ' (UTC). Regenerate exports to refresh.';
  // map panel only when any phase enables it
  const showMap = Object.values(m).some(x => (x.show_map||'').toLowerCase() === 'true');
  document.getElementById('mapPanel').style.display = showMap ? '' : 'none';
  // famous panel always shown (renders empty-state if none)
  // auto-refresh: when served over http, re-fetch latest leaders JSON every 60s
  if (window.location.protocol.startsWith('http')) {
    const el = document.getElementById('leaderRefresh');
    if (el) el.textContent = 'Auto-refresh: on (updates every 60s when served).';
    setInterval(async () => {
      try {
        const r = await fetch('civid_leaders_all.json?t=' + Date.now(), {cache:'no-store'});
        if (r.ok) { DATA.leaders = await r.json(); leadersList(); }
      } catch(e) { /* offline / file:// — ignore */ }
    }, 60000);
  }
}

function initMap(){
  const map=document.getElementById('map');
  if(!map) return;
  try{ const Lmap=L.map(map).setView([31.5,34.5],5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap'}).addTo(Lmap);
  }catch(e){ map.innerHTML='<div class="empty">Map library unavailable offline.</div>'; }
}

['f-phase','f-country','f-verify','f-role','f-age','f-date'].forEach(id=>document.getElementById(id).addEventListener('change',drawCharts));
summaryCards(); applyMeta(); drawCharts(); newsList(); famousList(); leadersList(); initMap();
</script>
</body>
</html>
"""
    html = html.replace("__DATA__", data_js)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[ok] HTML dashboard written: {OUT} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
