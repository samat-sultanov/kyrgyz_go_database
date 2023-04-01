from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Player, Country


class PlayerTestsSearchCompetitors(TestCase):  # Для анонимных пользователей
    @classmethod
    def setUpTestData(cls):  # Создаём тестировочные данные
        country = Country.objects.create(country_code='kg')
        cls.player_1 = Player.objects.create(
            first_name='Bob',
            last_name='Marley',
            current_rank='20k',
            country=country
            )
        cls.player_2 = Player.objects.create(
            first_name='Tim',
            last_name='Dim',
            current_rank='22k',
            country=country
        )
        cls.player_3 = Player.objects.create(
            first_name='Anna',
            last_name='Who',
            current_rank='2k',
            country=country
        )

    def setUp(self):
        self.client = Client()

    def test_search_by_rank(self):
        url = reverse('webapp:competitor_search') + '?search_rank=20k'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player_1.id)
        self.assertContains(response, self.player_2.id)
        self.assertNotContains(response, self.player_3.id)
