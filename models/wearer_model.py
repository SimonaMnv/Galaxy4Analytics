from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Wearer(db.Model):
    __tablename__ = "wearer"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(255), nullable=False)
    time = db.Column(db.String(255), nullable=False)
    heart_rate = db.Column(db.String(255), nullable=False)

    def __init__(self, date, time, heart_rate):
        self.date = date
        self.time = time
        self.heart_rate = heart_rate

    def __repr__(self):
        return '[' + str(self.id) + ']' + '_' + str(self.date) + '_' + str(self.time) + str(self.heart_rate)