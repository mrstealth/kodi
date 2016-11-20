#!/usr/bin/python
# Writer (c) 2014-2015, MrStealth
# -*- coding: utf-8 -*-

import os
import urllib
import urllib2
import sys
import re
import socket
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import KodiUtils
common = KodiUtils


import Translit as translit
translit = translit.Translit(encoding='cp1251')

socket.setdefaulttimeout(120)


# UnifiedSearch module
try:
    sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
    from unified_search import UnifiedSearch
except:
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)" % ("Warning", 'Please install UnifiedSearch add-on!', str(10 * 1000)))


class Kinokong():
    def __init__(self):
        self.id = 'plugin.video.kinokong.net'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = self.addon.getAddonInfo('path')
        self.profile = self.addon.getAddonInfo('profile')

        self.language = self.addon.getLocalizedString
        self.translit = self.addon.getSetting('translit')
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]

        self.url = 'http://kinokong.net'

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
            self.listGenres(url)
        if mode == 'show':
            self.getFilmInfo(url)
        if mode == 'category':
            self.getCategoryItems(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("genres", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % self.language(1000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.getCategoryItems('http://kinokong.net/films/novinki', 1)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getCategoryItems(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        response = common.fetchPage({"link": page_url})

        if response["status"] == 200:
            content = common.parseDOM(response["content"], "div", attrs={"id": "container"})
            items = common.parseDOM(content, "div", attrs={"class": "owl-item"})

            link_container = common.parseDOM(items, "div", attrs={"class": "main-sliders-title"})
            images_container = common.parseDOM(items, "div", attrs={"class": "main-sliders-img"})
            titles = common.parseDOM(link_container, "a")
            links = common.parseDOM(link_container, "a", ret="href")
            images = common.parseDOM(images_container, "img", ret="src")

            descs = common.parseDOM(items, "i")
            pagenav = common.parseDOM(content, "div", attrs={"class": "navigation"})

            for i, title in enumerate(titles):
                title = self.strip(self.encode(title))
                image = self.url + common.parseDOM(items[i], "img", ret="src")[2]

                genres_cont = common.parseDOM(items[i], "em")
                genres = common.parseDOM(genres_cont, "a")
                genre = self.encode(', '.join(genres))
                description = self.encode(descs[i])

                uri = sys.argv[0] + '?mode=show&url=%s' % (links[i])
                item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
                item.setInfo(type='Video', infoLabels={'title': title, 'genre': genre, 'plot': description})

                xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if pagenav and not len(titles) < 15:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9000), thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def getFilmInfo(self, url):
        xbmc.log("*** getFilmInfo for url %s " % url)
        xbmc.log(url)

        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"id": "container"})
        js_container = common.parseDOM(response["content"], "div", attrs={"class": "section"})
        sources = common.parseDOM(js_container, "script", attrs={"type": "text/javascript"})
        source = sources[6]

        for i, script in enumerate(sources):
            if 'mp4' in script:
                xbmc.log('%d - ################################################' % i)
                xbmc.log(script)

                source = script
                break


        title = self.encode(common.parseDOM(container, "h1")[0])
        image = common.parseDOM(container, "img", attrs={"id": "imgbigp"}, ret="src")[0]
        quality = common.parseDOM(container, "div", attrs={"class": "full-quality"})

        movie = source.split('file":"')[-1].split('"};')[0] if 'file":"' in source else None
        playlist = source.split(',pl:"')[-1].split('"};')[0] if ',pl:"' in source else None
        playlist = playlist.split('",')[0] if playlist and '",' in playlist else playlist

        image = image if image.startswith( 'http' ) else self.url + image

        if not playlist:
            links = movie.replace(' or ', ',').split(',') if(',' or ' or ') in movie else [movie]
            image = image if 'http' in image else self.url+image
            quality = quality[0] if quality else ''
            resolution = ['480P', '720P']

            for i, link in enumerate(links):
                link_title = "%s [%s - %s]" % (title, resolution[i], quality)
                link_title = link_title.replace(self.language(5002).encode('utf-8'), '').replace('720 hd', '')

                uri = sys.argv[0] + '?mode=play&url=%s' % link

                item = xbmcgui.ListItem(link_title, iconImage=image, thumbnailImage=image)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, link, item, False)

            xbmc.executebuiltin('Container.SetViewMode(52)')

        else:
            response = common.fetchPage({"link": playlist})
            response = eval(response["content"])

            if 'playlist' in response['playlist'][0]:
                print "This is a season multiple seasons"

                for season in response['playlist']:
                    episods = season['playlist']

                    for episode in episods:
                        etitle =  episode['comment'].replace('<br>', ' ')
                        url = episode['file'].split(',')[-1] if '_720' in episode['file'] else episode['file'].split(',')[0]

                        item = xbmcgui.ListItem(common.stripTags(etitle), iconImage=image, thumbnailImage=image)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, url, item, False)
            else:
                print "This is one season"
                for episode in response['playlist']:
                    try:
                        etitle = episode['comment']
                    except KeyError:
                        etitle = episode['commet']

                    url = episode['file'].split(',')[-1] if '_720' in episode['file'] else episode['file'].split(',')[0]

                    item = xbmcgui.ListItem(common.stripTags(etitle), iconImage=image, thumbnailImage=image)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self.handle, url, item, False)

            xbmc.executebuiltin('Container.SetViewMode(51)')

        xbmcplugin.endOfDirectory(self.handle, True)


    def listGenres(self, url):
        response = common.fetchPage({"link": url})
        menu = common.parseDOM(response["content"], "ul", attrs={"class": "reset top-menu"})
        genres = common.parseDOM(menu, "li")

        links = [
          'http://kinokong.net/films',
          'http://kinokong.net/films/novinki',
          'http://kinokong.net/serial',
          'http://kinokong.net/multfilm',
          'http://kinokong.net/anime',
          'http://kinokong.net/dokumentalnyy'
        ]

        for i, genre in enumerate(genres[:-1]):
            title = common.parseDOM(genre, "a")[0]
            link = links[i]

            uri = sys.argv[0] + '?mode=category&url=%s' % links[i]
            item = xbmcgui.ListItem(self.encode(title), iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)

    def getPlaylist(self, url):
        print "getPlaylist"

    def playItem(self, url):
        print "*** play url %s" % url
        if ' or ' in url:
            link = url.split(' or ')[-1]
        else:
            link = url
        item = xbmcgui.ListItem(path=link)
        xbmcplugin.setResolvedUrl(self.handle, True, item)

    def getUserInput(self):
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(self.language(4000))
        kbd.doModal()
        keyword = None

        if kbd.isConfirmed():
            if self.translit == 'true':
                keyword = translit.rus(kbd.getText())
            else:
                keyword = kbd.getText()

        return keyword


    def search(self, keyword, unified):
        if self.translit == 'false':
            self.info('Translit module is disabled in the settings')

        keyword = translit.rus(keyword) if unified else self.getUserInput()
        unified_search_results = []

        if keyword:
            url = 'http://kinokong.net/index.php?do=search'

            # Advanced search: titles only
            values = {
                "beforeafter":  "after",
                "catlist[]":    0,
                "do" :          "search",
                "full_search":  1,
                "replyless":    0,
                "replylimit":   0,
                "resorder":     "desc",
                "result_from":  1,
                "search_start": 1,
                "searchdate" :  0,
                "searchuser":   "",
                "showposts":    0,
                "sortby":       "date",
                "story" :       keyword,
                "subaction":    "search",
                "titleonly":    0
            }

            headers = {
                "Host" : "kinokong.net",
                "Referer" : 'http://kinokong.net/index.php?do=search',
                "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:35.0) Gecko/20100101 Firefox/35.0"
            }

            # Send request to server
            request = urllib2.Request(url, urllib.urlencode(values), headers)
            response = urllib2.urlopen(request).read()

            content = common.parseDOM(response, "div", attrs={"id": "container"})
            items = common.parseDOM(content, "div", attrs={"class": "item"})

            link_container = common.parseDOM(items, "div", attrs={"class": "main-sliders-title"})
            titles = common.parseDOM(link_container, "a")
            links = common.parseDOM(link_container, "a", ret="href")
            images = common.parseDOM(items, "img", ret="src")

            descs = common.parseDOM(items, "i")

            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    image = images[i] if 'http' in images[i] else self.url+images[i]
                    unified_search_results.append({'title':  self.encode(self.strip(title)), 'url': links[i], 'image': image, 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    uri = sys.argv[0] + '?mode=show&url=%s' % links[i]
                    image = images[i] if 'http' in images[i] else self.url+images[i]
                    item = xbmcgui.ListItem(self.encode(self.strip(title)), thumbnailImage=image)
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


# class URLParser():
#     def parse(self, string):
#         links = re.findall(r'(?:http://|www.).*?["]', string)
#         return list(set(self.filter(links)))

#     def filter(self, links):
#         links = self.strip(links)
#         return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

#     def strip(self, links):
#         return [l.replace('"', '') for l in links]

Kinokong = Kinokong()
Kinokong.main()
