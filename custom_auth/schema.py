from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CookieAuthenticationScheme(OpenApiAuthenticationExtension):
    """Describe the project's HttpOnly access-token cookie for OpenAPI."""

    target_class = 'custom_auth.permissions.CookieAuthentication'
    name = 'CookieAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'access_token',
            'description': (
                'JWT access token in the HttpOnly access_token cookie. '
                'Use POST /auth/login first; Swagger UI sends same-origin cookies automatically.'
            ),
        }
