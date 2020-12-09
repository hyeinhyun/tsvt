#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:17:47 2020

@author: hihyun
"""

import json
import urllib.request
from datetime import datetime
from datetime import timedelta
import re
import pandas as pd
import math
import chat_model
file=open('test.txt',"w",encoding="utf-8")
ClientId = "pnbcpj842zq89uy7hlhkakepr6xej7" # Client id 추가 #

game_id=''
def collectClip(v_id,  Clientid,v_stime,v_etime,game_i):
    print(v_id)
    #url = "https://api.twitch.tv/kraken/video/top?channel=" + channel + "&limit=" + str(lim)
    url="https://api.twitch.tv/kraken/videos/"+str(v_id)
    print(url)
    req = urllib.request.Request(url, headers = {"Client-ID": Clientid, "Accept" : "application/vnd.twitchtv.v5+json"})
    u = urllib.request.urlopen(req)
    c = u.read().decode('utf-8')
    js = json.loads(c)
    #print(js)
    f=open('./dataset/'+game_id+'_chat.txt',"w",encoding="utf-8")

    return collectChat(js, Clientid, f,v_id,v_stime,v_etime)

def collectChat(j, clientId, f,v_id,v_stime,v_etime):
    #id=v_id[:-1]
    id=v_id
    print(id)
    #id = j['clips'][num]['vod']['id']
    #offset = j['clips'][num]['vod']['offset']
    #duration = j['clips'][num]['duration']
    #print(duration)
    result={'title':[],'game':[],'views':[],'length':[],'date':[],'intime':[],'message':[]}

    cursor = ""
    count = 0

    while(1):
        try:
            url2 = ""
            if count == 0:
                url2 = "https://api.twitch.tv/kraken/videos/" + str(id) + "/comments"
            else:
                url2 = "https://api.twitch.tv/kraken/videos/" + str(id) + "/comments?cursor=" + str(cursor)
            req2 = urllib.request.Request(url2, headers = {"Client-ID": clientId, "Accept" : "application/vnd.twitchtv.v5+json"})
            u2 = urllib.request.urlopen(req2)
            c2 = u2.read().decode('utf-8')
            j2 = json.loads(c2)
            #print(j2)
            endCount = 0
            try:
                for number, com in enumerate(j2['comments']):



                    dateString = com['created_at']
                    if "." in dateString:
                        dateString = re.sub(r".[0-9]+Z","Z", dateString)
                    date = datetime.strptime(dateString, "%Y-%m-%dT%H:%M:%SZ")
                    #print(date)
                    leng=j['length']
                    off=com['content_offset_seconds']
                    if float(leng)<float(off):
                        return 0
                    if com['content_offset_seconds']>=v_stime and com['content_offset_seconds']<=v_etime:
                        result['title'].append(str(j['title']))
                        result['game'].append(str(j['game']))
                        result['views'].append(str(j['views']))
                        result['length'].append(str(j['length']))
                        result['date'].append(str(date + timedelta(hours=9)))
                        result['intime'].append(str(com['content_offset_seconds']))
                        result['message'].append(str(com['message']['body']))

                        f.write(str(j['title']) + "\t" +
                                str(j['game']) + "\t" +
                                str(j['views']) + "\t" +
                                str(j['length']) + "\t" +
                                str(date + timedelta(hours=9)) + "\t" +
                                str(com['content_offset_seconds'])+"\t"+
                                str(com['message']['body']) + "\n")
                    elif com['content_offset_seconds']>v_etime:
                        endCount=1
                        break
            except Exception as e:
                print(e)

            if endCount == 1:
                break

            if j2['_next']:
                cursor = j2['_next']

            count = count + 1

        except Exception as e:
            print(e)
    f.close()
    print('==========Collect fin===================')
    makeChat(result,v_etime-v_stime,v_stime)
def makeChat(result,dur,v_stime):
    print('==========Start preprocessing===================')
    global game_id
    data={}
    chat_data=pd.DataFrame(result)
    chat=['' for i in range(math.floor(float(dur)))]
    for idx,i in enumerate(chat_data['intime']):
        chat[math.floor(float(i))-v_stime]+=str(chat_data['message'][idx])
    
    data['test']=chat
    with open('./dataset/'+game_id+'_chat.json', 'w') as f:
        json.dump(data, f, indent=2)
    print('==========Chat end===================')
    
def main(v_id,Clientid,v_stime,v_etime,game_i):
    global game_id
    game_id=game_i
    collectClip(v_id,Clientid,v_stime,v_etime,game_i)
    print('==========Model train===================')
    chat_model.main(game_id)
    print('==========Model fin===================')
if __name__ == "__main__":


    main("496371424",ClientId,0,10,'test1234')
  
    
    
