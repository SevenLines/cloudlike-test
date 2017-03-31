from django.conf.urls import url, include

urlpatterns = [
    url(r'^repository/', include('repository.urls', namespace='repository')),
]
