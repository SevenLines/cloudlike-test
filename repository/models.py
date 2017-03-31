import uuid

from django.contrib.auth.models import User
from django.db import models
import hashlib


class FileManager(models.Manager):
    def create(self, file, **kwargs):
        hsh = hashlib.sha1(file.file.read()).hexdigest()
        existed_file = File.objects.filter(hash=hsh).first()
        if existed_file:
            return existed_file
        return super().create(file=file, hash=hsh, **kwargs)


class FileHashedUrl(models.Model):
    file = models.ForeignKey("File")
    hash = models.TextField("file name", editable=False)

    def save(self, *args, **kwargs):
        self.hash = uuid.uuid4().hex
        super().save(*args, **kwargs)


class File(models.Model):
    file = models.FileField("file instance", upload_to='repository')
    hash = models.TextField("file name", editable=False)

    objects = FileManager()


class UserFile(models.Model):
    name = models.TextField("file name")
    user = models.ForeignKey(User)
    file = models.ForeignKey(File)
