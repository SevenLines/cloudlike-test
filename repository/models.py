import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import hashlib

from repository.exceptions import FileLimitExceedApiException


class FileManager(models.Manager):
    def create_and_check_for_duplicate(self, file, **kwargs):
        """
        Create new file instance or get existed instance if file with hash already exists
        :return: (instance, is_duplicate) tuple 
        """
        hsh = hashlib.sha1(file.file.read()).hexdigest()
        existed_file = File.objects.filter(hash=hsh).first()
        if existed_file:
            return existed_file, True
        return super().create(file=file, hash=hsh, **kwargs), False


class FileHashedUrl(models.Model):
    file = models.ForeignKey("File")
    hash = models.TextField("file name", editable=False)

    def save(self, *args, **kwargs):
        # generate hash
        if not self.pk:
            self.hash = uuid.uuid4().hex
        super().save(*args, **kwargs)


class File(models.Model):
    file = models.FileField("file instance", upload_to='repository')
    hash = models.TextField("file name", editable=False)

    objects = FileManager()


class UserFile(models.Model):
    original = models.BooleanField("is file original", default=True)
    name = models.TextField("file name")
    user = models.ForeignKey(User)
    file = models.ForeignKey(File)
