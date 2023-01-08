"""report meta data module"""
from flask_restx import  fields, Model
    # -------------- Report Meta Data --------------
filters = Model('filters', {
        'field': fields.String(attribute="ReportFilterName"),
        'is_required': fields.Boolean(attribute="is_required"),
        'supported_operation': fields.List(fields.String()),
})
ReportData = Model('ReportData', {
        'title': fields.String(attribute='ReportMetaTitle'),
        'code': fields.String(attribute='ReportMetaTitleCode'),
        'filters': fields.List(fields.Nested(filters), default=[]),
        'supported_formats': fields.List(fields.String(), default=[])
})
ReportDevice = Model('ReportDevice', {
        'count': fields.Integer(),
        'data': fields.String(),
})
DefaultReport = Model('DefaultReport', {
        "name": fields.String(attribute="ReportFileName"),
        "devtype":fields.String(default=""),
        "schedule_color": fields.String(default=""),
        "title": fields.String(attribute="ReportTitle"),
        "tid": fields.String(attribute="ReportTid"),
        "end": fields.String(default=""),
        "date": fields.String(default=""),
        "adminuser": fields.String(default=""),
        "profileid": fields.String(default=""),
        "start": fields.String(attribute="ExecutedAt"),
        "timestamp-start": fields.Integer(default=None),
        "timestamp-end":fields.Integer(default=None),
        "period-start": fields.String(attribute="StartTime"),
        "period-end": fields.String(attribute="EndTime"),
        "device":fields.Nested(ReportDevice) ,
        "state": fields.String(default=""),
        "progress-percent": fields.Integer(attribute="ProgressReport"),
        "format":fields.List(fields.String(), default=[])
})

def default_report_response(api):
    api.models[ReportDevice.name] =ReportDevice
    api.models[DefaultReport.name] =DefaultReport
    return DefaultReport

def report_meta_response(api):
    api.models[filters.name] = filters
    api.models[ReportData.name] = ReportData
    return ReportData

class AdomreportsModel:

    ReportFilter = Model('ReportFilter', {
        'key': fields.String(required=True),
        'value': fields.String(required=True),
        'operation': fields.String(required=True)
    })

    ReportPayLoad = Model('ReportPayLoad', {
        'filter': fields.List(fields.Nested(ReportFilter)),
        'title': fields.String(),
        'start_date': fields.String(),
        'end_date': fields.String()
    })

    AdomReports = Model('AdomReports', {
        'name': fields.String(required=True),
        'devtype': fields.String(required=True),
        'schedule_color': fields.String(required=True),
        'title': fields.String(required=True),
        'tid': fields.String(required=True),
        'date': fields.String(required=True),
        'adminuser': fields.String(required=True),
        'profileid': fields.String(required=True),
        'start': fields.String(required=True),
        'timestamp-start': fields.Integer(required=True),
        'end': fields.String(required=True),
        'timestamp-end': fields.Integer(required=True),
        'period-start': fields.String(required=True),
        'period-end': fields.String(required=True),
        'device': fields.Wildcard(fields.String(required=True)),
        'state': fields.String(required=True),
        'progress-percent': fields.Integer(required=True),
        'format': fields.List(fields.String, default=[]),



    })

    AdomReportsData = Model('AdomReportsData', {
        'result': fields.List(fields.Nested(AdomReports)),

    })

    @staticmethod
    def adom_report_data_response(api):
        api.models[AdomreportsModel.AdomReports.name] = AdomreportsModel.AdomReports
        api.models[AdomreportsModel.AdomReportsData.name] = AdomreportsModel.AdomReportsData
        return AdomreportsModel.AdomReportsData


    ReportDownloadPayLoad = Model('ReportDownloadPayLoad', {
        'filter': fields.List(fields.Nested(ReportFilter)),
        'format': fields.String(),

    })

    AdomDownloadReports = Model('AdomDownloadReports', {
        'name': fields.String(required=True),
        'tid': fields.String(required=True),
        'data': fields.String(required=True),
        'data-type': fields.String(required=True),
        'checksum': fields.String(required=True),
        'length': fields.Integer(required=True)
        })

    @staticmethod
    def download_response(api):
        api.models[AdomreportsModel.AdomDownloadReports.name] = AdomreportsModel.AdomDownloadReports
        return AdomreportsModel.AdomDownloadReports

    DeleteReportData = Model('DeleteReportData', {
        'code': fields.Integer(),
        'message': fields.String(),
    })

    DeleteReportModel = Model('DeleteReportModel', {
        'status': fields.Nested(DeleteReportData)
    })

    @staticmethod
    def delete_report_response(api):
        api.models[AdomreportsModel.DeleteReportData.name] = AdomreportsModel.DeleteReportData
        api.models[AdomreportsModel.DeleteReportModel.name] = AdomreportsModel.DeleteReportModel
        return AdomreportsModel.DeleteReportModel


    AdomDownloadReportsData = Model('AdomDownloadReportsData', {
        'data': fields.List(fields.Nested(AdomDownloadReports)),
    })


    @staticmethod
    def reportInputPayload(api):
        api.models[AdomreportsModel.ReportFilter.name] = AdomreportsModel.ReportFilter
        api.models[AdomreportsModel.ReportPayLoad.name] = AdomreportsModel.ReportPayLoad
        return AdomreportsModel.ReportPayLoad

    @staticmethod
    def reportDownloadInputPayLoad(api):
        api.models[AdomreportsModel.ReportDownloadPayLoad.name] = AdomreportsModel.ReportDownloadPayLoad
        return AdomreportsModel.ReportDownloadPayLoad
