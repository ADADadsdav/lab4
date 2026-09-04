from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated
from rest_framework.authentication import BaseAuthentication


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Проверяем владение объектом
        return obj.user == request.user


class IsCookieAuthenticated(BasePermission):
    """Require a valid user populated by the cookie middleware (401, not 403)."""
    def has_permission(self, request, view):
        if not getattr(request.user, 'is_authenticated', False):
            raise NotAuthenticated()
        return True


class CookieAuthentication(BaseAuthentication):
    """Expose the user resolved by AuthenticationMiddleware to DRF."""
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if getattr(user, 'is_authenticated', False):
            return (user, None)
        return None

    def authenticate_header(self, request):
        return 'Cookie'
