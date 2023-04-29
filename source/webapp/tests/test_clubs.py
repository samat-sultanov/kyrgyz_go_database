from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from webapp.models import Club, City, Country, Region
from accounts.models import User
from io import BytesIO
from PIL import Image


class ClubTestsForUnregisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создание страны, региона и города
        test_country = Country.objects.create(country_code='KG')
        test_region = Region.objects.create(name='Test region', country=test_country)
        cls.test_city = City.objects.create(city='Test city', country=test_country, region=test_region)
        cls.new_city = City.objects.create(city='New city', country=test_country, region=test_region)
        # Создание юзера
        test_user = User.objects.create_user(username='test_user', password='test_password')
        # Создание лого для теста
        logo_file = BytesIO()  # создание объекта BytesIO, который будет использоваться для хранения данных изображения
        logo_image = Image.new('RGB', (100, 100), 'red')  # создание изображения
        logo_image.save(logo_file, 'jpeg')  # сохранение
        logo_file.name = 'test_logo.jpg'  # имя создаваемой картинки
        logo_file.seek(0)  # устанавливаем указатель позиции картинки в буфере памяти
        logo = SimpleUploadedFile(logo_file.name, logo_file.read(), content_type='image/jpeg')  # создание
        # объекта SimpleUploadedFile)

        cls.test_club = Club.objects.create(
            name='Test name',
            logo=logo,
            city=cls.test_city
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
        response = self.client.post(url, data=data)  # Запрос на создание клуба
        self.assertEqual(response.status_code, 302)  # Все ещё нет доступа на страницу
        self.assertEqual(Club.objects.count(), 1)  # Проверка на то, что клуб не был создан
        redirect_url = reverse('accounts:login') + f'?next={url}'  # url для сравнения с response
        response = self.client.post(url, data=data, follow=True)  # Запрос на создание и redirect_url
        self.assertEqual(response.status_code, 200)  # Статус, что редирект произошел. 200 потому что передаем
        # follow=True в запросе
        self.assertRedirects(response, redirect_url)  # Проверка редиректа

    def test_club_update(self):
        url = reverse('webapp:club_update', args=[self.test_club.pk])
        redirect_url = reverse('accounts:login') + f'?next={url}'
        data = {
            'name': 'New name',
            'city': self.new_city.pk,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirect_url)
        self.test_club.refresh_from_db()  # Обновление/актуализация бд
        self.assertEqual(self.test_club.name, 'Test name')  # Проверка, что название клуба не поменялось
        self.assertEqual(self.test_club.city, self.test_city)  # Проверка, что город не поменялся


class ClubTestsForRegisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_country = Country.objects.create(country_code='KG')
        test_region = Region.objects.create(name='Test region', country=test_country)
        cls.test_city = City.objects.create(city='Test city', country=test_country, region=test_region)
        cls.new_city = City.objects.create(city='New city', country=test_country, region=test_region)
        cls.test_user = User.objects.create_user(
            username='test_user',
            password='test_password'
        )
        cls.new_user = User.objects.create_user(
            username='new_user',
            email='new_user@example.com',
            password='test_password'
        )

        cls.test_club = Club.objects.create(
            name='Test name',
            city=cls.test_city
        )
        cls.test_club.coaches.set([cls.test_user])

    def setUp(self) -> None:
        self.client = Client()
        self.client.login(username='new_user', password='test_password')

    def test_club_create(self):
        url = reverse('webapp:club_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {'name': 'Test_club_create',
                'city': self.new_city.pk,
                'coaches': [self.new_user.pk]
                }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Club.objects.count(), 2)
        new_club = Club.objects.get(name='Test_club_create')
        self.assertEqual(new_club.name, 'Test_club_create')
        self.assertEqual(new_club.city, self.new_city)
        self.assertEqual(new_club.coaches.first(), self.new_user)
