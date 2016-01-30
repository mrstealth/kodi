#!/usr/bin/python
# Writer (c) 2016, MrStealth
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import KodiUtils
common = KodiUtils

class Example():
    def __init__(self):
        self.id = 'plugin.video.example.addon'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')
        self.language = self.addon.getLocalizedString

        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://www.sample-videos.com/'

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
        if mode == 'video':
            self.video(url)
        if mode == 'videos':
            self.videos(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[COLOR=FF00FF00]%s[/COLOR]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.videos(self.url, 1)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def videos(self, url, page):
        # page_url = "%s/page/%s/" % (url, str(int(page)))

        page_url = url
        response = common.fetchPage({"link": page_url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"class": "container"})

            items = common.parseDOM(content, "div", attrs={"id": "sample-mp4-video"})
            titles = common.parseDOM(items, "a", ret="download")
            links = common.parseDOM(items, "a", ret="href")

            print titles

            for i, title in enumerate(titles):
                uri = sys.argv[0] + '?mode=video&url=%s' % (links[i])
                item = xbmcgui.ListItem(title, iconImage=self.icon, thumbnailImage=self.icon)
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': 'genre', 'plot': 'description'})
                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if len(titles) == 10:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("videos", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(1000), thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def video(self, url):
        title = "Title"
        link = self.url + url
        image = self.icon

        item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)

        item.setInfo(type='Video', infoLabels = { 'genre': 'genre', 'plot': 'description' })
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, link, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def genres(self):
        print "Get genres"
        uri = sys.argv[0] + '?mode=genres&url=%s' % self.link
        item = xbmcgui.ListItem('Genre', iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, False)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def play(self, url):
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def search(self, keyword, unified):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(1000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            keyword = kbd.getText()

        self.info(keyword)

    # *** Add-on helpers
    def log(self, message):
        if self.debug:
            print "### %s: %s" % (self.id, message)

    def info(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("INFO", msg, str(10 * 1000)))

    def error(self, msg):
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", msg, str(10 * 1000)))


Example().main()
