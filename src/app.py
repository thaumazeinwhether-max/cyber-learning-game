from datetime import timedelta

from flask import Flask, render_template, session

from src.learn_routes import learn
from src.session_key import load_session_key


def create_app(instance_path=None):
    """Flaskアプリを作る。テストでは独立した鍵保存先を指定できる。"""
    options = {"instance_path": str(instance_path)} if instance_path else {}
    application = Flask(__name__, **options)
    application.secret_key = load_session_key(application.instance_path)
    application.permanent_session_lifetime = timedelta(days=90)
    application.register_blueprint(learn)

    @application.before_request
    def keep_progress_after_browser_close():
        session.permanent = True

    @application.route("/")
    def index():
        return render_template("index.html")

    return application


app = create_app()


if __name__ == "__main__":
    app.run()
