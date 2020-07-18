from flask import send_file
from yalse_core.database import db, File


def download_file(file_hash):
    from yalse_core.app import application
    with application.app_context():
        file = db.session.query(File).filter_by(file_hash=file_hash).first()
        return send_file(file.file_path, as_attachment=True)
