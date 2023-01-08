import logging
from flask.globals import request
from flask_restx import Resource,Namespace
from services.fortinet_api_services import FortinetAPIService
from languages.fortinet_api_languages import ErrorResponse
from languages.constants import HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR, \
        ERROR_CODE_HOST_NOT_REACHABLE,ERROR_CODE_INVALID_TOKEN, \
            HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS,ERROR_CODE_FOR_INTERNAL_SERVER_ERROR, \
                HTTP_STATUS_CODE_BAD_REQUEST,ERROR_CODE_VALIDATION_ERROR
from middleware.token_interceptor import validate_token
from constants import SUCCESS_CODE,SUCCESS_MESSAGE,ERROR_CODE_BAD_REQUEST, \
    ERROR_CODE_BAD_REQUEST_MESSAGE,ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, \
    ERROR_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,INVALID_DEVICE_ID,\
    FAI_GET_ADOM_DEVICE,FAI_GET_ADOM_DEVICE_LIST,FAI_GET_SYSTEM_STATUS,ERROR_CODE_UNAUTHORIZED_ACCESS


from validators.fortinet_api_validations import FortinetAPIValidations
from converters.fortinet_api_converters import FortinetConverters
from utils.fortinet_api_logger import FortinetAPILogger
from api_models.adom_api_model import SystemStatusModel, AdomidModel
from api_models.common_error_api_model import common_error_response
from flask import g
from languages.fortinet_api_exceptions import ValidationException
from fortinet_common.core.decorators import permission_required
#--------------- Middleware --------------------

from languages.fortinet_api_exceptions import HostNotReachableException, \
    HostRespondedWithErrorException,TokenCreationException, handle_exception

from middleware.request_interceptor import FortinetAPIRequestInterceptor
from integrators.fortinet_integrator import FortinetIntegrator

integrator_object = FortinetIntegrator()

logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))
api_converter = FortinetConverters()
# --------------------- gettings Validations ---------------------
validation_object = FortinetAPIValidations()
#--------------- parsers --------------------

api = Namespace(name='adom',description='set of Adom api')
interceptor_object = FortinetAPIRequestInterceptor()

parser = api.parser()
parser.add_argument('Correlationid', location='headers')
parser.add_argument('client_id', location='headers', required=True)

device_parser_api = api.parser()
device_parser_api.add_argument('Correlationid', location='headers')
device_parser_api.add_argument('device_id', location='args')
device_parser_api.add_argument('client_id', location='headers', required=True)


# -------------------- Layers -------------------
# Middleware/Interceptor - picks any required headers for us
# Controller - responsible to deligate substasks to other layers mentioned here
# Validator - usually called inside the service layer for validating input payload,
# or other required data Service - Calls the Integrator and Convertor layers
# -- Integrator - fetches the required data by making required external calls
# -- Convertor - Called when conversion of data is required
# Logger - Used in controller to log incoming request and each request is attached
# a correlation id for identifying each request

# ------------------ End Layers -----------------

# --------------Adom List -----------------#
# @api.expect(parser)
# @api.route("")
# class AdomList(Resource):
#     @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, AdomModel.alladomsdata(api)),
#                         ERROR_CODE_BAD_REQUEST: (
#                                                         ERROR_CODE_BAD_REQUEST_MESSAGE, common_error_response(api)),
#                         ERROR_CODE_UNAUTHORIZED_ACCESS: (
#                                                                 ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, common_error_response(api)),
#                         ERROR_CODE_INTERNAL_SERVER_ERROR: (
#                                                                   ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE, common_error_response(api))})
#     @validate_token
#     def get(self):
#         """
#         This API is used to fetch list of all available adoms
#         """
#         try:
#             #------------ Interceptor ------------#
#             interceptor_object.get_corelation_id()
#             # ------------- service --------------#
#             fortinet_api_service_obj = FortinetAPIService()
#             # ------------- service response -------------#
#             response = fortinet_api_service_obj.service_get_all_adom()
#             # -------------- logger ---------------#
#             logger.info(f"""response: {str(response)}""")
#             return response
#         except HostRespondedWithErrorException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#             ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except HostNotReachableException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#             ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except TokenCreationException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#             ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except Exception as ex:
#             return handle_exception(ex)
# --------------End Adom List -----------------#

# --------------Get Adom by Name -----------------#
# @api.expect(parser)
# @api.route("/<string:adom_name>")
# class Get_adom_by_name(Resource):
#     @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, AdombyNameModel.adomsbynamedata(api)),
#                         ERROR_CODE_BAD_REQUEST: (
#                                 ERROR_CODE_BAD_REQUEST_MESSAGE,
#                                 common_error_response(api)),
#                         ERROR_CODE_UNAUTHORIZED_ACCESS: (
#                                 ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
#                                 common_error_response(api)),
#                         ERROR_CODE_INTERNAL_SERVER_ERROR: (
#                                 ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
#                                 common_error_response(api))})
#     @validate_token
#     def get(self, adom_name=None):
#         """
#         This Api Used to fatch  Adom by Name
#         """
#         try:#------------ Interceptor ------------#
#             interceptor_object.get_corelation_id()
#             # -------------- logger ---------------#
#             logger.info(f""" { request.method } { request.url } """)
#             # ------------- service --------------#
#             fortinet_api_service_obj = FortinetAPIService()
#             # ------------- service response -------------#
#             response = fortinet_api_service_obj.service_get_adom_by_name(adom_name)
#             # -------------- logger ---------------#
#             logger.info(f"""response: {str(response)}""")
#             return response
#         except HostRespondedWithErrorException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#             ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except HostNotReachableException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#                 ERROR_CODE_HOST_NOT_REACHABLE), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except TokenCreationException as ex:
#             error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
#             ERROR_CODE_INVALID_TOKEN), HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS
#             logger.exception(f"""response: {str(error)}""")
#             return error
#         except Exception as ex:
#             return handle_exception(ex)
# --------------End Get Adom by Name -----------------#

# --------------Get Adom devices and device by id-----------------#
@api.expect(device_parser_api)
@api.route("/device")
class AdomAllDevices(Resource):
    """Adom all devices."""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE, AdomidModel.adom_id_response(
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
    @permission_required(perm=lambda *args,**kwargs :  FAI_GET_ADOM_DEVICE if request.args.get('device_id') else FAI_GET_ADOM_DEVICE_LIST,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self):
        """
        This API is used to fetch list of all available adom-devices and adom device by Id
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
            fortinet_api_service_obj.all_user_sites_response = fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            device_id =interceptor_object.get_device_id()
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------ validation ------------#
            if device_id is not None:
                validation_object.validate_dev_id(device_id)
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_get_device_by_id(g.manager_adom_name, device_id,client_id)
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
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)
# --------------End all devices -----------------#


# --------------Get System Status-----------------#
@api.expect(parser)
@api.route("/system-status/<string:device_id>")
class SystemStatus(Resource):
    """System Status."""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       SystemStatusModel.system_status_data(
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
    @permission_required(perm= FAI_GET_SYSTEM_STATUS,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self, device_id=None):
        """
        This API is used to fetch status of  adom-devices
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
            fortinet_api_service_obj.all_user_sites_response = fortinet_api_service_obj.service_validate_client_id(client_id)
            # ------------ Interceptor ------------#
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            # ------------ validation ------------#
            if device_id is None:
                raise ValidationException(INVALID_DEVICE_ID)
            else:
                validation_object.validate_dev_id(device_id)
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_get_system_status(g.manager_adom_name,device_id)
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
        except ValidationException as ex:
            error = ErrorResponse('', str(ex), HTTP_STATUS_CODE_BAD_REQUEST).get_dict(
            ERROR_CODE_VALIDATION_ERROR), HTTP_STATUS_CODE_BAD_REQUEST
            logger.exception(f"""error: {str(ex)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)
