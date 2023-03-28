from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from webapp.models import News


class NewsAddTest(TestCase):
    def setUp(self):
        self.client = Client()  # Анонимный пользователь пытается создать статью

    def test_add_news(self):
        url = reverse('webapp:news_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Проверка на то, что нет доступа для анонимных пользователей
        image_file = SimpleUploadedFile('image.jpg', b'image_content', content_type='image/jpg')
        # Создаю файл типа картинки (замена реальной картинки)
        data = {'title': 'Some text',
                'text': 'This is a long interesting text with at least 3 sentences.',
                'news_image': image_file}
        response = self.client.post(url, data)  # Отправляю запрос на создание статьи
        self.assertEqual(response.status_code, 302)  # Все ещё нет доступа на страницу
        self.assertEqual(News.objects.count(), 0)  # Проверяю, что статья не была создана
