import datetime
from . import db

metric_filtermapping_table = db.Table('Metric_FilterMapping',
    db.Column('MetricFilterMappingID', db.Integer, primary_key=True),
    db.Column('MetricID', db.Integer, db.ForeignKey('Metric.MetricID')),
    db.Column('MetricFilterID', db.Integer, db.ForeignKey('Metric_Filter.MetricFilterID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('Status', db.Boolean,  nullable=False, default=False),
    db.Column('IsRequired', db.Boolean,  nullable=False, default=False)
)