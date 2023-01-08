class ErrorResponse:
    def __init__(self, error_code, error_auxiliary, error_message):
        self.error_code = error_code
        self.error_auxiliary = error_auxiliary
        self.error_message = error_message

    def get_dict(self):
        return {
            "error-code": self.error_code,
            "error-auxiliary": self.error_auxiliary,
            "error-message": self.error_message
        }
