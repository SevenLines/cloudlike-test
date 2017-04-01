from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from repository.views import UserFilesViewSet, HashedUrlView

router = DefaultRouter()
router.register('files', UserFilesViewSet, 'files')

urlpatterns = [
    url(r'^link/(?P<hsh>\w+).(?P<name>.*?)$', HashedUrlView.as_view(), name="link"),
    url(r'^', include(router.urls)),
]
