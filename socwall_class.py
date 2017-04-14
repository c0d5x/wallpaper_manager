#!/usr/bin/env python3
''' Parse and download wallpapers from socwall.com '''

import glob
import shutil
import random
from concurrent import futures
import requests
from lxml import html


class SocWall(object):

    """
    Downloader for social wallpaper
    """

    SocWall_verbose = True
    SocWall_Domain = "http://www.socwall.com/"
    SocWall_max_page = 702
    SocWall_Executors = 100
    Headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    }


    def __init__(self):
        """TODO: to be defined1. """

    def dl_one_image(self):
        """ Get one image """
        rnd_num = random.randint(1, SOCWALL_MAX)
        url     = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(rnd_num)
        source  = requests.get(url, headers=HEADERS)

        while source.status_code == 404:
            print("Downloading a new image")
            rnd_num = random.randint(1, SOCWALL_MAX)
            url     = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(rnd_num)
            source  = requests.get(url, headers=HEADERS)

        doctree = html.fromstring(source.content)
        images  = doctree.xpath("//a[@class='image']")
        aref    = random.choice(images)
        download_img(aref.attrib['href'], path)


    def dl_page(self, page_num):


    def dl_random_page(self):


    def download_img(self, img_name, path):
        """ Download one specific image """
        image_id  = img_name.split('/')[2]
        img_url   = SOCWALL_DOMAIN + "/desktop-wallpaper/{}/wallpaper/".format(image_id)
        page      = requests.get(img_url, headers=HEADERS)

        if page.status_code == 404:
            print("Error: Page not found!")
            return

        doctree   = html.fromstring(page.content)
        imagepath = doctree.xpath("//a[@class='download']")[0].attrib['href']

        if SOCWALL_VERBOSE:
            print("Downloading %s" % (SOCWALL_DOMAIN + imagepath))
        image     = requests.get(SOCWALL_DOMAIN + imagepath, headers=HEADERS, stream=True)

        if image.status_code == 404:
            print("Error: Image not found!")
            return

        with open(path + "/socwall-" + image_id + ".jpg", 'wb+') as outf:
            shutil.copyfileobj(image.raw, outf)
        del image



def dl_page(num, path):
    ''' Download one page of imgs '''
    url = SOCWALL_DOMAIN + "wallpapers/page:{}/".format(num)
    # print(URL)
    source = requests.get(url, headers=HEADERS)
    doctree = html.fromstring(source.content)
    images = doctree.xpath("//a[@class='image']")

    with futures.ThreadPoolExecutor(SOCWALL_EXECUTORS) as executor:
        for aref in images:
            # print(aref.attrib['href'])
            executor.submit(download_img, aref.attrib['href'], path)


def dl_random_page(path):
    """ Download all images of a page at random """
    pagen = random.randint(1, SOCWALL_MAX)
    page_numbers = []
    with open(path+"/.page_numbers","r") as logf:
        page_numbers = map(lambda s: s.strip(), logf.readlines())

    for p in page_numbers:
        print(p)

    while pagen in page_numbers:
        pagen = random.randint(1, SOCWALL_MAX)

    dl_page(pagen, path)

    with open(path + "/.page_numbers", "a+") as logf:
        logf.write(str(pagen) + "\n")


# if __name__ == "__main__":
#    dl_random_page()
