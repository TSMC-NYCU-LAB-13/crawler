# Schedule: run once a week at 23:59

# Load Packages
import os
from GoogleNews import GoogleNews
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests_html import HTMLSession
from time import sleep
import mysql.connector
from mysql.connector import Error
import pytz
import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning

# ssl.SSLContext.check_hostname = False
# ssl.SSLContext.verify_mode = property(lambda self: ssl.CERT_NONE, lambda self, newval: None)
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Class: NeCrawler
class NeCrawler():
    def __init__(self):
        self.result_pages = 10

    def get_source(self, url):
        try:
            session = HTMLSession()
            response = session.get(url, verify=ssl.CERT_NONE)
            session.close()
            return response
        # except (requests.exceptions.RequestException, requests.exceptions.SSLError, requests.exceptions.RetryError) as e:
        #     print(e)
        except Exception as e:
            print(e)

    def html_parser(self, htmlText):
        soup = BeautifulSoup(htmlText, 'html.parser')
        return soup

    def html_get_text(self, soup):
        text_of_p_tag = ''
        for el in soup.find_all('p'):
            text_of_p_tag += ''.join(el.find_all(string=True))
        return text_of_p_tag

    def google_news_datetime_calculator(self, dt_now, dt_delta_string):
        # Calculate news date based on '? 天前'
        if "天" in dt_delta_string:
            dt_now -= timedelta(days=int(dt_delta_string.split()[0]))
        return dt_now.strftime('%Y-%m-%d')

    def prepare_google_news_result(self, keyword, googlenews=None, page_news=None):
        news_ne = []
        news_links = []
        tz_taipei = pytz.timezone('Asia/Taipei')
        dt_now = datetime.now(tz_taipei)
        for i in range(1, self.result_pages + 1):
            if googlenews is not None:
                page_news = googlenews.page_at(i)
            # filter YouTube because no content
            if len(page_news) > 0:
                page_news_without_youtube = list(filter(lambda pn: pn['media'] != 'YouTube', page_news))
                for pnwy in page_news_without_youtube:
                    if pnwy['link'] not in news_links:
                        news_ne.append({
                            'title': pnwy['title'],
                            'url': pnwy['link'],
                            'time': self.google_news_datetime_calculator(dt_now, pnwy['date']),
                            'keyword': keyword,
                            'content': '',
                        })
                        # prepare to compare if links duplicate
                        news_links.append(pnwy['link'])
        return news_ne

    def db_connect(self, db_options):
        try:
            return mysql.connector.connect(**db_options)
        except Error as e:
            print('[NeCrawler/ERROR]: Database connection error', e)

    def db_disconnect(self, connection):
        if (connection.is_connected()):
            connection.close()
        return connection

    def write_crawled_data_to_db(self, connection, news_ne, db_table):
        try:
            cursor = connection.cursor()
            for news in news_ne:
                sql_cmd = "INSERT INTO " + db_table + " (title, url, time, keyword, content) values (%s, %s, %s, %s, %s);"
                cmd_val = tuple(i for i in [v for k, v in news.items()])
                try:
                    cursor.execute(sql_cmd, cmd_val)
                    connection.commit()
                    # print('[NeCrawler/SUCCESS]: Store crawl data - ', news['time'], news['title'])
                except Error as e:
                    print('[NeCrawler/ERROR]: Insert database error - ', news['time'], news['title'], e)

        except Error as e:
            print('[NeCrawler/ERROR]: Database connection error', e)

        finally:
            if (connection.is_connected()):
                cursor.close()
                # print('[NeCrawler/FINISH]: Store crawl data')

def gen_end_date_based_on_start_date_for_google_news(start_date):
    period_day = 7
    date_format = '%m/%d/%Y'
    datetime_start = datetime.strptime(start_date, date_format)
    datetime_delta = timedelta(days = (period_day - 1))
    datetime_end = datetime_start + datetime_delta
    return datetime_end.strftime(date_format)


if __name__ == "__main__":
    load_dotenv(override = True)

    # Init NeCrawler
    ne_crawler = NeCrawler()

    # Search related news by GoogleNews
    start_date = os.getenv('NEWS_START_DATE')
    if start_date != '':
        news_options = {
            'lang': 'zh-TW',
            'region': 'TW',
            'start': start_date,
            'end': gen_end_date_based_on_start_date_for_google_news(start_date),
            'encode': 'utf-8'
        }
    else:
        news_options = {
            'lang': 'zh-TW',
            'region': 'TW',
            'period': '7d',
            'encode': 'utf-8'
        }
    keyword = os.getenv('NEWS_KEYWORD')
    googlenews = GoogleNews(**news_options)
    googlenews.search(keyword)
    print('[NeCrawler/SUCCESS]: Search Google news')

    # Prepare google news results
    news_ne = ne_crawler.prepare_google_news_result(keyword, googlenews)

    # START CRAWL!
    for item in news_ne:
        try:
            response = ne_crawler.get_source(item['url'])
            soup = ne_crawler.html_parser(response.text)
            content = ne_crawler.html_get_text(soup)
            item['content'] = content.strip()
            sleep(1)
        except Exception as e:
            print(e)
    print('[NeCrawler/SUCCESS]: Crawl contents')

    # Setup DB
    db_options = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
    }
    db_table = os.getenv('DB_TABLE')

    db_connection = ne_crawler.db_connect(db_options)

    # Store crawled data to DB
    ne_crawler.write_crawled_data_to_db(db_connection, news_ne, db_table)
    print('[NeCrawler/SUCCESS]: Store crawl data - ', len(news_ne))

    ne_crawler.db_disconnect(db_connection)
