from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from accounts.models import User
from webapp.models import News


class NewsAddTest(TestCase):
    def setUp(self):
        self.client.login(username='admin', password='admin')

    def test_add_news(self):
        url = reverse('webapp:news_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        image_file = '/Users/nomad/Documents/3.jpeg'
        data = {'title': 'Some text', 'text': 'Some text', 'news_image': image_file}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(News.objects.count(), 0)


