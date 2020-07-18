import logging
import os
from pathlib import Path

from redis import Redis
from rq import Queue
from yalse_core.common.constants import DOCUMENTS_DIR, SHA256
from yalse_core.common.email import send_email
from yalse_core.database import db, File
from yalse_core.elasticsearch.index import index_document


def check_anomalies():
    from yalse_core.app import application
    with application.app_context():
        warning_list = []
        for file in db.session.query(File).distinct(File.file_hash):
            if db.session.query(File.id).filter_by(file_hash=file.file_hash, duplicate=False, missing=False, anomaly=False).count() < 1:
                warning_list.append(file.file_path)
        if warning_list:
            send_email(f"WARNING! These files are an anomaly: {warning_list}")


def delete_missing_files():
    from yalse_core.app import application
    with application.app_context():
        missing_files = db.session.query(File).filter_by(missing=True).all()
        deleted_files = []
        for missing in missing_files:
            try:
                if Path(missing.file_path).exists():
                    raise Exception
                db.session.delete(missing)
                deleted_files.append(missing.file_path)
            except Exception as e:
                logging.error(f"Error in removing missing file: {missing.file_path}, {e}")
        db.session.commit()
        if deleted_files:
            send_email(f"Deleting MISSING records: {deleted_files}")


def delete_duplicate_files(dry_run):
    from yalse_core.app import application
    with application.app_context():
        duplicate_files = db.session.query(File).filter_by(duplicate=True).all()
        deleted_files = []
        for duplicate in duplicate_files:
            try:
                # check that exists at least one valid file for this hash
                original_file = db.session.query(File).filter(
                    File.file_path != duplicate.file_path,
                    File.file_hash == duplicate.file_hash,
                    File.duplicate == False,
                    File.missing == False,
                    File.anomaly == False
                ).first()

                if not Path(original_file.file_path).exists():
                    raise Exception
                if not Path(duplicate.file_path).exists():
                    raise Exception
                if not original_file.file_hash == duplicate.file_hash:
                    raise Exception
                if not original_file.file_path != duplicate.file_path:
                    raise Exception
                if original_file.duplicate:
                    raise Exception
                if original_file.missing:
                    raise Exception
                if original_file.anomaly:
                    raise Exception
                if not duplicate.duplicate:
                    raise Exception
                if duplicate.missing:
                    raise Exception
                if duplicate.anomaly:
                    raise Exception

                logging.warning(f"Deleting: {duplicate.file_path}")
                if not dry_run:
                    os.remove(duplicate.file_path)
                    db.session.delete(duplicate)
                deleted_files.append(duplicate.file_path)
            except Exception as e:
                logging.error(f"Error in deleting duplicate file: {duplicate.file_path}, {e}")
        db.session.commit()
        if deleted_files:
            send_email(f"Deleting {len(deleted_files)} DUPLICATE files: {deleted_files}")


def index_files():
    from yalse_core.app import application
    with application.app_context():
        queue = Queue(connection=Redis('redis'))
        for file in db.session.query(File).all():
            queue.enqueue(index_document, file.file_hash, file.file_path, job_timeout=60)


def files_scan(dry_run):
    from yalse_core.app import application
    with application.app_context():
        db.session.query(File).update({File.duplicate: False})
        for file in db.session.query(File).all():
            if not Path(file.file_path).exists():
                file.missing = True
        files = []
        logging.info("Starting OS scan..")
        for r, d, f in os.walk(DOCUMENTS_DIR):
            for file in f:
                file_path = os.path.join(r, file)
                file_hash = SHA256.hash_file(file_path)
                files.append((file_path, file_hash))
        logging.info(f"Completed OS scan: {len(files)} files found.")
        count = 0
        for file_path, file_hash in files:
            count += 1
            path_exists = db.session.query(File.id).filter_by(file_path=file_path).scalar() is not None
            hash_exists = db.session.query(File.id).filter(
                File.file_path != file_path,
                File.file_hash == file_hash,
                File.duplicate == False,
                File.missing == False,
                File.anomaly == False
            ).count() > 0

            if not path_exists:
                record = File(
                    file_hash=file_hash,
                    file_path=file_path,
                    duplicate=hash_exists,
                )
                db.session.add(record)
            else:
                file = db.session.query(File).filter_by(file_path=file_path).first()
                file.missing = False
                file.duplicate = hash_exists
                if file_hash != file.file_hash:
                    file.anomaly = True
                    file.file_hash = file_hash
                else:
                    file.anomaly = False
            if count % 1000 == 0:
                logging.info(f"Scanned {count} files out of {len(files)} so far.")

        db.session.commit()

        check_anomalies()
        delete_missing_files()
        delete_duplicate_files(dry_run)

        index_files()


def scan_files(body):
    dry_run = body.get('dry_run') is not None
    queue = Queue(connection=Redis('redis'))
    queue.enqueue(files_scan, dry_run, job_timeout='24h')
    return {'code': 202, 'message': "scan in progress"}, 202
