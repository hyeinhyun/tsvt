import numpy as np
import torch
import string
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.utils.rnn import pad_packed_sequence as unpack
from torch.nn.utils.rnn import pack_padded_sequence as pack
import math
import torch.utils.data as data
import json
import os
import pandas as pd
import random
import copy
import torch.utils.data.sampler as sampler
import torch.optim.lr_scheduler as lr_scheduler
import pickle

import torch.utils.data as data

gameId=''
class Mul_data(data.Dataset):
    def __init__(self,d_type):
        self.d_type=d_type
        if d_type=='test':
            with open('./dataset/'+gameId+'_chat_features.json',"rb") as f1:  
                self.chat_result=json.load(f1)
        with open('./dataset/'+gameId+'_audio.pickle',"rb") as f3:  
            self.audio=pickle.load(f3)
        self.audio_result={}
        self.audio_result['test']=(list(self.audio))
        print(len(self.audio))
        if d_type=='test':
            self.sample = ['test']


        
        self.sum=np.insert(np.cumsum([len(self.chat_result[str(i)]) for i in self.sample]),0,0)
        print("data load fin")

        
    def __len__(self):
        return self.sum[-1]
    def __getitem__(self,index):
            vid=np.histogram(index,self.sum)#sum으로 누적으로 히스토그램이 깔려있음/ 그중에 index의 위치
            vid = np.where(vid[0]>0)[0][0]#몇번째 game을 쓸지!
            vframe=index-self.sum[vid]#그 게임 안에서의 몇번째 프레임인지
            game_id=str(self.sample[vid])
            window=[]#batch*7(window size)*3(highlight result)
            for idx in range(23): #7 : window size
                s_window=[]
                if vframe+idx<len(self.chat_result[game_id]):
                    s_window.extend(self.chat_result[game_id][vframe+idx])#vframe의 chat
                    s_window.extend(self.audio_result[game_id][(vframe+idx)*10:(vframe+idx+1)*10])#vframe의 audio
#                     s_window+=[(self.image_result[game_id][vframe+idx])]#vframe의 image
                else:
                    #s_window=[0,0,0]#padding value
                    s_window=[0]*138
                window.append(s_window)
            return game_id,np.array(window)
        
input_size=138
hidden_size=23
length=7
num_layers=3
class LSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self._clf1 = nn.LSTM(input_size, hidden_size,3,batch_first=True)
        self._lin = nn.Sequential(nn.Linear(hidden_size, hidden_size),
                                 nn.Linear(hidden_size,2))

    def forward(self, x):
        hidden = Variable(torch.zeros(num_layers,x.size(0),hidden_size)) # (num_layers * num_directions, batch, hidden_size)
        cell = Variable(torch.zeros(num_layers,x.size(0),hidden_size)) # (num_layers * num_directions, batch, hidden_size)        out,hidden = self._clf1(x,h0)
        feature,hidden = self._clf1(x,(hidden,cell))#batch*7*3
        out = self._lin(feature[:,-1,:])
        return feature[:,-1,:]
def main(game_i):
    global gameId
    gameId=game_i
    model=LSTM()
    test=Mul_data('test')
    print(len(test))
    print(test[1832])
    test_loader=torch.utils.data.DataLoader(test,batch_size=32)
    dataset='./weights/chat_audio_best'
    checkpoint=torch.load(dataset)
    model.load_state_dict(checkpoint)
    model.eval()
    pred_sum = 0#model output
    gt_sum = 0#label
    tp_sum=0
    fp_sum=0
    fn_sum=0
    acc=0
    sum=0
    result={}
    with torch.no_grad():
        for it, (game_id,inputs) in enumerate(test_loader):
            inputs=inputs.float()
            output=model(inputs)
            for idx,g in enumerate(game_id):
                if g not in result.keys():
                    print(g)
                    result[g]=[output[idx].tolist()]
                else:
                    result[g].append(output[idx].tolist())
    with open('./dataset/'+gameId+'_2step_feature.json','w') as f:
        json.dump(result,f)
if __name__ == "__main__":
    main('104841804589544588')
