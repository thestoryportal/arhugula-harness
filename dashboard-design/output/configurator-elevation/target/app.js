"use strict";
const TOKEN = window.__PWRL_TOKEN__;
const BAR = ["text", "ball", "bar", "blocks", "blocks-line", "capped", "dots",
  "filled", "geometric", "line", "squares"];

// Segment catalog: label + tooltip description + configurable options.
// opt types: bool | enum(values) | text | number. "Output type / units" lives
// in *.type, *.displayStyle, context.percentageMode, *.showUnits. Budgets and
// context limits are folded into their relevant segments (see segRow).
const SEG = {
  directory: { label: "Directory", icon: "", desc: "Current working directory path.",
    opts: { style: { t: "enum", v: ["full", "fish", "basename"], d: "full path · fish-abbreviated · last folder only" } } },
  git: { label: "Git", icon: "⎇", desc: "Branch and working-tree status.",
    opts: { showAheadBehind: { t: "bool" }, showSha: { t: "bool" }, showWorkingTree: { t: "bool" },
      showOperation: { t: "bool" }, showTag: { t: "bool" }, showTimeSinceCommit: { t: "bool" },
      showStashCount: { t: "bool" }, showUpstream: { t: "bool" }, showRepoName: { t: "bool" } } },
  model: { label: "Model", icon: "✱", desc: "Active model name.", opts: {} },
  session: { label: "Session", icon: "§", desc: "Cumulative usage for this session.",
    opts: { type: { t: "enum", v: ["cost", "tokens", "both", "breakdown"], d: "output: $ · tokens · both · breakdown" },
      costSource: { t: "enum", v: ["calculated", "official"] }, showUnits: { t: "bool" } } },
  today: { label: "Today", icon: "☉", desc: "Usage so far today.",
    opts: { type: { t: "enum", v: ["cost", "tokens", "both", "breakdown"], d: "output: $ · tokens · both · breakdown" }, showUnits: { t: "bool" } } },
  block: { label: "Block", icon: "⊞", desc: "Current 5-hour billing block + burn rate.",
    opts: { type: { t: "enum", v: ["cost", "tokens", "both", "time", "weighted"] },
      burnType: { t: "enum", v: ["cost", "tokens", "both", "none"] },
      displayStyle: { t: "enum", v: BAR } } },
  context: { label: "Context", icon: "◔", desc: "Context-window occupancy.",
    opts: { percentageMode: { t: "enum", v: ["remaining", "used"], d: "show % remaining or % used" },
      showPercentageOnly: { t: "bool" }, displayStyle: { t: "enum", v: BAR },
      autocompactBuffer: { t: "number" } } },
  metrics: { label: "Metrics", icon: "⌛", desc: "Response time, duration, messages, lines changed.",
    opts: { showLastResponseTime: { t: "bool" }, showResponseTime: { t: "bool" }, showDuration: { t: "bool" },
      showMessageCount: { t: "bool" }, showLinesAdded: { t: "bool" }, showLinesRemoved: { t: "bool" } } },
  weekly: { label: "Weekly", icon: "◑", desc: "Usage this week.",
    opts: { displayStyle: { t: "enum", v: BAR } } },
  version: { label: "Version", icon: "⌘", desc: "Claude Code version.", opts: {} },
  agent: { label: "Agent", icon: "⧖", desc: "Agent / subagent status.",
    opts: { showLabel: { t: "bool" } } },
  thinking: { label: "Thinking", icon: "✦", desc: "Thinking mode on/off and effort level.",
    opts: { showEnabled: { t: "bool" }, showEffort: { t: "bool" } } },
  cacheTimer: { label: "Cache timer", icon: "◴", desc: "Prompt-cache TTL.",
    opts: { displayMode: { t: "enum", v: ["elapsed", "remaining"] } } },
  tmux: { label: "tmux", icon: "", desc: "tmux session info.", opts: {} },
  sessionId: { label: "Session ID", icon: "#", desc: "Session identifier.",
    opts: { showIdLabel: { t: "bool" } } },
  env: { label: "Env var", icon: "", desc: "Show the value of an environment variable.",
    opts: { variable: { t: "text", d: "env var name, e.g. AWS_PROFILE" }, prefix: { t: "text" } } },
};
const ALL_SEGS = Object.keys(SEG);
const DEFAULTS = { session: { type: "tokens" }, today: { type: "cost" }, block: { type: "cost" }, env: { variable: "" } };
const BUDGET_SEGS = ["session", "today", "block"];

let state = { config: null, custom: {} };
let previewTimer = null;

const $ = (id) => document.getElementById(id);
function el(tag, props = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) e.setAttribute(k, v);
  }
  for (const c of kids) if (c != null) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
}
function setStatus(msg, cls) { const s = $("status"); s.textContent = msg; s.className = "status " + (cls || ""); }
function dirty() { setStatus("unsaved changes", "dirty"); schedulePreview(); }

// ---- tooltip ---------------------------------------------------------------
const tip = $("tooltip");
function showTip(e, title, body) {
  tip.innerHTML = "";
  tip.append(el("div", { class: "tt-title" }, title));
  if (body) tip.append(el("div", {}, body));
  tip.hidden = false;
  const r = e.target.getBoundingClientRect();
  tip.style.left = Math.min(r.left, window.innerWidth - 320) + "px";
  tip.style.top = (r.bottom + 6) + "px";
}
function hideTip() { tip.hidden = true; }

// ---- widgets ---------------------------------------------------------------
function toggle(checked, onChange) {
  const inp = el("input", { type: "checkbox" });
  inp.checked = !!checked;
  inp.addEventListener("change", () => onChange(inp.checked));
  return el("label", { class: "switch" }, inp, el("span", { class: "slider" }));
}

// generic option control bound to obj[key]; labelText overrides the key label
function optControl(obj, key, spec, labelText) {
  const lab = labelText || key;
  if (spec.t === "bool") {
    return el("label", { class: "opt" }, toggle(obj[key], (v) => { obj[key] = v; dirty(); }), lab);
  }
  if (spec.t === "enum") {
    const sel = el("select");
    for (const v of spec.v) sel.append(el("option", { value: v }, v));
    sel.value = obj[key] ?? spec.v[0];
    sel.addEventListener("change", () => { obj[key] = sel.value; dirty(); });
    const wrap = el("label", { class: "opt" }, lab, sel);
    if (spec.d) wrap.title = spec.d;
    return wrap;
  }
  if (spec.t === "number") {
    const inp = el("input", { type: "number" });
    inp.value = obj[key] ?? "";
    inp.addEventListener("change", () => { obj[key] = inp.value === "" ? undefined : Number(inp.value); dirty(); });
    return el("label", { class: "opt" }, lab, inp);
  }
  const inp = el("input", { type: "text" });
  inp.value = obj[key] ?? "";
  if (spec.d) inp.placeholder = spec.d;
  inp.addEventListener("change", () => { obj[key] = inp.value; dirty(); });
  return el("label", { class: "opt" }, lab, inp);
}

// ---- folded budget / context-limits ----------------------------------------
function budgetFold(segKey) {
  state.config.budget = state.config.budget || {};
  const b = (state.config.budget[segKey] = state.config.budget[segKey] || {});
  const opts = el("div", { class: "opts" },
    optControl(b, "amount", { t: "number" }, "amount"),
    optControl(b, "warningThreshold", { t: "number" }, "warn %"),
    optControl(b, "type", { t: "enum", v: ["cost", "tokens"] }, "unit"));
  return el("div", { class: "fold" },
    el("div", { class: "fold-title" }, `Budget — warn when ${segKey} exceeds amount`), opts);
}
function limitsFold() {
  const c = state.config;
  c.modelContextLimits = c.modelContextLimits || {};
  const opts = el("div", { class: "opts" });
  for (const k of ["default", "opus", "sonnet"]) opts.append(optControl(c.modelContextLimits, k, { t: "number" }, k));
  return el("div", { class: "fold" },
    el("div", { class: "fold-title" }, "Context window limits (tokens, per model)"), opts);
}

// ---- one segment row -------------------------------------------------------
function segRow(lineSegs, key) {
  const segObj = lineSegs[key];
  const meta = SEG[key] || { label: key, icon: "", desc: "", opts: {} };
  const box = el("div", { class: "seg" + (segObj.enabled ? "" : " off") });
  const name = el("span", { class: "seg-name" }, meta.label);
  name.addEventListener("mouseenter", (e) => showTip(e, meta.label, meta.desc));
  name.addEventListener("mouseleave", hideTip);
  box.append(el("div", { class: "seg-row" },
    toggle(segObj.enabled, (v) => { segObj.enabled = v; box.className = "seg" + (v ? "" : " off"); dirty(); }),
    el("span", { class: "seg-icon" }, meta.icon || "•"),
    name,
    el("span", { class: "grow" }),
    el("button", { class: "btn mini", title: "Move up", onclick: () => moveSeg(lineSegs, key, -1) }, "↑"),
    el("button", { class: "btn mini", title: "Move down", onclick: () => moveSeg(lineSegs, key, 1) }, "↓"),
    el("button", { class: "btn mini danger", title: "Remove from this line", onclick: () => { delete lineSegs[key]; render(); dirty(); } }, "✕"),
  ));
  const optKeys = Object.keys(meta.opts);
  if (optKeys.length) {
    const opts = el("div", { class: "opts" });
    for (const ok of optKeys) opts.append(optControl(segObj, ok, meta.opts[ok]));
    box.append(opts);
  }
  if (BUDGET_SEGS.includes(key)) box.append(budgetFold(key));
  if (key === "context") box.append(limitsFold());
  return box;
}

function moveSeg(lineSegs, key, dir) {
  const keys = Object.keys(lineSegs);
  const i = keys.indexOf(key), j = i + dir;
  if (j < 0 || j >= keys.length) return;
  [keys[i], keys[j]] = [keys[j], keys[i]];
  const rebuilt = {};
  for (const k of keys) rebuilt[k] = lineSegs[k];
  for (const k of Object.keys(lineSegs)) delete lineSegs[k];
  Object.assign(lineSegs, rebuilt);
  render(); dirty();
}

// ---- segments (lines) ------------------------------------------------------
function renderLines() {
  const root = $("lines"); root.innerHTML = "";
  const lines = state.config.display.lines;
  lines.forEach((line, idx) => {
    line.segments = line.segments || {};
    const block = el("div", { class: "lineblock" });
    block.append(el("div", { class: "lhead" },
      el("span", { class: "ltitle" }, "Line " + (idx + 1)),
      el("button", { class: "btn mini danger", title: "Delete this whole line", onclick: () => { lines.splice(idx, 1); render(); dirty(); } }, "delete line")));
    for (const key of Object.keys(line.segments)) block.append(segRow(line.segments, key));
    const sel = el("select");
    sel.append(el("option", { value: "" }, "+ add segment…"));
    for (const s of ALL_SEGS.filter((s) => !(s in line.segments))) sel.append(el("option", { value: s }, SEG[s].label));
    sel.addEventListener("change", () => {
      if (!sel.value) return;
      line.segments[sel.value] = Object.assign({ enabled: true }, DEFAULTS[sel.value] || {});
      render(); dirty();
    });
    block.append(el("div", { class: "addrow" }, sel));
    root.append(block);
  });
  root.append(el("button", { class: "btn", onclick: () => { lines.push({ segments: {} }); render(); dirty(); } }, "+ add line"));
}

// ---- custom data -----------------------------------------------------------
function renderCustom() {
  const root = $("custom"); root.innerHTML = "";
  const rows = [
    ["rtkGlobal", "⚡ RTK savings (global)", "All-time token savings across every repo (rtk gain)."],
    ["rtkProject", "⌂ RTK savings (this repo)", "Token savings scoped to the current project."],
    ["link", "⚙ Configurator link", "Clickable link in the statusline that opens this page (OSC 8)."],
  ];
  for (const [k, label, desc] of rows) {
    const name = el("label", {}, label); name.title = desc;
    root.append(el("div", { class: "field" }, name,
      el("span", { class: "ctl" }, toggle(state.custom[k], (v) => { state.custom[k] = v; dirty(); }))));
  }
}

// ---- theme & display -------------------------------------------------------
function selField(label, obj, key, values, title) {
  const sel = el("select");
  for (const v of values) sel.append(el("option", { value: v }, v));
  sel.value = obj[key] ?? values[0];
  sel.addEventListener("change", () => { obj[key] = sel.value; dirty(); });
  const f = el("div", { class: "field" }, el("label", {}, label), el("span", { class: "ctl" }, sel));
  if (title) f.title = title;
  return f;
}
function boolField(label, obj, key) {
  return el("div", { class: "field" }, el("label", {}, label),
    el("span", { class: "ctl" }, toggle(obj[key], (v) => { obj[key] = v; dirty(); })));
}
function numField(label, obj, key) {
  const inp = el("input", { type: "number" });
  inp.value = obj[key] ?? "";
  inp.addEventListener("change", () => { obj[key] = inp.value === "" ? undefined : Number(inp.value); dirty(); });
  return el("div", { class: "field" }, el("label", {}, label), el("span", { class: "ctl" }, inp));
}
function renderDisplay() {
  const root = $("display"); root.innerHTML = "";
  const c = state.config, d = c.display;
  root.append(selField("Theme", c, "theme", ["dark", "light", "nord", "tokyo-night", "rose-pine", "gruvbox", "custom"]));
  root.append(selField("Style", d, "style", ["powerline", "minimal", "capsule", "tui"]));
  root.append(selField("Charset", d, "charset", ["unicode", "text"]));
  root.append(selField("Color compatibility", d, "colorCompatibility", ["auto", "truecolor", "ansi256", "ansi"]));
  root.append(boolField("Auto-wrap (reflow on narrow widths)", d, "autoWrap"));
  root.append(numField("Padding", d, "padding"));
  root.append(boolField("Show icons", d, "showIcons"));
}

// ---- preview / save / load -------------------------------------------------
function schedulePreview() { clearTimeout(previewTimer); previewTimer = setTimeout(runPreview, 250); }
async function runPreview() {
  try {
    const r = await fetch("/api/preview", {
      method: "POST", headers: { "Content-Type": "application/json", "X-Powerline-Token": TOKEN },
      body: JSON.stringify({ config: state.config, custom: state.custom, columns: Number($("cols").value) }),
    });
    const j = await r.json();
    $("preview").innerHTML = j.html || "(empty)";
    $("preview-err").textContent = j.error ? "preview error: " + j.error : (j.stderr || "").trim();
  } catch (e) { $("preview-err").textContent = "preview failed: " + e; }
}
async function save() {
  setStatus("saving…");
  try {
    const r1 = await fetch("/api/config", { method: "POST", headers: { "Content-Type": "application/json", "X-Powerline-Token": TOKEN }, body: JSON.stringify({ config: state.config }) });
    const j1 = await r1.json(); if (!r1.ok) throw new Error(j1.error || "config save failed");
    const r2 = await fetch("/api/custom", { method: "POST", headers: { "Content-Type": "application/json", "X-Powerline-Token": TOKEN }, body: JSON.stringify({ custom: state.custom }) });
    const j2 = await r2.json(); if (!r2.ok) throw new Error(j2.error || "custom save failed");
    setStatus("saved ✓ — appears on next statusline update", "saved");
  } catch (e) { setStatus("error: " + e.message, "err"); }
}
async function load() {
  setStatus("loading…");
  const r = await fetch("/api/state"); const j = await r.json();
  if (!r.ok) { setStatus("load error: " + (j.error || r.status), "err"); return; }
  state.config = j.config;
  state.config.display = state.config.display || { lines: [] };
  state.config.display.lines = state.config.display.lines || [];
  state.custom = j.custom || {};
  render(); setStatus("loaded", ""); runPreview();
}
function render() { renderDisplay(); renderLines(); renderCustom(); }

$("save").addEventListener("click", save);
$("reload").addEventListener("click", load);
$("cols").addEventListener("input", () => { $("cols-val").textContent = $("cols").value; schedulePreview(); });
load();
