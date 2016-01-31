#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2012, MrStealth

import os, sys, urllib, urllib2, cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import re, KodiUtils

common = KodiUtils

class MyHit():
  def __init__(self):
    self.id = 'plugin.audio.my-hit.com'
    self.addon = xbmcaddon.Addon(self.id)
    self.icon = self.addon.getAddonInfo('icon')
    self.path = self.addon.getAddonInfo('path')
    self.profile = self.addon.getAddonInfo('profile')

    self.language = self.addon.getLocalizedString
    self.translit = self.addon.getSetting('translit')
    self.handle = int(sys.argv[1])
    self.params = sys.argv[2]
    self.url = 'http://my-hit.com'

    self.inext = os.path.join(self.path, 'resources/icons/next.png')
    self.debug = False


  def main(self):
    params = common.getParameters(self.params)

    mode = params['mode'] if 'mode' in params else None
    url = urllib.unquote_plus(params['url']) if 'url' in params else None
    page = params['page'] if 'page' in params else 1

    if mode == 'play':
        self.play(url)
    if mode == 'search':
        self.search()
    if mode == 'genres':
        self.genres('genres')
    if mode == 'compilation':
        self.genres('compilation')
    if mode == 'artists':
        self.genres('artists')
    if mode == 'songs':
        self.songs(url, page)
    elif mode is None:
        self.menu()


  def menu(self):
    uri = sys.argv[0] + '?mode=search'
    item = xbmcgui.ListItem("[B][COLOR=orange]%s[/COLOR][/B]" % self.language(1000), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=genres'
    item = xbmcgui.ListItem("[B][COLOR=lightseagreen]Популярная музыка[/COLOR][/B]", iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=compilation'
    item = xbmcgui.ListItem("[B][COLOR=lightseagreen]Популярные сборники[/COLOR][/B]", iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=artists'
    item = xbmcgui.ListItem("[B][COLOR=lightseagreen]Популярные исполнители[/COLOR][/B]", iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    self.songs(self.url, 1)

  def genres(self, collection):
    page = common.fetchPage({"link": self.url})

    if collection == 'compilation':
        container = common.parseDOM(page["content"], "div", attrs = { "class" : "module-collections" })[0]
    elif collection == 'artists':
        container = common.parseDOM(page["content"], "div", attrs = { "class" : "module-collections" })[1]
    else:
        container = common.parseDOM(page["content"], "div", attrs = { "class" : "module-popular" })[0]

    links = common.parseDOM(container, "a", ret="href")
    titles = common.parseDOM(container, "a")

    for i, title in enumerate(titles):
      uri = sys.argv[0] + '?mode=songs&url=%s' % links[i]
      item = xbmcgui.ListItem(title, iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)

  def songs(self, url, page):
    print "*** GET SONGS FOR PLAYLIST: %s" % url

    container = common.parseDOM(common.get(url), "div", attrs = { "class" : "module-layout" })
    playlist = common.parseDOM(container, "h1")
    artists = common.parseDOM(container, "span", attrs = { "class":"artist" })
    tracks = common.parseDOM(container, "span", attrs = { "class":"track" })

    links = common.parseDOM(container, "a", attrs = { "class":"dl" }, ret="href")
    durations = common.parseDOM(container, "div", attrs = { "class":"duration" })

    pagination = common.parseDOM(page, "div", attrs={"class": "pagination"})

    for i, link in enumerate(links):
        song = "%s - %s"%(tracks[i], artists[i])

        item = xbmcgui.ListItem(song, iconImage=self.icon, thumbnailImage=self.icon)
        item.addStreamInfo('audio', {})
        item.setMimeType('audio/mpeg')
        item.setProperty('mimetype', 'audio/mpeg')
        item.setInfo(
        'music',
        {
          'title': tracks[i],
          'artist' : artists[i],
          'album' : playlist,
          'genre': playlist,
          'duration' : self.duration(durations[i]),
          'rating' : '5'
        }
        )

        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(self.handle, link, item, False)


    page = re.search('(\/\d+)', url)
    if page:
        page = str(int(page.group(0)[1:])+1)
        url = re.sub('(\/\d+)', '/' + page, url)
    else:
        url += '/2'

    print url

    uri = sys.argv[0] + '?mode=songs&url=%s' % urllib.quote_plus(url)
    item = xbmcgui.ListItem("[COLOR=orange]%s[/COLOR]" % self.language(1001), iconImage=self.inext)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)

  def duration(self, time):
    duration = time.split(':')
    return int(duration[0]) * 60 + int(duration[1])

  def search(self):
    query = common.getUserInput(self.language(1000), "")

    if query != None:
        url = "%s/%s" % (self.url, query)
        self.songs(url, 1)
    else:
      self.main()

  # def play(self, url):
  #   print "*** play URL %s"%url
  #   item = xbmcgui.ListItem(path = url)
  #   item.setProperty('mimetype', 'audio/mpeg')
  #   xbmcplugin.setResolvedUrl(self.handle, True, item)


  def error(self, msg):
    print msg
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))

  def encode(self, string):
    return string.decode('cp1251').encode('utf-8')


MyHit().main()
