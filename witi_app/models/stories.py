from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)

    def __init__(self, title, description, image=None, video_url=None):
        self.title = title
        self.description = description
        self.image = image
        self.video_url = video_url

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.image,
            "video_url": self.video_url,
        }
