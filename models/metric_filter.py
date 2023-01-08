import datetime
from . import db
#--------------- DO NOT REMOVE THE FOLLOWING MODEL ---------------
from .metric_supported_operation import MetricSupportedoperation
#---------- DO NOT REMOVE THE FOLLOWING MODEL ENDS HERE ----------
from .metric_filter_supported_operation_mapping import metric_filter_supported_operation_mapping_table

class MetricFilter(db.Model):
    __tablename__ = 'Metric_Filter'
    MetricFilterID = db.Column(db.Integer, primary_key=True)
    SupportedOperations = db.relationship('MetricSupportedoperation', secondary=metric_filter_supported_operation_mapping_table, lazy='subquery',
        backref=db.backref('associated_filters', lazy=True))
    MetricFilterCode = db.Column(db.String(50), nullable=False, unique=True)
    MetricFilterName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
