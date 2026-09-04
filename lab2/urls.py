
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from movies.views import pageNotFound, pageBadRequest, pageServerError

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
    path('auth/', include('custom_auth.urls')),
]

if settings.APP_ENV != 'production':
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]


