import os
import shutil
import datetime

from django.db.models import PositiveIntegerField
from django.test import TestCase
import accounts.models
from django.core.exceptions import ValidationError
from accounts.models import User
from webapp.models import Recommendation, Player, Country, Region, News, Tournament, City, CLASS_CHOICES


class RecommendationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.player = Player.objects.create(first_name='Test player', country=Country.objects.create(country_code='kg'))
        cls.recommendation = Recommendation.objects.create(text='Test recommendation', author=cls.user,
                                                           player=cls.player)

    def test_str_method(self):
        expected_method = f'{self.recommendation.pk}. Test recommendation'
        self.assertEqual(str(self.recommendation), expected_method)

    def test_text_max_length(self):
        max_length = Recommendation._meta.get_field('text').max_length
        self.assertEqual(max_length, 400)

    def test_author_foreign_key(self):
        author_field = Recommendation._meta.get_field('author')
        self.assertEqual(author_field.related_model, accounts.models.User)

    def test_player_foreign_key(self):
        player_field = Recommendation._meta.get_field('player')
        self.assertEqual(player_field.related_model, Player)

    def test_created_at_auto_now_add(self):
        created_at_field = Recommendation._meta.get_field('created_at')
        self.assertTrue(created_at_field.auto_now_add)

    def test_updated_at_auto_now(self):
        updated_at_field = Recommendation._meta.get_field('updated_at')
        self.assertTrue(updated_at_field.auto_now)

    def test_object_creation(self):
        self.assertEqual(self.recommendation.text, 'Test recommendation')
        self.assertEqual(self.recommendation.author, self.user)
        self.assertEqual(self.recommendation.player, self.player)
        self.assertIsNotNone(self.recommendation.created_at)
        self.assertIsNotNone(self.recommendation.updated_at)

    def test_object_update(self):
        self.recommendation.text = 'Updated recommendation'
        self.recommendation.save()
        updated_recommendation = Recommendation.objects.get(pk=self.recommendation.pk)
        self.assertEqual(updated_recommendation.text, 'Updated recommendation')
        self.assertGreater(updated_recommendation.updated_at, self.recommendation.created_at)

    def test_player_deletion(self):
        self.player.delete()
        self.assertFalse(Recommendation.objects.filter(pk=self.recommendation.pk).exists())

    def test_author_default_value(self):
        recommendation = Recommendation.objects.create(
            text='Test recommendation',
            player=self.player
        )
        self.assertEqual(recommendation.author_id, 1)

    def test_related_name_parameter(self):
        self.assertIn(self.recommendation, self.user.author.all())
        self.assertIn(self.recommendation, self.player.player.all())


class CountryModelTest(TestCase):
    def test_create_country_with_right_country_code(self):
        country = Country.objects.create(country_code='kg')
        self.assertIsInstance(country, Country)
        self.assertEqual(len(Country.objects.all()), 1)
        self.assertEqual(str(country), 'kg')

    def test_create_country_with_wrong_parameters(self):
        with self.assertRaises(Exception):
            Country.objects.create(country_code='kgz')

    def test_update_country(self):
        country = Country.objects.create(country_code='us')
        self.assertEqual(len(Country.objects.all()), 1)
        country.country_code = 'ca'
        country.save()
        updated_country = Country.objects.get(pk=country.pk)
        self.assertEqual(updated_country.country_code, 'ca')

    def test_delete_country(self):
        country = Country.objects.create(country_code='kg')
        self.assertEqual(len(Country.objects.all()), 1)
        country.delete()
        self.assertEqual(len(Country.objects.all()), 0)


class RegionModelTest(TestCase):
    def test_create_region_with_correct_parameters(self):
        country = Country.objects.create(country_code='kg')
        Region.objects.create(name='Chuy', country=country)
        self.assertEqual(len(Region.objects.all()), 1)
        created_region = Region.objects.filter(name='Chuy').first()
        self.assertEqual(created_region.name, 'Chuy')
        self.assertEqual(created_region.country, country)

    def test_create_region_with_wrong_parameters(self):
        country = Country.objects.create(country_code='US')
        region = Region(country=country, name='')
        with self.assertRaises(ValidationError):
            region.full_clean()
            region.save()
        self.assertEqual(len(Region.objects.all()), 0)

    def test_update_region(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        region.name = 'Naryn'
        region.save()
        updated_region = Region.objects.first()
        self.assertEqual(updated_region.name, 'Naryn')

    def test_delete_region(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        self.assertEqual(len(Region.objects.all()), 1)
        region.delete()
        self.assertEqual(len(Region.objects.all()), 0)


class NewsModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.news = News.objects.create(title="Test news title", text="Test news text", author=cls.user)
        cls.news_with_image = News.objects.create(title="Test news image",
                                                  text="Image taken from static. 'sengoku_logo.png'", author=cls.user,
                                                  news_image='news_images/sengoku_logo.png')
        cls.news_with_video = News.objects.create(title="Test news video", text="Rick Astley - Never gonna give you up",
                                                  author=cls.user,
                                                  video_link='https://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_str_method(self):
        expected_str = f"Test news title - {self.news.created_at.strftime('%d-%m-%Y %H:%M:%S')}"
        self.assertEqual(str(self.news), expected_str)

    def test_author_foreign_key(self):
        author_field = News._meta.get_field('author')
        self.assertEqual(author_field.related_model, accounts.models.User)

    def test_created_at_auto_now_add(self):
        created_at_field = News._meta.get_field('created_at')
        self.assertTrue(created_at_field.auto_now_add)

    def test_updated_at_auto_now(self):
        updated_at_field = News._meta.get_field('updated_at')
        self.assertTrue(updated_at_field.auto_now)

    def test_object_creation_no_video_no_image(self):
        self.assertEqual(self.news.title, 'Test news title')
        self.assertEqual(self.news.text, 'Test news text')
        self.assertEqual(self.news.author, self.user)
        self.assertIsNotNone(self.news.created_at)
        self.assertIsNotNone(self.news.updated_at)

    def test_object_creation_video_no_image(self):
        self.assertEqual(self.news_with_video.title, 'Test news video')
        self.assertEqual(self.news_with_video.text, 'Rick Astley - Never gonna give you up')
        self.assertEqual(self.news_with_video.video_link, 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        self.assertEqual(self.news_with_video.author, self.user)
        self.assertEqual(self.news_with_video.news_image, None)
        self.assertIsNotNone(self.news_with_video.created_at)
        self.assertIsNotNone(self.news_with_video.updated_at)

    def test_object_creation_image_no_video(self):
        self.assertEqual(self.news_with_image.title, 'Test news image')
        self.assertEqual(self.news_with_image.text, "Image taken from static. 'sengoku_logo.png'")
        self.assertEqual(self.news_with_image.news_image, 'news_images/sengoku_logo.png')
        self.assertEqual(self.news_with_image.author, self.user)
        self.assertEqual(self.news_with_image.video_link, None)
        self.assertIsNotNone(self.news_with_image.created_at)
        self.assertIsNotNone(self.news_with_image.updated_at)

    def test_update_title(self):
        self.news.title = 'Updated title of news'
        self.news.save()
        news_with_updated_title = News.objects.get(pk=self.news.pk)
        self.assertEqual(news_with_updated_title.title, 'Updated title of news')
        self.assertGreater(news_with_updated_title.updated_at, self.news.created_at)

    def test_update_text(self):
        self.news.text = 'Updated text of news'
        self.news.save()
        news_with_updated_text = News.objects.get(pk=self.news.pk)
        self.assertEqual(news_with_updated_text.text, 'Updated text of news')
        self.assertGreater(news_with_updated_text.updated_at, self.news.created_at)

    def test_update_image(self):
        self.news_with_image.news_image = 'news_images/11316.jpg'
        self.news_with_image.save()
        news_with_updated_image = News.objects.get(pk=self.news_with_image.pk)
        self.assertEqual(news_with_updated_image.news_image, 'news_images/11316.jpg')
        self.assertGreater(news_with_updated_image.updated_at, self.news_with_image.created_at)
        src = os.getcwd() + '/source/webapp/static/images/sengoku_logo.png'
        dst = os.getcwd() + '/source/uploads/news_images/'
        shutil.copy2(src, dst)

    def test_update_video(self):
        self.news_with_video.video_link = 'https://www.youtube.com/embed/Zi_XLOBDo_Y'
        self.news_with_video.save()
        news_with_updated_video = News.objects.get(pk=self.news_with_video.pk)
        self.assertEqual(news_with_updated_video.video_link, 'https://www.youtube.com/embed/Zi_XLOBDo_Y')
        self.assertGreater(news_with_updated_video.updated_at, self.news_with_video.created_at)

    def test_delete(self):
        news_to_delete = News.objects.create(title="Test_delete", text="test_delete_text")
        self.assertTrue(News.objects.filter(pk=news_to_delete.pk).exists())
        news_to_delete.delete()
        self.assertFalse(News.objects.filter(pk=news_to_delete.pk).exists())

    def test_author_default_value(self):
        news = News.objects.create(title='Test title', text='Test text')
        self.assertEqual(news.author_id, 1)


class TournamentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.country = Country.objects.create(country_code='kg')
        cls.city = City.objects.create(city='Test City', country=cls.country)
        cls.region = Region.objects.create(name='Test Region', country=cls.country)
        cls.tournament = Tournament.objects.create(name='Test Tournament', city=cls.city, region=cls.region,
                                                   location='Test Location', board_size=19, rounds=5,
                                                   date=datetime.date.today(), tournament_class='Test Class',
                                                   regulations='Test Regulations', uploaded_by=cls.user)

    def test_str_method(self):
        expected_method = f'{self.tournament.id}. Test Tournament - 19'
        self.assertEqual(str(self.tournament), expected_method)

    def test_name_max_length(self):
        max_length = Tournament._meta.get_field('name').max_length
        self.assertEqual(max_length, 50)

    def test_board_size_default(self):
        default_size = Tournament._meta.get_field('board_size').default
        self.assertEqual(default_size, 19)

    def test_board_size_positive_integer(self):
        board_size_field = Tournament._meta.get_field('board_size')
        self.assertIsInstance(board_size_field, PositiveIntegerField)

    def test_rounds_positive_integer(self):
        rounds_field = Tournament._meta.get_field('rounds')
        self.assertIsInstance(rounds_field, PositiveIntegerField)

    def test_tournament_class_choices(self):
        choices_field = Tournament._meta.get_field('tournament_class')
        self.assertEqual(choices_field.choices, CLASS_CHOICES)

    def test_uploaded_by_foreign_key(self):
        uploaded_by_field = Tournament._meta.get_field('uploaded_by')
        self.assertEqual(uploaded_by_field.related_model, accounts.models.User)

    def test_object_creation(self):
        self.assertEqual(self.tournament.name, 'Test Tournament')
        self.assertEqual(self.tournament.city, self.city)
        self.assertEqual(self.tournament.region, self.region)
        self.assertEqual(self.tournament.location, 'Test Location')
        self.assertEqual(self.tournament.board_size, 19)
        self.assertEqual(self.tournament.rounds, 5)
        self.assertEqual(self.tournament.date, datetime.date.today())
        self.assertEqual(self.tournament.tournament_class, 'Test Class')
        self.assertEqual(self.tournament.regulations, 'Test Regulations')
        self.assertEqual(self.tournament.uploaded_by, self.user)

    def test_object_update(self):
        self.tournament.name = 'Updated Tournament'
        self.tournament.save()
        updated_tournament = Tournament.objects.get(pk=self.tournament.pk)
        self.assertEqual(updated_tournament.name, 'Updated Tournament')

    def test_city_deletion(self):
        self.city.delete()
        self.assertFalse(Tournament.objects.filter(pk=self.tournament.pk).exists())
