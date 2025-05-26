import os
import pydicom
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from models import db, Study

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:55432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DICOM_STORAGE_PATH'] = os.path.join(os.getcwd(), 'dicom_storage')

db.init_app(app)

# Create tables on startup
with app.app_context():
    db.create_all()


@app.route('/qido/studies', methods=['GET'])
def qido_rs():
    patient_id = request.args.get('PatientID')
    query = Study.query

    if patient_id:
        query = query.filter_by(patient_id=patient_id)

    results = [entry.to_dict() for entry in query.all()]
    return jsonify(results)


@app.route('/wado/studies/<study_uid>', methods=['GET'])
def wado_rs(study_uid):
    record = Study.query.filter_by(study_uid=study_uid).first()

    if not record or not os.path.exists(record.file_path):
        return jsonify({"error": "Study not found"}), 404

    return send_file(record.file_path, mimetype='application/dicom')


@app.route('/stow/studies', methods=['POST'])
def stow_rs():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    dcm = pydicom.dcmread(file)

    study_uid = dcm.StudyInstanceUID
    series_uid = dcm.SeriesInstanceUID
    sop_uid = dcm.SOPInstanceUID
    patient_id = dcm.get("PatientID", "")
    study_date = dcm.get("StudyDate", "")

    save_dir = os.path.join(app.config['DICOM_STORAGE_PATH'], study_uid, series_uid)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{sop_uid}.dcm")

    file.seek(0)
    file.save(save_path)

    # Upsert into database
    existing = Study.query.filter_by(sop_uid=sop_uid).first()
    if not existing:
        study = Study(
            study_uid=study_uid,
            series_uid=series_uid,
            sop_uid=sop_uid,
            patient_id=patient_id,
            study_date=study_date,
            file_path=save_path
        )
        db.session.add(study)
        db.session.commit()

    return jsonify({"message": "DICOM file stored"}), 200


if __name__ == '__main__':
    app.run(debug=True)
