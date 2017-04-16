#!/usr/bin/env python3
''' Parse and download wallpapers from socwall.com '''

import os
import shutil
import random
from concurrent import futures
import requests
from lxml import html

SOCWALL_VERBOSE = True
SOCWALL_DOMAIN = "http://www.socwall.com/"
SOCWALL_MAX = 702
SOCWALL_EXECUTORS = 100
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


# TODO: implement class

def download_img(img_name, path):
    ''' Download one specific image '''
    image_id = img_name.split('/')[2]
    img_url = SOCWALL_DOMAIN + "/desktop-wallpaper/{}/wallpaper/".format(image_id)
    page = requests.get(img_url, headers=HEADERS)
    doctree = html.fromstring(page.content)
    imagepath = doctree.xpath("//a[@class='download']")[0].attrib['href']
    if SOCWALL_VERBOSE:
        print("Downloading %s" % (SOCWALL_DOMAIN + imagepath))
    image = requests.get(SOCWALL_DOMAIN + imagepath, headers=HEADERS, stream=True)
    new_image_path = path + "/socwall-" + image_id + ".jpg"
    with open(new_image_path, 'wb+') as outf:
        shutil.copyfileobj(image.raw, outf)
    del image
    return new_image_path


def dl_one(path):
    ''' Get one image '''
    num = random.randint(1, SOCWALL_MAX)
    url = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(num)
    source = requests.get(url, headers=HEADERS)
    doctree = html.fromstring(source.content)
    images = doctree.xpath("//a[@class='image']")
    aref = random.choice(images)
    return download_img(aref.attrib['href'], path)


def dl_page(num, path):
    ''' Download one page of imgs '''
    url = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(num)
    # print(URL)
    source = requests.get(url, headers=HEADERS)
    doctree = html.fromstring(source.content)
    images = doctree.xpath("//a[@class='image']")

    counter = 0

    with futures.ThreadPoolExecutor(SOCWALL_EXECUTORS) as executor:
        for aref in images:
            # print(aref.attrib['href'])
            executor.submit(download_img, aref.attrib['href'], path)
            counter += 1
    return counter


def dl_random_page(path):
    """ Download all images of a page at random """
    pagen = random.randint(1, SOCWALL_MAX)
    page_numbers = []

    # load page numbers that have been downloaded
    with open(path + "/.page_numbers", "r") as logf:
        # page_numbers = map(lambda s: s.strip(), logf.readlines())
        page_numbers = [s.strip() for s in logf.readlines()]

    # check if we have exausted half of the library
    if len(page_numbers) > (SOCWALL_MAX * 0.9):
        os.remove(path + "/.page_numbers")  # start over
        page_numbers = []

    while pagen in page_numbers:
        pagen = random.randint(1, SOCWALL_MAX)

    num_images = dl_page(pagen, path)

    with open(path + "/.page_numbers", "a+") as logf:
        logf.write(str(pagen) + "\n")

    return num_images


# if __name__ == "__main__":
#    dl_random_page()
