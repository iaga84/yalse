import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    file_hash = db.Column(db.String(128), index=True, nullable=False)
    file_path = db.Column(db.String(1024), index=True, unique=True, nullable=False)
    duplicate = db.Column(db.BOOLEAN, nullable=False)
    anomaly = db.Column(db.BOOLEAN, default=False, nullable=False)
    missing = db.Column(db.BOOLEAN, default=False, nullable=False)

    def __repr__(self):
        return '<File %r>' % self.file_hash
