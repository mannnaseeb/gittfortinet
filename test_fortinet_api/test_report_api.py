"""test cases for report api"""
from copy import Error
import os
import sys, json
from _pytest.python_api import raises
import datetime
import pytest
from dotenv import load_dotenv

from models import report_format
from models import report_meta

from mock import Mock

load_dotenv()
sys.path.append(os.getcwd())
from app import app

from flask_sqlalchemy import SQLAlchemy

from unittest.mock import patch, Mock
from middleware.request_interceptor import FortinetAPIRequestInterceptor
from services.fortinet_api_services import FortinetAPIService
from integrators.fortinet_integrator import FortinetIntegrator
from languages.fortinet_api_exceptions import HostAnalyzerRespondedWithErrorException, ValidationException
from validators.fortinet_api_validations import FortinetAPIValidations
from converters.fortinet_api_converters import FortinetConverters
from .constants import ERROR_CODE_PERMISSION_DENIED,UNIT_TEST_ADOM_NAME
from .mocker_functions import (success_create_report,mock_uuid,
                                success_download_report,success_delete_report,
                                success_list_report,success_list_reports,
                                report_list_by_title_report_list,
                                wrong_adom_name_report_list,integrator_report_list, 
                                report_list_integrator_response,patch_get_adom_device_report_response,
                                patch_get_adom_device_report_response,
                                mock_get_adom_device_report_permission_function_response,
                                mock_validate_token_success_response,mock_bad_permission_response
                                
                               
                                
                                )
from .responses import (create_report_request_pay_load,create_report_response,
                        download_report_reponse,download_report_request_pay_load,
                        delete_report_response,payload_list_report,list_report_reponse,
                        payload_report_list,final_response_report_list,
                        get_all_report_meta_from_database,
                        integrator_response_report_list,integrator_response_report_list,
                        valid_token,conveter_final_report_list,integrator_report_status_response
                        )
from apis.report import GetListOfReportMetaData

reports_object = GetListOfReportMetaData()
interceptor_object = FortinetAPIRequestInterceptor()
service_object = FortinetAPIService()
validation_object = FortinetAPIValidations()
fortinet_integrator_obj = FortinetIntegrator()
converter_object = FortinetConverters()

current_adom_name = "D-AND-D"
current_tid = "5d36645a-42d2-11ec-976f-04d5902dbff1"
import pytest
from models.report_format import ReportFormat
from models.report_meta import ReportMeta
from models.reports import Reports

from models import report_meta
from mock import Mock
from flask_sqlalchemy import SQLAlchemy

@pytest.fixture
def flask_app_mock():
    """Flask application set up"""
    db = SQLAlchemy(app)
    db.init_app(app)
    return app

@pytest.fixture
def mock_report_meta_unit_object():
    report_meta = ReportMeta(
        ReportMetaID = 1,
        ReportMetaTitleCode = "360-degree-security-review",
        ReportMetaTitle = "360-Degree Security Review",
        StatusID = 1,
        Description = "",
        CreatedBy = 1,
        CreatedOn = "2021-11-02 15:40:28",
        ModifiedBy = 1,
        ModifiedOn = "2021-11-02 15:40:28"
    )
    return report_meta

@pytest.fixture
def mock_report_format_unit_object():
    report_format = ReportFormat(
        ReportFormatID = 1,
        ReportFormatCode = "PDF",
        ReportFormatName = "PDF",
        CreatedBy = 1,
        CreatedOn = "2021-11-02 15:40:28",
        ModifiedBy = 1,
        ModifiedOn = "2021-11-02 15:40:28"
    )
    return report_format
def mock_report__list_meta_unit_object():
    report_meta = Reports(
        ReportTid = 247,
        ReportID= 247,
        TimePeriod= None,
        ReportFormat= '',
        DevicesData = 'GTT-DB-TX-54321[root],DT-40F[root],GTT-TA-TX-60F[root],GTT-DT-TX-69420[root],GTT-RSL-TX-12345[root]',
        ExecutedAt = datetime.datetime(2021, 11, 22, 0, 38, 1),
        ReportTitle =  'Bandwidth and Applications Report',
        CreatedOn = datetime.datetime(2021, 11, 22, 6, 36, 28),
        ProgressReport = 100, ModifiedBy =  88340, 
        CreatedBy =  88340,
        is_deleted = 0,
        ReportFileName = 'Bandwidth and Applications Report-2021-11-22-0038_2661', 
        EndTime = datetime.datetime(2021, 8, 11, 5, 30),
        

    )
    return [report_meta]

@pytest.fixture
def mock_get_sqlalchemy(mocker):
    mock = mocker.patch("flask_sqlalchemy._QueryProperty.__get__").return_value = mocker.Mock()
    return mock

def test_get_report_meta(flask_app_mock,mock_get_sqlalchemy,mock_report_meta_unit_object):
    with flask_app_mock.app_context():
        mock_get_sqlalchemy.filter_by.return_value.first.return_value = mock_report_meta_unit_object
        response = ReportMeta.query.filter_by(ReportMetaTitleCode="360-degree-security-review").first()
        assert response.ReportMetaTitle is "360-Degree Security Review"

def test_create_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.adom_create_reports',
                 success_create_report)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.adom_create_reports(create_report_request_pay_load)
        assert converted_response.original_response.json() == create_report_response

def test_status_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.get_adom_reports_status',
                 success_create_report)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.get_adom_reports_status(current_tid)
        assert converted_response.original_response.json() == create_report_response

def test_download_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.download_adom_reports',
                 success_download_report)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.download_adom_reports(current_tid,download_report_request_pay_load)
        assert converted_response.original_response.json() == download_report_reponse

def test_delete_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.service_delete_report_by_tid',
                 success_delete_report)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.service_delete_report_by_tid(current_tid)
        assert converted_response.original_response.json() == delete_report_response

def test_list_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.service_get_report_list_by_title',
                 success_list_report)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.service_get_report_list_by_title(payload_list_report)
        assert converted_response.original_response.json() == list_report_reponse

#-----------------------List Reports --------------------------------#
def test_list_reports(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.service_get_report_list_by_title',
                 success_list_reports)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.service_get_report_list_by_title(payload_report_list)
        assert converted_response.original_response.json() == final_response_report_list

#invalid matric name 
def test_invalid_matric_name_list_reports(mocker):
    mocker.patch('db_settings.db_utils.get_report_codes_from_database',
                 get_all_report_meta_from_database)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises(ValidationException) as ex : 
            validation_object.check_invalid_payload_reports(payload_report_list,end_point="")
            assert ex.type == ValidationException 
        #---------------service_layer--------------#   
def test_service_list_reports(mocker,flask_app_mock,mock_get_sqlalchemy,mock_report__list_meta_unit_object):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_reports_list_by_title',
                report_list_by_title_report_list)
    with flask_app_mock.test_request_context():
        mock_get_sqlalchemy.filter.return_value.order_by.return_value = mock_report__list_meta_unit_object
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response = service_object.service_get_report_list_by_title(payload_report_list)
        assert response == conveter_final_report_list  

def test_service_wrong_adom_name_list_reports(mocker):
    mocker.patch('integrators.fortinet_integrator.FortinetIntegrator.get_reports_list_by_title',
                wrong_adom_name_report_list)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        with pytest.raises(Exception)  as ex :
            service_object.service_get_report_list_by_title(payload_report_list)
            assert ex.type == Exception
        #------------End service_layer------------#        

        #----------- Integrator_layer ------------#
@patch('fortinet_common.APIService.post')
def test_integrator_list_reports(mocker):
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = valid_token
        fake_responses[1].json.return_value = integrator_response_report_list
        mocker.side_effect = fake_responses
        interceptor_object.get_corelation_id()
        response = fortinet_integrator_obj.get_reports_list_by_title(adom_name=UNIT_TEST_ADOM_NAME,req_payload=payload_report_list)
        assert response.json() == integrator_response_report_list  

@patch('fortinet_common.APIService.post')
def test_token_validation_integrator_list_reports(mocker):
    mocker.patch('fortinet_common.APIService.post', integrator_report_list)
    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        fake_responses = [Mock(), Mock()]
        fake_responses[0].json.return_value = None
        fake_responses[1].json.return_value = integrator_response_report_list
        mocker.side_effect = fake_responses
        interceptor_object.get_corelation_id()
        with pytest.raises(Exception) as ex:
            fortinet_integrator_obj.get_reports_list_by_title(adom_name=UNIT_TEST_ADOM_NAME,req_payload=payload_report_list)
            assert ex.type == Exception  
    #----------- Integrator_layer ------------#
    #------------ conveter_layer -------------#
def test_conveter_list_reports(mocker,flask_app_mock,mock_get_sqlalchemy,mock_report__list_meta_unit_object):

    with flask_app_mock.test_request_context():
        mock_get_sqlalchemy.filter.return_value.order_by.return_value = mock_report__list_meta_unit_object
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        response =converter_object.convert_response_get_report_by_title(response=report_list_integrator_response(),title="bandwidth-and-applications-report")
        assert response == conveter_final_report_list
    #-----------End conveter_layer------------#
#---------------------End List Reports ------------------------------#


def test_status_report(mocker):
    mocker.patch('services.fortinet_api_services.FortinetAPIService.get_adom_reports_status',
                 success_create_report)

    with app.test_request_context():
        mocker.patch("uuid.uuid4", mock_uuid)
        interceptor_object.get_corelation_id()
        converted_response = service_object.get_adom_reports_status(current_tid)
        assert converted_response.original_response.json() == create_report_response

def test_create_report_Validate_permission(mocker):
    mocker.patch('fortinet_common.APIService.get', patch_get_adom_device_report_response)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.auth.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_get_adom_device_report_permission_function_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        response = reports_object.get()
    assert response == integrator_report_status_response

def test_create_report_Validate_bad__permission(mocker):
    mocker.patch('fortinet_common.APIService.get', patch_get_adom_device_report_response)
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.info', return_value='mocked_logging')
    mocker.patch('utils.fortinet_api_logger.FortinetAPILogger.exception', return_value='mocked_logging')
    mocker.patch('fortinet_common.APIService.post',
                 mock_validate_token_success_response)
    mocker.patch('fortinet_common.core.im.IdentityManager.get_current_user_perms',
                 mock_bad_permission_response)
    mocker.patch('middleware.request_interceptor.FortinetAPIRequestInterceptor.get_token', return_value="token_value")
    with app.test_request_context():
        response = reports_object.get()
        assert response[0]['error-code'] == ERROR_CODE_PERMISSION_DENIED