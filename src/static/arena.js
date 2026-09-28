/* 画面はプレーンテキストで描画。コマンドや応答HTMLを実行しない。 */
"use strict";
const arenaInitial = JSON.parse(document.getElementById("arena-initial").textContent);
let arenaState = arenaInitial.state;
const arenaView = arenaState.view;
let arenaMode = "attack";
let arenaBusy = false;
let shownCopy = "";
const arenaById = id => document.getElementById(id);
function arenaText(id, text) { arenaById(id).textContent = text || ""; }

async function arenaPost(data) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch("/arena/action", {method: "POST", credentials: "same-origin",
      headers: {"Content-Type": "application/json", "X-Build-CSRF": arenaInitial.csrf},
      body: JSON.stringify(data), signal: controller.signal});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "操作できませんでした。");
    return result.state;
  } finally { clearTimeout(timer); }
}

function resultBox(id, attempt) {
  const box = arenaById(id);
  const ended = ["success", "failed"].includes(attempt.status);
  box.hidden = !ended;
  box.replaceChildren();
  if (!ended) return;
  box.classList.toggle("failed", attempt.status === "failed");
  const heading = document.createElement("h3");
  heading.textContent = attempt.status === "success" ? "MISSION COMPLETE / 成功" : "MISSION FAILED / 振り返り";
  const advice = document.createElement("p");
  advice.textContent = (attempt.cause ? `原因：${attempt.cause}\n` : "") + attempt.advice;
  const learn = document.createElement("p");
  learn.textContent = `関連Learn：第${attempt.related_learn.join('・')}訓練`;
  box.append(heading, advice, learn);
}

function renderArena() {
  for (const button of document.querySelectorAll("[data-difficulty]")) {
    button.setAttribute("aria-pressed", String(button.dataset.difficulty === arenaState.difficulty));
  }
  for (const button of document.querySelectorAll("[data-mode]")) button.setAttribute("aria-pressed", String(button.dataset.mode === arenaMode));
  arenaById("attack-section").hidden = arenaMode !== "attack";
  arenaById("defend-section").hidden = arenaMode !== "defend";
  // 操作後のボタン復帰でも、コピー元がない状態では開始させない。
  arenaById("defend-copy").disabled = arenaBusy || !arenaById("defend-project").value;
  const targets = arenaById("targets");
  targets.replaceChildren();
  for (const [index, target] of arenaState.targets.entries()) {
    const card = document.createElement("article"); card.className = "panel";
    const label = document.createElement("small"); label.textContent = `TARGET ${"ABC"[index]} / ${target.difficulty.toUpperCase()} / ${target.target_type}`;
    const title = document.createElement("h3"); title.textContent = target.title;
    const info = document.createElement("p"); info.textContent = target.description;
    const button = document.createElement("button"); button.type = "button"; button.className = "button button-secondary";
    button.textContent = "この対象を調査する";
    button.disabled = arenaBusy || arenaState.attack?.status === "active";
    button.addEventListener("click", () => arenaAction({action: "attack-select", target: target.id}));
    card.append(label, title, info, button); targets.append(card);
  }
  const attack = arenaState.attack;
  arenaById("attack-workbench").hidden = !attack;
  if (attack) {
    arenaText("attack-title", attack.title);
    arenaText("attack-objective", attack.objective);
    arenaText("attack-counter", `${attack.count} / ${attack.limit} REQUESTS / ${attack.status.toUpperCase()}`);
    arenaText("http-status", attack.http_status ? `HTTP ${attack.http_status}` : "READY");
    arenaText("attack-response", attack.response);
    arenaText("attack-logs", attack.logs.join("\n\n"));
    arenaById("request-form").hidden = attack.status !== "active";
    resultBox("attack-result", attack);
  }
  const defend = arenaState.defend;
  arenaById("defend-workbench").hidden = !defend;
  arenaById("hard-alert").hidden = arenaState.difficulty !== "hard";
  if (arenaState.difficulty === "hard") arenaText("hard-alert", !defend
    ? "HARD監視：Buildプロジェクトから隔離コピーを作成してください。"
    : defend.status === "armed" ? "HARD監視中：Phase 3を表示している間に、隔離コピーへ不定時の攻撃が発生します。"
    : defend.status === "incident" ? "INCIDENT DETECTED / DEFENDへ切り替えてコピーのログを確認してください。" : "HARD演習終了。新しいコピーを作成すると監視を再開します。");
  if (defend) {
    arenaText("defend-title", defend.title);
    arenaText("defend-description", defend.description);
    arenaText("defend-copy-info", `${defend.source_name} / 保存revision ${defend.source_revision} のコピー / ${defend.path}`);
    const labels = {ready: "READY / 開始ボタンで仮想攻撃を発生させます。", armed: "ARMED / 不定時の攻撃を監視しています。",
      incident: "INCIDENT / 探査通信を検知。ログを確認し、次の通信を封じ込めてください。", success: "防御成功", failed: "防御失敗、または通常アクセスが維持できませんでした。"};
    arenaText("defend-status", labels[defend.status]);
    arenaById("defend-start").hidden = defend.status !== "ready" || arenaState.difficulty === "hard";
    arenaById("policy-form").hidden = defend.status !== "incident";
    arenaText("defend-logs", defend.logs.join("\n\n") || "まだ通信は発生していません。");
    arenaText("defend-response", defend.response);
    arenaById("return-build").href = `/build/?project=${encodeURIComponent(defend.source_id)}`;
    if (shownCopy !== defend.id) {
      arenaById("defend-policy").value = JSON.stringify(defend.policy, null, 2);
      shownCopy = defend.id;
    }
    resultBox("defend-result", defend);
  }
  const attempt = arenaState[arenaMode];
  arenaText("guide-status", arenaState.difficulty === "easy" ? "支援ON / 外部AI通信を使わない段階ヒント" : "支援OFF / この難易度では挑戦中のヒントはありません。");
  arenaById("guide-hint").hidden = arenaState.difficulty !== "easy" || !attempt;
  arenaText("guide-text", attempt?.hints.join("\n\n"));
  arenaText("guide-learn", attempt?.related_learn.length ? `関連Learn：第${attempt.related_learn.join('・')}訓練` : "");
  const history = arenaById("arena-history"); history.replaceChildren();
  for (const item of arenaState.history.toReversed()) {
    const li = document.createElement("li");
    li.textContent = `${item.mode} / ${item.title} / ${item.difficulty.toUpperCase()} / ${item.passed ? "SUCCESS" : "FAILED"}`;
    history.append(li);
  }
}

async function arenaAction(data, silent = false) {
  if (arenaBusy) return;
  arenaBusy = true;
  document.querySelectorAll(".arena-interface button").forEach(button => { button.disabled = true; });
  if (!silent) arenaText("arena-message", "処理中です。隔離コンテナーでの実行には少し時間がかかります。");
  try {
    const previousDefendStatus = arenaState.defend?.status;
    arenaState = await arenaPost(data);
    if (!silent) arenaText("arena-message", "操作を反映しました。応答・ログ・結果を確認してください。");
    else if (previousDefendStatus === "armed" && arenaState.defend?.status === "incident") {
      arenaText("arena-message", "隔離コピーへの不審な通信を検知しました。DEFENDでログを確認してください。");
    }
  } catch (error) {
    arenaText("arena-message", error.name === "AbortError" ? "応答待ちを終了しました。再読み込みして処理結果を確認してください。" : error.message);
  } finally {
    arenaBusy = false;
    document.querySelectorAll(".arena-interface button").forEach(button => { button.disabled = false; });
    renderArena();
  }
}

for (const button of document.querySelectorAll("[data-difficulty]")) button.addEventListener("click", () => arenaAction({action: "difficulty", value: button.dataset.difficulty}));
for (const button of document.querySelectorAll("[data-mode]")) button.addEventListener("click", () => { arenaMode = button.dataset.mode; renderArena(); });
arenaById("request-form").addEventListener("submit", event => {
  event.preventDefault();
  try { arenaAction({action: "attack-request", attempt: arenaState.attack.id, sequence: arenaState.attack.count,
    path: arenaById("request-path").value, method: arenaById("request-method").value, fields: JSON.parse(arenaById("request-fields").value)}); }
  catch { arenaText("arena-message", "入力項目をJSONで記述してください。例：{\"q\": \"guide\"}"); }
});
arenaById("attack-finish").addEventListener("click", () => arenaAction({action: "attack-finish", attempt: arenaState.attack.id}));
arenaById("copy-form").addEventListener("submit", event => {
  event.preventDefault();
  arenaAction({action: "defend-copy", project: arenaById("defend-project").value, scenario: arenaById("defend-scenario").value, path: arenaById("defend-path").value});
});
arenaById("defend-start").addEventListener("click", () => arenaAction({action: "defend-start", attempt: arenaState.defend.id}));
arenaById("policy-form").addEventListener("submit", event => {
  event.preventDefault();
  try { arenaAction({action: "defend-assess", attempt: arenaState.defend.id, policy: JSON.parse(arenaById("defend-policy").value)}); }
  catch { arenaText("arena-message", "遮断ルールをJSONで記述してください。"); }
});
arenaById("guide-hint").addEventListener("click", () => arenaAction({action: "hint", mode: arenaMode}));

// タイマーは1本。非表示・ページ離脱時は停止し、復帰時はサーバーの基準時刻もリセットする。
let pulseTimer = null;
let pulseRunning = false;
let resetPresence = true;
let pageActive = true;
function schedulePulse() {
  clearTimeout(pulseTimer); pulseTimer = null;
  if (!pageActive || document.hidden || pulseRunning) return;
  pulseTimer = setTimeout(pulse, 3000);
}
async function pulse() {
  if (!pageActive || document.hidden || pulseRunning) return;
  pulseRunning = true;
  try {
    if (!arenaBusy && arenaState.difficulty === "hard" && arenaState.defend?.status === "armed") {
      const paused = resetPresence;
      await arenaAction({action: "pulse", view: arenaView, paused}, true);
      resetPresence = false;
    }
  } finally { pulseRunning = false; schedulePulse(); }
}
document.addEventListener("visibilitychange", () => { resetPresence = true; schedulePulse(); });
window.addEventListener("pagehide", () => { pageActive = false; clearTimeout(pulseTimer); });
window.addEventListener("pageshow", () => { pageActive = true; resetPresence = true; schedulePulse(); });
renderArena(); schedulePulse();
