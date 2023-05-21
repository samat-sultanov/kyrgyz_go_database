from django.test import TestCase, Client
from django.urls import reverse

from webapp.models import Player, City, Country, Club


class PlayerTestsForSearch(TestCase):
    @classmethod
    def setUpTestData(cls):  # Создаём тестировочные данные
        country = Country.objects.create(country_code='kg')
        city_1 = City.objects.create(city='Bishkek', country=country)
        city_2 = City.objects.create(city='Karakol', country=country)
        club_1 = Club.objects.create(name='sengoku')
        club_2 = Club.objects.create(name='aden')
        cls.test_player_1 = Player.objects.create(
            first_name='Akram',
            last_name='Begmetov',
            country=country,
            city=city_1,
            birth_date='2023-03-03',
            current_rank='20k',
            current_rating='30')
        cls.test_player_1.clubs.set([club_1])
        cls.test_player_2 = Player.objects.create(
            first_name='Alex',
            last_name='Di',
            country=country,
            city=city_2,
            birth_date='2023-03-03',
            current_rank='20k',
            current_rating='30')
        cls.test_player_2.clubs.set([club_2])

    def setUp(self):
        self.client = Client()

    def test_search_by_last_name(self):
        url = reverse('webapp:player_search') + '?search_last_name=B'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertNotContains(response, self.test_player_2.last_name)

    def test_search_by_name(self):
        url = reverse('webapp:player_search') + '?search_first_name=Ak'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertNotContains(response, self.test_player_2.last_name)

    def test_search_by_clubs(self):
        url = reverse('webapp:player_search') + '?search_clubs=s'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertNotContains(response, self.test_player_2.last_name)

    def test_search_by_city(self):
        url = reverse('webapp:player_search') + '?search_city=B'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertNotContains(response, self.test_player_2.last_name)

    def test_search_all_fields(self):
        url = reverse('webapp:player_search') + \
              '?search_last_name=B&search_first_name=Ak&search_clubs=s&search_city=B'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertNotContains(response, self.test_player_2.last_name)

    def test_search_null_fields(self):
        url = reverse('webapp:player_search') + \
              '?search_last_name=&search_first_name=&search_clubs=&search_city='
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_player_1.last_name)
        self.assertContains(response, self.test_player_2.last_name)
