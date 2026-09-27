/* 実際のUIスクリプトのイベントを検証。innerHTMLの使用はテストで即失敗する。 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const plan = {purpose: '<script>alert(1)</script>', features: "候補", learn: "第6訓練", first_step: "見出しを編集"};
function workspace(required = true, reply = async () => ({plan, mode: "ローカル"}), saveFails = false) {
  const elements = new Map();
  const calls = [];
  function element() {
    return {value: "", textContent: "", hidden: true, children: [], listeners: {},
      set innerHTML(value) { assert.fail("Do not parse untrusted HTML"); },
      replaceChildren() { this.children = []; }, append(...nodes) { this.children.push(...nodes); },
      addEventListener(event, fn) { this.listeners[event] = fn; },
      showModal() { this.open = true; }, close() { this.open = false; }, focus() { this.focused = true; }};
  }
  const get = id => { if (!elements.has(id)) elements.set(id, element()); return elements.get(id); };
  const context = vm.createContext({initial: {onboarding: {required, plan: required ? {} : plan}}, byId: get,
    document: {createElement: element}, api: async (url, data) => {
      calls.push({url, data});
      if (url.endsWith("/plan")) return reply();
      if (saveFails) throw new Error("offline");
      return {onboarding: {required: false, plan: data.action === "skip" ? {} : data.plan}};
    }});
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../src/static/build_onboarding.js"), "utf8"), context);
  return {get, calls, submit: () => get("onboarding-form").listeners.submit({preventDefault() {}}),
    click: id => get(id).listeners.click()};
}
const checks = {
  async flow() {
    const ui = workspace();
    assert.equal(ui.get("onboarding-dialog").open, true);
    ui.get("onboarding-idea").value = "映画の記録";
    await ui.submit();
    assert.equal(ui.get("plan-purpose").value, plan.purpose);
    assert.equal(ui.get("onboarding-start").hidden, false);
    ui.get("plan-features").value = "自分の候補";
    await ui.click("onboarding-start");
    assert.equal(ui.calls[1].data.plan.features, "自分の候補");
    assert.equal(ui.get("onboarding-dialog").open, false);
    assert.equal(ui.get("code-editor").focused, true);
    assert.equal(ui.get("onboarding-notes-body").children[1].textContent, plan.purpose);
    assert.deepEqual(ui.calls.map(c => c.url), ["/build/onboarding/plan", "/build/onboarding/complete"]);
  },
  async skip_pending() {
    let resolve;
    const ui = workspace(true, () => new Promise(done => { resolve = done; }));
    ui.get("onboarding-idea").value = "自由なページ";
    const pending = ui.submit();
    await ui.submit();
    assert.equal(ui.calls.length, 1);
    await ui.click("onboarding-skip");
    resolve({plan, mode: "test"});
    await pending;
    assert.equal(ui.get("onboarding-dialog").open, false);
    assert.equal(ui.get("onboarding-proposal").hidden, true);
    assert.equal(ui.calls[1].data.action, "skip");
  },
  async failure() {
    const ui = workspace(true, async () => { throw new Error("network"); });
    ui.get("onboarding-idea").value = "入力を失わない";
    await ui.submit();
    assert.equal(ui.get("onboarding-idea").value, "入力を失わない");
    assert.match(ui.get("onboarding-status").textContent, /スキップ/);
    assert.equal(ui.get("onboarding-organize").disabled, false);
    await ui.click("onboarding-skip");
    assert.equal(ui.get("onboarding-dialog").open, false);
  },
  async completed() {
    const ui = workspace(false);
    assert.equal(ui.calls.length, 0);
    assert.equal(ui.get("onboarding-dialog").open, undefined);
    assert.equal(ui.get("onboarding-notes").hidden, false);
  },
  async revise() {
    const ui = workspace();
    ui.get("onboarding-idea").value = "最初のアイデア";
    await ui.submit();
    assert.equal(ui.get("onboarding-form").hidden, true);
    await ui.click("onboarding-revise");
    assert.equal(ui.get("onboarding-form").hidden, false);
    assert.equal(ui.get("onboarding-proposal").hidden, true);
    assert.equal(ui.get("onboarding-idea").value, "最初のアイデア");
    await ui.click("onboarding-start");
    assert.equal(ui.calls.length, 1);
    ui.get("onboarding-idea").value = "別のアイデア";
    await ui.submit();
    assert.equal(ui.calls[1].data.idea, "別のアイデア");
  },
  async save_failure() {
    const ui = workspace(true, async () => ({plan, mode: "test"}), true);
    await ui.click("onboarding-skip");
    assert.equal(ui.get("onboarding-dialog").open, true);
    assert.equal(ui.get("onboarding-skip").disabled, false);
    assert.match(ui.get("onboarding-status").textContent, /保存できません/);
  }
};
checks[process.argv[2]]().catch(error => { console.error(error); process.exitCode = 1; });
