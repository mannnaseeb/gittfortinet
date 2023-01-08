import datetime
from signal import raise_signal
from typing import Text
import dateutil.parser
from flask import g
import copy
from fortinet_common import api
from sqlalchemy.sql.elements import and_
from constants import PROVIDE_FILTER, SUCCESS_CODE,ADOM_NAME_ERROR_CODE_IN_ANALYZER,WRONG_CLIENT_ID_PROVIDED, \
    PROVIDE_CLIENT_ID,PROVIDE_VALID_REPORT_NAME,PROVIDE_TIME_RANGE,PROVIDE_VALID_START_DATE_EPOCH, \
        PROVIDE_VALID_END_DATE_EPOCH,PROVIDE_VALID_METRIC_NAME,INVALID_METRIC_NAME_FOR_METRIC_TYPE, \
            SORT_BY_NOT_SUPPORTED,PROVIDE_FIELD_AND_ORDER_SORT_BY,FILTER_NOT_SUPPORTED,PROVIDE_VALID_FILTER_OPTION, \
                PROVIDE_VALID_FILTER_OPERATION,PROVIDE_VALID_FILTER_KEY,PROVIDE_VALID_FILTER_STRUCTURE, \
                    LIMIT_NOT_SUPPORTED,PROVIDE_VALID_LIMIT_TYPE,PROVIDE_START_DATE,PROVIDE_END_DATE, \
                        PROVIDE_VALID_TIME_RANGE_TYPE,PROVIDE_START_AND_END_TIME,PROVIDE_START_TIME, \
                            PROVIDE_END_TIME,PROVIDE_SAME_DATE_FORMATS,PROVIDE_VALID_RANGE,PROVIDE_VALID_DEVICE, \
                                VALID_ORDER,PROVIDE_VALID_SORT_BY,SORT_BY_ORDER,INPUT_PAYLOAD_MAX_LIMIT, \
                                    PROVIDE_VALID_SORT_BY_OPTION_FOR_END_POINT,INPUT_PAYLOAD_MIN_LIMIT,ACCEPTED_DATE_FORMAT, \
                                        PROVIDE_LIMIT_IN_PROPER_RANGE,PROVIDE_PROPER_DATE_FORMAT,PROVIDE_TITLE_VALUE, \
                                            END_DATE_GT_START_DATE,BAD_DATETIME,PROVIDE_FORMAT_VALUE,\
                                                PROVIDE_USER_ID,PROVIDE_VALID_FILTER_VALUE,PROVIDE_USER_ID, BAD_TITLE_CODE, \
                                                    INVALID_DEVID,NO_ADOM_FOUND,NO_DEVICE_DATA_FOUND,INVALID_DEVICE_ID,\
                                                        ERROR_INVALID_REPORT_DOWNLOAD_REQUEST

from db_settings.db_utils import get_report_codes_from_database,get_report_timestamp_from_database, \
    get_report_tid_from_database,get_metric_codes_from_database,get_all_metric_types_from_database, \
        get_type_for_metric_from_database,get_sort_by_options_from_database,\
            get_all_metric_supported_operations_from_database,get_filter_by_options_from_database,\
                get_limit_for_metric_from_database,get_all_metrics_with_filter_from_database,\
                    get_report_filter_from_database,get_all_report_meta_filter_database
from languages.constants import ERROR_MESSAGE_INTERNAL_SERVER_ERROR,ERROR_MESSAGE_HOST_NOT_REACHABLE, \
    ERROR_CODE_CLIENT_API_WITH_ERROR,ERROR_CODE_VALIDATION_ERROR,HTTP_STATUS_CODE_BAD_REQUEST, \
        PROVIDE_SORT_BY,FAILED_REQUEST_PAYLOAD_VALIDATION,ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR
from languages.fortinet_api_exceptions import NoRecordFoundException, ValidationException
from integrators.fortinet_integrator import FortinetIntegrator
from models.metric import Metric
from models.metric_filtermapping import metric_filtermapping_table
# from models.metric_filter import Metric_Filter
from models import db
from models.metric_filter import MetricFilter
import logging
from constants import EPOCH_TO_DATETIME_FORMAT
from utils.fortinet_api_logger import FortinetAPILogger


logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))

integrator_object = FortinetIntegrator()

class FortinetAPIValidations:
    """Fortinet API Validations """

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

    def check_client_id_association(self, client_id=None,user_id=None):
        """Checks if the sent client_id is associated to the list of clients of user"""
        if client_id:
            if user_id is not None:
                provided_user_id = user_id
            elif 'userId' in g.__dict__:
                provided_user_id = g.userId
            #--- fetching user's clients ---
            if provided_user_id:
                user_clients_response = integrator_object.get_clients_of_user({'userid':provided_user_id})
                #------------------ checking client API response for error -------------------
                if 'error-code' in (error_message := user_clients_response.original_response.json()) and error_message[
                    'error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                    raise Exception(self.raise_host_responded_with_error(user_clients_response), ERROR_CODE_CLIENT_API_WITH_ERROR)
                # ------------- checking client API response for error ENDS HERE -------------
                #------ validating that provided client id is linked to logged in user -------
                if type(user_clients_response.data) == list:
                    for client in user_clients_response.data:
                        #Hierarchy : user -> clients
                        #--- check provided client id in list of clients of user ---
                        if str(client_id) == str(client['id']):
                            break
                    #If client id does not belong to list of clients for user, raise error
                    else:
                        raise Exception(WRONG_CLIENT_ID_PROVIDED, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                #-- validating that provided client id is linked to logged in user ENDS HERE --
            else:
                raise Exception(PROVIDE_USER_ID, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        else:
            raise Exception(PROVIDE_CLIENT_ID, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)

    def check_invalid_filter_payload_reports(self, input_payload,tid=None):
        if not tid:
            title_report = get_report_codes_from_database(input_payload.get('title', '').strip())
            if not title_report:
                raise ValidationException(BAD_TITLE_CODE)
        if tid:
            try:
                required_filter = get_all_report_meta_filter_database(tid=tid)
            except Exception as ex:
                raise ValidationException(ERROR_INVALID_REPORT_DOWNLOAD_REQUEST)
        else:
            if "title" not in input_payload:
                raise ValidationException(PROVIDE_TITLE_VALUE)
            required_filter = get_all_report_meta_filter_database(input_payload['title'])
        for filter_r in required_filter:
            if 'filter' not in input_payload:
                raise ValidationException(PROVIDE_VALID_FILTER_OPTION)
            key_found = False
            required_key = ""
            for filter_payload in filter_r['filters']:
                if filter_payload['is_required']:
                    for all_key in input_payload['filter']:
                        if filter_payload['field'] == all_key['key']:
                            required_key = filter_payload['field']
                            key_found = True
                            if "value" not in all_key or ("value" in all_key and len(all_key["value"].strip()) == 0):
                                raise ValidationException(PROVIDE_VALID_FILTER_VALUE)
                            if "operation" not in all_key:
                                raise ValidationException(PROVIDE_VALID_FILTER_OPERATION)
                            elif all_key['operation'] not in filter_payload['supported_operation']:
                                raise ValidationException(PROVIDE_VALID_FILTER_OPERATION)
                            if filter_payload['field'] == "client-id":
                                g.client_id = all_key['value']
            if not key_found and not 'client_id' in g.__dict__:
                raise ValidationException(PROVIDE_VALID_FILTER_OPTION)
            input_payload['filter'] = [d for d in input_payload['filter'] if d.get('key') != required_key]
            if input_payload['filter'] == []:
                del input_payload['filter']
    # Returns error message if invalid input payload
    def check_invalid_payload_reports(self, input_payload, end_point):
        title_report = get_report_codes_from_database(end_point)
        if not title_report:
            raise ValidationException(PROVIDE_VALID_REPORT_NAME)
        input_payload['title'] = title_report[0]
        # start_date and end_date won't be there when payload is validated second time for fortinet analyzer
        if 'start-date' in input_payload:
            copy_inp_payload = copy.deepcopy(input_payload)
            copy_inp_payload['start_date'] = copy_inp_payload.get('start-date', None)
            copy_inp_payload['end_date'] = copy_inp_payload.get('end-date', None)
            self.validate_req_payload_date_format(copy_inp_payload)
        if 'end-date' in input_payload:
            copy_inp_payload = copy.deepcopy(input_payload)
            copy_inp_payload['start_date'] = copy_inp_payload.get('start-date', None)
            copy_inp_payload['end_date'] = copy_inp_payload.get('end-date', None)
            self.validate_req_payload_date_format(copy_inp_payload)
        if 'start-date' not in input_payload and 'end-date' not in input_payload:
            start_date = get_report_timestamp_from_database(title_report[0])
            if start_date:
                input_payload['time-range']={"start":start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                  "end":datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            else:
                raise NoRecordFoundException("No Record Found")

    # Returns error message if invalid report tid
    def check_invalid_tid_for_report(self, tid):
        """check if tid present in reports table"""
        if not get_report_tid_from_database(tid):
            raise NoRecordFoundException(ERROR_INVALID_REPORT_DOWNLOAD_REQUEST)

    def check_filter(self, input_payload, end_point, metric_type_position=None):
        # --------------------- Checking filter ----------------------
        ALL_METRIC_FILTERS = get_all_metrics_with_filter_from_database(end_point)
        required_key = ""
        key_found = False
        for current_metric in ALL_METRIC_FILTERS:
            if current_metric['code'] == end_point:
                for filter in current_metric['filters']:
                    if filter.get('is_required') == True:
                        if 'filter' not in input_payload:
                            raise Exception(PROVIDE_FILTER, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                        for filter_payload in input_payload['filter']:
                            if filter_payload['key'] == filter.get('field'):
                                key_found = True
                                if "value" not in filter_payload or ("value" in filter_payload and len(filter_payload["value"].strip()) == 0):
                                    raise Exception(PROVIDE_FILTER, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                                if "operation" not in filter_payload:
                                    raise Exception(PROVIDE_VALID_FILTER_OPERATION, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
                                elif filter_payload['operation'] not in filter.get("supported_operation"):
                                    raise Exception(PROVIDE_VALID_FILTER_OPERATION, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
                                if filter_payload['key'] == "client-id":
                                    g.client_id = filter_payload['value']
                        if not key_found and len(g.client_id) == 0:
                            raise Exception(PROVIDE_FILTER, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                        input_payload['filter'] = [d for d in input_payload['filter'] if d.get('key') != required_key]
                        if input_payload['filter'] == []:
                            del input_payload['filter']

    # Returns error message if invalid input payload
    def check_invalid_payload(self, input_payload, end_point, metric_type_position=None):
        """Checks for invalid payload"""
        # --------------------- Checking metrics name -----------------
        if end_point not in get_metric_codes_from_database():
            raise Exception(PROVIDE_VALID_METRIC_NAME, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)

        # --------------------- Checking proper metric type for end_point -----------------
        if (metric_type_position or metric_type_position == 0) and (all_metric_types := get_all_metric_types_from_database()) and (type_for_metrics := get_type_for_metric_from_database()):
                if not {all_metric_types[metric_type_position]}.intersection(set(type_for_metrics[end_point])):
                    raise Exception(INVALID_METRIC_NAME_FOR_METRIC_TYPE.format(metric_name=str(end_point), metric_type=str(all_metric_types[metric_type_position])), ERROR_CODE_VALIDATION_ERROR,
                                    HTTP_STATUS_CODE_BAD_REQUEST)

        # check if mandatory filter is present in request payoad
        try:
            mandatory_filters = db.session.query(Metric, metric_filtermapping_table, MetricFilter).select_from(Metric).join(metric_filtermapping_table).join(MetricFilter).filter(and_ (metric_filtermapping_table.c.IsRequired == 1, Metric.MetricCode == f"{end_point}")).all()
        except Exception as ex:
            logger.exception("Failed to read mandatory filters data from DB")
            raise Exception(FAILED_REQUEST_PAYLOAD_VALIDATION)

        if mandatory_filters:
            input_payload_filters = input_payload.get('filter', [])
            request_filters = []
            if type(input_payload_filters) == list:
                for filter in input_payload_filters:
                    request_filters.append(filter['key'])
                for mandatory_filter in mandatory_filters:
                    if mandatory_filter.MetricFilter.MetricFilterName not in request_filters:
                        raise ValidationException(f"Mandatory filter '{mandatory_filter.MetricFilter.MetricFilterName}' is missing.")
        SORT_BY_OPTIONS = get_sort_by_options_from_database()
        VALID_OPERATIONS = get_all_metric_supported_operations_from_database()
        FILTER_BY_OPTIONS = get_filter_by_options_from_database()
        # --------------------- Checking sort-by ----------------------
        if "sort-by" in input_payload and not SORT_BY_OPTIONS.get(end_point):
            raise Exception(SORT_BY_NOT_SUPPORTED, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        if SORT_BY_OPTIONS.get(end_point):
            if "sort-by" in input_payload:
                if len(input_payload["sort-by"]):
                    if error_message := self.check_sort_by_for_end_point(input_payload["sort-by"], end_point,
                                                                         SORT_BY_OPTIONS):
                        raise Exception(error_message, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                else:
                    raise Exception(PROVIDE_FIELD_AND_ORDER_SORT_BY, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        # ---------------- Checking sort-by ENDS HERE ----------------



        if "filter" in input_payload and not FILTER_BY_OPTIONS.get(end_point):
            raise Exception(FILTER_NOT_SUPPORTED, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        if "filter" in input_payload:
            # Below condition is to check if the filter option provided is of type string or not
            if type(input_payload['filter']) is list:
                if not len(input_payload['filter']):
                    raise Exception(PROVIDE_VALID_FILTER_OPTION, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
                else:
                    for filter_item in input_payload['filter']:
                        if not (
                                'key' in filter_item and 'value' in filter_item and 'operation' in
                                filter_item and filter_item.get('value','')):
                            raise Exception(PROVIDE_VALID_FILTER_OPTION, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
                        if not (type(filter_item['key']) is str and type(
                                filter_item['value']) is str):
                            raise Exception(PROVIDE_VALID_FILTER_OPTION, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
                        if filter_item['operation'] not in VALID_OPERATIONS:
                            raise Exception(PROVIDE_VALID_FILTER_OPERATION, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
                        if filter_item['key'] not in FILTER_BY_OPTIONS.get(end_point):
                            raise Exception(PROVIDE_VALID_FILTER_KEY, ERROR_CODE_VALIDATION_ERROR,
                                            HTTP_STATUS_CODE_BAD_REQUEST)
            elif not type(input_payload['filter']) == str:
                raise Exception(PROVIDE_VALID_FILTER_STRUCTURE, ERROR_CODE_VALIDATION_ERROR,
                                HTTP_STATUS_CODE_BAD_REQUEST)
        # ---------------- Checking filter ENDS HERE ----------------

        # --------------------- Checking limit ----------------------
        # -------- Stores all limit stored against each metric --------
        all_metric_limits = get_limit_for_metric_from_database()
        if "limit" in input_payload and not all_metric_limits.get(end_point):
            raise Exception(LIMIT_NOT_SUPPORTED, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        if "limit" in input_payload and type(input_payload["limit"]) == int:
            if error_message := self.check_limit_value(input_payload["limit"]):
                raise Exception(error_message, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        elif "limit" in input_payload and type(input_payload["limit"]) != int:
            raise Exception(PROVIDE_VALID_LIMIT_TYPE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        # ---------------- Checking limit ENDS HERE ----------------
        if 'start_date' in input_payload:
                self.validate_req_payload_date_format(input_payload)
        elif 'time-range' not in input_payload:
            raise Exception(PROVIDE_START_DATE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)

        if 'end_date' in input_payload:
                self.validate_req_payload_date_format(input_payload)
        
        # time-range won't be there when payload is validated first time for fortinet api
        elif 'time-range' not in input_payload:
            raise Exception(PROVIDE_END_DATE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
    

        # --------------------- Checking time-range ----------------------
        if "time-range" in input_payload:
            if not type(input_payload['time-range']) == dict:
                raise Exception(PROVIDE_VALID_TIME_RANGE_TYPE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            if 'start' not in input_payload['time-range'] or 'end' not in input_payload['time-range']:
                raise Exception(PROVIDE_START_AND_END_TIME, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            if not input_payload['time-range']['start']:
                raise Exception(PROVIDE_START_TIME, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            if not input_payload['time-range']['end']:
                raise Exception(PROVIDE_END_TIME, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            # --------------------- Checking start date format ----------------------
            if (type(start_date_response := self.check_for_proper_date_format(
                    input_payload['time-range']['start'])) != dict):
                raise Exception(start_date_response, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            # ---------------- Checking start date format ENDS HERE ----------------
            # --------------------- Checking end date format ----------------------
            if (type(end_date_response := self.check_for_proper_date_format(
                    input_payload['time-range']['end'])) != dict):
                raise Exception(end_date_response, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            # ---------------- Checking end date format ENDS HERE ----------------

            # Check if different start and end date format is passed
            if start_date_response['date-format-type'] != end_date_response['date-format-type']:
                raise Exception(PROVIDE_SAME_DATE_FORMATS, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)

            if start_date_response['passed-date'] >= end_date_response['passed-date']:
                raise Exception(PROVIDE_VALID_RANGE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)

        # start_date and end_date won't be there when payload is validated second time for fortinet analyzer
        elif 'start_date' not in input_payload and 'end_date' not in input_payload:
            raise Exception(PROVIDE_TIME_RANGE, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
        # ---------------- Checking time-range ENDS HERE ----------------
        

    # --------------------- Checking device ---------------------
    def check_device_structure(self, device_structure):
        """Checks device structure in request payload"""
        for item in device_structure:
            for key, value in list(item.items()):
                if type(value) != str:
                    return PROVIDE_VALID_DEVICE + " in " + str(key)
        return None

    # ---------------- Checking device ENDS HERE ----------------

    # --------------------- Checking sort-by ----------------------
    def check_sort_by_for_end_point(self, sort_by_values, end_point, SORT_BY_OPTIONS):
        """Checks sort-by options passed in request payload"""
        for item in sort_by_values:
            if 'field' and 'order' not in list(item.keys()):
                raise Exception(PROVIDE_FIELD_AND_ORDER_SORT_BY, ERROR_CODE_VALIDATION_ERROR, HTTP_STATUS_CODE_BAD_REQUEST)
            for key, value in list(item.items()):
                if key == list(VALID_ORDER.keys())[0]:
                    if value not in VALID_ORDER[key]:
                        return PROVIDE_VALID_SORT_BY + " in " + str(key)
                else:
                    # Below condition is to check if the sort by option provided is from the overall accepted unique sort by options
                    if type(value) != str or value not in SORT_BY_OPTIONS[end_point]:
                        return PROVIDE_VALID_SORT_BY + " in " + str(key)
                    # Below condition is to check if the sort by option provided is accepted for the enpoint
                    elif key != SORT_BY_ORDER and value in SORT_BY_OPTIONS[end_point] and value not in SORT_BY_OPTIONS[
                        end_point]:
                        return PROVIDE_VALID_SORT_BY_OPTION_FOR_END_POINT % str(key)

    # ---------------- Checking sort-by ENDS HERE ----------------

    # --------------------- Checking limit ----------------------
    def check_limit_value(self, limit):
        """Checks value of limit in request payload"""
        if not (INPUT_PAYLOAD_MIN_LIMIT <= limit and limit <= INPUT_PAYLOAD_MAX_LIMIT):
            return PROVIDE_LIMIT_IN_PROPER_RANGE.format(str(INPUT_PAYLOAD_MIN_LIMIT), str(INPUT_PAYLOAD_MAX_LIMIT))

    # ---------------- Checking limit ENDS HERE ----------------

    # --------------------- Checking proper date format ----------------------
    def check_for_proper_date_format(self, date_passed):
        """Checks date format as required"""
        try:
            date_format_type = "non-utc"
            # check format '%Y-%m-%d %H:%M:%S'
            date_passed = datetime.datetime.strptime(date_passed, ACCEPTED_DATE_FORMAT)
        except Exception:
            try:
                date_format_type = "utc"
                # check format 'yyyy-MM-dd'T'HH:mm:ssZ'
                date_passed = dateutil.parser.isoparse(date_passed)
            except Exception as ex:
                return PROVIDE_PROPER_DATE_FORMAT
        return {'success': 1, 'date-format-type': date_format_type, 'passed-date': date_passed}
    # ---------------- Checking proper date format ENDS HERE ----------------

    # Returns error message if invalid input payload
    def check_adom_report_invalid_payload(self, input_payload):
        """Checks for invalid payload"""

        # --------------------- Checking filter ----------------------
        if "filter" in input_payload:
            # if input_payload['filter'] == '':
            #     raise ValidationException(PROVIDE_VALID_FILTER_STRUCTURE)
            # Below condition is to check if the filter option provided is of type string or not
            if type(input_payload['filter']) is list:
                if not len(input_payload['filter']):
                    raise ValidationException(PROVIDE_VALID_FILTER_OPTION)
                else:
                    for filter_item in input_payload['filter']:
                        if not (
                                'key' in filter_item and 'value' in filter_item and 'operation' in
                                filter_item and filter_item.get('value','')):
                            raise ValidationException(PROVIDE_VALID_FILTER_OPTION)
                        if not (type(filter_item['key']) is str and type(
                                filter_item['value']) is str):
                            raise ValidationException(PROVIDE_VALID_FILTER_OPTION)

            elif not type(input_payload['filter']) == str:
                raise ValidationException(PROVIDE_VALID_FILTER_STRUCTURE)
        # ---------------- Checking filter ENDS HERE ----------------
        if "title" not in input_payload:
            raise ValidationException(PROVIDE_TITLE_VALUE)
        if "title" in input_payload and input_payload['title'] == '':
            raise ValidationException(PROVIDE_TITLE_VALUE)
        # ---------------- Checking title ENDS HERE ----------------
        self.validate_req_payload_date_format(input_payload)
        
        # ---------------- Checking end date ENDS HERE ----------------

    def validate_inp_payload(self, input_payload):
        """Checks for invalid payload"""
        # ---------------- Checking format ----------------
        if "format" in input_payload :
            if input_payload['format'] == '':
                raise ValidationException(PROVIDE_FORMAT_VALUE)
        else:
            raise ValidationException(PROVIDE_FORMAT_VALUE)

    def validate_device_id(self, req_payload):
        retrieved_dev_ids = False
        if req_payload and req_payload.get("filter"):
            filters = req_payload.get("filter", [])
            adom_all_device_ids = []
            for filter in filters:
                if filter.get("key") == "devid":
                    if(not retrieved_dev_ids):
                        adom_name = g.get('manager_adom_name', None)
                        if not adom_name:
                            raise Exception(NO_ADOM_FOUND)
                        apiResponse = FortinetIntegrator().get_device_by_id(adom_name)
                        if apiResponse.status == SUCCESS_CODE:
                            for device_data in apiResponse.data.get('data', []):
                                dev_sno = device_data.get("serial_number", None) 
                                dev_sno and adom_all_device_ids.append(dev_sno)
                        else:
                            error_msg = NO_DEVICE_DATA_FOUND
                            if apiResponse.original_response and type(
                                apiResponse.original_response.json()) == dict and 'error-code' in apiResponse.original_response.json():
                                error_msg = apiResponse.original_response.json()['error-message']
                                logger.exception(f"Failed to retrieve all device data reason: {apiResponse.original_response.json()}")
                            
                            raise Exception(error_msg)
                        retrieved_dev_ids = True
                    if filter.get("value") not in adom_all_device_ids:
                        raise ValidationException(INVALID_DEVID)

    def validate_dev_id(self, incoming_devids):
        adom_all_serial_numbers = []
        adom_name = g.get('manager_adom_name', None)
        if not adom_name:
            raise Exception(NO_ADOM_FOUND)
        apiResponse = FortinetIntegrator().get_device_by_id(adom_name)
        if apiResponse.status == SUCCESS_CODE:
            for device_data in apiResponse.data.get('data', []):
                adom_device_data = device_data.get("serial_number", None)
                adom_device_data and adom_all_serial_numbers.append(adom_device_data)
       
        else:
            error_msg = NO_DEVICE_DATA_FOUND
            if apiResponse.original_response and type(
                apiResponse.original_response.json()) == dict and 'error-code' in apiResponse.original_response.json():
                error_msg = apiResponse.original_response.json()['error-message']
                logger.exception(f"Failed to retrieve all device data reason: {apiResponse.original_response.json()}")
            raise Exception(error_msg)

        if incoming_devids not in adom_all_serial_numbers:
            raise ValidationException(INVALID_DEVICE_ID)
    
    def validate_req_payload_date_format(self,req_payload):
        if ('start_date' in req_payload and 'end_date' in req_payload):
            start_date_obj, end_date_obj = None, None
            start_date_format = None
            # accepted date formats epochtime, ISO
            error = None
            try:    
                start_date_obj = datetime.datetime.fromtimestamp(int(req_payload.get('start_date')))
                start_date_format = "epoch-time"
            except ValueError as e:
                error = str(e)
            if error:
                try:
                    start_date_obj = datetime.datetime.fromisoformat(req_payload.get('start_date'))
                    error = None
                    start_date_format = "iso-str"
                except ValueError as e:
                    error = str(e)
            if error:
                raise ValidationException("Invalid date format Please provide date in iso or epoch time format")

            if start_date_format == "epoch-time":
                try:
                    end_date_obj = datetime.datetime.fromtimestamp(int(req_payload.get('end_date')))
                except ValueError as e:
                    error = str(e)
            else:
                try:
                    end_date_obj = datetime.datetime.fromisoformat(req_payload.get('end_date'))
                except ValueError as e:
                    error = str(e)
            if error:
                raise ValidationException("Invalid date format Please provide date in iso or epoch format")
            
            try:
                assert end_date_obj > start_date_obj
            except AssertionError as ex:
                raise ValidationException(END_DATE_GT_START_DATE)
        else:
            error_msg = ""
            if(req_payload.get("start_date")):
                error_msg = "Please provide a valid end-date"
            else:
                error_msg = "Please provide a valid start-date"

            raise ValidationException(error_msg)
