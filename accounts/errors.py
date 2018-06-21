class LineAccountInactiveError(Exception):

    def __init__(self, message='This LINE account is inactive'):
        super(LineAccountInactiveError, self).__init__(message)
