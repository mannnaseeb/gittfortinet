import logging
from flask.globals import request
from flask import g
from flask_restx import Resource, Namespace
from services.fortinet_api_services import FortinetAPIService
from languages.fortinet_api_languages import ErrorResponse
from languages.constants import HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_INVALID_TOKEN, \
        HTTP_STATUS_CODE_UNAUTHORIZED_ACCESS,ERROR_CODE_FOR_INTERNAL_SERVER_ERROR, \
            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR,ERROR_CODE_HOST_NOT_REACHABLE, \
                HTTP_STATUS_CODE_BAD_REQUEST,ERROR_CODE_VALIDATION_ERROR, FILE_DOES_NOT_EXIST, ADOM_LIST_EMPTY
from validators.fortinet_api_validations import FortinetAPIValidations
from middleware.request_interceptor import FortinetAPIRequestInterceptor
from utils.fortinet_api_logger import FortinetAPILogger
from languages.fortinet_api_exceptions import TokenCreationException, \
    HostRespondedWithErrorException,HostNotReachableException, \
        ValidationException,handle_exception

from fortinet_common.core.decorators import permission_required
from api_models.metric_api_model import MetricsModel
from middleware.token_interceptor import validate_token
from api_models.common_error_api_model import common_error_response
from constants import SUCCESS_CODE,SUCCESS_MESSAGE,ERROR_CODE_BAD_REQUEST, \
    ERROR_CODE_BAD_REQUEST_MESSAGE,ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE, \
        ERROR_CODE_INTERNAL_SERVER_ERROR,ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE, \
            INSTANT_METRIC_POSITION,TIMESERIES_METRIC_POISTION, FILTER_BY_DEVICE_ID, \
                DEVID_OPERATOR, FILTER_BY_CLIENT_ID, WIDGET_TRAFFIC_SUMMARY, WIDGET_BANDWIDTH_SUMMARY, \
                    WIDGET_SLA_PERFORMANCE, WIDGET_SITE_DETAILS,FAI_GET_METRICS,ERROR_CODE_UNAUTHORIZED_ACCESS

from caching import cache
from utils.rest_keygen import RestKeyGen
from integrators.fortinet_integrator import FortinetIntegrator
from db_settings.db_utils import get_metrics_with_devid_filter
import json
import os
from flask import request
import copy

integrator_object = FortinetIntegrator()

api = Namespace('metrics', description='List of Classifiers and data')

rest_keygen = RestKeyGen()

# --------------- Middleware --------------------
interceptor_object = FortinetAPIRequestInterceptor()
# ---------------End  Middleware --------------------

# --------------------- gettings Validations ---------------------
validation_object = FortinetAPIValidations()
# ---------------- gettings Validations ENDS HERE ----------------
logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))

# --------------- parsers --------------------
parser = api.parser()
classifers_parser = api.parser()
parser.add_argument('Correlationid', location='headers')
parser.add_argument('user-id', location='headers')
parser.add_argument('person-id', location='headers')
classifers_parser.add_argument('Correlationid', location='headers')


# -------------End  parsers ------------------

# ------------- Get List Of Classifiers And Data ---------------
@api.expect(classifers_parser)
@api.route("")
class GetListOfClassifiersAndData(Resource):
    """List Of Classifiers And Data."""
    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       MetricsModel.metric_metadata(api)),
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
    @permission_required(perm= FAI_GET_METRICS,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def get(self):
        """
        Get List Of Classifiers And Data
        """
        try:
            # ----------- Interceptor ------------#
            interceptor_object.get_corelation_id()
            # ------------- logger ---------------#
            logger.info(f""" {request.method} {request.url} """)
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # ------------- service response -------------#
            response = fortinet_api_service_obj.service_get_classifiers_and_data()
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

def remove_client_id(req_payload):
    if 'filter' in req_payload:
        hold_filter = []
        for filter in req_payload.get('filter', []):
            if filter.get('key', '') != FILTER_BY_CLIENT_ID:
                hold_filter.append(filter)
        if hold_filter:
            req_payload['filter'] = hold_filter
        else:
            req_payload.pop('filter', None)

def add_devids_to_filter(endpoint, req_payload, client_id, fortinet_api_service_obj):
    filter_options = req_payload.get('filter', [])
    #Check from source of truth (databse) if endpoint requires devid
    if get_metrics_with_devid_filter(endpoint):
        all_devices = [filters.get('value') for filters in filter_options if
         filters.get('key', '') == FILTER_BY_DEVICE_ID]
        hold_filter = []
        for filter in req_payload.get('filter', []):
            if filter.get('key', '') != FILTER_BY_DEVICE_ID:
                hold_filter.append(filter)
        if hold_filter:
            req_payload['filter'] = hold_filter
        else:
            req_payload.pop('filter', None)

        #If filter in payload does not contain devid, attach devids
        if not all_devices:
            all_devices = []
            #---------- Fetch all adom devices ----------

            adom_devices = fortinet_api_service_obj.service_get_device_by_id(g.analyzer_adom_name, None, client_id)
            all_devices.extend([device.get('serial_number') for device in adom_devices.get('data', []) if device.get('serial_number') ])
            # ----- Fetch all adom devices ENDS HERE ----
        if all_devices:
            hold_devid_filters = []
            for devid in all_devices:
                hold_devid_filters.append({FILTER_BY_DEVICE_ID:devid})
            #-------- Attach to payload ---------
            req_payload['device'] = hold_devid_filters
            # --- Attach to payload ENDS HERE ---
    return req_payload

# ----------- List Of Classifiers And Data ENDS HERE -----------
@api.expect(parser)
@api.route("/<string:metric_name>/instant")
class InstantMetric(Resource):
    """Instant Metric."""

    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       MetricsModel.metric_response(api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @api.expect(MetricsModel.paylaod(api))
    @cache.cached(make_cache_key=rest_keygen.make_metric_cache_key,
                  response_filter=lambda response: False if (
                          type(response) == tuple and response[1] in range(400, 600)) else True)
    @validate_token
    @permission_required(perm= FAI_GET_METRICS,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def post(self, metric_name=None):
        """
            This is instant api for metric
        """

        try:
            # -------------- logger --------------#
            request_payload = copy.deepcopy(api.payload) if api.payload else "Not applicable"
            logger.info(f""" {request.method} {request.url} request payload: {request_payload} request headers: {request.headers} """)
            # ------------ validation ------------#
            req_payload = copy.deepcopy(api.payload)
            validation_object.check_invalid_payload(req_payload, metric_name, INSTANT_METRIC_POSITION)
            validation_object.check_filter(req_payload, metric_name, INSTANT_METRIC_POSITION)
            # ---------- check clientid ----------#
            client_id = g.client_id
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # ---------- check userid ----------#
            user_id = interceptor_object.get_user_id()
            validation_object.check_client_id_association(client_id, user_id)
            # ------------ Interceptor -----------#
            interceptor_object.get_corelation_id()
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'clientId': client_id}))
            validation_object.validate_device_id(request_payload)
            # --------- attach devids ------------#
            if metric_name not in [WIDGET_TRAFFIC_SUMMARY, WIDGET_SLA_PERFORMANCE, WIDGET_BANDWIDTH_SUMMARY, WIDGET_SITE_DETAILS]:
                req_payload = add_devids_to_filter(metric_name, request_payload, client_id, fortinet_api_service_obj)
            remove_client_id(req_payload)
            # --------- service response ---------#
            response = fortinet_api_service_obj.service_get_instant_metric(req_payload, metric_name)
            # -------------- logger ---------------#
            logger.info(f"""response: {str(response)}""")
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
            logger.exception(f"""response: {str(error)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)

@api.expect(parser)
@api.route("/<string:metric_name>/timeseries")
class TimeSeriesMetric(Resource):

    @api.doc(responses={SUCCESS_CODE: (SUCCESS_MESSAGE,
                                       MetricsModel.metric_response(api)),
                        ERROR_CODE_BAD_REQUEST: (
                                ERROR_CODE_BAD_REQUEST_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_UNAUTHORIZED_ACCESS: (
                                ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE,
                                common_error_response(api)),
                        ERROR_CODE_INTERNAL_SERVER_ERROR: (
                                ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE,
                                common_error_response(api))})
    @api.expect(MetricsModel.paylaod(api))
    @cache.cached(make_cache_key=rest_keygen.make_metric_cache_key,
                  response_filter=lambda response: False if (
                          type(response) == tuple and response[1] in range(400, 600)) else True)
    @validate_token
    @permission_required(perm= FAI_GET_METRICS,
                         get_curr_user_perm=lambda: g.current_user_perm)
    def post(self, metric_name=None):
        """
            This is timeseries api for metric
        """
        try:
            # -------------- logger --------------#
            request_payload = copy.deepcopy(api.payload) if api.payload else "Not applicable"
            logger.info(f""" {request.method} {request.url} request payload: {request_payload} request headers: {request.headers} """)
            # ------------ validation ------------#
            req_payload = copy.deepcopy(api.payload)
            validation_object.check_invalid_payload(req_payload, metric_name, TIMESERIES_METRIC_POISTION)
            validation_object.check_filter(req_payload, metric_name, TIMESERIES_METRIC_POISTION)
            # ---------- check clientid ----------#
            client_id = g.client_id
            # ---------- check userid ----------#
            user_id = interceptor_object.get_user_id()
            validation_object.check_client_id_association(client_id,user_id)
            # ------------ Interceptor -----------#
            interceptor_object.get_corelation_id()
            interceptor_object.set_base64_ip(integrator_object.get_clients_of_user({'client_id': client_id}))
            validation_object.validate_device_id(request_payload)
            # ------------- service --------------#
            fortinet_api_service_obj = FortinetAPIService()
            # --------- service response ---------#
            response = fortinet_api_service_obj.service_get_timeseries_metric(req_payload, metric_name)
            # -------------- logger ---------------#
            logger.info(f"""response: {str(response)}""")
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
            logger.exception(f"""response: {str(error)}""")
            return error
        except Exception as ex:
            return handle_exception(ex)
