/* エディタの文字列は表示・保存するだけ。ゲーム側でevalしない。 */
"use strict";

const initial = JSON.parse(document.getElementById("build-initial").textContent);
let project = initial.project;
let dirty = false;
let busy = false;
let previewToken = "";
let dialogMode = "file";
const byId = id => document.getElementById(id);
const editor = byId("code-editor");
const preview = byId("preview");

function message(text, error = false) {
  byId("workspace-message").textContent = text;
  byId("workspace-message").classList.toggle("is-error", error);
}

async function api(url, data) {
  const response = await fetch(url, {
    method: "POST", headers: {"Content-Type": "application/json", "X-Build-CSRF": initial.csrf},
    body: JSON.stringify(data), credentials: "same-origin"
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "処理できませんでした。再読み込みしてください。");
  return result;
}

function markDirty() {
  dirty = true;
  byId("save-state").textContent = "● 未保存";
}

function captureEditor() {
  project.files[project.active_file] = editor.value;
  project.name = byId("project-name").value;
}

function cursorPosition() {
  const before = editor.value.slice(0, editor.selectionStart).split("\n");
  byId("cursor-position").textContent = `Ln ${before.length}, Col ${before.at(-1).length + 1}`;
}

function renderFiles() {
  byId("files").replaceChildren();
  for (const filename of Object.keys(project.files)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "file-tab";
    button.textContent = filename;
    button.setAttribute("aria-pressed", String(filename === project.active_file));
    button.addEventListener("click", () => {
      if (busy) return;
      captureEditor();
      project.active_file = filename;
      markDirty();
      renderFiles();
      showSource();
      updateAdvice();
    });
    byId("files").append(button);
  }
}

function showSource() {
  editor.value = project.files[project.active_file];
  editor.setSelectionRange(0, 0);
  byId("file-label").textContent = project.active_file;
  byId("language").textContent = project.active_file.split(".").at(-1).toUpperCase();
  cursorPosition();
}

function renderChat(history) {
  byId("chat-history").replaceChildren();
  for (const item of history) {
    const text = document.createElement("p");
    text.className = `chat-message ${item.role === "user" ? "user" : "assistant"}`;
    text.textContent = `${item.role === "user" ? "YOU" : "GUIDE"}\n${item.text}`;
    byId("chat-history").append(text);
  }
  byId("chat-history").scrollTop = byId("chat-history").scrollHeight;
}

async function updateAdvice() {
  const active = project.active_file;
  try {
    const result = await api(`/build/projects/${project.id}/advice`, {active_file: active});
    if (active === project.active_file) byId("advice").textContent = result.answer;
  } catch (error) {
    // 新規ファイルは保存後に案内できる。編集中の内容は失わない。
    byId("advice").textContent = "ファイルを保存してから、この内容について質問できます。";
  }
}

function setBusy(value) {
  busy = value;
  for (const id of ["save", "run", "projects", "new-project", "add-file", "send-chat", "run-mode"]) byId(id).disabled = value;
  editor.readOnly = value;
  byId("project-name").readOnly = value;
}

async function save() {
  captureEditor();
  const result = await api(`/build/projects/${project.id}/save`, {
    name: project.name, files: project.files, active_file: project.active_file, revision: project.revision
  });
  project = result.project;
  dirty = false;
  byId("save-state").textContent = "保存済み";
  const option = [...byId("projects").options].find(item => item.value === project.id);
  option.textContent = project.name;
  message("コードを保存しました。再起動後も同じブラウザーから続けられます。");
  await updateAdvice();
}

async function run(path = "/", method = "GET", data = {}) {
  if (busy) return;
  setBusy(true);
  try {
    if (dirty) await save();
    const mode = byId("run-mode").value;
    const entry = project.active_file.endsWith(".html") ? project.active_file : "templates/index.html";
    byId("response-status").textContent = "RUNNING";
    const result = await api(`/build/projects/${project.id}/run`, {
      revision: project.revision, mode, entry, path, method, data
    });
    previewToken = result.token;
    preview.srcdoc = result.document;
    byId("run-log").textContent = result.logs || "リクエストを処理しました。";
    byId("response-status").textContent = `HTTP ${result.status}`;
    byId("preview-path").value = path;
    message(result.status >= 400 ? "実行結果にエラーがあります。ログを確認してください。" : "保存したコードをプレビューへ反映しました。", result.status >= 400);
  } catch (error) {
    byId("response-status").textContent = "ERROR";
    byId("run-log").textContent = error.message;
    message(error.message, true);
  } finally { setBusy(false); }
}

editor.addEventListener("input", () => { markDirty(); cursorPosition(); });
editor.addEventListener("click", cursorPosition);
editor.addEventListener("keyup", cursorPosition);
editor.addEventListener("keydown", event => {
  if (event.key === "Tab") {
    event.preventDefault();
    if (editor.readOnly) return;
    editor.setRangeText("    ", editor.selectionStart, editor.selectionEnd, "end");
    markDirty();
    cursorPosition();
  }
});
byId("project-name").addEventListener("input", markDirty);
byId("save").addEventListener("click", async () => {
  setBusy(true);
  try { await save(); } catch (error) { message(error.message, true); }
  finally { setBusy(false); }
});
byId("run").addEventListener("click", () => run(byId("preview-path").value));
window.addEventListener("message", event => {
  if (event.source !== preview.contentWindow || event.origin !== "null") return;
  const data = event.data;
  if (!data || data.type !== "build-request" || data.token !== previewToken) return;
  run(data.path, data.method, data.data);
});
window.addEventListener("beforeunload", event => {
  if (dirty) { event.preventDefault(); event.returnValue = ""; }
});
byId("projects").addEventListener("change", async () => {
  const selected = byId("projects").value;
  setBusy(true);
  try {
    if (dirty) await save();
    window.location.assign(`/build/?project=${encodeURIComponent(selected)}`);
  } catch (error) {
    byId("projects").value = project.id;
    message(error.message, true);
    setBusy(false);
  }
});

function openDialog(mode) {
  dialogMode = mode;
  byId("dialog-title").textContent = mode === "file" ? "新規ファイル" : "新規プロジェクト";
  byId("dialog-label").textContent = mode === "file" ? "例: templates/about.html" : "アプリの名前";
  byId("new-name").value = "";
  byId("dialog-error").textContent = "";
  byId("name-dialog").showModal();
}
byId("add-file").addEventListener("click", () => openDialog("file"));
byId("new-project").addEventListener("click", () => openDialog("project"));
byId("cancel-dialog").addEventListener("click", () => byId("name-dialog").close());
byId("name-form").addEventListener("submit", async event => {
  event.preventDefault();
  const name = byId("new-name").value.trim();
  try {
    if (dialogMode === "project") {
      if (dirty) await save();
      const result = await api("/build/projects", {name});
      dirty = false;
      window.location.assign(`/build/?project=${result.project.id}`);
    } else {
      if (!/^[A-Za-z0-9_-][A-Za-z0-9_./-]{0,119}\.(py|html|css|js|sql|md|txt|json)$/.test(name) || name.split("/").some(part => !part || part.startsWith(".")) || name.startsWith("data/")) throw new Error("英数字の相対パスと、対応する拡張子を指定してください。");
      if (Object.hasOwn(project.files, name)) throw new Error("同じ名前のファイルがあります。");
      if (Object.keys(project.files).length >= 30) throw new Error("ファイルは30個までです。");
      captureEditor();
      project.files[name] = "";
      project.active_file = name;
      markDirty(); renderFiles(); showSource();
      byId("name-dialog").close();
      updateAdvice();
    }
  } catch (error) { byId("dialog-error").textContent = error.message; }
});
byId("chat-form").addEventListener("submit", async event => {
  event.preventDefault();
  if (busy) return;
  const question = byId("chat-question").value.trim();
  if (!question) return;
  setBusy(true);
  document.querySelector(".ai-panel").classList.add("is-thinking");
  try {
    if (dirty) await save();
    const result = await api(`/build/projects/${project.id}/chat`, {question, active_file: project.active_file});
    project.chat = result.chat;
    renderChat(result.chat);
    byId("ai-mode").textContent = result.mode;
    byId("chat-question").value = "";
  } catch (error) { message(error.message, true); }
  finally { setBusy(false); document.querySelector(".ai-panel").classList.remove("is-thinking"); }
});

for (const item of initial.projects) {
  const option = document.createElement("option");
  option.value = item.id; option.textContent = item.name;
  byId("projects").append(option);
}
byId("projects").value = project.id;
byId("project-name").value = project.name;
renderFiles(); showSource(); renderChat(project.chat); updateAdvice(); run();
