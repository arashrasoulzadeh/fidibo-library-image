# -*- coding: utf-8 -*-
import os.path
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image, ImageDraw
import arabic_reshaper
from bidi.algorithm import get_display
import os
from urllib.parse import urlparse

token = ""
PHPSESSID = ""  # get from browser cookies
is_empty = False
books = []
if not os.path.exists('images'):
    os.makedirs('images')


def get_name(url):
    a = urlparse(url)
    return os.path.basename(a.path)


def file_exists(path):
    if os.path.isfile(path):
        return True
    else:
        return False


def download_image(url):
    file_name = 'images/{}'.format(get_name(url))
    if not file_exists(file_name):
        r = requests.get(url, allow_redirects=True)
        open(file_name, 'wb').write(r.content)


def is_last(paginations):

    for p in paginations:
        if p.text == "بعدی ›":
            return False
    return True


def load_page(num):
    global books
    url = "https://fidibo.com/library?page={}".format(num)
    page = requests.get(url, cookies={"PHPSESSID": PHPSESSID})
    # print(page.text)   # This should print 200
    soup = BeautifulSoup(page.text, 'html.parser')

    pages = soup.find_all('div', class_="row book")
    paginations = soup.find_all('li', class_="change_page")
    is_last(paginations)

    for page in pages:
        title = page.find("h2", class_="title")
        image = "https://fidibo.com{}".format(
            page.find("img")['src'])
        download_image(image)
        books.append({
            "title": title.text.replace("کتاب ", "").replace("صوتی ", ""),
            "image": get_name(image)
        })
    if is_last(paginations):
        pass
    else:
        load_page(num+1)


print("loading books...")
load_page(1)


image = Image.open('shelf.png')
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('yekan.ttf', size=25, encoding='unic')
print("generating image...")
# for book in books:
last_x, last_y, index_x, index_y = 0, 230, 1, 1
last_cover_x, last_cover_y, index_cover_x, index_cover_y = 0, 230, 1, 1
logo = Image.open("logo.png")


def get_text_pos():
    global last_x
    global last_y
    global index_x
    global index_y
    if index_x % 4 == 0:
        index_x = 1
        index_y += 1

    if (index_x == 1):
        last_x = 60
    if (index_x == 2):
        last_x = 330
    if (index_x == 3):
        last_x = 550

    if (index_y == 1):
        last_y = 230
    if (index_y == 2):
        last_y = 470
    if (index_y == 3):
        last_y = 700
    if (index_y == 4):
        last_y = 930

    index_x += 1
    return last_x, last_y


def get_image_pos():
    global last_cover_x
    global last_cover_y
    global index_cover_x
    global index_cover_y
    if index_cover_x % 4 == 0:
        index_cover_x = 1
        index_cover_y += 1
# 100, 90
    if (index_cover_x == 1):
        last_cover_x = 90
    if (index_cover_x == 2):
        last_cover_x = 350
    if (index_cover_x == 3):
        last_cover_x = 590

    if (index_cover_y == 1):
        last_cover_y = 90
    if (index_cover_y == 2):
        last_cover_y = 330
    if (index_cover_y == 3):
        last_cover_y = 560
    if (index_cover_y == 4):
        last_cover_y = 790

    index_cover_x += 1
    return last_cover_x, last_cover_y


def add_book(id):
    (x, y) = get_text_pos()

    message = books[id]['title'].encode().decode("utf-8")
    message = (message[:15] + '..') if len(message) > 15 else message
    reshaped_text = arabic_reshaper.reshape(message)    # correct its shape
    # correct its direction
    bidi_text = get_display(reshaped_text)
    color = 'rgb(0, 0, 0)'
    draw.text((x, y), bidi_text, fill=color, font=font)
    (x, y) = (150, 150)
    cover = Image.open("images/{}".format(books[id]['image']))
    image.paste(cover, get_image_pos())


index_file = 0
index_current_book = 0
for i in range(len(books)):
    add_book(i)
    index_current_book += 1
    if i % 12 == 0 and i != 0:
        index_current_book = 0
        index_file += 1
        image.paste(logo, (200, 1100), logo.convert('RGBA'))
        image.save('fidibo{}.png'.format(index_file))
        image = Image.open('shelf.png')
        draw = ImageDraw.Draw(image)
        last_x, last_y, index_x, index_y = 0, 230, 1, 1
        last_cover_x, last_cover_y, index_cover_x, index_cover_y = 0, 230, 1, 1
if index_current_book is not 0:
    index_file += 1
    image.paste(logo, (200, 1100), logo.convert('RGBA'))
    image.save('fidibo{}.png'.format(index_file))
