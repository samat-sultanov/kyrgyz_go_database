from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from accounts.models import User
from webapp.models import Calendar


class EventCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        #self.admin = User.objects.create()  #без этой строки терминал ругается, что во временной базе нет пользователей

    def test_links_create_event_success(self):
        url = reverse('webapp:event_create')
        data = {
            'event_name': 'test_event_name',
            'event_city': 'Tals',
            'event_date': '10/10/2024',
            'text': 'Test text for event create test',
            'deadline': '10/10/2024, 10:10 10',
        }
        self.client.get(url)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

