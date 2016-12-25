#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2014, MrStealth

import os, urllib, urllib2, sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re

import KodiUtils
common = KodiUtils

import Translit as translit
translit = translit.Translit(encoding='cp1251')

# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except: pass

class VideoKub():
    def __init__(self):
        self.id = 'plugin.video.videokub.me'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.translit = self.addon.getSetting('translit')
        self.inext = os.path.join(self.path, 'resources/icons/next.png')
        self.handle = int(sys.argv[1])
        self.url = 'http://videokub.net/'

    def main(self):
        params = common.getParameters(sys.argv[2])
        mode = url = page = None

        mode = params['mode'] if 'mode' in params else None
        url = urllib.unquote_plus(params['url']) if 'url' in params else None
        page = params['page'] if 'page' in params else 1

        keyword = params['keyword'] if 'keyword' in params else None
        unified = params['unified'] if 'unified' in params else None

        if mode == 'play':
            self.play(url)
        if mode == 'show':
            self.show(url)
        if mode == 'index':
            self.index(url, page)
        if mode == 'genres':
            self.genres()
        if mode == 'search':
            self.search(keyword, unified)
        elif mode == None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(1000), iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1003), iconImage=self.icon, thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.index('http://videokub.net/latest-updates/', 1)
        xbmcplugin.endOfDirectory(self.handle, True)

    def genres(self):

        url = 'http://videokub.net/categories/'
        response = common.fetchPage({"link": url})
        block_content = common.parseDOM(response["content"], "div", attrs={"class": "block_content"})

        titles = common.parseDOM(block_content, "a", attrs={"class": "hl"})
        links = common.parseDOM(block_content, "a", attrs={"class": "hl"}, ret='href')
        images = common.parseDOM(block_content, "img", attrs={"class": "thumb"}, ret='src')

        for i, title in enumerate(titles):
            if 'http' in links[i]:
                link = links[i]
            else:
                link = self.url + links[i]

            uri = sys.argv[0] + '?mode=%s&url=%s' % ("index", link)
            item = xbmcgui.ListItem(title, iconImage=images[i], thumbnailImage=images[i])
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        xbmcplugin.endOfDirectory(self.handle, True)


    def index(self, url, page):
        page_url = "%s%s/" % (url, page)

        print "Get videos for page_url %s" % page_url
        response = common.fetchPage({"link": page_url})
        content = common.parseDOM(response["content"], "div", attrs={"class": "list_videos"})
        videos = common.parseDOM(content, "div", attrs={"class": "short"})

        links = common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='href')
        titles = common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='title')
        images = common.parseDOM(videos, "img", attrs={"class": "thumb"}, ret='src')

        durations = common.parseDOM(videos, "span", attrs={"class": "time"})

        for i, title in enumerate(titles):
            duration = durations[i].split(':')[0]

            uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
            item = xbmcgui.ListItem("%s [COLOR=55FFFFFF](%s)[/COLOR]" % (title, durations[i]), iconImage=images[i], thumbnailImage=images[i])
            item.setInfo(type='Video', infoLabels={'title': title, 'genre': durations[i], 'duration': duration})
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("index", url, str(int(page) + 1))
        item = xbmcgui.ListItem(self.language(1004), iconImage=self.inext)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def show(self, url):
        print "Get video %s" % url
        response = common.fetchPage({"link": url})
        content = response["content"]
        scripts = common.parseDOM(response["content"], "script", attrs={"class": "splayer"})
        title = common.parseDOM(response["content"], "div", attrs={"class": "title"})[0]
        urls = []

        for script in scripts:
            if 'mp4' in script:
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.mp4', script)



        if urls:
            link = urls[-1]
        else:
            response = common.fetchPage({"link": url})
            iframes = common.parseDOM(response["content"], "iframe", ret="src")
            iframe = iframes[0].replace('//', 'http://')
            response = common.fetchPage({"link": iframe})
            hifile = common.parseDOM(response["content"], "hifile")[0]
            link = 'http://media.ntv.ru/vod' + hifile.replace('<![CDATA[', '').replace(']]>', '')

        xbmc.log("link %s" % link)

        item = xbmcgui.ListItem(title, thumbnailImage=self.icon, iconImage=self.icon)
        item.setInfo(type='Video', infoLabels={'title': title, 'overlay': xbmcgui.ICON_OVERLAY_WATCHED, 'playCount': 0})
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, link, item, False)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(1000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.addon.getSetting('translit') == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()
        return keyword


    def search(self, keyword, unified):
        print "*** Search: unified %s" % unified

        if self.translit == 'false':
            self.info('Translit module is disabled in the settings')


        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            keyword = self.encode(keyword)

            links = []
            titles = []
            images = []
            durations = []

            for i in range(1):
                # http://videokub.net/search/?q=Masha&search=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8
                url = 'http://videokub.net/search/%d/?q=%s&search=Найти' % (i+1, keyword)
                xbmc.log(url)

                request = urllib2.Request(url)
                request.add_header('Host', 'www.videokub.online')
                request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2872.0 Safari/537.36')
                request.add_header('Upgrade-Insecure-Requests', '1')


                response = urllib2.urlopen(request)
                content = common.parseDOM(response.read(), "div", attrs={"class": "list_videos"})
                videos = common.parseDOM(content, "div", attrs={"class": "short"})

                links += common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='href')
                titles += common.parseDOM(videos, "a", attrs={"class": "kt_imgrc"}, ret='title')
                images += common.parseDOM(videos, "img", attrs={"class": "thumb"}, ret='src')
                durations += common.parseDOM(videos, "span", attrs={"class": "time"})

            if unified:
                print "Perform unified search and return results"

                for i, title in enumerate(titles):
                    # title = self.encode(title)
                    unified_search_results.append({'title':  title, 'url': links[i], 'image': self.url + images[i], 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    duration = durations[i].split(':')[0]

                    uri = sys.argv[0] + '?mode=show&url=%s' % urllib.quote(links[i])
                    item = xbmcgui.ListItem("%s [COLOR=55FFFFFF](%s)[/COLOR]" % (title, durations[i]), iconImage=images[i])
                    item.setInfo(type='Video', infoLabels={'title': title, 'genre': durations[i], 'duration': duration})
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                # TODO: Fix search pagination
                # http://videokub.net/search/2/?q=%D0%B1%D0%B0%D1%80%D0%B1%D0%BE%D1%81%D0%BA&search=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8
                #uri = sys.argv[0] + '?mode=%s&url=%s' % ("show", url)
                #item = xbmcgui.ListItem(self.language(1004), iconImage=self.inext)
                #xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(52)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()

    def play(self, url):
        item = xbmcgui.ListItem(path = url)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def info(self, message):
        print "%s INFO: %s" % (self.id, message)
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("INFO", message, str(10 * 1000)))

    def error(self, message):
        print "%s ERROR: %s" % (self.id, message)
        xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("ERROR", message, str(10 * 1000)))

    # Python helpers
    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')

    def convert(s):
        try:
            return s.group(0).encode('latin1').decode('utf8')
        except:
            return s.group(0)

plugin = VideoKub()
plugin.main()
