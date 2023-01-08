"""report meta db table"""
import datetime
from . import db
from .report_format import ReportFormat
from .report_filter import ReportFilter
from .report_format_mapping import report_format_mapping_table
from .report_filtermapping import report_filtermapping_table

class Reports(db.Model):
    """Report Meta Table"""
    __tablename__ = 'Reports'
    ReportID = db.Column(db.Integer, primary_key=True)
    ReportTitle = db.Column(db.String(100), nullable=False)
    ReportTid = db.Column(db.String(100), nullable=False, unique=True)
    ReportFormat = db.Column(db.String(20), default="")
    ReportFileName = db.Column(db.String(200), default="")
    Version = db.Column(db.String(50), default=None)
    StatusID = db.Column(db.BigInteger, nullable=False)
    DeviceID = db.Column(db.String(50), nullable=False)
    TimePeriod = db.Column(db.String(50), default=None)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    StartTime = db.Column(db.DateTime, default=None)
    EndTime = db.Column(db.DateTime, default=None)
    ExecutedAt = db.Column(db.DateTime, default=None)
    is_deleted = db.Column(db.Integer, default=0)
    ProgressReport = db.Column(db.Integer, default=0)
    DevicesData = db.Column(db.String(1000), default=None)
    # ClientID= db.Column(db.String(50), default=None)