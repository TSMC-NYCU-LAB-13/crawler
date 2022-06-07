# Schedule: run once a week at 23:59

# Load Packages
import os
import pandas as pd
from GoogleNews import GoogleNews
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from requests_html import HTMLSession
from time import sleep
import mysql.connector
from mysql.connector import Error
import pytz

# Variables (const)
tz_taipei = pytz.timezone('Asia/Taipei')
keyword = '氖氣'
result_pages = 10

# Class: NeCrawler
class NeCrawler():
    def __init__(self):
        self.url = 'https://www.google.com/search?q='

    def get_source(self, url):
        try:
            session = HTMLSession()
            response = session.get(url)
            return response
        except requests.exceptions.RequestException as e:
            print(e)

    def html_parser(self, htmlText):
        soup = BeautifulSoup(htmlText, 'html.parser')
        return soup

    def html_getText(self, soup):
        text_of_p_tag = ''
        for el in soup.find_all('p'):
            text_of_p_tag += ''.join(el.find_all(text=True))
        return text_of_p_tag

def google_news_datetime_calculator(dt_string):
    # Calculate news date based on '? 天前'
    dt_now = datetime.now(tz_taipei)
    if "天" in dt_string:
        dt_now -= timedelta(days=int(dt_string.split()[0]))
    return dt_now.strftime('%Y-%m-%d')

# Search related news by GoogleNews
news_options = {
    'lang' = 'zh-TW',
    'region' = 'TW',
    'period' = '7d',
    'encode' = 'utf-8'
}
googlenews = GoogleNews(**news_options)
googlenews.search(keyword)
print('[NeCrawler/SUCCESS]: Search Google news')

# Prepare google news results
news_ne = []
for i in range(1, result_pages + 1):
    page_news = googlenews.page_at(i)
    # filter YouTube because no content
    page_news_without_youtube = list(filter(lambda pn: pn['media'] != 'YouTube', page_news))
    for pnwy in page_news_without_youtube:
        news_ne.append({
            'title': pnwy['title'],
            'url': pnwy['link'],
            'time': google_news_datetime_calculator(pnwy['date']),
            'keyword': keyword,
            'content': '',
        })

# START CRAWL!
crawler = NeCrawler()
for item in news_ne:
    response = crawler.get_source(item['url'])
    soup = crawler.html_parser(response.text)
    content = crawler.html_getText(soup)
    item['content'] = content.strip()
    sleep(1)

print('[NeCrawler/SUCCESS]: Crawl contents')

# Init DB
load_dotenv(override = True)
db_options = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
}
db_table = os.getenv('DB_TABLE')

# Store crawled data to DB
try:
    connection = mysql.connector.connect(**db_options)
    cursor = connection.cursor()

    for news in news_ne:
        sql_cmd = "INSERT INTO " + db_table + " (title, url, time, keyword, content) values (%s, %s, %s, %s, %s);"
        cmd_val = tuple(i for i in [v for k, v in news.items()])
        cursor.execute(sql_cmd, cmd_val)
        connection.commit()

except Error as e:
    print('[NeCrawler/ERROR]: Database connection error', e)

finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print('[NeCrawler/SUCCESS]: Store crawl data')

