import datetime
from . import db
from .metric_filtermapping import metric_filtermapping_table
from .metric_sort_mapping import metric_sortmapping_table
from .metric_type_mapping import metric_typemapping_table
from .metric_graph_mapping import metric_graphmapping_table
#--------------- DO NOT REMOVE THE FOLLOWING MODEL ---------------
from .metric_filter import MetricFilter
from .metric_sort import MetricSort
from .metric_type import MetricType
from .metric_graph import MetricGraph
#---------- DO NOT REMOVE THE FOLLOWING MODEL ENDS HERE ----------


class Metric(db.Model):
    """Metric"""
    __tablename__ = 'Metric'
    MetricID = db.Column(db.Integer, primary_key=True)
    MetricCode = db.Column(db.String(30), nullable=False, unique=True)
    MetricName = db.Column(db.String(100), nullable=False)
    ClassificationID = db.Column(db.Integer, db.ForeignKey('Metric_Classification.MetricClassificationID'),
                                 nullable=False)
    DefaultGraph = db.Column(db.Integer, db.ForeignKey('Metric_Graph.MetricGraphID'),
                                 nullable=False)
    FilterList = db.relationship('MetricFilter', secondary=metric_filtermapping_table, lazy='subquery',
        backref=db.backref('associated_metrics', lazy=True))
    SortList = db.relationship('MetricSort', secondary=metric_sortmapping_table, lazy='subquery',
        backref=db.backref('associated_metrics', lazy=True))
    TypeList = db.relationship('MetricType', secondary=metric_typemapping_table, lazy='subquery',
        backref=db.backref('associated_metrics', lazy=True))
    GraphList = db.relationship('MetricGraph', secondary=metric_graphmapping_table, lazy='subquery',
        backref=db.backref('associated_metrics', lazy=True))
    Version = db.Column(db.String(50), default='', nullable=True)
    TimeRangeFilter = db.Column(db.Integer, nullable=False, default=0)
    IsCustomer = db.Column(db.Integer, nullable=False, default=0)
    IsAdmin = db.Column(db.Integer, nullable=False, default=0)
    MetricLimit = db.Column(db.Integer, nullable=False, default=0)
    StatusID = db.Column(db.Integer, db.ForeignKey('Com_Status.StatusId'), nullable=False)
    Description = db.Column(db.String(500), nullable=True, default='')
    CreatedBy = db.Column(db.BigInteger, nullable=False)
    CreatedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    ModifiedBy = db.Column(db.BigInteger, nullable=False)
    ModifiedOn = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    CanConfigurable = db.Column(db.Integer, nullable=False, default=0)
    CanShowDatatable = db.Column(db.Integer, nullable=False, default=0)
    IsWidget = db.Column(db.Integer, nullable=False, default=0)
