
import uuid
import base64
from flask import g, request
from constants import IP_TO_BASE64_CONVERSION_FAILED, ADOM_NAME_ERROR_CODE_IN_ANALYZER,\
    TYPE_FORTIGATE_ANALYZER, TYPE_FORTIGATE_MANAGER, INVALID_CLIENT_ID
from languages.constants import ERROR_CODE_CLIENT_API_WITH_ERROR,\
        ERROR_CODE_VALIDATION_ERROR,HTTP_STATUS_CODE_BAD_REQUEST


class FortinetAPIRequestInterceptor:
    """Fortinet API Request Interceptor"""

    def get_corelation_id(self):
        """This will generate  corelational id """
        correlation_id = request.headers.get(
            'Correlationid') or str(uuid.uuid4())
        g.Correlationid = correlation_id
        return correlation_id

    def get_device_id(self):
        """ This Will get the device id from the args """
        device_id = request.args.get('device_id', None)
        return device_id

    def get_token(self):
        """ This method will return the token """
        auth_header = request.headers.get('Authorization')
        g.access_token = ""
        if auth_header:
            auth_token = auth_header.split(" ")
            #------- check for proper Bearer format -------
            if len(auth_token) == 2 and auth_token[0] == 'Bearer':
                token_index = 1
                if type(auth_token) is list and token_index <= len(auth_token):
                    validate_token = auth_token[1]
                g.access_token = auth_token[1]
                return validate_token

    def remove_unwanted_payload(self):
        """ This method will remove unwanted payload """
        input_payload = request.json
        input_payload.pop('sort-by', None)
        input_payload.pop('limit', None)
        return input_payload


    def get_client_id(self):
        """This will get client id from headers"""
        client_id = request.headers.get('client-id', None)
        if not client_id:
            raise Exception(INVALID_CLIENT_ID, ERROR_CODE_VALIDATION_ERROR,
                HTTP_STATUS_CODE_BAD_REQUEST)
        return client_id

    def set_base64_ip(self, user_clients_response):
        """Sets analyzer ip after converting base64"""
        try:
            # ------------------ checking client API response for error -------------------
            if 'error-code' in (
            error_message := user_clients_response.original_response.json()) and \
                    error_message[
                        'error-code'] != ADOM_NAME_ERROR_CODE_IN_ANALYZER:
                raise Exception(
                    self.raise_host_responded_with_error(user_clients_response),
                    ERROR_CODE_CLIENT_API_WITH_ERROR)
            # ------------- checking client API response for error ENDS HERE -------------
            fortinet_addresses = next(iter(user_clients_response.data), {}).get('fortinet', '')
            manager_ip_address = ''.join([client.get('ip', '') for client in fortinet_addresses if client.get('type', '') == TYPE_FORTIGATE_MANAGER])
            analyzer_ip_address = ''.join([client.get('ip', '') for client in fortinet_addresses if client.get('type', '') == TYPE_FORTIGATE_ANALYZER])
            g.analyzer_ip = base64.b64encode(bytes(analyzer_ip_address, 'utf-8')).decode('utf-8')
            g.manager_ip = base64.b64encode(bytes(manager_ip_address, 'utf-8')).decode('utf-8')
            g.analyzer_adom_name = ''.join([client.get('domain', '') for client in fortinet_addresses if client.get('type', '') == TYPE_FORTIGATE_ANALYZER])
            g.manager_adom_name = ''.join([client.get('domain', '') for client in fortinet_addresses if client.get('type', '') == TYPE_FORTIGATE_MANAGER])
            if g.analyzer_adom_name != g.manager_adom_name :
                raise Exception(
                    self.raise_host_responded_with_error(user_clients_response),
                    ERROR_CODE_CLIENT_API_WITH_ERROR)
        except Exception as e:
            raise Exception(IP_TO_BASE64_CONVERSION_FAILED)

    def get_user_id(self):
        """This will get user id from headers"""
        user_id = request.headers.get('user-id', None)
        return user_id
