from flask import Flask, request, jsonify
from db import db
from models import User
from redis_queue import publish_event
import os

postgres_user = os.environ.get('POSTGRES_USER', 'appuser')
postgres_password = os.environ.get('POSTGRES_PASSWORD', 'apppass')
postgres_url = os.environ.get('POSTGRES_URL', 'localhost')

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{postgres_user}:{postgres_password}@{postgres_url}:5432/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/events", methods=["POST"])
def create_event():
    data = request.json

    event_type = data.get("type")
    source = data.get("source")
    description = data.get("description")

    if not event_type or not source or not description:
        return jsonify({"error": "type, source and description are required"}), 400

    publish_event(event_type, source, description)

    return jsonify({
        "type": event_type,
        "source": source,
        "description": description
    }), 201


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    user = User(
        name=data["name"],
        email=data["email"]
    )

    db.session.add(user)
    db.session.commit()

    publish_event("USER_CREATED", str(user.id), f"User {user.name} created")

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email
    }), 201

@app.route("/users/<uuid:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    return jsonify({
        "id": str(user.id),
        "name": user.name,
        "email": user.email
    }), 201

@app.route("/users/<uuid:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    publish_event("USER_DELETED", str(user_id), f"User {user_id} deleted")

    return "", 204

@app.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()

    return [
        {
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }
        for user in users
    ], 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
