from sqlalchemy_utils import create_database, database_exists
from yalse_core.database import db, File
from yalse_core.elasticsearch.init import reset_index


def reset_library():
    from yalse_core.app import application
    with application.app_context():
        if not database_exists(application.config['SQLALCHEMY_DATABASE_URI']):
            create_database(application.config['SQLALCHEMY_DATABASE_URI'])
        try:
            File.__table__.drop(db.engine)
        except:
            pass
        db.create_all()
        reset_index()
    return {'code': 200, 'message': "reset"}, 200
