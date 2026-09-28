/* 実際のPhase 3 UIイベント・可視状態タイマー・テキスト描画を検証する。 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
function element() {
  return {textContent: "", value: "", hidden: false, dataset: {}, children: [], listeners: {},
    classList: {toggle() {}}, setAttribute() {},
    set innerHTML(value) { assert.fail("Untrusted HTML must not be parsed"); },
    append(...nodes) { this.children.push(...nodes); }, replaceChildren() { this.children = []; },
    addEventListener(type, callback) { this.listeners[type] = callback; }};
}
async function main() {
  const elements = new Map();
  const get = id => { if (!elements.has(id)) elements.set(id, element()); return elements.get(id); };
  const window = element();
  const document = {...element(), hidden: false, getElementById: get, createElement: element,
    querySelectorAll: () => []};
  const attack = {id: "a", status: "active", title: "Target", objective: "Observe", count: 0, limit: 10,
    response: "<script>never execute</script>", logs: [], hints: [], related_learn: []};
  const defend = {id: "d", status: "armed", title: "Copy", description: "observe", source_id: "p", source_name: "Copy",
    source_revision: 1, path: "/", policy: {blocked_sources: [], max_body: 10000}, logs: [], response: "", hints: [], related_learn: []};
  const state = {difficulty: "hard", view: "view-1", targets: [], attack, defend, history: []};
  get("arena-initial").textContent = JSON.stringify({state, csrf: "fixture"});
  get("request-path").value = "/"; get("request-method").value = "GET"; get("request-fields").value = "{}";
  let timerId = 0;
  const timers = new Map(); const calls = [];
  const context = vm.createContext({document, window, AbortController,
    setTimeout(fn, ms) { timers.set(++timerId, {fn, ms}); return timerId; },
    clearTimeout(id) { timers.delete(id); },
    fetch: async (url, options) => {
      const data = JSON.parse(options.body); calls.push(data);
      assert.equal(url, "/arena/action");
      assert.equal(options.headers["X-Build-CSRF"], "fixture");
      if (data.action === "attack-request") state.attack.count++;
      return {ok: true, json: async () => ({state: structuredClone(state)})};
    }});
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../src/static/arena.js"), "utf8"), context);
  assert.equal(get("attack-response").textContent, attack.response);
  assert.equal(get("guide-hint").hidden, true);
  assert.equal(get("defend-copy").disabled, true);
  const pulseTimers = () => [...timers.values()].filter(timer => timer.ms === 3000).length;
  assert.equal(pulseTimers(), 1);
  window.listeners.pageshow(); window.listeners.pageshow();
  assert.equal(pulseTimers(), 1);
  document.hidden = true; document.listeners.visibilitychange();
  assert.equal(pulseTimers(), 0);
  await context.pulse(); assert.equal(calls.length, 0);
  document.hidden = false; document.listeners.visibilitychange();
  await context.pulse();
  assert.equal(calls.at(-1).paused, true);
  await context.pulse();
  assert.equal(calls.at(-1).paused, false);
  assert.equal(calls.at(-1).view, "view-1");
  assert.equal(pulseTimers(), 1);
  window.listeners.pagehide();
  assert.equal(pulseTimers(), 0);
  const before = calls.length;
  get("request-fields").value = "not json";
  get("request-form").listeners.submit({preventDefault() {}});
  assert.equal(calls.length, before);
  assert.match(get("arena-message").textContent, /JSON/);
  get("request-fields").value = '{"q":"guide"}';
  get("request-form").listeners.submit({preventDefault() {}});
  get("request-form").listeners.submit({preventDefault() {}});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls.length, before + 1);
  assert.equal(calls.at(-1).sequence, 0);
  assert.equal(get("attack-response").textContent, attack.response);
  assert.equal(pulseTimers(), 0);
  assert.equal(get("defend-copy").disabled, true);
  get("defend-project").value = "project-1";
  context.renderArena();
  assert.equal(get("defend-copy").disabled, false);
}
main().catch(error => { console.error(error); process.exitCode = 1; });
