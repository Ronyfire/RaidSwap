from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, verify_jwt_in_request
from sqlalchemy import text

from config import Config
from extensions import db

# Single admin/raid-leader gate for the whole API — not per-route, per-resource
# ACLs (no multi-tenant, no roles beyond "logged in or not" — see
# projects/agent-architecture.md). Everything except these paths requires a
# valid JWT.
PUBLIC_PATHS = {"/health", "/api/auth/register", "/api/auth/login"}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)
    JWTManager(app)

    import models  # noqa: F401 — registra los modelos en el metadata de SQLAlchemy

    from routes.auth import auth_bp
    from routes.raiders import raiders_bp
    from routes.bosses import bosses_bp
    from routes.responsibilities import responsibilities_bp
    from routes.positions import positions_bp
    from routes.mechanic_profiles import mechanic_profiles_bp
    from routes.assignments import assignments_bp
    from routes.agent import agent_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(raiders_bp)
    app.register_blueprint(bosses_bp)
    app.register_blueprint(responsibilities_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(mechanic_profiles_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(agent_bp)

    @app.before_request
    def require_auth():
        if request.method == "OPTIONS" or request.path in PUBLIC_PATHS:
            return None
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify(error="Authentication required"), 401

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
