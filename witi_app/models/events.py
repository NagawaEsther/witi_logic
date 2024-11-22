from witi_app import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(200))
    rsvp_link = db.Column(db.String(200), nullable=True)  # New column for RSVP link

    def __init__(self, name, description, date, image_url, rsvp_link=None):
        self.name = name
        self.description = description
        self.date = date
        self.image_url = image_url
        self.rsvp_link = rsvp_link

    def __repr__(self):
        return f"Event('{self.name}', '{self.date}')"
