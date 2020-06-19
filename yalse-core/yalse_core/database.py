from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<File %r>' % self.file_hash
