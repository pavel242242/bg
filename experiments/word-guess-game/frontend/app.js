// Přihořívá hoří — frontend logic.

const API = "";  // same origin
let game = null; // { game_id, vocab_size, n_targets }
let history = []; // last server snapshot
let circles = null;
let solved = false;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

// ---- API helpers ----
async function api(path, body) {
  const res = await fetch(API + path, {
    method: body ? "POST" : "GET",
    headers: body ? { "content-type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status}: ${txt}`);
  }
  return res.json();
}

// ---- game lifecycle ----
async function newGame() {
  const model = $("#model-select").value;
  game = await api("/api/new-game", { model });
  history = [];
  circles = null;
  solved = false;
  $("#guess-list").innerHTML = "";
  $("#last-guess-card").classList.add("hidden");
  $("#status").textContent = "";
  $("#status").className = "status";
  const modelLabel = game.model === "simcse" ? "SimCSE (Seznam)" : "fastText cc.cs.300";
  $("#meta").textContent = `${modelLabel} · ${game.vocab_size} podstatných jmen · ${game.n_targets} cílů`;
  drawCircles({ target: [0, 0], guesses: [] });
  drawSky({ target: [0, 0], guesses: [], edges: [] });
  $("#guess-input").focus();
}

async function submitGuess(word) {
  if (!game) await newGame();
  let r;
  try {
    r = await api("/api/guess", { game_id: game.game_id, word });
  } catch (e) {
    flashStatus("Chyba serveru", "error");
    return;
  }
  if (!r.ok) {
    flashStatus(r.message || "Neznámé slovo", "error");
    return;
  }
  if (r.duplicate) {
    flashStatus(`„${r.guess.word}" už jsi tipoval`, "");
    return;
  }
  history = r.history;
  circles = r.circles;
  solved = r.solved;
  renderLastGuess(r.guess);
  renderList(history, r.guess);
  drawCircles(circles);
  // Refresh the sky on every guess so it never shows a stale state when the
  // user later switches to that tab.
  refreshSky();
  if (r.solved) {
    $("#status").textContent = `Uhodnuto! Slovo bylo "${r.target}". (${history.length} tipů)`;
    $("#status").className = "status win";
  } else {
    flashStatus(rankHint(r.guess.rank, r.guess.sim, r.guess.fallback));
  }
}

async function reveal() {
  if (!game) return;
  const r = await api("/api/reveal", { game_id: game.game_id, word: "x" });
  $("#status").textContent = `Slovo bylo "${r.target}". Zkus znovu!`;
  $("#status").className = "status win";
  solved = true;
}

function flashStatus(msg, cls = "") {
  $("#status").textContent = msg;
  $("#status").className = "status " + cls;
}

function rankHint(rank, sim, fallback) {
  if (fallback) return `Mimo hlavní slovník · SimCSE sim ${sim.toFixed(2)}`;
  if (rank == null) return `Mimo slovník (sim ${sim.toFixed(2)})`;
  if (rank <= 5) return `🔥 Hoří! (rank ${rank})`;
  if (rank <= 50) return `🌶️ Hoří (rank ${rank})`;
  if (rank <= 250) return `Přihořívá (rank ${rank})`;
  if (rank <= 1000) return `Vlažné (rank ${rank})`;
  if (rank <= 3000) return `Studí (rank ${rank})`;
  return `Mrzne (rank ${rank})`;
}

// ---- list view ----
function renderLastGuess(g) {
  const el = $("#last-guess-card");
  if (!g) {
    el.classList.add("hidden");
    return;
  }
  el.classList.remove("hidden");
  el.innerHTML = "";
  const total = (game && game.vocab_size) || 10000;

  const label = document.createElement("span");
  label.className = "label";
  label.textContent = "Tvůj tip";

  const word = document.createElement("span");
  word.className = "gword " + heatClass(g.rank, g.fallback);
  word.textContent = g.word;
  if (g.raw && g.raw.toLowerCase() !== g.word) {
    const raw = document.createElement("span");
    raw.className = "raw";
    raw.textContent = `(${g.raw})`;
    word.appendChild(raw);
  }
  if (g.fallback) {
    const tag = document.createElement("span");
    tag.className = "raw";
    tag.textContent = "· SimCSE";
    word.appendChild(tag);
  }

  const rank = document.createElement("span");
  rank.className = "grank";
  rank.textContent = g.fallback
    ? `sim ${g.sim.toFixed(2)}`
    : g.rank == null ? "mimo slovník" : `rank ${g.rank}`;

  const bar = document.createElement("span");
  bar.className = "gbar";
  const fill = document.createElement("span");
  fill.className = "gbar-fill";
  fill.style.width = barPct(g, total) + "%";
  fill.style.background = barColor(g);
  bar.appendChild(fill);

  el.append(label, word, rank, bar);
}

function heatClass(rank, fallback) {
  if (fallback) return "heat-fallback";
  if (rank == null) return "heat-5";
  if (rank <= 5) return "heat-1";
  if (rank <= 50) return "heat-2";
  if (rank <= 250) return "heat-3";
  if (rank <= 1000) return "heat-4";
  return "heat-5";
}

function barPct(g, total) {
  if (g.fallback) {
    // Map cosine sim 0..1 onto 0..100%; clamp negatives to 0.
    return Math.max(0, Math.min(1, g.sim)) * 100;
  }
  if (g.rank == null) return 0;
  const t = Math.max(1, Math.min(g.rank, total));
  return 100 * (1 - Math.log(t) / Math.log(total));
}

function barColor(g) {
  if (g.fallback) return "#7a85a3";
  return rankBarColor(g.rank);
}

function rankBarColor(rank) {
  if (rank == null) return "#4264c3";
  if (rank <= 5) return "#ff4f4f";
  if (rank <= 50) return "#ff7a3d";
  if (rank <= 250) return "#ffb84d";
  if (rank <= 1000) return "#ffe066";
  if (rank <= 3000) return "#6ec6ff";
  return "#4264c3";
}

function renderList(hist, fresh) {
  // Sort: ranked guesses first (best rank → worst), then fallback guesses
  // (highest sim first), then fully-unknown ones.
  const sortKey = (g) => {
    if (g.rank != null) return [0, g.rank];
    if (g.fallback) return [1, -g.sim];
    return [2, 0];
  };
  const sorted = [...hist].sort((a, b) => {
    const [ka, va] = sortKey(a);
    const [kb, vb] = sortKey(b);
    return ka - kb || va - vb;
  });
  const list = $("#guess-list");
  list.innerHTML = "";
  const total = (game && game.vocab_size) || 10000;
  for (const g of sorted) {
    const li = document.createElement("li");
    if (fresh && g.word === fresh.word) li.classList.add("fresh");
    if (g.rank === 1 && solved) li.classList.add("solved");

    const num = document.createElement("span");
    num.className = "gnum";
    num.textContent = "#" + (sorted.indexOf(g) + 1);

    const word = document.createElement("span");
    word.className = "gword " + heatClass(g.rank, g.fallback);
    word.textContent = g.word;
    if (g.raw && g.raw.toLowerCase() !== g.word) {
      const raw = document.createElement("span");
      raw.className = "raw";
      raw.textContent = `(${g.raw})`;
      word.appendChild(raw);
    }
    if (g.fallback) {
      const tag = document.createElement("span");
      tag.className = "raw";
      tag.textContent = "· SimCSE";
      word.appendChild(tag);
    }

    const rank = document.createElement("span");
    rank.className = "grank";
    rank.textContent = g.fallback
      ? `sim ${g.sim.toFixed(2)}`
      : g.rank == null ? "—" : `rank ${g.rank}`;

    const bar = document.createElement("span");
    bar.className = "gbar";
    const fill = document.createElement("span");
    fill.className = "gbar-fill";
    fill.style.width = barPct(g, total) + "%";
    fill.style.background = barColor(g);
    bar.appendChild(fill);

    li.append(num, word, rank, bar);
    list.appendChild(li);
  }
}

// ---- circles view ----
//
// Concentric rings at fixed rank thresholds (5, 50, 250, 1000, 3000). Each
// guess is placed at angle = atan2(y, x) from the backend's PCA layout so
// semantically-similar guesses still cluster, but radius = log(rank) so the
// rings are stable across the whole game (no rescaling per guess).

const RING_BANDS = [
  { rank: 5,    label: "🔥 top 5" },
  { rank: 50,   label: "Hoří 50" },
  { rank: 250,  label: "Přihořívá 250" },
  { rank: 1000, label: "Vlažné 1000" },
  { rank: 3000, label: "Studí 3000" },
];

function ringRadius(rank, rMax, vocabSize) {
  // log scale: rank 1 → 0, rank vocabSize → rMax.
  const v = Math.max(2, vocabSize);
  const r = Math.max(1, Math.min(rank, v));
  return rMax * Math.log(r) / Math.log(v);
}

function drawCircles(layout) {
  const svg = d3.select("#circles-svg");
  svg.selectAll("*").remove();
  const w = svg.node().clientWidth;
  const h = svg.node().clientHeight;
  const cx = w / 2;
  const cy = h / 2;
  const rMax = Math.min(w, h) / 2 - 56;
  const vocabSize = (game && game.vocab_size) || 12000;

  const root = svg.append("g").attr("transform", `translate(${cx},${cy})`);

  // Faint radial guides.
  for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
    root.append("line")
      .attr("class", "radial-guide")
      .attr("x1", 0).attr("y1", 0)
      .attr("x2", Math.cos(a) * rMax)
      .attr("y2", Math.sin(a) * rMax);
  }

  // Rings at fixed rank thresholds + an outermost ring at vocab edge.
  for (const band of RING_BANDS) {
    if (band.rank >= vocabSize) continue;
    const r = ringRadius(band.rank, rMax, vocabSize);
    root.append("circle").attr("class", "ring").attr("r", r);
    root.append("text")
      .attr("class", "ring-label")
      .attr("x", r + 4)
      .attr("y", 3)
      .attr("text-anchor", "start")
      .text(band.label);
  }
  root.append("circle").attr("class", "ring outer").attr("r", rMax);

  // Target at center.
  root.append("circle").attr("class", "target-glow").attr("r", 16);
  root.append("circle").attr("class", "target-dot").attr("r", 7);
  const targetLabel = solved && game && history.find((h) => h.rank === 1)
    ? history.find((h) => h.rank === 1).word
    : "?";
  root.append("text")
    .attr("class", "target-label")
    .attr("y", -18)
    .text(targetLabel);

  // Guesses — iterate history (not layout.guesses) because fallback guesses
  // exist in history but have no circle. Use h.circle (attached by backend)
  // for the angle, override radius from rank.
  const placed = []; // for label collision detection
  for (const h of history) {
    if (!h || !h.circle) continue;
    const c = h.circle;
    const angle = Math.atan2(c.y, c.x);
    const r = h.rank != null
      ? ringRadius(h.rank, rMax, vocabSize)
      : rMax * (1 - Math.max(0, Math.min(1, c.sim || 0)));
    const x = Math.cos(angle) * r;
    const y = Math.sin(angle) * r;
    const dotR = 4 + Math.max(0, 5 * (c.sim || 0));

    root.append("circle")
      .attr("class", "guess-dot")
      .attr("cx", x).attr("cy", y)
      .attr("r", dotR)
      .attr("fill", rankBarColor(h.rank))
      .attr("opacity", 0.92);

    const lbl = pickLabelPos(x, y, placed);
    placed.push(lbl);
    root.append("text")
      .attr("class", "guess-label")
      .attr("x", lbl.lx)
      .attr("y", lbl.ly)
      .attr("text-anchor", lbl.anchor)
      .text(h.word);
  }
}

function pickLabelPos(x, y, placed) {
  // Try four anchor offsets; pick the first one that doesn't collide.
  const candidates = [
    { dx:  9, dy:  4, anchor: "start" },
    { dx: -9, dy:  4, anchor: "end" },
    { dx:  9, dy: -8, anchor: "start" },
    { dx: -9, dy: -8, anchor: "end" },
  ];
  for (const c of candidates) {
    const lx = x + c.dx;
    const ly = y + c.dy;
    if (!placed.some((p) => Math.abs(p.lx - lx) < 30 && Math.abs(p.ly - ly) < 12)) {
      return { lx, ly, anchor: c.anchor };
    }
  }
  // Fallback: stack down.
  return { lx: x + 9, ly: y + 4 + placed.length * 12, anchor: "start" };
}

// ---- starry sky view ----
async function refreshSky() {
  if (!game) return;
  const r = await api("/api/sky/" + game.game_id);
  drawSky(r);
}

function drawSky(layout) {
  const svg = d3.select("#sky-svg");
  svg.selectAll("*").remove();
  const w = svg.node().clientWidth;
  const h = svg.node().clientHeight;
  const cx = w / 2;
  const cy = h / 2;

  // Star background.
  const stars = svg.append("g").attr("class", "bg-stars");
  for (let i = 0; i < 80; i++) {
    stars.append("circle")
      .attr("cx", Math.random() * w)
      .attr("cy", Math.random() * h)
      .attr("r", Math.random() * 1.2)
      .attr("fill", "#ffffff")
      .attr("opacity", 0.15 + Math.random() * 0.4);
  }

  if (!layout.guesses || layout.guesses.length === 0) {
    svg.append("text")
      .attr("x", cx).attr("y", cy)
      .attr("fill", "#98a3b3")
      .attr("text-anchor", "middle")
      .attr("font-size", 14)
      .text("Zatím žádné hvězdy. Zkus tipnout slovo.");
    return;
  }

  // Compute extent of layout to fit the SVG.
  const xs = [layout.target[0], ...layout.guesses.map((g) => g.x)];
  const ys = [layout.target[1], ...layout.guesses.map((g) => g.y)];
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const pad = 60;
  const sx = d3.scaleLinear().domain([minX, maxX]).range([pad, w - pad]);
  const sy = d3.scaleLinear().domain([minY, maxY]).range([pad, h - pad]);

  const g = svg.append("g");

  // Constellation edges.
  for (const e of layout.edges || []) {
    const a = layout.guesses[e[0]];
    const b = layout.guesses[e[1]];
    if (!a || !b) continue;
    g.append("line")
      .attr("class", "constellation-edge")
      .attr("x1", sx(a.x)).attr("y1", sy(a.y))
      .attr("x2", sx(b.x)).attr("y2", sy(b.y));
  }

  // Target star: bright golden, with halo.
  g.append("circle")
    .attr("cx", sx(layout.target[0]))
    .attr("cy", sy(layout.target[1]))
    .attr("r", 14)
    .attr("fill", "#ffb44d")
    .attr("opacity", 0.25);
  g.append("circle")
    .attr("cx", sx(layout.target[0]))
    .attr("cy", sy(layout.target[1]))
    .attr("r", 6)
    .attr("fill", "#ffb44d");
  g.append("text")
    .attr("class", "target-label")
    .attr("x", sx(layout.target[0]))
    .attr("y", sy(layout.target[1]) - 18)
    .text(solved && game && history.find((h) => h.rank === 1)
      ? history.find((h) => h.rank === 1).word
      : "?");

  // Guesses as stars.
  for (const gu of layout.guesses) {
    const r = 3 + 6 * gu.sim;
    g.append("circle")
      .attr("cx", sx(gu.x))
      .attr("cy", sy(gu.y))
      .attr("r", r)
      .attr("fill", rankBarColor(gu.rank))
      .attr("stroke", "rgba(255,255,255,0.2)");
    g.append("text")
      .attr("class", "guess-label")
      .attr("x", sx(gu.x) + r + 3)
      .attr("y", sy(gu.y) + 4)
      .text(gu.word);
  }
}

// ---- tabs ----
function setupTabs() {
  $$(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      $$(".tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      $$(".view").forEach((v) => v.classList.remove("active"));
      const view = tab.dataset.view;
      $("#view-" + view).classList.add("active");
      if (view === "circles") drawCircles(circles || { target: [0, 0], guesses: [] });
      if (view === "sky" && history.length > 0) refreshSky();
    });
  });
}

// ---- bootstrap ----
window.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  $("#guess-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const w = $("#guess-input").value.trim();
    if (!w) return;
    $("#guess-input").value = "";
    submitGuess(w);
  });
  $("#new-game-btn").addEventListener("click", newGame);
  $("#reveal-btn").addEventListener("click", reveal);
  $("#refresh-sky").addEventListener("click", refreshSky);
  $("#model-select").addEventListener("change", () => {
    if (history.length > 0 && !solved) {
      if (!confirm("Změnit model znamená novou hru. Pokračovat?")) {
        // revert
        $("#model-select").value = game.model;
        return;
      }
    }
    newGame();
  });
  newGame();
});
