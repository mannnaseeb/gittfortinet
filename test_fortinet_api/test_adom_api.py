import os
import sys

from dotenv import load_dotenv

#from constants import DEFAULT_DEVICE_ID

load_dotenv()
sys.path.append(os.getcwd())

from app import app
import pytest

from test_fortinet_api.constants import *
from test_fortinet_api.responses import *
from flask import g

from middleware.request_interceptor import FortinetAPIRequestInterceptor
from converters.fortinet_api_converters import FortinetConverters
from services.fortinet_api_services import FortinetAPIService
from languages.fortinet_api_languages import ErrorResponse
from integrators.fortinet_integrator import FortinetIntegrator

from test_fortinet_api.mocker_functions import *
from apis.adom_api import AdomAllDevices,SystemStatus

adom = AdomAllDevices()
system_status = SystemStatus()
interceptor_object = FortinetAPIRequestInterceptor()
service_object = FortinetAPIService()
converter_object = FortinetConverters()
error_response_object = ErrorResponse()
integrator_object = FortinetIntegrator()

# Below fixture is to ignore all decorators for a function
@pytest.fixture
def unwrap():
    def unwrapper(func):
        if not hasattr(func, '__wrapped__'):
            return func

        return unwrapper(func.__wrapped__)

    yield unwrapper

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ---------------------- Interceptor get correlation id ----------------------

def test_get_correlation_id(mocker):
    given_correlation_id = UNIT_TEST_CREDENTIAL_ID
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()

        assert g.Correlationid == given_correlation_id


# ---------------------- End Interceptor get correlation id ----------------------

# ---------------------- Services Adom by name ----------------------

def test_service_get_adom_by_name(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_adom_by_name',
                 success_response_from_adom_name)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_adom_by_name(UNIT_TEST_ADOM_NAME)
        data = response
        assert data['data'] == adom_list_by_name_final_response['data']


def test_bad_response_service_get_adom_by_name(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_adom_by_name',
                 bad_response_from_adom_name)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        with pytest.raises(TypeError) as ex:
            service_object.service_get_adom_by_name(UNIT_TEST_BAD_ADOM_NAME)
    assert EXPECTED_BAD_ERROR in str(ex)


# ---------------------- End Services Adom by name ----------------------

# ---------------------- Services Adom list ----------------------

def test_service_get_all_adom(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_all_adom',
                 success_response_from_adom_list)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_all_adom()
        data = response
        assert data['data'] == all_adom_list_final_response['data']


def test_bad_response_service_get_all_adom(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_all_adom',
                 bad_response_from_adom_list)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        with pytest.raises(TypeError) as ex:
            service_object.service_get_all_adom()
    assert EXPECTED_BAD_ERROR in str(ex)


# ---------------------- End Services Adom list ----------------------

# ---------------------- Services Adom device list ----------------------

def test_service_get_device_list(mocker):
    res = mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                       success_response_adom_device_list_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_device_by_id(adom_name=UNIT_TEST_ADOM_NAME)
        data = response
        assert data['data'] == adom_devices_list_final_response['data']


def test_bad_response_service_get_device_list(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                 bad_response_adom_device_list_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_device_by_id(adom_name=UNIT_TEST_BAD_ADOM_NAME)
        assert response == bad_response_device_list


# ---------------------- End Services Adom device list ----------------------

# ---------------------- Services Adom device by id ----------------------
def test_service_get_device_by_id(mocker):
    res = mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                       success_response_adom_device_by_id_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_device_by_id(adom_name=UNIT_TEST_ADOM_NAME,
                                                           device_id=UNIT_TEST_DEVICE_ID)
        data = response
        assert data['data'] == adom_devices_by_id_final_response['data']


def test_bad_response_service_get_device_by_id(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                 bad_response_adom_device_by_id_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_device_by_id(adom_name=UNIT_TEST_BAD_ADOM_NAME,
                                                           device_id=UNIT_TEST_BAD_DEVICE_ID)
        assert response == bad_response_device_list


# ---------------------- End Services Adom device by id ----------------------

# ---------------------- Converter Adom by name ----------------------
def test_convert_response_get_adom_by_name():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = converter_object.convert_response_get_adom_by_name(
            success_response_from_adom_name(adom_name=UNIT_TEST_ADOM_NAME))
        data = response
        assert data['data'] == adom_list_by_name_final_response['data']


def test_bad_response_convert_response_get_adom_by_name():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        with pytest.raises(TypeError) as ex:
            converter_object.convert_response_get_adom_by_name(
                bad_response_from_adom_name(adom_name=UNIT_TEST_BAD_ADOM_NAME))
        assert EXPECTED_BAD_ERROR in str(ex)


# ---------------------- End Converter Adom by name ----------------------

# ---------------------- Converter Adom list ----------------------

def test_convert_response_get_all_adom():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = converter_object.convert_response_get_adom_by_name(success_response_from_adom_list())
        data = response
        assert data['data'] == all_adom_list_final_response['data']


def test_bad_response_convert_response_get_all_adom():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        with pytest.raises(TypeError) as ex:
            converter_object.convert_response_get_adom_by_name(bad_response_from_adom_list())
        assert EXPECTED_BAD_ERROR in str(ex)


# ---------------------- End Converter Adom list ----------------------

# ---------------------- Converter Adom device by id ----------------------
def test_convert_response_get_device_by_id():
    with app.test_request_context():
        response = converter_object.convert_response_get_device_by_id(
            success_response_adom_device_by_id_from_api(adom_name=UNIT_TEST_ADOM_NAME,
                                                        device_id=UNIT_TEST_DEVICE_ID))
        data = response
        assert data['data'] == adom_devices_by_id_final_response['data']


def test_bad_response_convert_response_get_device_by_id():
    with app.test_request_context():
        response = converter_object.convert_response_get_device_by_id(
            bad_response_adom_device_by_id_from_api(adom_name=UNIT_TEST_BAD_ADOM_NAME,
                                                    device_id=UNIT_TEST_BAD_DEVICE_ID))
        assert response == bad_response_device_list


# ---------------------- End Converter Adom device by id ----------------------

# ---------------------- Converter Adom device list ----------------------
def test_convert_response_get_device_list():
    with app.test_request_context():
        response = converter_object.convert_response_get_device_by_id(
            success_response_adom_device_list_from_api(adom_name=UNIT_TEST_ADOM_NAME))
        data = response
        assert data['data'] == adom_devices_list_final_response['data']


def test_bad_response_convert_response_get_device_list():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = converter_object.convert_response_get_device_by_id(
            bad_response_adom_device_list_from_api(adom_name=UNIT_TEST_BAD_ADOM_NAME))
        assert response == bad_response_device_list


# ---------------------- End Converter Adom device list ----------------------

# ---------------------- Error Response ----------------------

def test_error_response_code():
    with app.test_request_context():
        response = error_response_object.get_dict(error_code=UNIT_TEST_ERROR_CODE)
        assert response == final_error_response


# ---------------------- End Error Response ----------------------

# ---------------------- Integrator Adom by name ----------------------

def test_integrator_get_adom_by_name(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 success_response_from_adom_name)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object._get_all_adom)
        data = decorated_function_unwrapped(adom_name=UNIT_TEST_ADOM_NAME, self=integrator_object)
        assert data.data['data'] == adom_list_by_name_integrator_response['data']


def test_bad_response_integrator_get_adom_by_name(mocker):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 bad_response_from_adom_name)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        data = integrator_object.get_adom_by_name(UNIT_TEST_BAD_ADOM_NAME)
    assert data.data is None


# ---------------------- End Integrator Adom by name ----------------------

# ---------------------- Integrator Adom list ----------------------

def test_integrator_get_all_adom(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get', success_response_from_adom_list)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object._get_all_adom)
        data = decorated_function_unwrapped(self=integrator_object)
        assert data.data['data'] == all_adom_list_integrator_response['data']

def test_bad_response_integrator_get_all_adom(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 bad_response_from_adom_list)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object._get_all_adom)
        data = decorated_function_unwrapped(self=integrator_object)
    assert data.data is None


# ---------------------- End Integrator Adom list ----------------------

# ---------------------- Integrator Adom devices list ----------------------

def test_integrator_get_device_list(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 success_response_adom_device_list_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object.get_device_by_id)
        data = decorated_function_unwrapped(adom_name=UNIT_TEST_ADOM_NAME, self=integrator_object)
        assert data.data['data'] == adom_devices_list_integrator_response['data']

def test_bad_response_integrator_get_device_list(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 bad_response_adom_device_list_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object.get_device_by_id)
        response = decorated_function_unwrapped(adom_name=UNIT_TEST_BAD_ADOM_NAME, self=integrator_object)
    assert response.data is None


# ---------------------- End Integrator Adom devices list ----------------------

# ---------------------- Integrator Adom device by id ----------------------

def test_integrator_get_device_by_id(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 success_response_adom_device_by_id_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object.get_device_by_id)
        data = decorated_function_unwrapped(adom_name=UNIT_TEST_ADOM_NAME, device_id=UNIT_TEST_DEVICE_ID, self=integrator_object)
        assert data.data['data'] == adom_devices_by_id_integrator_response['data']


def test_bad_response_integrator_get_device_by_id(mocker, unwrap):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                           original_response={'access_token': 'token_value'}))
    mocker.patch('fortinet_common.APIService.get',
                 bad_response_adom_device_by_id_from_api)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        #Below we are ensuring we ignore the decorator used for the function we are testing
        decorated_function_unwrapped = unwrap(integrator_object.get_device_by_id)
        response = decorated_function_unwrapped(adom_name=UNIT_TEST_BAD_ADOM_NAME, device_id=UNIT_TEST_BAD_DEVICE_ID, self=integrator_object)
    assert response.data is None

# ---------------------- End Integrator Adom device by id ----------------------

# ---------------------- Services System status ----------------------

def test_service_get_system_status(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_status',
                 success_response_from_system_status)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_system_status(UNIT_TEST_ADOM_NAME,UNIT_TEST_DEVICE_ID)
        data = response
        assert data == system_status_final_response

def test_bad_response_service_get_system_status(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_status',
                 bad_response_from_system_status)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_system_status(UNIT_TEST_ADOM_NAME,UNIT_TEST_BAD_DEVICE_ID)
        data = response
        assert data == system_status_bad_response

def test_wrong_adomname_response_service_get_system_status(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_status',
                 bad_response_from_system_status)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_system_status(UNIT_TEST_BAD_ADOM_NAME,UNIT_TEST_DEVICE_ID)
        data = response
        assert data == system_status_bad_response

def test_wrong_deviceid_adomname_response_service_get_system_status(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_status',
                 bad_response_from_system_status)
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = service_object.service_get_system_status(UNIT_TEST_BAD_ADOM_NAME,UNIT_TEST_BAD_DEVICE_ID)
        data = response
        assert data == system_status_bad_response

# ---------------------- End Services system status ----------------------

# ---------------------- Converter system status  ----------------------
def test_convert_response_get_system_status():
    with app.test_request_context():
        interceptor_object.get_corelation_id()
        response = converter_object.convert_response_get_system_status(
            success_response_from_system_status(adom_name=UNIT_TEST_ADOM_NAME,device_name=UNIT_TEST_DEVICE_ID))
        data = response
        assert data == system_status_final_response

# ---------------------- End Converter system status  ----------------------

# --------------------------- roles and permission test cases ----------------------
# ----------------------- test cases roles and permissions
def test_get_adom_device_Validate_permission(mocker):
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_client_id',return_value="client_id")
    mocker.patch('fortinet_common.APIService.get', patch_adom_all_devices_function)
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value = 'token_value')
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                            original_response={'access_token': 'token_value'}))
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',mock_adom_get_clients_of_user)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_get_adom_device_permission_function_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.set_base64_ip',return_value="set_base64_ip")
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        g.access_token = "token_value"
        g.manager_adom_name = UNIT_TEST_ADOM_NAME
        g.manager_ip = FORTINET_MANAGER_BASE_URL
        response = adom.get()
    assert response == adom_device_final_response

def test_get_adom_device_Validate_bad__permission(mocker):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                            original_response={'access_token': 'token_value'}))
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_client_id',return_value="client_id")
    mocker.patch('fortinet_common.APIService.get', patch_adom_all_devices_function)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',mock_adom_get_clients_of_user)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_bad_permission_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.set_base64_ip',return_value="set_base64_ip")
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        g.access_token = "token_value"
        g.manager_adom_name = UNIT_TEST_ADOM_NAME
        g.manager_ip = FORTINET_MANAGER_BASE_URL
        response = adom.get()
        assert response[0]['error-code'] == ERROR_CODE_PERMISSION_DENIED 

def test_get_system_status_Validate_permission(mocker):
    mocker.patch('fortinet_common.APIService.get', patch_response_from_system_status)
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                            original_response={'access_token': 'token_value'}))
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                        devices_list_response)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_sites_for_user',mock_adom_get_clients_of_user)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_system_status',patch_system_status_response)
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',patch_devices_list_function)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_client_id',return_value="client_id")
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_get_system_status_permission_function_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.set_base64_ip',return_value="set_base64_ip")
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                       success_response_adom_device_list_from_api)
    with app.test_request_context():
        g.access_token = "token_value"
        g.manager_adom_name = UNIT_TEST_ADOM_NAME
        g.analyzer_adom_name = UNIT_TEST_ADOM_NAME
        g.manager_ip = FORTINET_MANAGER_BASE_URL
        response = system_status.get(DEVICE_SERIAL_NUMBER)
    assert response == system_status_final_response

def test_get_system_status_Validate_bad__permission(mocker):
    mocker.patch('integrators.fortinet_integrator.im_generate_token', return_value=APIResponse(data={'access_token': 'token_value'},
                            original_response={'access_token': 'token_value'}))
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_client_id',return_value="client_id")
    mocker.patch('fortinet_common.APIService.get', patch_response_from_system_status)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_bad_permission_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.set_base64_ip',return_value="set_base64_ip")
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_device_by_id',
                       success_response_adom_device_list_from_api)
    with app.test_request_context():
        g.access_token = "token_value"
        g.manager_adom_name = UNIT_TEST_ADOM_NAME
        g.manager_ip = FORTINET_MANAGER_BASE_URL
        response = system_status.get(DEVICE_SERIAL_NUMBER)
        assert response[0]['error-code'] == ERROR_CODE_PERMISSION_DENIED 
