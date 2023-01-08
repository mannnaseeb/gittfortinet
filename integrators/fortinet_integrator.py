from flask import g
from fortinet_common import APIService
from db_settings.db_utils import get_all_metrics_from_database, get_all_report_meta_from_database
from decorators.caching import CacheManager
from converters.fortinet_api_converters import FortinetConverters
from middleware.token_interceptor import im_generate_token
from constants import FORTINET_MANAGER_BASE_URL,FORTINET_MANAGER_CREDENTIAL_UUID, \
    FORTINET_ANAYLYZER_BASE_URL,FORTINET_ANAYLYZER_CREDENTIAL_UUID,ADOM_NAME, \
        CLIENT_API_BASE_URL,MANAGER_API_CACHE_TIMEOUT
from .constants import API_VERSION_CALL,API_CALL_MANAGER,API_ADOM_CALL_NAME, \
    API_CALL_FORTIVIEW_NAME,API_CALL_EVENTMGMT_NAME,API_CALL_REPORTS_NAME, \
        TRAFFIC_LOGTYPE,API_CALL_LOGVIEW_NAME,API_CALL_LOGSEARCH_NAME, \
            API_SD_WAN_SLA_LOG_CALL_NAME,API_SD_WAN_INTERFACE_LOG_CALL_NAME, \
                API_CALL_REPORTS


cm = CacheManager()


fortinet_conversion_obj = FortinetConverters()

class FortinetIntegrator:
    """Fortinet Integrator to call backend api"""

    def __init__(self):
        self.api_service = APIService.get_instance()

    def get_adom_by_name(self, adom_name):
        """
        calls fortinet api to get adom details by name
        :param adom_name: name of the adom
        :return: response from the fortinet api
        """
        return self._get_all_adom(adom_name=adom_name)

    def get_all_adom(self):
        """
        calls fortinet api to get details of all adoms
        :return: response from the fortinet api
        """
        return self._get_all_adom()

    # @cm.cached(class_name=lambda *args, **kwargs: args[1] + "devices", key="name", pk="device_id", timeout= int(MANAGER_API_CACHE_TIMEOUT) if MANAGER_API_CACHE_TIMEOUT else None)
    def get_device_by_id(self, adom_name, device_id=None):
        """
         calls fortinet api to get information about a device
         :param adom_name: name of the adom
         :param device_id: id of the device
         :return: response from the fortinet api
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        device_url = f"?device_id={str(device_id)}" if device_id else ""
        return self.api_service.get(
            f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/device' + str(
                device_url), headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_classifiers_and_data(self):
        """
         calls the cached function which gets all required data for classifiers and data
         :param adom_name: name of the adom
         :param device_id: id of the device
         :return: response from the fortinet api
         """
        return get_all_metrics_from_database()

    def get_report_meta(self):
        """
         calls the cached function which gets all required meta data
         :return: response from the fortinet api
         """
        return get_all_report_meta_from_database()

    def get_instant_metrics(self, req_payload, metric_name):
        """calls the analyzer to gets instant metircs data"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{ADOM_NAME}/{metric_name}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_site_details_event_management(self, adom_name, **req_payload):
        """calls the analyzer to gets site details alert data"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_EVENTMGMT_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/alerts'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_reports_list_by_title(self, adom_name, **req_payload):
        """calls the analyzer to gets reports by title"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_REPORTS_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/reports'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def delete_reports_by_tid(self, tid, adom_name):
        """calls the analyzer to delete report by task id"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_REPORTS_NAME}/{g.analyzer_ip}/{API_CALL_REPORTS_NAME}/{API_ADOM_CALL_NAME}/{adom_name}/delete/{tid}'
        return self.api_service.delete(url, json={}, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_top_applications(self, adom_name=None, **req_payload):
        """calls the analyzer to gets top applications data"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if not adom_name:
            adom_name = ADOM_NAME
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-applications'
        analyzer_response = self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})
        #-------- filtering records with appcat having/containing 'Not.Scanned' --------
        if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                analyzer_response.data['result']:
            analyzer_response = fortinet_conversion_obj.filter_not_scanned_records(analyzer_response)
        #--- filtering records with appcat having/containing 'Not.Scanned' ENDS HERE ---
        return analyzer_response

    def get_widget_risk_analysis(self, adom_name=None, **req_payload):
        """calls the analyzer to gets risk analysis data"""
        if not adom_name:
            adom_name = ADOM_NAME
        return self.get_widget_top_applications(adom_name, **req_payload)

    def get_widget_top_sources(self, req_payload, adom_name=None):
        """calls the analyzer to gets top sources data"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if not adom_name:
            adom_name = ADOM_NAME
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-sources'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    @cm.cached(class_name="adoms", key="name", pk="adom_name")
    def _get_all_adom(self, adom_name=None):
        """calls the manager to gets all adom  data"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if adom_name:
            return self.api_service.get(
                f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}',
                headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})
        else:
            return self.api_service.get(
                f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}',
                headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_widget_top_users(self, req_payload, adom_name=None):
        """Fetches data for top users"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-sources'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_top_destination(self, req_payload, adom_name=None):
        """Fetches data for top destination"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-countries'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_logview(self, req_payload, adom_name=None):
        """Fetches data for logview"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if not adom_name:
            adom_name = ADOM_NAME
        if 'logtype' not in req_payload:
            req_payload['logtype'] = TRAFFIC_LOGTYPE
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_LOGVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/{API_CALL_LOGSEARCH_NAME}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_logview_top_sources_by_application(self, adom_name=None, **req_payload):
        """Fetches data for top sources by application"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if not adom_name:
            adom_name = ADOM_NAME
        if 'logtype' not in req_payload:
            req_payload['logtype'] = TRAFFIC_LOGTYPE
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_LOGVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/{API_CALL_LOGSEARCH_NAME}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_site_map_event_management(self, req_payload, adom_name):
        """Fetches data for site map event management"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_EVENTMGMT_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/alerts'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_top_policy_hits(self, req_payload,adom_name=None):
        """Fetches data for top policy hits"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/policy-hits'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_traffic_summarry(self, req_payload, metric_name, adom_name):
        """Fetches data for traffic summary"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/{metric_name}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_widget_top_application_threats(self, req_payload, adom_name=None):
        """Fetches data for Top Threates"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-applications'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_sites_for_user(self, client_id=None):
        """Fetches data for sites of user"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        client_id_param = ''
        if client_id:
            client_id_param = '?clientId='+client_id
        url = f'{CLIENT_API_BASE_URL}{API_VERSION_CALL}sites{client_id_param}'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_clients_of_user(self, req_payload={}):
        """Fetches data for clients of user"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{CLIENT_API_BASE_URL}{API_VERSION_CALL}clients'
        return self.api_service.get(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_device_sla_logs(self, req_payload, device_id):
        """
         calls fortinet api to get information about a device
         :param device_id: device id
         :param req_payload: parameters required to send across
         device_id: id of the device
         :return: response from the manager API
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_SD_WAN_SLA_LOG_CALL_NAME}/{device_id}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_device_interface_logs(self, device_id, interface_filter_value= None, **req_payload):
        """
         calls fortinet api to get interface logs about device(s)
         :param device_id: device id
         :param req_payload: parameters required to send across
         device_id: id of the device
         :return: response from the fortinet api
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if interface_filter_value:
            req_payload['interface'] = interface_filter_value
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_SD_WAN_INTERFACE_LOG_CALL_NAME}/{device_id}'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_sd_wan_usage(self, req_payload, adom_name=None):
        """Fetches data for sd-wan usage """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/sd-wan-usage'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def adom_create_reports(self,req_payload,adom_name=None):
        """Fetches data for adom reports """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_REPORTS}/{g.analyzer_ip}/{API_CALL_REPORTS}/{API_ADOM_CALL_NAME}/{adom_name}/create'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_adom_report_status(self,tid=None,adom_name=None):
        """Fetches data for adom reports status """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_REPORTS}/{g.analyzer_ip}/{API_CALL_REPORTS}/{API_ADOM_CALL_NAME}/{adom_name}/status/{tid}'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def download_adom_reports(self,req_payload,adom_name=None):
        """Fetches data for adom download  reports related data  """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_REPORTS}/{g.analyzer_ip}/{API_CALL_REPORTS}/{API_ADOM_CALL_NAME}/{adom_name}/download'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})

    def get_system_monitor_data(self, adom_name, device_id):
        """
         calls manager api to get system monitor data
         :param adom_name: name of the adom
         :param device_id: id of the device
         :return: response from the fortinet manager
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/system-monitor/{str(device_id)}'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_virtual_wan_healthchk_data(self, adom_name, device_id):
        """
         calls manager api to get virtual wan health check
         :param adom_name: name of the adom
         :param device_id: id of the device
         :return: response from the fortinet manager
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/virtual-wan/{str(device_id)}'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}",
                                                  "Correlationid": g.Correlationid})

    def get_wan_templates_data(self, adom_name):
        """
         calls manager api to get wan template data
         :param adom_name: name of the adom
         :return: response from the fortinet manager
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/wan-templates'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}",
                                                  "Correlationid": g.Correlationid})

    def get_template_info(self, adom_name, template_name):
        """
         calls manager api to get wan template info data for a particular template
         :param adom_name: name of the adom
         :return: response from the fortinet manager
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        url = f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/wan-template-info/{template_name}'
        return self.api_service.get(url, headers={"Authorization": f"Bearer {access_token}",
                                                  "Correlationid": g.Correlationid})

    def get_system_status(self, adom_name, device_id=None):
        """
         calls fortinet api to get information about a device
         :param adom_name: name of the adom
         :param device_id: id of the device
         :return: response from the fortinet api
         """
        token = im_generate_token()
        access_token = token.data.get('access_token')
        return self.api_service.get(
            f'{FORTINET_MANAGER_BASE_URL}{API_VERSION_CALL}{API_CALL_MANAGER}/{g.manager_ip}/{API_ADOM_CALL_NAME}/{adom_name}/package-status/{device_id}', headers={"Authorization": f"Bearer {access_token}", "Correlationid": g.Correlationid})

    def get_widget_top_threats(self, adom_name=None, **req_payload):
        """Fetches data for Top Threats"""
        token = im_generate_token()
        access_token = token.data.get('access_token')
        if not adom_name:
            adom_name = ADOM_NAME
        url = f'{FORTINET_ANAYLYZER_BASE_URL}{API_VERSION_CALL}{API_CALL_FORTIVIEW_NAME}/{g.analyzer_ip}/{API_ADOM_CALL_NAME}/{adom_name}/top-threats'
        return self.api_service.post(url, json=req_payload, headers={"Authorization": f"Bearer {access_token}",
                                                                     "Correlationid": g.Correlationid})
