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
  if ($("#view-sky").classList.contains("active")) {
    refreshSky();
  }
  if (r.solved) {
    $("#status").textContent = `Uhodnuto! Slovo bylo "${r.target}". (${history.length} tipů)`;
    $("#status").className = "status win";
  } else {
    flashStatus(rankHint(r.guess.rank, r.guess.sim));
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

function rankHint(rank, sim) {
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
  word.className = "gword " + heatClass(g.rank);
  word.textContent = g.word;
  if (g.raw && g.raw.toLowerCase() !== g.word) {
    const raw = document.createElement("span");
    raw.className = "raw";
    raw.textContent = `(${g.raw})`;
    word.appendChild(raw);
  }

  const rank = document.createElement("span");
  rank.className = "grank";
  rank.textContent = g.rank == null ? "mimo slovník" : `rank ${g.rank}`;

  const bar = document.createElement("span");
  bar.className = "gbar";
  const fill = document.createElement("span");
  fill.className = "gbar-fill";
  fill.style.width = rankBarPct(g.rank, total) + "%";
  fill.style.background = rankBarColor(g.rank);
  bar.appendChild(fill);

  el.append(label, word, rank, bar);
}

function heatClass(rank) {
  if (rank == null) return "heat-5";
  if (rank <= 5) return "heat-1";
  if (rank <= 50) return "heat-2";
  if (rank <= 250) return "heat-3";
  if (rank <= 1000) return "heat-4";
  return "heat-5";
}

function rankBarPct(rank, total) {
  if (rank == null) return 0;
  // Log scale so the difference between rank 1 and 100 is visible.
  const t = Math.max(1, Math.min(rank, total));
  return 100 * (1 - Math.log(t) / Math.log(total));
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
  // Sort by rank ascending (closest first); items without rank go last.
  const sorted = [...hist].sort((a, b) => {
    if (a.rank == null) return 1;
    if (b.rank == null) return -1;
    return a.rank - b.rank;
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
    word.className = "gword " + heatClass(g.rank);
    word.textContent = g.word;
    if (g.raw && g.raw.toLowerCase() !== g.word) {
      const raw = document.createElement("span");
      raw.className = "raw";
      raw.textContent = `(${g.raw})`;
      word.appendChild(raw);
    }

    const rank = document.createElement("span");
    rank.className = "grank";
    rank.textContent = g.rank == null ? "—" : `rank ${g.rank}`;

    const bar = document.createElement("span");
    bar.className = "gbar";
    const fill = document.createElement("span");
    fill.className = "gbar-fill";
    fill.style.width = rankBarPct(g.rank, total) + "%";
    fill.style.background = rankBarColor(g.rank);
    bar.appendChild(fill);

    li.append(num, word, rank, bar);
    list.appendChild(li);
  }
}

// ---- circles view ----
function drawCircles(layout) {
  const svg = d3.select("#circles-svg");
  svg.selectAll("*").remove();
  const w = svg.node().clientWidth;
  const h = svg.node().clientHeight;
  const cx = w / 2;
  const cy = h / 2;

  // Adaptive scale so the layout always fills the SVG, regardless of model
  // (fastText has dist range ~0..1.5, SimCSE ~0..0.3).
  const guesses = layout.guesses || [];
  const maxDist = Math.max(0.05, ...guesses.map((g) => g.dist));
  const radius = Math.min(w, h) / 2 - 30;
  const scale = radius / maxDist;

  // Rings as quartiles of the max distance — labels reflect band ordering, not absolute distance.
  const ringDefs = [
    { d: 0.25 * maxDist, label: "Hoří" },
    { d: 0.5 * maxDist, label: "Přihořívá" },
    { d: 0.75 * maxDist, label: "Vlažné" },
    { d: maxDist, label: "Studené" },
  ];
  const g = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  for (const r of ringDefs) {
    if (r.d <= 0) continue;
    g.append("circle")
      .attr("class", "ring")
      .attr("r", r.d * scale);
    g.append("text")
      .attr("class", "ring-label")
      .attr("x", 0)
      .attr("y", -r.d * scale - 3)
      .attr("text-anchor", "middle")
      .text(r.label);
  }

  // Target.
  g.append("circle")
    .attr("class", "target-dot")
    .attr("r", 8);
  g.append("text")
    .attr("class", "target-label")
    .attr("y", -14)
    .text(solved && game && history.find((h) => h.rank === 1)
      ? history.find((h) => h.rank === 1).word
      : "?");

  // Guesses.
  for (let i = 0; i < layout.guesses.length; i++) {
    const gg = layout.guesses[i];
    const word = (history[i] && history[i].word) || "";
    const x = gg.x * scale;
    const y = gg.y * scale;
    g.append("circle")
      .attr("class", "guess-dot")
      .attr("cx", x)
      .attr("cy", y)
      .attr("r", 5 + Math.max(0, 6 * gg.sim))
      .attr("fill", rankBarColor(history[i] && history[i].rank));
    g.append("text")
      .attr("class", "guess-label")
      .attr("x", x + 7)
      .attr("y", y + 4)
      .text(word);
  }
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
