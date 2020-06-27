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
        thumbnails = []
        images = []

        # Scrape all images
        for img_gallery in soup.findAll("a", {"class": "result-image"}):
            temp = []

            # Check if listing has no images
            if img_gallery.has_attr("title"):
                images.append("null")
            else:
                # We can construct image URL with data-ids attr
                data_id = img_gallery["data-ids"].split(',')
                for data in data_id:
                    cleaned = "https://images.craigslist.org/" + \
                        data.split(":", 1)[1] + "_1200x900.jpg"
                    temp.append(cleaned)
                images.append(temp)

        # Scrape thumbnails URLs
        for row in soup.findAll("li", {"class": "result-row"}):
            img = row.find("img")
            if img is None:
                thumbnails.append("null")
            if isinstance(img, Tag) and img.has_attr("src"):
                thumbnails.append(img['src'])

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

        return dates, titles, prices, thumbnails, images

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

            # Scrape desc
            for desc in soup.findAll("section", {"id": "postingbody"}):
                # Remove unwanted div inside section: QR code info
                unwanted = desc.find("div")
                unwanted.extract()
                descs.append(desc.text.strip())

        return descs

    # Convert output into json file
    @staticmethod
    def convert_into_json(dates, titles, prices, thumbnails, images, descs):
        output = []

        for index, (date, title, price, thumbnail, image, desc) in enumerate(zip(dates, titles, prices, thumbnails, images, descs)):
            json_info = {
                'title': title,
                'price': price,
                'date': date,
                'thumbnail': thumbnail,
                'image': image,
                'desc': desc,
                'id': index  # Create keys for React (1,2,3,...)
            }

            output.append(json_info)

        with open("output.json", "w") as outfile:
            json.dump(output, outfile, indent=4)

    def quit(self):
        self.driver.close()


# Parameters: Change them to your desired config
location = "newyork"
postal = "10012"
max_price = "2000"
radius = "5"

# Initialize scraper
scraper = CraigslistScraper(location, postal, max_price, radius)
# Load URL with parameters
scraper.load_craigslist_url()
# Scrape date, titles, prices, images
dates, titles, prices, thumbnails, images = scraper.extract_post_info()
# Scrape URLs: used for description scraping
urls = scraper.extract_post_urls()
# Scrape descriptions of each listing
descs = scraper.extract_post_desc(urls)
# Quit selenium driver
scraper.quit()
# Convert output into json file
scraper.convert_into_json(dates, titles, prices, thumbnails, images, descs)
