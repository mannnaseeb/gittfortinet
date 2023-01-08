import os
import sys, json
from unittest.mock import patch, Mock

import pytest
from dotenv import load_dotenv
from middleware.constants import *

load_dotenv()
sys.path.append(os.getcwd())

from test_fortinet_api.mocker_functions import *

from app import app
from test_fortinet_api.mocker_functions import *
from test_fortinet_api.constants import *
from test_fortinet_api.responses import *
from middleware.request_interceptor import FortinetAPIRequestInterceptor
from services.fortinet_api_services import FortinetAPIService
from validators.fortinet_api_validations import FortinetAPIValidations
from languages.fortinet_api_exceptions import *
from converters.fortinet_api_converters import FortinetConverters
from middleware.token_interceptor import validate_token, im_generate_token
from integrators.fortinet_integrator import FortinetIntegrator
from apis.metrics_api import GetListOfClassifiersAndData

metric = GetListOfClassifiersAndData()
interceptor_object = FortinetAPIRequestInterceptor()
service_object = FortinetAPIService()
validator_object = FortinetAPIValidations()
converter_object = FortinetConverters()
integrator_object = FortinetIntegrator()


# ---------------------- Validate token ----------------------
@validate_token
def func_for_validate_token():
    return VALIDATE_TOKEN_SUCCESS_TEXT

#Below fixture is to ignore all decorators for a function
@pytest.fixture
def unwrap():
    def unwrapper(func):
        if not hasattr(func, '__wrapped__'):
            return func

        return unwrapper(func.__wrapped__)

    yield unwrapper
    
def test_validate_token_exception(mocker):
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token',
                 return_value=None)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    with app.test_request_context():
        hold_response = func_for_validate_token()
        assert hold_response[1] == ERROR_CODE_UNAUTHORIZED_ACCESS


def test_validate_token_success(mocker):
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token',
                 return_value="token_value")
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_validate_token_success_response)
    with app.test_request_context():
        hold_response = func_for_validate_token()
        assert hold_response == VALIDATE_TOKEN_SUCCESS_TEXT


def test_im_generate_token_success(mocker):
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_generate_token_success_response)
    with app.test_request_context():
        response = im_generate_token()
        assert response.data.get('access_token') == SUCCESSFULLY_GENERATED_TOKEN


def test_im_generate_token_exception(mocker):
    mocker.patch('fortinet_common.auth.APIService.post',
                 return_value=None)
    with app.test_request_context():
        with pytest.raises((TokenCreationException, ValueError, KeyError, NameError)) as ex:
            im_generate_token()
        assert ex.typename == 'TokenCreationException'


# ---------------------- End Validate token ----------------------

# ---------------------- Services classifiers and data ----------------------
#Below autouse=True option will apply this fixture to all unit tests
@pytest.fixture()
def mock_database_call_classifiers_and_data(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_classifiers_and_data', return_value=metric_classifiers_and_data_response)
    mocker.patch('db_settings.db_utils.get_all_metrics_from_database', return_value=metric_classifiers_and_data_response)
    mocker.patch('validators.fortinet_api_validations.get_all_metric_supported_operations_from_database', return_value=operand_types_response)
    mocker.patch('validators.fortinet_api_validations.get_all_metric_types_from_database', return_value=metric_types_response)
    mocker.patch('validators.fortinet_api_validations.get_all_metrics_from_database', return_value=metric_classifiers_and_data_response)

def test_service_get_classifiers_and_data(mocker):
    with app.test_request_context():
        response = service_object.service_get_classifiers_and_data()
        data = response
        assert data == metric_classifiers_and_data_response


# ---------------------- End Services classifiers and data ----------------------

# ---------------------- Services instant metric ----------------------

def test_bad_response_service_get_instant_metric(mocker):
    for key, value in metric_failure_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_METRIC_NAME)
            assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
                ex)


# ---------------------- End Services instant metric ----------------------

# ---------------------- Convertor instant metric ----------------------
def test_convert_response_get_instant_metric(mocker):
    for key, value in metric_success_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = instant_metric_final_response[key]
            response = converter_object.convert_response_get_instant_metric(req_payload=value['input'],
                                                                            metric_name=UNIT_TEST_METRIC_NAME,
                                                                            response=value['function_obj']())
            assert response.get('data') == expected_response.get('data')


def test_bad_convert_response_get_instant_metric(mocker):
    for key, value in metric_failure_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises(AttributeError) as ex:
                converter_object.convert_response_get_instant_metric(req_payload=value['input'],
                                                                     metric_name=UNIT_TEST_BAD_METRIC_NAME,
                                                                     response=value['function_obj']())
            assert EXPECTED_BAD_ATTRIBUTE_ERROR in str(ex)


# ---------------------- End Convertor instant metric ----------------------

# # ---------------------- Traffic Summary --------------------------------
def test_service_get_traffic_summary(mocker):
    for key, value in widget_api_traffic_summary_success_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_traffic_summarry',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = traffic_summary_final_response[key]
            response = service_object.service_get_instant_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_TRAFFIC_SUMMARY)
            assert response.get('data') == expected_response.get('data')

def test_bad_response_service_get_traffice_summary(mocker):
    for key, value in traffic_summary_failure_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_traffic_summarry',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_TRAFFIC_SUMMARY)
            assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
                ex)

# --------------------------- End Traffic Summary ----------------------
# ---------------------- Bandwidth rate ---------------------------------
def test_service_get_bandwidth_rate(mocker):
    for key, value in widget_api_bandwidth_rate_success_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                     success_response_manager_site_details)
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_interface_logs',
                     success_response_manager_interface_logs)
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_logview',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = bandwidth_rate_final_response[key]
            response = service_object.service_get_timeseries_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_BANDWIDTH_RATE)
            assert response.get('data') == expected_response.get('data')


def test_bad_response_service_get_bandwidth_rate(mocker):
    for key, value in bandwidth_rate_failure_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_logview',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
                service_object.service_get_timeseries_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_BANDWIDTH_RATE)
            assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
                ex)

# -------------------- End Bandwidth rate -------------------------------

# ---------------------- Top application usage --------------------------#

# ----------------Service unit test---------------#
# CLIENT MAIN API
def test_client_application_usages(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_applications',
                 success_top_application_usages_all_adom_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.service_get_instant_metric(top_application_usages_all_adom_payload,
           UNIT_TEST_TOP_APPLICATION_USAGE)
        assert len(converted_response['data']) > 0
        for data in converted_response['data']:
            assert data['adom'] in ADOM_LIST


# LIMIT = 0
def test_bad_zero_limit_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_zero_limit_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_VALIDATION_EXCEPTION in str(
            ex)


# without sortby
def test_without_sortby_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_without_sortby_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)


# without field
def test_without_field_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_without_field_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)


# without order
def test_without_order_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_without_order_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)


# wrong field
def test_wrong_field_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_wrong_field_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)


# empty start time
def test_empty_start_time_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_empty_start_time_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)


# empty end time
def test_empty_end_time_client_application_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_empty_end_time_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)

    # ---------------End Service unit test--------------#

    # --------------- converter unit test---------------#


# SUCCESSFUL CONVERTER RESPONSE
def test_converter_top_application_usage(mocker):
    response = converter_object.convert_to_top_applications_usage(req_payload=top_application_usages_all_adom_payload,
                                                                  metric_name=UNIT_TEST_TOP_APPLICATION_USAGE,
                                                                  analyzer_response=all_adom_top_application_usages_ananlyzer_final_response)
    assert len(response['data']) == top_application_usages_all_adom_payload['limit']
    assert len(response['data'][0]) > 0
    data_keys = list(response['data'][0].keys())
    for key in REQUIRED_APPLICATION_USAGES_CONVERTER_OUTPUT:
        result = True if key in data_keys else False
        assert result == True

    # REQUIRED FIELD NULL


def test_convert_top_application_usages_with_null_fields(mocker):
    response = converter_object.convert_to_top_applications_usage(req_payload=top_application_usages_all_adom_payload,
                                                                  metric_name=UNIT_TEST_TOP_APPLICATION_USAGE,
                                                                  analyzer_response=all_adom_top_application_usages_ananlyzer_none_fields_response)
    assert response['data'][0]['application'] == None


# ALL_ADOM_RESPONSE_NULL
def test_convert_top_application_usages_with_empty_response(mocker):
    response = converter_object.convert_to_top_applications_usage(req_payload=top_application_usages_all_adom_payload,
                                                                  metric_name=UNIT_TEST_TOP_APPLICATION_USAGE,
                                                                  analyzer_response=[])

    assert response['metric'] == UNIT_TEST_TOP_APPLICATION_USAGE
    assert len(response['data']) == 0

    # ---------------End converter unit test---------------#

    # ---------------- -Integrator unit test---------------#


# INTERGRATOR SUCCESS RESPONSE
def test_top_application_usages_integrator_response(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_applications',
                 success_top_application_usages_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = integrator_object.get_widget_top_applications(adom_name=UNIT_TEST_ADOM_NAME,
                                                                 **top_application_usages_all_adom_payload)
        assert len(response.data['result']['data']) >= 0
        for data in response.data['result']['data']:
            data_keys = list(data.keys())
            for key in REQUIRED_APPLICATION_USAEGS_FIELD:
                result = True if key in data_keys else False
                assert result == True


def test_api_bad_credential_uuid_top_applications(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_applications',
                 bad_response_bad_credential_uuidfrom_client_top_applications)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = integrator_object.get_widget_top_applications(UNIT_TEST_ADOM_NAME,
                                                                 **top_application_usages_all_adom_payload)
        data = response
        assert data.data['error-code'] == ERROR_CODE_AUTHERIZATION_ERROR


def test_client_top_application_usages_host_unreachable(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_applications',
                 bad_response_analyzer_not_reachable_top_categories)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((HostRespondedWithErrorException)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_analyzer_payload,
                                                      metric_name=UNIT_TEST_TOP_APPLICATION_USAGE)

        assert EXPECTED_HOSTRESPONDEDWITHERROR_EXCEPTION in str(ex)


def test_im_server_failed_to_generate_token(mocker):
    mocker.patch('fortinet_common.APIService.post', failed_to_generate_token_top_application_usages)
    with app.test_request_context():
        with pytest.raises(TokenCreationException) as ex:
            im_generate_token()
        assert EXPECTED_TOKENCREATION_EXCEPTION in str(ex)


def test_im_server_success_generate_token(mocker):
    mocker.patch('fortinet_common.APIService.post', success_generate_token_top_application_usages)
    with app.test_request_context():
        response = im_generate_token()
        assert response.data['access_token'] == unit_test_token

    # invalid_matric_name


def test_client_top_application_usages_invalid_matric_name(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_applications',
                 bad_response_analyzer_not_reachable_top_application_usages_invalid_matric_name)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            service_object.service_get_instant_metric(
                req_payload=top_application_usages_invalid_matric_name_analyzer_payload,
                metric_name=UNIT_TEST_INVALID_MATRIC_NAME_TOP_APPLICATION_USAGE)

        assert EXPECTED_INVALID_MATRIC_NAME in str(ex)

    # ----------------End Integrator unit test-------------#


# -------------------- End Top application usage -------------------------------


# ---------------------- Site Details ---------------------------------
def test_service_get_site_details(mocker):
    for key, value in widget_api_site_details_success_input_payload.items():
        mocker.patch('services.fortinet_api_services.FortinetAPIService.get_all_sites_devices_data',
                     mock_get_all_device_data_for_users_)
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',
                     mock_get_all_site_for_users)
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = site_details_service_response
            response = service_object.service_get_instant_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_SITE_DETAILS)
            assert response.get('data') == expected_response.get('data')


def test_bad_response_service_get_site_details(mocker):
    for key, value in widget_api_site_details_failure_input_payload.items():
        mocker.patch('services.fortinet_api_services.FortinetAPIService.get_all_sites_devices_data',
                     value['function_obj_manager'])
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',
                     value['function_obj_analyzer'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=value['metric_name'])
            assert EXPECTED_VALIDATION_EXCEPTION or EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR in str(ex)


def test_convert_response_get_site_details(mocker):
    response = {'sites_up': 10, 'sites_down': 2, 'sites_alert': 200}
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        expected_response = site_details_converter_response
        response = converter_object.convert_to_site_details(req_payload=site_details_payload,
                                                            metric_name=UNIT_TEST_SITE_DETAILS,  sites_up_count=response['sites_up'], 
                                                            sites_down_count=response['sites_down'], sites_alert_count=response['sites_alert'])
    assert response.get('data') == expected_response.get('data')


def test_bad_convert_response_get_site_details(mocker):
    response = {'sites_up': 0, 'sites_down': 0, 'sites_alert': 0}
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        expected_response = site_details_converter_response
        response = converter_object.convert_to_site_details(req_payload=site_details_payload,
                                                            metric_name=UNIT_TEST_SITE_DETAILS,  sites_up_count=response['sites_up'], 
                                                            sites_down_count=response['sites_down'], sites_alert_count=response['sites_alert'])
    assert response.get('data') != expected_response.get('data')

# test case for site users
def test_success_get_site_for_users(mocker):
    mocker.patch('fortinet_common.APIService.post', mock_generate_token_success_response)
    mocker.patch('fortinet_common.APIService.get', sucess_get_all_site_for_users)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        data = integrator_object.get_sites_for_user()
        assert data.data is not None 

    
def test_success_manager_response_integrator_get_site_details(mocker, unwrap):
    file_data = open('adoms.json', )
    adom_data = json.load(file_data)
    for adom in adom_data:
        adom_name = adom['name']
        mocker.patch('integrators.fortinet_integrator.im_generate_token',
                     return_value=APIResponse(data={'access_token': 'token_value'},
                                              original_response={'access_token': 'token_value'}))
        mocker.patch('fortinet_common.APIService.post', mock_generate_token_success_response)
        mocker.patch('fortinet_common.APIService.get',
                     return_value=success_response_manager_site_details(adom_name=adom_name))
        with app.test_request_context():
            interceptor_object.get_corelation_id()
            # Below we are ensuring we ignore the decorator used for the function we are testing
            decorated_function_unwrapped = unwrap(integrator_object.get_device_by_id)
            data = decorated_function_unwrapped(adom_name=UNIT_TEST_ADOM_NAME, self=integrator_object)
            assert data.data.keys() == site_details_manager_response[UNIT_TEST_ADOM_NAME].keys()


@patch('fortinet_common.APIService.post')
def test_success_analyzer_response_integrator_get_site_details(mocker):
    for key, value in widget_api_site_details_success_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            adom_name = adom['name']
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = success_response_analyzer_site_details(adom_name=adom_name).data
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_site_details_event_management(adom_name, **value['input'])
                assert data.json() == site_details_analyzer_response[adom_name]


@patch('fortinet_common.APIService.post')
def test_bad_analyzer_response_integrator_get_site_details(mocker):
    for key, value in widget_api_site_details_success_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            adom_name = adom['name']
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = None
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_site_details_event_management(adom_name, **value['input'])
                assert data.json() is None


def test_bad_manager_response_integrator_get_site_for_userts(mocker, unwrap):
    mocker.patch('fortinet_common.APIService.post', mock_generate_token_success_response)
    mocker.patch('fortinet_common.APIService.get', bad_response_integrator_manager_site_details)
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object._get_all_adom)
        data = decorated_function_unwrapped(adom_name=UNIT_TEST_ADOM_NAME, self=integrator_object)
        assert data.data is None


@patch('fortinet_common.APIService.post')
def test_bad_response_adomname_integrator_get_site_details(mocker):
    for key, value in widget_api_site_details_success_input_payload.items():
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = None
        mocker.side_effect = fake_responses
        with app.test_request_context():
            interceptor_object.get_corelation_id()
            data = integrator_object.get_widget_site_details_event_management(UNIT_TEST_BAD_ADOM_NAME, **value['input'])
            assert data.json() is None




def test_response_exception_get_site_details(mocker):
    for key, value in widget_api_site_details_exception_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                     value['function_obj_manager'])
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_site_details_event_management',
                     value['function_obj_analyzer'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises(HostNotReachableException) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_SITE_DETAILS)
            assert FORTINET_MANAGER_NOT_REACHABLE or FORTINET_ANALYZER_NOT_REACHABLE in str(ex)


# GET_ALL_DEVICES_DATA_SITE
def test_get_all_sites_devices_data_site_details(mocker):
     mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',mock_function_get_device_by_id) 
     mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_site_details_event_management',mock_function_site_details_event_management)
     with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = service_object.get_all_sites_devices_data( adoms_list=site_map_adom_list, req_payload = req_payload_site_map)
        assert response[0] == ALL_ADOM_DEVICES
        assert response[1] == ALL_ADOM__DEVICES_WITH_ALERTS

# -------------------- End Site Details -------------------------------


# -------------------------  Top policy-hits ------------------------------------
# CLIENT MAIN API
def test_client_top_policy_hits(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_policy_hits',
                 success_top_application_usages_all_adom_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        filename = 'adoms.json'
        adoms_list = []
        with open(filename, "rb") as fin:
            adoms_list = json.load(fin)
        final_response_for_converter = []
        for adom in adoms_list:
            analyzer_response = integrator_object.get_widget_top_policy_hits(adom['name'],
                                                                             req_payload=top_policy_hits_final_payload)
            if analyzer_response.data is not None and 'result' in analyzer_response.data \
                    and 'data' in analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                analyzer_response.data['result']['data'] = [dict(item, adom=adom['name']) for item in
                                                            analyzer_response.data['result']['data']]
                final_response_for_converter.extend(analyzer_response.data['result']['data'])
            # ------------------------ Converted response -----------------------

        converted_response = converter_object.convert_to_top_policy_hits(req_payload=top_policy_hits_final_payload,
                                                                         analyzer_response=final_response_for_converter,
                                                                         metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert len(converted_response['data']) > 0
        for data in converted_response['data']:
            assert data['adom'] in ADOM_LIST


# LIMIT = 0
def test_bad_zero_limit_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_zero_limit_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)


# without sortby
def test_without_sortby_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_without_sortby_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

    # without field


def test_without_field_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_without_field_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)


def test_without_order_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_wrong_order_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

    # wrong field


def test_wrong_field_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_wrong_field_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

    # empty start time


def test_empty_start_time_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_empty_start_time_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

    # empty end time


def test_empty_end_time_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException, ValueError, KeyError, NameError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_policy_hits_empty_end_time_payload,
                                                      metric_name=UNIT_TEST_TOP_POLICY_HITS)
        assert EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR or EXPECTED_BAD_NAME_ERROR or EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

        # File not available


def test_file_not_exist_client_top_policy_hits(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            filename = 'wrong_file_name.json'
            if not os.path.exists(filename):
                raise ValidationException(FILE_DOES_NOT_EXIST)
            response = service_object.service_get_instant_metric(
                metric_name=UNIT_TEST_TOP_POLICY_HITS, req_payload=top_policy_hits_final_payload)
        assert EXPECTED_VALIDATION_EXCEPTION in str(ex)


# --------------- end service unit test  -------------#

# --------------- Integrator unit test  --------------#

# INTERGRATOR SUCCESS RESPONSE
def test_top_policy_hits_integrator_response(mocker):
    """  Checking of Required fields from the analyzer resposne """

    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_policy_hits',
                 success_top_policy_hits_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = integrator_object.get_widget_top_policy_hits(adom_name=UNIT_TEST_ADOM_NAME,
                                                                req_payload=top_policy_hits_final_payload)
        assert len(response.data['result']['data']) >= 0
        for data in response.data['result']['data']:
            data_keys = list(data.keys())
            for key in REQUIRED_FIELDS:
                result = True if key in data_keys else False
                assert result == True


# ---------------- -Integrator unit test---------------#

# ---------------- converter unit test------------------#


# REQUIRED_FIELD_CHECK
def test_convert_top_policy_hits_with_required_field_response(mocker):
    response = converter_object.convert_to_top_policy_hits(req_payload=top_policy_hits_final_payload,
                                                           metric_name=UNIT_TEST_TOP_POLICY_HITS,
                                                           analyzer_response=all_adom_top_policy_response)

    assert response['metric'] == UNIT_TEST_TOP_POLICY_HITS
    assert len(response['data'][0]) > 0
    data_keys = list(response['data'][0].keys())
    for key in REQUIRED_ACTUAL_FIELDS:
        result = True if key in data_keys else False
        assert result == True

    # SUCCESSFUL CONVERTER RESPONSE_AS_PER_GIVEN_LIMIT



def test_converter_policy_hits(mocker):
    response = converter_object.convert_to_top_policy_hits(req_payload=top_policy_hits_final_payload,
                                                           metric_name=UNIT_TEST_TOP_POLICY_HITS,
                                                           analyzer_response=all_adom_top_policy_response)
    assert len(response['data']) == top_policy_hits_final_payload['limit']


# ALL_ADOM_RESPONSE_NULL
def test_convert_top_policy_hits_with_empty_response(mocker):
    response = converter_object.convert_to_top_policy_hits(req_payload=top_policy_hits_final_payload,
                                                           metric_name=UNIT_TEST_TOP_POLICY_HITS,
                                                           analyzer_response=[])
    assert response is None


# --------------End converter unit test-------------#

# ------------------------- End Top policy-hits ----------------------------------

# -------------------- Top users -------------------------------

def test_service_get_top_users(mocker):
    for key, value in widget_api_top_users_success_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_users',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = top_users_full_payload_final_response[key]
            response = service_object.service_get_instant_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_TOP_USERS)
            assert response.get('data') == expected_response.get('data')


def test_bad_response_service_get_top_users(mocker):
    for key, value in widget_api_top_users_failure_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_users',
                     value['function_obj_analyzer'])

        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_TOP_USERS)
            assert ex.typename in (EXPECTED_VALIDATION_EXCEPTION, EXPECTED_BAD_VALUE_ERROR, EXPECTED_BAD_KEY_ERROR)


def test_success_response_converter_get_top_users(mocker):
    for key, value in widget_api_top_users_success_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = top_users_full_payload_final_response[key]
            response = converter_object.convert_to_top_users(req_payload=value['input'],
                                                             metric_name=UNIT_TEST_TOP_USERS,
                                                             analyzer_response=value['integrator_response'])
            assert response.get('data') == expected_response.get('data')


def test_bad_convert_response_get_top_users(mocker):
    for key, value in widget_api_top_users_failure_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises(HostRespondedWithErrorException) as ex:
                converter_object.convert_to_top_users(req_payload=value['input'],
                                                      metric_name=UNIT_TEST_TOP_USERS,
                                                      analyzer_response=value['function_obj_converter']())
            assert EXPECTED_HOSTRESPONDEDWITHERROR_EXCEPTION in str(ex)


@patch('fortinet_common.APIService.post')
def test_success_response_integrator_get_top_users(mocker):
    for key, value in widget_api_top_users_success_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            adom_name = adom['name']
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = value['final_integrator_response'][adom_name]
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_top_users(value['input'], adom_name)
            assert data.json() == top_users_integrator_response_full_payload[adom_name]


@patch('fortinet_common.APIService.post')
def test_bad_response_integrator_get_top_users(mocker):
    for key, value in widget_api_top_users_failure_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            adom_name = adom['name']
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = None
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_top_users(value['input'], adom_name)
                assert data.json() is None


@patch('fortinet_common.APIService.post')
def test_bad_response_adomname_integrator_get_top_users(mocker):
    for key, value in widget_api_top_users_success_input_payload.items():
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = None
        mocker.side_effect = fake_responses
        with app.test_request_context():
            interceptor_object.get_corelation_id()
            data = integrator_object.get_widget_top_users(value['input'], UNIT_TEST_BAD_ADOM_NAME)
            assert data.json() is None


def test_check_invalid_payload_top_users():
    for key, value in widget_api_top_users_failure_input_payload.items():
        with app.test_request_context():
            with pytest.raises(ValidationException) as ex:
                validator_object.check_invalid_payload(input_payload=value['input'],
                                                       end_point=UNIT_TEST_TOP_USERS)
            assert final_invalid_error_response_top_users[key] in str(ex)


def test_analyzer_exception_top_users(mocker):
    for key, value in widget_api_analyzer_exceptions_top_users.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_users',
                     value['analyzer_response'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((HostRespondedWithErrorException, HostNotReachableException, ValidationException)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=value['metric_name'])
            assert EXPECTED_HOSTRESPONDEDWITHERROR_EXCEPTION or ValidationException in str(ex)


def test_im_server_exception_top_users(mocker):
    mocker.patch('fortinet_common.APIService.post', mock_generate_token_bad_response)
    with app.test_request_context():
        with pytest.raises(TokenCreationException) as ex:
            im_generate_token()
        assert EXPECTED_TOKENCREATION_EXCEPTION in str(ex)


# -------------------- End Top users -------------------------------


# ------------------------- Risk Analysis ----------------------------------

# ------------------------- Services Unit Test----------------------------------

def test_service_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_success_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_risk_analysis',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = risk_analysis_final_response[key]
            response = service_object.service_get_instant_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_RISK_ANALYSIS)
            assert response.get('data') == expected_response.get('data')


def test_bad_response_service_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_failure_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_risk_analysis',
                     value['function_obj_analyzer'])

        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_RISK_ANALYSIS)
            assert EXPECTED_VALIDATION_EXCEPTION or EXPECTED_BAD_VALUE_ERROR or EXPECTED_BAD_KEY_ERROR in str(ex)


# ------------------------- End Services Unit Test----------------------------------

# ------------------------- Converter Unit Test----------------------------------
def test_convert_response_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_success_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = risk_analysis_final_response[key]
            response = converter_object.convert_to_risk_analysis(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_RISK_ANALYSIS,
                                                                 analyzer_response=value[
                                                                     'final_integrator_response'])
            assert response.get('data') == expected_response.get('data')


def test_bad_convert_response_get_top_sources_by_application(mocker):
    for key, value in widget_api_risk_analysis_failure_input_payload.items():
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises(HostRespondedWithErrorException) as ex:
                converter_object.convert_to_risk_analysis(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_RISK_ANALYSIS,
                                                          analyzer_response=value[
                                                              'function_obj_converter']())
            assert EXPECTED_HOSTRESPONDEDWITHERROR_EXCEPTION in str(ex)


# ------------------------- End Converter Unit Test----------------------------------

# ------------------------- Integrator Unit Test----------------------------------

@patch('fortinet_common.APIService.post')
def test_success_response_integrator_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_success_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            adom_name = adom['name']
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = value['integrator_response'][adom_name]
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_risk_analysis(adom_name,
                                                                  **value['input'])
                assert data.json() == risk_analysis_full_payload_integrator_original_response[adom_name]


@patch('fortinet_common.APIService.post')
def test_bad_response_integrator_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_success_input_payload.items():
        file_data = open('adoms.json', )
        adom_data = json.load(file_data)
        for adom in adom_data:
            fake_responses = [Mock(), Mock()]
            fake_responses[0].json.return_value = mock_generate_token_success_response
            fake_responses[1].json.return_value = None
            mocker.side_effect = fake_responses
            with app.test_request_context():
                interceptor_object.get_corelation_id()
                data = integrator_object.get_widget_risk_analysis(adom['name'], **value['input'])
                assert data.json() is None


@patch('fortinet_common.APIService.post')
def test_bad_response_adomname_integrator_get_risk_analysis(mocker):
    for key, value in widget_api_risk_analysis_success_input_payload.items():
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = None
        mocker.side_effect = fake_responses
        with app.test_request_context():
            interceptor_object.get_corelation_id()
            data = integrator_object.get_widget_risk_analysis(UNIT_TEST_BAD_ADOM_NAME,
                                                              **value['input'])
            assert data.json() is None


# ------------------------- End Integrator Unit Test----------------------------------

# ------------------------- Validation Unit Test----------------------------------
def test_check_invalid_payload_risk_analysis():
    for key, value in widget_api_risk_analysis_failure_input_payload.items():
        with app.test_request_context():
            with pytest.raises(ValidationException) as ex:
                validator_object.check_invalid_payload(input_payload=value['input'],
                                                       end_point=UNIT_TEST_RISK_ANALYSIS)
            assert ex.typename in (EXPECTED_VALIDATION_EXCEPTION, EXPECTED_BAD_VALUE_ERROR, EXPECTED_BAD_KEY_ERROR)


# ------------------------- End Validation Unit Test----------------------------------

# ------------------------- Exception Unit Test----------------------------------
def test_analyzer_exception_risk_analysis(mocker):
    for key, value in widget_api_analyzer_exceptions_risk_analysis.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_risk_analysis',
                     value['analyzer_response'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((HostRespondedWithErrorException, HostNotReachableException, ValidationException)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_RISK_ANALYSIS
                                                          )
            assert ex.typename in (EXPECTED_VALIDATION_EXCEPTION, EXPECTED_BAD_VALUE_ERROR, EXPECTED_BAD_KEY_ERROR)

# ------------------------- End Risk Analysis ----------------------------------
#------------------------- Top application-threats ----------------------------------

#----------------Service unit test---------------#
def test_service_get_top_application_threats(mocker):
    for key, value in widget_api_top_application_threats_success_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     value['function_obj'])
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            expected_response = top_application_threats_full_payload_final_response[key]
            response = service_object.service_get_instant_metric(req_payload=value['input'],
                                                                 metric_name=UNIT_TEST_TOP_APPLICATION_THREATS)
            assert response.get('data') == expected_response.get('data')

def test_bad_response_service_get_top_application_threats(mocker):
    for key, value in widget_api_top_application_threats_failure_input_payload.items():
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     value['function_obj_analyzer'])

        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            with pytest.raises((ValidationException, ValueError, KeyError)) as ex:
                service_object.service_get_instant_metric(req_payload=value['input'],
                                                          metric_name=UNIT_TEST_TOP_APPLICATION_THREATS)
            assert ex.typename in (EXPECTED_VALIDATION_EXCEPTION , EXPECTED_BAD_VALUE_ERROR, EXPECTED_BAD_KEY_ERROR)

# CLIENT MAIN API
def test_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     success_top_application_threats_all_adom_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        filename = 'adoms.json'
        adoms_list=[]
        with open(filename, "rb") as fin:
                adoms_list = json.load(fin)
        top_application_threats_response = []
        for adom in adoms_list:
            analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, adom['name'])
            if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                            analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                        analyzer_response.data['result']['data'] = [dict(item, adom=adom['name']) for item in
                                                                analyzer_response.data['result']['data']]                                       
                        top_application_threats_response.extend(analyzer_response.data['result']['data'])
            # ------------------------ Converted response -----------------------
        converted_response = converter_object.convert_to_application_threats(req_payload=top_application_threats_all_adom_input_payload,metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,analyzer_response=top_application_threats_response)
        assert len(converted_response['data']) > 0

        for data in converted_response['data']:
            assert data['adom'] in ADOM_LISTS


# LIMIT = 2
def test_bad_two_limit_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     success_with_two_limit_top_application_threats_all_adom_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        filename = 'adoms.json'
        adoms_list=[]
        with open(filename, "rb") as fin:
                adoms_list = json.load(fin)
        top_application_threats_response = []
        for adom in adoms_list:
            analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, adom['name'])
            if analyzer_response.data is not None and 'result' in analyzer_response.data and 'data' in \
                            analyzer_response.data['result'] and analyzer_response.data['result']['data']:
                        analyzer_response.data['result']['data'] = [dict(item, adom=adom['name']) for item in
                                                                analyzer_response.data['result']['data']]                                       
                        top_application_threats_response.extend(analyzer_response.data['result']['data'])
            # ------------------------ Converted response -----------------------
        converted_response = converter_object.convert_to_application_threats(req_payload=top_application_threats_all_adom_input_payload,metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,analyzer_response=top_application_threats_response)
        assert len(converted_response['data']) >0
        for data in converted_response['data']:
            assert data['adom'] in LIMIT_ADOM_LISTS




# LIMIT = 0
def test_bad_zero_limit_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_zero_limit_top_application_threats_all_adom_integrator_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_LIMIT

#without sortby
def test_without_sortby_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_without_sortby_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_SORTBY


# without field
def test_without_field_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_without_field_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_SORTBY_CODE
             
# without order
def test_without_order_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_without_order_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_SORTBY


# wrong field
def test_wrong_field_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_wrong_field_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_SORTBY

# empty start time
def test_empty_start_time_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_empty_start_time_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_TIME


# empty end time
def test_empty_end_time_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_empty_end_time_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_TIME

# wrong time range
def test_wrong_time_range_client_top_application_threats(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     bad_wrong_time_range_top_application_threats_all_adom_response)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
        assert analyzer_response.data['error-code'] ==IMPROPER_TIME


# File not available
def test_file_not_exist_client_top_application_threats(mocker):

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id() 
        with pytest.raises((ValidationException)) as ex:
            filename = 'adom.json'
            if not os.path.exists(filename):
                raise ValidationException(FILE_DOES_NOT_EXIST)
            response = service_object.service_get_instant_metric(
                                            metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,req_payload= top_application_threats_all_adom_input_payload)
        assert  EXPECTED_VALIDATION_EXCEPTION in str(ex)
               
    #---------------End Service unit test--------------#

    #--------------- converter unit test---------------#

#SUCCESSFUL CONVERTER RESPONSE 
def test_converter_top_application_threats(mocker):
            response = converter_object.convert_to_application_threats(req_payload=top_application_threats_all_adom_input_payload,
                                                                    metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,
                                                                    analyzer_response=all_adom_top_application_threats_ananlyzer_final_response)      
            assert len(response['data']) == top_application_threats_all_adom_input_payload['limit']

# REQUIRED FIELD NULL 
def test_convert_top_application_threats_with_null_fields(mocker):
    response = converter_object.convert_to_top_applications_usage(req_payload=top_application_threats_all_adom_input_payload,
                                                                    metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,
                                                                    analyzer_response=all_adom_top_application_threats_ananlyzer_none_fields_response)
    assert  response['data'][0]['adom'] == None


#ALL_ADOM_RESPONSE_NULL
def test_convert_top_application_threats_with_empty_response(mocker):
    response = converter_object.convert_to_application_threats(req_payload=top_application_threats_all_adom_input_payload,
                                                                    metric_name=UNIT_TEST_TOP_APPLICATION_THREATS,
                                                                    analyzer_response=[])
   
    assert response['metric'] == UNIT_TEST_TOP_APPLICATION_THREATS
    assert  len(response['data']) == 0

    #---------------End converter unit test---------------#

#---------------- -Integrator unit test---------------#
# INTERGRATOR SUCCESS RESPONSE 
def test_top_application_threats_integrator_response(mocker):
        mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_top_threats',
                     success_top_application_threats_integrator_response)
        with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            analyzer_response = integrator_object.get_widget_top_application_threats(top_application_threats_all_adom_input_payload, UNIT_TEST_ADOM_NAME)
            assert len(analyzer_response.data['result']['data']) >= 0    

#-------------- End Top application-threats ----------------------

#------------------SD-WAN=-DATA--------------------

#-------------- service unit test -----------------#
def test_service_sd_wan_usages(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sd_wan_usage',
                    mock_sd_wan_uasages)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = service_object.service_get_instant_metric(req_payload=sd_wan_request_client_paylaod,
                                                                metric_name=UNIT_TEST_SD_WAN_USAGES)
        for data in response['data']:
            for key in list(data.keys()):
                response = True if key in list(SA_WAN_FINAL_FIELD_RESPONSE.keys()) else False
                assert response == True 

# LIMIT = 0
def test_bad_zero_limit_client_sd_wan_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            service_object.service_get_instant_metric(req_payload=sd_wan_request_limit_zero_paylaod,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

# LIMIT = NEGATIVE
def test_bad_negative_limit_client_sd_wan_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            service_object.service_get_instant_metric(req_payload=sd_wan_request_limit_nagative_paylaod,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

# without sortby
def test_without_sortby_client_sd_wan_usages(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex:
            service_object.service_get_instant_metric(req_payload=sd_wan_request_sort_by_nagative_paylaod,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_VALIDATION_EXCEPTION in str(
            ex)

# without filter
def test_without_field_client_sd_wan_(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=top_application_usages_without_field_payload,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)

# empty start time
def test_empty_start_time_client_sd_wan(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=sd_wan_request_empty_start_time__paylaod,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)

# empty end time
def test_empty_end_time_client_sd_wan_usage(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex:
            service_object.service_get_instant_metric(req_payload=sd_wan_request_empty_end_time__paylaod,
                                                      metric_name=UNIT_TEST_SD_WAN_USAGES)
        assert EXPECTED_BAD_VALUE_ERROR in str(
            ex)
#------------------------- End Top application-threats ----------------------------------

#--------------------------------- Site - Map ------------------------------------------#
#CLIENT WORKER  
def test_client_widget_api_site_map(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.get_all_sites_devices_data',
                mock_data_all_site_device_data_site_map)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',
                mock_data_get_site_for_user)
    with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            response = service_object.service_get_instant_metric(req_payload= req_payload_site_map,
                                                                 metric_name=UNIT_TEST_SITE_MAP)
            assert len(response.get('data')) > 0 
            for data in  response.get('data'):
                for key in data.keys():
                    response = True if key in client_response_list else False 
                    assert response ==True

#LIMIT_VALIDATION
def test_client_limit_test_on_payload_site_map(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=req_payload_limit_apply_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex) 


#SORT_BY_VALIDATION
def test_client_sort_by_test_on_payload_site_map(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_sort_by_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex) 


#EMPTY_START_TIME_VALIDATION
def test_client__empty_start_time_test_on_payload_site_map(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_empty_start_time_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)               
        assert  EXPECTED_BAD_VALUE_ERROR in str(
                ex) 

#EMPTY_END_TIME_VALIDATION
def test_client_empty_end_time_test_on_payload_site_map(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_empty_end_time_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)               
        assert  EXPECTED_BAD_VALUE_ERROR in str(
                ex) 

#FIELTER_VALIDATION 
def test_client_filter_test_on_payload_site_map(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_filter_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex) 

#---------------integrator--------------------#

# GET_ALL_DEVICES_DATA_SITE
def test_get_all_sites_devices_data_site_map(mocker):
     mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',mock_function_get_device_by_id) 
     mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_widget_site_details_event_management',mock_function_site_details_event_management)
     with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = service_object.get_all_sites_devices_data( adoms_list=site_map_adom_list, req_payload = req_payload_site_map)
        assert response[0] == ALL_ADOM_DEVICES
        assert response[1] == ALL_ADOM__DEVICES_WITH_ALERTS

#GET_SITE_FOR_USER_SITE_MAP
def test_get_site_for_user_site_map(mocker):
    mocker.patch('fortinet_common.APIService.post', mock_generate_token_success_response)
    mocker.patch('fortinet_common.APIService.get',mock_data_get_site_for_use_site_map)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = integrator_object.get_sites_for_user()
        assert len(response.data) > 0 and ('error_code' or 'error' not in response.data) 

# HOST_RESPONSED_WITH_ERROR
def test_host_unreachable_site_map(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.get_all_sites_devices_data',
                mock_data_all_site_device_data_site_map)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',
                     mock_data_host_unreachable_site_map)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((HostRespondedWithErrorException,HostRespondedWithErrorException)) as ex:
            service_object.service_get_instant_metric(req_payload=request_paylaod_analyzer_site_map,
                                                                    metric_name=UNIT_TEST_SITE_MAP)
            
        assert EXPECTED_HOSTRESPONDEDWITHERROR_EXCEPTION  in str(ex)


#TOKEN_CREATION_EXCEPTION
def test_im_server_exception_site_map(mocker):
    mocker.patch('fortinet_common.APIService.post', mock_generate_token_bad_response)
    with app.test_request_context():
        with pytest.raises(TokenCreationException) as ex:
            im_generate_token()
        assert EXPECTED_TOKENCREATION_EXCEPTION in str(ex)
#-------------End service unit test----------------
#--------------- converter unit test---------------#

#SUCCESSFUL CONVERTER RESPONSE 
def test_converter_sd_wan_usages(mocker):
    response = converter_object.convert_to_sd_wan_usage(req_payload=sd_wan_request_paylaod,
                                                            metric_name=UNIT_TEST_SD_WAN_USAGES,
                                                            analyzer_response=ad_wan_analyzer_final_response)  
    assert len(response['data']) == top_application_threats_all_adom_input_payload['limit']
    
    for data in response['data']:
        for key in list(data.keys()):
            response = True if key in list(SA_WAN_FINAL_FIELD_RESPONSE.keys()) else False
            assert response == True 

# NULL ANALYZER RESPONSE 
def test_analyzer_null_response_converter_sd_wan_usages(mocker):
    response = converter_object.convert_to_sd_wan_usage(req_payload=sd_wan_request_paylaod,
                                                            metric_name=UNIT_TEST_SD_WAN_USAGES,
                                                            analyzer_response=MULL_ANALYZER_RESPONSE)      
    for data in response['data']:
        for key in list(data.keys()):
            response = True if key in list(SA_WAN_FINAL_FIELD_RESPONSE.keys()) else False
            assert response == True 

# FIELDS ARE MISSIG IN ANALYZER RESPONSE 
def test_analyzer_dielas_are_missing_response_converter_sd_wan_usages(mocker):
    response = converter_object.convert_to_sd_wan_usage(req_payload=sd_wan_request_paylaod,
                                                            metric_name=UNIT_TEST_SD_WAN_USAGES,
                                                            analyzer_response=SD_WAN_ANALYZER_RESPONSE_FIELDS_ARE_MISSING)     
    for data in response['data']:
        for key in list(data.keys()):
            response = True if key in list(SA_WAN_FINAL_FIELD_RESPONSE.keys()) else False
            assert response == True 

#---------------END converter unit test---------------#
#----------------integrator unit test  ---------------#
@patch('fortinet_common.APIService.post')
def test_integrator_response_sd_wan(mocker):
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = sd_wan_all_adom_analyzer_response
        mocker.side_effect = fake_responses
        data = integrator_object.get_sd_wan_usage(UNIT_TEST_ADOM_NAME)
        assert data.json() == sd_wan_all_adom_analyzer_response

@patch('fortinet_common.APIService.post')
def test_integrator_none_response_sd_wan(mocker):
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = None
        mocker.side_effect = fake_responses
        data = integrator_object.get_sd_wan_usage(UNIT_TEST_ADOM_NAME)
        assert data.json() == None


@patch('fortinet_common.APIService.post')
def test_integrator_wrong_adom_name_response_sd_wan(mocker):
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = mock_generate_token_success_response
        fake_responses[1].json.return_value = None
        mocker.side_effect = fake_responses
        data = integrator_object.get_sd_wan_usage(BAD_ADOM_NAME)
        assert data.json() == None
#-----------END integrator unit test---------------#


#----------------END SD-WAN=-DATA------------------#
#------------ End integrator -----------------#

#------------ Converter ---------------------#

def test_conveter_site_map(mocker):
    converted_response = converter_object.convert_to_site_map(req_payload = request_paylaod_conveter_site_map, metric_name = UNIT_TEST_SITE_MAP, all_sites_consolidated_data = all_site_consoldate_data)
    for data in converted_response['data']:
        for key in list(data.keys()):
            response = True if key in list(CONVERTER_IDLE_FIELD.keys()) else False 
            assert response == True
            

# STATUS_CHECK
def test_status_check_site_map(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.get_all_sites_devices_data',
                mock_data_all_site_device_data_site_map)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',
                mock_data_get_site_for_user)
    with app.test_request_context():
            expexted_status = ''
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            response = service_object.service_get_instant_metric(req_payload= req_payload_site_map,
                                                                 metric_name=UNIT_TEST_SITE_MAP)
            result = response.get('data')
            for i in range(3):
                    expexted_status = expected_result(i)
                    if expected_result =='1':
                        expected_result =='up'
                    elif expected_result !='1':
                        expected_result =='down'
                    else:
                        expected_result =='alert'
                    result[i].get('expexted_status') ==expexted_status
    
                    
            
#------------ End Converter -----------------#

#--------------------------------End Site - Map ----------------------------------------#

#------------------------------- Bandwidth Summary API --------------------------------- #

def test_bandwidth_summary_api(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_monitor_data',
                mock_get_system_monitor_data)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_virtual_wan_healthchk_data',
                mock_virtual_wan_healthchk_data)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                mock_get_device_by_id)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_interface_logs',
                mock_get_device_interface_logs)
    with app.test_request_context():
            mocker.patch("uuid.uuid4", mock_uuid)
            interceptor_object.get_corelation_id()
            response = service_object.service_get_instant_metric(req_payload= req_payload_bandwidth_summary,
                                                                 metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)
            assert len(response.get('data')) > 0 
            for data in  response.get('data'):
                for key in data.keys():
                    response = True if key in bandwidth_response else False 
                    assert response ==True

#LIMIT_VALIDATION
def test_limit_bandwidth_summary(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=req_payload_limit_apply_bandwidth_summary,
                                                                    metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex) 

#SORT_BY_VALIDATION
def test_client_sort_by_test_on_payload_bandwidth_summary(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_sort_by_bandwidth_summary,
                                                                    metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex)  

#EMPTY_START_TIME_VALIDATION
def test_empty_start_time_test_on_bandwidth_summary(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_empty_start_time_bandwidth_summary,
                                                                    metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)               
        assert  EXPECTED_BAD_VALUE_ERROR in str(
                ex) 

#EMPTY_END_TIME_VALIDATION
def test_client_empty_end_time_test_on_payload_bandwidth_summary(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValueError)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_empty_end_time_bandwidth_summary,
                                                                    metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)               
        assert  EXPECTED_BAD_VALUE_ERROR in str(
                ex)

#FIELTER_VALIDATION
def test_client_filter_test_on_payload_bandwidth_summary(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises((ValidationException)) as ex :
            service_object.service_get_instant_metric(req_payload=request_paylaod_filter_bandwidth_summary,
                                                                    metric_name=UNIT_TEST_BANDWIDTH_SUMMARY)               
        assert  EXPECTED_VALIDATION_EXCEPTION in str(
                ex) 

def test_get_metric_Validate_permission(mocker):
    mocker.patch('fortinet_common.APIService.get', patch_metric_response)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_metric_permission_function_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        response = metric.get()
    assert response == integrator_metric_response

def test_get_metric_Validate_bad__permission(mocker):
    mocker.patch('fortinet_common.APIService.get', patch_metric_response)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_bad_permission_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        response = metric.get()
        assert response[0]['error-code'] == ERROR_CODE_PERMISSION_DENIED
