#!/usr/bin/python
# Writer (c) 2016, MrStealth
# Rev. 1.0.0
# License: GPLv3

import os, re, sys, json
import urllib, urllib2, base64

import KodiUtils
common = KodiUtils

def movies(iframe):
    if 'video' in iframe:
        print 'Video link detected'
        return streams(iframe)
    elif 'serial' in iframe:
        if ('season' and 'episode' in iframe):
            return streams(iframe)
        elif 'season' in iframe:
            return episodes(iframe)
        else:
            return seasons(iframe)
    else:
        print "Unknown iframe URL %s" % iframe

def seasons(iframe):
    print "Get seasons for %s" % iframe

    response = common.fetchPage({"link": iframe})['content']
    body = common.parseDOM(response, "body")[0]
    select = common.parseDOM(body, "select", attrs={"name": "season"})

    titles = common.parseDOM(select, "option")
    links = common.parseDOM(select, "option", ret="value")
    seasons = []

    for i, title in enumerate(titles):
        url = "%s?season=%s" % (iframe, links[i])
        seasons.append({'title': title, 'episodes': episodes(url)})

    # print seasons
    return seasons

def episodes(iframe):
    print "Get episodes for %s" % iframe

    response = common.fetchPage({"link": iframe})['content']
    body = common.parseDOM(response, "body")[0]
    select = common.parseDOM(body, "select", attrs={"name": "episode"})

    titles = common.parseDOM(select, "option")
    links = common.parseDOM(select, "option", ret="value")

    episodes = []

    for i, title in enumerate(titles):
        url = "%s&episode=%s" % (iframe, links[i])
        episodes.append({'title': title, 'link': url})


    # print episodes
    return episodes

def streams(iframe):
    print "Get streams for %s" % iframe

    response = common.fetchPage({"link": iframe})['content']
    body = common.parseDOM(response, "body")[0]
    params = body.split('.success')[0].split('$.post')[-1]

    host = re.search("//([a-z0-9.]+/)", iframe).group(0).replace('/', '')
    # host = re.search("[0-9.]+", iframe).group(0)

    csrf_token = str(common.parseDOM(response, "meta", attrs = { "name": "csrf-token" }, ret="content")[0])
    d_id = int(re.search("d_id: [0-9]+", params).group(0).replace('d_id: ', ''))
    video_token = str(re.search("video_token: '[0-9A-Fa-f]+'", params).group(0).replace('video_token: ', '')).replace("'", '')
    access_key = str(re.search("access_key: '[0-9A-Fa-f]+'", params).group(0).replace('access_key: ', '')).replace("'", '')
    content_data = base64.b64encode(body.split('setRequestHeader|')[-1].split('|')[0])

    values = {
      'partner': '918',
      'd_id': 26873,
      'video_token': video_token,
      'content_type': 'movie',
      'access_key': access_key,
      'cd': '0'
    }

    headers = {
        'Host': host,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0',
        'Accept': '*/*',
        'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-CSRF-Token': csrf_token,
        'Content-Data': content_data,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': iframe,
    }

    print "***********************************************"
    print values
    print headers

    url = "http://%s/sessions/create_session" % host
    print "POST %s" % url

    request = urllib2.Request(url, urllib.urlencode(values), headers)
    response = urllib2.urlopen(request).read()
    streams = json.loads(response)

    for key,val in streams.items():
        print key
        print val

    print streams['manifest_m3u8']
    return streams
    #
    #
    # except Exception, e:
    #     print e


def parse(self, string):
    links = re.findall(r'(?:http://|www.).*?["]', string)
    return list(set(self.filter(links)))

def filter(self, links):
    links = self.strip(links)
    return [l for l in links if l.endswith('.mp4') or l.endswith('.mp4') or l.endswith('.txt')]

def strip(self, links):
    return [l.replace('"', '') for l in links]
