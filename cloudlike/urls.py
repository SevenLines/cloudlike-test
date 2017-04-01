from django.conf.urls import url, include
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView

import main.views

urlpatterns = [
    url('^register/', CreateView.as_view(
        template_name='register.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name="register"),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^repository/', include('repository.urls', namespace='repository')),
    url(r'^$', main.views.IndexView.as_view(), name='index'),
]
