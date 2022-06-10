import os
import pytz
import unittest
from datetime import datetime
from dotenv import load_dotenv
from crawler import NeCrawler, gen_end_date_based_on_start_date_for_google_news

load_dotenv(override = True)

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

    def test_html_get_text(self):
        crawler = NeCrawler()
        target_url = 'https://www.bbc.co.uk/sport/tennis/61693135'
        response = crawler.get_source(target_url)
        soup = crawler.html_parser(response.text)
        orignal_text = crawler.html_get_text(soup)
        self.assertTrue(len(orignal_text) > 0)

    def test_google_news_datetime_calculator(self):
        crawler = NeCrawler()
        current_datetime = datetime(2022, 6, 4)
        delta_datetime_string = '3 天前'
        specific_datetime = crawler.google_news_datetime_calculator(current_datetime, delta_datetime_string)
        self.assertEqual(specific_datetime, '2022-06-01')

    def test_prepare_google_news_result(self):
        crawler = NeCrawler()
        tz_taipei = pytz.timezone('Asia/Taipei')
        dt_now = datetime.now(tz_taipei)
        keyword = os.getenv('NEWS_KEYWORD')
        test_original_crawler_data = [
            {
                'title': 'test_title1',
                'media': 'test_media1',
                'date': '3 天前',
                'datetime': None,
                'desc': 'test_desc1',
                'link': 'test_link1',
                'img': 'test_img1'
            }, {
                'title': 'test_title2',
                'media': 'YouTube',
                'date': '3 天前',
                'datetime': None,
                'desc': 'test_desc2',
                'link': 'test_link2',
                'img': 'test_img2'
            }, {
                'title': 'test_title3',
                'media': 'test_media3',
                'date': '3 天前',
                'datetime': None,
                'desc': 'test_desc3',
                'link': 'test_link1',
                'img': 'test_img3'
            }
        ]
        test_prepared_crawler_data = [
            {
                'title': 'test_title1',
                'url': 'test_link1',
                'time': crawler.google_news_datetime_calculator(dt_now, '3 天前'),
                'keyword': keyword,
                'content': ''
            }
        ]
        prepared_data = crawler.prepare_google_news_result(keyword, page_news=test_original_crawler_data)
        self.assertEqual(prepared_data, test_prepared_crawler_data)

    def test_db_connect(self):
        crawler = NeCrawler()
        db_connection = crawler.db_connect({
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
        })
        self.assertTrue(db_connection.is_connected())

    def test_db_disconnect(self):
        crawler = NeCrawler()
        db_connection = crawler.db_connect({
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
        })
        if db_connection.is_connected():
            db_disconnection = crawler.db_disconnect(db_connection)
            self.assertFalse(db_disconnection.is_connected())
        else:
            self.assertEqual(1, 2)

    def test_write_crawled_data_to_db(self):
        test_db_table = os.getenv('DB_TABLE') + '_test'
        test_news = [
            {
                'title': 'test_title1',
                'url': 'test_url1',
                'time': '2022-01-01',
                'keyword': 'test_keyword1',
                'content': 'test_content1',
            }, {
                'title': 'test_title2',
                'url': 'test_url2',
                'time': '2022-01-01',
                'keyword': 'test_keyword2',
                'content': 'test_content2',
            }
        ]

        crawler = NeCrawler()
        db_connection = crawler.db_connect({
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
        })
        cursor = db_connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS ' + test_db_table + ' ( `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT, `title` text COLLATE utf8mb4_unicode_ci NOT NULL, `url` text COLLATE utf8mb4_unicode_ci NOT NULL, `time` datetime NOT NULL, `keyword` text COLLATE utf8mb4_unicode_ci NOT NULL, `content` text COLLATE utf8mb4_unicode_ci NOT NULL, `emotional_value` double DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(), PRIMARY KEY (`id`), UNIQUE KEY `url_unique` (`url`(768)) USING HASH, KEY `keyword_index` (`keyword`(768)) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci')
        crawler.write_crawled_data_to_db(db_connection, test_news, test_db_table)
        cursor.execute('SELECT COUNT(*) FROM ' + test_db_table)
        length_retrive_data = cursor.fetchall()[-1][-1]
        cursor.execute('DROP TABLE ' + test_db_table)
        cursor.close()
        self.assertEqual(len(test_news), length_retrive_data)

    def test_gen_end_date_based_on_start_date_for_google_news(self):
        start_date = '06/04/2022' # MM/DD/YYYY
        end_date = gen_end_date_based_on_start_date_for_google_news(start_date)
        self.assertEqual(end_date, '06/10/2022')

if __name__ == '__main__':
    unittest.main()

