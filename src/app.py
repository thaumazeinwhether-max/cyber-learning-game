import secrets

from flask import Flask, render_template

from src.learn_routes import learn


app = Flask(__name__)
# 進捗は署名付きCookieに保存する。再起動後は進捗が初期化される開発版。
app.secret_key = secrets.token_hex(32)
app.register_blueprint(learn)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
