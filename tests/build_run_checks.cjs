/* 実際のbuild.jsを読み込み、ボタンとiframeメッセージから送るリクエストを確認する。 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

async function workspace(mode = "flask", chatReply = async () => ({})) {
  // 描画そのものはブラウザーで確認する。ここではDOMと保存APIの境界だけを置換する。
  function element(tagName = "div") {
    return {
      tagName, value: "", textContent: "", children: [], listeners: {}, selectionStart: 0,
      classList: {toggle() {}, add() {}, remove() {}},
      addEventListener(name, callback) { this.listeners[name] = callback; },
      append(child) { this.children.push(child); },
      replaceChildren() { this.children = []; },
      setAttribute() {}, setSelectionRange() {},
      get options() { return this.children; }
    };
  }
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  };
  let saved = {
    id: "project-test", name: "Test", revision: 1, chat: [],
    active_file: mode === "html" ? "templates/index.html" : "app.py",
    files: {"app.py": "original app", "templates/index.html": "<h1>Home</h1>"}
  };
  get("build-initial").textContent = JSON.stringify({project: saved, projects: [saved], csrf: "test"});
  get("run-mode").value = mode;
  get("preview-path").value = "/";
  get("preview").contentWindow = {};
  const window = element();
  const calls = [];
  let token = "";
  const context = vm.createContext({
    window, AbortController, setTimeout, clearTimeout,
    document: {getElementById: get, createElement: element, querySelector: () => get("ai-panel")},
    fetch: async (url, options) => {
      const body = JSON.parse(options.body);
      calls.push({url, body});
      let result;
      if (url.endsWith("/save")) {
        saved = {...saved, ...body, revision: saved.revision + 1};
        result = {project: saved};
      } else if (url.endsWith("/run")) {
        token = `token-${calls.length}`;
        result = {token, document: `<p>${body.method} ${body.path}</p>`, status: 200};
      } else if (url.endsWith("/advice")) {
        result = {answer: "Test advice"};
      } else if (url.endsWith("/chat")) {
        result = await chatReply(body);
      } else {
        throw new Error(`Unexpected API: ${url}`);
      }
      return {ok: true, json: async () => result};
    }
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../src/static/build.js"), "utf8"), context);
  const settle = () => new Promise(resolve => setImmediate(resolve));
  await settle();
  return {
    get, calls, settle,
    submit: () => get("chat-form").listeners.submit({preventDefault() {}}),
    renderChat: history => context.renderChat(history),
    runs: () => calls.filter(call => call.url.endsWith("/run")),
    async click(id) { await get(id).listeners.click(); await settle(); },
    async navigate(path, method = "GET", data = {}) {
      window.listeners.message({source: get("preview").contentWindow, origin: "null",
        data: {type: "build-request", token, path, method, data}});
      await settle();
    },
    edit(code) { get("code-editor").value = code; get("code-editor").listeners.input(); }
  };
}

const checks = {
  async post_then_run() {
    const ui = await workspace();
    await ui.navigate("/count", "POST", {amount: "1"});
    assert.equal(ui.get("preview-path").value, "/count");
    await ui.click("run");
    const request = ui.runs().at(-1).body;
    assert.equal(request.path, "/");
    assert.equal(request.method, "GET");
    assert.deepEqual(request.data, {});
    assert.equal(ui.get("preview-path").value, "/");
  },
  async changed_routes() {
    const ui = await workspace();
    await ui.navigate("/old-route");
    ui.edit("new app with only root route");
    await ui.click("run");
    const saved = ui.calls.find(call => call.url.endsWith("/save"));
    assert.equal(saved.body.files["app.py"], "new app with only root route");
    const latest = ui.runs().at(-1);
    assert.ok(ui.calls.indexOf(saved) < ui.calls.indexOf(latest));
    assert.equal(latest.body.revision, 2);
    assert.equal(latest.body.path, "/");
    assert.equal(latest.body.method, "GET");
  },
  async navigation() {
    const ui = await workspace();
    await ui.navigate("/detail");
    await ui.navigate("/save", "POST", {body: "keep me"});
    await ui.navigate("/", "GET");
    assert.deepEqual(ui.runs().map(call => [call.body.path, call.body.method]),
      [["/", "GET"], ["/detail", "GET"], ["/save", "POST"], ["/", "GET"]]);
    assert.deepEqual(ui.runs()[2].body.data, {body: "keep me"});
  },
  async save_only() {
    const ui = await workspace();
    await ui.navigate("/count", "POST");
    const document = ui.get("preview").srcdoc;
    const count = ui.runs().length;
    ui.edit("edited app");
    await ui.click("save");
    assert.equal(ui.get("preview-path").value, "/count");
    assert.equal(ui.get("preview").srcdoc, document);
    assert.equal(ui.runs().length, count);
  },
  async html_mode() {
    const ui = await workspace("html");
    await ui.navigate("/templates/about.html");
    ui.edit("<h1>Updated home</h1>");
    await ui.click("run");
    const request = ui.runs().at(-1).body;
    assert.equal(request.mode, "html");
    assert.equal(request.entry, "templates/index.html");
    assert.equal(request.path, "/");
    assert.equal(request.method, "GET");
    assert.equal(request.revision, 2);
  },
  async chat_flow() {
    let finish;
    const ui = await workspace("flask", () => new Promise(resolve => { finish = resolve; }));
    await ui.navigate("/count", "POST");
    ui.edit("updated code");
    ui.get("chat-question").value = "help with error";
    const pending = ui.submit();
    await ui.settle();
    assert.match(ui.get("ai-mode").textContent, /PROCESSING/);
    assert.equal(ui.get("send-chat").disabled, true);
    await ui.submit();
    const chats = ui.calls.filter(call => call.url.endsWith("/chat"));
    assert.equal(chats.length, 1);
    assert.equal(chats[0].body.preview.mode, "flask");
    assert.equal(chats[0].body.preview.last_run.revision, 1);
    assert.ok(ui.calls.some(call => call.url.endsWith("/save") && call.body.files["app.py"] === "updated code"));
    finish({chat: [{role: "assistant", text: "sample"}], mode: "OpenAI", status: "generated"});
    await pending;
    assert.equal(ui.get("send-chat").disabled, false);
    assert.equal(ui.get("chat-question").value, "");
    assert.equal(ui.get("code-editor").value, "updated code");
    assert.equal(ui.get("preview-path").value, "/count");
  },
  async chat_failure() {
    const ui = await workspace("flask", async () => { throw new Error("private error detail"); });
    ui.get("chat-question").value = "keep my question";
    await ui.submit();
    assert.equal(ui.get("send-chat").disabled, false);
    assert.equal(ui.get("chat-question").value, "keep my question");
    assert.doesNotMatch(ui.get("chat-status").textContent, /private error detail/);
    assert.equal(ui.get("ai-mode").textContent, "送信失敗");
  },
  async chat_rendering() {
    const ui = await workspace();
    const malicious = '<img src=x onerror="alert(1)">';
    ui.renderChat([{role: "assistant", text: `${malicious}\n\n\`\`\`html\n${malicious}\n\`\`\``}]);
    const message = ui.get("chat-history").children[0];
    const all = [];
    function collect(node) { all.push(node); node.children.forEach(collect); }
    collect(message);
    assert.equal(all.filter(node => node.tagName === "code").length, 1);
    assert.ok(all.some(node => node.tagName === "code" && node.textContent.includes(malicious)));
    assert.ok(all.some(node => node.tagName === "p" && node.textContent.includes(malicious)));
    assert.ok(all.every(node => !["img", "script"].includes(node.tagName)));
  }
};

checks[process.argv[2]]().catch(error => { console.error(error); process.exitCode = 1; });
