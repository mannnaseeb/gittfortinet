import datetime
from flask import g, request
from flask_restx import marshal
from languages.fortinet_api_languages import ErrorResponse
from languages.fortinet_api_exceptions import NoRecordFoundException
from db_settings.db_utils import get_all_report_data_from_database, delete_report_tid_into_database

from constants import EPOCH_TO_DATETIME_FORMAT, \
    APP_CATEGORY_NOT_SCANNED, LINK_QUALITY_STATUS_FILTER_BY_INTERFACE,ADOM_EPOCH_TO_DATETIME_FORMAT,\
    NO_RECORD_FOUND, PERMITTED_STATUS_SITE_DETAILS, RISK_ANALYSIS_LEVELS, FILTER_BY_DEVICE_ID, DEVID_OPERATOR
from api_models.adom_api_model import AdomModel, AdombyNameModel, AdomidModel, SystemStatusModel
from api_models.metric_api_model import MetricsModel
from api_models.report_api_model import AdomreportsModel, DefaultReport
from models.report_meta import ReportMeta


class FortinetConverters:
    """FortinetConverters"""
    def __init__(self):
        self._all_adoms = AdomModel.AllAdomsData
        self._all_adom_name = AdombyNameModel.AdomsbynameData
        self._all_adom_all_device = AdomidModel.AdomsidData
        self._all_metrics_list_of_classification_and_data = MetricsModel.MetricsListOfClassifiersAndData
        self._all_metrics_data = MetricsModel.AllMetricData
        self._site_details_data = MetricsModel.SiteDetails
        self._top_applications_data = MetricsModel.TopApplications
        self._application_threats_data = MetricsModel.TopApplicationThreatsDetails
        self._traffic_summary_data = MetricsModel.TrafficSummaryDetails
        self._top_users_data = MetricsModel.TopUsersDetails
        self._top_destiantion_data = MetricsModel.TopDestination
        self.bandwidth_rate = MetricsModel.BandwidthRate
        self._site_map = MetricsModel.SiteMap
        self._top_applications_usage_data = MetricsModel.TopApplicationsUsageDetails
        self._application_categories_data = MetricsModel.ApplicationCategoriesDetails
        self._top_sources_by_bandwidth_data = MetricsModel.TopSourcesByBandwidthDetails
        self._risk_analysis_data = MetricsModel.RiskAnalysisDetails
        self.link_quality_status = MetricsModel.LinkQualityStatus
        self.top_policy_hits = MetricsModel.TopPolicyHits
        self.link_quality_status_sla_logs = MetricsModel.LinkQualityStatusSlaLogs
        self.sd_wan_usage_data = MetricsModel.SdWanUsageDataDetails
        self._adom_reports = AdomreportsModel.AdomReportsData
        self._adomdownloadreports =AdomreportsModel.AdomDownloadReports
        self.bandwidth_summary_data = MetricsModel.BandwidthSummaryMetricData
        self.sla_monitor_data = MetricsModel.SlaMonitorMetricData
        self.top_threats_data = MetricsModel.TopThreatsMetricData
        self.syste_status = SystemStatusModel.Status
        self.report_default = DefaultReport

    # pylint: disable=R0201
    def convert_date(self, str_inp):
        """
            Used to convert given string to required date format
           :param str_inp: the string that needs to be converted
           :return:
       """
        epoch = None
        try:
            inp_datetime = datetime.datetime.fromisoformat(str_inp)
            epoch = int(inp_datetime.timestamp())
        except ValueError:
            epoch = int(str_inp)
        #epoch value with > 10 characters used for millisecond
        # precision which would give us an issue during conversion
        #Hence we cut it to 10 charcters
        if (total_length := len(str(epoch))) > 10:
            remove_places = 10**(total_length - 10)
            epoch = int(epoch)//remove_places
        return datetime.datetime.fromtimestamp(epoch).strftime(EPOCH_TO_DATETIME_FORMAT)

    # pylint: disable=R0201
    def convert_response_to_sorted_format(self, req_payload, final_response):
        """convert response to sorted format"""

        sort_by_order = req_payload["sort-by"][0]["order"]
        sort_by_field = req_payload["sort-by"][0]["field"]
        reverse = True if sort_by_order == 'desc' else False
        sorted_data = sorted(final_response, key=lambda x: int(x[sort_by_field]), reverse=reverse)
        sorted_response = sorted_data[0:req_payload['limit']] if 'limit' in req_payload and req_payload[
            'limit'] else sorted_data
        return sorted_response

    # pylint: disable=R0201
    def convert_args(self, args):
        """convert to args."""
        request_paload = {}
        for arg in args:
            request_paload[arg] = args[arg]
        return request_paload

    # pylint: disable=R0201
    def convert_payload_for_instant_metric(self, req_payload):
        """
            converts request payload data as required
           :param request payload: the request payload received
           :return:
       """
        req_payload = self.convert_to_comma_seperated(req_payload)
        req_payload = self.create_time_range_in_payload(req_payload)
        return req_payload

    # pylint: disable=R0201
    def convert_payload_for_reports(self, req_payload):
        """
            converts request payload data as required
           :param request payload: the request payload received
           :return:
       """
        if 'start_date' in req_payload and 'end_date' in req_payload:
            req_payload = self.create_time_range_in_payload(req_payload)
        return req_payload

    # pylint: disable=R0201
    def convert_payload_for_timeseries_metric(self, req_payload):
        """
            converts request payload data as required
           :param request payload: the request payload received
           :return:
       """
        req_payload = self.convert_to_comma_seperated(req_payload)
        req_payload = self.create_time_range_in_payload(req_payload)
        return req_payload

    def convert_to_comma_seperated(self, req_payload):
        """
            Converts filter data from request payload as required
           :param request payload: the request payload received
           :return:
       """
        if req_payload.get('filter'):
            filters = []
            for filter_item in req_payload.get('filter'):
                filters.append(f"{filter_item['key']}{filter_item['operation']}{filter_item['value']}")
            req_payload['filter'] = ",".join(filters)
        return req_payload

    def create_time_range_in_payload(self, req_payload):
        """creating time range from epoch start and end date"""
        req_payload['time-range'] = {
            "start": self.convert_date(req_payload['start_date']),
            "end": self.convert_date(req_payload['end_date'])
        }
        del req_payload['start_date']
        del req_payload['end_date']
        return req_payload

    def convert_response_get_adom_by_name(self, response):
        """
        creates final response for adom by name
        :param response: raw response from API
        :return: converted response
        """
        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            response.data['id'] = g.Correlationid
            store_marshal = marshal(response.data, self._all_adom_name)
            return store_marshal

    def convert_response_get_all_adom(self, response):
        """
        creates final response for all adoms
        :param response: raw response from API
        :return: converted response
        """
        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            response.data['id'] = g.Correlationid
            store_marshal = marshal(response.data, self._all_adoms)
            return store_marshal

    def convert_tid_to_key_for_filter(self,reports):
        """convert tid to key for filter"""
        json_by_tid_as_key = {}
        for report in reports:
            json_by_tid_as_key[report['tid']] = report
        return json_by_tid_as_key

    def convert_response_get_report_by_title(self, response,title):
        """
        creates final response for adom device by id
        :param response: raw response from API
        :return: converted response
        """
        report_response = []
        report_data_by_title = get_all_report_data_from_database(title)
        if not report_data_by_title:
            raise NoRecordFoundException(message=NO_RECORD_FOUND)
        api_report = self.convert_tid_to_key_for_filter(response.original_response.json()['result']['data'])
        for report in report_data_by_title:
            current_report = api_report.get(report.ReportTid,[])
            if current_report:
                report_response.append(current_report)
            else:
                report.state = "running" if report.StatusID == 2 else "generated"
                report.format = [report.ReportFormat]
                devices = report.DevicesData
                if devices:
                    report.device = {'count':len(devices.split(",")),'data':devices}
                report_marshal = marshal(report,self.report_default)
                report_response.append(report_marshal)
        return report_response

    def convert_response_delete_report_by_tid(self, response,tid):
        """
        'status': {'code': 0, 'message': 'succeeded'}
        """
        report_response = [response.original_response.json()['result']]
        delete_report_tid_into_database(tid)
        return report_response

    def convert_response_get_device_by_id(self, response):
        """
        creates final response for adom device by id
        :param response: raw response from API
        :return: converted response
        """
        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            store_marshal = marshal(response.data, self._all_adom_all_device)
            return store_marshal

    def convert_response_get_instant_metric(self, req_payload, metric_name, response):
        """
        creates final response for instant metric
        :param response: raw response from API
        :return: converted response
        """
        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        response.data['id'] = g.Correlationid
        store_marshal = marshal(response.data, self._all_metrics_data)
        if req_payload.get('filter'):
            store_marshal['filter'] = req_payload.get('filter')
        store_marshal['metric'] = metric_name
        if req_payload.get('sort-by'):
            store_marshal['sort-by'] = req_payload['sort-by']
        if req_payload.get('limit'):
            store_marshal['limit'] = req_payload['limit']
        if response.data:
            store_marshal['data'] = response.data.get('result').get('data', [])
        return store_marshal

    def convert_widget_response(self, req_payload, metric_name, response):
        """
        creates final response for instant metric widget API's
        :param response: raw response from API
        :return: converted response
        """
        store_marshal = {}
        # since the original request payload has changed, get the data from the original request data
        actual_req_payload = request.json
        if actual_req_payload.get('filter'):
            store_marshal['filter'] = actual_req_payload.get('filter')
        store_marshal['metric'] = metric_name
        if actual_req_payload.get('sort-by'):
            store_marshal['sort-by'] = actual_req_payload['sort-by']
        if actual_req_payload.get('limit'):
            store_marshal['limit'] = actual_req_payload['limit']
        store_marshal['data'] = response
        return store_marshal

    def convert_to_site_details(self, req_payload, metric_name,  sites_up_count, sites_down_count, sites_alert_count, filter_by_status):
        """
        creates final response for instant metric: site-details

        """

        response = [{'sites_up': sites_up_count, 'sites_down': sites_down_count,'sites_alert': sites_alert_count }]

        if filter_by_status:
            data = {}
            for status in filter_by_status:
                data.update({'sites_'+status: response[0]['sites_'+status]})
            response[0] = data

        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data = self.remove_none_fields(req_payload,converted_response)
        return final_data

    def convert_to_application_threats(self, req_payload, metric_name, analyzer_response):
        """
        summary: creates final response for instant metric: top-application-threats
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - analyzer_response: response from analyzer
        returns: final converted response
        """
        response = []
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload, analyzer_response)
        if 'limit' in req_payload and req_payload['limit']:
            response.extend(analyzer_response[0:req_payload['limit']])
        else:
            response.extend(analyzer_response[0:])
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data = marshal(converted_response, self._application_threats_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_top_applications(self, req_payload, metric_name, analyzer_response):
        """
        creates final response for instant metric: top-applications
        :param response: response from analyzer for top-applications
        :return: converted response
        """
        response = []
        keys_required = {'app_group', 'sessions'}
        if 'result' in analyzer_response.data and 'data' in analyzer_response.data['result']:
            if type(analyzer_response.data['result']['data']) is list:
                for adom in analyzer_response.data['result']['data']:
                    # ---------- picks required keys and its value ----------
                    response.append({key: adom[key] for key in adom.keys() & keys_required})
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        return marshal(converted_response, self._top_applications_data)


    def convert_to_traffic_summary(self, req_payload, metric_name, final_response_from_service):
        """
        summary: creates final response for instant metric: traffic-summary
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_from_service: list containing response from manager and analyzer for specific adom
        returns: final converted response
        """
        final_converted_response = []
        for adom_response in final_response_from_service:
            device_ids = []
            analyzer_response = adom_response['analyzer_response']
            if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                    analyzer_response.data['result']:
                for device in analyzer_response.data['result']['data']:
                    device['adom'] = adom_response.get('adom_name', None)
                    if 'device_info' in device and device['device_info']:
                        device['dev_name'] = device.get('device_info', {}).get('dev_name', None)
                        device['srcip'] = device.get('device_info', {}).get('srcip', None)
                        device['devid'] and device_ids.append(device['devid'])
                    final_converted_response.append(device)
            manager_response = adom_response['manager_response']
            if manager_response.data is not None and 'data' in manager_response.data:
                for device in manager_response.data['data']:
                    if 'serial_number' in device and device['serial_number']:
                        if device['serial_number'] not in device_ids:
                            if adom_response['hostname_filter_list']:
                                if device.get('hostname', None) and device.get('hostname') not in adom_response['hostname_filter_list']:
                                    continue
                            dev = {}
                            dev['adom'] = adom_response.get('adom_name', None)
                            dev['devid']=device.get('serial_number',None)
                            dev['dev_name']=device.get('hostname',None)
                            dev['srcip']=device.get('ip_address',None)
                            dev['cpu_ave']=""
                            dev['mem_ave']=""
                            dev['disk_ave']=""
                            dev['sent_kbps']=0
                            dev['recv_kbps']=0
                            final_converted_response.append(dev)

        final_converted_response = final_converted_response[0:req_payload['limit']] if 'limit' in req_payload and \
                                                                                       req_payload[
                                                                                           'limit'] else final_converted_response
        converted_response = self.convert_widget_response(req_payload, metric_name, final_converted_response)
        final_data = marshal(converted_response, self._traffic_summary_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_top_users(self, req_payload, metric_name, analyzer_response):
        """
        creates final response for instant metric: top-users
        :param response: response from analyzer
        :return: converted response
        """
        limit = int()
        response = []
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload=req_payload,
                                                                   final_response=analyzer_response)
        if req_payload.get('limit'):
            limit = req_payload['limit']
        if limit:
            analyzer_response = analyzer_response[:limit]
        keys_required = {'adom', 'sessions', 'srcip', 'bandwidth', 'traffic_in', 'traffic_out', 'fortigate'}
        if type(analyzer_response) == list and len(analyzer_response) >= 1:
            for adom in analyzer_response:
                # ---------- picks required keys and its value ----------
                response.append({key: adom[key] for key in adom.keys() & keys_required})
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data =  marshal(converted_response, self._top_users_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_top_destination(self, req_payload, metric_name, analyzer_response):
        """
            creates final response for instant metric: top-destination
            :param response: response from analyzer
            :return: converted response
        """
        limit = int()
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload=req_payload,
                                                                   final_response=analyzer_response)
        if req_payload.get('limit'):
            limit = req_payload['limit']
        if limit:
            analyzer_response = analyzer_response[0:limit]
        response = list()
        if type(analyzer_response) == list and len(analyzer_response) >= 1:
            for destination in analyzer_response:
                data, data['adom'], data['dstcountry'], data['bandwidth'], data['fortigate'] = \
                    {}, destination.get('adom', None), destination.get('dstcountry', None), \
                    destination.get('bandwidth', 0), destination.get('fortigate', None)
                response.append(data)
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data =  marshal(converted_response, self._top_destiantion_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_bandwidth_rate(self, req_payload, metric_name, analyzer_response):
        """
            creates final response for instant metric: bandwidth-rate
            :param response: response from analyzer
            :return: converted response
        """
        limit = int()
        if req_payload.get('limit'):
            limit = req_payload['limit']
        if limit:
            analyzer_response = analyzer_response[:limit]
        response = list()
        if type(analyzer_response) == list and len(analyzer_response) >= 1:
            for analyzer_data in analyzer_response:
                data, data['adom'], data['itime'], data['srcintf'], data['srcip'], \
                data['dstintf'], data['destination_ip'], data['sentbyte'], \
                data['rcvdbyte'] = {}, analyzer_data['adom'], analyzer_data['itime'], analyzer_data['srcintf'], \
                                   analyzer_data['srcip'], analyzer_data['dstintf'], analyzer_data['dstip'], \
                                   analyzer_data['sentbyte'], analyzer_data['rcvdbyte']

                response.append(data)
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        return marshal(converted_response, self.bandwidth_rate)


    def convert_to_site_map(self, req_payload, metric_name, all_sites_consolidated_data):
        """
        summary: creates final response for instant metric: site-map
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing analyzer response for specific adom
        returns: final converted response
        """
        if 'limit' in req_payload and req_payload['limit']:
            all_sites_consolidated_data = all_sites_consolidated_data[0:req_payload['limit']]
        converted_response = self.convert_widget_response(req_payload, metric_name, all_sites_consolidated_data)
        final_data = marshal(converted_response, self._site_map)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_top_applications_usage(self, req_payload, metric_name, analyzer_response):
        """
        summary: creates final response for instant metric: top-applications-usage
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - analyzer_response: response from analyzer
        returns: final converted response
        """
        response = []
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload, analyzer_response)
        if 'limit' in req_payload and req_payload['limit']:
            response.extend(analyzer_response[0:req_payload['limit']])
        else:
            response.extend(analyzer_response[0:])
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data =  marshal(converted_response, self._top_applications_usage_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_applications_categories(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for instant metric: application-categories
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing analyzer response for specific adom
        returns: final converted response
        """
        final_response,sorted_response, comman_response, app_list = [], [], [], []
        for response_data in final_response_integrator:
            analyzer_response = response_data['analyzer_response']
            if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                    analyzer_response.data['result']:
                if type(analyzer_response.data['result']['data']) is list:
                    for usage_data in analyzer_response.data['result']['data']:
                        # ---------- picks required keys and its value ----------
                        final_response.append({'adom': response_data['adom_name'], 'appcat': usage_data['appcat'],
                                               'bandwidth': usage_data['bandwidth'],
                                               'app_group': usage_data['app_group'],
                                               'traffic_in': usage_data['traffic_in'],
                                               'traffic_out': usage_data['traffic_out'], 'risk': usage_data['risk'],
                                               'sessions': usage_data['sessions'],
                                               'device_id': usage_data['fortigate']})
        
        #-----------This code add multiple same appcate data into one appcate----------------------#
        for num in range(len(final_response)):
            appcat = final_response[num].get("appcat")
            if  appcat not in app_list:
                appdata = final_response[num]
                app_list.append(appcat)
                for num1 in range(num+1,len(final_response)):
                    if final_response[num1].get("appcat") == appcat  :
                            appdata['bandwidth'] = int(appdata['bandwidth']) +   int(final_response[num1]['bandwidth'])
                            appdata['traffic_in'] = int(appdata['traffic_in']) +   int(final_response[num1]['traffic_in'])
                            appdata['traffic_out'] = int(appdata['traffic_out']) +   int(final_response[num1]['traffic_out'])
                            appdata['app_group'] = appdata['app_group'] +","+ final_response[num1]['app_group'] 
                comman_response.append(appdata)
        #---------End This code add multiple same appcate data into one appcate--------------------#
        if "sort-by" in req_payload:
            sorted_response = self.convert_response_to_sorted_format(req_payload, comman_response)
        if not sorted_response:
            sorted_response = comman_response     
        if sorted_response and 'limit' in req_payload and req_payload['limit']:
            sorted_response = sorted_response[0:req_payload['limit']]
        converted_response = self.convert_widget_response(req_payload, metric_name, sorted_response)
        final_data =  marshal(converted_response, self._application_categories_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_risk_analysis(self, req_payload, metric_name, analyzer_response):
        """
        summary: creates final response for instant metric: riskp-analysis
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - analyzer_response: response from analyzer
        returns: final converted response
        """
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload, analyzer_response)
        if 'limit' in req_payload and req_payload['limit'] and 'sort-by' not in req_payload:
            analyzer_response = analyzer_response[0:req_payload['limit']]
        converted_response = self.convert_widget_response(req_payload, metric_name, analyzer_response)
        #---------------- Check risk level  ---------------
        if 'data' in converted_response:
            for device_risk in converted_response.get('data', []):
                app_risk = str(device_risk.get('risk','')).lower()
                device_risk['level'] =RISK_ANALYSIS_LEVELS.get(app_risk, None)
        # ----------- Check risk level ENDS HERE ----------
        final_data =  marshal(converted_response, self._risk_analysis_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_sources_by_bandwidth(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for instant metric: top-sources-by-bandwidth
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing analyzer response for specific adom
        returns: final converted response
        """
        final_response , sorted_final_response = [], []
        for response_data in final_response_integrator:
            analyzer_response = response_data['analyzer_response']
            if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                    analyzer_response.data['result']:
                if type(analyzer_response.data['result']['data']) is list:
                    for usage_data in analyzer_response.data['result']['data']:
                        # ---------- picks required keys and its value ----------
                        hold_result = {}
                        hold_result['adom'] = response_data.get('adom_name')
                        hold_result['srcip'] = usage_data.get('srcip')
                        hold_result['srcintf'] = usage_data.get('srcintf')
                        hold_result['threatweight'] = int(usage_data.get('threatweight', 0))
                        hold_result['bandwidth'] = int(usage_data.get('bandwidth', 0))
                        hold_result['traffic_in'] = int(usage_data.get('traffic_in', 0))
                        hold_result['traffic_out'] = int(usage_data.get('traffic_out', 0))
                        hold_result['device_id'] = usage_data.get('fortigate')
                        final_response.append(hold_result)
        if "sort-by" in req_payload:
            sorted_final_response = self.convert_response_to_sorted_format(req_payload, final_response)
        if not sorted_final_response:
            sorted_final_response =final_response
        converted_response = self.convert_widget_response(req_payload, metric_name, sorted_final_response)
        final_data = marshal(converted_response, self._top_sources_by_bandwidth_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_link_quality_status(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for instant metric: link-quality-status
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing analyzer response for specific adom
        returns: final converted response
        """
        final_response = []
        for response_data in final_response_integrator:
            analyzer_response = response_data['analyzer_response']
            if 'result' in analyzer_response.data and 'data' in analyzer_response.data['result']:
                for analyzer_data in analyzer_response.data['result']['data']:
                    final_response.append({'itime': analyzer_data.get('itime', None),
                                           'latency': analyzer_data.get('latency', None),
                                           'packetloss': analyzer_data.get('packetloss', None),
                                           'jitter': analyzer_data.get('jitter'),
                                           'adom': response_data['adom_name'],
                                           'interface': analyzer_data.get('interface')})
        final_response = final_response[0:req_payload['limit']] if 'limit' in req_payload and req_payload[
            'limit'] else final_response
        converted_response = self.convert_widget_response(req_payload, metric_name, final_response)
        return marshal(converted_response, self.link_quality_status)

    def convert_to_top_policy_hits(self, req_payload, metric_name, analyzer_response):
        """
            creates final response for instant metric: top- policy -hits
            :param response: response from analyzer
            :return: converted response
        """
        limit = int()
        response = list()
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload=req_payload,
                                                                       final_response=analyzer_response)
        if req_payload.get('limit'):
            limit = req_payload['limit']
        if limit:
            analyzer_response = analyzer_response[:limit]
        if type(analyzer_response) == list and len(analyzer_response) >= 1:
            for analyzer_data in analyzer_response:
                data, data['policy'], data['policy_filter'], data['srcintf'], \
                data['dstintf'], data['bandwidth'], data['adom'], data['time_stamp'], data['counts'], data[
                    'policytype'], data['vd'], data['dev_name'], data['devid'] = {}, analyzer_data['policy'], \
                                                                  analyzer_data['policy_filter'], \
                                                                  analyzer_data['srcintf'], \
                                                                  analyzer_data['dstintf'], analyzer_data['bandwidth'], \
                                                                  analyzer_data['adom'], analyzer_data['time_stamp'], \
                                                                  analyzer_data['counts'], \
                                                                  analyzer_data['policytype'], analyzer_data['vd'], \
                                                                  analyzer_data['device_info']['dev_name'], \
                                                                  analyzer_data['devid']
                response.append(data)
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data = marshal(converted_response, self.top_policy_hits)
        return self.remove_none_fields(req_payload,final_data)

    def extract_adom_devices(self, manager_response):
        """
        summary: extracts all the devices belonging to an adom
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - manager_response: response from manager
        returns: final converted response
        """
        if manager_response and 'data' in manager_response.data and type(manager_response.data['data']) == list:
            adom_device_ids = [next(iter(device.get('vdom', [])), {}).get('device_id', '') for device in manager_response.data['data']]
            #remove any empty values from list and returns the list
            return ' '.join(adom_device_ids).split()

    def convert_payload_for_timeseries(self, req_payload, start_date, end_date):
        """
        summary: converts the request payload as required for sla logs API
        description: This method converts the request payload as required for sla logs API to the main converter method and returns final
                    converted response
        parameters:
            - manager_response: response from manager
        returns: final converted response
        """
        if start_date and end_date:
            req_payload['timestamp'] = {"start": start_date, "end": end_date}
        return req_payload

    def convert_to_link_quality_status_sla_logs(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for timeseries metric: link-quality-status
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing manager response for specific device of an adom regards sla logs
        returns: final converted response
        """
        #-------- checking key = 'interface' filter in payload --------
        interface_filter_value = [filters.get('value') for filters in  req_payload.get('filter', []) if filters.get('key','') == LINK_QUALITY_STATUS_FILTER_BY_INTERFACE]
        #--- checking key = 'interface' filter in payload ENDS HERE ---
        final_response = []
        for response_data in final_response_integrator:
            manager_response = response_data['manager_response']
            if manager_response and manager_response.data is not None and 'data' in manager_response.data and type(manager_response.data['data']) == list:
                for manager_data in manager_response.data['data']:
                    #-------- Skip record if interface value does not match --------
                    if interface_filter_value and manager_data.get('interface', '') not in interface_filter_value:
                        continue
                    #--- Skip record if interface value does not match ENDS HERE ---
                    for log in manager_data.get('log', []):
                        hold_log = {'adom': response_data.get('adom_name', None),
                                               'device_id': response_data.get('device_id', None),
                                               'timestamp': log.get('timestamp', None),
                                                'interface': manager_data.get('interface', None)
                                    }
                        hold_log.update(log.get('value', {}))
                        final_response.append(hold_log)
        if "sort-by" in req_payload:
            final_response = self.convert_response_to_sorted_format(req_payload, final_response)
        if 'limit' in req_payload and req_payload['limit']:
            final_response = final_response[0:req_payload['limit']]
        converted_response = self.convert_widget_response(req_payload, metric_name, final_response)
        final_data = marshal(converted_response, self.link_quality_status_sla_logs)
        return self.remove_none_fields(req_payload,final_data)


    def convert_to_bandwidth_rate_interface_logs(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for timeseries metric: bandwidth-rate
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing manager response for specific device of an adom regarding interface logs
        returns: final converted response
        """
        final_response = []
        for response_data in final_response_integrator:
            manager_response = response_data['manager_response']
            if manager_response and type(manager_response.data) == list:
                for log in manager_response.data:
                    hold_log = {'timestamp': log.get('timestamp', None)}
                    hold_log.update(log.get('value', {}))
                    final_response.append(hold_log)
        if "sort-by" in req_payload:
            final_response = self.convert_response_to_sorted_format(req_payload, final_response)
        if 'limit' in req_payload and req_payload['limit']:
            final_response = final_response[0:req_payload['limit']]
        converted_response = self.convert_widget_response(req_payload, metric_name, final_response)
        final_data = marshal(converted_response, self.bandwidth_rate)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_sd_wan_usage(self, req_payload, metric_name, analyzer_response):
        """
        summary: creates final response for instant metric: sd-wan-usage
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - analyzer_response: response from analyzer
        returns: final converted response
        """
        response, conveter_resposne = [], []
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload, analyzer_response)
        if 'limit' in req_payload and req_payload['limit']:
            response.extend(analyzer_response[0:req_payload['limit']])
        else:
            response.extend(analyzer_response[0:])
        for data in response :
            if data is not None and  data.get('app_id') == "" :
                data['app_id']= None
            conveter_resposne.append(data)
        converted_response = self.convert_widget_response(req_payload, metric_name, conveter_resposne)
        final_data = marshal(converted_response, self.sd_wan_usage_data)
        return self.remove_none_fields(req_payload,final_data)


    def remove_none_fields(self, request_payload, response_data):
        """remove none fields."""
        actual_req_payload = request.json
        if not actual_req_payload.get("limit") and "limit" in response_data:
            del response_data["limit"]
        if not actual_req_payload.get('filter') and "filter" in response_data:
            del response_data["filter"]
        if not actual_req_payload.get("sort-by") and "sort-by" in response_data:
            del response_data["sort-by"]
        return response_data

    def filter_not_scanned_records(self, analyzer_response):
        """
        summary: ignores records with records with 'Not.Scanned' for: top-application analyzer data
        description: This method filters out records based on following condition:
        1) If record contains app_cat == 'Not.Scanned', the record is ignored/discarded
        2) If record contains app_cat with 'Not.Scanned' as a subset string then 'Not.Scanned'
        is removed from the string and the record is considered/passed
        parameters:
            - analyzer_response: response from analyzer for top-applications
        returns: final converted response
        """
        if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                analyzer_response.data['result']:
            if type(analyzer_response.data['result']['data']) is list:
                analyzer_response_data = analyzer_response.data['result']['data']
                # Ignore records with appcat = 'Not.Scanned'
                analyzer_data = [application for application in analyzer_response_data if
                                     str(application.get('appcat', '')) != APP_CATEGORY_NOT_SCANNED]
                # Checking if 'Not.Scanned' has anything prepended and appended to it
                for application in analyzer_data:
                    if APP_CATEGORY_NOT_SCANNED in application.get('appcat', ''):
                        # Checking if 'Not.Scanned' has anything before and after it
                        if application['appcat'][:application['appcat'].index(APP_CATEGORY_NOT_SCANNED)] and application['appcat'][(
                                application['appcat'].index(APP_CATEGORY_NOT_SCANNED) + len(APP_CATEGORY_NOT_SCANNED)):]:
                            application['appcat'] = application['appcat'].replace('.'+APP_CATEGORY_NOT_SCANNED+'.', '.')
                        # Checking if 'Not.Scanned' has anything before it
                        elif application['appcat'][:application['appcat'].index(APP_CATEGORY_NOT_SCANNED)]:
                            application['appcat'] = application['appcat'].replace('.'+APP_CATEGORY_NOT_SCANNED, '')
                        # Checking if 'Not.Scanned' has anything after it
                        elif application['appcat'][(application['appcat'].index(APP_CATEGORY_NOT_SCANNED) + len(APP_CATEGORY_NOT_SCANNED)):]:
                            application['appcat'] = application['appcat'].replace(APP_CATEGORY_NOT_SCANNED+'.', '')
                #Attaching filtered response back to original response
                analyzer_response.data['result']['data'] = analyzer_data
        return analyzer_response

    def convert_date_adoms(self, str_inp):
        """
            Used to convert str to required date format
           :param str_inp: the string that needs to be converted
           :return:
       """
        epoch = None
        try:
            inp_datetime = datetime.datetime.fromisoformat(str_inp)
            epoch = int(inp_datetime.timestamp())
        except ValueError:
            epoch = int(str_inp)
        #epoch value with > 10 characters used for millisecond precision which would give us an issue during conversion
        #Hence we cut it to 10 charcters
        if (total_length := len(str(epoch))) > 10:
            remove_places = 10**(total_length - 10)
            epoch = int(epoch)//remove_places
        return datetime.datetime.fromtimestamp(epoch).strftime(ADOM_EPOCH_TO_DATETIME_FORMAT)

    def convert_payload_for_adom_reports(self, req_payload, report_metadata: ReportMeta):
        """
            converts request payload data as required
           :param request payload: the request payload received
           :return:
       """
        analyser_req_payload = req_payload.copy()
        analyser_req_payload = self.create_time_range_in_payload_for_adom(analyser_req_payload)
        device_option = list(filter(lambda filter_option: True if filter_option['key'] == "devid" else False, analyser_req_payload.get('filter', [])))
        device_id = device_option and ",".join([devid.get('value', None) for devid in device_option])
        if not device_id:
            device_id = "All_Device"
        new_analyser_req_payload = {"device":device_id,
                                    "title": report_metadata.ReportMetaTitle,
                                    "time-range":analyser_req_payload['time-range']

        }
        return new_analyser_req_payload

    def create_time_range_in_payload_for_list_by_title(self, req_payload):
        """creating time range from epoch start and end date"""
        req_payload['time-range'] = {
            "start": self.convert_date(req_payload['start-date']),
            "end": self.convert_date(req_payload['end-date'])
        }
        del req_payload['start-date']
        del req_payload['end-date']
        return req_payload

    def convert_payload_for_list_by_title(self, req_payload):
        """
            converts request payload data as required
           :param request payload: the request payload received
           :return:
       """
        analyser_req_payload = req_payload.copy()
        if 'time-range' not in analyser_req_payload:
            analyser_req_payload = self.create_time_range_in_payload_for_list_by_title(analyser_req_payload)
        new_analyser_req_payload = {"title": analyser_req_payload.get('title'),
                                    "time-range":analyser_req_payload['time-range']

        }
        return new_analyser_req_payload

    def create_time_range_in_payload_for_adom(self, req_payload):
        """creating time range from epoch start and end date"""
        req_payload['time-range'] = {
            "start": self.convert_date_adoms(req_payload['start_date']),
            "end": self.convert_date_adoms(req_payload['end_date'])
        }
        del req_payload['start_date']
        del req_payload['end_date']
        return req_payload

    def convert_response_adom_reports(self, response):
        """convert response for adom reports."""

        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            store_marshal = marshal(response.data, self._adom_reports)
            return store_marshal

    def convert_response_adom_download_reports(self, response):
        """convert response for adom download reports."""

        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            store_marshal = marshal(response.data.get('result'), self._adomdownloadreports)
            return store_marshal

    def convert_to_bandwidth_summary(self, req_payload, metric_name, final_response_integrator):
        """
        summary: creates final response for instant metric: bandwidth-summary
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing manager response for specific device of an adom regarding interface logs and system monitor
        returns: final converted response
        """
        final_response = []
        for response_data in final_response_integrator:
            all_manager_intfc_response = response_data['manager_intfc_response']
            manager_sys_monitor_response = response_data['manager_sys_monitor_response']
            virtual_wan_healtchk = response_data['manager_virtual_wan_healthchk_response']

            underlay_items = {}
            # -------- Getting all interfaces from 'Underlay' field in virtual wan health check response --------
            if virtual_wan_healtchk.data is not None and 'result' in virtual_wan_healtchk.data and type(
                    virtual_wan_healtchk.data['result']) is list and (
            result_data := next(iter(virtual_wan_healtchk.data['result']), {})) \
                    and 'data' in result_data and (data_items := next(iter(result_data['data']), {})) and 'response' in data_items\
                    and type(data_items.get('response')) == list and (response_items := next(iter(data_items['response']), {}))\
                    and 'results' in response_items and type(response_items['results']) == dict and 'Underlay' in response_items['results']\
                    and (underlay_items := response_items['results']['Underlay']):
                #ignore ports/interfaces having status as error
                underlay_items = {key for key, value in underlay_items.items() if underlay_items[key].get('status', '') != 'error'}
            # --- Getting all interfaces from 'overlay' field in virtual wan health check response ENDS HERE ---

            device_id = str(response_data['device_id'])
            #Checking if any one of the responses if null
            if manager_sys_monitor_response.data is not None and 'result' in manager_sys_monitor_response.data \
                    and type(manager_sys_monitor_response.data['result']) is list \
                    and len(manager_sys_monitor_response.data['result']) > 0 and 'data' in manager_sys_monitor_response.data['result'][0] \
                    and type(manager_sys_monitor_response.data['result'][0]['data']) is list:

                #Looping over system monitor response to get all interfaces
                for item in manager_sys_monitor_response.data['result'][0]['data']:
                    for key, value in item.get('response', {}).get('results', {}).items():
                        #if condition to ignore port/interface if it does not intersect with
                        if key in underlay_items:
                            wan_data = {'speed': value.get('speed', None), "interface": key, 'device_id' : device_id, 'ip':value.get('ip', None),'link':value.get('link', None), "values": []}
                            wan_data['values'] = []
                            #getting matching interface log data
                            manager_intfc_response = all_manager_intfc_response.get(key, None)
                            if 'limit' in req_payload and req_payload['limit'] and manager_intfc_response and manager_intfc_response.data is not None:
                                manager_intfc_response.data = manager_intfc_response.data[0:req_payload['limit']]
                            if manager_intfc_response and manager_intfc_response.data is not None:
                                #Looping over interface logs
                                for int_log in manager_intfc_response.data:
                                    wan_data['values'].append({'rx_bytes': int_log.get('value', {}).get('rx_bytes', None), 'tx_bytes': int_log.get('value', {}).get('tx_bytes', None), 'timestamp': int_log.get('timestamp', None)
                                                      })
                            final_response.append(wan_data)
        converted_response = self.convert_widget_response(req_payload, metric_name, final_response)
        final_data = marshal(converted_response, self.bandwidth_summary_data)
        return self.remove_none_fields(req_payload,final_data)

    def extract_templates_device_relationship(self, manager_wan_templates_response):
        """
        summary: extracts all the relationship on templates to devices
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - manager_wan_templates_response: response from manager for wan templates
        returns: final converted response
        return structure: {'templates':{'template_ids'}, 'template_device_relation': {'template_id': ['device_id']} ,
        'device_template_relation': {'device_id':['template_id']} }
        """
        if manager_wan_templates_response.data is not None:
            # Storing template names, structure: {'template_ids'}
            templates = {item.get('name') for item in next(iter(manager_wan_templates_response.data.get('result', [])), {}).get('data', []) if item.get('name')}
            # Storing template-device relation, structure: {'template_id': ['device_id']}
            template_device_relation = {item.get('name'): [device.get('name') for device in item.get('scope member', [])]
                                        for item in next(iter(manager_wan_templates_response.data.get('result', [])), {}).get('data', [])}
            # ------- Storing device-template realtion -------
            device_template_relation = {}
            #structure: {'device_id':['template_id']}
            for key, value in template_device_relation.items():
                for device in value:
                    device_template_relation.setdefault(device, []).append(key)
            # -- Storing device-template realtion ENDS HERE --
            return {'templates': templates, 'template_device_relation': template_device_relation, 'device_template_relation': device_template_relation}

    def extract_underlay_sla_template_info(self, manager_wan_template_info):
        """
        summary: extracts all the sla_template_info
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - manager_wan_template_info: response from manager for individual wan template
        returns: final converted response
        return structure: [{'id': number, 'jitter-threshold': number, 'latency-threshold': number, 'link-cost-factor': number, 'packetloss-threshold': number}]
        """
        if manager_wan_template_info.data is not None:
            return [sla_data for item in next(iter(manager_wan_template_info.data.get('result', [])), {}).get('data', []) for sla_data in
           item.get('sla', []) if item.get('name', '') == 'Underlay']
        return []

    def extract_virtual_wan_interfaces(self, manager_virtual_wan_response):
        """
        summary: extracts all the sla_template_info
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - manager_wan_template_info: response from manager for individual wan template
        returns: final converted response
        """
        if manager_virtual_wan_response.data is not None and type(next(iter(manager_virtual_wan_response.data.get('result', [])), {}).get('data', [])) == list:
            return {interface: {'sla_targets_met': interface_data.get('sla_targets_met', [])} for item in
                   next(iter(manager_virtual_wan_response.data.get('result', [])), {}).get('data', []) for sla_data in item.get('response', []) for
                   interface, interface_data in sla_data.get('results', {}).get('Underlay', {}).items() if
                   interface_data.get('status', '') != 'error'}
        return {}

    def convert_to_sla_monitor(self, req_payload, metric_name, final_response_converter):
        """
        summary: creates final response for instant metric: sla-monitor
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - final_response_integrator: response from integrator containing manager response for wan-templates, wan-template-info, virtual-wan and sd-wan-sla-log
        returns: final converted response
        """
        final_response = []
        #Looping through adom data sent (assumes muliple adom data)
        for response_data in final_response_converter:
            #-------- extracting required data --------
            all_device_interfaces = response_data.get('all_device_interfaces', {})
            adom_devices_list = list(response_data.get('templates_device_relationships', {}).get('device_template_relation', {}).keys())
            device_template_relation = response_data.get('templates_device_relationships', {}).get('device_template_relation', {})
            #Looping over adom devices
            for device in adom_devices_list:
                all_device_sla_logs = response_data.get('all_device_sla_logs', {}).get(device).data or []
                if all_device_sla_logs:
                    all_device_sla_logs = all_device_sla_logs.get('data', [])
                template_sla_data = []
                #storing required sla data for template
                for template in device_template_relation.get(device, {}):
                    template_sla_data = response_data.get('all_templates_sla_data', {}).get(template, {})
                #Looping over device interfaces
                for interface, value in all_device_interfaces.get(device, {}).items():
                    # sla log data with condition if interface matches
                    hold_sla_logs = [dict({'timestamp': sla_log.get('timestamp'), **sla_log.get('value', {})}) for log_data in all_device_sla_logs for sla_log in log_data.get('log', []) if log_data.get('interface', '') == interface]
                    #--------- Attaching all required data for response --------
                    device_interface = {}
                    device_interface.update({'device_id': device, 'interface': interface})
                    device_interface.update({'sla': [data for data in template_sla_data if data.get('id', '') in value.get('sla_targets_met', [])]})
                    device_interface.update({'values': hold_sla_logs})
                    # --- Attaching all required data for response ENDS HERE ---
                    final_response.append(device_interface)
        converted_response = self.convert_widget_response(req_payload, metric_name, final_response)
        final_data = marshal(converted_response, self.sla_monitor_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_to_top_threats(self, req_payload, metric_name, analyzer_response):
        """
        summary: creates final response for instant metric: top-threats
        description: This method provides required data from response to the main converter method and returns final
                    converted response
        parameters:
            - req_payload: main request payload
            - metric_name : `str`
            - analyzer_response: response from analyzer
        returns: final converted response
        """
        response = []
        if "sort-by" in req_payload:
            analyzer_response = self.convert_response_to_sorted_format(req_payload, analyzer_response)
        if 'limit' in req_payload and req_payload['limit']:
            response.extend(analyzer_response[0:req_payload['limit']])
        else:
            response.extend(analyzer_response[0:])
        converted_response = self.convert_widget_response(req_payload, metric_name, response)
        final_data = marshal(converted_response, self.top_threats_data)
        return self.remove_none_fields(req_payload,final_data)

    def convert_response_get_system_status(self, response):
        """
        creates final response for system status
        :param response: raw response from API
        :return: converted response
        """
        final_output = {}
        if type(response) == dict:
            return ErrorResponse(response['error-auxiliary'], response['error-message']).get_dict(
                response['error-code'])
        if response:
            if  response.data.get('result') is not None:
                for data in response.data.get('result'):
                    final_output.update({'status':data.get('data').get('status')})
                    final_output.update({'pkg':data.get('data').get('pkg')})
        store_marshal = marshal(final_output, self.syste_status)
        return store_marshal

    def convert_all_sites_devices_ip(self, response):
        """
        Extracts ips of all devices from given sites of user's clients
        :param response: raw response from API
        :return: converted response
        """
        return [interface.get('cpeinterface_ipaddress') for devices in
         response.data for device in devices.get('devices', []) for
         interface in device.get('interfaces', []) if
         interface.get('cpeinterface_ipaddress')]

    def filter_devices_on_client_response(self, response, all_sites_device_ips):
        """
        Filters adom devices based on ip's in client API response for the client
        :param response: raw response from API
        :return: converted response
        """
        hold_devices = [device for device in response.data.get('data', []) if device.get('ip_address', '') in all_sites_device_ips]
        response.data['data'] = hold_devices
        response.data['count'] = len(hold_devices)
        return response

    def add_devids_to_create_report_filter(self, req_payload, client_id, fortinet_api_service_obj):
        """
        If no devid's are passed in filter for create report, then devids are attached
        :param response: raw response from API
        :return: converted response
        """
        # Hold all filter options
        filter_options = req_payload.get('filter', [])
        all_devices = [filters.get('value') for filters in filter_options if
                       filters.get('key', '') == FILTER_BY_DEVICE_ID]
        hold_filter = []
        # ----------- Hold all non-devid filters passed -----------
        for filter in req_payload.get('filter', []):
            if filter.get('key', '') != FILTER_BY_DEVICE_ID:
                hold_filter.append(filter)
        # ------ Hold all non-devid filters passed ENDS HERE ------

        # If filter in payload does not contain devid, attach devids
        if not all_devices:
            # ---------- Fetch all adom devices ----------
            adom_devices = fortinet_api_service_obj.service_get_device_by_id(
                g.analyzer_adom_name, None, client_id)
            all_devices.extend([device.get('serial_number') for device in
                                adom_devices.get('data', []) if
                                device.get('serial_number')])
            # ----- Fetch all adom devices ENDS HERE ----
            if all_devices:
                hold_filter.append(
                    {"key": FILTER_BY_DEVICE_ID, "value": ','.join(all_devices),
                     "operation": DEVID_OPERATOR})
        # -------- Attach to payload ---------
        if hold_filter:
            req_payload['filter'] = hold_filter
        # --- Attach to payload ENDS HERE ---
        return req_payload