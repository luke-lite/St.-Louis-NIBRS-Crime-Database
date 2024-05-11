from bs4 import BeautifulSoup
import requests
import pandas as pd

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
page = requests.get(page_url)

parser = BeautifulSoup(page.content, "html.parser")
block = parser.find('div', attrs = {'class': 'news_div', 'id': 'news_div'})

curr_entry_month = 'March'
curr_entry_year = '2024'
next_entry_month = 'April'
next_entry_year = '2025'

entries = block.findAll('a')
recent_entry = entries[-1]
tail_url = recent_entry['href']
tail_url

csv_link = base_url + tail_url
response = requests.get(csv_link)