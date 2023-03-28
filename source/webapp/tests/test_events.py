from django.test import TestCase
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EventCreateTest(TestCase):
    def setUp(self):
        self.driver = Chrome()
        self.driver.get('http://localhost:8000/accounts/login/')
        self.driver.find_element(By.ID, 'username').send_keys('admin')
        self.driver.find_element(By.ID, 'password').send_keys('admin')
        self.driver.find_element(By.ID, 'login_button').click()
        self.driver.get('http://localhost:8000/')

    def tearDown(self):
        self.driver.close()

    def test_create_event_displays_all_fields(self):
        self.driver.get('http://localhost:8000/event_create/')
        self.driver.find_element(By.NAME, 'event_name').send_keys('Test event #1')
        self.driver.find_element(By.NAME, 'event_city').send_keys('New York')
        self.driver.find_element(By.NAME, 'event_date').send_keys('03/30/2024')
        self.driver.find_element(By.NAME, 'text').send_keys('Test text from tester')
        self.driver.find_element(By.NAME, 'deadline').send_keys('04/30/2023, 10:10 10')
        self.driver.implicitly_wait(5)
        self.driver.find_element(By.CLASS_NAME, 'kgf_modal').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "confirm_button"))).click()
        self.driver.maximize_window()
        print(f"CURRENT_URL: {self.driver.current_url}")
        assert self.driver.current_url == 'http://localhost:8000/'