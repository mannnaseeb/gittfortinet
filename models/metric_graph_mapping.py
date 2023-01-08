import datetime
from . import db

metric_graphmapping_table = db.Table('Metric_GraphMapping',
    db.Column('MetricGraphMappingID', db.Integer, primary_key=True),
    db.Column('MetricID', db.Integer, db.ForeignKey('Metric.MetricID')),
    db.Column('MetricGraphID', db.Integer, db.ForeignKey('Metric_Graph.MetricGraphID')),
    db.Column('CreatedBy', db.BigInteger,  nullable=False),
    db.Column('CreatedOn', db.DateTime, nullable=False, default=datetime.datetime.utcnow()),
    db.Column('ModifiedBy', db.BigInteger,  nullable=False),
    db.Column('ModifiedOn', db.DateTime,  nullable=False, default=datetime.datetime.utcnow()),
)