from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Player, Country, City, Club


class PlayerTestsSearchCompetitors(TestCase):  # Для анонимных пользователей
    @classmethod
    def setUpTestData(cls):  # Создаём тестировочные данные
        country_1 = Country.objects.create(country_code='kg')
        country_2 = Country.objects.create(country_code='ru')
        city_1 = City.objects.create(city="Bishkek", country=country_1)
        city_2 = City.objects.create(city="Moskow", country=country_2)
        club_1 = Club.objects.create(name="Sengoku")
        club_2 = Club.objects.create(name='Spartak')
        cls.player_1 = Player.objects.create(
            first_name='Bob',
            last_name='Marley',
            current_rank='20k',
            current_rating=100,
            country=country_1,
            city=city_1,
            )
        cls.player_2 = Player.objects.create(
            first_name='Tim',
            last_name='Dim',
            current_rank='22k',
            current_rating=-100,
            country=country_1,
            city=city_1
        )
        cls.player_3 = Player.objects.create(
            first_name='Anna',
            last_name='Who',
            current_rank='2k',
            current_rating=1900,
            country=country_2,
            city=city_2
        )
        cls.player_1.clubs.add(club_1)
        cls.player_2.clubs.add(club_1)
        cls.player_3.clubs.add(club_2)

    def setUp(self):
        self.client = Client()

    def test_search_by_rank(self):
        url = reverse('webapp:competitor_search') + '?search_rank=20k'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player_1.last_name)
        self.assertContains(response, self.player_2.last_name)
        self.assertNotContains(response, self.player_3.last_name)
