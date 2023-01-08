from . import db
import datetime

class MetricSort(db.Model):
    __tablename__ = 'Metric_Sort'
    MetricSortID = db.Column(db.Integer, primary_key=True)
    MetricSortCode = db.Column(db.String(50), nullable=False, unique=True)
    MetricSortName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    IsSort = db.Column(db.Integer, nullable=False, default=0)
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
