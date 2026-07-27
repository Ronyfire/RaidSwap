from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)

    import models  # noqa: F401 — registra los modelos en el metadata de SQLAlchemy

    from routes.raiders import raiders_bp
    from routes.bosses import bosses_bp
    from routes.responsibilities import responsibilities_bp
    from routes.positions import positions_bp
    from routes.mechanic_profiles import mechanic_profiles_bp
    from routes.assignments import assignments_bp

    app.register_blueprint(raiders_bp)
    app.register_blueprint(bosses_bp)
    app.register_blueprint(responsibilities_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(mechanic_profiles_bp)
    app.register_blueprint(assignments_bp)

    @app.get("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", db="connected")
        except Exception as e:
            return jsonify(status="error", db=str(e)), 500

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Tables created.")

    @app.cli.command("seed-venomous-abyss")
    def seed_venomous_abyss_command():
        from seeds.venomous_abyss import seed_venomous_abyss

        seed_venomous_abyss()
        print("Seeded The Venomous Abyss (8 bosses).")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
