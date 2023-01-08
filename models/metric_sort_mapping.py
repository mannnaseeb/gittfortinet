from . import db
import datetime

metric_sortmapping_table = db.Table('Metric_SortMapping',
    db.Column('Metric_SortMappingID', db.Integer, primary_key=True),
    db.Column('MetricID', db.Integer, db.ForeignKey('Metric.MetricID')),
    db.Column('MetricSortID', db.Integer, db.ForeignKey('Metric_Sort.MetricSortID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)