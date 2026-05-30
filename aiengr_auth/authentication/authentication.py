from rest_framework.authentication import BaseAuthentication, CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .models import AuthToken


# authentication middleware made manually
class CookieTokenAuthentication(BaseAuthentication):
    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie based authentication.
        """
        # cookie auth require csrf protection
        # broweser auto-sends cookies
        # without csrf risky 
        check = CSRFCheck(get_response=lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        # verifies is it coming from the same site if valid compares csrf cookie and header
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
            # which user owns token
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed('Invalid or expired token.')
            
        if not auth_token.user.is_active:
            raise AuthenticationFailed('User account is not active.')
            
        return (auth_token.user, auth_token)