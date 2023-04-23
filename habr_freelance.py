# Habr Freelance parser
# Telegram: @vi8ilante
# ---------------------
# python3 -m vevn .hf && source .hf/bin/activate
# pip install pyTelegramBotAPI
# pip install BeautifulSoup4
# pip install duckdb
# ---------------------

import time
import duckdb
import telebot
import hashlib
import datetime
import requests
import configparser
import urllib.parse
from bs4 import BeautifulSoup
from inspect import currentframe
from functools import wraps


while True:
    # Read the config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Set variables
    chat_id = config.getint('telegram', 'chat_id')
    token = config.get('telegram', 'token')
    words_to_find = config.get('keywords', 'words_to_find').split(',')
    my_favorite_cats = config.get('categories', 'my_favorite_cats').split(',')
    SLEEP_TIMER = int(config.get('main', 'sleep_timer'))
    base_url = config.get('categories', 'base_url')

    # Make the URL
    categories = ','.join(my_favorite_cats)
    url = base_url + urllib.parse.quote(categories)
    # print(url)

    # Define the telegram bot
    bot = telebot.TeleBot(token)

    # Error handling
    def get_linenumber():
        cf = currentframe()
        global line_number
        line_number = cf.f_back.f_lineno

    # Retry decorator
    def retry(max_retries, delay_seconds):
        def decorator_retry(func):
            @wraps(func)
            def wrapper_retry(*args, **kwargs):
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(f'Exception {e} occurred, retrying in {delay_seconds} seconds')
                        retry_count += 1
                        time.sleep(delay_seconds)
                print(f'Max retries ({max_retries}) exceeded, raising last exception')
                raise e

            return wrapper_retry

        return decorator_retry

    # Connect to the database and create a table to store the task titles and URLs
    conn = duckdb.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (title_hash TEXT, url_hash TEXT)''')
    conn.commit()

    # Initialize new titles list
    new_titles = []

    # Get HTML content
    @retry(5, 2)
    def get_html_content():
        response = requests.get(url)
        return response.content

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(get_html_content(), 'html.parser')

    # Find all the task titles and URLs
    task_titles = []
    task_urls = []
    for title in soup.find_all('div', class_='task__title'):
        task_titles.append(title['title'])
        task_urls.append('https://freelance.habr.com' + title.a['href'])

    # Compute the hashes of the task titles and URLs
    title_hashes = [hashlib.sha256(title.encode()).hexdigest() for title in task_titles]
    url_hashes = [hashlib.sha256(url.encode()).hexdigest() for url in task_urls]

    # Insert the task title and URL hashes into the database
    for i, title_hash in enumerate(title_hashes):
        url_hash = url_hashes[i]
        # Check if the title and URL hashes are already saved in the database
        c.execute('SELECT COUNT(*) FROM tasks WHERE title_hash=? AND url_hash=?', (title_hash, url_hash))
        count = c.fetchone()[0]
        
        # If the title and URL hashes are new, add them to the new_titles list and insert them into the database
        if count == 0:
            new_titles.append((task_titles[i], task_urls[i]))
            c.execute('INSERT INTO tasks VALUES (?, ?)', (title_hash, url_hash))
            conn.commit()

    # Check if there are any new titles
    if new_titles:
        # Print the new titles and URLs
        for title, url in reversed(new_titles):
            print(title)
            print(url)
            try:
                # bot.send_message(chat_id, f'{title}\n{url}')
                bot.send_message(chat_id, url)
                time.sleep(3)
            except Exception as e:
                print('exception: {}'.format(e))
                pass
    else:
        print('No new data', datetime.datetime.now())

    # Close the database connection
    conn.close()

    time.sleep(SLEEP_TIMER)
