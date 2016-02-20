#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, MrStealth

import os, sys, re, urllib, urllib2, json
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
            self.genres()
        if mode == 'movie':
            self.movie(url)
        if mode == 'show':
            self.movie(url)
        if mode == 'movies':
            self.movies(url, page)
        elif mode is None:
            self.menu()

    def menu(self):
        uri = sys.argv[0] + '?mode=%s&url=%s' % ("search", self.url)
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % self.language(2000), thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s' % ("genres")
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Жанры', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/movies_z/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Фильмы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/movies_n/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Фильмы отечественные', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/serials_z/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % "Сериалы", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/serials_n/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % "Сериалы отечественные", thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("movies", 'http://vio24.com/cartoons/')
        item = xbmcgui.ListItem("[B][COLOR=FF00FFF0]%s[/COLOR][/B]" % 'Мультфильмы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)


        self.movies(self.url, 1)
        # self.movies('http://vio24.com/serials_z/')
        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movies(self, url, page):
        page_url = "%s/page/%s/" % (url, str(int(page)))
        print page_url
        response = common.fetchPage({"link": page_url})
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

        if len(titles) == 30:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("movies", url, str(int(page) + 1))
            item = xbmcgui.ListItem(self.language(9000), thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def movie(self, url):
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={ "class": "bg-video-990"})[0]


        mark = common.parseDOM(response["content"], "p", attrs={ "class": "btl4"})

        title = common.parseDOM(mark, "i")[0]
        title= title.replace(': ', '-').replace(' ', '.')

        video = re.search('"file":"(.*?)"', container)
        pl = re.search('"pl":"(.*?)"', container)

        print pl
        if video:
            link = Uppod.DecodeUppodTextHash(video.group(1))
            print "Encoded link: %s" % link

            if '999' in link:
                video_link = link.replace('999', '')
            elif 'm,' in link:
                url = "http://v1.vio24.com/video/m/z/%s/%s" %(title, link.split('/')[-1:])
            else:
                if 'm/z' in link:
                    video_link = "http://v1.vio24.com/video/m/z/" + "/".join(link.split('/')[-1:])
                else:
                    video_link = "http://v1.vio24.com/video/f/z/" + "/".join(link.split('/')[-1:])

            print "Fixed link: %s" % video_link

            item = xbmcgui.ListItem(title, iconImage='image', thumbnailImage='image')
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handle, video_link, item, False)
        else:
            link = Uppod.DecodeUppodTextHash(pl.group(1))
            print "Encoded link: %s" % link

            print link.find('�')


            if '999' in link:
                url = link.replace('999', '')
            elif 's,' in link:
                url = "http://v1.vio24.com/video/s/z/%s/%s" %(title, link.split('/')[-1])
            else:
                if 'm/s' in link:
                    url = "http://v1.vio24.com/video/m/s/%s/%s" %(title, link.split('/')[-1])
                elif 's/z' in link:
                    url = "http://v1.vio24.com/video/s/z/%s/%s" %(title, link.split('/')[-1])
                elif 's/d' in link:
                    url = "http://v1.vio24.com/video/s/d/%s/%s" %(title, link.split('/')[-1])


            print "Fixed link: %s" % url

            response = common.fetchPage({"link": url})["content"].decode("utf-8-sig").encode("utf-8")
            playlist = json.loads(response)['playlist']
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


    def search(self, keyword, unified):
        if self.translit == 'false':
            self.info('Translit module is disabled in the settings')

        if not unified:
            keyword = common.getUserInput()

        keyword = translit.rus(keyword)

        unified_search_results = []

        if keyword:
            url = "http://vio24.com/index.php?do=search&subaction=search&all_word_seach=1&titleonly=3&story=%s&x=0&y=0" % urllib.quote(keyword)

            print url
            container = common.fetchPage({"link": url})['content']
            headers = common.parseDOM(container, "b")
            movies = common.parseDOM(container, "a", attrs={"class": "tip_trigger"})
            links = common.parseDOM(headers, "a", ret="href")
            titles = common.parseDOM(headers, "a")
            images = common.parseDOM(container, "img", attrs={"width": "120"}, ret="src")

            self.info("По запросу [B]'%s'[/B] найдено %d ответов" % (self.encode(keyword), len(links)))


            if unified:
                self.log("Perform unified search and return results")

                for i, title in enumerate(titles):
                    image = images[i] if 'http' in images[i] else self.url+images[i]
                    unified_search_results.append({'title':  self.encode(self.strip(title)), 'url': links[i], 'image': image, 'plugin': self.id})

                UnifiedSearch().collect(unified_search_results)

            else:
                for i, title in enumerate(titles):
                    uri = sys.argv[0] + '?mode=movie&url=%s' % links[i]
                    image = images[i] if 'http' in images[i] else self.url+images[i]
                    item = xbmcgui.ListItem(self.encode(self.strip(title)), thumbnailImage=image)
                    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

                xbmc.executebuiltin('Container.SetViewMode(50)')
                xbmcplugin.endOfDirectory(self.handle, True)

        else:
            self.menu()


    def genres(self):
        titles = [
            "Биография",
            "Боевик",
            "Вестерн",
            "Военный",
            "Детектив",
            "Документальный",
            "Драма",
            "История",
            "Комедия",
            "Криминал",
            "Мелодрама",
            "Музыка",
            "Приключения",
            "Семейный",
            "Спорт",
            "Триллер",
            "Ужасы",
            "Фантастика",
            "Фэнтези"
        ]

        links = [
            "http://vio24.com/biography/",
            "http://vio24.com/action/",
            "http://vio24.com/western/",
            "http://vio24.com/military/",
            "http://vio24.com/detective/",
            "http://vio24.com/documentary/",
            "http://vio24.com/drama/",
            "http://vio24.com/history/",
            "http://vio24.com/comedy/",
            "http://vio24.com/crime/",
            "http://vio24.com/romance/",
            "http://vio24.com/musical/",
            "http://vio24.com/adventures/",
            "http://vio24.com/family/",
            "http://vio24.com/sport/",
            "http://vio24.com/thriller/",
            "http://vio24.com/horror-mystic/",
            "http://vio24.com/fantastic/",
            "http://vio24.com/fantasy/"
        ]


        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=movies&url=%s' % urllib.quote(links[i])
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
