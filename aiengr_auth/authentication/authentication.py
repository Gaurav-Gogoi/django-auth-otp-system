from rest_framework.authentication import BaseAuthentication, CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .models import AuthToken

class CookieTokenAuthentication(BaseAuthentication):
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie based authentication.
        """
        check = CSRFCheck(get_response=lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f'CSRF Failed: {reason}')

    def authenticate(self, request):
        token = request.COOKIES.get('auth_token')
        if not token:
            return None
        
        # ENFORCE CSRF VALIDATION HERE
        self.enforce_csrf(request)

        try:
            auth_token = AuthToken.objects.select_related('user').get(token=token)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid or expired token.')
            
        if not auth_token.user.is_active:
            raise AuthenticationFailed('User account is not active.')
            
        return (auth_token.user, auth_token)