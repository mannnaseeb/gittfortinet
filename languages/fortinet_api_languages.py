from languages.constants import ERROR_MESSAGE_UNAUTHORIZED_ACCESS ,ERROR_MESSAGE_INTERNAL_SERVER_ERROR,ERROR_UNAUTHORIZED_ACCESS, \
    ERROR_MESSAGE_REQUEST_FAIL ,ERROR_MESSAGE_VALIDATION_ERROR, ERROR_MESSAGE_HOST_NOT_REACHABLE,ERROR_MESSAGE_MANAGER_RESPONDED_WITH_ERROR, \
        ERROR_MESSAGE_ANALYZER_RESPONDED_WITH_ERROR,ERROR_MESSAGE_CLIENT_API_RESPONDED_WITH_ERROR, \
            TOKEN_ERROR_MESSAGE ,TOKEN_ERROR ,ERROR_CODE_TOKEN_ERROR ,ERROR_CODE_FOR_INTERNAL_SERVER_ERROR,ERROR_CODE_UNAUTHORIZED_ACCESS, \
                ERROR_CODE_API_ERROR ,ERROR_CODE_VALIDATION_ERROR,ERROR_CODE_HOST_NOT_REACHABLE, \
                    ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR,ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR,ERROR_CODE_CLIENT_API_WITH_ERROR


class ErrorResponse:
    """
    summary: Returns Error Responses
    description: This class is used to return response when any error or exception has occurred
    parameters:
        - error_auxiliary: `str`
        - error_message : `str`
    methods:
        get_dict() :
            - Returns the error response for the api.
            - Response contains error_code, error_auxiliary and error_message
    """

    def __init__(self, error_auxiliary=None, error_message=None, http_status_code=None):
        self.error_auxiliary = error_auxiliary
        self.error_message = error_message
        self.http_status_code = http_status_code
        self.error_dict = {
            ERROR_CODE_TOKEN_ERROR: {'error-code': ERROR_CODE_TOKEN_ERROR, 'error-auxiliary': TOKEN_ERROR_MESSAGE, 'error-message': TOKEN_ERROR},
            ERROR_CODE_FOR_INTERNAL_SERVER_ERROR: {'error-code': ERROR_CODE_FOR_INTERNAL_SERVER_ERROR, 'error-auxiliary': ERROR_MESSAGE_INTERNAL_SERVER_ERROR,
                   'error-message': ERROR_MESSAGE_INTERNAL_SERVER_ERROR},
            ERROR_CODE_UNAUTHORIZED_ACCESS: {'error-code': ERROR_CODE_UNAUTHORIZED_ACCESS, 'error-auxiliary': ERROR_MESSAGE_UNAUTHORIZED_ACCESS,
                   'error-message': ERROR_UNAUTHORIZED_ACCESS},
            ERROR_CODE_API_ERROR: {'error-code': ERROR_CODE_API_ERROR, 'error-auxiliary': ERROR_MESSAGE_REQUEST_FAIL,
                   'error-message': ERROR_MESSAGE_REQUEST_FAIL},
            ERROR_CODE_VALIDATION_ERROR: {'error-code': ERROR_CODE_VALIDATION_ERROR, 'error-auxiliary': ERROR_MESSAGE_VALIDATION_ERROR,
                   'error-message': ERROR_MESSAGE_VALIDATION_ERROR},
            ERROR_CODE_HOST_NOT_REACHABLE: {'error-code': ERROR_CODE_HOST_NOT_REACHABLE, 'error-auxiliary': ERROR_MESSAGE_HOST_NOT_REACHABLE,
                   'error-message': ERROR_MESSAGE_HOST_NOT_REACHABLE},
            ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR: {'error-code': ERROR_CODE_MANAGER_RESPONDED_WITH_ERROR, 'error-auxiliary': ERROR_MESSAGE_MANAGER_RESPONDED_WITH_ERROR,
                   'error-message': ERROR_MESSAGE_MANAGER_RESPONDED_WITH_ERROR},
            ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR: {'error-code': ERROR_CODE_ANALYZER_RESPONDED_WITH_ERROR,
                                                      'error-auxiliary': ERROR_MESSAGE_ANALYZER_RESPONDED_WITH_ERROR,
                                                      'error-message': ERROR_MESSAGE_ANALYZER_RESPONDED_WITH_ERROR},
            ERROR_CODE_CLIENT_API_WITH_ERROR: {'error-code': ERROR_CODE_CLIENT_API_WITH_ERROR,
                                                       'error-auxiliary': ERROR_MESSAGE_CLIENT_API_RESPONDED_WITH_ERROR,
                                                       'error-message': ERROR_MESSAGE_CLIENT_API_RESPONDED_WITH_ERROR},
        }

    def get_dict(self, error_code):
        """
        creates a dict that can be sent as response for errors
        :param error_code: code of the error
        :return: a dict with error information
        """
        error_dict = self.error_dict.get(error_code)
        if self.error_message:
            error_dict['error-message'] = self.error_message
        if self.error_auxiliary:
            error_dict['error-auxiliary'] = self.error_auxiliary
        return error_dict
