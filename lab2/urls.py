
from django.contrib import admin
from django.urls import path, include
from movies.views import pageNotFound, pageBadRequest, pageServerError

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
    path('auth/', include('custom_auth.urls')),
]


