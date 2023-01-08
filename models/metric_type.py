from . import db
import datetime

class MetricType(db.Model):
    __tablename__ = 'Metric_Type'
    MetricTypeID = db.Column(db.Integer, primary_key=True)
    MetricTypeName = db.Column(db.String(100), nullable=False, unique=True)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())