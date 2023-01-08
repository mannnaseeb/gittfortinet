"""report filter module"""
import datetime
from . import db
#--------------- DO NOT REMOVE THE FOLLOWING MODEL ---------------
from .report_supported_operation import ReportSupportedoperation
#---------- DO NOT REMOVE THE FOLLOWING MODEL ENDS HERE ----------
from .report_filter_supported_operation_mapping import report_filter_supported_operation_mapping_table

class ReportFilter(db.Model):
    """Report Filter Table"""
    __tablename__ = 'Report_Filter'
    ReportFilterID = db.Column(db.Integer, primary_key=True)
    SupportedOperations = db.relationship('ReportSupportedoperation', secondary=report_filter_supported_operation_mapping_table, lazy='subquery',
        backref=db.backref('associated_filters', lazy=True))
    ReportFilterCode = db.Column(db.String(50), nullable=False, unique=True)
    ReportFilterName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    IsRequired = db.Column( db.Boolean,  default=False)
    Status = db.Column(db.Boolean,  default=False)
