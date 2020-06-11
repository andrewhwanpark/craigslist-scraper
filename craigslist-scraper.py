from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib.request
import json


class CraigslistScraper(object):
    def __init__(self, location, postal, max_price, radius):
        self.location = location
        self.postal = postal
        self.max_price = max_price
        self.radius = radius
        # URL
        self.url = f"https://{location}.craigslist.org/search/sss?search_distance={radius}&postal={postal}&max_price={max_price}"
        # Selenium webdriver
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

    # Extract titles, dates, prices
    def extract_post_info(self):
        all_post = self.driver.find_elements_by_class_name("result-row")
        soup = BeautifulSoup(self.driver.page_source, "lxml")

        dates = []
        titles = []
        prices = []
        images = []

        # Scrape image URLs
        for row in soup.findAll("li", {"class": "result-row"}):
            img = row.find("img")
            if img is None:
                images.append("null")
            if isinstance(img, Tag) and img.has_attr("src"):
                images.append(img['src'])

        # Scrape title, price, date
        for post in all_post:
            title = post.text.split("$")

            if title[0] == '':
                title = title[1]
            else:
                title = title[0]

            title = title.split("\n")
            # Oddity: If no pictures are uploaded & price is 0, price is not scraped
            # Thus, if price is not a digit, set to 0
            price = title[0] if title[0].isdigit() else "0"
            title = title[-1]

            title = title.split(" ")
            month = title[0]
            day = title[1]
            title = ' '.join(title[2:])
            date = month + " " + day

            dates.append(date)
            titles.append(title)
            prices.append(price)

        return dates, titles, prices, images

    # Extract Post URLs
    def extract_post_urls(self):
        all_url = []
        html_page = urllib.request.urlopen(self.url)
        soup = BeautifulSoup(html_page, "lxml")

        for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
            all_url.append(link["href"])

        return all_url

    # Extract listing descriptions
    def extract_post_desc(self, all_url):
        descs = []

        for url in all_url:
            self.driver.get(url)
            try:
                wait = WebDriverWait(self.driver, self.delay)
                # Wait until HTML element "postingbody" is loaded
                wait.until(EC.presence_of_element_located(
                    (By.ID, "postingbody")))
            except TimeoutException:
                print("Loading timed out")

            soup = BeautifulSoup(self.driver.page_source, "lxml")

            for desc in soup.findAll("section", {"id": "postingbody"}):
                # Remove unwanted div inside section: QR code info
                unwanted = desc.find("div")
                unwanted.extract()
                descs.append(desc.text.strip())

        return descs

    def quit(self):
        self.driver.close()


# Parameters: Change them to your desired config
location = "newyork"
postal = "10012"
max_price = "2000"
radius = "5"

scraper = CraigslistScraper(location, postal, max_price, radius)
scraper.load_craigslist_url()
dates, titles, prices, images = scraper.extract_post_info()
urls = scraper.extract_post_urls()
descs = scraper.extract_post_desc(urls)
scraper.quit()
