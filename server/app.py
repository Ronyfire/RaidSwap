from flask import Flask, jsonify
from sqlalchemy import text

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    import models  # noqa: F401 — registra los modelos en el metadata de SQLAlchemy

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", db="connected")
        except Exception as e:
            return jsonify(status="error", db=str(e)), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
