METRIC_NAMES = list()
SORT_BY_OPTIONS = dict()
FILTER_BY_OPTIONS = dict()
from logging import debug, info
import logging
from flask import g
from models import db

from sqlalchemy.orm import query
from logging import debug, info
import logging

from sqlalchemy.orm import query
from constants import ERROR_REPORT_DELETE_FAILED,ERROR_CODE_INTERNAL_SERVER_ERROR, FILTER_BY_DEVICE_ID,\
                      ERROR_INVALID_REPORT_STATUS_REQUEST
from caching import cache
from models.metric import Metric
from models.metric_supported_operation import MetricSupportedoperation
from models.metric_type import MetricType
from models.metric_filtermapping import metric_filtermapping_table
from sqlalchemy.sql.elements import and_
from api_models.metric_api_model import MetricsModel
from models.report_meta import ReportMeta
from models.reports import Reports
from api_models.report_api_model import ReportData
from flask_restx import marshal
# --------------- DO NOT REMOVE THE FOLLOWING MODEL ---------------
from models.metric_classification import MetricClassification
from models.metric_graph import MetricGraph
from models.report_filter import ReportFilter
from models.metric_filter import MetricFilter
from languages.fortinet_api_exceptions import ValidationException 
# ---------- DO NOT REMOVE THE FOLLOWING MODEL ENDS HERE ----------

# --------------------- gettings all Dtos ---------------------
_all_metrics_list_of_classification_and_data = MetricsModel.MetricsListOfClassifiersAndData

_all_metrics_list_of_filter_and_data = MetricsModel.MetricsListWithFilter

_all_report_meta_list = ReportData


# ---------------- gettings all Dtos ENDS HERE ----------------
# @cache.memoize()
def get_all_metrics_with_filter_from_database(endpoint):
    """
    Return Structure:
    [
      {
        "name": "metric-name",
        "desc": "",
        "code": "metric-code-name",
        "classification": "classification-name",
        "type": ["type-name"],
        "filters": [
          {
            "field": "field-name",
            "supported_operation": ["operation"]
          }
        ],
        "sort-by": [
          {
            "field": "sort-by-value",
            "order": "asc/desc"
          }
        ],
        "limit": number,
        "time_range_filter": boolean,
        "is_customer": boolean,
        "is_admin": boolean,
        "can_configurable": boolean,
        "default_graph": string,
        "supported_graphs": [string,string...],
        "can_show_db": boolean,
        "is_widget": boolean,
      }
    ]
    Return structure mentioned above
    """
    dataset = []
    # ----------------- Fetching data from database -----------------
    for metric in Metric.query.filter_by(MetricCode=endpoint):
        if metric:
            # ----------------- Attaching classificationDetail to dataset -----------------
            if metric.classificationDetail and 'MetricClassificationCode' in metric.classificationDetail.__dict__:
                metric.classification = metric.classificationDetail.MetricClassificationCode
            # ------------ Attaching classificationDetail to dataset ENDS HERE ------------
            # ----------------- Attaching graphDetail to dataset -----------------
            if metric.graphDetail and 'MetricGraphCode' in metric.graphDetail.__dict__:
                metric.default_graph = metric.graphDetail.MetricGraphCode
            # ------------ Attaching graphDetail to dataset ENDS HERE ------------
            # ----------------- Attaching metric filters to dataset -----------------
            if metric.FilterList:
                metric_join_metric_mapping_rows = db.session.query(metric_filtermapping_table.c.MetricFilterID, metric_filtermapping_table.c.Status, metric_filtermapping_table.c.IsRequired).select_from(Metric).join(metric_filtermapping_table).filter(metric_filtermapping_table.c.MetricID == metric.MetricID).all()
                enabled_filters_metric_filter_id = [row['MetricFilterID'] for row in metric_join_metric_mapping_rows if row['Status'] == 1]
                required_filters_metric_filter_id = [row['MetricFilterID'] for row in metric_join_metric_mapping_rows if row['IsRequired'] == 1]
                # ----------------- Attaching supported operations to filter -----------------
                all_filters = []
                for filter in metric.FilterList:
                    # create a clone as the same filter object is returned for other metrics
                    filter_copy = MetricFilter()
                    filter_copy.MetricFilterName = filter.MetricFilterName
                    if  filter.MetricFilterID in enabled_filters_metric_filter_id:
                      filter_copy.supported_operation = [str(seperator.Metric_SupportedOperationCode) for seperator in
                                                        filter.SupportedOperations if
                                                        seperator.Metric_SupportedOperationCode is not None]
                      filter_copy.is_required = True if filter.MetricFilterID in required_filters_metric_filter_id else False
                      all_filters.append(filter_copy)
                # ------------ Attaching supported operations to filter ENDS HERE ------------
                metric.filters = all_filters
            # ------------ Attaching metric filters to dataset ENDS HERE ------------
            # ----------------- Attaching metric sort to dataset -----------------
            if metric.SortList:
                metric.__dict__['sort-by'] = metric.SortList
            # ------------ Attaching metric sort to dataset ENDS HERE ------------
            # ----------------- Attaching metric type to dataset -----------------
            if metric.TypeList:
                metric.type = [str(type_value.MetricTypeName) for type_value in metric.TypeList if
                               type_value.MetricTypeName is not None]
            # ------------ Attaching metric type to dataset ENDS HERE ------------
            # ----------------- Attaching metric graph to dataset -----------------
            if metric.GraphList:
                metric.supported_graphs = [str(graph_value.MetricGraphCode) for graph_value in metric.GraphList if
                               graph_value.MetricGraphCode is not None]
            # ------------ Attaching metric graph to dataset ENDS HERE ------------
            dataset.append(metric)
    # ------------ Fetching data from database ENDS HERE ------------
    store_marshal = marshal(dataset, _all_metrics_list_of_classification_and_data)
    return store_marshal


@cache.cached(key_prefix='all_metrics_data')
def get_all_metrics_from_database():
    """
    Return Structure:
    [
      {
        "name": "metric-name",
        "desc": "",
        "code": "metric-code-name",
        "classification": "classification-name",
        "type": ["type-name"],
        "filters": [
          {
            "field": "field-name",
            "supported_operation": ["operation"]
          }
        ],
        "sort-by": [
          {
            "field": "sort-by-value",
            "order": "asc/desc"
          }
        ],
        "limit": number,
        "time_range_filter": boolean,
        "is_customer": boolean,
        "is_admin": boolean,
        "can_configurable": boolean,
        "default_graph": string,
        "supported_graphs": [string,string...],
        "can_show_db": boolean,
        "is_widget": boolean,
      }
    ]
    Return structure mentioned above
    """
    dataset = []
    # ----------------- Fetching data from database -----------------
    for metric in Metric.query.all():
        if metric:
            # ----------------- Attaching classificationDetail to dataset -----------------
            if metric.classificationDetail and 'MetricClassificationCode' in metric.classificationDetail.__dict__:
                metric.classification = metric.classificationDetail.MetricClassificationCode
            # ------------ Attaching classificationDetail to dataset ENDS HERE ------------
            # ----------------- Attaching graphDetail to dataset -----------------
            if metric.graphDetail and 'MetricGraphCode' in metric.graphDetail.__dict__:
                metric.default_graph = metric.graphDetail.MetricGraphCode
            # ------------ Attaching graphDetail to dataset ENDS HERE ------------
            # ----------------- Attaching metric filters to dataset -----------------
            if metric.FilterList:
                # ----------------- Attaching supported operations to filter -----------------
                metric_join_metric_mapping_rows = db.session.query(metric_filtermapping_table.c.MetricFilterID, metric_filtermapping_table.c.Status, metric_filtermapping_table.c.IsRequired).select_from(Metric).join(metric_filtermapping_table).filter(metric_filtermapping_table.c.MetricID == metric.MetricID).all()
                enabled_filters_metric_filter_id = [row['MetricFilterID'] for row in metric_join_metric_mapping_rows if row['Status'] == 1]
                required_filters_metric_filter_id = [row['MetricFilterID'] for row in metric_join_metric_mapping_rows if row['IsRequired'] == 1]
                all_filters = []
                for filter in metric.FilterList:
                    # create a clone as the same filter object is returned for other metrics
                    filter_copy = MetricFilter()
                    filter_copy.MetricFilterName = filter.MetricFilterName
                    if  filter.MetricFilterID in enabled_filters_metric_filter_id:
                      filter_copy.supported_operation = [str(seperator.Metric_SupportedOperationCode) for seperator in
                                                        filter.SupportedOperations if
                                                        seperator.Metric_SupportedOperationCode is not None]
                      filter_copy.is_required = True if filter.MetricFilterID in required_filters_metric_filter_id else False
                      all_filters.append(filter_copy)
                # ------------ Attaching supported operations to filter ENDS HERE ------------
                metric.filters = all_filters
            # ------------ Attaching metric filters to dataset ENDS HERE ------------
            # ----------------- Attaching metric sort to dataset -----------------
            if metric.SortList:
                metric.__dict__['sort-by'] = metric.SortList
            # ------------ Attaching metric sort to dataset ENDS HERE ------------
            # ----------------- Attaching metric type to dataset -----------------
            if metric.TypeList:
                metric.type = [str(type_value.MetricTypeName) for type_value in metric.TypeList if
                               type_value.MetricTypeName is not None]
            # ------------ Attaching metric type to dataset ENDS HERE ------------
            # ----------------- Attaching metric graph to dataset -----------------
            if metric.GraphList:
                metric.supported_graphs = [str(graph_value.MetricGraphCode) for graph_value in metric.GraphList if
                               graph_value.MetricGraphCode is not None]
            # ------------ Attaching metric graph to dataset ENDS HERE ------------
            dataset.append(metric)
    # ------------ Fetching data from database ENDS HERE ------------
    store_marshal = marshal(dataset, _all_metrics_list_of_classification_and_data)
    return store_marshal

@cache.cached(key_prefix='all_supported_metric_operations')
def get_all_metric_supported_operations_from_database():
    """ Return Structure:  ["operation"] """
    operation_codes = []
    # ----------------- Fetching data from database -----------------
    for metric_supported_operation in MetricSupportedoperation.query.all():
        if metric_supported_operation:
            operation_codes.append(str(metric_supported_operation.Metric_SupportedOperationCode))
    # ------------ Fetching data from database ENDS HERE ------------
    return operation_codes

def get_metric_codes_from_database():
    """return structure : ['metric-code']"""
    return [metric['code'] for metric in get_all_metrics_from_database()]

def get_sort_by_options_from_database():
    """return structure : {'metric-code':['sort-by-option']}"""
    return {metric['code']: [sort_option['field'] for sort_option in metric['sort-by']] for metric in
            get_all_metrics_from_database()}

def get_filter_by_options_from_database():
    """return structure : {'metric-code':['filter-by-option']}"""
    return {metric['code']: [filter_option['field'] for filter_option in metric['filters']] for metric in
            get_all_metrics_from_database()}

def get_limit_for_metric_from_database():
    """return structure : {'metric-code':limit(int)}"""
    return {metric['code']: metric.get('limit', None) for metric in
            get_all_metrics_from_database()}

def get_type_for_metric_from_database():
    """return structure : {'metric-code':['metric-type']}"""
    return {metric['code']: metric.get('type', None) for metric in
            get_all_metrics_from_database()}

def get_report_codes_from_database(end_point):
    """return structure : ['report-code']"""
    return [report['title'] for report in get_all_report_meta_from_database() if report['code'] == end_point]

def get_report_timestamp_from_database(title):
    """return structure : ['report-code']"""

    query_report = Reports.query.filter(Reports.ReportTitle==title,Reports.ExecutedAt != None,Reports.is_deleted==0).first()
    if query_report:
      return query_report.ExecutedAt

    return None

def get_report_filter_from_database():
    """return structure : ['report-code']"""

    query_report = ReportFilter.query.filter(ReportFilter.IsRequired==True)
    return query_report

def get_report_tid_from_database(tid):
    """return structure : ['report-tid']"""
    query_report = Reports.query.filter(Reports.ReportTid==tid).first()
    if query_report:
      return True
    return None

def delete_report_tid_into_database(tid):
    """return structure : ['report-tid']"""
    query_report = Reports.query.filter(Reports.ReportTid==tid).first()
    if query_report:
      try:
        query_report.is_deleted = 1
        db.session.commit()
      except Exception as ex:
        raise Exception(ERROR_REPORT_DELETE_FAILED, ERROR_CODE_INTERNAL_SERVER_ERROR)


def get_all_report_data_from_database(title):
    """return structure : report list"""
    return Reports.query.filter(Reports.ReportTitle==title,Reports.is_deleted==0).order_by(Reports.ReportID.desc())
    # return Reports.query.filter(Reports.ReportTitle==title,Reports.is_deleted==0,Reports.CreatedBy  == g.userId ).order_by(Reports.ReportID.desc())

@cache.cached(key_prefix='all_metric_types')
def get_all_metric_types_from_database():
    """ Return Structure:  ["metric-type"] """
    metric_types = []
    # ----------------- Fetching data from database -----------------
    for metric_type in MetricType.query.all():
        if metric_type:
            metric_types.append(str(metric_type.MetricTypeName))
    # ------------ Fetching data from database ENDS HERE ------------
    return metric_types

def get_all_report_meta_filter_database(title_code=None,tid=None):
    """
    Return Structure:
    [
      {
        "title": "60-Degree Security Review",
        "code": "60-Degree Security Review",
        "filters": [
          {
            "field": "devid",
            "supported_operation": [
              "="
            ]
          }
        ],
        "format": [
          "PDF"
        ]
      }
    ]
    Return structure mentioned above
    """
    if tid:
      reports = Reports.query.filter(Reports.ReportTid==tid).first()
      if not reports:
        raise ValidationException(ERROR_INVALID_REPORT_STATUS_REQUEST)
      ReportsMetaData = ReportMeta.query.filter(ReportMeta.ReportMetaTitle==reports.ReportTitle)
    else:
      ReportsMetaData = ReportMeta.query.filter(ReportMeta.ReportMetaTitleCode==title_code.strip())

    dataset = []
    # ----------------- database query -----------------
    for report_meta in ReportsMetaData:
        if report_meta:
            if report_meta.SupportedFormat:
              #adding support format for report
              report_meta.supported_formats = [str(type_value.ReportFormatName) for type_value in report_meta.SupportedFormat if
                               type_value.ReportFormatName is not None]
            if report_meta.FilterList:
                all_filters = []
                for filter_list in report_meta.FilterList:
                  #adding supporting filter options
                  if filter_list.Status:
                    filter_list.supported_operation = [str(seperator.Report_SupportedOperationCode) for seperator in
                                                        filter_list.SupportedOperations if
                                                        seperator.Report_SupportedOperationCode is not None]
                    filter_list.is_required = filter_list.IsRequired
                    all_filters.append(filter_list)
                report_meta.filters = all_filters
            dataset.append(report_meta)
    store_marshal = marshal(dataset, _all_report_meta_list)
    return store_marshal

@cache.cached(key_prefix='all_report_meta_data')
def get_all_report_meta_from_database():
    """
    Return Structure:
    [
      {
        "title": "60-Degree Security Review",
        "code": "60-Degree Security Review",
        "filters": [
          {
            "field": "devid",
            "supported_operation": [
              "="
            ]
          }
        ],
        "format": [
          "PDF"
        ]
      }
    ]
    Return structure mentioned above
    """
    dataset = []
    # ----------------- database query -----------------
    for report_meta in ReportMeta.query.all():
        if report_meta:
            if report_meta.SupportedFormat:
              #adding support format for report
              report_meta.supported_formats = [str(type_value.ReportFormatName) for type_value in report_meta.SupportedFormat if
                               type_value.ReportFormatName is not None]
            if report_meta.FilterList:
                all_filters = []
                for filter_list in report_meta.FilterList:
                  #adding supporting filter options
                  if filter_list.Status:
                    filter_list.supported_operation = [str(seperator.Report_SupportedOperationCode) for seperator in
                                                        filter_list.SupportedOperations if
                                                        seperator.Report_SupportedOperationCode is not None]
                    filter_list.is_required = filter_list.IsRequired
                    all_filters.append(filter_list)
                report_meta.filters = all_filters
            dataset.append(report_meta)
    store_marshal = marshal(dataset, _all_report_meta_list)
    return store_marshal

def get_metrics_with_devid_filter(endpoint):
    metric_filters = next(iter(get_all_metrics_with_filter_from_database(endpoint)), {}).get('filters', [])
    #Check if endpoint filter contains devid
    if [filter.get('field') for filter in metric_filters if filter.get('field') == FILTER_BY_DEVICE_ID]:
        return True