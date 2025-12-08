from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import AppVersion

class AppVersionTests(TestCase):
    def setUp(self):
        self.apk_file = SimpleUploadedFile("app.apk", b"file_content", content_type="application/vnd.android.package-archive")
        self.version1 = AppVersion.objects.create(
            version_code=1,
            version_name="1.0.0",
            apk_file=self.apk_file,
            is_mandatory=False
        )
        self.version2 = AppVersion.objects.create(
            version_code=2,
            version_name="1.1.0",
            apk_file=self.apk_file,
            is_mandatory=True
        )

    def test_latest_version_api(self):
        url = reverse('latest-version')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['version_code'], 2)
        self.assertEqual(data['version_name'], "1.1.0")
        self.assertTrue(data['is_mandatory'])
        self.assertIn('download_url', data)

    def test_no_version_api(self):
        AppVersion.objects.all().delete()
        url = reverse('latest-version')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
