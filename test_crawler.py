import unittest
from datetime import datetime, timedelta

from crawler import NeCrawler

class TestCrawler(unittest.TestCase):

    def test_get_source(self):
        crawler = NeCrawler()
        target_url = 'https://www.bbc.co.uk/sport/tennis/61693135'
        response = crawler.get_source(target_url)
        self.assertTrue(response.status_code == 200)

    def test_html_parser(self):
        crawler = NeCrawler()
        target_url = 'https://www.bbc.co.uk/sport/tennis/61693135'
        response = crawler.get_source(target_url)
        soup = crawler.html_parser(response.text)
        results = soup.findAll("div")
        self.assertTrue(len(results) > 0)

    def test_html_getText(self):
        crawler = NeCrawler()
        target_url = 'https://www.bbc.co.uk/sport/tennis/61693135'
        response = crawler.get_source(target_url)
        soup = crawler.html_parser(response.text)
        orignal_text = crawler.html_getText(soup)
        self.assertTrue(len(orignal_text) > 0)

    def test_google_news_datetime_calculator(self):
        crawler = NeCrawler()
        currentDatetime = datetime(2022, 6, 4)
        deltaDatetimeString = '3 天前'
        specificDatetime = crawler.google_news_datetime_calculator(currentDatetime, deltaDatetimeString)
        self.assertEqual(specificDatetime, '2022-06-01')

if __name__ == '__main__':
    unittest.main()

