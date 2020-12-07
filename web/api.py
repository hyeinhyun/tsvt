key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'

import requests
import pandas as pd
import numpy as np
import time
import datetime
gameId=''

def league(id,time):
    print('function - league')
    key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'
    header = {'x-api-key':key}
    datas = [time,id]
    datas[0] = datas[0][:-1]+'.00Z'
    gamedata = {}
    #get window
    timeframe = pd.DataFrame(np.zeros((0,2)))
    timeframe.columns = ['Time','frame']

    first = 0
    index = 0
    seconds = 0
    last = 0
    dead = 0
    while dead == 0 :

        try:
            if first == 0:
                startT = datas[0]
                timeT = datetime.datetime.strptime(startT, "%Y-%m-%dT%H:%M:%S.%fZ")
                timeT = timeT - datetime.timedelta(hours=1)
                first +=1
            else:
                if seconds == 0 :
                    timeT = timeT + datetime.timedelta(minutes=1)
                else:
                    timeT = timeT + datetime.timedelta(seconds=10)
            param = {'id':datas[1],'startingTime':str(timeT.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))}

            leagues = 'https://feed.lolesports.com/livestats/v1/window/'+str(param['id'])
            r = requests.get(leagues,headers = header,params = param)
            data = r.json()
            for i in range(len(data['frames'])):
                if len(data['frames'][i]['rfc460Timestamp']) == 20:
                    data['frames'][i]['rfc460Timestamp'] = data['frames'][i]['rfc460Timestamp'][:-1]+'.00Z'

                tempTime = datetime.datetime.strptime(data['frames'][i]['rfc460Timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

                check = str(tempTime.hour)+'-'+str(tempTime.minute)+'-'+str(tempTime.second)

                if data['frames'][i]['gameState']=='finished':
                    dead = 1
                    if check in list(timeframe['Time']):
                        timeframe.loc[index-1] = check,data['frames'][i]
                        continue

                if  check not in list(timeframe['Time']):
                    timeframe.loc[index] = check,data['frames'][i]
                    index += 1

            if seconds == 0:
                timeT = timeT - datetime.timedelta(minutes=1)
                timeframe = pd.DataFrame(np.zeros((0,2)))
                timeframe.columns = ['Time','frame']
                seconds =1

        except Exception as e:
            pass
    gamedata[datas[1]] = timeframe
    print('finish')
    
    for k,v in gamedata.items():
        for i in v['frame']:
            if i['blueTeam']['totalGold'] == 0:
                gamedata[k] = gamedata[k].drop([gamedata[k].index[0]])
    
    for game_id in gamedata.keys():
        gamedata[game_id]['Timestamp'] = list(map(lambda x:x['rfc460Timestamp'],gamedata[game_id]['frame'].values))

        gamedata[game_id]['blue_gold'] = list(map(lambda x:x['blueTeam']['totalGold'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['blue_towers'] = list(map(lambda x:x['blueTeam']['towers'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['blue_barons'] = list(map(lambda x:x['blueTeam']['barons'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['blue_totalKills'] = list(map(lambda x:x['blueTeam']['totalKills'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['blue_dragons'] = list(map(lambda x:len(x['blueTeam']['dragons']),gamedata[game_id]['frame'].values))

        gamedata[game_id]['red_gold'] = list(map(lambda x:x['redTeam']['totalGold'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['red_towers'] = list(map(lambda x:x['redTeam']['towers'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['red_barons'] = list(map(lambda x:x['redTeam']['barons'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['red_totalKills'] = list(map(lambda x:x['redTeam']['totalKills'],gamedata[game_id]['frame'].values))
        gamedata[game_id]['red_dragons'] = list(map(lambda x:len(x['redTeam']['dragons']),gamedata[game_id]['frame'].values))

        gamedata[game_id].drop(['frame'],axis='columns',inplace=True)
        gamedata[game_id] = gamedata[game_id].reset_index(drop=True)
    
    for game in gamedata.keys():
        gamedata[game]['Time'] = list(map(lambda x:int(x.split('-')[0])*3600+int(x.split('-')[1])*60+int(x.split('-')[2]),gamedata[game]['Time']))
    
    for game in gamedata.keys():
        init = gamedata[game]['Time'][0]
        gamedata[game]['Time'] = list(map(lambda x:x-init,gamedata[game]['Time']))
    
    for game in gamedata.keys():
        temp_data= pd.DataFrame(columns = gamedata[game].columns)
        time = 0
        index = 0
        last = gamedata[game]['Time'].values[-1]
        while(time<last):
            temp = gamedata[game].iloc[[index]]
            if temp['Time'].values[0] == time:
                temp_data = pd.concat([temp_data,temp],ignore_index = True)
                index+=1
            else :
                temp['Time'] = time
                temp_data = pd.concat([temp_data,temp],ignore_index = True)
            time+=1
        gamedata[game] = temp_data

    duration = 0
    for key in gamedata.keys():
        duration = len(gamedata[key])
    video_features(gamedata)
    print('league-finish')
    return duration



def video_features(gamedata):
    print('function - features')
    
    # 논문 통계 적용
    baron_statistic={}
    dragon_statistic={}

    highlight_add = {}

    for game in gamedata.keys():
        baron_s=[]
        dragon_s=[]
        end_s=[]

        baron = []
        dragon = []
        end = []
        bb=0
        rb=0
        bd=0
        rd=0
        for i in range(len(gamedata[game])):
            #default -17,8  -7,5
            if gamedata[game].loc[i]['blue_barons']!=bb:
                baron_s.append(i)
                for j in range(i-20,min(i+9,len(gamedata[game]))):
                    baron.append(j)
                bb = gamedata[game].loc[i]['blue_barons']
            if gamedata[game].loc[i]['red_barons']!=rb:
                baron_s.append(i)
                for j in range(i-20,min(i+9,len(gamedata[game]))):
                    baron.append(j)
                rb = gamedata[game].loc[i]['red_barons']
            if gamedata[game].loc[i]['blue_dragons']!=bd:
                dragon_s.append(i)
                for j in range(i-8,min(i+4,len(gamedata[game]))):
                    dragon.append(j)
                bd = gamedata[game].loc[i]['blue_dragons']
            if gamedata[game].loc[i]['red_dragons']!=rd:
                dragon_s.append(i)
                for j in range(i-8,min(i+4,len(gamedata[game]))):
                    dragon.append(j)
                rd = gamedata[game].loc[i]['red_dragons']
        #for j in range(len(data[game])-48,len(data[game])):
        #        end.append(j)

        highlight_add[game] = baron+dragon

        baron_statistic[game] = baron_s
        dragon_statistic[game] = dragon_s
    
    for game in gamedata.keys():
        gamedata[game] = gamedata[game][['blue_gold','red_gold','blue_towers','red_towers','blue_totalKills','red_totalKills']]
    
    #normalization
    for game in gamedata.keys():
        final = pd.DataFrame(columns = ['gold','tower','kill'])
        for i in range(len(gamedata[game])):
            temp =[]
            temp.append((gamedata[game]['blue_gold'][i]+1) / (gamedata[game]['blue_gold'][i]+gamedata[game]['red_gold'][i]+2))
            temp.append((gamedata[game]['blue_towers'][i]+1) / (gamedata[game]['blue_towers'][i]+gamedata[game]['red_towers'][i]+2))
            temp.append((gamedata[game]['blue_totalKills'][i]+1) / (gamedata[game]['blue_totalKills'][i]+gamedata[game]['red_totalKills'][i]+2))
            final.loc[i] = temp

        gamedata[game] = final

    # 0. 사용할 패키지 불러오기
    from keras.utils import np_utils
    from keras.models import Sequential
    from keras.layers import Dense, Activation
    import numpy as np
    from numpy import argmax


    # load model
    from keras.models import load_model
    model = load_model('/home/ubuntu/hyein/tsvt/web/weights/344-0.0404.hdf5')

    predict = {}
    result = {}
    
    for game in gamedata.keys():
        predict[game] = model.predict(gamedata[game])
    
    highlight_re = {}
    highlight_delta = {}
    for game in gamedata.keys():
        predict_blue = pd.DataFrame(predict[game])
        predict_red = predict_blue[1]
        predict_blue = predict_blue[0]

        predict_temp = list(predict_blue)
        predict_temp.insert(0,0)
        predict_temp.pop(-1)

        predict_blue = abs(np.array(predict_blue)-np.array(predict_temp))
        predict_blue[0] = predict_blue[1]

        predict_temp = list(predict_red)
        predict_temp.insert(0,0)
        predict_temp.pop(-1)

        predict_red = abs(np.array(predict_red)-np.array(predict_temp))
        predict_red[0] = predict_red[1]

        predict_delta = predict_blue+predict_red

        highlight_delta[game] = predict_delta

        highlight = []
        for i,v in enumerate(predict_delta):
            if v>0.0085:
                highlight.append(i)

        highlight_re[game] = highlight
        
    for key in highlight_delta.keys():
        highlight_delta[key] = list(map(lambda x : 1 if x>0.0085 else x, highlight_delta[key]))
    
    for key in highlight_re.keys():
    #print(tdelta[key])
    
        for index in highlight_re[key]:
            before=[]
            #before 10
            v = 1/21
            temp=v
            for i in range(20):
                before.append(temp)
                temp+=v

            after=[]
            #after 7
            v = 1/15
            temp=v
            for i in range(14):
                after.insert(0,temp)
                temp+=v
            total=before
            total.append(1)
            total = total+after
            ti =0
            for i in range(max(0,-20+index),min(len(highlight_delta[key]),14+index)):
                if highlight_delta[key][i] < total[ti]:
                    highlight_delta[key][i] = total[ti]
                ti+=1
        
    for key in baron_statistic.keys():
        #16,7
        for index in baron_statistic[key]:
            before=[]
            #before 10
            #v = max(delta[key])/17
            v = 1/33
            temp=v
            for i in range(32):
                before.append(temp)
                temp+=v

            after=[]
            #after 7
            #v = max(delta[key])/8
            v = 1/15
            temp=v
            for i in range(14):
                after.insert(0,temp)
                temp+=v
            total=before
            #total.append(max(delta[key]))
            total.append(1)
            total = total+after
            ti =0
            for i in range(max(0,-32+index),min(len(highlight_delta[key]),14+index)):
                if highlight_delta[key][i] < total[ti]:
                    highlight_delta[key][i] = total[ti]
                ti+=1
        
    for key in dragon_statistic.keys():
        #6, 3
        for index in dragon_statistic[key]:
            before=[]
            #before 10
            #v = max(delta[key])/6
            v = 1/11
            temp=v
            for i in range(10):
                before.append(temp)
                temp+=v

            after=[]
            #after 7
            #v = max(delta[key])/3
            v = 1/5
            temp=v
            for i in range(4):
                after.insert(0,temp)
                temp+=v
            total=before
            #total.append(max(delta[key]))
            total.append(1)
            total = total+after
            ti =0
            for i in range(max(0,-10+index),min(len(highlight_delta[key]),4+index)):
                if highlight_delta[key][i] < total[ti]:
                    highlight_delta[key][i] = total[ti]
                ti+=1
    for key in baron_statistic.keys():
        #6, 3
        before=[]
        #before 10
        #v = max(delta[key])/47
        v = 1/93
        temp=v
        for i in range(92):
            before.append(temp)
            temp+=v

        total=before
        #total.append(max(delta[key]))
        total.append(1)
        ti =0
        for i in range(len(highlight_delta[key])-92,len(highlight_delta[key])):
            if highlight_delta[key][i] < total[ti]:
                highlight_delta[key][i] = total[ti]
            ti+=1
    import pickle
    with open('/home/ubuntu/hyein/tsvt/web/dataset/'+gameId+'_video.pickle','wb') as fw:
        pickle.dump(highlight_delta,fw)

def main(game_i,time):
    global gameId
    gameId=game_i
    dur=league(gameId,time)
    return dur
    
    
