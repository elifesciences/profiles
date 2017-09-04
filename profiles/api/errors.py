class OAuth2Error(Exception):
    error = None
    description = None
    status_code = 400

    def __init__(self, description=None):
        message = '(' + self.error + ')'

        if description:
            self.description = description
            message += ' ' + description

        super(OAuth2Error, self).__init__(message)


class InvalidClient(OAuth2Error):
    error = 'invalid_client'
    status_code = 401


class InvalidGrant(OAuth2Error):
    error = 'invalid_grant'


class InvalidRequest(OAuth2Error):
    error = 'invalid_request'


class UnsupportedGrantType(OAuth2Error):
    error = 'unsupported_grant_type'
