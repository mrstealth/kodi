#-------------------------------------------------------------------------------
# Uppod decoder
#-------------------------------------------------------------------------------

import urllib2
import base64
import json

# iframe = 'http://kodik.cc/video/7971/17a3230b1e3fe11917178d5edc6f8850/720p'
# uhash = uppodHash(iframe)
# print decode(uhash)

def streams(kpid):
    try:
        url = iframe(kpid)
        uhash = uppodHash(url)
        streams = decode(uhash)

        return streams.split(',')[:-1]
    except Exception:
        return []

def iframe(kpid):
    url = 'http://kodik.cc/api.js?width=640&height=365&class_name=noypleer&kp_id=%s&title_orig=true' % kpid
    request = urllib2.Request(url, None)
    response = urllib2.urlopen(request).read()
    iframe = response.split('player_iframe.setAttribute("src",')[-1].split(');')[0]
    return iframe

def uppodHash(url):
    params = url.split('/')
    video = params[4]
    key = params[5]

    url = 'http://kodik.cc/player/newjplayer_ajax.php?hash=%s&id=%s&type=database' % (key, video)
    request = urllib2.Request(url, None)
    request.add_header('Referer', url)
    response = urllib2.urlopen(request).read()
    return json.loads(response)['player_script'].split(',')[1]


def decode(param):
    hash1 = "i9DBzZT640N5JmMRuoLcn3Isk="
    hash2 = "lGbU8Y7xXtawWyvg2QHeVfpd1r"

    for i in range(0, len(hash1)):
        re1 = hash1[i]
        re2 = hash2[i]

        param = param.replace(re1, '___')
        param = param.replace(re2, re1)
        param = param.replace('___', re2)

    return base64.b64decode(param)
