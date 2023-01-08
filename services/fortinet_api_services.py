import os
import logging
from datetime import datetime
import json
import re
import time
from flask import g
from requests.exceptions import ConnectionError
from utils.fortinet_api_logger import FortinetAPILogger
from converters.fortinet_api_converters import FortinetConverters
from integrators.fortinet_integrator import FortinetIntegrator
from validators.fortinet_api_validations import FortinetAPIValidations
from fortinet_common import  APIException
from constants import SUCCESS_CODE,BAD_TITLE,ERROR_REPORT_METADATA_SAVE_FAILED, \
    ERROR_INVALID_REPORT_STATUS_REQUEST,ERROR_REPORT_IS_DELETED,BAD_FORMAT,WIDGET_SLA_PERFORMANCE, \
        ERROR_INVALID_REPORT_DOWNLOAD_REQUEST,WIDGET_SITE_DETAILS,WIDGET_TOP_APPLICATIONS, \
            ADOM_NAME_ERROR_CODE_IN_ANALYZER,WIDGET_TOP_USERS,WIDGET_TOP_DESTINATIONS, \
                WIDGET_TRAFFIC_SUMMARY,WIDGET_RESOURCE_USAGE,WIDGET_SITE_MAP,WIDGET_RISK_ANALYSIS, \
                    WIDGET_TOP_APPLICATIONS_USAGE,WIDGET_APPLICATION_CATEGORIES,WIDGET_TOP_SOURCES_BY_BANDWIDTH, \
                        WIDGET_TOP_POLICY_HITS,WIDGET_TOP_THREATS,WIDGET_TOP_APPLICATION_THREATS, \
                            WIDGET_SD_WAN_USAGE,WIDGET_BANDWIDTH_SUMMARY,BANDWIDTH_SUMMARY_FILTER_BY_DEVICE_ID, \
                                BANDWIDTH_SUMMARY_FILTER_BY_INTERFACE,ADOM_NAME_ERROR_CODE_IN_MANAGER, \
                                    SLA_MONITOR_FILTER_BY_DEVICE_ID,WIDGET_LINK_QUALITY_STATUS,WIDGET_BANDWIDTH_RATE, \
                                        FILTER_BY_DEVICE_ID,PROVIDE_CLIENT_ID, INVALID_CLIENT_ID, FILTER_BY_SITE_STATUS, \
                                            PERMITTED_STATUS_SITE_DETAILS, FILTER_BY_DEVICE_STATUS



from languages.fortinet_api_languages import ErrorResponse
from languages.fortinet_api_exceptions import logger, HostRespondedWithErrorException
from validators.fortinet_api_validations import ValidationException
from languages.constants import ERROR_MESSAGE_INTERNAL_SERVER_ERROR,ERROR_MESSAGE_HOST_NOT_REACHABLE, \
    ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR,FORTINET_MANAGER_NOT_REACHABLE,ERROR_CODE_API_ERROR, \
        HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR,FILE_DOES_NOT_EXIST,ADOM_LIST_EMPTY,FORTINET_ANALYZER_NOT_REACHABLE, \
            HTTP_STATUS_CODE_BAD_REQUEST,ERROR_CODE_VALIDATION_ERROR,ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR, \
                ERROR_CODE_FOR_INTERNAL_SERVER_ERROR,ERROR_CODE_CLIENT_API_WITH_ERROR,ERROR_CODE_HOST_NOT_REACHABLE,\
                    PROVIDE_PROPER_SITE_STATUS_FILTER, PROVIDE_PROPER_DEVICE_STATUS_FILTER,\
                    ERROR_MESSAGE_CLIENT_API_RESPONDED_WITH_ERROR

from models.reports import Reports
from models.report_status import ReportStatus
from models.report_meta import ReportMeta
from models.report_format import  ReportFormat
from models import db
from models.report_availability import ReportAvailability


class FortinetAPIService:
    """
        summary: Returns final response of an api
        description: This class works in two steps:
            - Call an integrator layer to get required response data for an api
            - Call the converter layer to convert response data returned from integrator layer into desired format
        methods:
            service_get_adom_by_name(adom_name) :
                - Call an integrator layer object to get required response data for provided adom name
                - Convert the response data into desired format by calling converter layer object
                - Returns the response from converter layer
            service_get_all_adom() :
                - Call an integrator layer object to get required response data for all adoms
                - Convert the response data into desired format by calling converter layer object
                - Returns the response from converter layer
            service_get_device_by_id(adom_name, device_id) :
                - Call an integrator layer object to get required response data for provided adom name and device id
                - Convert the response data into desired format by calling converter layer object
                - Returns the response from converter layer
            service_get_classifiers_and_data() :
                - Call an integrator layer object to get required response data for all metrics
                - Data is already pulled in a converted format as per requirement so we have not used conversion layer in this service for now
                - Returns the response from integrator layer
            service_get_instant_metric(req_payload, metric_name) :
                - Convert the request payload by calling the required converter layer object
                - Validate the above request payload for passing it to fortinet analyzer
                - Call an integrator layer object to get required response data for all metrics
                - Convert the response data into desired format by calling converter layer object
                - Returns the response from integrator layer
            service_convert_instant_metric_payload(req_payload) :
                - Used as a helper function for service_get_instant_metric to convert request payload
    """

    def __init__(self):
        self.fortinet_integrator_obj = FortinetIntegrator()
        self.fortinet_conversion_obj = FortinetConverters()
        self.logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))
        self.all_user_sites_response = None

    def service_get_device_id(self,filter_options=None,req_payload=None,device_id_filter_list=None, device_id=None):
        """
        This Method Convert serialnumber to device_id
        """
        device_id_filter_list = []
        if  req_payload :
            if 'filter' in req_payload :
                req_payload['filter'] = filter_options
                adom_devices = self.service_get_device_by_id(adom_name=g.analyzer_adom_name)
                if adom_devices.get("data") :
                    for adom_device_data in  adom_devices.get("data"):
                        for data in req_payload['filter']:
                            if data.get("key") == "devid" and  adom_device_data.get("serial_number") == data.get("value"):
                                for vdom_data in adom_device_data.get("vdom"):
                                    data['value'] = vdom_data.get("device_id")
                                    device_id_filter_list.append(vdom_data.get("device_id"))
                req_payload = self.fortinet_conversion_obj.convert_to_comma_seperated(req_payload)
            return req_payload, device_id_filter_list
        if device_id:
            adom_devices = self.service_get_device_by_id(adom_name=g.analyzer_adom_name)
            if adom_devices.get("data") :
                for adom_device_data in  adom_devices.get("data"):
                        if adom_device_data.get("serial_number") == device_id:
                            for vdom_data in adom_device_data.get("vdom"):
                                device_id = vdom_data.get("device_id")
            return device_id


    def raise_host_responded_with_error(self, response):
        """Used as a common function to check if host responded with error"""
        try:
            if response.status != SUCCESS_CODE and (response.original_response is None or
                                                    response.original_response.json() is None):
                return ERROR_MESSAGE_INTERNAL_SERVER_ERROR + ' or ' + ERROR_MESSAGE_HOST_NOT_REACHABLE
        except:
            return ERROR_MESSAGE_INTERNAL_SERVER_ERROR + ' or ' + ERROR_MESSAGE_HOST_NOT_REACHABLE
        if response.status != SUCCESS_CODE and type(
                response.original_response.json()) == dict and 'error-code' in response.original_response.json():
            return response.original_response.json()['error-message']

    def service_get_adom_by_name(self, adom_name):
        """Calls integrator layer to fetch data for adom by name"""
        try:
            response = self.fortinet_integrator_obj.get_adom_by_name(adom_name)
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                raise Exception(response.original_response.json()['error-message'], ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                raise Exception(error_message, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return self.fortinet_conversion_obj.convert_response_get_adom_by_name(response)
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_MANAGER_NOT_REACHABLE, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_all_adom(self):
        """Calls integrator layer to fetch data for all adoms"""
        try:
            response = self.fortinet_integrator_obj.get_all_adom()
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                raise Exception(response.original_response.json()['error-message'], ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                raise Exception(error_message, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return self.fortinet_conversion_obj.convert_response_get_all_adom(response)
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_MANAGER_NOT_REACHABLE, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_device_by_id(self, adom_name, device_id=None, client_id=None):
        """Calls integrator layer to fetch data for adom devices and device by id"""
        try:
            #------- Validate ClientId ENDS HERE -------
            device_id = self.service_get_device_id(device_id=device_id)
            response = self.fortinet_integrator_obj.get_device_by_id(adom_name, device_id=device_id)
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                raise Exception(response.original_response.json()['error-message'], ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            # # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                raise Exception(error_message, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            #Following condition is used to save a extra integrator call
            if self.all_user_sites_response:
                all_sites_response = self.all_user_sites_response
            else:
                all_sites_response = self.fortinet_integrator_obj.get_sites_for_user(client_id)
            all_sites_device_ips = self.fortinet_conversion_obj.convert_all_sites_devices_ip(all_sites_response)
            response = self.fortinet_conversion_obj.filter_devices_on_client_response(
                response, all_sites_device_ips)
            return self.fortinet_conversion_obj.convert_response_get_device_by_id(response)
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_MANAGER_NOT_REACHABLE, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_report_list_by_title(self, req_payload):
        """Calls integrator layer to fetch data for adom devices and device by id"""
        try:
            req_payload = self.fortinet_conversion_obj.convert_payload_for_list_by_title(req_payload)
            response = self.fortinet_integrator_obj.get_reports_list_by_title(adom_name=g.analyzer_adom_name,**req_payload)
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                raise Exception(response.original_response.json()['error-message'])
            # # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                raise Exception(error_message)
            return self.fortinet_conversion_obj.convert_response_get_report_by_title(response,req_payload['title'])
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE)
            return ErrorResponse('', ex.message).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR


    def service_delete_report_by_tid(self,tid):
        """Calls integrator layer to fetch data for adom devices and device by id"""
        try:
            response = self.fortinet_integrator_obj.delete_reports_by_tid(tid,adom_name=g.analyzer_adom_name)
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                if response.status == HTTP_STATUS_CODE_BAD_REQUEST:
                    raise ValidationException(response.original_response.json()['error-message'])
                else:
                    raise Exception(response.original_response.json()['error-message'])
            # # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                if response.status == HTTP_STATUS_CODE_BAD_REQUEST:
                    raise ValidationException(error_message)
                else:
                    raise Exception(error_message)
            return self.fortinet_conversion_obj.convert_response_delete_report_by_tid(response,tid)
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def adom_create_reports(self,req_payload):
        """Calls integrator layer to create a new report"""

        try:
            # client_id = ""
            # client_status = False
            # if "filter" in req_payload :
            #     filter_data = req_payload.get("filter")
            #     for data in filter_data:
            #         if data.get("key") == "client-id":
            #             client_status =True
            #             client_id =  data.get("value")
            #     if  client_status == False:
            #         raise ValidationException(PROVIDE_CLIENT_ID)
            report_metadata = ReportMeta.query.filter_by(ReportMetaTitleCode=req_payload['title']).first()
            if not report_metadata:
                raise ValidationException(BAD_TITLE)
            req_payload = self.fortinet_conversion_obj.convert_payload_for_adom_reports(req_payload, report_metadata)
            response = self.fortinet_integrator_obj.adom_create_reports(req_payload,adom_name=g.analyzer_adom_name)
            if response.status != SUCCESS_CODE:
                error_msg = response.original_response.json()['error-message'] if response.original_response != None and isinstance(response.original_response.json(), dict) and 'error-code' in response.original_response.json() else  "An error occured while creating report"
                raise Exception(error_msg, ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)

            start_time = end_time = executed_at = status_id = None
            try:
                start_time = datetime.strptime(response.data['result'].get('period-start'), '%Y/%m/%d %H:%M')
                end_time = datetime.strptime(response.data['result'].get('period-end'), '%Y/%m/%d %H:%M')
                executed_at = datetime.strptime(response.data['result'].get('start'), '%Y/%m/%d %H:%M:%S')
                report_file_name = response.data['result'].get('name')
                progress_percent = response.data['result'].get('progress-percent')
                devices = response.data['result'].get('device')
                devices_data = None
                if 'data' in devices:
                    devices_data = devices['data']
                status_id = ReportStatus.GENERATED.value if (response.data.get('result') and response.data['result'].get("progress-percent", None) == 100) else ReportStatus.RUNNING.value
                adom_reports_data:Reports = Reports(ReportTitle=response.data['result']['title'],
                                            ReportTid=response.data['result']['tid'],
                                            ReportFileName=report_file_name,
                                            CreatedBy=g.get('userId', 1), ModifiedBy=g.get('userId', 1),
                                            StatusID=status_id,
                                            DeviceID=req_payload.get('device', ""),
                                            StartTime=start_time,
                                            EndTime=end_time,
                                            ExecutedAt=executed_at,
                                            ProgressReport=progress_percent,
                                            DevicesData=devices_data,
                                            # ClientID =client_id
                                            )
                db.session.add(adom_reports_data)
                db.session.commit()
            except Exception as ex:
                logger.exception(f"An error occured while saving report meta data reason: {str(ex)}")
                raise Exception(ERROR_REPORT_METADATA_SAVE_FAILED, ERROR_CODE_FOR_INTERNAL_SERVER_ERROR)

            # -------------------------- Converted response --------------------------
            converted_response = self.fortinet_conversion_obj.convert_response_adom_reports(response=response)
            return converted_response

        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def get_adom_reports_status(self,tid):
        """Calls integrator layer to fetch data for adom reports status related data"""

        try:
            report = Reports.query.filter_by(ReportTid=tid).first()
            if not report:
                return ErrorResponse('', ERROR_INVALID_REPORT_STATUS_REQUEST, HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
                ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            if report.is_deleted==ReportAvailability.DELETED.value:
                return ErrorResponse('', ERROR_REPORT_IS_DELETED, HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
                ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            response = self.fortinet_integrator_obj.get_adom_report_status(tid,adom_name=g.analyzer_adom_name)
            if response.status != SUCCESS_CODE:
                error_msg = response.original_response.json()['error-message'] if response.original_response != None and isinstance(response.original_response.json(), dict) and 'error-code' in response.original_response.json() else  "An error occured while getting report status"
                raise Exception(error_msg)

            # update  status in DB
            report.ModifiedBy = g.get('userId', 1)
            if response.data.get('result') and response.data['result'].get("progress-percent", None) == 100:
                report.StatusID=ReportStatus.GENERATED.value
            else:
                report.StatusID = ReportStatus.RUNNING.value
            try:
                db.session.commit()
            except Exception as ex:
                logger.exception(f"An error occured while saving report meta data reason: {str(ex)}")
                raise Exception(ERROR_REPORT_METADATA_SAVE_FAILED)
            # -------------------------- Converted response --------------------------
            converted_response = self.fortinet_conversion_obj.convert_response_adom_reports(response=response)
            return converted_response

        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def download_adom_reports(self,tid,req_payload):
        """Calls integrator layer to fetch data for download adom reports related data"""

        try:
            report_format = ReportFormat.query.filter_by(ReportFormatCode=req_payload['format']).first()
            if not report_format:
                raise ValidationException(BAD_FORMAT)
            report: Reports  = Reports.query.filter_by(ReportTid=tid).first()
            if not report:
                return ErrorResponse('', ERROR_INVALID_REPORT_DOWNLOAD_REQUEST, HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
                ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            if report.is_deleted==ReportAvailability.DELETED.value:
                return ErrorResponse('', ERROR_REPORT_IS_DELETED, HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
                ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            analyser_req_payload = {
                "tid": tid,
                "format": req_payload.get("format")
            }
            response = self.fortinet_integrator_obj.download_adom_reports(analyser_req_payload,adom_name=g.analyzer_adom_name)
            if response.status != SUCCESS_CODE:
                error_msg = response.original_response.json()['error-message'] if response.original_response != None and isinstance(response.original_response.json(), dict) and 'error-code' in response.original_response.json() else  "An error occured while downloading report"
                raise Exception(error_msg, ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)

            report.ReportFormat=req_payload.get("format")
            report.ModifiedBy = g.get('userId', 1)
            try:
                db.session.commit()
            except Exception as ex:
                logger.exception(f"An error occured while saving report meta data reason: {str(ex)}")
                raise Exception(ERROR_REPORT_METADATA_SAVE_FAILED)
            # -------------------------- Converted response --------------------------
            converted_response = self.fortinet_conversion_obj.convert_response_adom_download_reports(response=response)
            return converted_response
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_classifiers_and_data(self):
        """Calls integrator layer to fetch data for metric related data"""
        try:
            return self.fortinet_integrator_obj.get_classifiers_and_data()
        except APIException as ex:
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def get_site_devices_data(self, site_devices, all_adom_devices, all_adom_devices_with_alerts):
        # if a device is present in a site but not in all adom devices it wil be skipped
        site_devices_data = {next(iter(device.get('interfaces', [])), {}).get("cpeinterface_ipaddress"):all_adom_devices[next(iter(device.get('interfaces', [])), {}).get("cpeinterface_ipaddress")] for device in site_devices if next(iter(device.get('interfaces', [])), {}).get("cpeinterface_ipaddress") in all_adom_devices}
        site_devices_with_alert = {site_device_data.get("serial_number"):all_adom_devices_with_alerts.get(site_device_data.get("serial_number")) for _ , site_device_data,  in site_devices_data.items() if site_device_data.get("serial_number") in all_adom_devices_with_alerts}
        return site_devices_data, site_devices_with_alert

    def get_all_sites_devices_data(self, adom, req_payload):
        all_adom_devices = {}
        all_adom_devices_with_alerts = {}
        manager_response = self.fortinet_integrator_obj.get_device_by_id(adom)
        if manager_response.status != SUCCESS_CODE and 'error-code' in (error_message := manager_response.original_response.json()):
            raise Exception(self.raise_host_responded_with_error(manager_response), ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)

        if manager_response.data and 'data' in manager_response.data:
            for data in manager_response.data.get('data'):
                data['adom_name'] = adom
            adom_devices = {device.get("ip_address"): device for device in manager_response.data.get('data')}
            all_adom_devices.update(adom_devices)

        analyzer_response = self.fortinet_integrator_obj.get_widget_site_details_event_management(adom, **req_payload)
        if analyzer_response.status != SUCCESS_CODE and 'error-code' in (error_message := analyzer_response.original_response.json()):
            raise Exception(self.raise_host_responded_with_error(analyzer_response),
                            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)

        if analyzer_response.data and 'result' in analyzer_response.data and 'data' in analyzer_response.data['result']:
            for data in  analyzer_response.data['result']['data']:
                data['adom_name'] = adom
            adom_devices_with_alerts = {device['devid']: device for device in analyzer_response.data['result']['data'] }
            all_adom_devices_with_alerts.update(adom_devices_with_alerts)
        return all_adom_devices, all_adom_devices_with_alerts

    def service_get_instant_metric(self, req_payload, metric_name):
        """Calls integrator layer to fetch data for regarding instant metric"""
        try:
            filter_options = req_payload.get('filter', [])
            start_date = req_payload.get('start_date', '')
            end_date = req_payload.get('end_date', '')
            if metric_name == WIDGET_SITE_DETAILS:
                # ------------- Check for device filter -------------
                filter_by_devid = [filters.get('value') for filters in filter_options if filters.get('key', '') == FILTER_BY_DEVICE_ID]
                # -------- Check for device filter ENDS HERE --------
                # -------------- remove devid filter ----------
                req_payload['filter'] = [filter for filter in filter_options if filter.get('key', '') != FILTER_BY_DEVICE_ID]
                filter_options = req_payload['filter']
                if not req_payload['filter']:
                    del req_payload['filter']
                # -------------- remove devid filter ---------
            req_payload = self.fortinet_conversion_obj.convert_payload_for_instant_metric(req_payload)
            # ------------- validating payload for fortinet analyzer ----------------
            validation_object = FortinetAPIValidations()
            # validation_object.check_invalid_payload(req_payload, metric_name)
            # --------- For site-details ---------
            if metric_name == WIDGET_SITE_DETAILS:
                #--- limit not required for site-details ---
                if 'limit' in req_payload:
                    del req_payload['limit']
                #-- sort-by not required for site-details --
                if 'sort-by' in req_payload:
                    del req_payload['sort-by']
                # ------ Get all adoms list from file -------
                # ------------- Check for site status filter -------------
                filter_by_site_status = []
                filter_by_device_status = []
                if filter_options:
                    filter_by_site_status = [filters.get('value') for filters in filter_options if
                                        filters.get('key', '') == FILTER_BY_SITE_STATUS]
                    if filter_by_site_status and not all(item in PERMITTED_STATUS_SITE_DETAILS for item in filter_by_site_status):
                        raise Exception(PROVIDE_PROPER_SITE_STATUS_FILTER, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                # -------- Check for site status filter ENDS HERE
                # ------------- Check for device status filter -------------
                    filter_by_device_status = [filters.get('value') for filters in filter_options if
                                        filters.get('key', '') == FILTER_BY_DEVICE_STATUS]
                    if filter_by_device_status and not all(item in PERMITTED_STATUS_SITE_DETAILS for item in filter_by_device_status):
                        raise Exception(PROVIDE_PROPER_DEVICE_STATUS_FILTER, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                # -------- Check for site device  status filter ENDS HERE --------
                #------------- Attaching proper filters again -------------

                if 'filter' in req_payload:
                    filters_passed = req_payload['filter'].split(',')
                    hold_filter = []
                    for index, filter in enumerate(filters_passed):
                        if FILTER_BY_SITE_STATUS not in filter and FILTER_BY_DEVICE_STATUS not in filter:
                            hold_filter.append(filter)
                    if hold_filter:
                        req_payload['filter'] = ','.join(hold_filter)
                    else:
                        req_payload.pop('filter', None)

                # -------- Attaching proper filters again ENDS HERE --------
                all_adom_devices, all_adom_devices_with_alerts = self.get_all_sites_devices_data(g.analyzer_adom_name, req_payload)
                all_sites_response = self.fortinet_integrator_obj.get_sites_for_user()
                if all_sites_response.status != SUCCESS_CODE and 'error-code' in (error_message := all_sites_response.original_response.json()):
                        raise Exception(self.raise_host_responded_with_error(all_sites_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR)
                sites_up_count = sites_down_count = sites_alert_count = 0
                if all_sites_response.data and all_adom_devices:
                    all_sites = all_sites_response.data
                    #When device_status is sent in filter:
                    #sent up: Count increases only when atleast one device is found up
                    #sent down: Count increases only when atleast one device is found down
                    #sent alert: Count increases only when atleast one device is found as alert
                    for site in all_sites:
                        site_devices = site.get('devices') or []
                        site_devices_data, site_devices_with_alert = self.get_site_devices_data(site_devices, all_adom_devices, all_adom_devices_with_alerts)
                        on_alert = False
                        site_down = False
                        site_up = False
                        add_to_site = False
                        device_in_site = False
                        for k,site_device_data in site_devices_data.items():
                            #---- Condition to check when device ids sent in filter and if device id exists in site ----
                            if filter_by_devid and site_device_data.get('serial_number', None) and site_device_data.get('serial_number', '') in filter_by_devid:
                                device_in_site = True
                            # ------ If devid passed in filter ------
                            connection_status = int(site_device_data.get('connection_status')) if site_device_data.get('connection_status', None) else None
                            if connection_status is None or connection_status == 0:
                                self.logger.warn(f"device with ip: {k} serial_number: {site_device_data.get('serial_number')} connection status not found")
                                continue
                            elif connection_status == 1 and all_adom_devices.get(k).get('serial_number') in site_devices_with_alert:
                                if 'alert' in filter_by_device_status or not filter_options:
                                    add_to_site = True
                                on_alert = True
                            elif connection_status == 1:
                                if 'up' in filter_by_device_status or not filter_options:
                                    add_to_site = True
                                site_up = True
                            elif connection_status != 1:
                                if 'down' in filter_by_device_status or not filter_options:
                                    add_to_site = True
                                site_down = True
                        #If devid is passed in filter and device not found in site, the site is not considered in count
                        if filter_by_devid and not device_in_site:
                            add_to_site = False
                        # if add_to_site or (not filter_by_site_status and not filter_by_device_status):
                        # if at least one device is down site is considered down
                        # if all devices is up and no device has alert site is considered as up
                        if (not filter_options and add_to_site) or (filter_by_devid and not filter_options and device_in_site) or (filter_by_device_status and add_to_site) or (filter_by_site_status and not filter_by_device_status) or (filter_by_site_status and filter_by_device_status and add_to_site):
                            if site_down:
                                sites_down_count = sites_down_count + 1
                            elif on_alert:
                                sites_alert_count = sites_alert_count + 1
                            elif site_up:
                                sites_up_count = sites_up_count + 1

                converted_response = self.fortinet_conversion_obj.convert_to_site_details(req_payload,WIDGET_SITE_DETAILS, sites_up_count, sites_down_count, sites_alert_count, filter_by_site_status)
                return converted_response
            # --------- For top-applications ---------
            if metric_name == WIDGET_TOP_APPLICATIONS:
                # ------------ Analyzer API call to fetch top-applications -----------
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_applications(req_payload)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message[
                    'error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------- Handle HostRespondedWithErrorException --------------
                if error_message := self.raise_host_responded_with_error(analyzer_response):
                    raise Exception(error_message, ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------------------ Converted response -----------------------
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_top_applications(req_payload,
                                                                                              WIDGET_TOP_APPLICATIONS,
                                                                                              analyzer_response)
                return converted_response
            # --------- For top-users ---------
            if metric_name == WIDGET_TOP_USERS:
                adom_lists,data = list(), list()
                # ------------ Analyzer API call to fetch top-users -----------
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_users(req_payload, adom_name =g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------------------ Converted response -----------------------
                if analyzer_response.data is not None and 'result' in analyzer_response.data and \
                    'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                            for analyzer_data in analyzer_response.data['result']['data']:
                                analyzer_data['adom']= g.analyzer_adom_name
                                data.append(analyzer_data)
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_top_users(req_payload, WIDGET_TOP_USERS,
                                                                                       analyzer_response =data)
                return converted_response
            if metric_name == WIDGET_TOP_DESTINATIONS:
            #------------ Widget top Destination Api------------#
                adom_lists,data = list(), list()
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_destination(req_payload,adom_name=g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------- Handle HostRespondedWithErrorException --------------
                if analyzer_response.data is not None and 'result' in analyzer_response.data and \
                    'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in analyzer_response.data['result']['data']]
                    data.extend(analyzer_response.data['result']['data'])
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_top_destination(req_payload,
                                                                                             WIDGET_TOP_DESTINATIONS,
                                                                                             analyzer_response=data)
                return converted_response
            # --------- For traffic-summary ---------
            if metric_name == WIDGET_TRAFFIC_SUMMARY:
                # ------------ Manager APi call to fetch all adom devices ----------
                final_response_for_converter = []
                time.sleep(1)
                # --------- Manager APi call to fetch all device  ---------
                manager_response = self.fortinet_integrator_obj.get_device_by_id(g.analyzer_adom_name)
                if manager_response.status != SUCCESS_CODE and 'error-code' in (error_message := manager_response.original_response.json()):
                    raise Exception(self.raise_host_responded_with_error(manager_response), ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
                devid_regex = r"devid=([^,]*)"
                device_serial_numbers_map = {}
                hostname_filter_list = []
                match = re.match(devid_regex, req_payload.get("filter", ""))
                analyzer_filter_value = req_payload.get("filter") or ""
                def repl_fn(match_obj):
                    device_hostname = match_obj.group(1)
                    hostname_filter_list.append(device_hostname)
                    return f"devid={device_serial_numbers_map.get(match_obj.group(1), '')}"
                if match:
                    for device in manager_response.data['data']:
                        device_serial_numbers_map[device.get('hostname', "")] = device.get('serial_number',None)
                    analyzer_filter_value = re.sub(devid_regex, repl_fn, req_payload.get("filter"))
                # analyzer_req_payload = req_payload.copy()
                # if analyzer_filter_value:
                #     analyzer_req_payload["filter"] = analyzer_filter_value
                analyzer_req_payload,device_id_filter_list = self.service_get_device_id(filter_options,req_payload,hostname_filter_list)
                # --------- Analyzer APi call to fetch fortiview resource-usage ---------
                analyzer_response = self.fortinet_integrator_obj.get_widget_traffic_summarry(analyzer_req_payload,
                                                                                                WIDGET_RESOURCE_USAGE,
                                                                                                g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------------------ Converted response -----------------------
                final_response_for_converter.append({'adom_name':  g.analyzer_adom_name,
                                                        'analyzer_response': analyzer_response,
                                                        'manager_response': manager_response, 'hostname_filter_list': device_id_filter_list})
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_traffic_summary(analyzer_req_payload,
                                                                                             WIDGET_TRAFFIC_SUMMARY,
                                                                                             final_response_for_converter)
                return converted_response
            # --------- For site-map ---------
            if metric_name == WIDGET_SITE_MAP:
                final_response_for_converter = []
                all_adom_devices, all_adom_devices_with_alerts = self.get_all_sites_devices_data(g.analyzer_adom_name, req_payload)
                all_sites_response = self.fortinet_integrator_obj.get_sites_for_user()
                if all_sites_response.status != SUCCESS_CODE and 'error-code' in (error_message := all_sites_response.original_response.json()):
                    raise Exception(self.raise_host_responded_with_error(all_sites_response), ERROR_CODE_CLIENT_API_WITH_ERROR)
                if all_sites_response.data and all_adom_devices:
                    all_sites_consolidated_data = []
                    all_sites = all_sites_response.data
                    for site in all_sites:
                        site_consolidated_data = {}
                        site_consolidated_data['site_id'] = site.get('id')
                        site_consolidated_data['address'] = {
                            "address1": site.get('address1'),
                            "address2":  site.get('address1'),
                            "city":  site.get('city'),
                            "state":  site.get('state'),
                            "postalcode":  site.get('postalcode'),
                            "country": site.get('country')
                        }
                        site_consolidated_data['latitude'] = site.get('lat')
                        site_consolidated_data['longitude'] = site.get('lon')
                        site_consolidated_data['devices'] = []
                        site_consolidated_data['adom_name'] = ''

                        site_devices = site.get('devices') or []
                        site_devices_data, site_devices_with_alert = self.get_site_devices_data(site_devices, all_adom_devices, all_adom_devices_with_alerts)
                        site_has_alert = False
                        site_down = False
                        device_status =""
                        for k,site_device_data in site_devices_data.items():
                            if not site_device_data.get("connection_status") == '1':
                                device_status="down"
                            else:
                                if len(site_devices_with_alert) > 0:
                                    if site_device_data.get('serial_number') in list(site_devices_with_alert.keys()):
                                        device_status ="alert"
                                    else:
                                        if site_device_data.get("connection_status") == '1':
                                            device_status = "up"
                                        else:
                                            device_status = "down"
                                elif site_device_data.get("connection_status") == '1':
                                    device_status = "up"
                                else:
                                    device_status = "down"
                            site_consolidated_data['devices'].append(
                                {
                                    "serial_number": site_device_data.get('serial_number'),
                                    "devid": site_device_data.get('vdom')[0].get('device_id', "") if site_device_data.get('vdom') else "",
                                    "status" : device_status,
                                    })
                            site_consolidated_data['adom_name'] = site_device_data.get('adom_name')
                            connection_status = int(site_device_data.get('connection_status')) if site_device_data.get('connection_status', None) else None
                            if connection_status is None:
                                self.logger.warn(f"device with ip: {k} serial_number: {site_device_data.get('serial_number')} connection status not found")
                                continue
                            elif connection_status == 1 and all_adom_devices.get(k).get('serial_number') in site_devices_with_alert:
                                site_has_alert = True
                            elif connection_status == 1:
                                continue
                            elif connection_status != 1:
                                site_down = True


                        if site_down:
                            site_consolidated_data['status'] = 'down'
                        elif site_has_alert:
                            site_consolidated_data['status'] = 'alert'
                        else:
                            site_consolidated_data['status'] = 'up'

                        all_sites_consolidated_data.append(site_consolidated_data)
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_site_map(req_payload,
                                                                                      WIDGET_SITE_MAP,
                                                                                      all_sites_consolidated_data)

                return converted_response

            # --------- For widget risk analysis ---------
            if metric_name == WIDGET_RISK_ANALYSIS:
                # ------ Get all adoms list from file -------
                risk_analysis_response = []
                # ------------ Analyzer API call to fetch top-threats -----------
                analyzer_response = self.fortinet_integrator_obj.get_widget_risk_analysis(g.analyzer_adom_name, **req_payload)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ----------------------- Append results ------------------------
                if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                        analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in analyzer_response.data['result']['data']]
                    risk_analysis_response.extend(analyzer_response.data['result']['data'])
                # ------------------------ Converted response -----------------------
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_risk_analysis(req_payload,
                                                                                       WIDGET_RISK_ANALYSIS,
                                                                                       risk_analysis_response)
                return converted_response

            # --------- end  widget risk analysis ---------
            # --------- For top-applications-usage ---------
            if metric_name == WIDGET_TOP_APPLICATIONS_USAGE:
                # ------ Get all adoms list from file -------
                top_application_usage_response = []
                # ------------ Analyzer API call to fetch top-applications -----------
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_applications(g.analyzer_adom_name, **req_payload)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    # ----------------------- Append results ------------------------
                    if 'result' in analyzer_response.data and 'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                        analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in analyzer_response.data['result']['data']]
                        top_application_usage_response.extend(analyzer_response.data['result']['data'])
                # ------------------------ Converted response -----------------------
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_top_applications_usage(req_payload,
                                                                                                    WIDGET_TOP_APPLICATIONS_USAGE,
                                                                                                    top_application_usage_response)
                return converted_response
            # --------- For application-categories ---------
            if metric_name == WIDGET_APPLICATION_CATEGORIES:
                final_response_for_converter = []
                # ------------ Analyzer API call to fetch top-applications -----------
                     #------- extend limit to------# 
                if "limit" in req_payload and req_payload.get("limit"):
                    limit_extended_req_payload = req_payload.copy()
                    limit_extended_req_payload['limit'] = req_payload['limit']  *5
                else:
                    limit_extended_req_payload = req_payload.copy()
                     #------- End extend limit to------#
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_applications(g.analyzer_adom_name, **limit_extended_req_payload)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------------------ Converted response -----------------------
                final_response_for_converter.append({'adom_name': g.analyzer_adom_name,
                                                    'analyzer_response': analyzer_response})
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_applications_categories(req_payload,
                                                                                                     WIDGET_APPLICATION_CATEGORIES,
                                                                                                     final_response_for_converter)
                return converted_response
            # --------- For top-sources-by-bandwidth ---------
            if metric_name == WIDGET_TOP_SOURCES_BY_BANDWIDTH:
                final_response_for_converter = []
                # ------------ Analyzer API call to fetch top-sources -----------
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_sources(req_payload, g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ------------------------ Converted response -----------------------
                final_response_for_converter.append({'adom_name': g.analyzer_adom_name,
                                                        'analyzer_response': analyzer_response})
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_sources_by_bandwidth(req_payload,
                                                                                                  WIDGET_TOP_SOURCES_BY_BANDWIDTH,
                                                                                                  final_response_for_converter)
                return converted_response
            #-----------------Top policy hits----------------#
            if metric_name == WIDGET_TOP_POLICY_HITS:
                adom_lists,data =  list(), list()
                # --------- Analyzer APi call to fetch top-policy-hits
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_policy_hits(req_payload,adom_name=g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message[
                    'error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                if analyzer_response.data is not None and 'result' in analyzer_response.data \
                    and 'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in
                                                                analyzer_response.data['result']['data']]
                    data.extend(analyzer_response.data['result']['data'])
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_top_policy_hits(req_payload,
                                                                                             WIDGET_TOP_POLICY_HITS,
                                                                                             analyzer_response=data)
                return converted_response
            #--------------------Widget Api Top-threats------------------------#
            if metric_name == WIDGET_TOP_THREATS:
                adom_lists, data =  list(), list()
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_threats(g.analyzer_adom_name, **req_payload)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ----------------------- Append results ------------------------
                if analyzer_response.data is not None:
                    data.extend(analyzer_response.data.get('result', {}).get('data', []))
                req_payload['filter'] = filter_options
                # -------------------------- Converted response --------------------------
                return self.fortinet_conversion_obj.convert_to_top_threats(req_payload, metric_name, data)
            #--------------------Widget Api Top-Application-threats------------------------#
            if metric_name == WIDGET_TOP_APPLICATION_THREATS:
                adom_lists,data =  list(), list()
                analyzer_response = self.fortinet_integrator_obj.get_widget_top_application_threats(req_payload,g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ----------------------- Append results ------------------------
                if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                        analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in
                                                            analyzer_response.data['result']['data']]
                    data.extend(analyzer_response.data['result']['data'])
                req_payload['filter'] = filter_options
                # -------------------------- Converted response --------------------------
                return self.fortinet_conversion_obj.convert_to_application_threats(req_payload, metric_name, data)
            #--------------------Widget Api Sd-wan-usage------------------------#
            if metric_name == WIDGET_SD_WAN_USAGE:
                adom_lists =  list()
                final_response_for_converter = []
                analyzer_response = self.fortinet_integrator_obj.get_sd_wan_usage(req_payload,g.analyzer_adom_name)
                # ------------- Handle HostRespondedWithErrorException --------------
                if 'error-code' in (error_message := analyzer_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(analyzer_response), ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
                # ----------------------- Append results ------------------------
                if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                        analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                    analyzer_response.data['result']['data'] = [dict(item, adom=g.analyzer_adom_name) for item in
                                                            analyzer_response.data['result']['data']]
                    final_response_for_converter.extend(analyzer_response.data['result']['data'])
                req_payload['filter'] = filter_options
                # -------------------------- Converted response --------------------------
                converted_response = self.fortinet_conversion_obj.convert_to_sd_wan_usage(req_payload,
                                                                                             WIDGET_SD_WAN_USAGE,
                                                                                             analyzer_response=final_response_for_converter)
                return converted_response
            #--------------------Widget Api Bandwidth Summary------------------------#
            if metric_name == WIDGET_BANDWIDTH_SUMMARY:
                req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries(req_payload, start_date, end_date)
                req_payload, device_id_filter_list = self.service_get_device_id(filter_options,req_payload)
                final_response = []
                device_filter_value = [filters.get('value') for filters in filter_options if
                                          filters.get('key', '') == BANDWIDTH_SUMMARY_FILTER_BY_DEVICE_ID]
                interface_filter_value = [filters.get('value') for filters in filter_options if
                                       filters.get('key', '') == BANDWIDTH_SUMMARY_FILTER_BY_INTERFACE]
                if interface_filter_value:
                    interface_filter_value = interface_filter_value[0]
                adom_device_ids = []
                # ------------ Manager APi call to fetch device -----------
                if not device_filter_value:
                    manager_response = self.fortinet_integrator_obj.get_device_by_id(g.analyzer_adom_name)
                    # ------------- Handle HostRespondedWithErrorException --------------
                    if manager_response.status != SUCCESS_CODE and 'error-code' in (
                    error_message := manager_response.original_response.json()) and error_message[
                        'error-code'] != ADOM_NAME_ERROR_CODE_IN_MANAGER:
                        raise Exception(self.raise_host_responded_with_error(manager_response),
                                        ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
                    adom_device_ids = self.fortinet_conversion_obj.extract_adom_devices(manager_response)
                else:
                    adom_device_ids.append(next(iter(device_filter_value)))
                for device_id in adom_device_ids:
                    # ------------ Manager APi call to fetch device sla logs-----------
                    manager_virtual_wan_healthchk_response = self.fortinet_integrator_obj.get_virtual_wan_healthchk_data(g.analyzer_adom_name, device_id)
                    time.sleep(1)
                    # device_interfaces Structure : {'interface_name': {'sla_targets_met': ['ids']} }
                    device_interfaces = self.fortinet_conversion_obj.extract_virtual_wan_interfaces(manager_virtual_wan_healthchk_response)
                    manager_sys_monitor_response = self.fortinet_integrator_obj.get_system_monitor_data(g.analyzer_adom_name,
                                                                                                device_id)
                    time.sleep(1)
                    all_manager_intfc_response = {}
                    for port in list(device_interfaces.keys()):
                        manager_intfc_response = self.fortinet_integrator_obj.get_device_interface_logs(device_id, port, **req_payload)
                        all_manager_intfc_response.update({port:manager_intfc_response})
                        time.sleep(1)
                    final_response.append(
                        {'manager_intfc_response': all_manager_intfc_response,
                            'manager_sys_monitor_response': manager_sys_monitor_response,
                            'device_id': device_id,
                            'manager_virtual_wan_healthchk_response': manager_virtual_wan_healthchk_response})
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_bandwidth_summary(req_payload,
                                                                                          WIDGET_BANDWIDTH_SUMMARY,
                                                                                          final_response)
                return converted_response
            #--------------------Widget Api Sla Monitor------------------------#
            if metric_name == WIDGET_SLA_PERFORMANCE:
                req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries(req_payload, start_date, end_date)
                req_payload, device_id_filter_list = self.service_get_device_id(filter_options,req_payload)
                final_response = []
                #--------- variable initialization --------
                all_templates_sla_data = {}
                all_device_interfaces = {}
                all_device_sla_logs = {}
                # --- variable initialization ENDS HERE ---
                req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries(req_payload, start_date,
                                                                                          end_date)

                device_id_filter = []
                if filter_options:
                    device_id_filter = [filter_option.get('value', '') for filter_option in filter_options if filter_option.get('key', '') == SLA_MONITOR_FILTER_BY_DEVICE_ID and filter_option.get('value', '')]
                #Fetching all templates under adom
                manager_wan_template_response = self.fortinet_integrator_obj.get_wan_templates_data(g.analyzer_adom_name)
                #Extrating all relationship of templates with device
                templates_device_relationships = self.fortinet_conversion_obj.extract_templates_device_relationship(manager_wan_template_response)
                #Fetching individual template information
                for template in templates_device_relationships['templates']:
                    if template not in all_templates_sla_data:
                        manager_wan_template_info = self.fortinet_integrator_obj.get_template_info(g.analyzer_adom_name, template)
                        all_templates_sla_data.update({template: self.fortinet_conversion_obj.extract_underlay_sla_template_info(
                            manager_wan_template_info)})
                #Filter if device_id is passed
                if device_id_filter:
                    templates_device_relationships['device_template_relation'] = {device_id: templates_device_relationships['device_template_relation'].get(device_id, []) for device_id in device_id_filter}
                #Fetching virtual wan healtcheck data
                for device in templates_device_relationships['device_template_relation']:
                    manager_virtual_wan_response = self.fortinet_integrator_obj.get_virtual_wan_healthchk_data(
                        g.analyzer_adom_name, device)
                    # device_interfaces Structure : {'interface_name': {'sla_targets_met': ['ids']} }
                    device_interfaces = self.fortinet_conversion_obj.extract_virtual_wan_interfaces(manager_virtual_wan_response)
                    all_device_interfaces.update({device: device_interfaces})
                    # Fetching sla logs
                    manager_sla_logs_response = self.fortinet_integrator_obj.get_device_sla_logs(req_payload, device)
                    all_device_sla_logs.update({device: manager_sla_logs_response})
                final_response.append(
                    {'templates_device_relationships': templates_device_relationships,
                        'all_templates_sla_data': all_templates_sla_data,
                        'all_device_interfaces': all_device_interfaces,
                        'all_device_sla_logs': all_device_sla_logs
                        })
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_sla_monitor(req_payload,
                                                                                         WIDGET_SLA_PERFORMANCE,
                                                                                         final_response)
                return converted_response
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_ANALYZER_NOT_REACHABLE, ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR


    def service_get_timeseries_metric(self, req_payload, metric_name):
        """Calls integrator layer to fetch data regarding timeseries metric"""
        try:
            filter_options = req_payload.get('filter', [])
            start_date = req_payload.get('start_date', '')
            end_date = req_payload.get('end_date', '')
            req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries_metric(req_payload)
            # ------------- validating payload for fortinet analyzer ----------------
            validation_object = FortinetAPIValidations()
            validation_object.check_invalid_payload(req_payload, metric_name)
            # --------- For link-quality-status ---------
            if metric_name == WIDGET_LINK_QUALITY_STATUS:
                # ------ Get all adoms list from file -------
                req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries(req_payload, start_date, end_date)
                req_payload, device_id_filter_list = self.service_get_device_id(filter_options,req_payload)
                final_response = []
                adom_device_ids = [filters.get('value') for filters in filter_options if filters.get('key', '') == FILTER_BY_DEVICE_ID]
                # ------------ Manager APi call to fetch device -----------
                if not adom_device_ids:
                    manager_response = self.fortinet_integrator_obj.get_device_by_id(g.analyzer_adom_name)
                    # ------------- Handle HostRespondedWithErrorException --------------
                    if manager_response.status != SUCCESS_CODE and 'error-code' in (error_message := manager_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_MANAGER:
                        raise Exception(self.raise_host_responded_with_error(manager_response), ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
                    adom_device_ids = self.fortinet_conversion_obj.extract_adom_devices(manager_response)
                for device_id in adom_device_ids:
                    # ------------ Manager APi call to fetch device sla logs-----------
                    manager_response = self.fortinet_integrator_obj.get_device_sla_logs(req_payload, device_id)
                    final_response.append({'manager_response': manager_response, 'device_id': device_id, 'adom_name':g.analyzer_adom_name })
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_link_quality_status_sla_logs(req_payload,
                                                                                          WIDGET_LINK_QUALITY_STATUS,
                                                                                          final_response)
                return converted_response
            # --------- For bandwidth-rate ---------
            if metric_name == WIDGET_BANDWIDTH_RATE:
                # ------ Get all adoms list from file -------
                req_payload = self.fortinet_conversion_obj.convert_payload_for_timeseries(req_payload, start_date, end_date)
                final_response = []
                adom_device_ids = [filters.get('value') for filters in filter_options if filters.get('key', '') == FILTER_BY_DEVICE_ID]
                # ------------ Manager APi call to fetch device interface logs-----------
                if not adom_device_ids:
                    manager_response = self.fortinet_integrator_obj.get_device_by_id(g.analyzer_adom_name)
                    # ------------- Handle HostRespondedWithErrorException --------------
                    if manager_response.status != SUCCESS_CODE and 'error-code' in (error_message := manager_response.original_response.json()) and error_message['error-code'] != ADOM_NAME_ERROR_CODE_IN_MANAGER:
                        raise Exception(self.raise_host_responded_with_error(manager_response), ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
                    adom_device_ids = self.fortinet_conversion_obj.extract_adom_devices(manager_response)
                for device_id in adom_device_ids:
                    # ------------ Manager APi call to fetch device interface logs-----------
                    manager_response = self.fortinet_integrator_obj.get_device_interface_logs(device_id, None, **req_payload)
                    final_response.append({'manager_response': manager_response, 'device_id': device_id})
                req_payload['filter'] = filter_options
                converted_response = self.fortinet_conversion_obj.convert_to_bandwidth_rate_interface_logs(req_payload,
                                                                                          WIDGET_BANDWIDTH_RATE,
                                                                                          final_response)
                return converted_response


        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(ERROR_MESSAGE_HOST_NOT_REACHABLE, ERROR_CODE_HOST_NOT_REACHABLE)
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_report_meta(self):
        """Calls integrator layer to fetch meta data for report"""
        try:
            return self.fortinet_integrator_obj.get_report_meta()
        except APIException as ex:
            return ErrorResponse('', ex.message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_API_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR

    def service_get_system_status(self,adom_name =None ,device_id=None):
        """Calls integrator layer to fetch status for devices"""
        try:
            device_id = self.service_get_device_id(device_id=device_id)
            response = self.fortinet_integrator_obj.get_system_status(adom_name,device_id)
            if response.status != SUCCESS_CODE and response.original_response and type(
                    response.original_response.json()) == dict and 'error-code' in response.original_response.json():
                raise Exception(response.original_response.json()['error-message'], ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            # ------------- Handle HostRespondedWithErrorException --------------
            if error_message := self.raise_host_responded_with_error(response):
                raise Exception(error_message, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)
            return self.fortinet_conversion_obj.convert_response_get_system_status(response)
        except APIException as ex:
            if isinstance(ex.get_wrapped_exception(), ConnectionError):
                raise Exception(FORTINET_MANAGER_NOT_REACHABLE, ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR)

    def service_validate_client_id(self, client_id):
        if client_id.startswith('#') or client_id.startswith('&'):
            raise Exception(INVALID_CLIENT_ID, ERROR_CODE_VALIDATION_ERROR,
                HTTP_STATUS_CODE_BAD_REQUEST)
        else:
            all_sites_response = self.fortinet_integrator_obj.get_sites_for_user(
            client_id)
        # ------------ Validate ClientId ------------
            if all_sites_response.status != SUCCESS_CODE and 'error-code' in (
            error_message := all_sites_response.original_response.json()):
                raise Exception(
                error_message.get('error-message', INVALID_CLIENT_ID),
                ERROR_CODE_VALIDATION_ERROR,
                HTTP_STATUS_CODE_BAD_REQUEST)
        # ------- Validate ClientId ENDS HERE -------
        return all_sites_response
