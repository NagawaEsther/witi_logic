from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
import africastalking
from dotenv import load_dotenv

from witi_app.extensions import db, bcrypt, migrate

# Load environment variables from .env file
load_dotenv()

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

# SendGrid API key
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)


def send_email(sender_email, email_addresses, subject, message):
    from_email = Email(sender_email)  # Dynamic sender email
    to_emails = [To(email) for email in email_addresses]
    content = Content("text/plain", message)

    mail = Mail(from_email, to_emails, subject, content)

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        if response.status_code == 202:
            return {"status": "Emails sent successfully!"}
        else:
            return {"error": "Failed to send emails, try again."}
    except Exception as e:
        return {"error": str(e)}

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    # Initialize database and extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Initialize JWT
    app.config['JWT_SECRET_KEY'] = '12345'
    jwt = JWTManager(app)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

    # Register blueprints
    from witi_app.controllers.user_controller import user_bp
    from witi_app.controllers.program_controller import program_bp
    from witi_app.controllers.events_controller import event_bp
    from witi_app.controllers.gallery_controllers import gallery_bp
    from witi_app.controllers.contact_inquiry_controller import contact_inquiry_bp
    from witi_app.controllers.donations_controller import donation_bp
    from witi_app.controllers.stories_controller import stories_bp

    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(program_bp, url_prefix='/api/v1/program')
    app.register_blueprint(event_bp, url_prefix='/api/v1/event')
    app.register_blueprint(gallery_bp, url_prefix='/api/v1/gallery')
    app.register_blueprint(contact_inquiry_bp, url_prefix='/api/v1/contact-inquiry')
    app.register_blueprint(donation_bp, url_prefix='/api/v1/donation')
    app.register_blueprint(stories_bp,url_prefix='/api/v1/stories')

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
    from flask_swagger_ui import get_swaggerui_blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "witi_At_app"}
    )
    app.register_blueprint(swaggerui_blueprint)

    @app.route('/')
    def home():
        return 'Welcome to Women in technology website!'

    # Protected route example
    @app.route('/protected')
    @jwt_required()
    def protected():
        current_user_id = get_jwt_identity()
        return jsonify(logged_in_as=current_user_id), 200

    # Route to send SMS
    @app.route('/send-sms', methods=['POST'])
    def send_sms_route():
        data = request.get_json()
        phone_number = data.get('phone_numbers')
        message = data.get('message')

        if not phone_number or not message:
            return jsonify({'error': 'Phone numbers and messages are required'}), 400

        responses = []
        for number in phone_number:
            response = send_sms(number, message)
            responses.append({'number': number, 'response': response})

        return jsonify({'status': 'SMS sent', 'details': responses}), 200

    # Route to send email
    @app.route('/send-email', methods=['POST'])
    def send_email_route():
        data = request.get_json()
        sender_email = data.get('sender_email')  # Get sender email from the request
        email_addresses = data.get('email_addresses')
        subject = data.get('subject')
        message = data.get('message')

        if not sender_email or not email_addresses or not subject or not message:
            return jsonify({"error": "Missing sender email, email addresses, subject, or message."}), 400

        response = send_email(sender_email, email_addresses, subject, message)

        if "status" in response:
            return jsonify(response), 200
        else:
            return jsonify(response), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
