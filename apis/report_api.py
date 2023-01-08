"""report api module"""
import logging
from flask.globals import request
from flask_restx import Resource, Namespace
from constants import SUCCESS_CODE, SUCCESS_MESSAGE, \
    ERROR_CODE_BAD_REQUEST, ERROR_CODE_BAD_REQUEST_MESSAGE, \
        ERROR_CODE_UNAUTHORIZED_ACCESS,ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, \
            ERROR_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE
from services.fortinet_api_services import FortinetAPIService
from validators.fortinet_api_validations import FortinetAPIValidations
from middleware.request_interceptor import FortinetAPIRequestInterceptor
from middleware.token_interceptor import validate_token
from utils.fortinet_api_logger import FortinetAPILogger
from languages.fortinet_api_languages import ErrorResponse
from languages.fortinet_api_exceptions import TokenCreationException,handle_exception, \
    HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR, ERROR_CODE_FOR_INTERNAL_SERVER_ERROR
from api_models.report_api_model import report_meta_response
from api_models.common_error_api_model import common_error_response
from languages.constants import ERROR_CODE_INVALID_TOKEN,HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS

api = Namespace('report_meta', description='List of Report Meta Data')

# --------------- Middleware --------------------
interceptor_object = FortinetAPIRequestInterceptor()
# ---------------End  Middleware --------------------

# --------------------- gettings Validations ---------------------
validation_object = FortinetAPIValidations()
# ---------------- gettings Validations ENDS HERE ----------------
logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))

# --------------- parsers --------------------
parser = api.parser()
parser.add_argument('Correlationid', location='headers')
# -------------End  parsers ------------------

@api.expect(parser)
@api.route("")
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
