# Create your views here.
import mimetypes
import os

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

from repository.models import UserFile, File, FileHashedUrl
from repository.serializers import UserFileSerializer


class UserFilesViewSet(ListModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):
    queryset = UserFile.objects.all()
    serializer_class = UserFileSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        return super().get_permissions()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        file = File.objects.create(file=request.data['file'])
        user_file = UserFile.objects.create(
            user=request.user,
            name=request.data['name'],
            file=file
        )

        serializer = self.get_serializer(user_file)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk, *args, **kwargs):
        user_file = get_object_or_404(UserFile, pk=pk)
        hashed_file = FileHashedUrl.objects.create(file_id=user_file.file_id)
        return redirect(reverse('repository:link', args=[hashed_file.hash, user_file.name]))


class HashedUrlView(APIView):
    def get(self, request, hsh, name):
        hashed_file = get_object_or_404(FileHashedUrl, hash=hsh)
        file_instance = hashed_file.file
        file = file_instance.file
        response = HttpResponse(file.read(), mimetypes.guess_type(file.name))
        response['Content-Disposition'] = 'attachment; filename="{name}.{ext}"'.format(
            name=name,
            ext=file.name.split('.')[-1]
        )
        return response
