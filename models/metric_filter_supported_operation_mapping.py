from . import db
import datetime

metric_filter_supported_operation_mapping_table = db.Table('Metric_Filter_SupportedOperationMapping',
    db.Column('Metric_SupportedOperationsMappingId', db.Integer, primary_key=True),
    db.Column('MetricFilterID', db.Integer, db.ForeignKey('Metric_Filter.MetricFilterID')),
    db.Column('Metric_SupportedOperationID', db.Integer, db.ForeignKey('Metric_SupportedOperation.Metric_SupportedOperationID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)
