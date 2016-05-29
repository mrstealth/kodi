#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, MrStealth

#http://onlain.ws/filmy-2016/page/2
#http://onlain.ws/filmy-2016/page/2/

import os
import urllib
import urllib2
import sys
import re

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import Moonwalk
import Kodik

import KodiUtils
common = KodiUtils

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
        self.playback_file = os.path.join(xbmc.translatePath('special://temp'), 'temp_video_file.mp4')

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
        if mode == 'PlayHLS':
            self.PlayHLS(url)
        if mode == 'PlayHDS':
            self.PlayHDS(url)
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
        item = xbmcgui.ListItem("[B][COLOR=FF00FF00]%s[/COLOR][/B]" % 'Поиск', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://onlain.ws/filmy-2016")
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % 'Новинки кино', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://onlain.ws/serialy")
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % 'Сериалы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        uri = sys.argv[0] + '?mode=%s&url=%s' % ("category", "http://onlain.ws/multfilmy")
        item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % 'Мультфильмы', thumbnailImage=self.icon)
        xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        self.movies(self.url, 1)
        # self.movie('http://onlain.ws/1098-lihoradka.html')

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movies(self, url, page):
        print "*** Get category items %s" % url
        page_url = "%s/page/%s/" % (url, str(int(page)))
        print page_url

        content = common.fetchPage({"link": page_url})["content"]
        container = common.parseDOM(content, "div", attrs={"id": "dle-content"})


        movies = common.parseDOM(container, "div", attrs={"class": "sh-block ns"})
        headers = common.parseDOM(movies, "h2", attrs={"class": "title-main"})
        images_container = common.parseDOM(content, "div", attrs={"class": "poster-box"})

        titles = common.parseDOM(headers, "a")
        links = common.parseDOM(headers, "a", ret="href")
        images = common.parseDOM(images_container, "img", ret="src")

        ratings = common.parseDOM(movies, "div", attrs={"class": "titlePageSprite star-box-giga-star"})
        infos = common.parseDOM(movies, "noindex")

        for i, title in enumerate(titles):
            image = images[i] if 'http' in images[i] else self.url+images[i]

            uri = sys.argv[0] + '?mode=show&url=%s' % (links[i])
            item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        if not len(titles) < 10:
            uri = sys.argv[0] + '?mode=%s&url=%s&page=%s' % ("category", url, str(int(page) + 1))
            item = xbmcgui.ListItem('следующая страница >>', thumbnailImage=self.inext, iconImage=self.inext)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)

    def movie(self, url):
        print "*** movie for url %s " % url


        response = common.fetchPage({"link": url})
        iframes = common.parseDOM(response["content"], "iframe", ret="src")

        container = common.parseDOM(response["content"], "div", attrs={ "class": "full-block view" })
        poster = common.parseDOM(container, "div", attrs={ "class": "poster-box" })
        rating = common.parseDOM(container, "div", attrs={ "class": "rating" })
        title = self.strip(common.parseDOM(container, "h1")[0])
        image = self.icon
        iframe = iframes[0]

        print iframes

        for iframe in iframes:
            if not 'http' in iframe:
                self.error('Unknown video source')
                return

            if 'kodik.cc' in iframe:
                print "Kodic link detected"
                uhash = Kodik.uppodHash(iframe)
                stream = Kodik.decode(uhash).split(',')[1]

                print stream

                uri = sys.argv[0] + '?mode=PlayHLS&url=%s' % urllib.quote_plus(stream)
                item = xbmcgui.ListItem(title,  iconImage=image, thumbnailImage=image)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(self.handle, uri, item)

            if not 'kodik.cc' in iframe:
                try:
                    if 'serial' in iframe:
                        print 'season'
                        seasons = Moonwalk.seasons(iframe)
                        for season in seasons:
                            for episode in season['episodes']:
                                title = "%s (%s)" % (episode['title'], season['title'])
                                print episode['link']

                                uri = sys.argv[0] + '?mode=play&url=%s' % urllib.quote_plus(episode['link'])
                                item = xbmcgui.ListItem(title,  iconImage=image, thumbnailImage=image)

                                item.setProperty('IsPlayable', 'true')
                                xbmcplugin.addDirectoryItem(self.handle, uri, item)

                    else:
                        streams = Moonwalk.movies(iframe)

                        hls_stream = streams['manifest_m3u8']
                        hds_stream = streams['manifest_f4m']


                        mtitle = '%s - %s' % (title, 'HLS Stream - m3u8')
                        uri = sys.argv[0] + '?mode=PlayHLS&url=%s' % urllib.quote_plus(hls_stream)
                        item = xbmcgui.ListItem(mtitle,  iconImage=image, thumbnailImage=image)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item)


                        mtitle = '%s - %s' % (title, 'HDS Stream - f4m')
                        uri = sys.argv[0] + '?mode=PlayHDS&url=%s' % urllib.quote_plus(hds_stream)
                        item = xbmcgui.ListItem(mtitle,  iconImage=image, thumbnailImage=image)
                        item.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(self.handle, uri, item)

                except:
                    print "Moonwalk exception"
                    pass

        xbmc.executebuiltin('Container.SetViewMode(52)')
        xbmcplugin.endOfDirectory(self.handle, True)


    def play(self, url):
        # streams = Moonwalk.movies(url)
        # hds_stream = streams['manifest_f4m']
        #
        # self.PlayHDS(hds_stream)

        streams = Moonwalk.movies(url)
        hls_stream = streams['manifest_m3u8']

        self.PlayHLS(hls_stream)


    def PlayHLS(self, url):
        # 0
        # from F4mProxy import f4mProxyHelper
        # player = f4mProxyHelper()
        # player.playF4mLink(link, name)

        # 1
        print 'Play URL: %s' % url
    	item = xbmcgui.ListItem(path = url)
    	item.setProperty('IsPlayable', 'true')
    	xbmcplugin.setResolvedUrl(self.handle, True, item)


        # 2
        # use_proxy_for_chunks = True
        #
        # from F4mProxy import f4mProxyHelper
        # player=f4mProxyHelper()
        # # playF4mLink(self,url,name,proxy=None,use_proxy_for_chunks=False, maxbitrate=0, simpleDownloader=False, auth=None, streamtype='HDS',setResolved=False,swf=None):
        #
        # player.playF4mLink(url, 'name', None, True, maxbitrate=0, simpleDownloader=False, auth=None, streamtype='HDS',setResolved=False, swf=None)
        #
        # return

    def PlayHDS(self, url, name = "f4mstream"):
        from F4mProxy import f4mProxyHelper
        player=f4mProxyHelper()

        urltoplay, item= player.playF4mLink(url,name,proxy=None,use_proxy_for_chunks=False, maxbitrate=0, simpleDownloader=False, auth=None, streamtype='HDS',setResolved=False)
        item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        # # WORKS but no seeking
    	# from F4mProxy import f4mProxyHelper
    	# import time
    	# helper = f4mProxyHelper()
    	# link, stopEvent = helper.start_proxy(url, "f4mstream")
        #
    	# item = xbmcgui.ListItem(path = link)
    	# item.setProperty('IsPlayable', 'true')
    	# xbmcplugin.setResolvedUrl(self.handle, True, item)
        #
    	# player = xbmc.Player()
    	# time.sleep(10)
        #
    	# while player.isPlaying():
    	# 	print "WAITING FOR PLAYER TO STOP"
    	# 	time.sleep(5)
    	# time.sleep(10)
    	# stopEvent.set()




    def genres(self, url):
        print "list genres"
        response = common.fetchPage({"link": url})
        container = common.parseDOM(response["content"], "div", attrs={"id": "dle-content"})
        menu = common.parseDOM(container, "div", attrs={"class": "horizontal-menu ns"})
        titles = common.parseDOM(menu, "a")
        links = common.parseDOM(menu, "a", ret="href")


        for i, link in enumerate(links):
            title = titles[i]
            link = self.url + '/zhanr' + links[i][:-1]

            uri = sys.argv[0] + '?mode=category&url=%s' % link
            item = xbmcgui.ListItem(title, iconImage=self.icon)
            xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

        xbmcplugin.endOfDirectory(self.handle, True)



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


class MyPlayer (xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)

    def play(self, url, listitem):
        print 'Now im playing... %s' % url
        self.stopPlaying.clear()
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, listitem)
    def onPlayBackEnded( self ):
        # Will be called when xbmc stops playing a file
        print "seting event in onPlayBackEnded "
        self.stopPlaying.set();
        print "stop Event is SET"
    def onPlayBackStopped( self ):
        # Will be called when user stops xbmc playing a file
        print "seting event in onPlayBackStopped "
        self.stopPlaying.set();
        print "stop Event is SET"

# class MyPlayer(xbmc.Player) :
#         print("[CUSTOM SCRIPT]Checking PlayBackState")
#         def __init__ (self):
#                 xbmc.Player.__init__(self)
#
#         def onPlayBackStarted(self):
#                 if xbmc.Player().isPlayingVideo():
#                         print("[CUSTOM SCRIPT]Video is playing")
#                         os.system("sudo python /usr/local/share/xbmc/addons/service.procmanager/resources/stopall.py") #Calls another script to stop proce$
#
#         def onPlayBackEnded(self): #Dosen't seem to get called
#                         print("[CUSTOM SCRIPT]Video isn't playing")
#                         os.system("sudo python /usr/local/share/xbmc/addons/service.procmanager/resources/startall.py") #Calls another script to start pro$
#




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
