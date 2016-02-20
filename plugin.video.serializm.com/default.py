#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2014-2015, MrStealth

import os, sys, re, urllib, json
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import KodiUtils
common = KodiUtils


import Translit as translit
translit = translit.Translit(encoding='cp1251')


# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except:
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Warning", 'Please install UnifiedSearch add-on!', str(10 * 1000)))


class Serializm():
    def __init__(self):
        self.id = 'plugin.video.serializm.com'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.translit = self.addon.getSetting('translit')
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://serializm.com'

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
            self.playItem(url)
        if mode == 'search':
            self.search(keyword, unified)
        if mode == 'genres':
            self.genres(url)
        if mode == 'movie':
            self.movie(url)
        if mode == 'show':
            self.movie(url)
        if mode == 'movies':
            self.movies(url)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://serializm.com/new/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % "Новинки", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.movies(self.url)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movies(self, url):
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"class": "wrap"})

        items = common.parseDOM(container, "a", attrs={"class": "serial-item"})
        links = common.parseDOM(container, "a", attrs={"class": "serial-item"}, ret="href")
        titles = common.parseDOM(items, "span", attrs={"class": "title"})
        images = common.parseDOM(items, "img", ret="src")

        print len(titles)
        print len(links)
        print len(images)

        for i, link in enumerate(links):
            uri = sys.argv[0] + '?mode=movie&url=%s' % (self.url + link)
            item = xbmcgui.ListItem(titles[i], iconImage=self.url+images[i], thumbnailImage=self.url+images[i])
            item.setInfo(type='Video', infoLabels={'title': titles[i], 'genre': 'genre', 'plot': 'description'})
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def movie(self, url):
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"class": "content"})
        pl = re.search('"pl":"(.*?)"};', response["content"]).group(1).replace("'", '"')

        playlist = json.loads(pl)['playlist']

        for episode in playlist:
            title =  episode['comment'].replace('<br>', ' ')
            link = episode['file']

            item = xbmcgui.ListItem(title, iconImage='image', thumbnailImage='image')
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, link, item, False)

        xbmc.executebuiltin('Container.SetViewMode(51)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def genres(self, url):
        response = common.fetchPage({"link": url})

        container = common.parseDOM(response["content"], "div", attrs={"class": "wrap"})
        menu = common.parseDOM(container, "ul")[0]
        titles = common.parseDOM(menu, "a")
        links = common.parseDOM(menu, "a", ret="href")

        for i, title in enumerate(titles[:-1]):
            link = self.url + links[i]
            print link

            uri = sys.argv[0] + '?mode=movies&url=%s' % urllib.quote(link)
            item = xbmcgui.ListItem(title, iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def search(self, keyword, unified):
        if self.translit == 'false':
            self.info('Translit module is disabled in the settings')

        if not unified:
            keyword = common.getUserInput()

        if self.translit != 'false':
            keyword = translit.rus(keyword)

        unified_search_results = []

        if keyword:
            url = "http://serializm.com/search?searchtext=%s&submit=submit" % urllib.quote(self.encode(keyword))

            response = common.fetchPage({"link": url})
            container = common.parseDOM(response["content"], "div", attrs={"class": "wrap"})

            items = common.parseDOM(container, "a", attrs={"class": "serial-item"})
            links = common.parseDOM(container, "a", attrs={"class": "serial-item"}, ret="href")
            titles = common.parseDOM(items, "span", attrs={"class": "title"})
            images = common.parseDOM(items, "img", ret="src")

            self.info("По запросу [B]'%s'[/B] найдено %d ответов" % (self.encode(keyword), len(links)))


            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    link = links[i] if 'http' in links[i] else self.url+links[i]
                    image = images[i] if 'http' in images[i] else self.url+images[i]
                    unified_search_results.append({'title':  title, 'url': link, 'image': image, 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    link = links[i] if 'http' in links[i] else self.url+links[i]
                    image = images[i] if 'http' in images[i] else self.url+images[i]

                    uri = sys.argv[0] + '?mode=movie&url=%s' % links[i]
                    item = xbmcgui.ListItem(title, thumbnailImage=image)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()


    # *** Add-on helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def info(self, message):
        print "%s INFO: %s" % (self.id, message)
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("INFO", message, str(10 * 1000)))

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", message, str(10 * 1000)))

    def strip(self, string):
        return common.stripTags(string)

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')


Serializm().main()
