"""Filter suppported operation module"""
from . import db
import datetime

report_filter_supported_operation_mapping_table = db.Table('Report_Filter_SupportedOperationMapping',
    db.Column('Report_SupportedOperationsMappingId', db.Integer, primary_key=True),
    db.Column('ReportFilterID', db.Integer, db.ForeignKey('Report_Filter.ReportFilterID')),
    db.Column('Report_SupportedOperationID', db.Integer, db.ForeignKey('Report_SupportedOperation.Report_SupportedOperationID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)
