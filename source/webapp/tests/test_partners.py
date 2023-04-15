from django.test import TestCase, Client
from django.urls import reverse
from webapp.models import Partner
from accounts.models import User


class PartnerTestsForUnregisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_partner = Partner.objects.create(
            name='Test name',
            web_link='https://test.com',
        )

    def setUp(self):
        self.client = Client()

    def test_partner_create(self):
        url = reverse('webapp:partner_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        data = {
            'name': 'New name',
            'web_link': 'https://example.com'
                }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Partner.objects.count(), 1)
        redirect_url = reverse('accounts:login') + f'?next={url}'
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirect_url)

    def test_partner_update(self):
        url = reverse('webapp:partner_update', args=[self.test_partner.pk])
        redirect_url = reverse('accounts:login') + f'?next={url}'
        data = {
            'name': 'New name',
            'web_link': 'https://example.com'
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirect_url)
        self.test_partner.refresh_from_db()
        self.assertEqual(self.test_partner.name, 'Test name')
        self.assertEqual(self.test_partner.web_link, 'https://test.com')

    def test_partner_delete(self):
        url = reverse('webapp:partner_delete', args=[self.test_partner.pk])
        redirect_url = reverse('accounts:login') + f'?next={url}'
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirect_url)


