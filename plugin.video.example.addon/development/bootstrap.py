#!/usr/bin/python
# Writer (c) 2016, MrStealth
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys

import XbmcHelpers
common = XbmcHelpers


def videos(url):
    response = common.fetchPage({"link": url})["content"]
    items = common.parseDOM(response, "div", attrs={"id": "sample-mp4-video"})
    titles = common.parseDOM(items, "a", ret="download")
    links = common.parseDOM(items, "a", ret="href")

    print titles

def video(url):
    response = common.fetchPage({"link": page_url})

    content = common.parseDOM(response["content"], "div", attrs={"class": "container"})
    items = common.parseDOM(content, "div", attrs={"id": "sample-mp4-video"})
    titles = common.parseDOM(items, "a", ret="dowload")
    links = common.parseDOM(items, "a", ret="href")

videos('http://www.sample-videos.com/')
