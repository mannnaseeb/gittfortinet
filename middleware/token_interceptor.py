import logging
from flask import request
from flask import g
from fortinet_common.core.im import IdentityManager
from fortinet_common import APIService

api_service = APIService.get_instance()
from utils.fortinet_api_logger import FortinetAPILogger
from languages.fortinet_api_languages import ErrorResponse
from languages.constants import ERROR_CODE_INVALID_TOKEN,ERROR_CODE_FOR_INTERNAL_SERVER_ERROR,\
                        USER_PERMISSION_FETCHING_ERROR
from constants import FORTINET_IM_SERVER_BASE_URL,FORTINET_IM_SERVER_GET_USER_URL, \
    SUCCESS_CODE,ERROR_CODE_UNAUTHORIZED_ACCESS,FORTINET_IM_SERVER_USERNAME,FORTINET_IM_SERVER_PASSWORD, \
        FORTINET_IM_SERVER_GRANT_TYPE,FORTINET_IM_SERVER_CLIENT_ID,FORTINET_IM_SERVER_TOKEN_GENERATION
from .constants import AUTHORIZATION,TOKEN_ERROR_MESSAGE,TOKEN_VALIDATION_ERROR, \
    IMPROPER_TOKEN_RESPONSE

from .request_interceptor import FortinetAPIRequestInterceptor

logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))

# --------------- Middleware --------------------
interceptor_object = FortinetAPIRequestInterceptor()
im_service = IdentityManager()
# ---------------End  Middleware --------------------


# decorator to authenticate gtt gui token
# Note: By default a Python function returns None unless a return value is specified
def validate_token(func):
    """validate token"""
    def authenticate_token(*args, **kwargs):
        # ------------ Interceptor ------------#
        interceptor_object.get_corelation_id()
        # -------------- logger ---------------#
        logger.info(f""" {request.method} {request.url} """)
        # ------------ Interceptor ------------#
        if validate_token := interceptor_object.get_token():
            # -------- Check token validity -------#
            headers = {AUTHORIZATION: f"BEARER {validate_token}"}
            # ---------- service response ---------#
            response = api_service.post(FORTINET_IM_SERVER_BASE_URL + FORTINET_IM_SERVER_GET_USER_URL, headers=headers)
        if validate_token is None or (response.status != SUCCESS_CODE and type(
                response.original_response.json()) == dict and 'error' in response.original_response.json()):
            # ---------- error response -----------#
            error = ErrorResponse(error_message=TOKEN_ERROR_MESSAGE, error_auxiliary=TOKEN_VALIDATION_ERROR).get_dict(ERROR_CODE_INVALID_TOKEN), ERROR_CODE_UNAUTHORIZED_ACCESS
            # -------------- logger ---------------#
            logger.exception(f"""response: {str(error)}""")
            return error
        else:
            g.userId = request.headers.get('person-id', None)
            if g.userId == None:
                if type(response.data) == dict:
                    g.userId = response.data.get('person-id', None)
            #----------- Setting user permissions -----------
            try:
                g.current_user_perm = im_service.get_current_user_perms(interceptor_object.get_token())
            except Exception as ex:
                error = {'error-code': ERROR_CODE_FOR_INTERNAL_SERVER_ERROR,
                         'error-auxiliary': USER_PERMISSION_FETCHING_ERROR,
                         'error-message': str(ex)}
                return error, ERROR_CODE_FOR_INTERNAL_SERVER_ERROR
            #------ Setting user permissions ENDS HERE ------
        return func(*args, **kwargs)

    return authenticate_token


def im_generate_token(*args, **kwargs):
    """generate token"""
    body, body['username'], body['password'], body['grant_type'], body[
        'client_id'] = {}, FORTINET_IM_SERVER_USERNAME, FORTINET_IM_SERVER_PASSWORD, FORTINET_IM_SERVER_GRANT_TYPE, FORTINET_IM_SERVER_CLIENT_ID
    response = api_service.post(FORTINET_IM_SERVER_TOKEN_GENERATION, data=body)
    if not response or response.data is None:
        raise Exception(TOKEN_ERROR_MESSAGE, ERROR_CODE_INVALID_TOKEN)
    if not response.data.get('access_token'):
        raise Exception(IMPROPER_TOKEN_RESPONSE, ERROR_CODE_INVALID_TOKEN)
    return response
