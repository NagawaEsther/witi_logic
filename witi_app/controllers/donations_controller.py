from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from witi_app.models.donations import Donation
from witi_app import db
from datetime import datetime
from functools import wraps

donation_bp = Blueprint('donation', __name__, url_prefix='/api/v1/donation')

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

# Create a new donation
@donation_bp.route('/create', methods=['POST'])
def create_donation():
    try:
        data = request.get_json()
        donor_name = data.get('donor_name')
        donor_email = data.get('donor_email')
        donation_amount_usd = data.get('donation_amount_usd')
        donation_amount_ugx = data.get('donation_amount_ugx')
        payment_method = data.get('payment_method')
        screenshot_path = data.get('screenshot_path')
        message = data.get('message')

        if not donor_name or not donor_email or not payment_method:
            return jsonify({'error': 'Missing required fields (donor_name, donor_email, payment_method)'}), 400

        new_donation = Donation(
            donor_name=donor_name,
            donor_email=donor_email,
            donation_amount_usd=donation_amount_usd,
            donation_amount_ugx=donation_amount_ugx,
            payment_method=payment_method,
            screenshot_path=screenshot_path,
            message=message
        )

        db.session.add(new_donation)
        db.session.commit()

        donation_data = {
            'id': new_donation.id,
            'donor_name': new_donation.donor_name,
            'donor_email': new_donation.donor_email,
            'donation_amount_usd': new_donation.donation_amount_usd,
            'donation_amount_ugx': new_donation.donation_amount_ugx,
            'payment_method': new_donation.payment_method,
            'screenshot_path': new_donation.screenshot_path,
            'donation_date': new_donation.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'message': new_donation.message,
        }

        return jsonify({'message': 'Donated successfully', 'donation': donation_data}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get all donations
@donation_bp.route('/donations', methods=['GET'])
@admin_required
def get_all_donations():
    try:
        donations = Donation.query.all()
        output = []
        for donation in donations:
            donation_data = {
                'id': donation.id,
                'donor_name': donation.donor_name,
                'donor_email': donation.donor_email,
                'donation_amount_usd': donation.donation_amount_usd,
                'donation_amount_ugx': donation.donation_amount_ugx,
                'payment_method': donation.payment_method,
                'screenshot_path': donation.screenshot_path,
                'donation_date': donation.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'message': donation.message,
            }
            output.append(donation_data)
        return jsonify({'donations': output})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a specific donation
@donation_bp.route('/donation/<int:id>', methods=['GET'])
@admin_required
def get_donation(id):
    try:
        donation = Donation.query.get_or_404(id)
        donation_data = {
            'id': donation.id,
            'donor_name': donation.donor_name,
            'donor_email': donation.donor_email,
            'donation_amount_usd': donation.donation_amount_usd,
            'donation_amount_ugx': donation.donation_amount_ugx,
            'payment_method': donation.payment_method,
            'screenshot_path': donation.screenshot_path,
            'donation_date': donation.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'message': donation.message,
        }
        return jsonify(donation_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a donation
@donation_bp.route('/donation/<int:id>', methods=['PUT'])
@admin_required
def update_donation(id):
    try:
        donation = Donation.query.get_or_404(id)
        data = request.get_json()

        donation.donor_name = data.get('donor_name', donation.donor_name)
        donation.donor_email = data.get('donor_email', donation.donor_email)
        donation.donation_amount_usd = data.get('donation_amount_usd', donation.donation_amount_usd)
        donation.donation_amount_ugx = data.get('donation_amount_ugx', donation.donation_amount_ugx)
        donation.payment_method = data.get('payment_method', donation.payment_method)
        donation.screenshot_path = data.get('screenshot_path', donation.screenshot_path)
        donation.message = data.get('message', donation.message)

        db.session.commit()

        donation_data = {
            'id': donation.id,
            'donor_name': donation.donor_name,
            'donor_email': donation.donor_email,
            'donation_amount_usd': donation.donation_amount_usd,
            'donation_amount_ugx': donation.donation_amount_ugx,
            'payment_method': donation.payment_method,
            'screenshot_path': donation.screenshot_path,
            'donation_date': donation.donation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'message': donation.message,
        }

        return jsonify({
            'message': 'Donation updated successfully',
            'donation': donation_data
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete a donation
@donation_bp.route('/donation/<int:id>', methods=['DELETE'])
@admin_required
def delete_donation(id):
    try:
        donation = Donation.query.get_or_404(id)
        db.session.delete(donation)
        db.session.commit()
        return jsonify({'message': 'Donation deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete donation', 'details': str(e)}), 500
