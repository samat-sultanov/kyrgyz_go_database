from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from webapp.models import Club


class TestClubCreate(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def setUpTestData(cls):
        pass

    def test_club_create(self):
        data = {'logo': SimpleUploadedFile('image.jpg', b'image_content', content_type='image/jpg'),
                'name': 'Test_club_create',
                'coaches': 'admin'
                }
        response = self.client.post(reverse('webapp:club_create'), data=data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)