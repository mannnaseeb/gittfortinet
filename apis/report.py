import logging
from flask.globals import request
from flask import g
from flask_restx import Resource,Namespace
from services.fortinet_api_services import FortinetAPIService
from languages.fortinet_api_languages import ErrorResponse
from languages.constants import HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR, \
        ERROR_CODE_HOST_NOT_REACHABLE,ERROR_CODE_INVALID_TOKEN, \
            HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS,ERROR_CODE_FOR_INTERNAL_SERVER_ERROR, \
                ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR,HTTP_STATUS_CODE_BAD_REQUEST, \
                    ERROR_CODE_VALIDATION_ERROR
from middleware.token_interceptor import validate_token
from constants import SUCCESS_CODE,SUCCESS_MESSAGE,ERROR_CODE_BAD_REQUEST, \
    ERROR_CODE_BAD_REQUEST_MESSAGE,ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, \
        ERROR_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,\
        FAI_GET_ADOM_DEVICE_REPORT,ERROR_CODE_UNAUTHORIZED_ACCESS
from validators.fortinet_api_validations import FortinetAPIValidations
from converters.fortinet_api_converters import FortinetConverters
from utils.fortinet_api_logger import FortinetAPILogger

from api_models.report_api_model import AdomreportsModel, default_report_response
from api_models.common_error_api_model import common_error_response
#--------------- Middleware --------------------
from languages.fortinet_api_exceptions import HostNotReachableException, \
    HostRespondedWithErrorException,NoRecordFoundException, \
        TokenCreationException, ValidationException, handle_exception
from middleware.request_interceptor import FortinetAPIRequestInterceptor
from integrators.fortinet_integrator import FortinetIntegrator
from api_models.report_api_model import report_meta_response
from fortinet_common.core.decorators import permission_required
integrator_object = FortinetIntegrator()

logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))
api_converter = FortinetConverters()
# --------------------- gettings Validations ---------------------
validation_object = FortinetAPIValidations()
#--------------- parsers --------------------

api = Namespace(name='report',description='set of all report api')
interceptor_object = FortinetAPIRequestInterceptor()


parser = api.parser()
parser.add_argument('Correlationid', location='headers')
parser.add_argument('client_id', location='headers', required=True)
parser_reports_list = api.parser()
parser_reports_list.add_argument('Correlationid', location='headers')
parser_reports_list.add_argument('start-date', location='args')
parser_reports_list.add_argument('end-date', location='args')
parser_reports_list.add_argument('client_id', location='headers', required=True)
reports_parser_api = api.parser()
reports_parser_api.add_argument('Correlationid', location='headers')
report_status_parser_api = api.parser()
report_status_parser_api.add_argument('Correlationid', location='headers')
report_status_parser_api.add_argument('client_id', location='headers', required=True)

download_report_parser_api = api.parser()
download_report_parser_api.add_argument('Correlationid', location='headers')

report_meta = api.parser()
report_meta.add_argument('Correlationid', location='headers')
#-------------End  parsers ------------------

@api.expect(report_meta)
@api.route("/meta")
class GetListOfReportMetaData(Resource):
    """Report Meta Data"""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, report_meta_response(
        api)),
                        ERROR_CODE_BAD_REQUEST: (
                                                        ERROR_CODE_BAD_REQUEST_MESSAGE, common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                                                  ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE, common_error_response(api))})
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self):
        """
        Get List Of Report Meta Data
        """
        try:
            # ----------- Interceptor ------------#
            interceptor_object.get_corelation_id()
            # ------------- logger ---------------#
            logger.info(f""" {request.method} {request.url} """)
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_get_report_meta()
            # -------------- logger ---------------#
            logger.info(f"""response: {str(response)}""")
            return response
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""response: {str(error)}""")
            return error
        except Exception as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
                ERROR_CODE_FOR_INTERNAL_SERVER_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error

# --------------Create report-----------------#
@api.expect(reports_parser_api)
@api.route("")
class AdomReports(Resource):
    """Adom Reports."""

    fortinet_api_service_obj = FortinetAPIService()

    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       default_report_response(api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @api.expect(AdomreportsModel.reportInputPayload(api))
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def post(self):
        try:
            #------------ Interceptor ------------#
            interceptor_object.get_corelation_id()

            req_payload = api.payload.copy()
            validation_object.check_invalid_filter_payload_reports(req_payload)
            # ---------- check clientid ----------#
            client_id = g.client_id
            # ------------- validate clientID --------------#
            self.fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------ validation ------------#
            validation_object.check_adom_report_invalid_payload(req_payload)
            validation_object.validate_device_id(req_payload)
            # ---------- attach client-id ---------#
            req_payload = api_converter.add_devids_to_create_report_filter(req_payload, client_id, self.fortinet_api_service_obj)
            # ------------- service response -------------#
            response = self.fortinet_api_service_obj.adom_create_reports(req_payload)
            return response

        except HostRespondedWithErrorException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""error: {str(ex)}""")
            return error
        except HostNotReachableException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""error: {str(error)}""")
            return error
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""error: {str(ex)}""")
            return error
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)

# --------------Get report status -----------------#

@api.expect(report_status_parser_api)
@api.route("/status/<string:tid>")
class AdomReportStatus(Resource):
    """Adom Reports Status."""

    fortinet_api_service_obj = FortinetAPIService()

    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       AdomreportsModel.adom_report_data_response(api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self,tid):
        try:
            #------------ Interceptor ------------#
            interceptor_object.get_corelation_id()
            # ---------- check clientid ----------#
            client_id = interceptor_object.get_client_id()
            # ------------- validate clientID --------------#
            self.fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------- service response -------------#
            response = self.fortinet_api_service_obj.get_adom_reports_status(tid)
            return response

        except HostRespondedWithErrorException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""error: {str(error)}""")
            return error
        except HostNotReachableException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""error: {str(error)}""")
            return error
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""error: {str(error)}""")
            return error
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)

# --------------Get Adom download report  -----------------#

@api.expect(download_report_parser_api)
@api.route("/download/<string:tid>")
class AdomDownloadReport(Resource):
    """Adom Download Reports."""

    fortinet_api_service_obj = FortinetAPIService()

    @api.expect(AdomreportsModel.reportDownloadInputPayLoad(api))
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, AdomreportsModel.download_response(
        api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def post(self, tid):
        try:
            #------------ Interceptor ------------#
            interceptor_object.get_corelation_id()
            req_payload = api.payload.copy()
            validation_object.check_invalid_filter_payload_reports(req_payload,tid)
            # ------------ validation ------------#
            validation_object.validate_inp_payload(req_payload)
            # ---------- check clientid ----------#
            client_id = g.client_id
            # ------------- validate clientID --------------#
            self.fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            validation_object.validate_device_id(req_payload)
            # ------------- service response -------------#
            response = self.fortinet_api_service_obj.download_adom_reports(tid,req_payload)
            return response

        except HostRespondedWithErrorException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except HostNotReachableException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""response: {str(error)}""")
            return error
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)


#------------------delete report--------------#
@api.expect(parser)
@api.route("/<string:tid>")
class ReportsDelete(Resource):
    """ Reports Delete."""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, AdomreportsModel.delete_report_response(
        api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def delete(self,tid):
        """
        Report Delete
        """
        try:#------------ Interceptor ------------#
            interceptor_object.get_corelation_id()
            # -------------- logger ---------------#
            logger.info(f""" { request.method } { request.url } """)
            
            # ---------- check clientid ----------#
            client_id = interceptor_object.get_client_id()
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # ------------- validate clientID --------------#
            fortinet_api_service_obj.service_validate_client_id(client_id)
            #validate tid
            validation_object.check_invalid_tid_for_report(tid)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_delete_report_by_tid(tid)
            # -------------- logger ---------------#
            logger.info(f"""response: {str(response)}""")
            return response
        except HostRespondedWithErrorException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except HostNotReachableException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
            ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""response: {str(error)}""")
            return error
        except NoRecordFoundException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""response: {str(ex)}""")
            return error
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)

# --------------List Reports-----------------#
@api.expect(parser_reports_list)
@api.route("/<string:title_code>")
class ReportsList(Resource):
    """ Reports List."""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                            AdomreportsModel.adom_report_data_response(api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @validate_token
    @permission_required(perm= FAI_GET_ADOM_DEVICE_REPORT,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self,title_code=None):
        """
        Report List Get
        """
        try:#------------ Interceptor ------------#
            interceptor_object.get_corelation_id()
            # -------------- logger ---------------#
            logger.info(f""" { request.method } { request.url } """)
            payload = api_converter.convert_args(request.args)
            validation_object.check_invalid_payload_reports(payload,end_point=title_code)
            # ---------- check clientid ----------#
            client_id = interceptor_object.get_client_id()
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # ------------- validate clientID --------------#
            fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_get_report_list_by_title(payload)
            # -------------- logger ---------------#
            logger.info(f"""response: {str(response)}""")
            return response
        except HostRespondedWithErrorException as ex:
            error = ErrorResponse('', str(ex)).get_dict(
            ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except HostNotReachableException as ex:
            error = ErrorResponse('', str(ex)).get_dict(
            ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
            logger.exception(f"""response: {str(error)}""")
            return error
        except TokenCreationException as ex:
            error = ErrorResponse('', str(ex)).get_dict(
            ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
            logger.exception(f"""response: {str(error)}""")
            return error
        except NoRecordFoundException as ex:
            error = [], 200
            logger.exception(f"""response: {str(ex)}""")
            return error
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)
