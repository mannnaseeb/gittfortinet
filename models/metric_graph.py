import datetime
from . import db
from sqlalchemy.orm import backref

class MetricGraph(db.Model):
    __tablename__ = 'Metric_Graph'
    MetricGraphID = db.Column(db.Integer, primary_key=True)
    #'Metric' is classname of model, 'graphDetail' is like a variable name given that will be available when fetching Metric data
    metrics = db.relationship("Metric", backref=backref("graphDetail"))
    MetricGraphCode = db.Column(db.String(30), nullable=False, unique=True)
    MetricGraphName = db.Column(db.String(100), nullable=False)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())