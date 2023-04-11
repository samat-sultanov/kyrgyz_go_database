from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from webapp.models import Club, City, Country, Region
from accounts.models import User


class ClubTestsForUnregisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_country = Country.objects.create(country_code='KG')
        test_region = Region.objects.create(name='Test region', country=test_country)
        test_city = City.objects.create(city='Test city', country=test_country, region=test_region)
        test_user = User.objects.create_user(username='test_user', password='test_password')
        image_file = SimpleUploadedFile('image.jpg', b'image_content', content_type='image/jpg')
        cls.test_club = Club.objects.create(
            logo=image_file,
            city=test_city
        )
        cls.test_club.coaches.set([test_user])

    def setUp(self) -> None:
        self.client = Client()

    def test_club_create(self):
        url = reverse('webapp:club_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Проверка на то, что нет доступа для анонимных пользователей
        data = {'logo': SimpleUploadedFile('image.jpg', b'image_content', content_type='image/jpg'),
                'name': 'Test_club_create',
                'coaches': 'admin'
                }
        response = self.client.post(url, data=data)  # Запрос на создание статьи
        self.assertEqual(response.status_code, 302)  # Все ещё нет доступа на страницу
        self.assertEqual(Club.objects.count(), 0)  # Проверка на то, что клуб не был создан
        redirect_url = reverse('accounts:login') + f'?next={url}'  # url для сравнения с response
        response = self.client.post(url, data=data, follow=True)  # Запрос на создание и redirect_url
        self.assertEqual(response.status_code, 200)  # Статус, что редирект произошел. 200 потому что передаем
        # follow=True в запросе
        self.assertRedirects(response, redirect_url)  # Проверка редиректа
