from .schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_service_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, Mechanic, db, Inventory
from . import service_tickets_bp
from app.blueprints.mechanics.schemas import mechanic_schema
from app.blueprints.inventory.schemas import inventory_schema
from app.utils.util import token_required


@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_service_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_service_ticket), 201

@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.scalars(query).all()
    return service_tickets_schema.jsonify(service_tickets), 200

@service_tickets_bp.route('/<ticket_id>/assign-mechanic/<mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    if service_ticket and mechanic:
        if mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            db.session.commit()
            return jsonify({
                "message": "successfully assigned mechanic to service ticket",
                "service_ticket": service_ticket_schema.dump(service_ticket),
                "mechanic": mechanic_schema.dump(mechanic)
            }), 200
        return jsonify({"error": "Mechanic already assigned to this service ticket"}), 400
    return jsonify({"error": "Service ticket or mechanic not found"}), 404

@service_tickets_bp.route('/<ticket_id>/remove-mechanic/<mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if service_ticket and mechanic:
        if mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
            db.session.commit()
            return jsonify({
                "message": "successfully removed mechanic from service ticket",
                "service_ticket": service_ticket_schema.dump(service_ticket),
                "mechanic": mechanic_schema.dump(mechanic)
            }), 200
        return jsonify({"error": "Mechanic not assigned to this service ticket"}), 400
    return jsonify({"error": "Service ticket or mechanic not found"}), 404


@service_tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_service_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200

@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def edit_service_ticket(ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    for mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for mechanic_id in service_ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return return_service_ticket_schema.jsonify(service_ticket), 200

@service_tickets_bp.route('/<int:ticket_id>/add-part/<int:part_id>', methods=['POST'])
def add_part_to_ticket(ticket_id, part_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    part = db.session.get(Inventory, part_id)

    if service_ticket and part:
        if part not in service_ticket.parts:
            service_ticket.parts.append(part)
            db.session.commit()
            return jsonify({
                "message": "successfully added part to service ticket",
                "service_ticket": service_ticket_schema.dump(service_ticket),
                "part": inventory_schema.dump(part)
            }), 200
        return jsonify({"error": "Part already added to this service ticket"}), 400
    return jsonify({"error": "Service ticket or part not found"}), 404