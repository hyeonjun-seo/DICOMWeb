from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Study(db.Model):
    __tablename__ = 'study'

    id = db.Column(db.Integer, primary_key=True)
    study_uid = db.Column(db.String(64), nullable=False, index=True)
    series_uid = db.Column(db.String(64), nullable=False, index=True)
    sop_uid = db.Column(db.String(64), nullable=False, unique=True)
    patient_id = db.Column(db.String(64))
    study_date = db.Column(db.String(8))
    file_path = db.Column(db.String(256), nullable=False)

    def to_dict(self):
        return {
            "StudyInstanceUID": self.study_uid,
            "SeriesInstanceUID": self.series_uid,
            "SOPInstanceUID": self.sop_uid,
            "PatientID": self.patient_id,
            "StudyDate": self.study_date
        }
