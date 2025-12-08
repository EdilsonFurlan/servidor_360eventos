from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """
    Extends TokenAuthentication to support 'Bearer' keyword
    instead of the default 'Token' keyword.
    Compatible with the Android App's AuthInterceptor.
    """
    keyword = 'Bearer'
