from rest_framework import serializers

from repository.models import UserFile, File


class UserFileSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserFile
        fields = ('id', 'file', 'name', 'user')
