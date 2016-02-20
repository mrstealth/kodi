#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, MrStealth

import base64

def DecodeUppodTextHash(data, hash="0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"):
    # hash = "0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"
    data = DecodeUppod_tr(data, "r", "A")
    data = data.replace("\n", "")
    hash = hash.split('ih')

    if data.endswith('!'):
        data = data[:-1]
        taba = hash[3]
        tabb = hash[2]
    else:
        taba = hash[1]
        tabb = hash[0]

    i = 0;
    while i < len(taba):
        data = data.replace(tabb[i], "__"   )
        data = data.replace(taba[i], tabb[i])
        data = data.replace("__"   , taba[i])
        i += 1

    result = base64.b64decode(data)
    return result

def DecodeUppod_tr(data, ch1, ch2):
    if data[:-1].endswith(ch1) and data[2]==ch2:
        srev = data[::-1]  # revers string
        try:
            loc3 = int(float(srev[-2:]) / 2) # get number at end of string
        except ValueError:
            return data
        srev = srev[2:-3] # get string between ch1 and ch2
        if loc3 < len(srev):
            i = loc3
            while i < len(srev):
                srev = srev[:i] + srev[i+1:] # remove char at index i
                i += loc3
        data = srev + "!"
    return data
