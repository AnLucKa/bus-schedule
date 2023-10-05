import requests
from bs4 import BeautifulSoup
import json
import os
import re
from csv import writer
import csv
import shutil
from tqdm import tqdm
import time

url = "https://mybuses.ru/balashiha/"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

#получаем текст запроса
def get_html(url, headers):
    response = requests.get(url, headers=headers)
    return response.text


#создаем таблицы в виде списокв на основе расписания и 2 файла в текущей директории:
#по одному на расписание в каждую сторону
def save_csvs(name, url, headers):
    response = get_html(url, headers)
    soup = BeautifulSoup(response, "lxml")
    tables = soup.find_all("table")
    for table in tables:
        name, schedule_table = get_dict(table)
        name = name.replace('/', '-')
        with open(f'{name}.csv', 'w', encoding='utf-8-sig', newline='') as file:
            table_writer = writer(file, delimiter = ';')
            table_writer.writerows(schedule_table)

#формирует кортежи (имя файла, таблица в виде списка)
def get_dict(table):
    name = re.split("[():]", table.find_previous_sibling("h2").text)[1].strip()
    schedule_table = [[]]
    for column in table.find("thead").find_all("th"):
        schedule_table[0].append(column.text.strip())
    for row in table.tbody.find_all("tr"):
        schedule_table.append([])
        for item in row.find_all("td"):
            schedule_table[-1].append(item.text)
    # print(schedule_table)
    return name, schedule_table

starttime = time.time()
with open("index.html", "w") as file:
    file.write(get_html(url, headers))

with open("index.html", "r") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")

divs = soup.find_all("div", class_="panel panel-info")
schedules = {}
for div in divs:
    schedules[div.find("h2").text.strip()] = {bus.get("title") : bus.get("href") for bus in \
                             div.find_next("div", class_="list-group").children if bus.name == "a"}

if not os.path.isdir('data'):
    os.mkdir('data')
os.chdir('data')



with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(schedules, file, indent = 4, ensure_ascii=False)


for key, item in schedules.items():
    folder = key.capitalize()
    if not os.path.isdir(folder):
        os.mkdir(folder)
    os.chdir(folder)
    for name, link in tqdm(item.items()):
        link = f'{url[:-11]}{link}'
        name = name.replace('/', '-')
        folder = name
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)
        os.chdir(folder)
        save_csvs(name, link, headers)
        os.chdir('..')
    #     break
    # break
    os.chdir('..')
print(time.time()-starttime)
