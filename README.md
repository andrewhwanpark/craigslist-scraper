# craigslist-scraper

Craigslist Web Scraper made to scrap data in order to populate our [craigslist-redux project](https://github.com/andrewhwanpark/craigslist-redux), in which we clone craigslist.org using modern technologies.

# How it works

The scraper will scrape one page of recent craigslist postings given parameters. You can adjust the parameters at the bottom of the code. Note that the location must be the same string in your craigslist URL. For example, in NYC, the location is "newyork".

```python
location = "newyork"
postal = "10012"
max_price = "2000"
radius = "5"
```
