/* 初回案内のみ。プロジェクトのコード・実行状態・チャットには触れない。 */
"use strict";

(() => {
  const fields = {purpose: "アプリの目的", features: "主要機能の候補", learn: "関連するLearn", first_step: "最初の一歩"};
  function showNotes(plan) {
    const body = byId("onboarding-notes-body");
    body.replaceChildren();
    for (const [key, label] of Object.entries(fields)) {
      if (!plan[key]) continue;
      const heading = document.createElement("strong");
      const text = document.createElement("p");
      heading.textContent = label;
      text.textContent = plan[key];
      body.append(heading, text);
    }
    byId("onboarding-notes").hidden = !Object.values(plan).some(Boolean);
  }
  showNotes(initial.onboarding.plan);
  if (!initial.onboarding.required) return;
  const dialog = byId("onboarding-dialog");
  const status = byId("onboarding-status");
  let organizing = false;
  let finishing = false;
  let closed = false;
  let hasPlan = false;
  dialog.showModal();

  byId("onboarding-form").addEventListener("submit", async event => {
    event.preventDefault();
    if (organizing || finishing || closed) return;
    const idea = byId("onboarding-idea").value.trim();
    if (!idea || idea.length > 1500) {
      status.textContent = "作りたいものを1〜1500文字で入力してください。";
      return;
    }
    organizing = true;
    byId("onboarding-organize").disabled = true;
    byId("onboarding-start").disabled = true;
    status.textContent = "AI CORE / アイデアを整理しています…";
    try {
      const result = await api("/build/onboarding/plan", {idea}, 40000);
      if (closed) return; // 応答を待たずにスキップした場合、遅れて画面を戻さない。
      for (const key of Object.keys(fields)) byId(`plan-${key}`).value = result.plan[key];
      hasPlan = true;
      byId("onboarding-form").hidden = true;
      byId("onboarding-intro").hidden = true;
      byId("onboarding-proposal").hidden = false;
      byId("onboarding-start").hidden = false;
      status.textContent = `${result.mode} / ${result.notice || "提案を確認して、自由に編集してください。"}`;
      byId("plan-purpose").focus();
    } catch (error) {
      if (!closed) status.textContent = "整理結果を受け取れませんでした。入力は残しています。再送信するか、スキップして開発を始められます。";
    } finally {
      organizing = false;
      byId("onboarding-organize").disabled = false;
      byId("onboarding-start").disabled = false;
    }
  });

  byId("onboarding-revise").addEventListener("click", () => {
    if (finishing) return;
    hasPlan = false;
    byId("onboarding-form").hidden = false;
    byId("onboarding-intro").hidden = false;
    byId("onboarding-proposal").hidden = true;
    byId("onboarding-start").hidden = true;
    status.textContent = "入力を変更して、もう一度整理できます。";
    byId("onboarding-idea").focus();
  });

  async function finish(action) {
    if (finishing || closed || (action === "start" && (!hasPlan || organizing))) return;
    finishing = true;
    byId("onboarding-start").disabled = true;
    byId("onboarding-skip").disabled = true;
    const plan = {};
    if (action === "start") {
      for (const key of Object.keys(fields)) plan[key] = byId(`plan-${key}`).value;
    }
    try {
      const result = await api("/build/onboarding/complete", {action, plan}, 15000);
      closed = true;
      showNotes(result.onboarding.plan);
      dialog.close();
      byId("code-editor").focus();
    } catch (error) {
      status.textContent = "完了状態を保存できませんでした。内容は残っています。接続を確認して、もう一度開始またはスキップしてください。";
    } finally {
      finishing = false;
      byId("onboarding-start").disabled = false;
      byId("onboarding-skip").disabled = false;
    }
  }
  byId("onboarding-start").addEventListener("click", () => finish("start"));
  byId("onboarding-skip").addEventListener("click", () => finish("skip"));
  dialog.addEventListener("cancel", event => { event.preventDefault(); finish("skip"); });
})();
