"""doctustech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="DoctusTech Social Backend",
      default_version='v1',
      description="DoctusTech Social Backend Endpoint Description",
      contact=openapi.Contact(email="arun.bhatt077@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

apis = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include("accounts.urls")),
    url(r'^api/v1/', include("social_feed.urls")),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

urlpatterns = [
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger'),
 ] + apis

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)