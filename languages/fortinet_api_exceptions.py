import logging
from languages.fortinet_api_languages import ErrorResponse
from utils.fortinet_api_logger import FortinetAPILogger
from .constants import ERROR_CODE_FOR_INTERNAL_SERVER_ERROR,HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
logger = FortinetAPILogger(logging.getLogger('gunicorn.error'))

class ValidationException(Exception):
    """Exception raised for validation errors in fortinet API"""
    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        """wrapped exception"""
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message}'

class HostNotReachableException(Exception):
    """Exception raised when Host is down"""
    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message}'

class HostRespondedWithErrorException(Exception):
    """Exception raised when Host responds with error"""
    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message}'

class HostAnalyzerRespondedWithErrorException(Exception):
    """Exception raised when Host responds with error"""
    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message}'

class TokenCreationException(Exception):

    """Exception raised for errors in the Token Generation """

    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message} wrapped ex:  {str(self.wrapped_exception)}'

class NoRecordFoundException(Exception):
    """Exception raised for No Record found in database in fortinet API"""
    def __init__(self, message, wrapped_ex=None):
        self.message = message
        self.wrapped_exception = wrapped_ex
        super().__init__(message)

    def get_wrapped_exception(self):
        return self.wrapped_exception

    def __str__(self):
        return f'{self.message}'

def handle_exception(ex):
    """Handle Exception """
    # ---------- setting default values ---------
    error_code = ERROR_CODE_FOR_INTERNAL_SERVER_ERROR
    error_message = str(ex)
    status_code = HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR
    # ---- setting default values ENDS HERE ----
    # --------- checking for arguments sent in expection ---------
    if hasattr(ex, 'args') and type(ex.args) == tuple and ex.args:
        #converting tuple to dictionary since we can easily fetch values without errors using .get function
        error_details = {index: item for index, item in enumerate(ex.args)}
        error_message = error_details.get(0, None)
        error_code = error_details.get(1, ERROR_CODE_FOR_INTERNAL_SERVER_ERROR)
        status_code = error_details.get(2, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR)
    # ---- checking for arguments sent in expection ENDS HERE ---
    error = ErrorResponse('', error_message, HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR).get_dict(
        error_code), status_code
    logger.exception(f"""response: {str(error)}""")
    return error
