#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, MrStealth

import os, sys, re, urllib, json
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import Uppod

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


class Plugin():
    def __init__(self):
        self.id = 'plugin.video.vio24.com'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.translit = self.addon.getSetting('translit')
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://vio24.com'

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
        if mode == 'movies':
            self.movies(url)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/movies_z/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Фильмы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/serials_z/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1001), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/cartoons/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Мультфильмы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        self.movies(self.url)
        # self.movies('http://vio24.com/serials_z/')
        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movies(self, url):
        response = common.fetchPage({"link": url})
        container = response["content"]

        headers = common.parseDOM(container, "b")
        movies = common.parseDOM(container, "a", attrs={"class": "tip_trigger"})
        links = common.parseDOM(headers, "a", ret="href")
        titles = common.parseDOM(headers, "a")
        images = common.parseDOM(movies, "img", ret="src")

        print len(titles)
        print len(links)
        print len(images)

        for i, link in enumerate(links):
            title = titles[i].decode('cp1251')
            uri = sys.argv[0] + '?mode=movie&url=%s' % (link)
            item = xbmcgui.ListItem(title, iconImage=self.url+images[i], thumbnailImage=self.url+images[i])
            item.setInfo(type='Video', infoLabels={'title': titles[i], 'genre': 'genre', 'plot': 'description'})
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def movie(self, url):
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={ "class": "bg-video-990"})[0]


        mark = common.parseDOM(response["content"], "p", attrs={ "class": "btl4"})
        title = common.parseDOM(mark, "i")[0].replace(' ', '.')

        video = re.search('"file":"(.*?)"', container)
        pl = re.search('"pl":"(.*?)"', container)

        print pl
        if video:
            link = Uppod.DecodeUppodTextHash(video.group(1))
            video_link = "http://v1.vio24.com/video/f/z/" + "/".join(link.split('/')[-1:])

            print link

            print "Fixed link: %s" % video_link


            item = xbmcgui.ListItem(title, iconImage='image', thumbnailImage='image')
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, video_link, item, False)
        else:
            link = Uppod.DecodeUppodTextHash(pl.group(1))
            url = "http://v1.vio24.com/video/s/z/%s/%s" %(title, link.split('/')[-1])
            print link

            print "Fixed link: %s" % url

            response = common.fetchPage({"link": url})["content"]
            response = response.strip('" ').replace('“', '"').replace('”', '')
            response = response.replace('\\x', '').replace('\r\n', '')
            response = response.replace('\r', '').replace('\n', '')
            response = response.replace('\r\n', '')
            response = response.replace('\r', '').replace('\t', '').replace('\r\n', '')

            print response
            playlist = eval(response)['playlist']


            print playlist
            for episode in playlist:
                title =  episode['comment']
                link = episode['file']

                item = xbmcgui.ListItem(title, iconImage='image', thumbnailImage='image')
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, link, item, False)

            xbmc.executebuiltin('Container.SetViewMode(51)')
            xbmcplugin.endOfDirectory(self.handle, True)


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


Plugin().main()
