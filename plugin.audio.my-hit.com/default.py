#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-

import os, sys, urllib, urllib2, cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json, KodiUtils

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
        self.genres()
    if mode == 'songs':
        self.songs(url, page)
    elif mode is None:
        self.menu()


  def menu(self):
    uri = sys.argv[0] + '?mode=search'
    item = xbmcgui.ListItem("[B][COLOR=orange]%s[/COLOR][/B]" % self.language(1000), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    uri = sys.argv[0] + '?mode=genres'
    item = xbmcgui.ListItem("[B][COLOR=lightseagreen]%s[/COLOR][/B]" % self.language(1000), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    self.songs(self.url, 1)

  def genres(self):
    page = common.fetchPage({"link": self.url})
    styles = common.parseDOM(page["content"], "div", attrs = { "class" : "module-popular" })
    links = common.parseDOM(styles, "a", ret="href")
    titles = common.parseDOM(styles, "a")

    for i, title in enumerate(titles):
      print links[i].encode('utf-8')
      link = links[i]
      uri = sys.argv[0] + '?mode=songs&url=%s' % link
      item = xbmcgui.ListItem(title, iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)

  def songs(self, url, page):
    print "*** GET SONGS FOR PLAYLIST: %s" % url
    page = common.fetchPage({"link": url})
    container = common.parseDOM(page["content"], "div", attrs = { "class" : "module-layout" })

    playlist = common.parseDOM(container, "h1")
    artists = common.parseDOM(container, "span", attrs = { "class":"artist" })
    tracks = common.parseDOM(container, "span", attrs = { "class":"track" })

    links = common.parseDOM(container, "a", attrs = { "class":"dl" }, ret="href")
    durations = common.parseDOM(container, "div", attrs = { "class":"duration" })

    pagination = common.parseDOM(page["content"], "div", attrs={"class": "pagination"})

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

    if pagination:
        self.pagination('songs', url)

    xbmcplugin.endOfDirectory(self.handle, True)

  def pagination(self, mode, url):
      if 'page' in url:
          page = int(url[-2:].replace('/', ''))+1
          link = "%s%d/" % (url[:-2], page)
      else:
          link = url + '/2/'

      uri = sys.argv[0] + '?mode=%s&url=%s' % (mode, urllib.quote_plus(link))
      item = xbmcgui.ListItem("[COLOR=orange]%s[/COLOR]" % self.language(1001), iconImage=self.inext)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

  def duration(self, time):
    duration = time.split(':')
    return int(duration[0]) * 60 + int(duration[1])

  # def play(self, url):
  #   print "*** play URL %s"%url
  #   item = xbmcgui.ListItem(path = url)
  #   item.setProperty('mimetype', 'audio/mpeg')
  #   xbmcplugin.setResolvedUrl(self.handle, True, item)

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
