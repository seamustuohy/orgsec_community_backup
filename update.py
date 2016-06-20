#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of orgsec community backup, a backup of orgsec.community.
# Copyright © 2016 seamus tuohy, <code@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

import argparse
import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

from bs4 import BeautifulSoup

import requests
#from os import path, mkdir
import re
import os
from getpass import getpass
from datetime import datetime

def get_page_source(session, page_url):
    page = session.get(page_url)
    html_text = page.text
    html_obj = BeautifulSoup(html_text, 'lxml')
    base_url = "https://orgsec.community"
    pagesrc_path = html_obj.find("a", {'id':'action-view-source-link'})['href']
    pagesrc_url = "{0}{1}".format(base_url, pagesrc_path)
    # Get page source
    src_page = session.get(pagesrc_url)
    html_text = src_page.text
    html_obj = BeautifulSoup(html_text, 'lxml')
    return html_obj.find('body')


def login():
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
    username = getpass("Please enter your username: ")
    password = getpass("Please enter your password: ")
    payload = {"os_username":username,
               "os_password":password,
               "login":"Log in"}
    session = requests.Session()
    session.post('https://orgsec.community/dologin.action', data=payload, headers=headers, allow_redirects=True, verify=False)
    return session

def main():
    dir_path = "_posts"
    session = login()
    #print(type(session))
    pages = get_all_pages(session)
    for page in pages:
        url = page[0]
        title = page[1]
        src = get_page_source(session, url)
        write_page(dir_path, title, src)

def write_page(dir_path, title, src):
    todays_date = datetime.today().strftime("%Y-%m-%d")
    header_text = """---
layout: post
title: {0}
date: {1}
---

""".format(title, todays_date)

    page_title = re.sub(" ", "+", title)
    file_name = os.path.join(dir_path, "{0}-{1}.md".format(todays_date, page_title))
    with open(file_name, "w+") as cur_page:
        cur_page.write(header_text)
        cur_page.write(str(src))

def get_all_pages(s):
    more_pages = True
    content_urls = []
    base_url = None
    all_pages = "https://orgsec.community/pages/listpages-alphaview.action?key=OS&startsWith="
    while more_pages is True:
        loaded_page = s.get(all_pages)
        html_text = loaded_page.text
        html_obj = BeautifulSoup(html_text, 'lxml')
        if base_url is None:
            base_url = html_obj.find("meta", {'id':'confluence-base-url'})['content']
        # Get pages content
        new_pages = get_pages(html_obj, base_url)
        content_urls += new_pages
        try:
            next_url = html_obj.find("li", "aui-nav-next").find('a')['href']
            all_pages = "{0}/pages/{1}".format(base_url, next_url)
        except KeyError:
            more_pages = False
    return content_urls

def get_pages(html_obj, base_url):
    content_urls = []
    # Get links to all pages
    for item in (x.findChildren('a', {'href':re.compile('OS')}) for x in html_obj.findAll('td')):
        if item != []:
            page_url = "{0}{1}".format(base_url, item[0]['href'])
            content_urls.append((page_url, item[0].text))
    return content_urls

def set_logging(verbose=False, debug=False):
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose == True:
        log.setLevel("INFO")

def parse_arguments():
    parser = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    parser.add_argument("--backup", "-b",
                        help="Backup all netmundial data",
                        action='store_true')
    args = parser.parse_args()
    #print(args)
    return args

if __name__ == '__main__':
    print("starting")
    main()
