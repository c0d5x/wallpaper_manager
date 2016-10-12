#!/usr/bin/env python
''' Parse and download wallpapers from socwall.com '''

import requests
import random
import shutil
from lxml import html

SOCWALL_DOMAIN = "http://www.socwall.com/"
SOCWALL_MAX = 702
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


def download_img(img_name):
    image_id = img_name.split('/')[2]
    img_url = SOCWALL_DOMAIN + "/desktop-wallpaper/{}/wallpaper/".format(image_id)
    page = requests.get(img_url, headers=HEADERS)
    doctree = html.fromstring(page.content)
    imagepath = doctree.xpath("//a[@class='download']")[0].attrib['href']
    image = requests.get(SOCWALL_DOMAIN + imagepath, headers=HEADERS, stream=True)
    with open(image_id + ".jpg", 'wb+') as outf:
        shutil.copyfileobj(image.raw, outf)
    del image


def main():
    pagen = random.randint(1, SOCWALL_MAX)
    URL = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(pagen)
    print(URL)
    source = requests.get(URL, headers=HEADERS)
    doctree = html.fromstring(source.content)
    images = doctree.xpath("//a[@class='image']")
    for aref in images:
        print(aref.attrib['href'])
        download_img(aref.attrib['href'])


if __name__ == "__main__":
    main()
