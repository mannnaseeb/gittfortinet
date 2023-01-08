from . import db
import datetime

class MetricSupportedoperation(db.Model):
    __tablename__ = 'Metric_SupportedOperation'
    Metric_SupportedOperationID = db.Column(db.Integer, primary_key=True)
    Metric_SupportedOperationCode = db.Column(db.String(50), nullable=False, unique=True)
    Metric_SupportedOperationName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())