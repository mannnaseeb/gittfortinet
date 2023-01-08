from tokenize import String
from flask_restx import fields, Model

wild = fields.Wildcard(fields.String)


class ConnectionStatus(fields.Integer):
    """ConnectionStatus"""
    def format(self, connection_status):
        if int(connection_status):
            return "up"
        return "down"

class LinkStatus(fields.Boolean):
    """LinkStatus"""
    def format(self, connection_status):
        if connection_status:
            return "up"
        return "down"

class StingToInt(fields.String):
    """StingToInt"""
    def format(self, field_val):
        try:
            if type(field_val) == str:
                return int(field_val)
            return field_val
        except Exception as e:
            return field_val


class MetricsModel:
    sortBy = Model('sortBy', {
        'field': fields.String(attribute="MetricSortName"),
        'order': fields.String(default="asc/desc"),
    })

    filters = Model('filters', {
        'field': fields.String(attribute="MetricFilterName"),
        'is_required': fields.Boolean(attribute="is_required"),
        'supported_operation': fields.List(fields.String()),
    })

    MetricsListOfClassifiersAndData = Model('MetricsListOfClassifiersAndData', {
        'name': fields.String(attribute='MetricName'),
        'desc': fields.String(attribute='Description', default=""),
        'code': fields.String(attribute='MetricCode'),
        'classification': fields.String(default=""),
        'type': fields.List(fields.String(), default=[]),
        'filters': fields.List(fields.Nested(filters), default=[]),
        'sort-by': fields.List(fields.Nested(sortBy), default=[]),
        'limit': fields.Integer(attribute='MetricLimit'),
        'time_range_filter': fields.Boolean(attribute='TimeRangeFilter'),
        'is_customer': fields.Boolean(attribute='IsCustomer'),
        'can_configurable': fields.Boolean(attribute='CanConfigurable'),
        'default_graph': fields.String(default=""),
        'supported_graphs': fields.List(fields.String(), default=[]),
        'can_show_datatable': fields.Boolean(attribute='CanShowDatatable'),
        'is_widget': fields.Boolean(attribute='IsWidget')
    })

    all_filters = Model('filters', {
        'field': fields.String(attribute="MetricFilterName"),
        'is_required': fields.Boolean(attribute="IsRequired"),
    })

    MetricsListWithFilter = Model('MetricsListOfClassifiersAndData', {
        'name': fields.String(attribute='MetricCode'),
        'filters': fields.List(fields.Nested(all_filters), default=[])
    })

    @staticmethod
    def metric_metadata(api):
        api.models[MetricsModel.sortBy.name] = MetricsModel.sortBy
        api.models[MetricsModel.filters.name] = MetricsModel.filters
        api.models[MetricsModel.MetricsListOfClassifiersAndData.name] = MetricsModel.MetricsListOfClassifiersAndData
        return [MetricsModel.MetricsListOfClassifiersAndData]

    EpochValues = Model('EpochValues', {
        '*': wild,
    })

    MetricDataValues = Model('MetricDataValues', {
        'values': fields.Nested(EpochValues)
    })

    MetricFilter = Model('MetricFilter', {
        'key': fields.String(required=True),
        'value': fields.String(required=True),
        'operation': fields.String(required=True)
    })

    MetricSortBy = Model('MetricSortBy', {
        'field': fields.String(required=True),
        'order': fields.String(required=True)
    })

    AllMetricData = Model('AllMetricData', {
        'metric': fields.String(required=True),
        'filter': fields.List(fields.Nested(MetricFilter)),
        'sort-by': fields.List(fields.Nested(MetricSortBy)),
        'limit': fields.Integer(),
    })

    # --------------------- site-details model ---------------------
    SiteDetailsData = Model('SiteDetailsData', {
        'sites_up': fields.Integer(required=True),
        'sites_down': fields.Integer(required=True),
        'sites_alert': fields.Integer(required=True),
    })

    SiteDetails = AllMetricData.clone('SiteDetails', {
        'data': fields.List(fields.Nested(SiteDetailsData), default=[])
    })
    # ---------------- site-details model ENDS HERE ----------------

    # --------------------- top-applications model ---------------------
    TopApplicationsData = Model('TopApplicationsData', {
        'app_group': fields.String(required=True),
        'sessions': fields.String(required=True)
    })

    TopApplications = AllMetricData.clone('TopApplications', {
        'data': fields.List(fields.Nested(TopApplicationsData), default=[])
    })
    # ---------------- top-applications model ENDS HERE ----------------

    # --------------------- top application threats model ---------------------
    TopApplicationThreatsData = Model('TopApplicationThreatsData', {
        'risk': fields.String(required=True),
        'd_risk': fields.String(required=True),
        'bytes_total': fields.Integer(required=True, attribute="bandwidth"),
        'app_group': fields.String(required=True),
        'device_id': fields.String(required=True, attribute="fortigate"),
    })

    TopApplicationThreatsDetails = AllMetricData.clone('TopApplicationThreatsDetails', {
        'data': fields.List(fields.Nested(TopApplicationThreatsData), default=[])
    })
    # ---------------- top application threats model ENDS HERE ----------------

    # --------------------- bandwidth summary model ---------------------
    TrafficSummaryData = Model('TrafficSummaryData', {
        'device_id': fields.String(required=True, attribute="devid"),
        'host': fields.String(required=True, attribute="dev_name"),
        'ip': fields.String(required=True, attribute="srcip"),
        'cpu': fields.String(required=True, attribute="cpu_ave"),
        'memory': fields.String(required=True, attribute="mem_ave"),
        'disk': fields.String(required=True, attribute="disk_ave"),
        'sent_kbps': StingToInt(),
        'recv_kbps': StingToInt()
    })

    TrafficSummaryDetails = AllMetricData.clone('TrafficSummaryDetails', {
        'data': fields.List(fields.Nested(TrafficSummaryData), default=[])
    })
    # ---------------- bandwidth summary model ENDS HERE ----------------
    # --------------------- top-destination model ---------------------
    TopDestinationData = Model('TopDestinationData', {
        'country': fields.String(required=True, attribute='dstcountry'),
        'bytes_total': fields.Integer(required=True, attribute="bandwidth"),
        'devices': fields.String(required=True, attribute='fortigate'),
    })

    TopDestination = AllMetricData.clone('TopDestination', {
        'data': fields.List(fields.Nested(TopDestinationData), default=[])
    })
    # ---------------- top destination model ENDS HERE ----------------
    # --------------------- BandwidthRateData model ---------------------
    BandwidthRateData = Model('BandwidthRateData', {
        'bi_bandwidth': fields.Integer(required=True),
        'timestamp': fields.Integer(required=True),
        'rx_bandwidth': fields.Integer(required=True),
        'rx_bytes': fields.Integer(required=True),
        'tx_bandwidth': fields.Integer(required=True),
        'tx_bytes': fields.Integer(required=True),
    })

    BandwidthRate = AllMetricData.clone('BandwidthRate', {
        'data': fields.List(fields.Nested(BandwidthRateData), default=[])
    })
    # ----------------BandwidthRateData model ENDS HERE ----------------

    # --------------------- Link-Qality-StatusData model ---------------------
    LinkQualityStatusData = Model('LinkQualityStatusData', {
        'itime': fields.String(required=True),
        'latency': fields.String(required=True),
        'packetloss': fields.String(required=True),
        'jitter': fields.String(required=True),
        'interface': fields.String(required=True),

    })
    LinkQualityStatus = AllMetricData.clone('LinkQualityStatus', {
        'data': fields.List(fields.Nested(LinkQualityStatusData), default=[])
    })
    # ----------------LinkQualityStatusData model ENDS HERE ----------------

    # --------------------- top-policy-hits model ---------------------
    TopPolicyHitsData = Model('TopPolicyHitsData', {
        'policy': fields.String(required=True),
        'policy_filter': fields.String(required=True),
        'source_interface': fields.String(required=True, attribute='srcintf'),
        'destination_interface': fields.String(required=True, attribute='dstintf'),
        'bytes_total': fields.Integer(required=True, attribute="bandwidth"),
        'timestamp': fields.String(required=True, attribute='time_stamp'),
        'counts': fields.Integer(required=True),
        'policy_type': fields.String(required=True, attribute='policytype'),
        'VDOM': fields.String(required=True, attribute='vd'),
        'device_name': fields.String(required=True, attribute='dev_name'),
        'device_id': fields.String(required=True, attribute='devid')

    })

    TopPolicyHits = AllMetricData.clone('TopPolicyHits', {
        'data': fields.List(fields.Nested(TopPolicyHitsData), default=[])
    })
    # ----------------top-polivy-hits model ENDS HERE ----------------

    # --------------------- top users model ---------------------
    TopUsersData = Model('TopUsersData', {
        'sessions': fields.Integer(required=True),
        'source_ip': fields.String(required=True, attribute='srcip'),
        'bytes_total': fields.Integer(required=True, attribute="bandwidth"),
        'bytes_in': fields.Integer(required=True, attribute="traffic_in"),
        'bytes_out': fields.Integer(required=True, attribute="traffic_out"),
        'device_id':fields.String(required=True, attribute='fortigate')
    })

    TopUsersDetails = AllMetricData.clone('TopUsersDetails', {
        'data': fields.List(fields.Nested(TopUsersData), default=[])
    })
    # ---------------- top users model ENDS HERE ----------------
    # --------------------- site-map model ---------------------
    SiteAddress = Model('SiteAddress', {
        'address1': fields.String(required=True),
        'address2': fields.String(required=True),
        'city': fields.String(required=True),
        'state': fields.String(required=True),
        'postalcode': fields.String(required=True),
        'country': fields.String(required=True)
    })
    SiteDeviceData = Model('SiteDeviceData', {
        'serial_number': fields.String(required=True),
        'devid': fields.String(required=True),
        'status':fields.String(required=True),
    })
    SiteMapData = Model('SiteMapData', {
        'adom_name': fields.String(required=True),
        'site_id': fields.Integer(required=True),
        'address': fields.Nested(SiteAddress, default=""),
        'latitude': fields.String(required=True),
        'longitude': fields.String(required=True),
        'devices': fields.List(fields.Nested(SiteDeviceData), default=[]),
        'status': fields.String(required=True)


    })

    SiteMap = AllMetricData.clone('SiteMap', {
        'data': fields.List(fields.Nested(SiteMapData), default=[])
    })
    # ---------------- site-map model ENDS HERE ----------------

    # --------------------- top application usage model ---------------------
    TopApplicationsUsageData = Model('TopApplicationsUsageData', {
        "application": fields.String(required=True, attribute='app_group'),
        "number_of_users": fields.Integer(required=True, attribute='num_users'),
        "bytes_total": fields.Integer(required=True, attribute="bandwidth"),
        "device_id": fields.String(required=True, attribute='fortigate')
    })

    TopApplicationsUsageDetails = AllMetricData.clone('TopApplicationsUsageDetails', {
        'data': fields.List(fields.Nested(TopApplicationsUsageData), default=[])
    })
    # ---------------- top application usage model ENDS HERE ----------------

    # --------------------- top application categories model ---------------------
    ApplicationCategoriesData = Model('ApplicationCategoriesData', {
        "app_category": fields.String(required=True, attribute='appcat'),
        "bytes_total": fields.Integer(required=True, attribute="bandwidth"),
        "application": fields.String(required=True, attribute='app_group'),
        "bytes_in": fields.Integer(required=True, attribute="traffic_in"),
        "bytes_out": fields.Integer(required=True, attribute="traffic_out"),
        "risk": fields.String(required=True),
        "device_id": fields.String(required=True)
    })

    ApplicationCategoriesDetails = AllMetricData.clone('ApplicationCategoriesData', {
        'data': fields.List(fields.Nested(ApplicationCategoriesData), default=[])
    })
    # ---------------- top application categories model ENDS HERE ----------------

    # --------------------- top sources by bandwidth model ---------------------
    TopSourcesByBandwidthData = Model('TopSourcesByBandwidthData', {
        'source_ip': fields.String(required=True, attribute='srcip'),  # srcip
        'source_interface': fields.String(required=True, attribute='srcintf'),  # srcintf
        'threat_weight': fields.Integer(required=True, attribute="threatweight"),
        'bytes_total': fields.Integer(required=True, attribute="bandwidth"),
        'bytes_in': fields.Integer(required=True, attribute="traffic_in"),
        'bytes_out': fields.Integer(required=True, attribute="traffic_out"),
        'device_id': fields.String(required=True),
    })

    TopSourcesByBandwidthDetails = AllMetricData.clone('TopSourcesByBandwidthDetails', {
        'data': fields.List(fields.Nested(TopSourcesByBandwidthData), default=[])
    })
    # ---------------- top sources by bandwidth model ENDS HERE ----------------
    # --------------------- risk analysis model ---------------------
    RiskAnalysisData = Model('RiskAnalysisData', {
        "app_risk": fields.String(required=True, attribute='risk'),
        "number_of_users": StingToInt(attribute="num_users"),
        "app": fields.String(required=True, attribute="app_group"),
        "bytes_in": StingToInt(attribute="traffic_in"),
        "bytes_out": StingToInt(attribute="traffic_out"),
        "device_id": fields.String(required=True, attribute="fortigate"),
        "level": fields.Integer()
    })

    RiskAnalysisDetails = AllMetricData.clone('RiskAnalysisDetails', {
        'data': fields.List(fields.Nested(RiskAnalysisData), default=[])
    })
    # ---------------- risk analysis model ENDS HERE ----------------
    # --------------------- sd wan usage model ---------------------
    SdWanUsageData = Model('SdWanUsageData', {
        "vwlservice": fields.String(required=True),
        "interface": fields.String(required=True),
        "app_group": fields.String(required=True),
        "app_id": fields.Integer(required=True),
        "bytes_total": fields.Integer(required=True, attribute="bandwidth"),
    })

    SdWanUsageDataDetails = AllMetricData.clone('SdWanUsageDataDetails', {
        'data': fields.List(fields.Nested(SdWanUsageData), default=[])
    })
    # ---------------- sd wan usage model ENDS HERE ----------------

    InputPayLoad = Model('InputPayLoad', {
        'filter': fields.List(fields.Nested(MetricFilter)),
        'sort-by': fields.List(fields.Nested(MetricSortBy)),
        'limit': fields.Integer(),
        'start_date': fields.String(),
        'end_date': fields.String()
    })

    # --------------------- Link-Qality-StatusData model ---------------------
    LinkQualityStatusSlaLogsData = Model('LinkQualityStatusSlaLogsData', {
        'timestamp': StingToInt(),
        'latency': fields.String(required=True),
        'packetloss': fields.String(required=True),
        'jitter': fields.String(required=True),
        'link': fields.String(required=True),
        'device_id': fields.String(required=True),
        'interface': fields.String(required=True),
    })
    LinkQualityStatusSlaLogs = AllMetricData.clone('LinkQualityStatusSlaLogs', {
        'data': fields.List(fields.Nested(LinkQualityStatusSlaLogsData), default=[])
    })
    # ----------------LinkQualityStatusData model ENDS HERE ----------------

    # --------------------- Bandwidth-summary model ---------------------
    BandwidthSummaryInterfaceValues =  Model('BandwidthSummaryInterfaceValues', {
        'rx_bytes': StingToInt(),
        'tx_bytes': StingToInt(),
        'timestamp': StingToInt(),
    })

    BandwidthSummaryWanData = Model('BandwidthSummaryWanData', {
        'interface': fields.String(),
        'ip': fields.String(),
        'link': LinkStatus(),
        'speed': StingToInt(),
        'device_id': fields.String(),
        'values': fields.List(fields.Nested(BandwidthSummaryInterfaceValues), default=[])
    })

    BandwidthSummaryMetricData = AllMetricData.clone('BandwidthSummaryMetricData', {
        'data': fields.List(fields.Nested(BandwidthSummaryWanData), default=[])
    })
    # ----------------Bandwidth-summary model ENDS HERE ----------------

    # --------------------- sla-monitor model ---------------------
    ValuesData = Model('ValuesData', {
        'latency': fields.Float(),
        'packetloss': fields.Float(),
        'jitter': fields.Float(),
        'timestamp': StingToInt(),
    })

    SlaValues =  Model('SlaValues', {
        'id': StingToInt(),
        'jitter-threshold': StingToInt(),
        'latency-threshold': StingToInt(),
        'packetloss-threshold': StingToInt(),
    })

    SlaMonitorData = Model('SlaMonitorData', {
        'interface': fields.String(),
        'device_id': fields.String(),
        'sla': fields.List(fields.Nested(SlaValues), default=[]),
        'values': fields.List(fields.Nested(ValuesData), default=[]),
    })

    SlaMonitorMetricData = AllMetricData.clone('SlaMonitorMetricData', {
        'data': fields.List(fields.Nested(SlaMonitorData), default=[])
    })
    # ----------------sla-monitor model ENDS HERE ----------------

    # --------------------- top-threats model ---------------------
    TopThreatsData = Model('TopThreatsData', {
        'threat': fields.String(),
        'threattype': fields.String(),
        'threatlevel': fields.String(),
        'level_s': fields.String(),
        'threatweight': fields.String(),
        'threat_block': fields.String(),
        'threat_pass': fields.String(),
        'incidents': fields.String(),
        'incident_block': fields.String(),
        'incident_pass': fields.String(),
        'device_id': fields.String(attribute="fortigate"),
        'appid': fields.String(),
    })

    TopThreatsMetricData = AllMetricData.clone('TopThreatsMetricData', {
        'data': fields.List(fields.Nested(TopThreatsData), default=[])
    })
    # ----------------top-threats model ENDS HERE ----------------

    EmptyDict = Model('EmptyDict', {
    })

    MetricResponse = AllMetricData.clone('MetricResponse', {
        'data': fields.List(fields.Nested(EmptyDict), default=[])
    })

    @staticmethod
    def metric_response(api):
        api.models[MetricsModel.MetricFilter.name] = MetricsModel.MetricFilter
        api.models[MetricsModel.MetricSortBy.name] = MetricsModel.MetricSortBy
        api.models[MetricsModel.AllMetricData.name] = MetricsModel.AllMetricData
        api.models[MetricsModel.EmptyDict.name] = MetricsModel.EmptyDict
        api.models[MetricsModel.MetricResponse.name] = MetricsModel.MetricResponse
        return MetricsModel.MetricResponse


    @staticmethod
    def paylaod(api):
        api.models[MetricsModel.MetricFilter.name] = MetricsModel.MetricFilter
        api.models[MetricsModel.MetricSortBy.name] = MetricsModel.MetricSortBy
        api.models[MetricsModel.InputPayLoad.name] = MetricsModel.InputPayLoad
        return MetricsModel.InputPayLoad
