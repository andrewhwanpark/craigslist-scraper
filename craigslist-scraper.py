from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import urllib.request

class CraigslistScraper(object):
    def __init__(self, location, postal, max_price, radius):
        self.location = location
        self.postal = postal
        self.max_price = max_price
        self.radius = radius
        # URL
        self.url = f"https://{location}.craigslist.org/search/sss?search_distance={radius}&postal={postal}&max_price={max_price}"
        # Selenium browser
        self.driver = webdriver.Chrome()
        # Load delay
        self.delay = 3

    def load_craigslist_url(self):
        self.driver.get(self.url)
        try:
            wait = WebDriverWait(self.driver, self.delay)
            # Wait until HTML element "searchform" is loaded
            wait.until(EC.presence_of_element_located((By.ID, "searchform")))
            print("Ready")
        except TimeoutException:
            print("Loading timed out")

    # Extract Post titles from all class "result-row" elements
    def extract_post_titles(self):
        all_post = self.driver.find_elements_by_class_name("result-row")
        post_title_list = []

        for post in all_post:
            post_title_list.append(post.text)

        return post_title_list

    def extract_post_urls(self):
        all_url = []
        html_page = urllib.request.urlopen(self.url)
        soup = BeautifulSoup(html_page, "lxml")

        for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
            all_url.append(link["href"])
        print(all_url)
        return all_url

location = "newyork"
postal = "10012"
max_price = "2000"
radius = "5"

scraper = CraigslistScraper(location, postal, max_price, radius)
scraper.load_craigslist_url()
# scraper.extract_post_titles()
scraper.extract_post_urls()
