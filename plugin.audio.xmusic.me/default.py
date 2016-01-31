#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-

import os, sys, urllib, urllib2, cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import json, KodiUtils

common = KodiUtils

class Xmusic():
  def __init__(self):
    self.id = 'plugin.audio.xmusic.me'
    self.addon = xbmcaddon.Addon(self.id)
    self.icon = self.addon.getAddonInfo('icon')
    self.path = self.addon.getAddonInfo('path')
    self.profile = self.addon.getAddonInfo('profile')

    self.language = self.addon.getLocalizedString
    self.handle = int(sys.argv[1])
    self.url = 'http://xmusic.me'

    self.icover = os.path.join(self.path, 'resources/icons/cover.png')
    self.inext = os.path.join(self.path, 'resources/icons/next.png')

  def main(self):
    params = common.getParameters(sys.argv[2])
    mode = url = style = playlist = None

    mode = params['mode'] if params.has_key('mode') else None
    url = urllib.unquote_plus(params['url']) if params.has_key('url') else None
    language = params['language'] if params.has_key('language') else None

    if mode == 'play':
      self.play(url)
    if mode == 'songs':
      self.songs(url)
    if mode == 'search':
      self.search()
    elif mode == None:
      self.menu()

  def menu(self):
    uri = sys.argv[0] + '?mode=%s'%('search')
    item = xbmcgui.ListItem("[B][COLOR=orange]%s[/COLOR][/B]" % self.language(1000), iconImage=self.icon)
    xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    self.genres()

  def genres(self):
    page = common.fetchPage({"link": self.url})
    styles = common.parseDOM(page["content"], "ul", attrs = { "class" : "music_styles" })
    links = common.parseDOM(styles, "a", ret="href")
    titles = common.parseDOM(styles, "a")

    for i, title in enumerate(titles):
      link = self.url + '/top/' if links[i] == '/' else self.url + links[i]
      uri = sys.argv[0] + '?mode=%s&url=%s'%('songs', urllib.quote_plus(link))
      item = xbmcgui.ListItem(title, iconImage=self.icon)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

    xbmcplugin.endOfDirectory(self.handle, True)

  def songs(self, url):
    print "*** GET SONGS FOR PLAYLIST: %s" % url
    page = common.fetchPage({"link": url})
    playlist = common.parseDOM(page["content"], "ul", attrs = { "id" : "playlist" })

    artists = common.parseDOM(playlist, "em")
    titles = common.parseDOM(playlist, "i")
    links = common.parseDOM(playlist, "li", attrs = { "class":"track" }, ret="data-download")
    durations = common.parseDOM(playlist, "span", attrs = { "class":"player-duration" })

    style = common.parseDOM(page["content"], "h2", attrs = { "class":"xtitle" })
    playlist_title = style if style else 'XMusic.me playlist'
    navigation = common.parseDOM(page["content"], "li", attrs={"class": "listalka1-l"})

    for i, link in enumerate(links):
      title = common.parseDOM(titles[i], "a")[0]
      artist = common.parseDOM(artists[i], "a")[0]
      song = "%s - %s"%(title, artist)
      image = self.icon

      item = xbmcgui.ListItem(song, iconImage=image, thumbnailImage=image)
      item.addStreamInfo('audio', {})
      item.setMimeType('audio/mpeg')
      item.setProperty('mimetype', 'audio/mpeg')
      item.setInfo(
        'music',
        {
          'title': song,
          'artist' : artist,
          'album' : style,
          'genre': 'xmusic.me',
          'duration' : self.duration(durations[i]),
          'rating' : '5'
        }
      )

      item.setProperty('IsPlayable', 'true')
      xbmcplugin.addDirectoryItem(self.handle, link, item, False)

    if navigation:
        self.navigation('songs', url)

    xbmcplugin.endOfDirectory(self.handle, True)

  def navigation(self, mode, url):
      if 'page' in url:
          page = int(url[-2:].replace('/', ''))+1
          link = "%s%d/" % (url[:-2], page)
      else:
          link = url + '/page/2/'

      uri = sys.argv[0] + '?mode=%s&url=%s' % (mode, urllib.quote_plus(link))
      item = xbmcgui.ListItem("[COLOR=orange]%s[/COLOR]" % self.language(1001), iconImage=self.inext)
      xbmcplugin.addDirectoryItem(self.handle, uri, item, True)

  def duration(self, time):
    duration = time.split(':')
    return int(duration[0]) * 60 + int(duration[1])

  def play(self, url):
    print "*** play URL %s"%url
    item = xbmcgui.ListItem(path = url)
    item.setProperty('mimetype', 'audio/mpeg')
    xbmcplugin.setResolvedUrl(self.handle, True, item)

  def search(self):
    query = common.getUserInput(self.language(1000), "")
    url = self.url + '/public/api.search.php'

    if query != None:
      post_data = { 'q': query, 'type': 'q' }
      page = common.fetchPage({"link": url, "post_data": post_data, "hide_post_data": "true"})

      try:
          self.songs(self.url + page['content'])
      except:
          main()
    else:
      main()

  def error(self, msg):
    print msg
    xbmc.executebuiltin("XBMC.Notification(%s,%s, %s)"%("ERROR",msg, str(10*1000)))


  def encode(self, string):
    return string.decode('cp1251').encode('utf-8')


xmusic = Xmusic()
xmusic.main()
