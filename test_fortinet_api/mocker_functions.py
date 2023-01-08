import json as js

from fortinet_common import APIResponse
from requests import Response
from languages.fortinet_api_exceptions import HostNotReachableException, HostRespondedWithErrorException, ValidationException

from test_fortinet_api.constants import SUCCESSFULLY_GENERATED_TOKEN,FORTINET_MANAGER_NOT_REACHABLE,EXPECTED_BAD_REQUEST_STATUS, \
    UNIT_TEST_SITE_DETAILS,UNIT_TEST_BAD_METRIC_NAME,UNIT_TEST_TOP_USERS,UNIT_TEST_RISK_ANALYSIS
from test_fortinet_api.responses import *
from services.fortinet_api_services import FortinetAPIService

service_object = FortinetAPIService()

# ------------------- Mock Exceptions -------------------
validate_token_data = {
    "status": 200
}


# validate token
def mock_validate_token_success_response(url, *args, **kwargs):
    response = APIResponse(data=validate_token_data)
    return response


generate_token_data = {
    "access_token": SUCCESSFULLY_GENERATED_TOKEN
}


# validate token
def mock_generate_token_success_response(url, *args, **kwargs):
    response = APIResponse(data=generate_token_data)
    return response

# validate token
def mock_generate_token_bad_response(url, *args, **kwargs):
    response = APIResponse(data=None)
    return response


# ------------------- Mock Exceptions -------------------

# ---------------------- Interceptor mock function get correlation id ----------------------

def mock_uuid():
    return 22


# ---------------------- End Interceptor mock function get correlation id ----------------------

# ---------------------- Services mock function Adom by name ----------------------
def success_response_from_adom_name(self=None, adom_name=None, url=None, headers=None):
    response = APIResponse(data=adom_list_by_name_integrator_response)
    return response


def bad_response_from_adom_name(self=None, adom_name=None, url=None, headers=None):
    response = APIResponse(data=None)
    return response


# ---------------------- End Services mock function Adom by name ----------------------

# ---------------------- Services mock function Adom list ----------------------
def success_response_from_adom_list(self=None, url=None, headers=None):
    response = APIResponse(data=all_adom_list_integrator_response)
    return response


def bad_response_from_adom_list(self=None, url=None, headers=None):
    response = APIResponse(data=None)
    return response


# ---------------------- End Services mock function Adom list ----------------------

# ---------------------- Services mock function Adom device list ----------------------
def success_response_adom_device_list_from_api(self=None, adom_name=None, device_id=None, url=None, headers=None):
    response = APIResponse(data=adom_devices_list_integrator_response)
    return response


def bad_response_adom_device_list_from_api(self=None, adom_name=None, device_id=None, url=None, headers=None):
    response = APIResponse(data=None)
    return response


def bad_response_adom_device_list_from_api_mock_cache(self=None, class_name=None, key=None, pk=None):
    response = APIResponse(data=None)
    return response

# ---------------------- End Services mock function Adom device list ----------------------

# ---------------------- Services mock function Adom device by id ----------------------

def success_response_adom_device_by_id_from_api(self=None, adom_name=None, device_id=None, url=None, headers=None):
    response = APIResponse(data=adom_devices_by_id_integrator_response)
    return response


def bad_response_adom_device_by_id_from_api(self=None, adom_name=None, device_id=None, url=None, headers=None):
    response = APIResponse(data=None)
    return response


# ---------------------- End Services mock function Adom device by id ----------------------

# ---------------------- Services mock function instant metric ----------------------
def success_response_metric_instant(self=None, url=None, json=None):
    response = APIResponse(data=instant_metric_integrator_response)
    return response


def success_no_filter_metric_instant(self=None, url=None, json=None):
    response = APIResponse(data=instant_metric_no_filter_response)
    return response

def success_no_sort_by_metric_instant(self=None, url=None, json=None):
    response = APIResponse(data=instant_metric_no_sort_by_response)
    return response


def success_no_limit_metric_instant(self=None, url=None, json=None):
    response = APIResponse(data=instant_metric_no_limit_response)
    return response


def validation_error(self=None, url=None, json=None):
    data = {
        "error-code": 9004,
        "error-auxiliary": "Validation error",
        "error-message": "error_message"
    }
    response = APIResponse(data=data)
    return response


# ---------------------- End Services mock function instant metric ----------------------

# ---------------------- Services mock function bandwidth rate ----------------------
def full_payload_success_response_traffic_summary(self=None, req_payload=None, metric_name=None, adom_name=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(traffic_summary_full_payload_integrator_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=traffic_summary_full_payload_integrator_response[adom_name],
                           original_response=response)
    return response

def success_no_filter_traffic_summary(self=None, req_payload=None, metric_name=None, adom_name=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(traffic_summary_no_filter_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=traffic_summary_no_filter_response[adom_name],
                           original_response=response)
    return response


# ---------------------- End Services mock function Traffic Summary ------------------

# ---------------------- Services mock function bandwidth rate ----------------------
def full_payload_success_response_bandwidth_rate(self=None, url=None, json=None):
    response = APIResponse(data=bandwidth_rate_full_payload_integrator_response)
    return response


def success_no_sort_by_bandwidth_rate(self=None, url=None, json=None):
    response = APIResponse(data=bandwidth_rate_no_sort_by_integrator_response)
    return response


def success_no_filter_bandwidth_rate(self=None, url=None, json=None):
    response = APIResponse(data=bandwidth_rate_no_filter_integrator_response)
    return response


def success_no_limit_bandwidth_rate(self=None, url=None, json=None):
    response = APIResponse(data=bandwidth_rate_no_limit_integrator_response)
    return response


# ---------------------- End Services mock function bandwidth rate ------------------

# ---------------------- Services mock function top application usage ----------------------
def full_payload_success_response_top_application_usage(self=None, url=None, json=None):
    response = APIResponse(data=top_application_usage_full_payload_integrator_response)
    return response


def success_no_sort_by_top_application_usage(self=None, url=None, json=None):
    response = APIResponse(data=top_application_usage_no_sort_by_integrator_response)
    return response

def success_no_filter_top_application_usage(self=None, url=None, json=None):
    response = APIResponse(data=top_application_usage_no_filter_integrator_response)
    return response


def success_no_limit_top_application_usage(self=None, url=None, json=None):
    response = APIResponse(data=top_application_usage_no_limit_integrator_response)
    return response

def success_top_application_usages_integrator_response(self, adom_name=None, **req_payload):
    response = APIResponse(data=adom_cloudsmartz_response)
    return response


def success_top_application_usages_all_adom_integrator_response(self=None,adom_name=None,**req_payload):
    if adom_name == "CloudSmartz":
        response = Response()
        response.status_code = 200
        response._content = str.encode(js.dumps(adom_cloudsmartz_response))
        response._content_consumed = True
        response.encoding = 'utf-8'
        response = APIResponse(data=adom_cloudsmartz_response, original_response=response)
        return response
    if adom_name == "Cloud_Firewall":
        response = Response()
        response.status_code = 200
        response._content = str.encode(js.dumps(adom_cloudsmartz_response))
        response._content_consumed = True
        response.encoding = 'utf-8'
        response = APIResponse(data=adom_cloud_firewall_response,original_response=response)
        return response
    if adom_name == "D-AND-D":
        response = Response()
        response.status_code = 200
        response._content = str.encode(js.dumps(adom_cloudsmartz_response))
        response._content_consumed = True
        response.encoding = 'utf-8'
        response = APIResponse(data=adom_d_and_d_response,original_response=response)
        return response
    if adom_name == "FortiAnalyzer":
        response = Response()
        response.status_code = 200
        response._content = str.encode(js.dumps(adom_cloudsmartz_response))
        response._content_consumed = True
        response.encoding = 'utf-8'
        response = APIResponse(data=adom_FortiAnalyzer_response,original_response=response)
        return response
    return APIResponse(data=None)




def bad_top_application_usages_integrator_response(self, adom_name=None, **req_payload):
    response = APIResponse(data=top_application_usages_bad_integrator_response)
    return response

def bad_token_top_application_usages_all_adom_response(self, adom_name=None, **req_payload):
    response = APIResponse(data=top_application_token_expired_response)
    return response




def failed_to_generate_token_top_application_usages(*args, **kwargs):
    response = APIResponse(data=None,status=500)
    return response
def success_generate_token_top_application_usages(*args, **kwargs):
    response = APIResponse(data=valid_token)
    return response

# bad_credential_data
def bad_response_bad_credential_uuidfrom_client_top_applications(self, adom_name, **kwargs):
    response = APIResponse(data=bad_response_credential_uuid_top_applications)
    return response

# bad_service_reponse
def bad_response_from_service__client_top_applications(*args, **kwargs):
    response = APIResponse(data=None,status=500)
    return response

def failed_to_generate_token(*args, **kwargs):
    response = APIResponse(data=None,status=500)
    return response

def bad_response_analyzer_not_reachable_top_categories(self, adom_name=None, **req_payload):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(host_not_reachable))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=host_not_reachable,
                        original_response=response)
    return response

def bad_response_analyzer_not_reachable_top_application_usages_invalid_matric_name(self, adom_name=None, **req_payload):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(invalid_matric_name))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=invalid_matric_name,
                        original_response=response)
    return response


# ---------------------- End Services mock function top application usage ------------------

# ---------------------- Services mock function top users ----------------------
def full_payload_success_response_top_users(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(top_users_integrator_response_full_payload[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=top_users_integrator_response_full_payload[adom_name],
                           original_response=response)
    return response

def full_payload_success_response_top_application_threats(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(top_application_threats_integrator_response_full_payload[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=top_application_threats_integrator_response_full_payload[adom_name],
                           original_response=response)
    return response

def bad_response_converter_top_users(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = APIResponse(data=None, status=500)
    raise HostRespondedWithErrorException(service_object.raise_host_responded_with_error(response))

def bad_response_converter_top_application_threats(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = APIResponse(data=None, status=500)
    raise HostRespondedWithErrorException(service_object.raise_host_responded_with_error(response))

def bad_response_analyzer_not_reachable(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(analyzer_not_reachable_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=None, original_response=response)
    return response


def bad_response_im_server_top_users(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(im_server_token_exception))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=None, original_response=response)
    return response


# ---------------------- End Services mock function top users ------------------

# ---------------------- Services mock function top sources by application ----------------------
def full_payload_success_response_top_sources_by_application(self=None, adom_name=None, url=None,
                                                             json=None, **req_payload):
    response = Response()
    response.status_code = 200
    response._content = str.encode(
        js.dumps(top_sources_by_application_full_payload_integrator_original_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=top_sources_by_application_full_payload_integrator_original_response[adom_name],
                           original_response=response)
    return response


def bad_response_analyzer_top_services_by_application(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = APIResponse(data=None, status=500)
    raise HostRespondedWithErrorException(service_object.raise_host_responded_with_error(response))


def bad_response_analyzer_not_reachable_top_users(self=None, req_payload=None, adom_name=None, url=None, json=None):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(analyzer_not_reachable_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=None,
                           original_response=response)
    return response


def bad_response_im_server_top_services_by_application(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(im_server_token_exception))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=None,
                           original_response=response)
    return response


# ---------------------- End Services mock function top sources by application ------------------

def success_response_manager_interface_logs(self=None, req_payload=None, device_id=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(interface_log_manager_response[device_id]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=interface_log_manager_response[device_id], original_response=response)
    return response
# ---------------------- Services mock function site details ----------------------
def success_response_manager_site_details(self=None, adom_name=None, device_id=None, url=None, json=None, headers=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(site_details_manager_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=site_details_manager_response[adom_name], original_response=response)
    return response


def success_response_analyzer_site_details(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(site_details_analyzer_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=site_details_analyzer_response[adom_name], original_response=response)
    return response


def success_response_manager_site_details_no_device(self=None, adom_name=None, device_id=None, url=None, json=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(site_details_manager_response_no_device[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=site_details_manager_response_no_device[adom_name], original_response=response)
    return response


def success_response_analyzer_site_details_no_device(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(site_details_analyzer_response_no_device[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=site_details_analyzer_response_no_device[adom_name], original_response=response)
    return response


def bad_response_integrator_manager_site_details(self=None, adom_name=None, device_id=None, url=None, headers=None):
    response = APIResponse(data=None)
    return response


def bad_response_converter_site_details(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = APIResponse(data=None, status=500)
    raise HostRespondedWithErrorException(service_object.raise_host_responded_with_error(response))


def exception_response_manager_site_details(self=None, adom_name=None, device=None, url=None, json=None):
    raise HostNotReachableException(FORTINET_MANAGER_NOT_REACHABLE)

def exception_response_site_for_user_site_details(self=None, adom_name=None, device=None, url=None, json=None):
    raise HostNotReachableException(FORTINET_MANAGER_NOT_REACHABLE)

def exception_response_analyzer_site_details(self=None, adom_name=None, url=None, json=None, **req_payload):
    raise HostNotReachableException(FORTINET_ANALYZER_NOT_REACHABLE)



# ---------------------- End Services mock function site details ------------------

# ---------------------- Services mock function risk analysis ----------------------
def full_payload_success_response_risk_analysis(self=None, adom_name=None, url=None,
                                                json=None, **req_payload):
    response = Response()
    response.status_code = 200
    response._content = str.encode(
        js.dumps(risk_analysis_full_payload_integrator_original_response[adom_name]))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=risk_analysis_full_payload_integrator_original_response[adom_name],
                           original_response=response)
    return response


def bad_response_analyzer_risk_analysis(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = APIResponse(data=None, status=500)
    raise HostRespondedWithErrorException(service_object.raise_host_responded_with_error(response))


def bad_response_analyzer_not_reachable(self=None, adom_name=None, url=None, json=None, **req_payload):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(analyzer_not_reachable_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=None,
                           original_response=response)
    return response


# ---------------------- End Services mock function risk analysis ------------------
# ---------------------- Services mock function top application threats ------------------
widget_api_top_application_threats_success_input_payload = {
    'full_input_payload': {
        'input': {
            "sort-by": [
                {
                "field": "d_risk",
                "order": "asc"
              }
            ],
            "limit": 4,
             "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'function_obj': full_payload_success_response_top_application_threats,
        'final_integrator_response': top_application_threats_integrator_response_full_payload
    },
    # 'no_limit': {
    #     'input': {
    #         "sort-by": [
    #             {
    #             "field": "d_risk",
    #             "order": "asc"
    #           }
    #         ],
    #          "start_date": "1620717116",
    #         "end_date": "1626419516"
    #     },
    #     'function_obj': full_payload_success_response_top_application_threats,
    #     'final_integrator_response': top_application_threats_integrator_response_full_payload
    # }
}

widget_api_top_users_failure_input_payload = {
    'no_filter': {
        'input': {
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_wrong_filter_keys': {
        'input': {
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_start_date': {
        'input': {
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_end_date': {
        'input': {
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'no_sort_by': {
        'input': {
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_non_supported_filed_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "counts",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_non_supported_order_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "sessions",
                    "order": "wrong_order"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'limit_above_500': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'limit_below_1': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_limit': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 'a',
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    }
}

def success_top_application_threats_all_adom_integrator_response(self, req_payload, adom_name=None):
    
    if adom_name == "CloudSmartz":
        response = APIResponse(data=top_threats_adom_cloudsmartz_response)
        return response
    
    if adom_name == "D-AND-D":
        response = APIResponse(data=top_threats_adom_d_and_d_response)
        return response

    if adom_name == "LG-LAB":
        response = APIResponse(data=top_threats_adom_lg_lab_response)
        return response

    if adom_name == "Saint_Louis_Inc":
        response = APIResponse(data=top_threats_adom_saint_louis_inc_response)
        return response
    return APIResponse(data=None)

#limit = 2

def success_with_two_limit_top_application_threats_all_adom_integrator_response(self, req_payload, adom_name=None):
    
    if adom_name == "CloudSmartz":
        response = APIResponse(data=top_threats_adom_cloudsmartz_response)
        return response
    
    if adom_name == "D-AND-D":
        response = APIResponse(data=top_threats_adom_d_and_d_response)
        return response

    return APIResponse(data=None)    

#LIMIT = 0
def bad_zero_limit_top_application_threats_all_adom_integrator_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_zero_limit_response)
    return response

#without sortby
def bad_without_sortby_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_without_sortby_response)
    return response

#without field
def bad_without_field_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_without__field_sortby_response)
    return response

#without order
def bad_without_order_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_without_order_sortby_response)
    return response


#wrong field
def bad_wrong_field_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_wrong_field_sortby_response)
    return response


#empty start time
def bad_empty_start_time_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_empty_start_time_response)
    return response

#empty-endtime
def bad_empty_end_time_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_empty_end_time_response)
    return response


#wrong time range
def bad_wrong_time_range_top_application_threats_all_adom_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_wrong_time_range_response)
    return response


# ---------------------- End Services mock function top application threats ------------------

#INTEGRATOR

def success_top_application_threats_integrator_response(self, req_payload, adom_name=None):
    response = APIResponse(data=top_application_threats_integrator_response)
    return response


# ---------------------- Instant metric input payload ----------------------
metric_success_input_payload = {
    'proper_input_payload': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_response_metric_instant
    },
    'no_sort_by': {
        'input': {
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_no_sort_by_metric_instant
    },
    'no_filter': {
        'input': {
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_no_filter_metric_instant,
    },
    'no_limit': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_no_limit_metric_instant
    }
}

metric_failure_input_payload = {
    'invalid_start_date': {
        'input': {
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'invalid_end_date': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'limit_above_500': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': 'fortinet_common.APIService.post'
    },
    'limit_below_1': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': 'fortinet_common.APIService.post'
    },
}

# ---------------------- End Instant metric input payload ----------------------

#------------------------ Widget API Traffic Summary ----------------------------
widget_api_traffic_summary_success_input_payload = {
    'full_input_payload': {
        'input': {
        "filter": [
        {
        "key": "devid",
        "value":"101F-A",
        "operation": "="
        }
        ],
        "start_date": "1633489659",
        "end_date": "1633489659"
        },
        'function_obj': full_payload_success_response_traffic_summary
    },'no_filter': {
        'input': {
        "start_date": "1633435526",
        "end_date": "1633435526"
        },
        'function_obj': success_no_filter_traffic_summary
    }
}
traffic_summary_failure_input_payload = {
    'invalid_start_date': {
        'input': {
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'invalid_end_date': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'start_date_greater': {
        'input': {
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'with_filter': {
        'input': {
            "filter": [
                {
                    "key": "device_id",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'with_sort_by': {
        'input': {
            "sort-by": [
                {

                }
            ],
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    }
}
# ----------------------- Widget API Traffic Summary End Here -------------------
# ----------------------- Widget API Bandwidth rate -----------------------------
widget_api_bandwidth_rate_success_input_payload = {
    'full_input_payload':{
        'input': {
            "filter": [
                {
                "key": "devid",
                "value": "101F-A",
                "operation": "="
                }
            ],
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': full_payload_success_response_bandwidth_rate
    },
    'no_filter': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': full_payload_success_response_bandwidth_rate
    }
}

bandwidth_rate_failure_input_payload = {
    'invalid_start_date': {
        'input': {
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'invalid_end_date': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'start_date_greater': {
        'input': {
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 'desc'
                }
            ],
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_limit': {
        'input': {
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': 'fortinet_common.APIService.post'
    }, 'send_wrong_filter_keys': {
        'input': {
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    }
}
# ------------------ Widget API Bandwidth rate ENDS HERE -----------------------
# ------------------ Widget API Site Details -----------------------
widget_api_site_details_success_input_payload = {
    'full_input_payload': {
        'input': {
            "device": [
                {
                    "devid": "All_Fortigate"
                }
            ],
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'function_obj_manager': success_response_manager_site_details,
        'function_obj_analyzer': success_response_analyzer_site_details
    },
    'no_device_input_payload': {
        'input': {
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'function_obj_manager': success_response_manager_site_details_no_device,
        'function_obj_analyzer': success_response_analyzer_site_details_no_device
    }
}

widget_api_site_details_failure_input_payload = {
    'send_wrong_filter_keys': {
        'input': {
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'invalid_start_date': {
        'input': {
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'invalid_end_date': {
        'input': {
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'start_date_greater': {
        'input': {
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'send_non_supported_filed_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "counts",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'send_non_supported_order_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "sessions",
                    "order": "wrong_order"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'limit_above_500': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'limit_below_1': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'invalid_limit': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "limit": 'a',
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_SITE_DETAILS
    },
    'invalid_metric_name': {
        'input': {
            "device": [
                {
                    "devid": "All_Fortigate"
                }
            ],
            "filter": "",
            "limit": 20,
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'function_obj_manager': validation_error,
        'function_obj_analyzer': validation_error,
        'function_obj_converter': bad_response_converter_site_details,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'metric_name': UNIT_TEST_BAD_METRIC_NAME
    }
}

widget_api_site_details_exception_input_payload = {
    'manager_not_reachable': {
        'input': {
            "device": [
                {
                    "devid": "All_Fortigate"
                }
            ],
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'function_obj_manager': exception_response_manager_site_details,
        'function_obj_analyzer': success_response_analyzer_site_details,
    },
    'analyzer_not_reachable': {
        'input': {
            "device": [
                {
                    "devid": "All_Fortigate"
                }
            ],
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'function_obj_manager': success_response_manager_site_details,
        'function_obj_analyzer': exception_response_analyzer_site_details
    }
}

def mock_get_all_site_for_users(self):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(all_site_for_user))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=all_site_for_user, original_response = response)  

def mock_get_all_device_data_for_users_(self=None, adoms_list=None, req_payload=None):
    return all_device_for_user

def sucess_get_all_site_for_users(self, url, params=None, **kwargs):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(all_site_for_user))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=all_site_for_user, original_response = response)  
# ------------------ END Widget API Site Details -----------------------

# ----------------------- Widget API Top application usage -----------------------------
widget_api_top_application_usage_success_input_payload = {
    'full_input_payload': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': full_payload_success_response_top_application_usage
    },
    'no_sort_by_success_response': {
        'input': {
            "limit": 1,
            "start_date": "1472636593",
            "end_date": "1630402993"
        },
        'function_obj': success_no_sort_by_top_application_usage
    },
    'no_filter': {
        'input': {
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_no_filter_top_application_usage,
    },
    'no_limit': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': success_no_limit_top_application_usage
    }
}

top_application_usage_failure_input_payload = {
    'invalid_start_date': {
        'input': {
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'invalid_end_date': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'start_date_greater': {
        'input': {
            "start_date": "1630474868",
            "end_date": "1472708468"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'limit_above_500': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': 'fortinet_common.APIService.post'
    },
    'limit_below_1': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {

                }
            ],
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': 'fortinet_common.APIService.post'
    },
    'send_non_supported_filed_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "counts",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_non_supported_order_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "sessions",
                    "order": "wrong_order"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    },
    'send_wrong_filter_keys': {
        'input': {
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_to_mock': ''
    }
}
# ------------------ Widget API Top application usage ENDS HERE -----------------------



# --------------------------- Widget API Top policy-hits ------------------------------

def success_top_policy_hits_integrator_response(self, adom_name=None, **req_payload):
    response = APIResponse(data=cloudsmaer_adom_response)
    return response


def success_top_application_usages_all_adom_integrator_response(self=None, adom_name=None, req_payload=None):
    if adom_name == "CloudSmartz":
        response = APIResponse(data=adom_cloud_firewall_response)
        return response
    if adom_name == "D-AND-D":
        response = APIResponse(data=adom_d_and_d_response)
        return response
    if adom_name == "FortiAnalyzer":
        response = APIResponse(data=adom_FortiAnalyzer_response)
        return response
    return APIResponse(data=None)


# ---------------------------End Widget API Top policy-hits ------------------------------


# ------------------ Widget API Top Users -----------------------
widget_api_top_users_success_input_payload = {
    'full_input_payload': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc"
                }
            ],
            "limit": 4,
            "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'integrator_response': top_users_converter_full_payload_response,
        'function_obj': full_payload_success_response_top_users,
        'final_integrator_response': top_users_integrator_response_full_payload
    },
    'no_limit': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc"
                }
            ],
            "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'integrator_response': top_users_converter_full_payload_response,
        'function_obj': full_payload_success_response_top_users,
        'final_integrator_response': top_users_integrator_response_full_payload
    }
}
widget_api_top_application_threats_failure_input_payload = {
    'no_sort_by': {
        'input': {
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_application_threats
    },
    'send_wrong_sort_by_field': {
        'input': {
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_application_threats
    },
    'send_wrong_sort_by_order': {
        'input': {
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc/desc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_application_threats
    },
    'send_wrong_filter_keys': {
        'input': {
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "sort-by": [{
                "field": "d_risk",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'no_key_in_filter': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_start_date': {
        'input': {
            "sort-by": [{
                "field": "d_risk",
                "order": "desc"
            }],
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_end_date': {
        'input': {
            "sort-by": [{
                "field": "d_risk",
                "order": "desc"
            }],
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'no_sort_by': {
        'input': {
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_non_supported_filed_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "filter": [
                {
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'limit_above_500': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'limit_below_1': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    },
    'invalid_limit': {
        'input': {
            "filter": [
                {
                    "key": "devid",
                    "value": "abc",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 'a',
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_converter_top_users
    }
}

widget_api_analyzer_exceptions_top_users = {
    'analyzer_not_reachable': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "limit": 4,
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_analyzer_not_reachable_top_users,
        'metric_name': UNIT_TEST_TOP_USERS
    },
    'analyzer_responded_with_error': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "bandwidth",
                "order": "desc"
            }],
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_converter_top_users,
        'metric_name': UNIT_TEST_TOP_USERS
    },
    'invalid_metric_name': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [
                {
                    "field": "bandwidth",
                    "order": "asc"
                }
            ],
            "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'analyzer_response': bad_response_converter_top_users,
        'metric_name': UNIT_TEST_BAD_METRIC_NAME
    }
}
widget_api_im_server_exceptions_top_sources_by_application = {
    'im_server_not_reachable': {
        'input': {
            "filter": [
                {
                    "key": "dstip",
                    "value": "*",
                    "operation": "="
                }
            ],
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_im_server_top_users
    }
}

# ------------------ Widget API Top Users ENDS HERE -----------------------

# ---------------------------End Widget API Risk Analysis ------------------------------
widget_api_risk_analysis_success_input_payload = {
    'full_input_payload': {
        'input': {
            "sort-by": [
                {
                    "field": "d_risk",
                    "order": "asc"
                }
            ],
            "limit": 4,
            "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'integrator_response': risk_analysis_full_payload_integrator_original_response,
        'function_obj': full_payload_success_response_risk_analysis,
        'final_integrator_response': risk_analysis_full_payload_integrator_response
    },
    'no_limit': {
        'input': {
            "sort-by": [
                {
                    "field": "d_risk",
                    "order": "asc"
                }
            ],
            "start_date": "1620717116",
            "end_date": "1626419516"
        },
        'integrator_response': risk_analysis_full_payload_integrator_original_response,
        'function_obj': full_payload_success_response_risk_analysis,
        'final_integrator_response': risk_analysis_full_payload_integrator_response
    }
}

widget_api_risk_analysis_failure_input_payload = {
    'filter_support': {
        'input': {
            "sort-by": [
                {
                    "field": "d_risk",
                    "order": "asc"
                }
            ],
            "filter": [
                {
                    "wrong_keys": "devids",
                    "wrong_values": "abc",
                    "wrong_operations": "="
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'invalid_start_date': {
        'input': {
            "start_date": "1623711600.987",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'invalid_end_date': {
        'input': {
            "start_date": "1623711600",
            "end_date": "1623844800.8974"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'sort_by_support': {
        'input': {
            "sort-by": [{
                "field": "threatweight",
                "order": "desc"
            }],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'send_non_supported_filed_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "counts",
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'send_non_supported_order_for_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": "sessions",
                    "order": "wrong_order"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'send_num_for_field_in_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": 222,
                    "order": "asc"
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'send_num_for_field_and_order_in_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": 222,
                    "order": 222
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'send_num_for_order_in_sort_by': {
        'input': {
            "sort-by": [
                {
                    "field": 'session_pass',
                    "order": 333
                }
            ],
            "limit": 1,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'limit_above_500': {
        'input': {
            "limit": 600,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'limit_below_1': {
        'input': {
            "limit": 0,
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
    'invalid_limit': {
        'input': {
            "limit": 'a',
            "start_date": "1623711600",
            "end_date": "1623844800"
        },
        'function_obj_analyzer': validation_error,
        'expected_status': EXPECTED_BAD_REQUEST_STATUS,
        'function_obj_converter': bad_response_analyzer_risk_analysis
    },
}

widget_api_analyzer_exceptions_risk_analysis = {
    'analyzer_not_reachable': {
        'input': {
            "limit": 4,
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_analyzer_not_reachable,
        'metric_name': UNIT_TEST_RISK_ANALYSIS
    },
    'analyzer_responded_with_error': {
        'input': {
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_analyzer_risk_analysis,
        'metric_name': UNIT_TEST_RISK_ANALYSIS
    },
    'invalid_metric_name': {
        'input': {
            "start_date": "1466196393",
            "end_date": "1630442793"
        },
        'analyzer_response': bad_response_analyzer_risk_analysis,
        'metric_name': UNIT_TEST_BAD_METRIC_NAME
    }
}

# ---------------------------End Widget API Risk Analysis ------------------------------
# --------------------------------site - map -------------------------------------------
def mock_data_all_site_device_data_site_map(self=None, adoms_list=None, req_payload=None):
    return all_site_device_data 

def mock_data_get_site_for_user(self=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(all_site_map))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=all_site_map, original_response=response)
 
def mock_function_get_device_by_id(self, adom_name, device_id=None):
    response = Response()
    response.status_code= 200 
    response._content = str.encode(js.dumps(manager_d_and_d_response))
    return APIResponse(data= manager_d_and_d_response, original_response =response )

def  mock_function_site_details_event_management(self=None, adom_name=None, **req_payload):
    response = Response()
    response.status_code= 200 
    response._content = str.encode(js.dumps(analyzer_d_and_d_data))
    return APIResponse(data= analyzer_d_and_d_data, original_response = response)
    
def mock_get_site_for_user():
    response = Response()
    response.status_code= 200 
    response._content = str.encode(js.dumps(analyzer_d_and_d_data))
    return APIResponse(data= analyzer_d_and_d_data, original_response = response)

def mock_data_get_site_for_use_site_map(self, url, params=None, **kwargs):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(all_site_map))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=all_site_map, original_response=response)

def mock_data_host_unreachable_site_map(self):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(host_not_reachable))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=host_not_reachable,
                        original_response=response)
    return response

def mock_manager_data_host_unreachable_site_map(self,device_id=None,adom_name=None):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(host_not_reachable))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=host_not_reachable,
                        original_response=response)
    return response

def mock_analyzer_data_host_unreachable_site_map(self):
    response = Response()
    response.status_code = 500
    response._content = str.encode(js.dumps(host_not_reachable))
    response._content_consumed = True
    response.encoding = 'utf-8'
    response = APIResponse(data=host_not_reachable,
                        original_response=response)
    return response

def mock_data_all_site_device_up_site_check_site_map(self=None, adoms_list=None, req_payload=None):
    return status_run 

def mock_data_check_status_up_get_site_for_user(self=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(site_analyzer_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=site_analyzer_response, original_response=response)

def expected_result(i):  
    ip_list = ['66.95.209.44','47.220.185.118','195.143.129.106']
    return all_site_device_data[0].get(ip_list[i]).get('connection_status')


# ------------------------------End site - map -----------------------------------------


#------------------ Widget API Top application usage ENDS HERE -----------------------

#-----------------------------------SD WAN--------------------------------------
def mock_sd_wan_uasages(self, req_payload, adom_name=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(sd_wan_all_adom_analyzer_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=sd_wan_all_adom_analyzer_response, original_response= response)

#-----------------------------------END SD WAN--------------------------------------

def success_create_report(self=None, req_payload=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(create_report_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=create_report_response, original_response=response)

def success_download_report(self=None,tid=None,req_payload=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(download_report_reponse))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=download_report_reponse, original_response=response)

def success_delete_report(self=None,tid=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(delete_report_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=delete_report_response, original_response=response)

def success_list_report(self=None,req_payload=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(list_report_reponse))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=list_report_reponse, original_response=response)
# ------------------------ System status -------------------------------------

def success_response_from_system_status(self=None, adom_name=None,device_name=None):
    response = APIResponse(data=service_system_status_response)
    return response

def bad_response_from_system_status(self=None, adom_name=None, device_name=None):
    response = APIResponse(data=service_system_status_for_badresponse)
    return response

def bad_deviceid_response_from_system_status(self=None, adom_name=None, device_name=None):
    response = APIResponse(data=service_system_status_wrongadom_name_response)
    return response
#------------------------------- Bandwidth Summary API --------------------------------- #

def mock_get_system_monitor_data(self, adom_name, device_id):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(manager_sys_monitor_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=manager_sys_monitor_response, original_response=response)

def mock_virtual_wan_healthchk_data(self, adom_name, device_id):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(manager_virtual_wan_healthchk_response))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=manager_virtual_wan_healthchk_response, original_response=response)


def mock_get_device_by_id(self, adom_name, device_id=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(manager_response_bandwidth_summary))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=manager_response_bandwidth_summary, original_response=response)

def mock_get_device_interface_logs(self, device_id, interface_filter_value= None, **req_payload):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(manager_response_bandwidth_summary))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=None, original_response=response)

#--------------------Report List--------------------#
def success_list_reports(self=None, req_payload=None):
    response = Response()
    response.status_code = 200
    response._content = str.encode(js.dumps(final_response_report_list))
    response._content_consumed = True
    response.encoding = 'utf-8'
    return APIResponse(data=final_response_report_list, original_response=response)

def invalid_matric_name_list_reports(end=None):
    return None

def report_list_by_title_report_list(self, adom_name, **req_payload):
    response = Response()
    response.status_code = 200
    response._content =str.encode(js.dumps(integrator_final_response))
    response.encoding = 'utf-8'
    return APIResponse(data =integrator_final_response, original_response=response)

def wrong_adom_name_report_list(self, adom_name, **req_payload):
    response = Response()
    response.status_code = 500
    response._content =str.encode(js.dumps(host_responded_with_error))
    response.encoding = 'utf-8'
    return APIResponse(data =host_responded_with_error, original_response=response)

def integrator_report_list(self, adom_name, **req_payload):
    response = Response()
    response.status_code = 200
    response._content =str.encode(js.dumps(integrator_response_report_list))
    response.encoding = 'utf-8'
    return APIResponse(data =integrator_response_report_list, original_response=response)


def report_list_integrator_response():
    response = Response()
    response.status_code = 200
    response._content =str.encode(js.dumps(integrator_response_report_list))
    response.encoding = 'utf-8'
    return APIResponse(data =integrator_response_report_list, original_response=response)

#--------------------Report List--------------------#

def patch_adom_all_devices(*args, **kwargs):
    response = APIResponse(data=adom_devices_by_id_integrator_response)
    response.status = 200
    return response

def patch_system_status_by_deviceid(*args, **kwargs):
    response = APIResponse(data=service_system_status_response)
    response.status = 200
    return response

def patch_adom_all_devices(*args, **kwargs):
    response = APIResponse(data=adom_devices_by_id_final_response)
    response.status = 200
    return response

def patch_metric_response(*args, **kwargs):
    response = APIResponse(data=metric_classifiers_and_data_response)
    response.status = 200
    return response

def patch_get_adom_device_report_response(*args, **kwargs):
    response = APIResponse(data=metric_classifiers_and_data_response)
    response.status = 200
    return response

def mock_get_adom_device_permission_function_response(self, auth_token, scope_rsname=None):
    return ('FAI_GET_ADOM_DEVICE')

def mock_get_system_status_permission_function_response(self, auth_token, scope_rsname=None):
    return ('FAI_GET_SYSTEM_STATUS')

def mock_metric_permission_function_response(self, auth_token, scope_rsname=None):
    return ('FAI_GET_METRICS')

def mock_get_adom_device_report_permission_function_response(self, auth_token, scope_rsname=None):
    return ('FAI_GET_ADOM_DEVICE_REPORT')

def mock_bad_permission_response(self, auth_token, scope_rsname=None):
    return ('Without_permission')

def patch_response_from_system_status(self, *args,**kwargs):
    response = APIResponse(data=integrator_system_status_response)
    response.status = 200
    return response

def mock_adom_get_clients_of_user(self,*args,**kwars):
    response = APIResponse(data=clients_for_users_response)
    response.status = 200
    return response

def patch_adom_all_devices_function(self,*args,**kwargs):
    response = APIResponse(data=integrator_adom_device_reponse)
    response.status = 200
    return response

def patch_devices_list_function(self,*args,**kwargs):
    response = APIResponse(data=devices_list_response)
    response.status = 200
    return response

def patch_system_status_response(self,*args,**kwargs):
    response = APIResponse(data=integrator_system_status_response)
    response.status = 200
    return response

def devices_list_response(self,*args,**kwargs):
    response = APIResponse(data=devices_response)
    response.status = 200
    return response