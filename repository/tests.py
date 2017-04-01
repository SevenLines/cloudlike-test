from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.urls import reverse

from main.tests import BaseTestCase
from repository.models import UserFile, File


class TestFileViewSet(BaseTestCase):
    def test_list_files_for_each_user(self):
        with open("manage.py", 'rb') as f:
            file = File.objects.create(file=SimpleUploadedFile('filename', f.read()))
        user1_file1 = UserFile.objects.create(user=self.user1, name='user1-file1', file=file)
        user1_file2 = UserFile.objects.create(user=self.user1, name='user1-file2', file=file)
        user2_file1 = UserFile.objects.create(user=self.user2, name='user2-file1', file=file)

        with self.login('user1'):
            r = self.client.get(reverse("repository:files-list"))
            self.assertIn(user1_file1.pk, [i['id'] for i in r.data])
            self.assertIn(user1_file2.pk, [i['id'] for i in r.data])
            self.assertNotIn(user2_file1.pk, [i['id'] for i in r.data])

        with self.login('user2'):
            r = self.client.get(reverse("repository:files-list"))
            self.assertNotIn(user1_file1.pk, [i['id'] for i in r.data])
            self.assertNotIn(user1_file2.pk, [i['id'] for i in r.data])
            self.assertIn(user2_file1.pk, [i['id'] for i in r.data])

    def test_upload_file(self):
        with self.login('user1'):
            with open("manage.py", 'rb') as f:
                r = self.client.post(reverse("repository:files-list"), {
                    'name': 'name1',
                    'file': f
                })
                id1 = r.data['id']

            with open("manage.py", 'rb') as f:
                r = self.client.post(reverse("repository:files-list"), {
                    'file': f
                })
                id2 = r.data['id']

            self.assertEqual(UserFile.objects.get(id=id1).file, UserFile.objects.get(id=id2).file)
            self.assertEqual('name1.py', UserFile.objects.get(id=id1).name)
            self.assertEqual('manage.py', UserFile.objects.get(id=id2).name)
            self.assertEqual(1, File.objects.count())
            self.assertEqual(2, UserFile.objects.count())

    def test_remove_file(self):
        with open("manage.py", 'rb') as f:
            file = File.objects.create(file=SimpleUploadedFile('filename', f.read()))
            user_file1 = UserFile.objects.create(file=file, user=self.user1, name="name")
            user_file2 = UserFile.objects.create(file=file, user=self.user2, name="name")

        self.assertEqual(2, UserFile.objects.count())
        self.assertEqual(1, File.objects.count())

        with self.login('user1'):
            self.client.delete(reverse("repository:files-detail", args=[user_file1.pk]))
            self.client.delete(reverse("repository:files-detail", args=[user_file2.pk]))
            self.assertFalse(UserFile.objects.filter(pk=user_file1.pk).exists())
            self.assertTrue(UserFile.objects.filter(pk=user_file2.pk).exists())
        self.assertEqual(1, File.objects.count())

        with self.login('user2'):
            self.client.delete(reverse("repository:files-detail", args=[user_file2.pk]))
            self.assertFalse(UserFile.objects.filter(pk=user_file2.pk).exists())
        self.assertEqual(0, UserFile.objects.count())
        self.assertEqual(1, File.objects.count())

    def test_url_generating(self):
        with self.login('user1'):
            with open("manage.py", 'rb') as f:
                file = File.objects.create(file=SimpleUploadedFile('filename', f.read()))
                user_file = UserFile.objects.create(file=file, user=self.user1, name="name")

            r = self.client.get(reverse('repository:files-detail', args=[user_file.pk]))
            r = self.client.get(r.url)
            self.assertIsNotNone(r.content)

    @override_settings(MAX_FILES_COUNT=1)
    def test_file_limit(self):
        with self.login('user1'):
            with open("manage.py", 'rb') as f:
                r = self.client.post(reverse("repository:files-list"), {
                    'name': 'name1',
                    'file': f
                })

            with open("manage.py", 'rb') as f:
                r = self.client.post(reverse("repository:files-list"), {
                    'name': 'name1',
                    'file': f
                })
                self.assertEqual(500, r.status_code)

            self.assertEqual(1, UserFile.objects.count())