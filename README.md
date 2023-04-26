# Habr Freelance Telegram
Скрипт парсит Хабр Фриланс и отправляет новые заказы в телеграм канал

![image](https://user-images.githubusercontent.com/130507972/232136344-fbcaa884-0eda-4cd2-a8c9-f39c801439b3.png)

Вы можете поменять сферу деятельности в конфиге, а так же вписать туда свой тг канал, куда слать оповещения.

![image](https://user-images.githubusercontent.com/130507972/232136056-d48af87c-81b8-441d-9f70-1598c3539e78.png)

![image](https://user-images.githubusercontent.com/130507972/232136207-648d0830-a1fa-4f5a-9f35-f5941a84278a.png)


В планах сделать бота, в котором любой пользователь может выбрать разделы, по которым хочет получать уведомения о новых задачах, либо даже можно указывать ключевые слова.

Для установки поставьте нужныe библиотеки:

<code>pip install pyTelegramBotAPI</code>

<code>pip install BeautifulSoup4</code>

<code>pip install duckdb</code>


p.s. проект сделан, чтобы протестировать как работать с БД DuckDB и делать конфиги через ini-файлы. И то и другое "через жопу". Лучше конфиги делать через config.py, а базу использовать нормальный sqlite.
