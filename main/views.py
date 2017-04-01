from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "index.html")
