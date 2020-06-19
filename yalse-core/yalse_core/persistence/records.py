from yalse_core.database import File, db


def create_file(hash):
    f = File(file_hash=hash)
    db.session.add(f)
    db.session.commit()


def get_all_files():
    results = []
    for f in File.query.all():
        results.append(f.file_hash)
    return {'records': results}
