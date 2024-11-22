from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from witi_app.models.stories import Story
from witi_app import db
from functools import wraps

stories_bp = Blueprint('stories', __name__, url_prefix='/api/v1/stories')

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

# Create a new story
@stories_bp.route('/create', methods=['POST'])
@admin_required  # Ensuring only admin can create a story
def create_story():
    data = request.json
    try:
        new_story = Story(
            title=data.get('title'),
            description=data.get('description'),
            image=data.get('image'),
            video_url=data.get('video_url'),
        )
        db.session.add(new_story)
        db.session.commit()
        return jsonify({"message": "Story created successfully", "story": new_story.to_dict()}), 201
    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({"error": str(e)}), 400

# Get all stories
@stories_bp.route('/get_all', methods=['GET'])
def get_stories():
    try:
        stories = Story.query.all()
        return jsonify([story.to_dict() for story in stories]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get a specific story by ID
@stories_bp.route('/get/<int:story_id>', methods=['GET'])
def get_story(story_id):
    story = Story.query.get(story_id)
    if story:
        return jsonify(story.to_dict()), 200
    else:
        return jsonify({"error": "Story not found"}), 404

# Update a story
@stories_bp.route('/update/<int:story_id>', methods=['PUT'])
@admin_required  # Only admin can update a story
def update_story(story_id):
    data = request.json
    story = Story.query.get(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404

    try:
        story.title = data.get('title', story.title)
        story.description = data.get('description', story.description)
        story.image = data.get('image', story.image)
        story.video_url = data.get('video_url', story.video_url)
        db.session.commit()
        return jsonify({"message": "Story updated successfully", "story": story.to_dict()}), 200
    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({"error": str(e)}), 400

# Delete a story
@stories_bp.route('/delete/<int:story_id>', methods=['DELETE'])
@admin_required  # Only admin can delete a story
def delete_story(story_id):
    story = Story.query.get(story_id)
    if not story:
        return jsonify({"error": "Story not found"}), 404

    try:
        db.session.delete(story)
        db.session.commit()
        return jsonify({"message": "Story deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback on error
        return jsonify({"error": str(e)}), 500
