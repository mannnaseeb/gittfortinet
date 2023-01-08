from . import db
import datetime

metric_typemapping_table = db.Table('Metric_TypeMapping',
    db.Column('MetricTypeMappingID', db.Integer, primary_key=True),
    db.Column('MetricID', db.Integer, db.ForeignKey('Metric.MetricID')),
    db.Column('MetricTypeID', db.Integer, db.ForeignKey('Metric_Type.MetricTypeID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime, nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)

