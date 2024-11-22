from flask import Blueprint, request, jsonify
from witi_app import db
from witi_app.models.events import Event
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

event_bp = Blueprint('event', __name__, url_prefix='/api/v1/event')

# Admin required decorator
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_info = get_jwt_identity()
        if user_info['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Get all events
@event_bp.route('/events', methods=['GET'])
def get_all_events():
    events = Event.query.all()
    output = []
    for event in events:
        event_data = {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'date': event.date.strftime('%Y-%m-%d'),
            'image_url': event.image_url,
            'rsvp_link': event.rsvp_link
        }
        output.append(event_data)
    return jsonify({'events': output})

# Get a specific event
@event_bp.route('/event/<int:id>', methods=['GET'])
@admin_required
def get_event(id):
    event = Event.query.get_or_404(id)
    event_data = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d'),
        'image_url': event.image_url,
        'rsvp_link': event.rsvp_link
    }
    return jsonify(event_data)

# Create a new event
@event_bp.route('/create', methods=['POST'])
@admin_required
def create_event():
    try:
        data = request.get_json()

        # Create new event with the necessary fields
        new_event = Event(
            name=data['name'],
            description=data['description'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            image_url=data['image_url'],
            rsvp_link=data.get('rsvp_link')  # Handle the optional RSVP link
        )

        db.session.add(new_event)
        db.session.commit()

        event_data = {
            'id': new_event.id,
            'name': new_event.name,
            'description': new_event.description,
            'date': new_event.date.strftime('%Y-%m-%d'),
            'image_url': new_event.image_url,
            'rsvp_link': new_event.rsvp_link
        }

        return jsonify({
            'message': 'Event created successfully',
            'event': event_data
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Update an event
@event_bp.route('/event/<int:id>', methods=['PUT'])
@admin_required
def update_event(id):
    try:
        event = Event.query.get_or_404(id)
        data = request.get_json()

        # Update fields, ensuring that we handle new fields
        event.name = data.get('name', event.name)
        event.description = data.get('description', event.description)
        event.date = datetime.strptime(data['date'], '%Y-%m-%d') if 'date' in data else event.date
        event.image_url = data.get('image_url', event.image_url)
        event.rsvp_link = data.get('rsvp_link', event.rsvp_link)

        db.session.commit()

        event_data = {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'date': event.date.strftime('%Y-%m-%d'),
            'image_url': event.image_url,
            'rsvp_link': event.rsvp_link
        }

        return jsonify({
            'message': 'Event updated successfully',
            'event': event_data
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete an event
@event_bp.route('/event/<int:id>', methods=['DELETE'])
@admin_required
def delete_event(id):
    try:
        event = Event.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete event', 'details': str(e)}), 500
