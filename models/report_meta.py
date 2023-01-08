"""report meta db table"""
import datetime
from . import db
from .report_format import ReportFormat
from .report_filter import ReportFilter
from .report_format_mapping import report_format_mapping_table
from .report_filtermapping import report_filtermapping_table

class ReportMeta(db.Model):
    """Report Meta Table"""
    __tablename__ = 'Report_Meta'
    ReportMetaID = db.Column(db.Integer, primary_key=True)
    ReportMetaTitleCode = db.Column(db.String(30), nullable=False,unique=True)
    ReportMetaTitle = db.Column(db.String(100), nullable=False)
    SupportedFormat = db.relationship('ReportFormat',
                    secondary=report_format_mapping_table,
                    lazy='subquery',
                    backref=db.backref('associated_report',lazy=True))
    FilterList = db.relationship('ReportFilter',
                    secondary=report_filtermapping_table,
                    lazy='subquery',
                    backref=db.backref('associated_report', lazy=True))

    StatusID = db.Column(db.Integer, db.ForeignKey('Com_Status.StatusId'), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
