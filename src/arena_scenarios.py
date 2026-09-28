"""架空の演習定義。追加時は同じ辞書形式とターゲットファイルを登録する。"""

DIFFICULTIES = ("easy", "normal", "hard")

FAMILIES = (
    ("records", "Lumen Archive", "記録サービス", "記録を整理する架空の共有サービス。",
     "別チームの非公開記録に置かれた演習マーカーを取得する。", "オブジェクト単位の認可不足",
     ["トップの案内から公開記録を開き、URLを観察しましょう。", "番号を指定できることと、その記録を見る権限があることは別です。"],
     "IDを受け取った後、ログイン利用者と記録の所有者をサーバー側で照合する。", [4, 7, 11]),
    ("exports", "Nacre Reports", "帳票サービス", "帳票の閲覧と出力を扱う架空の業務画面。",
     "内部向け帳票に置かれた演習マーカーを取得する。", "HTTPメソッド間の認可漏れ",
     ["応答に書かれたURL・HTTPメソッド・入力項目を確認しましょう。", "GETが拒否されてもPOSTに同じ権限確認があるとは限りません。"],
     "画面の表示制限だけでなく、GET・POSTの処理それぞれで権限を確認する。", [4, 7, 11]),
    ("search", "Vela Catalog", "検索サービス", "資料名から架空のカタログを検索する画面。",
     "検索から内部資料に置かれた演習マーカーを取得する。", "SQLへの入力文字列の連結",
     ["検索語を変えたときの結果やエラーを観察しましょう。", "入力がSQLの値ではなく命令の一部になると、検索条件の意味が変わります。"],
     "SQL文字列へ入力を連結せず、プレースホルダーで値として渡す。公開条件と認可も維持する。", [8, 11]),
    ("support", "Orin Monitor", "稼働情報サービス", "架空のアプリケーションの稼働情報を提供する画面。",
     "管理者用の詳細情報に置かれた演習マーカーを取得する。", "診断情報へのアクセス制御不足",
     ["公開の稼働情報にある参照先を確認しましょう。", "診断用URLも公開APIです。詳細表示に権限チェックがあるか観察しましょう。"],
     "診断用エンドポイントに認可を設け、不要な内部情報は本番の応答から除く。", [4, 10, 11, 12]),
)

SCENARIOS = {}
for difficulty in DIFFICULTIES:
    for family, title, kind, description, objective, vulnerability, hints, advice, learn in FAMILIES:
        key = f"{difficulty}-{family}"
        SCENARIOS[key] = {
            "id": key, "difficulty": difficulty, "title": title, "target_type": kind,
            "description": description, "objective": objective, "family": family,
            "initial_state": {}, "vulnerability": vulnerability,
            "success_condition": "response_marker", "failure_condition": "request_limit_or_finish",
            "request_limit": {"easy": 14, "normal": 10, "hard": 12}[difficulty],
            "easy_hints": hints, "related_learn": learn, "post_failure_advice": advice,
        }

DEFEND_SCENARIOS = {
    "repeated-reads": {
        "id": "repeated-reads", "title": "不審な取得要求の封じ込め", "method": "GET", "data": {},
        "description": "同じ画面への不審な反復要求を、正規利用者の閲覧を維持しながら遮断する。",
        "easy_hints": ["ACCESS LOGのsourceとmethodを比較しましょう。sourceは演習内だけの送信元ラベルです。",
                       "正規のvisitorを残して、不審なprobeのラベルだけをblocked_sourcesへ設定できます。"],
        "related_learn": [4, 11, 12],
        "advice": "送信元と要求の繰り返しを見落とすと、不要な処理がアプリへ届き続けます。ログを比較して入口で封じ込め、Buildではレート制限・監視を検討しましょう。",
    },
    "oversized-input": {
        "id": "oversized-input", "title": "過大入力の封じ込め", "method": "POST", "data": {"body": "X" * 4096},
        "description": "過大なフォーム入力を拒否し、通常の閲覧を維持する。",
        "easy_hints": ["ACCESS LOGのbytesとmethodを確認しましょう。画面のmaxlengthだけでは直接のPOSTを制限できません。",
                       "max_bodyで入口の入力サイズを制限できます。Build側でも長さ・型・値を検証しましょう。"],
        "related_learn": [4, 7, 11, 12],
        "advice": "ブラウザーの入力制限だけでは直接送信される過大なデータを防げません。入口のサイズ制限とアプリ内の検証を分けて考え、Buildでサーバー側の制限を確認しましょう。",
    },
}
