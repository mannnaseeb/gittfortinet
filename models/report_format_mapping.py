"""format mapping module"""
import datetime
from . import db

report_format_mapping_table = db.Table('Report_FormatMapping',
    db.Column('ReportMappingID', db.Integer, primary_key=True),
    db.Column('ReportMetaID', db.Integer, db.ForeignKey('Report_Meta.ReportMetaID')),
    db.Column('ReportFormatID', db.Integer, db.ForeignKey('Report_Format.ReportFormatID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)