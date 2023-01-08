"""report filter mapping module"""
import datetime
from . import db

report_filtermapping_table = db.Table('Report_FilterMapping',
    db.Column('ReportFilterMappingID', db.Integer, primary_key=True),
    db.Column('ReportMetaID', db.Integer, db.ForeignKey('Report_Meta.ReportMetaID')),
    db.Column('ReportFilterID', db.Integer, db.ForeignKey('Report_Filter.ReportFilterID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)