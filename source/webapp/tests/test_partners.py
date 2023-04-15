from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from webapp.models import Partner
from accounts.models import User
from io import BytesIO
from PIL import Image


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

    def test_partner_detail(self):
        url = reverse('webapp:partner_detail', args=[self.test_partner.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_partner_delete(self):
        url = reverse('webapp:partner_delete', args=[self.test_partner.pk])
        redirect_url = reverse('accounts:login') + f'?next={url}'
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirect_url)
        self.test_partner.refresh_from_db()
        self.assertEqual(Partner.objects.count(), 1)


class PartnerTestsForRegisteredUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        logo_file = BytesIO()
        logo_image = Image.new('RGB', (100, 100), 'red')
        logo_image.save(logo_file, 'jpeg')
        logo_file.name = 'test_logo.jpg'
        logo_file.seek(0)
        logo = SimpleUploadedFile(logo_file.name, logo_file.read(), content_type='image/jpeg')
        cls.test_partner = Partner.objects.create(
            name='Test name',
            logo=logo,
            web_link='https://test.com',
        )
        cls.test_user = User.objects.create_superuser(
            username='testuser',
            password='testpass'
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_partner_create(self):
        url = reverse('webapp:partner_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        logo_file = BytesIO()
        logo_image = Image.new('RGB', (100, 100), 'blue')
        logo_image.save(logo_file, 'jpeg')
        logo_file.name = 'new_logo.jpg'
        logo_file.seek(0)
        new_logo = SimpleUploadedFile(logo_file.name, logo_file.read(), content_type='image/jpeg')
        data = {
            'name': 'New name',
            'logo': new_logo,
            'web_link': 'https://example.com'
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Partner.objects.count(), 2)

        new_partner = Partner.objects.exclude(pk=self.test_partner.pk).get()
        self.assertEqual(new_partner.name, 'New name')
        self.assertEqual(new_partner.web_link, 'https://example.com')
        self.assertTrue(new_partner.logo)

        partner_detail_url = reverse('webapp:partner_detail', args=[new_partner.pk])
        self.assertRedirects(response, partner_detail_url)

    def test_partner_update(self):
        url = reverse('webapp:partner_update', args=[self.test_partner.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        logo_file = BytesIO()
        logo_image = Image.new('RGB', (100, 100), 'black')
        logo_image.save(logo_file, 'jpeg')
        logo_file.name = 'updated_logo.jpg'
        logo_file.seek(0)
        logo_update = SimpleUploadedFile(logo_file.name, logo_file.read(), content_type='image/jpeg')
        data = {
            'name': 'Updated name',
            'logo': logo_update,
            'web_link': 'https://example111.com'
        }

        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Partner.objects.count(), 1)

        self.test_partner.refresh_from_db()
        self.assertEqual(self.test_partner.name, 'Updated name')
        self.assertEqual(self.test_partner.web_link, 'https://example111.com')
        updated_partner = Partner.objects.get(pk=self.test_partner.pk)
        self.assertIn('updated_logo', updated_partner.logo.name)

        partner_detail_url = reverse('webapp:partner_detail', args=[updated_partner.pk])
        self.assertRedirects(response, partner_detail_url)

    def test_partner_detail(self):
        url = reverse('webapp:partner_detail', args=[self.test_partner.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_partner_delete(self):
        url = reverse('webapp:partner_delete', args=[self.test_partner.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Partner.objects.count(), 0)

        partner_list_url = reverse('webapp:partners_list')
        self.assertRedirects(response, partner_list_url)

