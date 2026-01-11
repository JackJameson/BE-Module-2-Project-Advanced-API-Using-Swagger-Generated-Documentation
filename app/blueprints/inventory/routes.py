from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp

@inventory_bp.route('/', methods=['POST'])
def create_inventory_item():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_inventory = Inventory(**inventory_data)
    db.session.add(new_inventory)
    db.session.commit()

    return inventory_schema.jsonify(new_inventory), 201

@inventory_bp.route('/', methods=['GET'])
def get_inventory_items():
    query = select(Inventory)
    parts = db.session.scalars(query).all()
    return inventories_schema.jsonify(parts), 200

@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
def get_inventory_item(inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if part:
        return inventory_schema.jsonify(part), 200
    return jsonify({"error": "Inventory item not found"}), 404

@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
def update_inventory_item(inventory_id):
    part = db.session.get(Inventory, inventory_id)

    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in inventory_data.items():
        setattr(part, key, value)

    db.session.commit()
    return inventory_schema.jsonify(part), 200

@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
def delete_inventory_item(inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Inventory item id: {inventory_id}, deleted successfully"}), 200



