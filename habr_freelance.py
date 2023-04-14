# Habr Freelance parser
# Telegram: @vi8ilante
# ---------------------
# python3 -m vevn .hf && source .hf/bin/activate
# pip install pyTelegramBotAPI
# pip install BeautifulSoup4
# ---------------------
import time
import sqlite3
import telebot
import datetime
import requests
import configparser
import urllib.parse
from bs4 import BeautifulSoup
from inspect import currentframe


# Read the config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Set variables
chat_id = config.getint('telegram', 'chat_id')
token = config.get('telegram', 'token')
words_to_find = config.get('keywords', 'words_to_find').split(',')
my_favorite_cats = config.get('categories', 'my_favorite_cats').split(',')
sleep_timer = int(config.get('main', 'sleep_timer'))
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

# Connect to the database and create a table to store the task titles and URLs
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (title TEXT, url TEXT)''')


# Main loop
while True:

    new_titles = []  # Move this line here

    response = requests.get(url)

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the task titles and URLs
    task_titles = []
    task_urls = []
    for title in soup.find_all('div', class_='task__title'):
        task_titles.append(title['title'])
        task_urls.append('https://freelance.habr.com' + title.a['href'])

    # Insert the task titles and URLs into the database
    for i, title in enumerate(task_titles):
        # Check if the title and URL are already saved in the database
        c.execute('SELECT COUNT(*) FROM tasks WHERE title=? AND url=?', (title, task_urls[i]))
        count = c.fetchone()[0]

        if count == 0:
            # If the title and URL are new, add them to the new_titles list and insert them into the database
            new_titles.append(title)
            c.execute('INSERT INTO tasks VALUES (?, ?)', (title, task_urls[i]))
            conn.commit()

    # Check if there are any new titles
    if new_titles:
        # Print the new titles and URLs
        for title, url in reversed(list(zip(new_titles, task_urls))):
            print(title)
            print(url)
            try:
                # bot.send_message(chat_id, f'{title}\n{url}')
                bot.send_message(chat_id, url)
                time.sleep(3)
            except Exception as e:
                get_linenumber()
                print(line_number, 'exception: {}'.format(e))
                pass
    else:
        print('No new data',datetime.datetime.now())

    # Close the database connection
    conn.close()

    time.sleep(sleep_timer)

    # Reconnect to the database
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
