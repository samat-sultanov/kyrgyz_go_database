from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Tournament, City


class TournamentTestsForUnregisterUser(TestCase):  # Для анонимных пользователей
    @classmethod
    def setUpTestData(cls):  # Создаём тестировочные данные
        test_user = User.objects.create_user(username='test_user', password='test_password')
        city_1 = City.objects.create(city='Bishkek')
        city_2 = City.objects.create(city='Karakol')
        cls.test_tournament = Tournament.objects.create(
            uploaded_by=test_user,
            name='Some name',
            city=city_1,
            tournament_class='A')
        cls.test_tournament = Tournament.objects.create(
            uploaded_by=test_user,
            name='Tournament',
            city=city_2,
            tournament_class='B')

    def setUp(self):
        self.client = Client()

    def test_add_news(self):
        url = reverse('webapp:news_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

