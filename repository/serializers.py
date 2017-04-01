from django.conf import settings
from rest_framework import serializers

from repository.exceptions import FileLimitExceedApiException
from repository.models import UserFile, File


class UserFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ('id', 'name')


class UserFileCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = UserFile
        fields = ('id', 'name', 'file')

    def create(self, validated_data):
        user = self.context.get('user')
        file_ext = validated_data['file'].name.split('.')[-1]
        file_name = validated_data['file'].name if not validated_data['name'] \
            else "{}.{}".format(validated_data['name'], file_ext)

        # check that we not exceed file count limit
        if UserFile.objects.filter(user=user).count() >= settings.MAX_FILES_COUNT:
            raise FileLimitExceedApiException("File limit for user {} was exceeded".format(user))

        # get or create file
        file, is_duplicate = \
            File.objects.create_and_check_for_duplicate(file=validated_data['file'])

        return super().create({
            'user': user,
            'name': file_name,
            'original': not is_duplicate,
            'file': file,
        })
