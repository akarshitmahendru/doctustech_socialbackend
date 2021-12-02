from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import apis

router = DefaultRouter()
router.register('feed', apis.UploadImageAPI, basename='feed')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'leave-a-like/', apis.UserLikeActionAPI.as_view(),
        name='likes'),
    url(r'leave-a-comment/', apis.UserCommentsAPI.as_view(),
        name='comments')
]
