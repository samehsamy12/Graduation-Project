from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models.horse import Horse
from app.models.family_tree import FamilyTree
from app.utils.jwt_utils import token_required

family_tree_bp = Blueprint("family_tree", __name__)

@family_tree_bp.route("/add-family-member", methods=["POST"])
@token_required
def add_family_member():
    data = request.get_json()
    parent_id = data.get("parent_id")
    child_name = data.get("child_name")

    if not child_name:
        return jsonify({"message": "Child name is required"}), 400

    if parent_id:
        parent = FamilyTree.query.get(parent_id)
        if not parent or parent.owner_id != g.user_id:
            return jsonify({"message": "Parent not found or unauthorized"}), 404
    else:
        # If no parent_id, create a new root linked to a horse
        horse_id = data.get("horse_id")
        if not horse_id:
            return jsonify({"message": "Horse ID is required for root node"}), 400
        horse = Horse.query.get(horse_id)
        if not horse or horse.owner_id != g.user_id:
            return jsonify({"message": "Horse not found or unauthorized"}), 404
        parent = FamilyTree.query.filter_by(horse_id=horse_id, is_root=True).first()
        if parent:
            return jsonify({"message": "Root node already exists for this horse"}), 400

    new_member = FamilyTree(name=child_name, parent_id=parent_id, horse_id=horse_id if not parent_id else None, is_root=bool(not parent_id))
    db.session.add(new_member)
    db.session.commit()

    return jsonify({"message": "Family member added", "id": new_member.id, "member": new_member.to_dict()}), 201

@family_tree_bp.route("/get-family-tree/<int:horse_id>", methods=["GET"])
@token_required
def get_family_tree(horse_id):
    horse = Horse.query.get(horse_id)
    if not horse or horse.owner_id != g.user_id:
        return jsonify({"message": "Horse not found or unauthorized"}), 404

    root = FamilyTree.query.filter_by(horse_id=horse_id, is_root=True).first()
    if not root:
        return jsonify({"message": "No family tree for this horse"}), 404

    def build_tree(node):
        if not node:
            return None
        return node.to_dict()

    tree = build_tree(root)
    return jsonify(tree), 200