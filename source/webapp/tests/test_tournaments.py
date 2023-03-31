from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Tournament, City, Country


class TournamentTestsForUnregisterUser(TestCase):  # Для анонимных пользователей
    @classmethod
    def setUpTestData(cls):  # Создаём тестировочные данные
        test_user = User.objects.create_user(username='test_user', password='test_password')
        country = Country.objects.create(country_code='kg')
        city_1 = City.objects.create(city='Bishkek', country=country)
        city_2 = City.objects.create(city='Karakol', country=country)
        cls.test_tournament_1 = Tournament.objects.create(
            uploaded_by=test_user,
            name='Some name',
            city=city_1,
            tournament_class='A',
            date='2023-03-03',
            rounds=7)
        cls.test_tournament_2 = Tournament.objects.create(
            uploaded_by=test_user,
            name='Tournament',
            city=city_2,
            tournament_class='B',
            date='2022-01-20',
            rounds=9)

    def setUp(self):
        self.client = Client()

    def test_search_by_name(self):
        url = reverse('webapp:tournament_search') + '?search_name=S'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_by_class(self):
        url = reverse('webapp:tournament_search') + '?search_tournament_class=A'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_by_city(self):
        url = reverse('webapp:tournament_search') + '?search_city=B'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_by_date(self):
        url = reverse('webapp:tournament_search') + '?search_date=2023-03-03'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_all_fields(self):
        url = reverse('webapp:tournament_search') + \
              '?search_name=S&search_city=B&search_date=2023-03-03&search_tournament_class=A'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_null_fields(self):
        url = reverse('webapp:tournament_search') + \
              '?search_name=&search_city=&search_date=&search_tournament_class='
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_tournament_1.name)
        self.assertContains(response, self.test_tournament_2.name)

    def test_search_wrong_data_name(self):
        url = reverse('webapp:tournament_search') + '?search_name=3'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_wrong_data_city(self):
        url = reverse('webapp:tournament_search') + '?search_city=5'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    def test_search_wrong_data_class(self):
        url = reverse('webapp:tournament_search') + '?search_tournament_class=T'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.test_tournament_1.name)
        self.assertNotContains(response, self.test_tournament_2.name)

    # def test_search_wrong_data_date(self):
    #     url = reverse('webapp:tournament_search') + '?search_date=h'
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotContains(response, self.test_tournament_1.name)
    #     self.assertNotContains(response, self.test_tournament_2.name)
