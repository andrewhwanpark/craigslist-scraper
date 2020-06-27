# craigslist-scraper

Craigslist Web Scraper made to scrap data in order to populate our [craigslist-redux project](https://github.com/andrewhwanpark/craigslist-redux), in which we clone craigslist.org using modern technologies.

## Pre-reqs: Install Chromedriver

Selenium won't work with Chrome unless you install chromedriver.

```zsh
brew install chromedriver
```

If you are a Firefox user, you can just change the constructor to:

```python
self.driver = webdriver.Firefox()
```

## How it works

The scraper will scrape one page of recent craigslist postings given parameters. You can adjust the parameters at the bottom of the code. Note that the location must be the same string in your craigslist URL. For example, in NYC, the location is "newyork".

```python
location = "newyork"
postal = "10012"
max_price = "2000"
radius = "5"
```

## Output

The scraper will output a output.json file with the scraped titles, post descriptions, thumbnails, images, dates, and prices. The images are original size (1200x900).
