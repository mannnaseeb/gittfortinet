import datetime
from sqlalchemy.orm import backref
from . import db

class MetricClassification(db.Model):
    """Metric Classification"""
    __tablename__ = 'Metric_Classification'
    MetricClassificationID = db.Column(db.Integer, primary_key=True)
    #'Metric' is classname of model, 'classificationDetail' is like a variable name given that will be available when fetching Metric data
    metrics = db.relationship("Metric", backref=backref("classificationDetail"))
    MetricClassificationCode = db.Column(db.String(30), nullable=False, unique=True)
    MetricClassificationName = db.Column(db.String(100), nullable=False)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
