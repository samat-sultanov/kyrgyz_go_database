import datetime
from django.contrib.auth.models import Permission
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from webapp.models import Calendar, Country, City


class EventCreateTestByRegisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(username='admin', email='admin@admin.com', password='admin')
        test_user = User.objects.create_user(username='test_user', email='test@user.com', password='test_user')
        delete_event_permission = Permission.objects.get(codename='delete_calendar')
        test_user.user_permissions.add(delete_event_permission)
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
            'author': User.objects.first()
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

    def test_update_event(self):
        self.client.login(username='test_user', password='test_user')
        new_event = Calendar.objects.create(event_name='New event',
                                            text='New text',
                                            event_city=self.city_1,
                                            event_date=datetime.date(2030, 11, 11),
                                            deadline=datetime.date(2030, 11, 11),
                                            author=User.objects.first())
        url = reverse('webapp:event_update', args=[new_event.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'event_name': 'Updated event',
            'event_city': self.city_2,
            'event_date': datetime.date(2030, 12, 12),
            'text': 'Updated text',
            'deadline': datetime.date(2030, 12, 12),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('webapp:index')
        self.assertRedirects(response, redirect_url)
        updated_event = Calendar.objects.get(pk=new_event.pk)
        self.assertEqual(updated_event.event_name, 'Updated event')
        self.assertEqual(updated_event.event_date, datetime.date(2030, 12, 12))
        self.assertEqual(updated_event.deadline, datetime.date(2030, 12, 12))
        self.assertEqual(updated_event.text, 'Updated text')
        self.assertEqual(updated_event.event_city, self.city_2.city)

    def test_soft_delete_event(self):
        self.client.login(username='test_user', password='test_user')
        new_event = Calendar.objects.create(event_name='New event',
                                            text='New text',
                                            event_city=self.city_1,
                                            event_date=datetime.date(2030, 11, 11),
                                            deadline=datetime.date(2030, 11, 11),
                                            author=User.objects.first())
        url = reverse('webapp:index')
        response = self.client.get(url)
        self.assertContains(response, 'data-bs-target="#delete_event_Modal"')
        response = self.client.post(reverse('webapp:event_delete', args=[new_event.pk]))
        new_event.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Calendar.objects.filter(pk=new_event.pk).exists())
        self.assertEqual(new_event.is_deleted, True)
        self.assertEqual(Calendar.objects.count(), 1)
        self.assertEqual(new_event.event_name, "New event")

    def test_hard_delete_event(self):
        self.client.login(username='admin', password='admin')
        new_event = Calendar.objects.create(event_name='New event',
                                            text='New text',
                                            event_city=self.city_1,
                                            event_date=datetime.date(2030, 11, 11),
                                            deadline=datetime.date(2030, 11, 11),
                                            author=User.objects.first())
        new_event.is_deleted = True
        url = reverse('webapp:event_hard_delete_one', args=[new_event.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        redirect_url = reverse('webapp:deleted_calendar_list')
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Calendar.objects.count(), 0)

    def tearDown(self) -> None:
        self.client.logout()
