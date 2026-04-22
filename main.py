import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from auth import require_auth
from db import db
from models import User
from redis_queue import publish_event


def create_app():
    app = Flask(__name__)
    CORS(app)

    postgres_user = os.environ.get("POSTGRES_USER", "appuser")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "apppass")
    postgres_url = os.environ.get("POSTGRES_URL", "localhost")

    db_uri = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", db_uri)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.route("/events", methods=["POST"])
    @require_auth()
    def create_event():
        data = request.json or {}
        required = ("type", "source", "description")

        if not all(data.get(k) for k in required):
            return jsonify({"error": "type, source and description are required"}), 400

        payload = {k: data[k] for k in required}
        publish_event(payload["type"], payload["source"], payload["description"])
        return jsonify(payload), 201

    @app.route("/users", methods=["POST"])
    @require_auth()
    def create_user():
        data = request.json
        user = User(name=data["name"], email=data["email"])
        db.session.add(user)
        db.session.commit()

        publish_event("USER_CREATED", str(user.id), f"User {user.name} created")
        return jsonify(user.to_dict()), 201

    @app.route("/users", methods=["GET"])
    @require_auth()
    def list_users():
        return jsonify([u.to_dict() for u in User.query.all()]), 200

    @app.route("/users/<uuid:user_id>", methods=["GET"])
    @require_auth()
    def get_user(user_id):
        return jsonify(User.query.get_or_404(user_id).to_dict()), 200

    @app.route("/users/<string:email>/email", methods=["GET"])
    @require_auth()
    def get_user_by_email(email):
        return jsonify(User.query.filter_by(email=email).first_or_404().to_dict()), 200

    @app.route("/users/<uuid:user_id>", methods=["DELETE"])
    @require_auth()
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        publish_event("USER_DELETED", str(user_id), f"User {user_id} deleted")
        return "", 204

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
