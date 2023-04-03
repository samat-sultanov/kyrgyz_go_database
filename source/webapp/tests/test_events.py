import datetime

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Calendar, Country, City


class EventCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_admin = User.objects.create_superuser(username='admin', email='admin@admin.com', password='admin')
        cls.test_user = User.objects.create_user(username='test_user', email='test@user.com', password='test_user')
        country = Country.objects.create(country_code='kg')
        cls.city_1 = City.objects.create(city='Bishkek', country=country)
        cls.city_2 = City.objects.create(city='Talas', country=country)

    def setUp(self):
        self.client = Client()

    def test_view_create_event(self):
        self.client.login(username='test_user', password='test_user')
        url = reverse('webapp:event_create')
        data = {
            'event_name': 'test_event_name',
            'event_city': self.city_1,
            'event_date': datetime.date(2024, 10, 10),
            'text': 'Test text for event create test',
            'deadline': datetime.date(2024, 10, 10),
        }
        self.client.get(url)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('webapp:index')
        self.assertRedirects(response, redirect_url)
        event = Calendar.objects.get(event_name='test_event_name')
        self.assertEqual(event.event_name, 'test_event_name')
        self.assertEqual(event.event_city, self.city_1.city)
        self.assertEqual(event.event_date, datetime.date(2024, 10, 10))
        self.assertEqual(event.text, 'Test text for event create test')
        self.assertEqual(event.deadline, datetime.date(2024, 10, 10))


#
# class EventDeleteTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#
#     def create_event(self, adm):
#         event_name = 'Event #1'
#         event_city = 'Kara-Kol'
#         event_date = '2024-10-10'
#         text = 'Test text ofr event #1'
#         deadline = timezone.now()
#         author = adm.pk
#         return Calendar.objects.create(event_name=event_name, event_city=event_city, event_date=event_date, text=text,
#                                        deadline=deadline, author_id=author)
#
#     def tearDown(self):
#         Calendar.objects.all().delete()
#
#     def test_view_event_soft_delete(self):
#         adm = User.objects.create()
#         event_to_delete = self.create_event(adm)
#         url = reverse('webapp:event_delete', kwargs={'pk': event_to_delete.pk})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 302)
#
#     def test_model_hard_delete(self):
#         adm = User.objects.create()
#         event_to_delete = self.create_event(adm)
#         self.assertIn(event_to_delete, Calendar.objects.all())
#         event_to_delete.delete()
#         self.assertNotIn(event_to_delete, Calendar.objects.all())
#
#     def test_view_hard_delete(self):
#         adm = User.objects.create()
#         adm.is_superuser = True
#         event_to_delete = self.create_event(adm)
#         self.assertIn(event_to_delete, Calendar.objects.all())
#         event_to_delete.is_deleted = True
#         self.assertTrue(event_to_delete.is_deleted)
#         url = reverse('webapp:event_hard_delete_one', kwargs={'pk': event_to_delete.pk})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 302)
