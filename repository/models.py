import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import hashlib

from repository.exceptions import FileLimitExceedException, FileLimitExceedApiException


class FileManager(models.Manager):
    def create_and_check_for_duplicate(self, file, **kwargs):
        """
        Create new file instance or get existed if file already exists in system
        :return: (instance, is_duplicate) tuple 
        """
        hsh = hashlib.sha1(file.file.read()).hexdigest()
        existed_file = File.objects.filter(hash=hsh).first()
        if existed_file:
            return existed_file, True
        return super().create(file=file, hash=hsh, **kwargs), False


class UserFileManager(models.Manager):
    def create(self, *args, **kwargs):
        user = kwargs.get('user')
        if UserFile.objects.filter(user=user).count() >= settings.MAX_FILES_COUNT:
            raise FileLimitExceedApiException("File limit for user {} was exceed".format(user))

        return super(UserFileManager, self).create(*args, **kwargs)


class FileHashedUrl(models.Model):
    file = models.ForeignKey("File")
    hash = models.TextField("file name", editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.hash = uuid.uuid4().hex
        super().save(*args, **kwargs)


class File(models.Model):
    file = models.FileField("file instance", upload_to='repository')
    hash = models.TextField("file name", editable=False)

    objects = FileManager()


class UserFile(models.Model):
    original = models.BooleanField("Is file original", default=True)
    name = models.TextField("file name")
    user = models.ForeignKey(User)
    file = models.ForeignKey(File)

    objects = UserFileManager()
