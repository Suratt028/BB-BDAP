from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Task
from ..extensions import db

task_bp = Blueprint("task", __name__)

@task_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()

    task = Task(title=data["title"], user_id=user_id)
    db.session.add(task)
    db.session.commit()

    return jsonify({"msg": "Task created"}), 201


@task_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()

    return jsonify([
        {"id": t.id, "title": t.title}
        for t in tasks
    ])


@task_bp.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()

    task.title = data["title"]
    db.session.commit()

    return jsonify({"msg": "Updated"})


@task_bp.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": "Deleted"})
