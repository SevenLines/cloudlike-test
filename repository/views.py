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
from repository.serializers import UserFileSerializer


class UserFilesViewSet(ListModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):
    queryset = UserFile.objects.all().order_by('-id')
    serializer_class = UserFileSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        form_file = request.data['file']
        file_name = form_file.name if not request.data.get('name') \
            else "{}.{}".format(request.data['name'], form_file.name.split('.')[-1])

        file, is_duplicate = File.objects.create_and_check_for_duplicate(file=form_file)

        user_file = UserFile.objects.create(
            user=request.user,
            name=file_name,
            original=not is_duplicate,
            file=file
        )

        serializer = self.get_serializer(user_file)
        headers = self.get_success_headers(serializer.data)

        data = serializer.data
        if is_duplicate:
            user_of_original = User.objects.filter(
                pk__in=UserFile.objects.filter(original=True, file_id=file.pk).values('user')
            ).first()
            if user_of_original:
                data.update({
                    'user_of_original': user_of_original.username
                })
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

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
        response['Content-Disposition'] = 'attachment; filename="{name}"'.format(
            name=name,
        )
        return response
