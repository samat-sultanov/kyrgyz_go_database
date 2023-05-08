import os
import shutil
import datetime
from phonenumbers import parse, PhoneNumberFormat

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import PositiveIntegerField, FloatField, DateTimeField, ProtectedError
from django.test import TestCase
import accounts.models
from accounts.models import User
from webapp.models import Recommendation, Player, Country, Region, News, Tournament, City, CLASS_CHOICES, Game, \
    Calendar, get_author, Partner, Club, DayOfWeek


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


class CityModelTest(TestCase):
    def test_create_city_with_correct_parameters(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        city = City.objects.create(city='Bishkek', country=country, region=region)
        self.assertIsInstance(city, City)
        self.assertEqual(len(City.objects.all()), 1)
        self.assertEqual(str(city), 'Bishkek')
        self.assertLessEqual(len(city.city), 50)

    def test_create_city_with_incorrect_parameters(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        city = City(city='', country=country, region=region)
        with self.assertRaises(ValidationError):
            city.full_clean()
            city.save()
        city = City(city='a' * 51, country=country, region=region)
        with self.assertRaises(ValidationError):
            city.full_clean()
            city.save()
        self.assertEqual(len(City.objects.all()), 0)

    def test_update_city(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        city = City.objects.create(city='Bishkek', country=country, region=region)
        city.city = 'Osh'
        city.save()
        updated_city = City.objects.get(id=city.id)
        self.assertEqual(updated_city.city, 'Osh')

    def test_delete_city(self):
        country = Country.objects.create(country_code='kg')
        region = Region.objects.create(name='Chuy', country=country)
        city = City.objects.create(city='Bishkek', country=country, region=region)
        self.assertEqual(len(City.objects.all()), 1)
        city.delete()
        self.assertEqual(len(City.objects.all()), 0)


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
        src = os.getcwd() + '/source/webapp/static/images'
        dst = os.getcwd() + '/source/uploads/news_images/'
        shutil.copy2(src + '/sengoku_logo.png', dst + 'sengoku_logo_for_test.png')
        shutil.copy2(src + '/11316.jpg', dst + '11316_for_test.jpg')
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.news = News.objects.create(title="Test news title", text="Test news text", author=cls.user)
        cls.news_with_image = News.objects.create(title="Test news image",
                                                  text="Image taken from static. 'sengoku_logo_for_test.png'",
                                                  author=cls.user,
                                                  news_image='news_images/sengoku_logo_for_test.png')
        cls.news_with_video = News.objects.create(title="Test news video", text="Rick Astley - Never gonna give you up",
                                                  author=cls.user,
                                                  video_link='https://www.youtube.com/embed/dQw4w9WgXcQ')

    @classmethod
    def tearDownClass(cls):
        sengoku_logo = os.getcwd() + '/source/uploads/news_images/sengoku_logo_for_test.png'
        dummy = os.getcwd() + '/source/uploads/news_images/11316_for_test.jpg'
        if os.path.isfile(sengoku_logo) or os.path.isfile(dummy):
            os.remove(sengoku_logo)
            os.remove(dummy)

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
        self.assertEqual(self.news_with_image.text, "Image taken from static. 'sengoku_logo_for_test.png'")
        self.assertEqual(self.news_with_image.news_image, 'news_images/sengoku_logo_for_test.png')
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
        self.news_with_image.news_image = 'news_images/11316_for_test.jpg'
        self.news_with_image.save()
        news_with_updated_image = News.objects.get(pk=self.news_with_image.pk)
        self.assertEqual(news_with_updated_image.news_image, 'news_images/11316_for_test.jpg')
        self.assertGreater(news_with_updated_image.updated_at, self.news_with_image.created_at)

    def test_update_video(self):
        self.news_with_video.video_link = 'https://www.youtube.com/embed/Zi_XLOBDo_Y'
        self.news_with_video.save()
        news_with_updated_video = News.objects.get(pk=self.news_with_video.pk)
        self.assertEqual(news_with_updated_video.video_link, 'https://www.youtube.com/embed/Zi_XLOBDo_Y')
        self.assertGreater(news_with_updated_video.updated_at, self.news_with_video.created_at)

    def test_soft_delete(self):
        news_to_delete = News.objects.create(title="Test_soft_delete", text="test_soft_delete_text")
        self.assertTrue(News.objects.filter(pk=news_to_delete.pk).exists())
        news_to_delete.is_deleted = True
        news_to_delete.save()
        self.assertTrue(News.objects.filter(pk=news_to_delete.pk).exists())
        self.assertTrue(News.objects.filter(is_deleted=True).exists())
        self.assertIn(news_to_delete, News.objects.filter(is_deleted=True))
        self.assertNotIn(news_to_delete, News.objects.filter(is_deleted=False))

    def test_hard_delete(self):
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
        with self.assertRaises(ProtectedError):
            self.city.delete()

    def test_region_deletion(self):
        with self.assertRaises(ProtectedError):
            self.region.delete()

    def test_author_default_value(self):
        tournament = Tournament.objects.create(
            name='Test Tournament',
            city=self.city,
            region=self.region,
            location='Test Location',
            board_size=19,
            rounds=5,
            date=datetime.date.today(),
            tournament_class='Test Class',
            regulations='Test Regulations'
        )
        self.assertEqual(tournament.uploaded_by_id, 1)


class GameModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.country = Country.objects.create(country_code='kg')
        cls.region = Region.objects.create(name='Test Region', country=cls.country)
        cls.city = City.objects.create(city='Bishkek', country=cls.country)
        cls.black_player = Player.objects.create(first_name='Black Player', country=cls.country)
        cls.white_player = Player.objects.create(first_name='White Player', country=cls.country)
        cls.tournament = Tournament.objects.create(name='Test Tournament', city=cls.city, rounds=3)
        cls.game = Game.objects.create(black=cls.black_player, white=cls.white_player,
                                       result='1-0', black_score=1, white_score=0,
                                       board_number=1, date=timezone.now(), tournament=cls.tournament,
                                       round_num=1, black_gor_change=200, white_gor_change=-200)

    def test_str_method(self):
        expected_method = f'{self.game.id}. {self.black_player} : {self.white_player} = 1-0'
        self.assertEqual(str(self.game), expected_method)

    def test_black_foreign_key(self):
        black_field = Game._meta.get_field('black')
        self.assertEqual(black_field.related_model, Player)

    def test_white_foreign_key(self):
        white_field = Game._meta.get_field('white')
        self.assertEqual(white_field.related_model, Player)

    def test_board_number_default_value(self):
        default_value = Game._meta.get_field('board_number').default
        self.assertEqual(default_value, 0)

    def test_date_field_type(self):
        date_field = Game._meta.get_field('date')
        self.assertIsInstance(date_field, DateTimeField)

    def test_tournament_foreign_key(self):
        tournament_field = Game._meta.get_field('tournament')
        self.assertEqual(tournament_field.related_model, Tournament)

    def test_round_num_positive_integer(self):
        round_num_field = Game._meta.get_field('round_num')
        self.assertIsInstance(round_num_field, PositiveIntegerField)

    def test_black_gor_change_float(self):
        black_gor_change_field = Game._meta.get_field('black_gor_change')
        self.assertIsInstance(black_gor_change_field, FloatField)

    def test_white_gor_change_float(self):
        white_gor_change_field = Game._meta.get_field('white_gor_change')
        self.assertIsInstance(white_gor_change_field, FloatField)

    def test_object_creation(self):
        self.assertEqual(self.game.black, self.black_player)
        self.assertEqual(self.game.white, self.white_player)
        self.assertEqual(self.game.result, '1-0')
        self.assertEqual(self.game.black_score, 1)
        self.assertEqual(self.game.white_score, 0)
        self.assertEqual(self.game.board_number, 1)
        self.assertIsNotNone(self.game.date)
        self.assertEqual(self.game.tournament, self.tournament)
        self.assertEqual(self.game.round_num, 1)
        self.assertEqual(self.game.black_gor_change, 200)
        self.assertEqual(self.game.white_gor_change, -200)

    def test_object_update(self):
        self.game.black_score = 0
        self.game.save()
        updated_game = Game.objects.get(pk=self.game.pk)
        self.assertEqual(updated_game.black_score, 0)

    def test_black_player_deletion(self):
        self.black_player.delete()
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())

    def test_white_player_deletion(self):
        self.white_player.delete()
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())


class CalendarModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        src = os.getcwd() + '/source/webapp/static/images'
        dst = os.getcwd() + '/source/uploads/calendar_images/'
        shutil.copy2(src + '/sengoku_logo.png', dst + 'sengoku_logo_for_test.png')
        shutil.copy2(src + '/11316.jpg', dst + '11316_for_test.jpg')
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.calendar = Calendar.objects.create(
            event_name="Test event",
            event_city="Bishkek",
            event_date="2023-03-04",
            text="Test event text",
            author=cls.user,
            deadline="2023-02-01"
        )
        cls.calendar_with_image = Calendar.objects.create(
            event_name="Event with image",
            event_city="Bishkek",
            event_date="2023-03-04",
            text="Test event with image",
            author=cls.user,
            calendar_image="calendar_images/sengoku_logo_for_test.png",
            deadline="2023-02-01"
        )

    @classmethod
    def tearDownClass(cls):
        sengoku_logo = os.getcwd() + '/source/uploads/calendar_images/sengoku_logo_for_test.png'
        dummy = os.getcwd() + '/source/uploads/calendar_images/11316_for_test.jpg'
        if os.path.isfile(sengoku_logo) or os.path.isfile(dummy):
            os.remove(sengoku_logo)
            os.remove(dummy)

    def test_author_foreign_key(self):
        author_field = Calendar._meta.get_field('author')
        self.assertEqual(author_field.related_model, accounts.models.User)

    def test_created_at_auto_now_add(self):
        created_at_field = Calendar._meta.get_field('created_at')
        self.assertTrue(created_at_field.auto_now_add)

    def test_updated_at_auto_now(self):
        updated_at_field = Calendar._meta.get_field('updated_at')
        self.assertTrue(updated_at_field.auto_now)

    def test_object_creation_no_image(self):
        self.assertEqual(self.calendar.event_name, 'Test event')
        self.assertEqual(self.calendar.event_city, 'Bishkek')
        self.assertEqual(self.calendar.event_date, "2023-03-04")
        self.assertEqual(self.calendar.text, 'Test event text')
        self.assertEqual(self.calendar.author, self.user)
        self.assertEqual(self.calendar.is_deleted, False)
        self.assertIsNotNone(self.calendar.created_at)
        self.assertIsNotNone(self.calendar.updated_at)

    def test_object_creation_with_image(self):
        self.assertEqual(self.calendar_with_image.event_name, 'Event with image')
        self.assertEqual(self.calendar_with_image.event_city, 'Bishkek')
        self.assertEqual(self.calendar_with_image.event_date, "2023-03-04")
        self.assertEqual(self.calendar_with_image.text, 'Test event with image')
        self.assertEqual(self.calendar_with_image.author, self.user)
        self.assertEqual(self.calendar_with_image.calendar_image, 'calendar_images/sengoku_logo_for_test.png')
        self.assertEqual(self.calendar_with_image.is_deleted, False)
        self.assertIsNotNone(self.calendar_with_image.created_at)
        self.assertIsNotNone(self.calendar_with_image.updated_at)

    def test_update_event_name(self):
        self.calendar.event_name = 'Updated event name'
        self.calendar.save()
        event_with_updated_name = Calendar.objects.get(pk=self.calendar.pk)
        self.assertEqual(event_with_updated_name.event_name, 'Updated event name')
        self.assertEqual(event_with_updated_name.is_deleted, False)
        self.assertGreater(event_with_updated_name.updated_at, self.calendar.created_at)

    def test_update_event_city(self):
        self.calendar.event_city = 'Osh'
        self.calendar.save()
        event_with_updated_city = Calendar.objects.get(pk=self.calendar.pk)
        self.assertEqual(event_with_updated_city.event_city, 'Osh')
        self.assertEqual(event_with_updated_city.is_deleted, False)
        self.assertGreater(event_with_updated_city.updated_at, self.calendar.created_at)

    def test_update_event_date(self):
        self.calendar.event_date = "2024-11-11"
        self.calendar.save()
        event_with_updated_date = Calendar.objects.get(pk=self.calendar.pk)
        self.assertEqual(event_with_updated_date.event_date, datetime.date(2024, 11, 11))
        self.assertEqual(event_with_updated_date.is_deleted, False)
        self.assertGreater(event_with_updated_date.updated_at, self.calendar.created_at)

    def test_update_event_text(self):
        self.calendar.text = 'Updated event text'
        self.calendar.save()
        event_with_updated_text = Calendar.objects.get(pk=self.calendar.pk)
        self.assertEqual(event_with_updated_text.text, 'Updated event text')
        self.assertEqual(event_with_updated_text.is_deleted, False)
        self.assertGreater(event_with_updated_text.updated_at, self.calendar.created_at)

    def test_update_event_deadline(self):
        self.calendar.deadline = "2023-12-12"
        self.calendar.save()
        event_with_updated_deadline = Calendar.objects.get(pk=self.calendar.pk)
        self.assertEqual(event_with_updated_deadline.deadline, datetime.date(2023, 12, 12))
        self.assertEqual(event_with_updated_deadline.is_deleted, False)
        self.assertGreater(event_with_updated_deadline.updated_at, self.calendar.created_at)

    def test_update_event_image(self):
        self.calendar_with_image.calendar_image = 'calendar_images/11316_for_test.jpg'
        self.calendar_with_image.save()
        event_with_updated_image = Calendar.objects.get(pk=self.calendar_with_image.pk)
        self.assertEqual(event_with_updated_image.calendar_image, 'calendar_images/11316_for_test.jpg')
        self.assertEqual(event_with_updated_image.is_deleted, False)
        self.assertGreater(event_with_updated_image.updated_at, self.calendar_with_image.created_at)

    def test_soft_delete(self):
        event_to_delete = Calendar.objects.create(
            event_name="Event with image to delete",
            event_city="Talas",
            event_date="2025-03-04",
            text="Test event with image to delete",
            author=self.user,
            calendar_image="calendar_images/sengoku_logo_for_test.png",
            deadline="2024-12-11"
        )
        self.assertTrue(Calendar.objects.filter(pk=event_to_delete.pk).exists())
        event_to_delete.is_deleted = True
        event_to_delete.save()
        sengoku_logo = os.getcwd() + '/source/uploads/calendar_images/sengoku_logo_for_test.png'
        self.assertTrue(os.path.isfile(sengoku_logo))
        self.assertTrue(Calendar.objects.filter(pk=event_to_delete.pk).exists())
        self.assertTrue(Calendar.objects.filter(is_deleted=True).exists())
        self.assertIn(event_to_delete, Calendar.objects.filter(is_deleted=True))
        self.assertNotIn(event_to_delete, Calendar.objects.filter(is_deleted=False))

    def test_hard_delete(self):
        event_to_delete = Calendar.objects.create(
            event_name="Event with image to hard delete",
            event_city="Talas",
            event_date="2025-10-14",
            text="Test event with image to hard delete",
            author=self.user,
            calendar_image="calendar_images/sengoku_logo_for_test.png",
            deadline="2024-12-13"
        )
        self.assertTrue(Calendar.objects.filter(pk=event_to_delete.pk).exists())
        event_to_delete.delete()
        self.assertNotIn(event_to_delete, Calendar.objects.filter(is_deleted=True))
        self.assertNotIn(event_to_delete, Calendar.objects.filter(is_deleted=False))
        self.assertFalse(Calendar.objects.filter(pk=event_to_delete.pk).exists())

    def test_author_default_value(self):
        event = Calendar.objects.create(
            event_name="Test event",
            event_city="Bishkek",
            event_date="2023-03-04",
            text="Test event text",
            author=self.user,
            deadline="2023-02-01"
        )
        self.assertEqual(event.author_id, get_author().id)


class PartnerModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        src = os.getcwd() + '/source/webapp/static/images'
        dst = os.getcwd() + '/source/uploads/partner_logo/'
        shutil.copy2(src + '/sengoku_logo.png', dst + 'sengoku_logo_for_test.png')
        shutil.copy2(src + '/no_image.jpg', dst + 'no_image_for_test.jpg')
        shutil.copy2(src + '/11316.jpg', dst + '11316_for_test.jpg')
        cls.partner = Partner.objects.create(
            name="Partner with image",
            logo="partner_logo/sengoku_logo_for_test.png"
        )
        cls.partner_with_link = Partner.objects.create(
            name="Test partner",
            logo="partner_logo/no_image_for_test.jpg",
            web_link="https://www.europeangodatabase.eu/"
        )

    @classmethod
    def tearDownClass(cls):
        sengoku_logo = os.getcwd() + '/source/uploads/partner_logo/sengoku_logo_for_test.png'
        dummy = os.getcwd() + '/source/uploads/partner_logo/11316_for_test.jpg'
        if os.path.isfile(sengoku_logo) or os.path.isfile(dummy):
            os.remove(sengoku_logo)
            os.remove(dummy)

    def test_object_creation(self):
        self.assertEqual(self.partner.name, 'Test partner')
        self.assertEqual(self.partner.logo, 'partner_logo/sengoku_logo_for_test.png')

    def test_object_creation_with_link(self):
        self.assertEqual(self.partner_with_link.name, 'Partner with image')
        self.assertEqual(self.partner_with_link.logo, "partner_logo/no_image_for_test.jpg")
        self.assertEqual(self.partner_with_link.web_link, "https://www.europeangodatabase.eu/")

    def test_update_partner_name(self):
        self.partner.name = 'Updated partner name'
        self.partner.save()
        partner_with_updated_name = Partner.objects.get(pk=self.partner.pk)
        self.assertEqual(partner_with_updated_name.name, 'Updated partner name')
        self.assertEqual(partner_with_updated_name.logo, "partner_logo/sengoku_logo_for_test.png")

    def test_update_partner_logo(self):
        self.partner.logo = 'partner_logo/11316_for_test.jpg'
        self.partner.save()
        partner_with_updated_logo = Partner.objects.get(pk=self.partner.pk)
        self.assertEqual(partner_with_updated_logo.logo, 'partner_logo/11316_for_test.jpg')

    def test_update_partner_link(self):
        self.partner_with_link.web_link = "https://www.kyrgyzgodatabase.kg/"
        self.partner_with_link.save()
        partner_with_updated_link = Partner.objects.get(pk=self.partner_with_link.pk)
        self.assertEqual(partner_with_updated_link.web_link, "https://www.kyrgyzgodatabase.kg/")

    def test_hard_delete(self):
        partner_to_delete = Partner.objects.create(
            name="Partner to delete",
            logo="partner_logo/sengoku_logo_for_test.png"
        )
        self.assertTrue(Partner.objects.filter(pk=partner_to_delete.pk).exists())
        partner_to_delete.delete()
        self.assertFalse(Calendar.objects.filter(pk=partner_to_delete.pk).exists())


class ClubModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.country = Country.objects.create(country_code='kg')
        cls.city = City.objects.create(city='Test City', country=cls.country)
        cls.region = Region.objects.create(name='Test Region', country=cls.country)
        cls.club = Club.objects.create(
            name='Test Club',
            EGDName='123456',
            city=cls.city,
            country=cls.country,
            region=cls.region,
            num_players=10,
            address='Test Address',
            phonenumber='+996555123456',
            web_link='https://www.example.com',
            schedule_from='10:00:00',
            schedule_to='18:00:00',
            breakfast_from='08:00:00',
            breakfast_to='09:00:00',
        )
        cls.club.coaches.add(cls.user)

    def test_coaches_field(self):
        club = Club.objects.get(name='Test Club')
        self.assertEqual(club.coaches.through.__name__, 'Club_coaches')
        self.assertEqual(club.coaches.through._meta.get_field('club').related_model.__name__, 'Club')
        self.assertEqual(club.coaches.through._meta.get_field('user').related_model.__name__, 'User')

    def test_create_club_with_required_fields(self):
        country = Country.objects.create(country_code='KG')
        city = City.objects.create(city='Test City', country=country)
        region = Region.objects.create(name='Test Region', country=country)
        club = Club.objects.create(name='Test Club', city=city, country=country, region=region)
        self.assertIsNotNone(club.id)

    def test_create_club_with_all_fields(self):
        country = Country.objects.create(country_code='KG')
        city = City.objects.create(city='Test City', country=country)
        region = Region.objects.create(name='Test Region', country=country)
        user = User.objects.create_user(username='testuser1', email='user1@example.com', password='testpass1')
        day_of_week = DayOfWeek.objects.create(name='Monday')
        club = Club.objects.create(
            name='Test Club',
            EGDName='test',
            city=city,
            country=country,
            region=region,
            num_players=10,
            address='Test Address',
            phonenumber='+996555123456',
            web_link='http://www.testclub.com',
            schedule_from=datetime.time(9, 0),
            schedule_to=datetime.time(18, 0),
            breakfast_from=datetime.time(12, 0),
            breakfast_to=datetime.time(13, 0)
        )
        club.coaches.add(user)
        club.days_of_work.add(day_of_week)
        club.day_of_week.add(day_of_week)
        self.assertIsNotNone(club.id)

    def test_update_club(self):
        country = Country.objects.create(country_code='KG')
        city = City.objects.create(city='Test City', country=country)
        region = Region.objects.create(name='Test Region', country=country)
        club = Club.objects.create(name='Test Club', city=city, country=country, region=region)
        club.name = 'Updated Club Name'
        club.save()
        updated_club = Club.objects.get(id=club.id)
        self.assertEqual(updated_club.name, 'Updated Club Name')
