from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^registration/$', apis.RegistrationAPI.as_view(), name='register'),
    url(r'^verify-otp/$', apis.VerifyOTPView.as_view(), name='verify'),
    url(r'^login/$', apis.LoginView.as_view(), name='login'),
    url(r'^logout/$', apis.LogOutView.as_view(), name='logout'),
    url(r'^user-info/$', apis.UserInfo.as_view(), name='user-info'),
    url(r'^search-users/$', apis.SearchUsersAPI.as_view(), name='search'),
    url(r'^send-request/$', apis.InvitationAPI.as_view(), name='invitation'),
    url(r'^my-requests/$', apis.MyFriendRequests.as_view(), name='requests'),
]