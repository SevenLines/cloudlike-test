# Create your views here.
import mimetypes

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls.base import reverse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from repository.models import UserFile
from repository.models import File
from repository.models import FileHashedUrl
from repository.serializers import UserFileCreateSerializer, UserFileListSerializer


class UserFilesViewSet(ListModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):
    queryset = UserFile.objects.all().order_by('-id')
    serializer_class = UserFileListSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        # filter returned list by logged user
        queryset = super().filter_queryset(queryset)
        return queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'user': self.request.user
        })
        return context

    def get_serializer_class(self):
        if self.action == 'create':
            return UserFileCreateSerializer
        return super().get_serializer_class()

    def retrieve(self, request, pk, *args, **kwargs):
        """
        Generate hashed file url, and redirect to it
        :pk UserFile id
        """
        user_file = get_object_or_404(UserFile, pk=pk)
        hashed_file = FileHashedUrl.objects.create(file_id=user_file.file_id)
        return redirect(reverse('repository:link', args=[hashed_file.hash, user_file.name]))


class HashedUrlView(APIView):
    def get(self, request, hsh, name):
        # get hashed file using provided hash
        hashed_file = get_object_or_404(FileHashedUrl, hash=hsh)
        file_instance = hashed_file.file
        file = file_instance.file

        # create response, add attachement headers
        response = HttpResponse(file.read(), mimetypes.guess_type(file.name))
        response['Content-Disposition'] = 'attachment; filename="{name}"'.format(
            name=name,
        )
        return response
