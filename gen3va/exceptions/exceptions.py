"""Application-specific exceptions, useful for normalizing output to the
front-end.
"""


class Gen3vaException(Exception):
    """Base exception for serializing all exceptions for JSON.
    """

    def __init__(self, message, python_error=None, status_code=500):
        super(Gen3vaException, self).__init__(message)
        self.message = message
        self.python_error = python_error
        self.status_code = status_code

    @property
    def serialize(self):
        result = {
            'error': self.message
        }
        if self.python_error:
            result['python_error'] = str(self.python_error)
            result['error_type'] = type(self.python_error).__name__
        return result


class UserInputException(Gen3vaException):
    """Exception to be raised when erroring on user input.
    """

    def __init__(self, message, python_error=None, status_code=400):
        super(UserInputException, self).__init__(message, python_error,
                                                 status_code)