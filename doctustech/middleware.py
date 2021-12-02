from django.views.debug import technical_500_response
import sys
from django.utils.deprecation import MiddlewareMixin


class UserBasedExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        return technical_500_response(request, *sys.exc_info())