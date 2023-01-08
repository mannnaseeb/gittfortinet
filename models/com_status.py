from . import db

class ComStatus(db.Model):
    """COM_Status"""
    __tablename__ = 'COM_Status'
    StatusID = db.Column(db.Integer, primary_key=True)
    StatusCode = db.Column(db.String(3), nullable=False, unique=True)
    StatusName = db.Column(db.String(20), nullable=False)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False)
