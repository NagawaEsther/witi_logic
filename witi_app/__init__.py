from email import message
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from witi_app.extensions import db, bcrypt
from witi_app.extensions import migrate
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask import send_from_directory
import os  
from flask_cors import CORS
import africastalking

#importing blueprints
from witi_app.controllers.user_controller import user_bp
from witi_app.controllers.program_controller import program_bp
from witi_app.controllers.events_controller import event_bp
from witi_app.controllers.gallery_controllers import gallery_bp
from witi_app.controllers.contact_inquiry_controller import contact_inquiry_bp
from witi_app.controllers.donations_controller import donation_bp


# Initialize Africa's Talking SDK
africastalking.initialize(username='livewell_medical_app', api_key='atsk_c6f2d52c6f637e9ff0183d8d802dc7b9771902b4009ed1dfdba398c1b4370c6e8565eece')
sms = africastalking.SMS

# Function to send SMS
def send_sms(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        return {'error': str(e)}



def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Initialize JWTManager with secret key
    app.config['JWT_SECRET_KEY'] = '12345'  
    jwt = JWTManager(app)

    # Configure token expiration time 
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  

    # Importing models
    from witi_app.models import user
    from witi_app.models import gallery
    from witi_app.models import program
    from witi_app.models import events
    from witi_app.models import contact_inquiry
    from witi_app.models import donations

    # Import blueprints
    from witi_app.controllers.user_controller import User

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(program_bp, url_prefix='/api/v1/program')
    app.register_blueprint(event_bp, url_prefix='/api/v1/event')
    app.register_blueprint(gallery_bp, url_prefix='/api/v1/gallery')
    app.register_blueprint(contact_inquiry_bp, url_prefix='/api/v1/contact-inquiry')
    app.register_blueprint(donation_bp, url_prefix='/api/v1/donation')

    # Serve Swagger JSON file
    @app.route('/swagger.json')
    def serve_swagger_json():
        try:
            return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')
        except FileNotFoundError:
            return jsonify({"message": "Swagger JSON file not found"}), 404

    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'  
    API_URL = '/swagger.json'  
    
    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={  
            'app_name': "witi_At_app"
        }
    )
    
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint)

    @app.route('/')
    def home():
        return 'Welcome to Women in technology website!'

    # Routes for protected resources
    @app.route('/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        return jsonify(logged_in_as=current_user_id), 200
    
    # Example route to send SMS
    @app.route('/send-sms', methods=['POST'])
    def send_sms_route():
        data = request.get_json()
        phone_number = data.get('phone_numbers')
        message = data.get('message')

        if not phone_number or not message:
            return jsonify({'error': 'Phone numbers and messages are required'}), 400

        # Iterate over phone numbers and send SMS
        responses = []
        for phone_number in phone_number:
            response = send_sms(phone_number, message)
            responses.append({'number': phone_number, 'response': response})
        
        return jsonify({'status': 'SMS sent', 'details': responses}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
