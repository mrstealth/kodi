#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, MrStealth

import os
import urllib
import urllib2
import sys
import re

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import KodiUtils
common = KodiUtils

import Moonwalk
import Kodik

import Translit as translit
translit = translit.Translit(encoding='cp1251')

# import socket
# socket.setdefaulttimeout(120)


# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except:
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Warning", 'Please install UnifiedSearch add-on!', str(10 * 1000)))


class OnlainWs():
    def __init__(self):
        self.id = 'plugin.video.onlain.ws'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://onlain.ws'

        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.debug = False

    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Handle: %d" % self.handle)
        self.log("Params: %s" % self.params)

        params = common.getParameters(self.params)

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.genres(url)
        if mode == 'show':
            self.movie(url)
        if mode == 'category':
            self.movies(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://onlain.ws/zhanr/serialy/")
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % self.language(1001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://onlain.ws/zhanr/multfilmy/")
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % self.language(1002), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.movies(self.url, 1)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movies(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        print page_url

        content = common.fetchPage({"link": page_url})["content"]
        movies = common.parseDOM(content, "div", attrs={"class": "shortstory"})
        headers = common.parseDOM(movies, "h2", attrs={"class": "zagolovki"})

        titles = common.parseDOM(headers, "a")
        links = common.parseDOM(headers, "a", ret="href")
        images = common.parseDOM(movies, "img", ret="src")

        ratings = common.parseDOM(movies, "div", attrs={"class": "titlePageSprite star-box-giga-star"})
        infos = common.parseDOM(movies, "noindex")

        for i, title in enumerate(titles):
            image = images[i] if 'http' in images[i] else self.url+images[i]

            uri = sys.argv[0] + '?mode=show&url=%s' % (links[i])
            item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if not len(titles) < 10:
            print page
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9000), thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movie(self, url):
        print "*** movie for url %s " % url


        response = common.fetchPage({"link": url})
        iframes = common.parseDOM(response["content"], "iframe", ret="src")

        try:
            shortstorytitle = common.parseDOM(response["content"], "div", attrs={ "class": "shortstorytitle" })
            container = common.parseDOM(response["content"], "div", attrs={ "class": "ratingimdb" })
            kpid = common.parseDOM(container, "a", ret="href")[0].split('/')[-1].replace('.png', '')
            title = self.strip(common.parseDOM(shortstorytitle, "h1")[0])
            image = common.parseDOM(response["content"], "img", attrs={ "width": "200" }, ret="src")[0]
            image = image if 'http' in image else self.url+image

            iframe = iframes[0]

            if not 'http' in iframe:
                self.error('Unknown video source')
                return


            if 'serial' in iframe:
                seasons = Moonwalk.seasons(iframe)
                for season in seasons:
                    for episode in season['episodes']:
                        title = "%s (%s)" % (episode['title'], season['title'])
                        uri = sys.argv[0] + '?mode=playMoonwalkItem&url=%s' % urllib.quote_plus(episode['link'])
                        item = xbmcgui.ListItem(title,  iconImage=image, thumbnailImage=image)

                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item)

            else:
                moonwalk_stream = Moonwalk.movies(iframe)['manifest_m3u8']
                mtitle = '%s - %s' % (title, 'Moonwalk')
                item = xbmcgui.ListItem(title,  iconImage=image, thumbnailImage=image)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, moonwalk_stream, item)

                quality = ['720p', '480p', '360p']
                kodik_streams = Kodik.streams(kpid)

                for i, link in enumerate(kodik_streams):
                    mtitle = '%s - %s [%s]' % (title, 'Kodic', quality[i])
                    item = xbmcgui.ListItem(mtitle, iconImage=image, thumbnailImage=image)
                    xbmcplugin.addDirectoryItem(self.handle, link, item)

        except IndexError as e:
            link = re.search('"file":"(.*?)","', response["content"]).group(1)
            item = xbmcgui.ListItem('Трейлер',  iconImage=image, thumbnailImage=image)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, link, item)


        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def genres(self, url):
        print "list genres"
        response = common.fetchPage({"link": url})
        menu = common.parseDOM(response["content"], "div", attrs={"class": "mini"})[0]
        titles = common.parseDOM(menu, "a")
        links = common.parseDOM(menu, "a", ret="href")


        for i, link in enumerate(links):
            title = titles[i]
            link = self.url + '/zhanr' + links[i][:-1]

            uri = sys.argv[0] + '?mode=category&url=%s' % link
            item = xbmcgui.ListItem(title, iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
        print "*** play url %s" % url
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def playMoonwalkItem(self, url):
        link = Moonwalk.streams(url)['manifest_m3u8']
        self.play(link)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword

    def search(self, keyword, unified):
        self.error('Not yet implemented')

    # *** Add-on helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def error(self, msg):
        print "%s ERROR: %s" % (self.id, msg)
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))

    def strip(self, string):
        return common.stripTags(string)

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')


# class URLParser():
#     def parse(self, string):
#         links = re.findall(r'(?:http://|www.).*?["]', string)
#         return list(set(self.filter(links)))

#     def filter(self, links):
#         links = self.strip(links)
#         return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

#     def strip(self, links):
#         return [l.replace('"', '') for l in links]

OnlainWs = OnlainWs()
OnlainWs.main()
