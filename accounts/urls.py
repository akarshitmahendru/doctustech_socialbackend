from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^registration/$', apis.RegistrationAPI.as_view(), name='register'),
    url(r'^verify-otp/$', apis.VerifyOTPView.as_view(), name='verify'),
    url(r'^search-users/$', apis.SearchUsersAPI.as_view(), name='search'),
]