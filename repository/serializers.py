from rest_framework import serializers

from repository.models import UserFile, File


class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ('id', 'name')
