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
        self.admin = User.objects.create()  # без этой строки терминал ругается, что во временной базе нет пользователей

    def create_event(self):
        event_name = 'Event #1'
        event_city = 'Kara-Kol'
        event_date = '2024-10-10'
        text = 'Test text ofr event #1'
        deadline = timezone.now()
        author = 1
        return Calendar.objects.create(event_name=event_name, event_city=event_city, event_date=event_date, text=text,
                                       deadline=deadline, author_id=author)

    def test_view_create_event(self):
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

    def test_model_event_create_success(self):
        event = self.create_event()
        self.assertTrue(isinstance(event, Calendar))


class EventDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create()
        event_name = 'Event #1'
        event_city = 'Kara-Kol'
        event_date = '2024-10-10'
        text = 'Test text ofr event #1'
        deadline = timezone.now()
        author = 1
        self.event_to_delete = Calendar.objects.create(event_name=event_name, event_city=event_city,
                                                       event_date=event_date, text=text, deadline=deadline,
                                                       author_id=author)

    def test_view_event_soft_delete(self):
        url = reverse('webapp:event_delete', kwargs={'pk': self.event_to_delete.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
