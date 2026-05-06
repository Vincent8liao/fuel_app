import os

from flask import Flask, render_template

from database.db import init_db
from fuel import fuel_bp
from users import users_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FUEL_APP_SECRET_KEY", "dev-change-this-secret-key")

    init_db()

    app.register_blueprint(users_bp)
    app.register_blueprint(fuel_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
