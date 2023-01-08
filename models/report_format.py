"""report format module"""
import datetime
from . import db

class ReportFormat(db.Model):
    """report format table"""
    __tablename__ = 'Report_Format'
    ReportFormatID = db.Column(db.Integer, primary_key=True)
    ReportFormatCode = db.Column(db.String(50), nullable=False, unique=True)
    ReportFormatName = db.Column(db.String(100), nullable=False)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())