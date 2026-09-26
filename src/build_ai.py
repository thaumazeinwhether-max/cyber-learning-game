"""開発ナビゲーターの境界。未設定時は通信しないルール型ガイド。"""

class LocalGuide:
    mode = "ローカルガイド（生成AI未接続）"

    def reply(self, context, history, question):
        text = (question + " " + context["active_file"]).lower()
        code = context["code"]
        if any(word in text for word in ("エラー", "error", "動か", "syntax")):
            return ("まず実行ログの最後の行を確認しましょう。ファイル名・行番号・エラー名が手掛かりです。\n"
                    "次に、その行の少し前からインデント、括弧、変数名を確認します。\n"
                    "Learn第5訓練の例外とデバッグにつながります。具体的なエラー文も質問に含めてください。")
        if any(word in text for word in ("db", "sql", "保存", "データベース")):
            return ("入力を保存するには、フォーム → Flask → DB → 画面という流れを考えます。\n"
                    "まず保存する項目と型をschema.sqlに書き、app.pyで受け取る値を確認しましょう。\n"
                    "SQLへ値を渡すときは文字列結合を避け、プレースホルダーを使います。\n"
                    '例: db.execute("INSERT INTO entries (body) VALUES (?)", (body,))\n'
                    "Learn第8訓練のINSERT・安全なDBアクセスと対応します。")
        if any(word in text for word in ("フォーム", "post", "入力", "request")):
            has_form = "request.form" in code
            return ("フォームのnameが、Flaskで入力を取り出すキーになります。\n"
                    "HTMLのmethodとnameを確認し、RouteがPOSTを受け付けるか見てみましょう。\n"
                    + ("今のファイルにはrequest.formがあります。HTML側と名前を見比べましょう。\n" if has_form else "")
                    + '例: body = request.form.get("body", "")\n'
                    "Learn第4訓練のPOSTと、第7訓練のrequest.formを組み合わせる場面です。")
        if any(word in text for word in ("route", "ルート", ".py", "flask")):
            return ("URLとPythonの関数を結ぶのがRouteです。まず、どのURLで何を表示したいか決めましょう。\n"
                    '小さな例:\n@app.route("/about")\ndef about():\n    return "このアプリについて"\n'
                    'app.pyへ追加し、トップ画面に <a href="/about">紹介</a> を置きます。FlaskモードでRUN後、そのリンクから移動します。Learn第7訓練のRouteを使っています。\n'
                    "Flask実行環境が未設定の場合はコードを保存できますが、Pythonは実行されません。")
        if ".css" in text or any(word in text for word in ("色", "余白", "レイアウト")):
            return ("見た目はHTMLのclassとCSSのセレクタを対応させて調整します。\n"
                    "まず変えたい要素を1つ選び、色か余白のどちらかを変更してRUNしましょう。\n"
                    "例: .card { padding: 32px; }\nLearn第6訓練のCSSとボックスの考え方を使っています。")
        if ".js" in text or "javascript" in text:
            return ("JavaScriptは入力やクリックに応じてDOMを変更する役割です。\n"
                    "まず対象の要素とイベントを書き出しましょう。Learn第6訓練のDOMと対応します。\n"
                    "初期版ではJavaScriptを編集・保存できますが、保護プレビュー内では実行しません。")
        return (f'「{context["project_name"]}」の{context["active_file"]}を編集中です。\n'
                "まず誰が何のために使う画面かを決め、見出しと説明を自分の言葉に変えてみましょう。\n"
                "HTMLで構造、CSSで見た目、Flaskでサーバー処理を分担します。Learn第6・7訓練とつながります。\n"
                "このガイドは生成AIではなく、現在のファイルと質問のキーワードに応じた案内です。"
                "理解できない質問には、目的と困っている箇所を具体的に書いてみてください。")


def ask_guide(provider, project, active_file, question):
    context = {
        "project_name": project["name"], "active_file": active_file,
        "code": project["files"].get(active_file, "")[:6000],
    }
    guide = provider or LocalGuide()
    try:
        answer = guide.reply(context, project["chat"][-10:], question)
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Empty guide response")
        return {"answer": answer[:6000], "mode": guide.mode}
    except Exception:
        fallback = LocalGuide()
        return {"answer": "AI接続を利用できないためローカルガイドで案内します。\n" + fallback.reply(context, [], question),
                "mode": fallback.mode}
